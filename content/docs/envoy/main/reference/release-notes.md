---
title: Release notes
description: What's new, breaking changes, and bug fixes for each kgateway release.
weight: 100
---

Review the release notes for kgateway. For a detailed list of changes between tags, use the [GitHub Compare changes tool](https://github.com/kgateway-dev/kgateway/compare/).

## 2.5.0

### 🔥 Breaking changes {#v24-breaking-changes}



### 🌟 New features {#v24-new-features}

#### Control the Host header of mirrored requests {#v25-request-mirror-host}

The `requestMirror` section of a {{< reuse "kgw-docs/snippets/trafficpolicy.md" >}} now supports two new fields for controlling the `Host`/`:authority` header of requests that an HTTPRoute or GRPCRoute `RequestMirror` filter mirrors.

* **`disableShadowHostSuffixAppend`**: By default, Envoy appends `-shadow` to the `Host`/`:authority` header of mirrored requests. Set this field to `true` to send the original header unchanged. This is useful when the shadow destination has strict host-based routing rules that reject the modified header.
* **`hostRewriteLiteral`**: Replaces the `Host`/`:authority` header of mirrored requests with the specified value. Include a port if the shadow destination needs one, as the port from the original request is not carried over.

For more information, see [Mirroring]({{< link-hextra path="/resiliency/mirroring/#request-mirror" >}}).


<!--

### ⚒️ Installation changes {#v2.2-installation-changes}

### 🔄 Feature changes {#v2.2-feature-changes}

### 🗑️ Deprecated or removed features {#v2.2-removed-features}

### 🚧 Known issues {#v2.2-known-issues}
-->

