---
title: Microgateway Patterns with kgateway and Ambient
toc: false
publishDate: 2025-04-04T00:00:00-00:00
author: Ram Vennam
excludeSearch: true
---

# Microgateway Patterns with kgateway and Ambient

Legacy API gateways like Apigee and cloud provider API gateways have long been used to manage API traffic, especially for ingress. They run in a stand-alone model and provide "big front door" style perimeter security capabilities. They were designed for monolith workloads running on virtual machines (VMs). However, their capabilities quickly fall short when managing dynamic container workloads in a Kubernetes cluster, between clusters, or across cloud-native environments.

By virtue of sitting outside the Kubernetes cluster, further away from the workloads, these gateways also **lack native awareness of Kubernetes** networking, configuration, service discovery, or pod lifecycles. This limits their capabilities, as the Kubernetes cluster essentially becomes a black box for them. Application-aware routing, advanced rate-limiting, pod-level session affinity, and canary deployments, among other features, are more complex to achieve.

{{< reuse-image src="blog/microgateway-patterns-2.png" width="750px" >}}

**Developer experience** is also poor, as these gateways require users to learn and use non-Kubernetes-native tools, UIs, and proprietary APIs instead of working with familiar Kubernetes resources like CRDs. Often, separate teams manage the gateway configuration, and developers have to interact with them using ticket-ops methodologies instead of being able to safely self-service. This dramatically slows down development and delivery speed.

**Security and latency** are also concerns. External API gateways cannot transparently enforce authentication and authorization between services within a cluster or across clusters, making it difficult to implement fine-grained security policies at the service level. To work around this, users often route service-to-service traffic externally and back, adding unnecessary round trips and making troubleshooting more difficult.

To address these challenges, we need a modern API gateway that can be deployed in a way that aligns better with how we deploy our applications.

## Moving API Gateway Capabilities Closer to Workloads

Similar to how modern applications broke apart monoliths into microservices, modern API gateway patterns require us to do the same. Use lightweight, purpose-built proxies deployed where needed, scaled to meet traffic demands, and programmed using declarative configuration with central control planes.

Many users start this journey by focusing on ingress first. A modern API gateway like kgateway, built on [Envoy](https://www.envoyproxy.io/), sits at the edge of the cluster to handle all incoming traffic. While network load balancers manage basic L4 routing, the gateway takes care of TLS termination, security checks, and routing requests to the right services, whether that's within the cluster or outside. It integrates naturally with Kubernetes—you configure it with CRDs, which allow you to package them into Helm charts, and you scale and manage its lifecycle using Kubernetes. This makes it easy for teams already familiar with Kubernetes to manage and extend.

After solving the ingress, users look at service-to-service communication next. The lines between north-south and east-west start to blur as this traffic often needs similar security requirements. Zero trust requires you to not trust anyone, including other services running in the same cluster. This is where a service mesh comes in.

For service-to-service communication, sidecar-based Istio solved this problem by moving the microgateway concept to the extreme—where every single pod had its own sidecar proxy acting as a microgateway. While this provided fine-grained control, it also introduced resource and operational overhead.

Sidecar-less [Istio Ambient mesh](https://ambientmesh.io/) to the rescue. Most applications don't need a full-blown layer 7 proxy sitting next to every pod. Instead, they just need a layer that can handle encryption, authentication, and authorization, which can be managed at the node level. This is the fundamental idea behind ztunnel in Istio Ambient mesh.

For workloads that do require more advanced traffic management, the microgateway model still applies. However, instead of deploying a sidecar for each instance, a shared proxy can be used per workload or namespace, called a waypoint. Waypoints allow services to apply API gateway functionality without forcing every pod to run a dedicated proxy.

This brings us to a best-of-both-worlds model, where networking and security enforcement happen closer to the application, with different layers handling different concerns. This layered model provides a more scalable, adaptable, and Kubernetes-native approach to managing service-to-service traffic.

## Kgateway as ingress and waypoint

One of the biggest advantages of Istio Ambient waypoints is that they can be [swapped with kgateway](https://www.youtube.com/watch?v=B8oZ1seIDIM), allowing kgateway to act as both an ingress and a waypoint. This offers several advantages:

- Platform teams manage the main kgateway proxy for ingress traffic, applying global security policies and delegating routing to application teams (e.g., OpenID/OAuth authentication, JWT claims to headers, and global rate limiting).

- Application teams can optionally deploy kgateway waypoints, which serve as microgateways for their services, giving them control over fine-grained routing, such as claim-based routing, additional security policies, local rate-limiting, and request transformations—all without being dependent on platform teams.

- A single control plane simplifies lifecycle management, while the [Kubernetes Gateway API](https://gateway-api.sigs.k8s.io/) ensures a Kubernetes-native experience with broad ecosystem support.

- Gateways can be added to a mesh to leverage [cross-cluster routing capabilities](https://www.youtube.com/watch?v=94vhMLqMqbI) to achieve high availability and failover at the service level.

{{< reuse-image src="blog/microgateway-patterns-1.png" width="750px" >}}

## In Conclusion

Traditional API gateways weren't built for modern, Kubernetes-based applications. They sit outside the cluster, making security, traffic management, and developer workflows more complicated. Teams often deal with slow, ticket-driven processes, added latency, and limited capabilities.

By bringing API gateway capabilities closer to where applications run, we get a faster, more flexible, and secure approach. Kgateway, combined with Istio Ambient, lets platform teams manage ingress while giving application teams control over their routing and security—all without the complexity of sidecars or external gateways.