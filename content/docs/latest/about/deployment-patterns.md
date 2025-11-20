---
title: Deployment patterns
weight: 20
---

Learn how you can deploy gateway proxies to ensure proper traffic routing, security, and isolation for your apps. 

The flexibility of {{< reuse "/docs/snippets/kgateway.md" >}} allows you to deploy it in a way that best serves your environment. Review the following recommended deployment patterns to choose how to set up gateway proxies.

## API Gateway and ingress controller

Use {{< reuse "docs/snippets/kgateway.md" >}}'s Envoy gateway proxy as a fast and flexible Kubernetes-native ingress controller and next-generation API gateway to aggregate and provide uniform access to your APIs. 

### Simple ingress

The following image shows a gateway proxy that serves as a single ingress API gateway to the workloads in a Kubernetes cluster. The gateway is centrally managed by the {{< reuse "/docs/snippets/kgateway.md" >}} control plane and configured to match and forward traffic based on the traffic management, resiliency, and security rules that you define. 

{{% reuse-image src="img/pattern-simple-ingress.svg" width="400px" caption="Simple ingress"  %}}
{{% reuse-image-dark srcDark="img/pattern-simple-ingress.svg" width="400px" caption="Simple ingress"  %}}

<!--Source https://app.excalidraw.com/s/AKnnsusvczX/1HkLXOmi9BF-->

This setup is a great way to get started with {{< reuse "/docs/snippets/kgateway.md" >}}, and is suitable for smaller environments where all workloads run in a single cluster and traffic is balanced between services. However, in larger environments or environments where you have both high traffic and low traffic services, consider adding [multiple gateway proxies to distribute traffic load more evenly](#sharded-gateway). 

### Sharded gateway {#sharded-gateway}

In larger environments or environments where you have both high traffic and low traffic services, you can isolate services from each other and protect against noisy neighbors by using a sharded gateway. With a sharded gateway architecture, you typically have multiple gateway proxies that split up the traffic for different services in the cluster as depicted in the following image. 

{{% reuse-image src="img/pattern-sharded-gateway.svg" width="400px" caption="Sharded gateway" %}}
{{% reuse-image-dark srcDark="img/pattern-sharded-gateway.svg" width="400px" caption="Sharded gateway" %}}

<!--Source https://app.excalidraw.com/s/AKnnsusvczX/1HkLXOmi9BF-->

All gateway proxies are managed by the {{< reuse "/docs/snippets/kgateway.md" >}} control plane. However, one gateway proxy manages traffic for the workloads in the `foo` and `bar` namespaces. The second gateway proxy is a dedicated API gateway for the workloads in the `extra` namespace. Both gateway proxies are exposed directly on the edge. 

While this setup is great to split up and load balance traffic across apps, you might not want the gateway proxies to be exposed directly on the edge. Instead, you might want a central ingress gateway proxy that applies common traffic management, resiliency, and security rules, and that forwards traffic to other gateway proxies that are dedicated to certain apps, teams, or namespaces. To learn more about this deployment pattern, see [Sharded gateway with central ingress](#sharded-gatway-with-central-ingress). 


### Sharded gateway with central ingress {#sharded-gatway-with-central-ingress}

The following image shows a gateway proxy that serves as the main ingress endpoint for all traffic. The gateway proxy can be configured to apply common traffic management, resiliency, and security rules to all traffic that enters the cluster. For example, you can set header manipulation policies on that gateway before you forward traffic to a second layer of gateway proxies. This is useful if you need a central IP address and DNS name for the gateway that serves all your traffic. 

The second layer of gateway proxies can apply additional traffic management, resiliency, and security policies to incoming traffic for specific apps. You also shard the second layer of proxies to better account for high and low traffic services to avoid noisy neighbor problems. All gateway proxies are managed by the same {{< reuse "/docs/snippets/kgateway.md" >}} control plane.

{{% reuse-image src="img/pattern-central-ingress-gloo.svg" width="600px"  %}}
{{% reuse-image-dark srcDark="img/pattern-central-ingress-gloo.svg" width="600px"  %}}

<!--Source https://app.excalidraw.com/s/AKnnsusvczX/1HkLXOmi9BF-->

Depending on your existing setup, you might want to use a different type of proxy as your central ingress endpoint. For example, you might have an HAProxy or AWS NLB/ALB instance that all traffic must go through. Kgateway can be paired with these types of proxies as depicted in the following image. 

{{% reuse-image src="img/pattern-central-ingress-any.svg" width="600px"  %}}
{{% reuse-image-dark srcDark="img/pattern-central-ingress-any.svg" width="600px"  %}}

<!--Source https://app.excalidraw.com/s/AKnnsusvczX/1HkLXOmi9BF-->

## Service mesh gateway

{{< reuse "/docs/snippets/kgateway-capital.md" >}} integrates seamlessly with your Istio service mesh so that you can control and manage ingress, {{< gloss "Egress" >}}egress{{< /gloss >}}, and mesh-internal traffic. 

### Ambient mesh

You can deploy {{< reuse "/docs/snippets/kgateway.md" >}} as an ingress, egress, or waypoint proxy gateway for the workloads in an Istio ambient mesh. An ambient mesh uses node-level ztunnels to route and secure Layer 4 traffic between pods with mutual TLS (mTLS). Waypoint proxies enforce Layer 7 traffic policies whenever needed.

The following image shows a gateway proxy that is exposed on the edge and serves traffic for the ambient mesh. Services in the mesh communicate with each other via mutual TLS (mTLS). 

{{% reuse-image src="img/ambient-ingress.svg" width="600px"  %}}
{{% reuse-image-dark srcDark="img/ambient-ingress.svg" width="600px"  %}}

<!--Source https://app.excalidraw.com/s/AKnnsusvczX/1HkLXOmi9BF-->

For more information, see the guides for using {{< reuse "/docs/snippets/kgateway.md" >}} as an [ingress gateway](../../integrations/istio/ambient/ambient-ingress/) or [waypoint proxy](../../integrations/istio/ambient/waypoint/) for your ambient mesh. 

### Sidecar mesh

You can deploy {{< reuse "/docs/snippets/kgateway.md" >}} with an Istio sidecar to route traffic to services in an Istio sidecar mesh. The following image shows a gateway proxy that is exposed on the edge and serves traffic for the sidecar mesh. Services in the mesh communicate with each other via mutual TLS (mTLS) by using the istio-proxy sidecar that is injected into the app. The sidecar is represented with the Envoy logo in the image. 

{{< reuse-image src="img/sidecar-ingress.svg" width="800px" >}}
{{< reuse-image-dark srcDark="img/sidecar-ingress.svg" width="800px" >}}

<!--Source https://app.excalidraw.com/s/AKnnsusvczX/1HkLXOmi9BF-->

For more information, see the guide for using {{< reuse "/docs/snippets/kgateway.md" >}} as an [ingress gateway](../../integrations/istio/sidecar/ingress/) to your sidecar mesh. 

## AI and Agentic Gateway

Traditional API gateways, reverse proxies, and AI gateways like Envoy were designed for REST-style microservices. In those systems, a gateway takes short-lived HTTP requests from a client, picks a backend, and forwards the request there. Agentic AI workloads are different. They keep long-lived state and exchange bidirectional messages. Such workloads also typically are resource intensive. As such, traditional gateways can experience performance impacts or even failure. Instead, AI workloads need a gateway that handles sessions and message context at scale.

[Agentgateway](https://agentgateway.dev/docs/about/introduction/) is an open source, highly available, highly scalable, and enterprise-grade data plane that provides AI connectivity for AI agents, MCP tool servers, and LLM providers. You can use {{< reuse "docs/snippets/kgateway.md" >}} as the control plane to quickly spin up and manage the lifecycle of agentgateway proxies in Kubernetes environments. In addition, you get {{< reuse "docs/snippets/kgateway.md" >}}'s enterprise-grade security, observability, resiliency, reliability, and multi-tenancy features. 

{{< reuse-image src="img/kgateway-agw.svg" >}}
{{< reuse-image-dark srcDark="img/kgateway-agw.svg" >}}

For more information, see [About {{< reuse "docs/snippets/agentgateway.md" >}}]({{< link-hextra path="/agentgateway/about/" >}}).
