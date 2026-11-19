---
title: Release notes
description: What's new, breaking changes, and bug fixes for each kgateway release.
weight: 100
---

Review the release notes for kgateway. For a detailed list of changes between tags, use the [GitHub Compare changes tool](https://github.com/kgateway-dev/kgateway/compare/).

## 2.6.0

### 🔥 Breaking changes {#v26-breaking-changes}



### 🌟 New features {#v26-new-features}



### ⚒️ Installation changes {#v26-installation-changes}

#### Go runtime sets GOMAXPROCS for the controller {#v26-controller-gomaxprocs}

The `GOMAXPROCS` setting controls how many CPUs the controller uses at the same time. Now, the controller's `GOMAXPROCS` value follows the CPU limit of the controller container, even when the limit changes while the pod runs. For example, if a Vertical Pod Autoscaler (VPA) raises the CPU limit, the controller starts to use the extra CPU without a restart.

Before, the Helm chart set `GOMAXPROCS` once when the pod started. If the CPU limit changed later, the controller kept the old value until the pod restarted.

To use a fixed value instead, set `GOMAXPROCS` in `controller.extraEnv`. A fixed value turns off the automatic updates.

```yaml
controller:
  extraEnv:
    GOMAXPROCS: "4"
```

For more information, see [Controller CPU limit and GOMAXPROCS]({{< link-hextra path="/install/advanced/#controller-gomaxprocs" >}}).


<!--

### 🔄 Feature changes {#v2.2-feature-changes}

### 🗑️ Deprecated or removed features {#v2.2-removed-features}

### 🚧 Known issues {#v2.2-known-issues}
-->
