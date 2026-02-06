---
title: AgentgatewayPolicy (agentgateway) — long form guide
toc: true
publishDate: 2026-01-01T00:00:00-00:00
author: Gaurav Singh
---

# AgentgatewayPolicy — complete reference & examples

**Overview (TL;DR)**  
`AgentgatewayPolicy` is the agentgateway-native policy CRD that replaces the older `TrafficPolicy` for agentgateway-based dataplanes. It lets you attach policy objects (logging, transformations, rate limits, extAuth, backend TLS, etc.) to Gateways, HTTPRoutes, backends, and services. This page explains the key fields, shows how it differs from previous policies, and provides three runnable examples: **access logging**, **backend TLS/TCP**, and **request/response transformations**.

> Why this matters: `AgentgatewayPolicy` centralizes security, observability, and traffic transformation for AI traffic (LLMs, MCP, agent-to-agent) and is the recommended way to configure agentgateway in Kubernetes.

---

## Short conceptual summary

- **apiVersion / kind**: `apiVersion: agentgateway.dev/v1alpha1`, `kind: AgentgatewayPolicy`.  
- **Targets**: Use `targetRefs` (or `targetSelectors`) to attach this policy to `Gateway`, `HTTPRoute`, `Backend/Service`, or `MCP` targets.  
- **Top areas in `spec`**:
  - `frontend` (listener-level settings; observability like tracing/access logs)
  - `traffic` (routing-related policies: rate limits, extAuth, retries)
  - `backend` (per-backend TLS/auth/prompt guard settings for AI backends)
  - `transformation` / `transform` (request and response header/body transforms using CEL and templates)

---

## Quick schema excerpt (illustrative)
```yaml
apiVersion: agentgateway.dev/v1alpha1
kind: AgentgatewayPolicy
metadata:
  name: example-policy
  namespace: agentgateway-system
spec:
  targetRefs:
    - group: gateway.networking.k8s.io
      kind: HTTPRoute
      name: example-route
  frontend:
    accessLogs:
      openTelemetry:
        backendRef:
          name: otel-collector
          namespace: telemetry
          port: 4317
  traffic:
    rateLimit: {}
  backend:
    tls: {}
  transformation: {}