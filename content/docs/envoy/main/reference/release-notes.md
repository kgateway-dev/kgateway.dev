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

#### Kubernetes Gateway API version 1.6.0 {#gw-api}

The Kubernetes Gateway API dependency is updated to support version 1.6.0. This version introduces several changes, including:

* **New `kgateway.dev/Programmed` condition on Routes**: Route programming issues, such as conflicts, dropped routes, or replaced routes, are now surfaced on the new `kgateway.dev/Programmed` condition instead of the `Accepted` condition. The `Accepted` condition now reflects semantic validity only. Update any tooling or automation that checks the `Accepted` condition to detect route programming failures.
* **TCPRoute promoted to v1**: The TCPRoute resource is promoted from `gateway.networking.k8s.io/v1alpha2` to `gateway.networking.k8s.io/v1`. Update your TCPRoute manifests to use `apiVersion: gateway.networking.k8s.io/v1`.
* **`disableStatsOnProxy` Helm value removed**: The `disableStatsOnProxy` Helm value and the `KGW_DISABLE_STATS_ON_PROXY` controller environment variable are removed. The dedicated Prometheus listener on port 9091 is now always included in the Envoy bootstrap config by default. To disable stats on the proxy, set `spec.kube.stats.enabled: false` in a `GatewayParameters` resource. Note that disabling proxy stats, only removes the Prometheus scrape listener and pod annotations from the proxy pod. However, Envoy continues to collect internal stats and they remain accessible via the admin interface on port 19000. For more information, see [Disable stats]({{< link-hextra path="/observability/gateway-metrics/#disable-stats" >}}).

### 🌟 New features {#v23-new-features}

#### Controller changes {#v24-controller-changes}

The following controller configuration options are now available:

* **Customizable controller probes**: Override the readiness and startup probes for the kgateway controller container by using the `controller.readinessProbe` and `controller.startupProbe` Helm values. Settings are deep-merged with the defaults, so you only need to specify the fields you want to change. For more information, see [Controller probes]({{< link-hextra path="/install/advanced/#controller-probes" >}}).
* **Configurable admin server bind address**: Configure the bind address for the kgateway controller's admin and debug server by using the `controller.admin.bindAddress` Helm value or the `KGW_ADMIN_BIND_ADDRESS` environment variable. The server listens on port 9095 and binds to `localhost` by default. Set `bindAddress` to `0.0.0.0` to expose the server outside the pod for profiling or diagnostics in trusted environments. For more information, see [Controller admin server bind address]({{< link-hextra path="/install/advanced/#controller-admin-server-bind-address" >}}).
* **xDS first-connect grace period**: By default, the control plane waits 1 second after a new proxy connects before sending its first xDS snapshot. This prevents newly started gateway pods from receiving incomplete configuration after a controller restart. Adjust the grace period by using the `KGW_XDS_FIRST_CONNECT_DELAY` environment variable on the controller, or set it to `0` to disable the grace period entirely.
* **ReferenceGrant enforcement modes**: Configure how strictly kgateway enforces Gateway API ReferenceGrant requirements for cross-namespace references by using the `KGW_REFERENCE_GRANT_MODE` environment variable. Choose between `STRICT` (all cross-namespace references require a ReferenceGrant), `PERMISSIVE` (default, enforces grants for `BackendRef` and `SecretRef` but not `ExtensionRef`), or `OFF` (disables all enforcement). For more information, see [ReferenceGrant enforcement modes]({{< link-hextra path="/install/advanced/#referencegrant-modes" >}}).

#### ExtProc changes {#v24-extproc-changes}

The following ExtProc features are now available in the GatewayExtension resource:

* **Configurable filter stages**: Control where in the Envoy filter chain an ExtProc filter runs by setting the `filterStage` field. You can also apply multiple ExtProc filters to the same route at different stages. For more information, see [Staged ExtProc filters]({{< link-hextra path="/traffic-management/extproc/filter-stages/" >}}).
* **Forward Envoy attributes**: Configure the `requestAttributes` field to forward connection-level Envoy attributes, such as `source.address` or `connection.requested_server_name`, to your ExtProc server. Envoy populates the `ProcessingRequest.attributes` map with the specified attribute values on every HTTP request. For more information, see [Request attributes]({{< link-hextra path="/traffic-management/extproc/header-manipulation/#request-attributes" >}}).

#### Header control enhancements{#v24-header-control}

The following header control features are now available:

* **Forward client certificate header**: Configure how the gateway proxy handles the `x-forwarded-client-cert` (XFCC) header before forwarding requests to upstream backends by using the `forwardClientCertDetails` field in the ListenerPolicy. By default, Envoy strips the XFCC header from all requests. For more information, see [Forward client certificate header]({{< link-hextra path="/traffic-management/header-control/forward-xfcc/" >}}).
* **Strip port from Host header**: Use the `stripHostPortMode` setting in the HTTP settings of the ListenerPolicy resource to strip the port information from the `Host` or `authority` header before forwarding requests. Choose between `AnyPort` to remove any port, or `MatchingPort` to remove the port only if it matches the listener's own port. For more information, see [Strip port from Host header]({{< link-hextra path="/traffic-management/header-control/strip-port-host/" >}}).
* **Limit request header count**: Use the `maxHeadersCount` field in the HTTP settings of the ListenerPolicy resource to set the maximum number of headers that Envoy accepts on incoming requests. Requests that exceed the limit receive a `431 Request Header Fields Too Large` response for HTTP/1.x connections and a stream reset for HTTP/2 connections. If unset, Envoy's built-in default of 100 headers is used. For more information, see [Limit request header count]({{< link-hextra path="/traffic-management/header-control/max-headers-count/" >}}).
* **Inject header values from Kubernetes Secrets**: Source HTTP header values from Kubernetes Secrets instead of inlining them in your route configuration. Use the `secretRef` field on the `HTTPHeaderFilter` in a {{< reuse "kgw-docs/snippets/trafficpolicy.md" >}} resource to reference a secret. The gateway proxy automatically injects the secret value as a request or response header at runtime. For more information, see [Add a header from a secret]({{< link-hextra path="/traffic-management/header-control/request-header/#header-from-secret" >}}).

#### AWS backend updates {#v24-aws}

The following AWS backend features are now available:

* **AssumeRole authentication**: You can now configure AWS Lambda and EC2 backends to use role chaining for authentication. The gateway proxy uses its ambient IRSA credentials to call `sts:AssumeRole` and obtain temporary credentials for the specified role, rather than relying on long-lived secrets. For more information, see [Access AWS Lambda with a service account]({{< link-hextra path="/traffic-management/destination-types/backends/lambda/service-accounts/" >}}) and [AWS EC2]({{< link-hextra path="/traffic-management/destination-types/backends/ec2/" >}}).
* **AWS EC2 backend**: You can now route traffic directly to AWS EC2 instances that are discovered dynamically by using tag-based filters. The gateway proxy periodically calls `ec2:DescribeInstances` to refresh the list of running instances that match your filters, and serves the endpoints to Envoy through EDS (Endpoint Discovery Service). To enable this feature, set `controller.enableAwsEc2Discovery=true` in your Helm values. For more information, see [AWS EC2]({{< link-hextra path="/traffic-management/destination-types/backends/ec2/" >}}).

#### Istio integration updates {#v24-istio}

The following Istio integration features are now available:

* **Exclude ServiceEntries from discovery**: You can now exclude specific Istio ServiceEntry resources from the gateway's backend and endpoint discovery by using Kubernetes label selectors. To enable this feature, set the `serviceEntriesExclusionLabelSelectors` Helm value to a list of selectors. Any ServiceEntry that matches a selector is ignored during the backend and endpoint discovery phase. For more information, see [Exclude ServiceEntries from discovery]({{< link-hextra path="/integrations/istio/ambient/ambient-ingress/#exclude-serviceentries" >}}).
* **Cluster draining weights**: The gateway proxy now honors the `solo.io/draining-weight` annotation on east-west and remote peering gateways when routing ingress traffic to a multicluster ambient mesh. Previously, the draining weight was respected by ztunnel and waypoints for east-west traffic, but the proxy continued to send ingress traffic to a draining cluster, resulting in connection errors. For more information, see [Cluster draining weights]({{< link-hextra path="/integrations/istio/ambient/ambient-ingress/#cluster-draining" >}}).

#### Envoy local replies {#v24-local-replies}

You can now customize the format and content of error responses that Envoy generates directly, such as 404 no-route and 403 policy-denial replies, by configuring the `localReplies` field in a ListenerPolicy resource. You can set a default body format that applies to all local replies on a listener, or use mappers to intercept specific replies and override their status code, body, or response headers.

For more information, see [Local replies]({{< link-hextra path="/traffic-management/local-replies/" >}}).

#### Custom Envoy bootstrap config {#v24-custom-bootstrap}

You can now inject custom Envoy bootstrap configuration into a managed gateway proxy by overriding the bootstrap ConfigMap that the control plane generates with a `deploymentOverlay` in the {{< reuse "kgw-docs/snippets/gatewayparameters.md" >}} resource. Use this method to configure bootstrap-level options that are not exposed as built-in fields, such as `stats_config.histogram_bucket_settings` to tune histogram bucket boundaries for your metrics.

For more information, see [Custom Envoy bootstrap config]({{< link-hextra path="/setup/customize/envoy/custom-bootstrap/" >}}).

#### PROXY protocol on the Envoy readiness listener {#v24-readiness-proxy-protocol}

You can now enable the PROXY protocol listener filter on the Envoy readiness listener (port 8082) by setting `spec.kube.envoyContainer.bootstrap.enableReadinessProbeProxyProtocol: true` in the {{< reuse "kgw-docs/snippets/gatewayparameters.md" >}} resource. This configuration allows an external load balancer that prepends PROXY protocol headers, such as an AWS NLB with proxy protocol v2 enabled, to perform health checks against the readiness port. Kubelet probes continue to work because the filter accepts connections without a PROXY header.

For more information, see [Readiness listener PROXY protocol]({{< link-hextra path="/traffic-management/proxy-protocol/#readiness" >}}).

#### Route source metadata {#v24-route-source-metadata}

You can now enable the proxy to attach route source metadata to every Envoy route. When enabled, each Envoy route receives a `dev.kgateway.route_source` filter metadata entry that identifies the originating Kubernetes route resource by `kind`, `group`, `name`, `namespace`, and `rule`. You can reference this metadata in access log format strings by using the `%METADATA(ROUTE:dev.kgateway.route_source:name)%` command operator. Note that this metadata is not surfaced as OTel span attributes and does not appear in distributed traces.

To enable this feature, set `enableRouteSourceMetadata: true` in your Helm values or set the `KGW_ENABLE_ROUTE_SOURCE_METADATA=true` environment variable on the kgateway controller deployment. This feature is disabled by default.

For more information, see [Access logging]({{< link-hextra path="/security/access-logging/" >}}).

#### Downstream TCP keepalive {#v24-downstream-tcp-keepalive}

You can now configure TCP keepalive for downstream client connections on a gateway listener, such as the idle time before probes start, the interval between probes, and the maximum number of probes before a connection is considered stale, by using the `tcpKeepalive` field in the ListenerPolicy resource. 

For more information, see [TCP keepalive]({{< link-hextra path="/resiliency/tcp-keepalive/" >}}).

#### Downstream HTTP/2 protocol options {#v24-http2-protocol-options}

You can now configure the HTTP/2 connection behavior between downstream clients and the gateway proxy by setting the `http2ProtocolOptions` field in the ListenerPolicy resource. The new settings let you configure the initial stream and connection flow-control window sizes and the maximum number of concurrent streams per connection.

For more information, see [HTTP/2 downstream]({{< link-hextra path="/traffic-management/http2-downstream/" >}}).

#### BackendConfigPolicy merge semantics {#v24-bcp-merge}

When multiple BackendConfigPolicy resources target the same backend, their fields are now merged. If two or more policy resources configure the same top-level fields, only the oldest policy fields are enforced. If a BackendConfigPolicy and a BackendTLSPolicy both target the same backend, the BackendTLSPolicy takes precedence for TLS configuration and an `Overridden` condition is set on the BackendConfigPolicy to inform you of the conflict.

For more information, see [BackendConfigPolicy]({{< link-hextra path="/about/policies/backendconfigpolicy/#policy-priority-and-merging-rules" >}}).

#### Zone-aware routing {#v24-zone-aware-routing}

You can now configure zone-aware routing for backend services by using the `loadBalancer.zoneAware` field in a BackendConfigPolicy resource. Zone-aware routing instructs the gateway proxy to prefer endpoints in its own availability zone, reducing cross-zone latency and network costs. 

For more information, see [Zone-aware routing]({{< link-hextra path="/traffic-management/zone-routing/" >}}).

#### Internal redirects {#v24-internal-redirects}

You can now configure the gateway proxy to follow upstream HTTP redirect responses (3xx) on behalf of the client. Instead of returning the redirect to the client, the proxy reads the `Location` header from the redirect response, sends a new request to that URL internally, and returns only the final response. The client never sees the intermediate redirect.

For more information, see [Internal redirects]({{< link-hextra path="/traffic-management/redirect/internal/" >}}).

#### Cookie value retrieval functions in transformations {#v24-get-cookie}

You can now use the `get_cookie(cookie_name)` and `get_cookie_i(cookie_name)` functions in the rustformation templating language for transformations to retrieve the value of a `Cookie` request header. 

For more information, see [Templating language]({{< link-hextra path="/traffic-management/transformations/templating-language/" >}}).

#### Async fetch and retry support for remote JWKS {#v24-jwks-async-fetch}

You can now configure how kgateway fetches the remote JSON Web Key Set (JWKS) that is used for JWT validation by using the `asyncFetch` and `retryPolicy` fields on the `remoteJWKS` section of a GatewayExtension resource.

- **`asyncFetch`**: Fetches and caches the JWKS asynchronously on a background timer instead of synchronously during request handling. This setting prevents JWT validation failures when the JWKS server is slow or temporarily unavailable. For more information, see [Async JWKS fetch]({{< link-hextra path="/security/jwt/simple/basic/#async-fetch" >}}). 
- **`retryPolicy`**: Configures exponential backoff retries when the JWKS server is unavailable. For more information, see [JWKS retry policy]({{< link-hextra path="/security/jwt/simple/basic/#jwks-retry-policy" >}}). 

#### HTTP listener isolation {#v24-http-listener-isolation}

{{< reuse "kgw-docs/snippets/kgateway-capital.md" >}} now supports the Gateway API GatewayHTTPListenerIsolation conformance feature. When multiple HTTP listeners share the same port, routes on a less-specific listener no longer interfere with hostnames owned by a more-specific sibling listener. This ensures predictable, spec-compliant hostname ownership in multi-listener configurations.



<!--

### ⚒️ Installation changes {#v2.2-installation-changes}

### 🔄 Feature changes {#v2.2-feature-changes}

### 🗑️ Deprecated or removed features {#v2.2-removed-features}

### 🚧 Known issues {#v2.2-known-issues}
-->

