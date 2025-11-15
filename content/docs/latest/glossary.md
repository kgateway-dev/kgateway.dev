---
title: "Glossary"
weight: 1000
description: "Definitions for Kgateway, AI, service mesh, and cloud-native terms"
---

## Kgateway Glossary

Welcome to the Kgateway glossary! This page breaks down AI, service mesh, Kubernetes, and cloud-native terms you’ll encounter while using Kgateway. Think of it as your quick reference hub whenever something feels unfamiliar.

{{< callout type="tip" >}}
**How to Use This Glossary**

- **New to Kgateway?** Start by skimming the A2A, Agentgateway, API Gateway, and Backends definitions.  
- **Working with AI traffic?** Focus on LLM Gateway, MCP, Inference Extensions, and Agentgateway.  
- **Exploring service mesh?** Ambient mesh, ztunnels, data plane, and control plane will be most helpful.  
- **Unsure about a Kubernetes term?** Anything marked with 🔗 links to the official docs.
{{< /callout >}}

{{< callout type="info" >}}
**About External References**

Some definitions come directly from the Kubernetes or Gateway API ecosystem.  
These are marked with **🔗** and link to their authoritative documentation.  
This ensures you always get the exact spec, while still understanding how Kgateway uses the concept.
{{< /callout >}}

---

### A–C

#### A2A
**Agent-to-Agent Protocol.**  
A secure, policy-driven communication method for AI agents running in an ambient mesh. It enables lightweight, sidecar-free interactions between agents.

**Learn more**: https://a2a-protocol.org/latest/

#### Agentgateway
An open-source data plane optimized for agentic AI workloads. Kgateway uses Agentgateway to route and manage traffic for LLMs, inference services, and AI-native applications.

**Learn more**: https://kgateway.dev/docs/latest/agentgateway/

#### Agents
Autonomous AI components that make decisions, communicate with services, and interact with other agents (with or without sidecars). In Kgateway, agents participate in the mesh and communicate over A2A or Envoy-based traffic.

#### Ambient Mesh
A service mesh architecture that removes the need for sidecars. Instead of injecting proxies into every pod, ambient mesh uses waypoint proxies and ztunnels to simplify operations and reduce overhead.

**Learn more**: https://ambientmesh.io/

#### API Gateway
The central entry point for controlling, securing, and routing API traffic.  
In Kgateway, two types of proxies can act as API Gateways:

- The **Envoy-based Kgateway proxy** (traditional API and service mesh traffic)  
- **Agentgateway** (AI/LLM-specific traffic)

#### Backends
Destination services or endpoints Kgateway can route traffic to—Kubernetes Services, Lambdas, external hosts, or custom backends. These are connected to routes for forwarding traffic.

**Learn more**: https://kgateway.dev/docs/latest/backends/

#### Cluster (Kubernetes)
A collection of Kubernetes nodes (control plane + workers) that run your workloads and host Kgateway.

#### Cluster (Envoy)
A logical group of upstream endpoints used by Envoy for load balancing. Kgateway automatically generates Envoy clusters based on your Backends and route configuration.

#### Control Plane
The system that configures and manages the data plane.  
In Kgateway, the control plane distributes routing rules, policies, and extension configuration to proxies and agents.

#### CRDs (Custom Resource Definitions)
Extend the Kubernetes API with custom resource types.

🔗 *See official documentation*: https://kubernetes.io/docs/reference/glossary/?all=true#term-custom-resource-definition

---

### D–F

#### Data Plane
The layer that actually processes live traffic.  
In Kgateway, this includes:

- Envoy-based Kgateway proxies  
- Agentgateway (for AI workloads)  
- Agents participating in traffic flows  

#### Delegation
A way to share routing responsibility across teams or namespaces.  
A parent route delegates part of its routing logic to child routes, allowing flexible ownership.

#### DirectResponse
A policy that allows the gateway to immediately return a response—without forwarding traffic to a backend. Useful for maintenance pages, blocking traffic, or custom messages.

#### Egress
Outbound traffic leaving the mesh or cluster. Egress gateways often apply policies such as access control, filtering, or auditing.

#### Envoy
A high-performance L7 proxy used as the primary data plane for API and service mesh workloads in Kgateway.

#### External Authorization
An Envoy extension that offloads authorization decisions to an external service. Kgateway can integrate with these systems to enforce access control.

---

### G–L

#### Gateway
A Gateway API resource that represents the instantiation of a gateway implementation.

🔗 *See official documentation*: https://gateway-api.sigs.k8s.io/references/spec/#gateway.networking.k8s.io/v1.Gateway

#### GatewayClass
Defines a class of Gateways with a shared configuration or implementation.

🔗 *See official documentation*: https://gateway-api.sigs.k8s.io/references/spec/#gateway.networking.k8s.io/v1.GatewayClass

#### Gateway Extension
A Kgateway resource that integrates external services—auth, rate limits, processors, etc.—into the Gateway data plane.

**Learn more**: https://kgateway.dev/docs/latest/gateway-extensions/

#### GatewayParameters
Configures template, deployment, and runtime settings for a Gateway instance (including Envoy proxy configuration).

**Learn more**: https://kgateway.dev/docs/latest/reference/api/#gatewayparameters

#### GRPCRoute
A Gateway API resource for configuring gRPC routing rules.

🔗 *See official documentation*: https://gateway-api.sigs.k8s.io/references/spec/#gateway.networking.k8s.io/v1.GRPCRoute

#### HTTPRoute
A Gateway API resource for configuring HTTP/HTTPS routing rules.

🔗 *See official documentation*: https://gateway-api.sigs.k8s.io/references/spec/#gateway.networking.k8s.io/v1.HTTPRoute

#### Inference Extension Project
Mechanisms for running inference or AI processing in traffic flows—typically implemented as Envoy filters or external processors.

#### Lambda
Serverless compute functions (e.g., AWS Lambda) that Kgateway can route traffic to via Backends.

#### Large Language Model (LLM)
AI models trained on massive datasets to generate human-like text. Kgateway manages LLM traffic using Agentgateway and LLM Gateway patterns.

#### LLM Gateway / AI Gateway
A traffic-management pattern specialized for LLM or AI inference traffic.  
Agentgateway powers this in Kgateway deployments.

---

### M–O

#### MCP (Model Context Protocol)
A protocol for exchanging model context, metadata, and tool information between LLM gateways, tools, and agents.

#### Observability (Logging, Monitoring, Tracing)
Systems that help you understand the behavior of your network traffic. In Kgateway, this includes:

- Access logs  
- Metrics  
- Distributed traces  

---

### P–R

#### Proxy
A data plane process (Envoy or Agentgateway) that receives, processes, and forwards traffic based on Kgateway configuration.

**Learn more**: https://kgateway.dev/docs/latest/about/architecture/

#### Rate Limiting
Controls how many requests can reach your services over time. Often implemented via Gateway Extensions using Envoy rate-limit services.

#### ReferenceGrant
A Gateway API resource that controls cross-namespace references.

🔗 *See official documentation*: https://gateway-api.sigs.k8s.io/references/spec/#gateway.networking.k8s.io/v1.ReferenceGrant

#### Resiliency
Techniques like retries, timeouts, and circuit breakers that make applications more reliable when failures occur.

---

### S–Z

#### Security
Authentication, authorization, and encryption settings that protect your traffic and data.

#### Service Mesh
A network layer for service-to-service communication. Kgateway integrates with ambient mesh and Istio to support mesh-based traffic patterns.

#### TCPRoute
A Gateway API resource for configuring TCP routing rules.

🔗 *See official documentation*: https://gateway-api.sigs.k8s.io/references/spec/#gateway.networking.k8s.io/v1.TCPRoute

#### Traffic Management
All features that shape, route, or modify traffic—load balancing, filtering, transformation, retries, mirroring, etc.

#### TrafficPolicy
A Kgateway resource that defines advanced traffic management settings (retries, timeouts, mirroring, security policies).

**Learn more**: https://kgateway.dev/docs/latest/traffic-policy/

#### Translation
The process that converts Gateway API resources and CRDs into Envoy xDS configuration for enforcement in the data plane.

---

{{< callout type="info" >}}
### How These Terms Fit Together

Understanding how Kgateway’s concepts relate helps you see the full picture:

- The **Control Plane** configures the **Data Plane**  
- **Agentgateway** handles AI/LLM traffic  
- The Envoy-based **API Gateway** handles traditional API traffic  
- **Gateways** and **Routes** define how requests are processed  
- **TrafficPolicy** and **Extensions** add behavior and integrations  
- **Backends** are the final destinations for requests  
- Everything is monitored through **Observability**
{{< /callout >}}

{{< callout type="success" >}}
### Learning Path

- **Just starting?**  
  Begin with API Gateway → Backends → Routes → TrafficPolicy.

- **Focusing on AI?**  
  Explore Agentgateway → A2A → LLM Gateway → MCP.

- **Working with service mesh?**  
  Study ambient mesh → data plane → control plane → security.
{{< /callout >}}

### Still Not Finding What You Need?

If a term is missing:

1. Try the search bar  
2. Check examples in the tutorials  
3. Visit the API reference  
4. Remember that some terms come from general Kubernetes or cloud-native concepts  

*This glossary grows alongside Kgateway. If you notice a missing term, consider contributing to help others!*
