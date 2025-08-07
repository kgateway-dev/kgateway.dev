---
title: Understanding Gateway API Basics
toc: false
publishDate: 2025-04-05T00:00:00-00:00
author: James Ilse
excludeSearch: true
---

# Understanding Gateway API Basics

In the previous blog in this series, we discussed the Kubernetes Gateway API at a higher level. In this blog, we build a more practical example by building out the Gateway object and then applying a route.

If you've been following along with the series and have completed the [previous installation step](https://kgateway.dev/blog/guide-to-installing-kgateway), skip to the **Creating a Gateway Object** section below.

Firstly, the Kubernetes Gateway API's [Custom Resource Definitions](https://kubernetes.io/docs/concepts/extend-kubernetes/api-extension/custom-resources/) (CRDs) must be explicitly applied to the cluster:

```bash
kubectl apply -f https://github.com/kubernetes-sigs/gateway-api/releases/download/v1.2.1/standard-install.yaml
```

As the API continues to evolve, you can access the features coming soon by using the [experimental channel](https://gateway-api.sigs.k8s.io/guides/#install-experimental-channel) with additional CRDs that haven't yet reached the "stable" status.

We can verify that the necessary resource definitions are in place by doing the following:

```yaml
k api-resources --api-group=gateway.networking.k8s.io
```

The output should resemble:

```yaml
gatewayclasses                      gc                   gateway.networking.k8s.io/v1        false        GatewayClass
gateways                            gtw                  gateway.networking.k8s.io/v1        true         Gateway
grpcroutes                                               gateway.networking.k8s.io/v1        true         GRPCRoute
httproutes                                               gateway.networking.k8s.io/v1        true         HTTPRoute
referencegrants                     refgrant             gateway.networking.k8s.io/v1beta1   true         ReferenceGrant

```

This is a list of all the installed CRDs (think of them as just API specs at this point; we will be building actual resources based on their spec). In this blog, we are just covering the creation of the bare necessities, a gateway, and a route.

While that covers the CRDs needed for the Kubernetes Gateway API spec, you still need something to process the configuration. In our case, it's going to be [kgateway](http://kgateway.dev), which we will install with helm:

```yaml
#install kgateway CRDs
helm upgrade -i --create-namespace --namespace kgateway-system --version v2.0.0-main kgateway-crds oci://cr.kgateway.dev/kgateway-dev/charts/kgateway-crds

#install kgateway
helm upgrade -i --namespace kgateway-system --version v2.0.0-main kgateway oci://cr.kgateway.dev/kgateway-dev/charts/kgateway

#check installation (will output a pod with a kgateway- prefix)
kubectl get pods -n kgateway-system
```

## Creating a Gateway Object

The concrete implementation that a Gateway leverages is specified by referencing the name of a [GatewayClass](https://gateway-api.sigs.k8s.io/api-types/gatewayclass/), which in turn is associated with a specific controller.

Let us then proceed to assume the role of the cluster operator, primarily concerned with creating gateways and governing what ports and protocols to expose.

For that, the Gateway API provides the [Gateway](https://gateway-api.sigs.k8s.io/api-types/gateway/#gateway) resource:

```yaml
kubectl apply -f- <<EOF
apiVersion: gateway.networking.k8s.io/v1
kind: Gateway
metadata:
  name: http
  namespace: kgateway-system
  labels:
    example: httpbin
spec:
  gatewayClassName: kgateway
  listeners:
  - protocol: HTTP
    port: 80
    name: http
    allowedRoutes:
      namespaces:
        from: All
EOF
```

Above, we see that the two main facets of the specification are:

1. the association, or reference to the `gatewayClassName` - the specific implementation of the API
2. the listeners section, what ports and protocols we wish to "open" or make available for ingress

One interesting facet of each listener is the `allowedRoutes` field, which gives the operator control over the association of routes to this particular gateway. The above example allows routes defined in any namespace to attach to this gateway. By expanding upon this, you can delegate routes to other applications, allowing application teams to control their own routes instead of the traditional ingress way of having your operations team handle all routing.

We will explore a more practical example of the usage of `allowedRoutes` in an upcoming lesson on the subject of shared gateways.

Applying the Gateway resource accomplishes two distinct tasks:

1. the "on-demand" provisioning of a gateway to the same namespace where the resource is applied, and
2. the subsequent "programming" of the gateway - the instructions to define an HTTP listener on port 80.

Per [Objects in Kubernetes](https://kubernetes.io/docs/concepts/overview/working-with-objects/#object-spec-and-status), the `status` section of the resource is updated by the control plane to inform us of the status of these tasks.

Check the status of the gateway with:

```yaml
kubectl get gtw -n kgateway-system http -o yaml
```

```yaml
apiVersion: gateway.networking.k8s.io/v1
kind: Gateway
metadata:
  name: http
  namespace: gloo-system
...
spec:
  gatewayClassName: gloo-gateway
  listeners:
  - allowedRoutes:
      namespaces:
        from: All
    name: http
    port: 80
    protocol: HTTP
status:
  addresses:
  - type: IPAddress
    value: ...
  conditions:
    [...]
  listeners:
  - attachedRoutes: 0
    conditions:
      ...
```

Above, note how the status section informs us of the IP address associated with the Gateway, and the `conditions` section provides feedback in terms of whether the Gateway configuration was accepted and programmed.to

Indeed, we can instruct Kubernetes to wait for that "Programmed" condition to transition to "true" before proceeding:

```yaml
kubectl wait --for=condition=Programmed=True -n kgateway-system gtw/http
```

The gateway is provisioned, and we can inspect the pods and service in the namespace in question that represent, in this case, the Envoy proxy that will govern ingress to the cluster.

Since routing rules have yet to be defined for this gateway, an HTTP request to the Gateway's IP address on the matching port should produce a 404 "Not Found" response.

Let us next assume the role of the application developer, primarily concerned with defining routes to their backend APIs and applications.

This is performed by "attaching" a route to the Gateway that the cluster operator has provisioned.

Let's build out a simple `httpbin` so we can attach a route to it and have it return traffic:

```yaml
kubectl apply -f https://raw.githubusercontent.com/kgateway-dev/kgateway/refs/heads/main/examples/httpbin.yaml
```

Once that's in place, we can apply [HTTPRoute](https://gateway-api.sigs.k8s.io/api-types/httproute/) below to attach to it:

```yaml
kubectl apply -f- <<EOF
apiVersion: gateway.networking.k8s.io/v1
kind: HTTPRoute
metadata:
  name: httpbin
  namespace: httpbin
  labels:
    example: httpbin
spec:
  parentRefs:
  - name: http
    namespace: kgateway-system
  hostnames:
  - "httpbin.example.com"
  rules:
  - backendRefs:
    - name: httpbin
      port: 8000
EOF
```

Note the three parts of the "spec":

1. `parentRefs` - what "parent reference" (think Gateway) does this route attach to? Note that you can have multiple gateways for multiple reasons.
2. `hostnames` - what hostnames should we match against?
3. `rules` - one or more routing rules that specify how matching incoming requests should be routed

The configuration states that requests to the hostname `httpbin.example.com` should be routed to the `httpbin` backend service listening on port 8000.

Once the route is applied, the control plane takes care to update the configuration of (i.e., to "re-program") the gateway with the routing rule.

Inspect the status section of the route resource to verify whether the parent reference was resolved successfully and whether the route was "accepted" (recall the `allowedRoutes` stanza on the gateway):

```yaml
kubectl get httproute -n httpbin -o yaml
```

The resource's status from the output:

```yaml
...
status:
  parents:
  - conditions:
    - lastTransitionTime: "2025-01-29T23:30:10Z"
      message: ""
      observedGeneration: 1
      reason: Accepted
      status: "True"
      type: Accepted
    - lastTransitionTime: "2025-01-29T23:30:10Z"
      message: ""
      observedGeneration: 1
      reason: ResolvedRefs
      status: "True"
      type: ResolvedRefs
    controllerName: solo.io/gloo-gateway
    parentRef:
      group: gateway.networking.k8s.io
      kind: Gateway
      name: http
      namespace: gloo-system
```

All that remains is to verify that requests to the hostname `httpbin.example.com` that resolve to the gateway's IP address are indeed routed to the `httpbin` service. There are a couple of ways of doing this.

The quick and dirty way is to port forward and check. This is great if you are running a test cluster on your laptop or don't have a way to route to service external-ips:

```yaml
#fork a port-forward
kubectl port-forward --address localhost service/http -n kgateway-system 8084:80 &

#curl the portforwarded endpoint
curl -v -o /dev/null http://127.0.0.1:8084 -H "host: httpbin.example.com"
#remove port forward
ps aux | grep -i kubectl | grep -i port-forward | grep -v grep | awk {'print $2'} | xargs kill
```

If you are on a more proper cluster (GKE/EKS/AKS/etc) and have a route to connect to an exposed Kubernetes service, you can verify it like this:

```yaml
export GW_IP=$(kubectl get gtw -n kgateway-system http -ojsonpath='{.status.addresses[0].value}')
curl -v -o /dev/null http://$GW_IP:80 -H "host: httpbin.example.com"
```

In a production environment, you would match a DNS record to the host instead of altering the header host tag, which we do just for testing purposes. In either case, the response should resemble the following output:

```yaml
[...]
> GET / HTTP/1.1
> Host: httpbin.example.com
> User-Agent: curl/8.5.0
> Accept: */*
>
< HTTP/1.1 200 OK
< access-control-allow-credentials: true
< access-control-allow-origin: *
< content-security-policy: default-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' camo.githubusercontent.com
< content-type: text/html; charset=utf-8
< date: Tue, 01 Apr 2025 01:02:21 GMT
< x-envoy-upstream-service-time: 0
< server: envoy
< transfer-encoding: chunked
[...]
```

What we've done is send traffic through the gateway service, which is defined and controlled by the Kubernetes API gateway specification, to the underlying httpbin service. This is the most basic and regular process that most operations teams will be implementing with an API Gateway.

## In Summary

Those are the basics of the Gateway API: Gateways that cluster operators can provision and configure on-demand, and routes that application teams can self-service for their backend applications.

In subsequent lessons, we will discuss shared vs dedicated gateways, configuring routes that involve TLS certificates (https), and more. Make sure to check out the free [corresponding lab](https://www.solo.io/resources/lab/understanding-the-basics-of-kubernetes-gateway-api-with-kgateway?web&utm_source=organic&utm_medium=FY26&utm_campaign=WW_GEN_LAB_kgateway.dev&utm_content=community) and [video](https://youtu.be/j89S4tV192g) on understanding the basics of Gateway API.