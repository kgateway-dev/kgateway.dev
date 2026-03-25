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

####  Static IPs for Gateways

Assign a static IP address to the Kubernetes service that exposes your Gateway using the `spec.addresses` field with `type: IPAddress`.

For more information, see [Static IP address]({{< link-hextra path="/setup/gateway/#static-ip-address" >}}). 

#### Gateway proxy customization {#v23-gateway-customization}

The GatewayParameters resource now supports gateway proxy customization via overlay fields. Overlays use strategic merge patch (SMP) semantics to apply advanced customizations to the Kubernetes resources that are generated for gateway proxies, including the Service, ServiceAccount, and Deployment. 

The following overlays are supported: 

* Use `deploymentOverlay`, `serviceOverlay`, and `serviceAccountOverlay` to patch the generated Deployment, Service, and ServiceAccount.
* Use `horizontalPodAutoscaler`, `verticalPodAutoscaler`, and `podDisruptionBudget` to automatically create and configure these resources targeting the proxy Deployment.

For more information, see [Change proxy settings]({{< link-hextra path="/setup/customize/gateway/" >}}) and [Overlay examples]({{< link-hextra path="/setup/customize/configs/" >}}).

<!-- TODO release 2.2

### ⚒️ Installation changes {#v2.2-installation-changes}

### 🔄 Feature changes {#v2.2-feature-changes}

### 🗑️ Deprecated or removed features {#v2.2-removed-features}

### 🚧 Known issues {#v2.2-known-issues}
-->
