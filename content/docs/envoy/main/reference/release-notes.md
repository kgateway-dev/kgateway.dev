---
title: Release notes
weight: 100
---

Review the release notes for kgateway. For a detailed list of changes between tags, use the [GitHub Compare changes tool](https://github.com/kgateway-dev/kgateway/compare/).

## v2.3.0

<!-- TODO release 2.2 
For more details, review the [GitHub release notes](https://github.com/kgateway-dev/kgateway/releases/tag/v2.2.0).-->

### 🔥 Breaking changes {#v22-breaking-changes}



### 🌟 New features {#v22-new-features}

#### Control plane changes

- **Common labels**: Add custom labels to all resources that are created by the Helm charts by using the `commonLabels` field, including the Deployment, Service, and ServiceAccount of the control plane. This allows you to better organize your resources or integrate with external tools. For more information, see [Common labels]({{< link-hextra path="/install/advanced/#common-labels" >}}).
- **PriorityClass support**: Assign a PriorityClassName to control plane pods using the `controller.priorityClassName` Helm field. [Priority](https://kubernetes.io/docs/concepts/scheduling-eviction/pod-priority-preemption/) indicates the importance of a pod relative to other pods and allows higher priority pods to preempt lower priority ones when scheduling.
- **Topology spread constraints**: Distribute kgateway controller pods across failure domains such as zones or nodes by using the `topologySpreadConstraints` Helm field. For more information, see [Topology spread constraints]({{< link-hextra path="/install/advanced/#topology-spread-constraints" >}}).

#### Static IPs for Gateways

Assign a static IP address to the Kubernetes service that exposes your Gateway using the `spec.addresses` field with `type: IPAddress`.

For more information, see [Static IP address]({{< link-hextra path="/setup/gateway/#static-ip-address" >}}). 

#### Local rate limit filter options {#v23-local-rate-limit-filter-options}

The {{< reuse "docs/snippets/trafficpolicy.md" >}} resource now supports the `percentEnabled` and `percentEnforced` optional fields to control the percentage of requests for which the local rate limit filter is enabled or enforced. If not set, both fields default to `100`, which enables and enforces the local rate limiting filter for 100% of all requests.

Use these fields for gradual rollouts or to run the filter in shadow mode (`percentEnabled: 100`, `percentEnforced: 0`), where rate limiting statistics are collected without blocking any requests.

For more information, see [Gradual rollout and shadow mode]({{< link-hextra path="/security/ratelimit/local/#gradual-rollout" >}}).

#### Gateway proxy customization {#v23-gateway-customization}

The GatewayParameters resource now supports gateway proxy customization via overlay fields. Overlays use strategic merge patch (SMP) semantics to apply advanced customizations to the Kubernetes resources that are generated for gateway proxies, including the Service, ServiceAccount, and Deployment. 

The following overlays are supported: 

* Use `deploymentOverlay`, `serviceOverlay`, and `serviceAccountOverlay` to patch the generated Deployment, Service, and ServiceAccount.
* Use `horizontalPodAutoscaler`, `verticalPodAutoscaler`, and `podDisruptionBudget` to automatically create and configure these resources targeting the proxy Deployment.

For more information, see [Change proxy settings]({{< link-hextra path="/setup/customize/gateway/" >}}) and [Overlay examples]({{< link-hextra path="/setup/customize/configs/" >}}).


#### GRPCRoute support {#v23-grpcroute}

Route traffic to gRPC services by using the GRPCRoute resource for protocol-aware routing. Unlike the HTTPRoute, which requires matching on HTTP paths and methods, the GRPCRoute allows you to define routing rules by using gRPC-native concepts, such as service and method names.

For more information, see [gRPC routing]({{< link-hextra path="/traffic-management/grpc/" >}}).

<!-- TODO release 2.2

### ⚒️ Installation changes {#v2.2-installation-changes}

### 🔄 Feature changes {#v2.2-feature-changes}

### 🗑️ Deprecated or removed features {#v2.2-removed-features}

### 🚧 Known issues {#v2.2-known-issues}
-->
