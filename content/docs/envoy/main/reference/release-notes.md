---
title: Release notes
description: What's new, breaking changes, and bug fixes for each kgateway release.
weight: 100
---

Review the release notes for kgateway. For a detailed list of changes between tags, use the [GitHub Compare changes tool](https://github.com/kgateway-dev/kgateway/compare/).

## 2.5.0

### 🔥 Breaking changes {#v24-breaking-changes}



### 🌟 New features {#v24-new-features}

#### Share a local rate limit across Gateway replicas {#v25-share-local-ratelimit}

The {{< reuse "kgw-docs/snippets/trafficpolicy.md" >}} resource now supports the `shareAcrossGateway` field for local rate limiting. By default, each Envoy proxy replica enforces its own local token bucket, so the effective rate increases as the Gateway scales out. Set `shareAcrossGateway` to `true` to divide the token bucket evenly across all Gateway proxy replicas, so the configured rate applies to the Gateway as a whole.

For more information, see [Share a local rate limit across Gateway replicas]({{< link-hextra path="/security/ratelimit/local/#share-across-gateway" >}}).


<!--

### ⚒️ Installation changes {#v2.2-installation-changes}

### 🔄 Feature changes {#v2.2-feature-changes}

### 🗑️ Deprecated or removed features {#v2.2-removed-features}

### 🚧 Known issues {#v2.2-known-issues}
-->

