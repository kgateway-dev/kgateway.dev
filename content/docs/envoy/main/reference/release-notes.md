---
title: Release notes
description: What's new, breaking changes, and bug fixes for each kgateway release.
weight: 100
---

Review the release notes for kgateway. For a detailed list of changes between tags, use the [GitHub Compare changes tool](https://github.com/kgateway-dev/kgateway/compare/).

## 2.5.0

### 🔥 Breaking changes {#v25-breaking-changes}

#### SDS sidecar binds to loopback by default {#v25-sds-loopback-bind}

The SDS (Secret Discovery Service) sidecar now binds to `127.0.0.1:8234` (loopback) by default instead of `0.0.0.0:8234`. Previously, any pod on the cluster network could reach the SDS endpoint. Because all consumers of SDS run in the same pod as the sidecar, restricting the bind address to loopback closes this unintended exposure.

If you need to reach the SDS sidecar from outside its pod in a trusted environment, set the `SDS_SERVER_ADDRESS=0.0.0.0:8234` environment variable on the `sds` container. For an example, see [Change the SDS sidecar's pod-network bind address]({{< link-hextra path="/setup/customize/configs/#sds-bind-address" >}}). If you use a custom deployment overlay or manifest that overrides the SDS container's readiness probe, note that the default probe also changed, from a `tcpSocket` check on port 8234 to an `exec` probe that runs `sds healthcheck`, because a TCP probe against the pod IP no longer succeeds against a loopback-only listener.

### 🌟 New features {#v25-new-features}

#### JWT verified token caching {#v25-jwt-cache}

You can now enable Envoy's in-memory cache of successfully verified JWTs by using the `cache` field on a JWT provider in a GatewayExtension resource. For a successfully verified token that is presented more than once, the gateway proxy does not parse the token again, or perform a JWKS lookup and signature verification. Expired tokens are automatically removed from the cache. For more information, see [JWT caching]({{< link-hextra path="/security/jwt/simple/basic/#jwt-caching" >}}).

#### Preserve request paths {#v25-preserve-request-paths}
You can now disable Envoy's default path normalization and slash merging on a listener by using the `normalizePath` and `mergeSlashes` fields in the HTTP settings of a ListenerPolicy resource. Disable these settings for backends that depend on the original, unmodified request path, such as S3-compatible object stores that use object keys containing repeated slashes.

For more information, see [Preserve request paths]({{< link-hextra path="/traffic-management/preserve-request-paths/" >}}).

#### JWKS fetch timeout {#v25-jwks-timeout}

You can now set the `timeout` field on the `jwks.remote` settings of a JWT provider in a GatewayExtension resource to configure how long the gateway waits for the remote JWKS server to respond to a single fetch. For more information, see [JWKS fetch timeout]({{< link-hextra path="/security/jwt/simple/basic/#jwks-timeout" >}}).


<!--

### ⚒️ Installation changes {#v2.2-installation-changes}

### 🔄 Feature changes {#v2.2-feature-changes}

### 🗑️ Deprecated or removed features {#v2.2-removed-features}

### 🚧 Known issues {#v2.2-known-issues}
-->

