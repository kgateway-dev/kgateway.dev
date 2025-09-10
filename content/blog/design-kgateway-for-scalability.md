---
title: Designing kgateway for Scalability – Not All Gateways Are Created Equal
toc: false
publishDate: 2025-05-07T00:00:00-00:00
author: Lin Sun & Yuval Kohavi
excludeSearch: true
---

With the Kubernetes Gateway API becoming the de facto standard for managing traffic into, out of, and within clusters, a growing number of gateways now implement this API. While gateways are often thought of as interchangeable, the choice can have major implications—especially in terms of scale.

Before comparing features, a critical consideration is whether a gateway is built on a solid, reliable foundation.

## Aren’t All Envoy-Based Gateways the Same?

It's a fair question. Many gateways use the Envoy proxy under the hood to enforce routing, security, and other traffic policies. But despite sharing the same data plane, not all gateways are equal: the **control plane** makes all the difference.

The control plane is responsible for translating Kubernetes Gateway API resources into actual Envoy configuration. This translation layer can be simple for a few routes, but when you’re managing 20,000 resources (which will translate into 500,000+ lines of Envoy config), the efficiency and scalability of the control plane become critical—as I noted in a previous [LinkedIn post](https://www.linkedin.com/posts/lin-sun-a9b7a81_from-20000-kubernetes-gateway-resources-activity-7305695363049373696-UVNz?utm_source=share&utm_medium=member_desktop&rcm=ACoAAABLihcBuozqLyftNtauegAdN2-QszsmqQQ).

## Designing kgateway for Scalability

When we started building Gloo (now kgateway) seven years ago, we used a snapshot-based model that recalculated everything on every update—whether it was a new route, an update, or a backend change. This meant even small changes triggered a full control plane recalculation. With Kubernetes, where pods and backends change constantly, this was not scalable.

Managing resource dependencies via manual references like `targetRefs` and `extensionRefs` also proved cumbersome. Dependency resolution sometimes failed, creating reliability issues.

Learning from that experience, we designed kgateway using the battle-tested [krt](https://github.com/istio/istio/blob/master/pkg/kube/krt/README.md) framework to handle dependency tracking automatically. Now, only affected objects are re-translated when a change occurs—ensuring fast updates and efficient scaling.

Let’s walk through a few core scenarios to illustrate how kgateway scales to support large teams and applications, starting with a setup of 10,000 routes and backends, and see how kgateway handles new routes, route update, deletion or control plane becomes unavailable.

## Core Scalability Scenarios

### When a New Route Is Added

In a production system with thousands of existing routes, adding a new one should be near-instant. Ideally, the route becomes effective within 1 second, without needing a periodic timer or restart. This ensures teams can test and deploy with confidence.

{{< reuse-image src="blog/scalability-add-a-route.gif" width="75%" caption="Watch the full demo in the Test These Scenarios Yourself section below" >}}

### When a Route Is Updated

Updates to an existing route should not interrupt traffic. The old route should be replaced atomically, and the new route should take effect immediately. Any delay or downtime can lead to outages or security issues—especially in critical systems.

{{< reuse-image src="blog/scalability-modify-a-route.gif" width="75%" caption="Watch the full demo in the Test These Scenarios Yourself section below" >}}

### When a Route Is Removed

Removing a route should instantly revoke access. Lingering routes, even for a few seconds, can pose security risks and violate compliance requirements.

{{< reuse-image src="blog/scalability-delete-a-route.gif" width="75%" caption="Watch the full demo in the Test These Scenarios Yourself section below" >}}

### When the Control Plane Is Restarted or Scaled

The system should remain fully operational when the control plane restarts or scales out. Since the Envoy proxies are already configured, their behavior should not be affected. Once the control plane returns, it should not trigger unnecessary reconfigurations if there’s been no change.

## Test These Scenarios Yourself

1. [Install kgateway](https://kgateway.dev/docs/quickstart/).

2. Create the `http` gateway proxy using a Gateway resource:

```yaml
$ kubectl apply -f - <<EOF
kind: Gateway
apiVersion: gateway.networking.k8s.io/v1
metadata:
 name: http
 namespace: kgateway-system
spec:
 gatewayClassName: kgateway
 listeners:
 - protocol: HTTP
   port: 8080
   name: http
   allowedRoutes:
     namespaces:
       from: All
EOF
```

3. **(Optional)** Install the [OpenTelemetry Collector](https://kgateway.dev/docs/observability/#otel) and [kube-prometheus-stack](https://kgateway.dev/docs/observability/#grafana) to observe CPU, memory and Envoy metrics. (Make sure your cluster has adequate resources if doing this.)

4. Clone the [kgateway repo](https://github.com/kgateway-dev/kgateway). From the cloned directory, use the `applier` utilitiy to load 10,000 routes and backends (from 0 to 9999). Send a few random requests to confirm routes are effective immediately.

```bash
cd hack/utils/applier
wget https://raw.githubusercontent.com/linsun/gateway-tests/refs/heads/main/scale/routes.yaml
go run main.go apply -f routes.yaml --iterations 10000
kubectl port-forward deployment/http -n kgateway-system 8080:8080 &
curl http://localhost:8080/foo/9
curl http://localhost:8080/foo/99
curl http://localhost:8080/foo/9999
```

5. Add the 10,001st route and backend, and check if the request to the newly added route is effective immediately.

```bash
go run main.go apply -f routes.yaml --start 10000 --iterations 1
curl http://localhost:8080/foo/10000
```

6. Update the 10,001st route. Send the request with `-v` (verbose); you should see the response header `hello: kgateway` being added:

```yaml
kubectl apply -f - <<EOF
apiVersion: gateway.networking.k8s.io/v1
kind: HTTPRoute
metadata:
 generation: 1
 name: route-10000
 namespace: default
spec:
 parentRefs:
 - group: gateway.networking.k8s.io
   kind: Gateway
   name: http
   namespace: kgateway-system
 rules:
 - backendRefs:
   - group: gateway.kgateway.dev
     kind: Backend
     name: backend-10000
     weight: 1
   filters:
   - type: URLRewrite
     urlRewrite:
       path:
         replacePrefixMatch: /anything/
         type: ReplacePrefixMatch
   - type: ResponseHeaderModifier
     responseHeaderModifier:
       add:
         - name: hello
           value: kgateway
   matches:
   - path:
       type: PathPrefix
       value: /foo/10000
EOF
curl http://localhost:8080/foo/10000 -v
```

7. Delete the 10,001st route, and confirm the route is no longer functional:

```bash
kubectl delete httproute route-10000
curl http://localhost:8080/foo/10000
```

8. Delete the kgateway control plane. The CPU/memory of the Envoy proxy managed by the control plane should remain stable, and all requests should continue to work:

```bash
for i in {2..1009}
do
  curl http://localhost:8080/foo/9999
  sleep 0.1
  date
Done
```

In a new terminal window:

```bash
kubectl delete pod -l kgateway=kgateway -n kgateway-system
```

You can also watch the [video demo here](https://youtu.be/g_P1Zcdwcf0).

{{< youtube g_P1Zcdwcf0 >}}

## Wrapping Up

Scalability and stability are the foundation of kgateway. Before we add new features, we ensure the core is reliable under heavy load and across failure scenarios. If the foundation isn’t solid, everything built on top is at risk of collapsing.

To dive deeper into our control plane design, check out our previous [blog post](https://kgateway.dev/blog/five-learnings-from-seven-years-of-building-gloo-and-kgateway/#control-plane-scalability). We’d love to hear your thoughts—join us on the [kgateway slack channel](https://kgateway.dev/slack/) or [follow us on LinkedIn](https://www.linkedin.com/company/kgateway/) to keep the conversation going.
