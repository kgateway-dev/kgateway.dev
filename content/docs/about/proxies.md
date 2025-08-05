---
title: Gateway proxies
weight: 30
---

Learn more about the gateway proxies that {{< reuse "/docs/snippets/kgateway.md" >}} supports.

## About gateway proxies {#about}

Gateway proxies are network components that handle traffic between clients and servers, or backend applications. Because the clients typically request services from backend applications in the form of APIs, these proxies are also known as API gateways. Although the traffic is often "north-south" ingress traffic, a gateway proxy can also be used to route traffic between services in the same local environment, such as a service mesh, or "east-west" traffic. They can also be used to secure traffic that leaves the local environment, or "egress" traffic. 

Gateway proxies offer you ways to configure advanced routing, load balancing, security enforcement, and protocol translation. They also generate metrics and logs that you can use to monitor and troubleshoot your traffic.

## Architecture

{{< reuse "/docs/snippets/kgateway-capital.md" >}} is a control plane that manages the lifecycle of gateway proxies that adhere to the [Kubernetes Gateway API](https://gateway-api.sigs.k8s.io) spec.

When you install {{< reuse "/docs/snippets/kgateway.md" >}}, you automatically get GatewayClasses out of the box. When you create a Gateway resource based on one of these GatewayClasses, {{< reuse "/docs/snippets/kgateway.md" >}} automatically spins up a gateway proxy for you. The gateway proxy controls the data plane that routes traffic to the backend services. {{< reuse "/docs/snippets/kgateway-capital.md" >}} then configures the data plane based on the Gateway API and {{< reuse "/docs/snippets/kgateway.md" >}} custom resources that you configure, such as HTTPRoutes and TrafficPolicies.

For more information, see the other docs in this [About](../) section.

## Supported gateway proxies {#supported}

Kgateway supports the following gateway proxies. You can use both gateway proxies in the same Kubernetes cluster, depending on your use case.

| Gateway proxy | Primary use cases | Description | Doc sections |
| --- | --- | --- | --- |
| Kgateway proxy | L3/L4 and L7 network proxy for advanced API, ingress, and egress gateway | The kgateway project includes its own kgateway proxy that is based on Envoy. Beyond Envoy, kgateway provides a set of extensions for advanced configuration, security, and traffic management features. For more information, see the [kgateway FAQs](../../faqs/) and [Envoy docs](https://www.envoyproxy.io/docs/envoy/latest/intro/what_is_envoy). | The entire doc set, with the exception of the agentgateway guides. |
| Agentgateway | AI-first, MCP, agent-to-agent (A2A), and API gateway | Agentgateway is an enterprise-grade gateway data plane that provides AI connectivity for agents and tools in any environment. For more information, see the [Agentgateway docs](https://agentgateway.dev/docs/). | <ul><li>Kgateway control plane docs, such as the [Get started guide](../../quickstart/), select [Operations guides](../../operations/), and [Reference guides](../../reference/)</li><li>[Agentgateway](../../agentgateway/) guides.</li></ul>|
