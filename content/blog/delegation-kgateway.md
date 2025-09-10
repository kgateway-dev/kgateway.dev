---
title: Delegation in kgateway - scaling routing with multi-tenant ownership
toc: false
publishDate: 2025-05-09T00:00:00-00:00
author: Alex Ly
excludeSearch: true
---

As environments scale, traffic routing through Kubernetes gateways naturally becomes increasingly complex. Microservices architecture adoption tends to amplify this challenge as what used to be a single route for a monolith becomes hundreds or even thousands of path-based matchers across services, often bundled under a shared hostname. 

While it's technically possible to configure all routes in a single HTTPRoute resource, this monolithic approach doesn't scale well in multi-team environments. A common failure mode observed is a situation where Team A inadvertently configures a route or policy that impacts Team B or Team C, potentially causing outages or other traffic-related issues.

Thankfully, API gateways such as kgateway have long solved this multi-tenancy problem by providing a feature called Route Delegation, which allows the user to split up complex routes into smaller, independently owned units. These units can form a routing hierarchy, where policies and matchers are delegated from parent routes to child routes, and even grandchild routes. 

By allowing a complete route be assembled from separate config, we can form a tree of config objects which allow us to achieve the following benefits:

| **Benefit** | **Description** |
|-------------|-----------------|
| Organize routing rules by user groups | With route delegation, you can break up large routing configurations into smaller routing configurations which makes them easier to maintain and to assign ownership to. Each routing configuration in the routing hierarchy contains the routing rules and policies for only a subset of routes. |
| Restrict access to routing configuration | Because route delegation lets you break up large routing configurations into smaller, manageable pieces, you can easily assign ownership and restrict access to the smaller routing configurations to the individual or teams that are responsible for a specific app or domain. For example, the network administrator can configure the top level routing rules, such as the hostname and main route match, and delegate the individual routing rules to other teams. |
| Simplify blue-green route testing | To test new routing configuration, you can easily delegate a specific number of traffic to the new set of routes. |
| Optimize traffic flows | Route delegation can be used to distribute traffic load across multiple paths or nodes in the cluster, which can improve network performance and reliability. |
| Easier updates with limited blast radius | Individual teams can easily update the routing configuration for their apps and manage the policies for their routes. If errors are introduced, the blast radius is limited to the set of routes that were changed. |

## Use Case: Shared Gateway, Isolated Ownership

Imagine a platform team managing a shared ingress Gateway for multiple API teams. The platform team defines which hostnames and top-level paths (like `/api/reviews` or `/api/details`) are allowed, but delegates ownership of what happens beyond those paths to specific namespaces.

For example:

- The **platform team** defines the public interface (`bookinfo.example.com/api/reviews`) but doesn't care how traffic is split between `/v1`, `/v2`, etc.

- The **reviews team** owns the internal routing logic—versioning, rewrites, backend selection—within their namespace.

In the lab example, we follow a similar scenario where leveraging kgateway delegation provides us a separation of responsibilities to help reduce operational bottlenecks and improve developer velocity - allowing teams to independently modify or version their routes without opening platform tickets or waiting for centralized approval.

In order to accomplish this, we first create the following `HTTPRoute` manifests in our cluster first starting with the parent route

```yaml
apiVersion: gateway.networking.k8s.io/v1
kind: HTTPRoute
metadata:
  name: parent
spec:
  parentRefs:
  - name: my-gateway
  hostnames:
  - bookinfo.example.com
  rules:
  - matches:
    - path:
        type: PathPrefix
        value: /api/reviews
    backendRefs:
    - group: gateway.networking.k8s.io
      kind: HTTPRoute
      name: "*"
      namespace: reviews
  - matches:
    - path:
        type: PathPrefix
        value: /api/details
    backendRefs:
    - group: gateway.networking.k8s.io
      kind: HTTPRoute
      name: "*"
      namespace: details
```

This parent route achieves two key goals:

1. **Defines base-level constraints**: Only traffic for `bookinfo.example.com` and certain top-level paths is allowed.

2. **Delegates routing authority**: Requests matching `/api/reviews` or `/api/details` are forwarded to child `HTTPRoute` resources in the `reviews` and `details` namespaces, respectively.

**Note:** The `backendRefs` here point to other `HTTPRoute` objects—not `Service` objects—enabling **chained routing logic**. This allows child routes to fully own how traffic is handled beyond the initial match.

Next, we configure the following child `HTTPRoute` resource for each respective team, in this case the `reviews` and `details` API teams, which inherit the host and its routing hierarchy from the parent route configured in the previous step.

**Child Route #1:**

```yaml
apiVersion: gateway.networking.k8s.io/v1
kind: HTTPRoute
metadata:
  name: reviews
  namespace: reviews
spec:
  rules:
  - matches:
    - path:
        type: PathPrefix
        value: /api/reviews
    filters:
    - type: URLRewrite
      urlRewrite:
        path:
          type: ReplacePrefixMatch
          replacePrefixMatch: /reviews
    backendRefs:
    - name: reviews
      port: 9080
```

**Child Route #2:**

```yaml
apiVersion: gateway.networking.k8s.io/v1
kind: HTTPRoute
metadata:
  name: details
  namespace: details
spec:
  rules:
  - matches:
    - path:
        type: PathPrefix
        value: /api/details
    filters:
    - type: URLRewrite
      urlRewrite:
        path:
          type: ReplacePrefixMatch
          replacePrefixMatch: /details
    backendRefs:
    - name: details
      port: 9080
```

Why do the child routes matter? These child routes are the entry point for API autonomy, allowing developers to define routing logic for their particular application - how traffic is processed, rewritten, and forwarded - all without affecting other tenants on the shared gateway. Specifically, the following benefits can be observed when using delegation:

**Team autonomy and velocity:** Developers can modify, version, or extend their routing logic (e.g. split traffic between `/v1`, `/v2`, etc.) without waiting on the platform team or modifying the shared gateway. This accelerates development and deployment workflows.

Example:

A team wants to A/B test between two backends. They can add weighted routes or request-based match conditions in their child route independently.

**Logical separation of concerns:** The platform team manages global ingress policy (e.g., only exposing `/api/reviews`) while the API team manages internal business logic and backend routing under that prefix. This separation supports least privilege access and prevents unrelated teams from affecting shared ingress behavior.

**URL decoupling and abstraction:** The external path (`/api/reviews`) is decoupled from internal application routing (`/reviews`). This allows developers the ability to change internal app structure without affecting the public APIs and is especially helpful in API versioning, migrations, or exposing legacy systems behind modern URLs.

**Scoped permissions and governance:** Because child routes live in the team's namespace, RBAC can enforce that only the owning team can edit them. Platform teams can enforce naming conventions and restrict delegation scopes in the parent route.

**Reusability and modularity:** Child routes can evolve independently and be composed into higher-order routing structures (e.g. introducing a "grandchild" route)

## Summary

In this blog, we explored how route delegation in kgateway is a powerful tool for scaling API gateway management and providing API autonomy across teams in large multitenant environments. It combines:

- Clear separation of responsibilities
- Safe and flexible developer self-service
- Enforced governance and policy inheritance

If you are enjoying this learning series on Gateway API, we have more for you in store so stay tuned!

For a complete, hands-on example covering the concepts of shared gateways in this blog, check out our [video](https://youtu.be/5uUGN4Qn_1c) and [hands-on lab](https://www.solo.io/resources/lab/route-delegation-in-kgateway?web&utm_source=organic%20&utm_medium=FY26&utm_campaign=WW_GEN_LAB_kgateway.dev&utm_content=community) on route delegation!