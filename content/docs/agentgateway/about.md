---
title: About
weight: 10
---

[Agentgateway](https://agentgateway.dev/) is an open source, highly available, highly scalable, and enterprise-grade data plane that provides AI connectivity for agents and tools in any environment. For Kubernetes environments, agentgateway supports the Kubernetes Gateway API. {{< reuse "/docs/snippets/kgateway-capital.md" >}} acts as the control plane to translate Gateway API and {{< reuse "/docs/snippets/kgateway.md" >}} custom resources into proxy configuration for the agentgateway data plane.

Agentgateway supports many agent connectivity use cases, including the following:

* Agent-to-agent (A2A)
* Model Context Protocol (MCP)
* REST APIs as agent-native tools
* AI routing to cloud and local large language models (LLMs)
* Support for the Gateway API Inference Extension project

## Architecture

For more information about how kgateway integrates with agentgateway, see the [Architecture](../about/architecture/) topic.

For more information about agentgateway resources, see the [Agentgateway docs](https://agentgateway.dev/docs/about/).

## Agentgateway resource configuration {#resources}

Review the following table to understand how to configure agentgateway resources in {{< reuse "/docs/snippets/kgateway.md" >}}.

| Agentgateway resource | Description | Configured in {{< reuse "/docs/snippets/kgateway.md" >}} by |
| -- | -- | -- |
| Bind | The set of ports on which the agentgateway listens for incoming requests. | Inferred from the ports and listeners in a Gateway or ListenerSet. |
| Port | The port to listen on. Each port has a set of listeners that in turn have their own routes with policies and backends. | Ports in a Gateway or ListenerSet. |
| Listener | Listener configuration for how agentgateway accepts and processes incoming requests. Listeners can each have their own set of routes with policies and backends. | Listeners in a Gateway or ListenerSet. |
| Route | Route configuration for how agentgateway routes incoming requests to the appropriate backend, such as matching rules. | Route resources such as HTTPRoute, GRPCRoute, and TCPRoute. |
| Backend | The backing destination where traffic is routed. | Services and Backends. |
| Target | The details of the backend, such as the tools in an MCP backend. | Services and Backends. |
| Policies | Policies for how agentgateway processes incoming requests, such as traffic shaping and security. | Policies in an HTTPRoute, GRPCRoute, or TCPRoute, as well as kgateway TrafficPolicies. |
