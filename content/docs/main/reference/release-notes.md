---
title: Release notes
weight: 100
---

Review the release notes for kgateway. For a detailed list of changes between tags, use the [GitHub Compare changes tool](https://github.com/kgateway-dev/kgateway/compare/).

## v2.2.0 

<!-- TODO release 2.2 
For more details, review the [GitHub release notes](https://github.com/kgateway-dev/kgateway/releases/tag/v2.2.0).-->

### 🔥 Breaking changes {#v22-breaking-changes}

#### Feature gate for experimental Gateway API features {#expimental-feature-gate}

Starting in kgateway 2.2, experimental Gateway API features are gated behind the `KGW_ENABLE_GATEWAY_API_EXPERIMENTAL_FEATURES` environment variable. This setting defaults to `false` and must be explicitly enabled to use experimental features such as the following:

- ListenerSets
- CORS policies
- Retries
- Session persistence

To enable these features, set the environment variable in your kgateway controller deployment in your Helm values file.

```yaml
controller:
  extraEnv:
    KGW_ENABLE_GATEWAY_API_EXPERIMENTAL_FEATURES: "true"
```

If you are currently using any of these experimental features, you must enable this setting before upgrading to kgateway 2.2, or those features will stop working.

#### Waypoint integration removed

The waypoint integration for Envoy-based gateway proxies was removed. 

### 🌟 New features {#v22-new-features}



<!-- TODO release 2.2

### ⚒️ Installation changes {#v2.2-installation-changes}

### 🔄 Feature changes {#v2.2-feature-changes}

### 🗑️ Deprecated or removed features {#v2.2-removed-features}

### 🚧 Known issues {#v2.2-known-issues}
-->
