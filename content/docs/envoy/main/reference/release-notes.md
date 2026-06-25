---
title: Release notes
description: What's new, breaking changes, and bug fixes for each kgateway release.
weight: 100
---

Review the release notes for kgateway. For a detailed list of changes between tags, use the [GitHub Compare changes tool](https://github.com/kgateway-dev/kgateway/compare/).

## 2.4.0

### 🔥 Breaking changes {#v23-breaking-changes}

#### Envoy 1.38

The Envoy dependency in kgateway was upgraded to 1.38.x. This change includes the following upstream breaking changes.

* **RSA key usage enforcement**: Envoy 1.38 sets [`enforce_rsa_key_usage`](https://www.envoyproxy.io/docs/envoy/v1.38.0/api-v3/extensions/transport_sockets/tls/v3/tls.proto.html#envoy-v3-api-field-extensions-transport-sockets-tls-v3-upstreamtlscontext-enforce-rsa-key-usage) to `true` by default for upstream TLS connections. If the `keyUsage` extension is present in the upstream certificate and is incompatible with the TLS usage, the TLS handshake fails. In a future version of Envoy, this option will be removed and enforcing behavior will always apply. This setting is specific to upstream TLS connections (not downstream client connections). The `keyUsage` extension tells consumers what the certificate's public key is allowed to be used for. If the extension is present but does not match the TLS role, the upstream handshake fails. Note that kgateway does not expose this setting in `BackendConfigPolicy`, so it cannot be set back to `false`. Common RSA key usage values compatible with TLS are:
  * `digitalSignature`
  * `keyEncipherment`
  * `keyCertSign` (CA certs only)
  * `cRLSign` (CA certs that sign revocation lists only)

  Verify your upstream certificates include compatible `keyUsage` values before upgrading.

* **Circuit breaker metrics**: Added a new `upstream_rq_active_overflow` counter that is incremented when a request is rejected because the `max_requests` circuit breaker is exhausted. Previously, this condition incorrectly incremented the `upstream_rq_pending_overflow` metric, making it impossible to distinguish between pending queue saturation and active request saturation. After the upgrade, only the `upstream_rq_active_overflow` is incremented for this case, so you might see a drop in `upstream_rq_pending_overflow` counts. If you have existing dashboards or alerts that rely on the `upstream_rq_pending_overflow` metric to detect `max_requests` circuit breaker trips, set the Envoy runtime flag `envoy.reloadable_features.skip_pending_overflow_count_on_active_rq` to `false` to increment both counters while you migrate your monitoring to the `upstream_rq_active_overflow` metric.
* **Memory management**: Replaced the custom timer-based tcmalloc memory release with tcmalloc's native `ProcessBackgroundActions` and `SetBackgroundReleaseRate` APIs. This provides more comprehensive background memory management, including per-CPU cache reclamation, cache shuffling, and size class resizing, in addition to memory release. The `tcmalloc.released_by_timer` stat is removed.
* **RBAC header matching**: Fixed the RBAC header matcher to validate each header value individually instead of concatenating multiple header values into a single string. This prevents potential policy bypasses when requests contain multiple values for the same header. The new behavior is enabled by default and controlled by the runtime guard `envoy.reloadable_features.rbac_match_headers_individually`.

### 🌟 New features {#v23-new-features}

#### Configurable ExtProc filter stages {#v24-extproc-filter-stages}

You can now control where in the Envoy filter chain an ExtProc filter runs by setting the `filterStage` field in the GatewayExtension resource. You can also apply multiple ExtProc filters to the same route at different stages.

For more information, see [Staged ExtProc filters]({{< link-hextra path="/traffic-management/extproc/filter-stages/" >}}).

#### Forward client certificate header {#v24-xfcc}

You can now configure how the gateway proxy handles the `x-forwarded-client-cert` (XFCC) header before forwarding requests to upstream backends by using the `forwardClientCertDetails` field in the ListenerPolicy. By default, Envoy strips the XFCC header from all requests. 

For more information, see [Forward client certificate header]({{< link-hextra path="/traffic-management/header-control/forward-xfcc/" >}}).

#### Strip port from Host header {#v24-strip-host-port}

Added the `stripHostPortMode` setting to the HTTP settings of the ListenerPolicy resource that allows you to configure the gateway proxy to strip the port information from the `Host` or `authority` header before forwarding requests to upstream backends. You can choose between two modes: 
* `AnyPort`: Removes any port from the header.
* `MatchingPort`: Removes the port only if it matches the listener's own port.  

For more information, see [Strip port from Host header]({{< link-hextra path="/traffic-management/header-control/strip-port-host/" >}}).

#### Limit request header count {#v24-max-headers-count}

Added the `maxHeadersCount` field to the HTTP settings of the ListenerPolicy resource. You can use this field to set the maximum number of headers that Envoy accepts on incoming requests. Requests that exceed the limit receive a `431 Request Header Fields Too Large` response for HTTP/1.x connections and a stream reset for HTTP/2 connections. If unset, Envoy's built-in default of 100 headers is used.

For more information, see [Limit request header count]({{< link-hextra path="/traffic-management/header-control/max-headers-count/" >}}).

#### AWS EC2 backend {#v24-ec2-backend}

You can now route traffic directly to AWS EC2 instances that are discovered dynamically by using tag-based filters. The gateway proxy periodically calls `ec2:DescribeInstances` to refresh the list of running instances that match your filters, and serves the endpoints to Envoy through EDS (Endpoint Discovery Service). To enable this feature, set `controller.enableAwsEc2Discovery=true` in your Helm values.

For more information, see [AWS EC2]({{< link-hextra path="/traffic-management/destination-types/backends/ec2/" >}}).

#### Solo Istio cluster draining weights {#v24-cluster-draining}

kgateway now honors the `solo.io/draining-weight` annotation on east-west and remote peering gateways when routing ingress traffic to a multicluster ambient mesh. Previously, the draining weight was respected by ztunnel and waypoints for east-west traffic, but kgateway continued to send ingress traffic to a draining cluster, resulting in connection errors.

When a remote cluster's east-west gateway is annotated with `solo.io/draining-weight`, kgateway adjusts the Envoy load balancing weights for that cluster's endpoints on the ingress path:

| Draining mode | Annotation value | Traffic to remote cluster |
|---|---|---|
| Off (default) | `solo.io/draining-weight: "0"` or absent | 100% |
| Partial | `solo.io/draining-weight: "40"` | 60% (100% minus the draining weight) |
| Full | `solo.io/draining-weight: "100"` | 0% (cluster excluded from Envoy endpoint set) |

#### Inject header values from Kubernetes Secrets {#v23-header-from-secret}

You can now source HTTP header values from Kubernetes Secrets instead of inlining them in your route configuration. Use the `secretRef` field on the `HTTPHeaderFilter` in a {{< reuse "docs/snippets/trafficpolicy.md" >}} resource to reference a secret. The gateway proxy automatically injects the secret value as a request or response header at runtime.

For more information, see [Add a header from a secret]({{< link-hextra path="/traffic-management/header-control/request-header/#header-from-secret" >}}).

#### Downstream HTTP/2 protocol options {#v24-http2-protocol-options}

You can now configure the HTTP/2 connection behavior between downstream clients and the gateway proxy by setting the `http2ProtocolOptions` field in the ListenerPolicy resource. The new settings let you configure the initial stream and connection flow-control window sizes and the maximum number of concurrent streams per connection.

For more information, see [HTTP/2 downstream]({{< link-hextra path="/traffic-management/http2-downstream/" >}}).

<!--

### ⚒️ Installation changes {#v2.2-installation-changes}

### 🔄 Feature changes {#v2.2-feature-changes}

### 🗑️ Deprecated or removed features {#v2.2-removed-features}

### 🚧 Known issues {#v2.2-known-issues}
-->

