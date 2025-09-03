---
title: Shared Gateways in kgateway
toc: false
publishDate: 2025-03-28T00:00:00-00:00
author: Alex Ly
excludeSearch: true
---

In [part 1](https://kgateway.dev/blog/introduction-to-kubernetes-gateway-api/) of this blog series, we explored persona-based management as a new concept of the Kubernetes Gateway API compared to the monolithic or single-owner approach of the legacy Ingress API. By defining clear roles for infrastructure providers, cluster operators, and application developers, Gateway API enables teams to work independently while still adhering to organizational policies.

In [part 2](https://kgateway.dev/blog/guide-to-installing-kgateway/), we highlighted a second key design change: the ability to configure multiple gateways within the same cluster easily. Traditionally, ingress controllers often funneled all traffic through one shared gateway, which could lead to operational complexity and potential bottlenecks. With Gateway API, teams can now choose whether to share gateways or provision dedicated ones, providing the right balance between cost efficiency, security, and operational overhead for the teams operating these gateways.

In this post, we’ll explore the design rationale behind these decisions and how they deliver value for Gateway API users.

## Flexible Gateway Provisioning

With the Ingress API, provisioning multiple gateways was not as straightforward. Typically, a single gateway was provisioned at cluster installation and then shared among a few application teams. As more teams onboarded applications to the cluster, sharing a single ingress controller started to become problematic.

## Challenges

- **Limited Flexibility** - Sharing a cluster-wide ingress model forced teams to align on the lowest common set of features, often favoring stability over innovation. Adopting new capabilities required coordination and consensus across multiple teams.
- **Lack of Separation of Concerns** - Routing rules and gateway configurations were mixed together, and often controlled by custom annotations.
- **Noisy Neighbor** - High-traffic workloads could monopolize shared resources, causing latency spikes, congestion, or even outages for other tenants.

By making Gateway provisioning a first-class concern of the API, creating a new gateway becomes as straightforward as configuring a Deployment or Service in Kubernetes. This makes it easy to provide stronger traffic isolation for sensitive workloads, while applications with less critical requirements can continue to share gateways for improved cost efficiency.

## Persona Driven Responsibilities

Another longstanding challenge in Kubernetes networking is around enabling application teams to manage their own ingress configurations without compromising security. With the Ingress API, this was difficult because teams often needed admin privileges to make changes or had to rely on centralized platform teams to do so, creating bottlenecks in delivery.

Over the years, projects such as [Gloo Gateway](https://www.solo.io/products/gloo-gateway) and [Istio](https://istio.io) have addressed this concern by introducing APIs that align with persona-driven responsibilities. These APIs define clear roles for platform administrators and application developers based on their day-to-day responsibilities. While effective, these capabilities were solution-specific, meaning each implementation that did solve this problem ended up solving it in isolation, without a common standard shared across the Kubernetes ecosystem.

Gateway API formalizes the successes and lessons learned from these projects into a standardized approach, ensuring that persona-based management is consistent across various provider implementations. By incorporating the concept of personas into the API itself, Gateway API provides governance over critical infrastructure while empowering application teams with self-service capabilities with the added benefit of avoiding vendor lock-in. This separation of concerns enables Application teams to define routing configurations without requiring cluster-admin privileges and Platform teams to manage gateway lifecycles, control which ports and hostnames are available, and enforce security policies such as TLS management. 

For a deeper dive, take a look at the section [Why does a role-oriented API matter?](https://gateway-api.sigs.k8s.io/#why-does-a-role-oriented-api-matter) in the Gateway API documentation.

## Example: Shared Gateways in Action

A great way to combine the “Flexible Gateway Provisioning” and “Persona Driven Responsibilities” concepts discussed so far is to walk through the Shared Gateway example from the Gateway API documentation. 

Here is a summary of the steps in this example:

1. **Cluster Operators** provision a gateway in a dedicated namespace (e.g., `infra`), separate from application team namespaces.
2. **Multiple Application Teams** each work in their own namespaces and deploy services there.
3. **Application Teams** create routes referencing the shared gateway in the `infra` namespace.

Below is a snippet for a `HTTPRoute` located in the `httpbin` namespace that attaches to a gateway named `infra-gateway` in the `infra` namespace:

```yaml
---
apiVersion: gateway.networking.k8s.io/v1
kind: HTTPRoute
metadata:
  name: httpbin
  namespace: httpbin
spec:
  parentRefs:
  - name: infra-gateway
    namespace: infra
    sectionName: httpbin-https
  rules:
  - backendRefs:
    - name: httpbin
      port: 8000
```
Thanks to the Gateway API’s separation of concerns, cluster operators can decide which routes can attach to a gateway. For example, the default `allowedRoutes` setting `from: Same` means only HTTPRoutes living in the same namespace as the gateway are accepted:

```yaml
---
kind: Gateway
apiVersion: gateway.networking.k8s.io/v1
metadata:
  name: infra-gateway
  namespace: infra
spec:
  gatewayClassName: kgateway
  listeners:
  - name: httpbin-https
    protocol: HTTPS
    port: 443
    hostname: httpbin.example.com
    tls:
      mode: Terminate
      certificateRefs:
      - name: httpbin-cert
    allowedRoutes:
      namespaces:
        from: Same
```
To achieve cross-namespace routing, cluster operators can devise a convention such as a specific label on the application's namespace, to give application teams permission to attach their routes, something along these lines:

```yaml
kind: Gateway
apiVersion: gateway.networking.k8s.io/v1
metadata:
  name: infra-gateway
  namespace: infra
spec:
  gatewayClassName: kgateway
  listeners:
  - name: httpbin-https
    protocol: HTTPS
    port: 443
    hostname: httpbin.example.com
    tls:
      mode: Terminate
      certificateRefs:
      - name: httpbin-cert
    allowedRoutes:
      namespaces:
        from: Selector
        selector:
          matchLabels:
            self-serve-ingress: "true"
```
Application teams that have not been given permission to program the gateway will find out through the resource's status section that their route was not accepted. In the example below, if an application team attempts to attach a route without the proper label, the status will display `reason: NotAllowedByListeners`.

```yaml
apiVersion: gateway.networking.k8s.io/v1
kind: HTTPRoute
metadata:
  name: httpbin
  namespace: httpbin
  ...
spec:
  ...
status:
  parents:
  - conditions:
    - lastTransitionTime: "2025-02-12T21:26:46Z"
      message: ""
      observedGeneration: 1
      reason: NotAllowedByListeners
      status: "False"
      type: Accepted
      ...
    parentRef:
      group: gateway.networking.k8s.io
      kind: Gateway
      name: infra-gateway
      namespace: infra
      sectionName: httpbin-https
```
These controls greatly help cluster operators manage and control which teams have access to a particular gateway or even have the ability to expose routes at all!

## Summary 
In this blog, we explored how design choices incorporating persona-driven responsibilities and flexible gateway provisioning can significantly improve multitenant Kubernetes networking. By introducing a standardized way to define and manage gateways, Gateway API enables operators and development teams to collaborate in a role-oriented manner effectively.

If you are enjoying this learning series on Gateway API, we have more for you in store! In the next part of this series, we’ll dive deeper into `HTTPRoute`, examining its routing capabilities and the policy management extensions it offers.

For a complete, hands-on example covering the concepts of shared gateways in this blog, check out our [hands-on labs](https://kgateway.dev/resources/labs/)!
