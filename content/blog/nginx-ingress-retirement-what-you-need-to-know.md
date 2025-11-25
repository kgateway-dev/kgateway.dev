---
title: "Ingress NGINX Retirement: What You Need to Know"
toc: false
publishDate: 2025-11-18T00:00:00-00:00
author: Lin Sun & Michael Levan
excludeSearch: true
---

During KubeConNA last week, the Kubernetes community [announced](https://kubernetes.io/blog/2025/11/11/ingress-nginx-retirement/) the **Ingress NGINX retirement** and recommended that users move to the **Gateway API**, which is the modern replacement for Ingress. Best-effort maintenance of Ingress NGINX will continue until **March 2026**, meaning users need a migration plan soon.

This announcement is significant—Ingress NGINX has been one of the most popular ingress controllers for traffic into Kubernetes clusters. It’s part of the core Kubernetes project with over 19,000 stars on [GitHub](https://github.com/kubernetes/ingress-nginx). In this blog, we’ll share key considerations to help you choose a replacement.

### What Is Ingress NGINX?

Before planning a migration, it’s important to understand what **Ingress** and **Ingress NGINX** are.

In Kubernetes, an **[Ingress Controller](https://kubernetes.io/docs/concepts/services-networking/ingress-controllers/)** is essential—it watches Ingress objects in the cluster and programs NGINX accordingly, routing incoming traffic to the applications in your cluster.

Here’s a simple example of an Ingress object:

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: example-ingress
  namespace: default
spec:
  rules:
  - host: example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: example-service
            port:
              number: 80
```

This config routes traffic from `example.com` to the backend service `example-service` on port 80, allowing users to reach your application from outside the cluster.

## Why Gateway API?

One challenge with the Ingress API is **inconsistent behavior across vendors**, largely due to its reliance on annotations. These overloaded annotations are project-specific and can behave unpredictably when migrating between implementations. Earlier this year, Wiz Research disclosed [several CVEs](https://www.wiz.io/blog/ingress-nginx-kubernetes-vulnerabilities) in NGINX related to annotation-based authentication or UID configuration.

Another challenge is the **lack of a proper status field**, which makes troubleshooting difficult. While you can inspect rules, events, and annotations, it’s often unclear why an Ingress isn’t working.

Because of these limitations, the Kubernetes community has been evolving the Ingress API since KubeCon 2019. The Gateway API reached **[GA](https://kubernetes.io/blog/2023/10/31/gateway-api-ga/)** in **October 2023**, making core APIs like `Gateway`, `GatewayClass`, and `HTTPRoute` stable.

## Advantages of Gateway API

What we love about the Gateway API:
- Extensibility: You can define custom traffic policies, rate limits, and more.
- Status field: Provides clear insights into whether a resource is accepted, programmed, and error-free.

Example with **kgateway** using the core Gateway and the extended TrafficPolicy resources:

```yaml
apiVersion: gateway.networking.k8s.io/v1
kind: Gateway
metadata:
  name: http
spec:
  gatewayClassName: kgateway
  listeners:
  - protocol: HTTP
    port: 80
    name: http
---
apiVersion: gateway.kgateway.dev/v1alpha1
kind: TrafficPolicy
metadata:
  name: transformation
spec:
  targetRefs:
  - group: gateway.networking.k8s.io
    kind: HTTPRoute
    name: http
  transformation:
    request:  
      add:
      - name: x-forwarded-uri
        value: 'https://{{ request_header(":authority") }}{{ request_header(":path") }}'
```

After deployment, the status field for each resource lets you see whether resources are programmed correctly and if any errors exist. Here’s an example of the status field for the `http` Gateway resource:

```yaml
status:
  addresses:
  - type: IPAddress
    value: 172.18.0.7
  conditions:
  ...
  - lastTransitionTime: "2025-11-17T22:59:37Z"
    message: Successfully accepted Gateway
    observedGeneration: 1
    reason: Accepted
    status: "True"
    type: Accepted
  - lastTransitionTime: "2025-11-17T22:59:37Z"
    message: Successfully programmed Gateway
    observedGeneration: 1
    reason: Programmed
    status: "True"
    type: Programmed
  listeners:
  - attachedRoutes: 1
    conditions:
    ...
    - lastTransitionTime: "2025-11-17T22:59:37Z"
      message: Successfully resolved all references
      observedGeneration: 1
      reason: ResolvedRefs
      status: "True"
      type: ResolvedRefs
    - lastTransitionTime: "2025-11-17T22:59:37Z"
      message: Successfully programmed Listener
      observedGeneration: 1
      reason: Programmed
      status: "True"
      type: Programmed
    name: http
```

## Envoy Proxy

Many Gateway API [implementations](https://gateway-api.sigs.k8s.io/implementations/) are built on **Envoy**, a high-performance modern proxy. Projects like Istio, kgateway, Contour, Cilium, Envoy Gateway, and Emissary-Ingress use Envoy as the data plane.

While multiple gateways may share the same data plane, the **control plane** is what sets them apart. The control plane translates Gateway API resources into Envoy configuration. For small setups, this is simple, but for large-scale deployments (e.g., 20,000 routes → 500,000+ lines of Envoy config), control plane **efficiency and scalability** are critical.

Check out our [blog](https://kgateway.dev/blog/design-kgateway-for-scalability/) on designing kgateway for scalability, which includes simple tests to evaluate control plane performance during route changes.

## Gateway API Benchmark

Performance matters. Regardless of whether your environment is bare-metal, virtualized, cloud, Kubernetes, or serverless, network speed and application responsiveness remain crucial.

One of the most thorough benchmarks comes from John Howard, who recently published [v2](https://github.com/howardjohn/gateway-api-bench/blob/main/README-v2.md) with reproducible test scripts. We recommend checking it out, running the tests in your environment, and engaging with his findings.

{{< reuse-image src="blog/nginx-ingress-retirement-1.png" caption="Resource Consumption During Route Scale Test from John’s Benchmark" >}}

## Inference and Agentic AI

According to the latest CNCF [State of Cloud Native Development Report](https://www.cncf.io/reports/state-of-cloud-native-development/), ~1/3 of cloud native developers are using AI.

{{< reuse-image src="blog/nginx-ingress-retirement-2.png" width="750px" caption="Trends in Cloud Native Development">}}

If you’re adopting AI workloads, it’s worth considering a **consistent** Gateway not only for Ingress traffic but also for inference and agentic AI workloads. The CNCF [Tech Radar](https://www.cncf.io/reports/cncf-technology-landscape-radar/) ranks gateways for inference and agentic AI usage, helping guide your selection.

{{< reuse-image src="blog/nginx-ingress-retirement-3.png" width="750px" caption="Maturity Ratings for AI Inferencing from the Tech Radar">}}

{{< reuse-image src="blog/nginx-ingress-retirement-4.png" width="600px" caption="Agentic AI Radar from the Tech Radar">}}

## Wrapping Up

With Ingress NGINX retiring soon, you need a Gateway solution that:

- Is based on the Kubernetes Gateway API.
- Provides consistent performance, whether you have 2 or 2,000 routes.
- Is open-source and ideally hosted in a vendor-neutral foundation like CNCF.
- Has a thriving community of users.
- Provides a consistent Gateway for inference and/or agentic AI workloads if your organization is using or planning to adopt AI.
- Is easy to use.

Are there any important criteria we missed for evaluating your next Gateway? We’d love to hear what matters most to you.

Good luck choosing the best replacement for NGINX Ingress! We hope your migration is as smooth as possible. If you have any questions regarding kgateway (we may be biased but we believe it meets all of the criteria above) or Istio, feel free to [reach out](https://kgateway.dev/slack/) to our maintainers for assistance.