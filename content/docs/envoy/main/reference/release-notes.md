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

Several additional capabilities are now available for the control plane and Gateway resources:

* **Common labels**: Add custom labels to all resources created by the Helm charts using the `commonLabels` field, including the Deployment, Service, and ServiceAccount of gateway proxies. This allows you to better organize your resources or integrate with external tools.
* **Static IP addresses for Gateways**: Assign a static IP address to the Kubernetes service that exposes your Gateway using the `spec.addresses` field with `type: IPAddress`.

<!-- TODO release 2.2

### ⚒️ Installation changes {#v2.2-installation-changes}

### 🔄 Feature changes {#v2.2-feature-changes}

### 🗑️ Deprecated or removed features {#v2.2-removed-features}

### 🚧 Known issues {#v2.2-known-issues}
-->
