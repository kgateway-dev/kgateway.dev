---
title: Deployment patterns
weight: 20
---

Learn how you can deploy {{< reuse "docs/snippets/product-name.md" >}} proxies to ensure proper traffic routing, security, and isolation for your apps. 

The flexibility of {{< reuse "docs/snippets/product-name.md" >}} allows you to deploy it in a way that best serves your environment. Review the following recommended deployment patterns to choose how to set up {{< reuse "docs/snippets/product-name.md" >}} proxies.

## Simple ingress

The following image shows a {{< reuse "docs/snippets/product-name.md" >}} proxy that serves as a single ingress API gateway to the workloads in a Kubernetes cluster. The gateway is centrally managed by the {{< reuse "docs/snippets/product-name.md" >}} control plane and configured to match and forward traffic based on the traffic management, resiliency, and security rules that you define. 

{{% reuse-image src="img/pattern-simple-ingress.svg" width="400px" caption="Kgateway as a simple ingress"  %}}

This setup is a great way to get started with {{< reuse "docs/snippets/product-name.md" >}}, and is suitable for smaller environments where all workloads run in a single cluster and traffic is balanced between services. However, in larger environments or environments where you have both high traffic and low traffic services, consider adding [multiple gateway proxies to distribute traffic load more evenly](#sharded-gateway). 

## Sharded gateway {#sharded-gateway}

In larger environments or environments where you have both high traffic and low traffic services, you can isolate services from each other and protect against noisy neighbors by using a sharded gateway. With a sharded gateway architecture, you typically have multiple gateway proxies that split up the traffic for different services in the cluster as depicted in the following image. 

{{% reuse-image src="img/pattern-sharded-gateway.svg" width="400px" caption="Kgateway as a sharded gateway" %}}

All gateway proxies are managed by the {{< reuse "docs/snippets/product-name.md" >}} control plane. However, one gateway proxy manages traffic for the workloads in the `foo` and `bar` namespaces. The second gateway proxy is a dedicated API gateway for the workloads in the `extra` namespace. Both gateway proxies are exposed directly on the edge. 

While this setup is great to split up and load balance traffic across apps, you might not want the gateway proxies to be exposed directly on the edge. Instead, you might want a central ingress gateway proxy that applies common traffic management, resiliency, and security rules, and that forwards traffic to other gateway proxies that are dedicated to certain apps, teams, or namespaces. To learn more about this deployment pattern, see [Sharded gateway with central ingress](#sharded-gatway-with-central-ingress). 


## Sharded gateway with central ingress {#sharded-gatway-with-central-ingress}

The following image shows a {{< reuse "docs/snippets/product-name.md" >}} proxy that serves as the main ingress endpoint for all traffic. The gateway proxy can be configured to apply common traffic management, resiliency, and security rules to all traffic that enters the cluster. For example, you can set CORS or header manipulation policies on that gateway before you forward traffic to a second layer of gateway proxies. This is useful if you need a central IP address and DNS name for the gateway that serves all your traffic. 

The second layer of gateway proxies can apply additional traffic management, resiliency, and security policies to incoming traffic for specific apps. You also shard the second layer of proxies to better account for high and low traffic services to avoid noisy neighbor problems. All gateway proxies are managed by the same {{< reuse "docs/snippets/product-name.md" >}} control plane.

{{% reuse-image src="img/pattern-central-ingress-gloo.svg" width="600px"  %}}

Depending on your existing setup, you might want to use a different type of proxy as your central ingress endpoint. For example, you might have an HAProxy or AWS NLB/ALB instance that all traffic must go through. {{< reuse "docs/snippets/product-name.md" >}} can be paired with these types of proxies as depicted in the following image. 

{{% reuse-image src="img/pattern-central-ingress-any.svg" width="600px"  %}}

## API gateway for a service mesh

You can deploy {{< reuse "docs/snippets/product-name.md" >}} as an API gateway for any ingress and egress traffic to and from the service mesh. A service mesh uses proxies to provide central management for your cloud-native microservices architecture to optimize communication, routing, reliability, security, and observability between your apps. 

The following image shows a {{< reuse "docs/snippets/product-name.md" >}} proxy that is exposed on the edge and serves traffic for the service mesh. Services in the mesh communicate with each other via mutual TLS (mTLS). {{< reuse "docs/snippets/product-name.md" >}} proxies can be configured with an Istio sidecar to establish a trusted, mTLS connection to the services in the mesh. 

{{% reuse-image src="img/pattern-service-mesh.svg" width="600px"  %}}
