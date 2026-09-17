---
title: Release notes
description: What's new, breaking changes, and bug fixes for each kgateway release.
weight: 100
---

Review the release notes for kgateway. For a detailed list of changes between tags, use the [GitHub Compare changes tool](https://github.com/kgateway-dev/kgateway/compare/).

## 2.5.0

### 🔥 Breaking changes {#v25-breaking-changes}



### 🌟 New features {#v25-new-features}

#### Configurable buffer filter stage {#v25-buffer-filter-stage}

You can now set `buffer.filterStage` in a TrafficPolicy to move the buffer filter earlier in the filter chain, so that `maxRequestSize` is enforced before filters that read the request body, such as ext_proc. The default placement is unchanged.

For more information, see [Buffering]({{< link-hextra path="/traffic-management/buffering/" >}}).

#### Fetch timeout for remote JWKS {#v25-remote-jwks-timeout}

You can now set an optional `timeout` on `remoteJwks` in a JWT TrafficPolicy to bound how long the gateway waits when it fetches keys from a remote JWKS server.

For more information, see [JWT]({{< link-hextra path="/security/jwt/" >}}).

#### Maximum connection duration {#v25-max-connection-duration}

You can now set a maximum connection duration on ListenerPolicy for downstream connections and on BackendConfigPolicy for upstream connections. Use it to recycle long-lived connections so that clients periodically re-resolve DNS and pick up new endpoints.

For more information, see [Listeners]({{< link-hextra path="/setup/listeners/" >}}) and [BackendConfigPolicy]({{< link-hextra path="/about/policies/backendconfigpolicy/" >}}).

#### HTTP protocol upgrades {#v25-http-upgrades}

You can now configure HTTP protocol upgrades with `httpUpgrade` in a TrafficPolicy, including CONNECT termination. Use it to allow protocols such as WebSocket through a route.

For more information, see [Listeners]({{< link-hextra path="/setup/listeners/" >}}).

#### Gateway-wide local rate limits {#v25-rate-limit-share}

The `rateLimit.local` block in a TrafficPolicy gains an optional `shareAcrossGateway` field. When it is true, the token bucket applies to the Gateway as a whole and is divided evenly across its proxy replicas, so the rate you configure no longer scales with the replica count.

For more information, see [Local rate limiting]({{< link-hextra path="/security/ratelimit/local/" >}}).

#### Clock skew tolerance for JWT providers {#v25-jwt-clock-skew}

You can now set `clockSkew` on a GatewayExtension JWT provider to allow clock drift between the identity provider, the gateway, and the backend service when the `exp` and `nbf` claims are checked. Omit it to keep Envoy's 60-second default.

For more information, see [OAuth2 and OIDC]({{< link-hextra path="/security/oauth/" >}}).




<!--

### ⚒️ Installation changes {#v2.2-installation-changes}

### 🔄 Feature changes {#v2.2-feature-changes}

### 🗑️ Deprecated or removed features {#v2.2-removed-features}

### 🚧 Known issues {#v2.2-known-issues}
-->

