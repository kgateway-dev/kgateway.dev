Welcome to the kgateway glossary! This page breaks down the key terms for API gateways, AI, service mesh, Kubernetes, and other cloud-native words you'll find while using kgateway. Think of it as your quick reference hub whenever something feels unfamiliar.

## How to use this glossary

To get a clear picture of how kgateway works, you might find it helpful to explore related key terms. 

- **Just starting?** Begin with API Gateway → Backends → Routes → TrafficPolicy.
- **Focusing on AI?** Explore Agentgateway → A2A → LLM Gateway → MCP.
- **Working with service mesh?** Study ambient mesh → data plane → control plane → security.

In this glossary, some terms come directly from the Kubernetes, Gateway API, or cloud-native open source ecosystem. These terms are marked with a chain-link icon (🔗) and link to the docs for the relevant project.

Throughout the docs, terms that are defined in this glossary are underlined. When you hover over the term, the definition pops up for quick reference.

### Still not finding what you need?

If a term is missing:

1. Try the search bar.
2. Check examples in the tutorials.
3. Visit the [API reference]({{< link-hextra path="/reference/api/" >}}).
4. Remember that some terms come from general Kubernetes or cloud-native concepts.

*This glossary grows alongside kgateway. If you notice a missing term, consider contributing to help others!*

## A–C

### A2A
**Agent-to-Agent Protocol (A2A)**

A secure, policy-driven communication method for AI agents running in an ambient mesh. It enables lightweight, sidecar-free interactions between agents.

🔗 *See official documentation*: https://a2a-protocol.org/latest/

### Agentgateway
An open-source data plane optimized for agentic AI workloads. Kgateway uses agentgateway to route and manage traffic for LLMs, inference services, and AI-native applications.

**Learn more**: [Agentgateway docs]({{< link-hextra path="/agentgateway/" >}})

### Agents
Autonomous AI components that make decisions, communicate with services, and interact with other agents (with or without sidecars). In Kgateway, agents participate in the mesh and communicate over A2A or Envoy-based traffic.

### Ambient Mesh
A service mesh architecture that removes the need for sidecars. Instead of injecting proxies into every pod, ambient mesh uses waypoint proxies and ztunnels to simplify operations and reduce overhead.

🔗 *See official documentation*: https://ambientmesh.io/

### API Gateway
The central entry point for controlling, securing, and routing API traffic.

In kgateway, two types of proxies can act as API Gateways:

- The **Envoy-based Kgateway proxy** (traditional API and service mesh traffic)  
- **Agentgateway** (AI/LLM-specific traffic)

### Backends
Destination services or endpoints that kgateway routes traffic to, such as Kubernetes Services, Lambdas, external hosts, or custom backends. These backends are connected to routes for forwarding traffic.

**Learn more**: [Backend guides]({{< link-hextra path="/traffic-management/destination-types/backends/" >}})

### Cluster (Kubernetes)
A collection of Kubernetes nodes (control plane + workers) that run your workloads and host kgateway.

### Cluster (Envoy)
A logical group of upstream endpoints used by Envoy for load balancing. The Envoy-based kgateway data plane automatically generates Envoy clusters based on your Backends and route configuration.

### Control Plane
The system that configures and manages the data plane.  
In kgateway, the control plane distributes routing rules, policies, and extension configuration to the supported data plane proxies: the Envoy-based kgateway proxy and the agentgateway proxy.

### CRDs (Custom Resource Definitions)
Extend the Kubernetes API with custom resource types.

🔗 *See official documentation*: https://kubernetes.io/docs/reference/glossary/?all=true#term-custom-resource-definition

## D–F

### Data Plane
The layer that actually processes live traffic. Kgateway supports the following data plane proxies:

- Envoy-based Kgateway proxies
- Agentgateway (for AI workloads) 

### Delegation
A way to share routing responsibility across teams or namespaces. A parent route delegates part of its routing logic to child routes, allowing flexible ownership.

### DirectResponse
A policy that allows the gateway to immediately return a response without forwarding traffic to a backend. Useful for maintenance pages, blocking traffic, or custom messages.

### Egress
Outbound traffic leaving the mesh or cluster. Egress gateways often apply policies such as access control, filtering, or auditing.

### Envoy
A high-performance L7 proxy used as the primary data plane for API and service mesh workloads when you create a Gateway from the `kgateway` GatewayClass.

### External Authorization
An Envoy extension that offloads authorization decisions to an external service. Kgateway can integrate with these systems to enforce access control.

## G–L

### Gateway
A Gateway API resource that represents the instantiation of a gateway implementation.

🔗 *See official documentation*: https://gateway-api.sigs.k8s.io/references/spec/#gateway.networking.k8s.io/v1.Gateway

### GatewayClass
Defines a class of Gateways with a shared configuration or implementation. Depending on how you install kgateway, you may have one or more GatewayClass resources created for you.

🔗 *See official documentation*: https://gateway-api.sigs.k8s.io/references/spec/#gateway.networking.k8s.io/v1.GatewayClass

### Gateway Extension
A kgateway resource that integrates extended services such as external authorization, rate limits, and processors into the Gateway data plane configuration.

**Learn more**: [GatewayExtension API docs]({{< link-hextra path="/reference/api/#gatewayextension" >}})

### GatewayParameters
Configures template, deployment, and runtime settings for a Gateway instance (including Envoy proxy configuration).

**Learn more**: [Gateway setup guides]({{< link-hextra path="/setup/default/" >}})

### GRPCRoute
A Gateway API resource for configuring gRPC routing rules.

🔗 *See official documentation*: https://gateway-api.sigs.k8s.io/references/spec/#gateway.networking.k8s.io/v1.GRPCRoute

### HTTPRoute
A Gateway API resource for configuring HTTP/HTTPS routing rules.

🔗 *See official documentation*: https://gateway-api.sigs.k8s.io/references/spec/#gateway.networking.k8s.io/v1.HTTPRoute

### Inference Extension Project
Mechanisms for running inference or AI processing in traffic flows—typically implemented as Envoy filters or external processors.

🔗 *See official documentation*: https://gateway-api-inference-extension.sigs.k8s.io/

### Lambda
Serverless compute functions in Amazon Web Services (AWS) that kgateway can route traffic to via Backends.

### Large Language Model (LLM)
AI models trained on massive datasets to generate human-like text. Kgateway manages LLM traffic by using the agentgateway data plane.

### LLM Gateway / AI Gateway
A traffic-management pattern specialized for LLM, agent, MCP, and AI inference traffic. Agentgateway acts as the data plane for this pattern.

## M–O

### MCP (Model Context Protocol)
A protocol for exchanging model context, metadata, and tool information between LLM gateways, tools, and agents.

### Observability (Logging, Monitoring, Tracing)
Systems that help you understand the behavior of your network traffic. You can integrate an OpenTelemetry-based observability solution into kgateway to get telemetry data for your traffic, including access logs, metrics, and distributed traces.

## P–R

### Proxy
A data plane process (Envoy or agentgateway) that receives, processes, and forwards traffic based on kgateway configuration.

**Learn more**: [Architecture docs]({{< link-hextra path="/about/architecture/" >}})

### Rate Limiting
Controls how many requests can reach your services over time. Often implemented via Gateway Extensions using Envoy rate-limit services.

### ReferenceGrant
A Gateway API resource that controls cross-namespace references.

🔗 *See official documentation*: https://gateway-api.sigs.k8s.io/references/spec/#gateway.networking.k8s.io/v1.ReferenceGrant

### Resiliency
Techniques like retries, timeouts, and circuit breakers that make applications more reliable when failures occur.

## S–Z

### Security
Authentication, authorization, and encryption settings that protect your traffic and data.

### Service Mesh
A network layer for service-to-service communication. Kgateway integrates with Istio and ambient mesh to support mesh-based traffic patterns.

### TCPRoute
A Gateway API resource for configuring TCP routing rules.

🔗 *See official documentation*: https://gateway-api.sigs.k8s.io/references/spec/#gateway.networking.k8s.io/v1.TCPRoute

### Traffic Management
Features that shape, route, or modify traffic, such as load balancing, matching, filtering, and transformations.

### TrafficPolicy
A kgateway resource that defines advanced traffic management settings, retries, timeouts, mirroring, security policies, and more.

**Learn more**: [TrafficPolicy concept docs]({{< link-hextra path="/about/policies/trafficpolicy/" >}})

### Translation
The kgateway control plane process that converts Gateway API resources and CRDs into xDS configuration for enforcement in the Envoy-based kgateway or agentgateway data planes.
