---
title: GAMMA and Service Mesh Support
weight: 15
description: Understanding kGateway's role in the GAMMA initiative and service mesh integration
---

## What is GAMMA?

GAMMA (Gateway API for Mesh Management and Administration) is a dedicated workstream within the Kubernetes Gateway API subproject that defines how the Gateway API can be used to configure service meshes for east-west (service-to-service) traffic within the same cluster.

The Gateway API was originally designed for north-south (ingress) traffic. The GAMMA initiative, established in 2022, extends Gateway API to support service mesh use cases while making minimal changes to the specification and preserving its role-oriented nature.

## kGateway's Role in Service Mesh

**kGateway is an API gateway and ingress controller, not a service mesh.** However, kGateway can integrate with service meshes like Istio to provide enhanced Layer 7 capabilities.

### Key Distinctions

- **North-South Traffic (Ingress)**: kGateway excels as a feature-rich API gateway for external traffic entering your cluster
- **East-West Traffic (Service Mesh)**: kGateway can be deployed as a waypoint proxy within Istio's ambient mesh to provide Layer 7 processing for internal service-to-service communication

## kGateway as a Waypoint Proxy

In Istio's ambient mesh architecture, kGateway can function as a waypoint proxy, providing:

- **Layer 7 Policy Enforcement**: Apply advanced traffic management, security policies, and transformations to mesh traffic. In ambient mode, all policies are enforced by the destination waypoint.
- **HTTPRoute with Service parentRefs**: Configure routes that attach directly to Kubernetes Services rather than Gateways, following GAMMA specifications
- **Unified Gateway Experience**: Use the same kGateway platform for both ingress and in-mesh traffic, reducing operational complexity
- **Advanced Features Without EnvoyFilter**: Access powerful L7 capabilities through Kubernetes-native APIs instead of fragile EnvoyFilter configurations

### Service parentRefs Example

When operating as a waypoint, HTTPRoutes can reference Services directly as parentRefs. This is a key GAMMA pattern - the HTTPRoute attaches to the Service frontend, controlling how traffic directed to that Service is routed:

```yaml
apiVersion: gateway.networking.k8s.io/v1
kind: HTTPRoute
metadata:
  name: reviews-route
  namespace: default
spec:
  # parentRef points to a Service (mesh traffic)
  # instead of a Gateway (ingress traffic)
  parentRefs:
  - group: ""
    kind: Service
    name: reviews
    port: 9080
  rules:
  - backendRefs:
    - name: reviews-v1
      port: 9080
      weight: 90
    - name: reviews-v2
      port: 9080
      weight: 10
```

This configuration applies to service-to-service traffic within the mesh. Any request directed to the `reviews` Service will be routed according to this HTTPRoute, with 90% going to reviews-v1 and 10% to reviews-v2.

## When to Use kGateway as a Waypoint

Consider using kGateway as a waypoint proxy when you need:

1. **Advanced Layer 7 Features**: Rate limiting, request transformation, header manipulation, external auth, and other capabilities beyond the default Istio waypoint - all without EnvoyFilter
2. **Unified Platform**: Single gateway solution for both north-south (ingress) and east-west (mesh) traffic with consistent tooling and operational experience
3. **Kubernetes-Native APIs**: kGateway's policy APIs instead of complex EnvoyFilter configurations that are fragile and remain in Alpha status
4. **AI/LLM Gateway Capabilities**: First-class support for AI traffic patterns, model failover, prompt enrichment, and LLM provider integrations

## Architecture Overview

```
┌─────────────────────────────────────────────────┐
│  North-South Traffic (Ingress)                  │
│  ┌──────────┐                                   │
│  │ kGateway │ ──> HTTPRoute (parentRef: Gateway)│
│  └──────────┘                                   │
└─────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────┐
│  East-West Traffic (Service Mesh)               │
│  ┌─────────────────┐                            │
│  │ kGateway        │                            │
│  │ (Waypoint Proxy)│ ──> HTTPRoute (parentRef:  │
│  └─────────────────┘      Service)              │
└─────────────────────────────────────────────────┘
```

## Learn More

For detailed implementation guides on deploying kGateway as a waypoint proxy, see:
- [Waypoint Proxy Configuration]({{< relref "../ambient/waypoint" >}})
- [Istio Ambient Mesh Integration]({{< relref "../ambient" >}})
