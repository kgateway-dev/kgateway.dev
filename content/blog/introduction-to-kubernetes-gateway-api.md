---
title: Introduction to the Kubernetes Gateway API
toc: false
publishDate: 2025-03-05T00:00:00-00:00
author:  Eitan Suez & Alex Ly
---

Kubernetes has come a long way since its early days of exposing services via the original Ingress API. As more workloads adopt Kubernetes, the types of traffic management needed—ingress from the outside world, service-to-service (east-west) communication within the cluster, and egress to external systems—have also become more sophisticated. 

As the various implementations of ingress controllers emerged, it became clear that having a common, extensible standard for traffic management was critical to ensure stability, portability, and widespread community adoption. Quickly becoming the de facto standard for network traffic management in Kubernetes, Gateway API (also called Kubernetes Gateway API) addresses many shortcomings of its predecessor, the Ingress API, and unifies best practices that have evolved through real-world usage. 

This blog post explores why Gateway API was created, the challenges it solves, and how a balance of flexibility and standardization drives innovation and improvements to the open source community.

## Why We Needed Something Beyond Ingress

When Kubernetes first introduced the Ingress resource, clusters were primarily concerned with accepting external traffic (north-south). The premise was straightforward: the ability to perform TLS termination, configure host-based or path-based routing from the public internet to services in the cluster, and to be able to support multiple routing rules through a shared gateway. Ingress handled many basic use cases well and quickly became a core concept in Kubernetes. However, as more organizations adopted Kubernetes in production, the limitations became clear:

**Annotations Everywhere!**
The community discovered that Ingress alone was not expressive enough when it came to advanced traffic management, resiliency, and security needs. Different ingress controllers introduced custom annotations to capture these nuances, which led to fragmentation, portability issues, and confusion.

**Service-to-Service and Egress**
Microservice adoption at scale along with the broad adoption of SaaS and other cloud-based services additionally drove the need for consistent ways to handle internal service-to-service and egress connectivity. Again, the community tackled this need, with various implementations of service mesh for example, but did not fully address the stickiness or portability issues, leading to increased complexity and poor onboarding experiences.

**Personas and Multitenancy**
Ingress was also silent on how multiple teams (platform engineers, developers, security operators) share or delegate gateway configurations. As Kubernetes grew inside large organizations, it became clear that having distinct resource definitions for each “persona” (e.g., cluster admin vs. application team) was a better approach. Additionally, the provisioning of a single shared gateway was generally performed at installation time, and coupled to the installation of the ingress controller proper because the implementation of multiple dedicated gateways was not straightforward. This led to many noisy neighbor issues in large-scale implementations.

## The Journey Toward a Common Standard

One of the core strengths of the Kubernetes ecosystem is its consistency across different environments and vendors. For example, Kubernetes users trust that a Deployment resource in one cluster means the same thing in another. The Ingress API aimed to achieve the same for external traffic but fell short due to heavy reliance on vendor-specific annotations.

Gateway API seeks to solve that by providing well-defined Kubernetes resources that align with the broader Kubernetes philosophy, consistent APIs with clear boundaries. When the community and its vendors implement the same standard resource types, it becomes far easier for end users to adopt or move between solutions with reduced friction.

Today, Gateway API is a product of collaboration between many community members, including maintainers from projects like kgateway, Istio, Envoy, Contour, NGINX, Traefik, and more. This cross-project collaboration helps to ensure that the final standard isn’t biased towards a single vendor’s perspective. Instead, it embraces the combined real-world lessons of dozens of implementers and thousands of users all across the world!

This collaboration also extends beyond just “ingress” traffic. The community recognized that the same standard could address both north-south and east-west traffic patterns, and today the GAMMA (Gateway API for Mesh Management and Administration) initiative is a part of Gateway API that addresses similar standardization needs for routing between services in-cluster and across-clusters.

## Overview of the API model

Gateway API is a family of Custom Resource Definitions (CRDs) that provide dynamic infrastructure provisioning and advanced traffic routing and can be applied to a cluster with the following command:

```
kubectl apply -f https://github.com/kubernetes-sigs/gateway-api/releases/download/v1.2.0/standard-install.yaml
```

This command will list the applied resource definitions:

```
kubectl api-resources --api-group=gateway.networking.k8s.io
```

Here is the output:

```
NAME              SHORTNAMES   APIVERSION                          NAMESPACED   KIND
gatewayclasses    gc           gateway.networking.k8s.io/v1        false        GatewayClass
gateways          gtw          gateway.networking.k8s.io/v1        true         Gateway
grpcroutes                     gateway.networking.k8s.io/v1        true         GRPCRoute
httproutes                     gateway.networking.k8s.io/v1        true         HTTPRoute
referencegrants   refgrant     gateway.networking.k8s.io/v1beta1   true         ReferenceGrant
```

### Multiple personas

{{< reuse-image src="blog/introduction-to-kubernetes-gateway-api-1.png" width="750px" >}}

A key design principle behind Gateway API is recognizing who configures what:

**Platform Engineers / Administrators:**
Use GatewayClass and Gateway to define the overall gateway capabilities, such as load balancer parameters, TLS configurations, and other security and governance considerations.

**Application Developers / Teams:**
Define HTTPRoute (or TLSRoute, etc.) resources that attach to Gateways. They control how traffic is routed to backend services, canary versions, or particular subsets of pods—without needing cluster-admin-level access.

**Security / Ops Teams:**
Leverage policy attachment points to insert custom capabilities (rate limiting, WAF configuration, etc.) in a consistent way by using [extension points](https://gateway-api.sigs.k8s.io/guides/migrating-from-ingress/?h=extensionref#approach-to-extensibility) within the API.

This separation of concerns mirrors successful design patterns in Kubernetes, such as the way storage classes are managed by platform teams while developers issue persistent volume claims. It’s a more secure and maintainable approach that fosters collaboration within organizations.

### Protocol-specific routes

Gateway API also recognizes that route configurations are protocol-specific, and so defines multiple protocol-specific types of routes:  HTTPRoute, GRPCRoute, TLSRoute, TCPRoute, and UDPRoute.  It's a simple and extensible model that is open to future extension.

### Provisioning triggered by Gateway creation

Applying the Gateway resource to a namespace triggers the creation of the corresponding Gateway deployment. This allows for on-demand creation of gateways, and makes it easy to provision dedicated gateways when necessary, for example when there is a need for greater isolation of network traffic to a specific application.

## Designed for extensibility

The design of Gateway API no longer forces implementers to resort to using annotations.

Gateway API specification explicitly defines patterns for extensibility through [policy attachments](https://gateway-api.sigs.k8s.io/reference/policy-attachment/). The idea behind policy attachments is providing a way to extend the API with resources that are unique to an implementer, and that can be associated with a Gateway or Route.

An example might be a custom resource for configuring rate limiting on requests through a particular route. The gateway and route definitions are a part of the API proper, whereas the custom CRD, for example, a CRD named RateLimitOptions, is a policy attachment associated with the route, defined by the implementer.

Below is an example where an implementation might augment Gateway API with its own CRDs:

{{< reuse-image src="blog/introduction-to-kubernetes-gateway-api-2.png" width="750px" >}}

## Looking Ahead

Gateway API is already fulfilling its promise as a widely adopted standard, [over two dozen implementations](https://gateway-api.sigs.k8s.io/implementations/) across the Kubernetes ecosystem. As the specification continues to evolve, we can expect even broader adoption and deeper [integrations for Gateway API](https://gateway-api.sigs.k8s.io/implementations/#integrations), including:

* [cert-manager](https://cert-manager.io/docs/usage/gateway/) to automate certificate management in cloud native environments using Gateway API.

* [Flagger](https://docs.flagger.app/tutorials/gatewayapi-progressive-delivery) and [Argo Rollouts](https://rollouts-plugin-trafficrouter-gatewayapi.readthedocs.io/en/latest/) to support advanced deployment methods such as blue/green and canary rollouts

* [Istio](https://istio.io/latest/docs/overview/what-is-istio/) service mesh which supports the GAMMA initiative and leverages Gateway API to program [waypoints](https://ambientmesh.io/docs/about/architecture/#gateways-and-waypoints) for service-to-service routing and policy management

## Next in the series..

Now that we’ve explored motivation for Gateway API and how it improves upon Kubernetes' traditional ingress model, it’s time to see it in action. In the next post, we’ll take a deeper dive into the core concepts of Gateway API and walk through a concrete example. 

Also, don’t forget that this blog series is accompanied by an in-depth video series which you can watch [here](https://kgateway.dev/resources/videos/) and [hands-on-labs](https://kgateway.dev/resources/labs/) for you to test out the concepts.
