Learn more about the gateway proxies that {{< reuse "/docs/snippets/kgateway.md" >}} supports.

## About gateway proxies {#about}

Gateway proxies are the data plane in your {{< reuse "/docs/snippets/kgateway.md" >}} setup. The data plane handles traffic between clients and servers, or backend applications.

The type of gateway proxy that you want to use depends on your use case, which is often related to the backend applications and the "direction" of the traffic.

Backend applications are commonly accessed by clients through application programming interfaces (APIs). Hence, an "API gateway" is a common use case for a gateway proxy. For more information, see the [API gateway overview topic](../overview/#api-gateway). If the client is outside your cluster, you need an ingress gateway to handle this "north-south" traffic. If the client is within the cluster or service mesh, you need an "east-west" gateway. To control traffic that leaves your environment, you need an egress gateway.

Increasingly, gateway proxies are designed to meet the challenges that are specific to artificial intelligence (AI) networking. In these scenarios, your backend applications might be cloud provider large language models (LLMs), your own LLMs and inferences, model context protocol (MCP) servers, agent-to-agent (A2A) servers, and similar AI use cases.

The best gateway proxies offer you ways to configure advanced routing, load balancing, security enforcement, protocol translation, and more. They also generate metrics and logs that you can use to monitor and troubleshoot your traffic.

## Architecture

{{< reuse "/docs/snippets/kgateway-capital.md" >}} is a control plane that manages the lifecycle of gateway proxies that adhere to the [Kubernetes Gateway API](https://gateway-api.sigs.k8s.io) spec.

When you install {{< reuse "/docs/snippets/kgateway.md" >}}, you automatically get GatewayClasses out of the box. When you create a Gateway resource based on one of these GatewayClasses, {{< reuse "/docs/snippets/kgateway.md" >}} automatically spins up a gateway proxy for you. The gateway proxy controls the data plane that routes traffic to the backend services. {{< reuse "/docs/snippets/kgateway-capital.md" >}} then configures the data plane based on the Gateway API and {{< reuse "/docs/snippets/kgateway.md" >}} custom resources that you configure, such as HTTPRoutes and TrafficPolicies. This way, you can standardize the configuration of your gateway proxies with the same set of open source resources.

For more information, see the other docs in this [About](../) section.

## Supported gateway proxies {#supported}

{{< reuse "/docs/snippets/kgateway-capital.md" >}} supports the following gateway proxies. You can use both gateway proxies in the same Kubernetes cluster, depending on your use case.

| Gateway proxy | Primary use cases | Description | Doc sections |
| --- | --- | --- | --- |
| {{< icon "kgateway" >}} kgateway | API, ingress, egress, service mesh | The kgateway project includes its own proxy that is based on Envoy, an L3/L4/L7 network proxy. Beyond Envoy, kgateway provides a set of extensions for advanced configuration, security, and traffic management features. You can also integrate kgateway with the Istio service mesh in sidecar and ambient modes. For more information, see the [kgateway FAQs](../../faqs/) and [Envoy docs](https://www.envoyproxy.io/docs/envoy/latest/intro/what_is_envoy). | The entire doc set, with the exception of the agentgateway guides. |
| {{< icon "agentgateway" >}} agentgateway | AI, A2A, MCP, LLM, Inference Extension | Agentgateway is an enterprise-grade gateway data plane that provides AI connectivity for agents and tools in any environment. For more information, see the [Agentgateway docs](https://agentgateway.dev/docs/). | <ul><li>Kgateway control plane docs, such as the [Get started guide](../../quickstart/), select [Operations guides](../../operations/), and [Reference guides](../../reference/)</li><li>[Agentgateway](../../agentgateway/) guides.</li></ul>|

## Reserved ports

{{< reuse "docs/snippets/reserved-ports.md" >}}