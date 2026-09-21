---
title: Release notes
description: What's new, breaking changes, and bug fixes for each kgateway release.
weight: 100
---

Review the release notes for kgateway. For a detailed list of changes between tags, use the [GitHub Compare changes tool](https://github.com/kgateway-dev/kgateway/compare/).

## 2.5.0

### 🔥 Breaking changes {#v24-breaking-changes}



### 🌟 New features {#v24-new-features}

#### Preserve request paths {#v25-preserve-request-paths}

You can now disable Envoy's default path normalization and slash merging on a listener by using the `normalizePath` and `mergeSlashes` fields in the HTTP settings of a ListenerPolicy resource. Disable these settings for backends that depend on the original, unmodified request path, such as S3-compatible object stores that use object keys containing repeated slashes.

For more information, see [Preserve request paths]({{< link-hextra path="/traffic-management/preserve-request-paths/" >}}).


<!--

### ⚒️ Installation changes {#v2.2-installation-changes}

### 🔄 Feature changes {#v2.2-feature-changes}

### 🗑️ Deprecated or removed features {#v2.2-removed-features}

### 🚧 Known issues {#v2.2-known-issues}
-->

