---
title: Release notes
description: What's new, breaking changes, and bug fixes for each kgateway release.
weight: 100
---

Review the release notes for kgateway. For a detailed list of changes between tags, use the [GitHub Compare changes tool](https://github.com/kgateway-dev/kgateway/compare/).

## 2.5.0

### 🔥 Breaking changes {#v24-breaking-changes}



### 🌟 New features {#v24-new-features}

#### Move the buffer filter before body-reading filters {#v25-buffer-filter-stage}

You can now use the `buffer.filterStage` field on a {{< reuse "kgw-docs/snippets/trafficpolicy.md" >}} resource to place the buffer filter at an earlier position in the HTTP filter chain. By default, the buffer filter runs after authentication, authorization, and rate limiting, so a filter that reads the request body first, such as external auth with request-body checks or ExtProc, can prevent `buffer.maxRequestSize` from being enforced. 

For more information about to change the position of the filter, see [Move the buffer filter before body-reading filters]({{< link-hextra path="/traffic-management/buffering/#move-the-buffer-filter-before-body-reading-filters" >}}).


<!--

### ⚒️ Installation changes {#v2.2-installation-changes}

### 🔄 Feature changes {#v2.2-feature-changes}

### 🗑️ Deprecated or removed features {#v2.2-removed-features}

### 🚧 Known issues {#v2.2-known-issues}
-->

