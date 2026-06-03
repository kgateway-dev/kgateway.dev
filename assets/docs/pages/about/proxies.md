Learn more about the gateway proxies that the {{< reuse "/docs/snippets/kgateway.md" >}} {{< gloss "Control Plane" >}}control plane{{< /gloss >}} supports.

## About gateway proxies {#about}

Gateway proxies are the {{< gloss "Data Plane" >}}data plane{{< /gloss >}} in your {{< reuse "/docs/snippets/kgateway.md" >}} setup. The data plane handles traffic between clients and servers, or backend applications.

The type of gateway proxy that you want to use depends on your use case, which is often related to the backend applications and the "direction" of the traffic.

Backend applications are commonly accessed by clients through application programming interfaces (APIs). Hence, an "API gateway" is a common use case for a gateway proxy. For more information, see the [API gateway overview topic](../overview/#api-gateway). If the client is outside your cluster, you need an ingress gateway to handle this "north-south" traffic. If the client is within the cluster or service mesh, you need an "east-west" gateway. To control traffic that leaves your environment, you need an egress gateway.

Increasingly, gateway proxies are designed to meet the challenges that are specific to artificial intelligence (AI) networking. In these scenarios, your backend applications might be cloud provider large language models (LLMs), your own LLMs and inferences, model context protocol (MCP) servers, agent-to-agent (A2A) servers, and similar AI use cases. For AI, MCP, LLM, and agent connectivity, use [Agentgateway](https://agentgateway.dev/docs), which has its own documentation and installation.

The best gateway proxies offer you ways to configure advanced routing, load balancing, security enforcement, protocol translation, and more. They also generate metrics and logs that you can use to monitor and troubleshoot your traffic.

## Architecture

{{< reuse "/docs/snippets/kgateway-capital.md" >}} is a control plane that manages the lifecycle of gateway proxies that adhere to the [Kubernetes Gateway API](https://gateway-api.sigs.k8s.io) spec.

When you install {{< reuse "/docs/snippets/kgateway.md" >}}, you automatically get GatewayClasses out of the box. When you create a Gateway resource based on one of these GatewayClasses, {{< reuse "/docs/snippets/kgateway.md" >}} automatically spins up a gateway proxy for you. The gateway proxy controls the data plane that routes traffic to the backend services. {{< reuse "/docs/snippets/kgateway-capital.md" >}} then configures the data plane based on the Gateway API and {{< reuse "/docs/snippets/kgateway.md" >}} custom resources that you configure, such as HTTPRoutes and TrafficPolicies. This way, you can standardize the configuration of your gateway proxies with the same set of open source resources.

For more information, see the other docs in this [About](../) section.

## Reserved ports

{{< reuse "docs/snippets/reserved-ports.md" >}}
