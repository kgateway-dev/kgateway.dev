---
title: Istio
weight: 10
description: Integrate kgateway with an Istio service mesh and understand its role in the GAMMA initiative.
---

Integrate kgateway with an Istio service mesh.

{{< cards >}}
  {{< card link="ambient" title="Ambient" >}}
  {{< card link="sidecar" title="Sidecar" >}}
  {{< card link="gamma" title="GAMMA & Service Mesh" >}}
{{< /cards >}}

## GAMMA and Service Mesh Support

### Understanding kGateway's Role

**kGateway is an API gateway and ingress controller, not a service mesh.** However, kGateway integrates with service meshes like Istio to provide enhanced capabilities, particularly as a waypoint proxy in Istio's ambient mesh.

### What is GAMMA?

GAMMA (Gateway API for Mesh Management and Administration) is a dedicated workstream within the Kubernetes Gateway API subproject that extends the API to support service mesh use cases. Established in 2022, GAMMA defines how Gateway API can be used for east-west (service-to-service) traffic within the same cluster, while making minimal changes to the specification and preserving its role-oriented nature.

Key GAMMA concepts relevant to kGateway:

- **Service parentRefs**: HTTPRoutes attach directly to Service resources (instead of Gateway resources) when configuring mesh traffic
- **Destination-Side Policy Enforcement**: In ambient mode, all policies are enforced by the destination waypoint
- **Vendor-Neutral Standard**: Works across different service mesh implementations, promoting consistency

### kGateway in Mesh Context

When deployed as a waypoint proxy in Istio ambient mesh, kGateway supports GAMMA patterns and provides advanced L7 capabilities without requiring EnvoyFilter configurations.

#### Service parentRefs Example
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

This HTTPRoute attaches to the `reviews` Service frontend. Any traffic directed to this Service will be routed according to these rules - 90% to reviews-v1 and 10% to reviews-v2. This is a core GAMMA pattern for mesh traffic management.

For detailed waypoint configuration, see the [Waypoint Proxy documentation]({{< relref "ambient/waypoint" >}}).
