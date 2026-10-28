---
title: Release notes
description: What's new, breaking changes, and bug fixes for each kgateway release.
weight: 100
---

Review the release notes for kgateway. For a detailed list of changes between tags, use the [GitHub Compare changes tool](https://github.com/kgateway-dev/kgateway/compare/).

## 2.5.0

### 🔥 Breaking changes {#v25-breaking-changes}

#### Gateway API 1.7.0 {#v25-gw-api}

The Kubernetes Gateway API dependency is updated to support version 1.7.0. To upgrade the Gateway API custom resources in your cluster, see [Upgrade]({{< link-hextra path="/operations/upgrade/" >}}). For all changes in this version, see the [Gateway API release notes](https://github.com/kubernetes-sigs/gateway-api/releases/tag/v1.7.0). The following changes can affect your {{< reuse "kgw-docs/snippets/kgateway.md" >}} configuration.

* **Session persistence in HTTPRoutes is deprecated**: The Gateway API version 1.7 deprecates the `sessionPersistence` field of an HTTPRoute rule in favor of session persistence on the backend. In {{< reuse "kgw-docs/snippets/kgateway.md" >}}, you can set up session persistence in the experimental `sessionPersistence` field of a BackendConfigPolicy instead. The HTTPRoute field still works in this version, but a BackendConfigPolicy that targets the backend takes precedence. If you keep the HTTPRoute field, note the following changes in the Gateway API version 1.7.
  * **Renamed fields**: The `sessionName` and `cookieConfig` fields are removed. Use `cookie.name` and `cookie.lifetimeType` for cookies, and `header.name` for headers. The API server rejects an HTTPRoute that sets the removed fields, so migrate your HTTPRoutes before you upgrade the Gateway API CRDs.
  * **Default cookie lifetime**: If you set `absoluteTimeout` for cookie-based session persistence and do not set `cookie.lifetimeType`, the cookie now has the `Session` lifetime. Previously, the cookie got a `Max-Age` from `absoluteTimeout`. A `Session` cookie has no `Max-Age`, so the client deletes it when its session ends, such as when the browser closes, and `absoluteTimeout` has no effect. To keep the previous behavior, set `cookie.lifetimeType: Permanent`.
  * For more information about both options, see [Session persistence]({{< link-hextra path="/traffic-management/session-affinity/session-persistence/" >}}).
* **Retries**: The `retry` field of an HTTPRoute is now part of the standard channel of the Gateway API version 1.7. Retries work without the experimental CRDs and when experimental Gateway API features are disabled. If your cluster runs Gateway API version 1.6 or earlier, retries still require the experimental channel. For more information, see [Retries]({{< link-hextra path="/resiliency/retry/retry/" >}}).
* **BackendTLSPolicy and the HTTP version**: This applies if you use a BackendTLSPolicy for a Service that does not set `appProtocol` on its port. Previously, the gateway proxy always used HTTP/1.1 for these backends. Now, the proxy offers both HTTP/2 and HTTP/1.1 during the TLS handshake (ALPN) and uses the version that the backend selects, which is HTTP/2 if the backend supports it. To always use HTTP/1.1, set `appProtocol: http` on the port of the Service. For more information, see [HTTP version]({{< link-hextra path="/security/backend-tls/#http-version" >}}).

#### Kubernetes versions {#v25-kubernetes-versions}

{{< reuse "kgw-docs/snippets/kgateway.md" >}} 2.5 supports Kubernetes versions 1.33 to 1.37. Support for Kubernetes 1.32 is removed. If your cluster runs Kubernetes 1.32, upgrade the cluster to version 1.33 or later before you upgrade {{< reuse "kgw-docs/snippets/kgateway.md" >}}. For the supported versions of other components, see [Supported versions]({{< link-hextra path="/reference/versions/" >}}).

#### Envoy 1.39 {#v25-envoy-139}

The Envoy dependency in {{< reuse "kgw-docs/snippets/kgateway.md" >}} was upgraded to 1.39.x. For all upstream changes, see the [Envoy 1.39 changelog](https://www.envoyproxy.io/docs/envoy/latest/version_history/v1.39/v1.39). The following upstream breaking changes can affect your gateways. {{< reuse "kgw-docs/snippets/kgateway.md" >}} does not expose Envoy runtime guards, so you cannot revert these changes with a setting.

* **TLS client versions**: On listeners that terminate or inspect TLS, such as HTTPS and TLS listeners, the proxy now rejects clients that send a TLS version outside of the range TLS 1.0 to TLS 1.3. Previously, the proxy did not check the client's version at this stage. If you have legacy clients, check the TLS versions that they send before you upgrade.
* **OpenTelemetry trace sampling**: The OpenTelemetry tracer now honors the sampling decisions that the proxy makes when a request enters, including `clientSampling`, `randomSampling`, and `overallSampling` in the `tracing` section of your ListenerPolicy. Previously, a request that arrived with a sampled `traceparent` header could be exported even when these settings excluded it. After the upgrade, you might see fewer spans. For more information, see [Tracing]({{< link-hextra path="/observability/tracing/" >}}).
* **Upstream TLS failure reasons**: The proxy no longer includes the reason for an upstream transport failure, such as a TLS certificate validation error, in the response body that it sends to the client. The reason is still available in the access log through the `%UPSTREAM_TRANSPORT_FAILURE_REASON%` command operator. If your clients or tests match on this text in the response body, such as for a Backend that uses a BackendTLSPolicy, update them to match the status code instead.
* **Multi-value header matching**: A header match now checks each value of a header that is sent in separate header lines, instead of the comma-joined string. For example, a request that sends `x-role: user` and `x-role: admin` as two headers now matches a rule for `admin`, and no longer matches a rule for `user,admin`. A single header line that contains `user,admin` is still matched as one value. This change applies to header matches in HTTPRoutes and to other policies that match on headers.

#### Listener ports are no longer container ports {#v25-listener-container-ports}

The proxy Deployment no longer lists Gateway and ListenerSet listener ports, such as `listener-8080`, as container ports. Only `http-monitoring` (9091) remains, when stats are enabled. The Service that {{< reuse "kgw-docs/snippets/kgateway.md" >}} generates for the Gateway is unchanged.

When you upgrade to 2.5, the pod template of every managed Gateway changes, so the proxy pods restart once during the upgrade. After the upgrade, a listener port change restarts the proxy pods only in the following cases:

* **First low port**: A Gateway gains its first listener port below port number 1024. {{< reuse "kgw-docs/snippets/kgateway.md" >}} adds a pod setting that allows the proxy to bind low ports. For example, a Gateway with listeners on ports 8080 and 8443 restarts when you add a listener on port 443. Adding a listener on port 80 afterward does not restart the pods, because the Gateway already has a port below 1024.
* **Last low port**: A Gateway loses its last listener port below port number 1024. {{< reuse "kgw-docs/snippets/kgateway.md" >}} removes that pod setting. For example, a Gateway with listeners on ports 80 and 443 does not restart when you remove port 80, but restarts when you also remove port 443.

Any resource, such as a custom proxy Service or a NetworkPolicy resource, that refers to the proxy's container ports by name no longer works. Before you upgrade, check the following setups and update them if needed:

* **Named port references**: If a NetworkPolicy rule or a Service that you created uses the `listener-<port>` name format to reference a proxy port, switch to the port number. With a default-deny NetworkPolicy, a rule that no longer matches blocks traffic to the proxy. The Service that {{< reuse "kgw-docs/snippets/kgateway.md" >}} generates already uses port numbers and is not affected.
* **`hostNetwork` set in a deployment overlay, with stats disabled**: Container ports also act as host ports, which keep two proxies that use the same port off the same node. Without the listener container ports, nothing keeps two proxies apart, the scheduler can place both on one node, and the second proxy fails to start. If stats are enabled, which is the default, the `http-monitoring` port 9091 still keeps the proxies apart. To prevent the problem if you disable stats, add your Gateway's listener ports as container ports in the overlay. For an example, see [Run the proxy with hostNetwork]({{< link-hextra path="/setup/customize/configs/#host-network-ports" >}}).

#### Drain time for listener changes {#v25-drain-time}

The gateway proxy now starts Envoy with `--drain-time-s 60` and `--drain-strategy immediate` settings. Previously, the proxy used the Envoy defaults of 600 seconds and `gradual`.

When a listener is modified or removed, Envoy now asks the connections on the old listener to close right away, and force-closes the connections that are still open after 60 seconds. Previously, the connections were phased out gradually over 10 minutes. This change frees the memory that the old listener configuration holds much sooner. However, long-lived connections, such as WebSockets or streams, can now be closed after 60 seconds when their listener is modified.

If your clients cannot handle a connection that closes after 60 seconds, you can restore the previous behavior by setting the drain flags in the `envoyContainer.extraArgs` field of your {{< reuse "kgw-docs/snippets/gatewayparameters.md" >}}. For an example, see [Change the listener drain behavior]({{< link-hextra path="/setup/customize/configs/#drain-settings" >}}).

#### Gateway proxy stats per listener {#v25-stat-prefix}

The Envoy HTTP connection manager and TCP proxy stats of the gateway proxy are now reported per listener. Previously, all HTTP and HTTPS listeners shared the stat prefix `http`. Now, each listener has its own prefix, such as `http_8080` for an HTTP listener on port 8080, or `https_8443_tenant-a` for an HTTPS listener named `tenant-a` on port 8443. The stat prefixes of TCPRoutes and TLSRoutes also changed.

Update the following settings if you use these stats.

* **Prometheus queries and dashboards** that filter on `envoy_http_conn_manager_prefix="http"`, or that use the previous per-route `envoy_tcp_*` metric names. These queries no longer return data.
* **`stats.matcher` entries** in your GatewayParameters resources that match the earlier prefix, such as `http.http.`. These entries no longer match any stats.

For the stat prefix of each listener type and example queries, see [Per-listener metrics]({{< link-hextra path="/observability/gateway-metrics/#listener-metrics" >}}).


#### SDS sidecar binds to loopback {#v25-sds-loopback-bind}

The SDS (Secret Discovery Service) sidecar now binds to `127.0.0.1:8234` (loopback) by default instead of `0.0.0.0:8234`. Previously, any pod on the cluster network could reach the SDS endpoint. Because all consumers of SDS run in the same pod as the sidecar, restricting the bind address to loopback closes this unintended exposure.

If you need to reach the SDS sidecar from outside its pod in a trusted environment, set the `SDS_SERVER_ADDRESS=0.0.0.0:8234` environment variable on the `sds` container. For an example, see [Change the SDS sidecar's pod-network bind address]({{< link-hextra path="/setup/customize/configs/#sds-bind-address" >}}). If you use a custom deployment overlay or manifest that overrides the SDS container's readiness probe, note that the default probe also changed, from a `tcpSocket` check on port 8234 to an `exec` probe that runs `sds healthcheck`, because a TCP probe against the pod IP no longer succeeds against a loopback-only listener.

#### Route source metadata changes {#v25-route-source-metadata}

When you enable route source metadata, the `dev.kgateway.route_source` filter metadata changes in the following ways:

* **Rule name**: The `rule` field now holds the rule name from the originating route resource instead of a generated Envoy route name.
* **Match**: A new `match` field identifies the match within the rule that handled the request.

If your access log formats, log queries, or dashboards parse the previous `rule` value, update them. For more information, see [Route source metadata]({{< link-hextra path="/security/access-logging/#route-source-metadata" >}}).


#### Waypoint support removed {#v25-waypoint-removed}

The deprecated support for running {{< reuse "kgw-docs/snippets/kgateway.md" >}} as an Istio ambient waypoint is removed. The following items are removed:

* The `kgateway-waypoint` GatewayClass.
* The translation of Istio AuthorizationPolicy resources.
* The `KGW_WAYPOINT_LOCAL_BINDING` setting.

To move your existing waypoints to Istio waypoints, see the [migration guide](https://github.com/kgateway-dev/kgateway/blob/main/docs/guides/migrating-kgateway-waypoints.md).

Sending ingress traffic through the Istio waypoint of a destination is still supported. If you label a Service or ServiceEntry with `istio.io/ingress-use-waypoint=true`, the gateway sends ingress traffic to the cluster IP of the destination, so that ztunnel passes the traffic through the waypoint of the destination. To enable this feature, set the `waypoint.enabled` Helm value to `true`. If you do not use Helm, set the `KGW_INGRESS_USE_WAYPOINTS=true` environment variable on the controller. The default of this setting changed from `true` to `false`, so enable it explicitly if you use this feature. The deprecated `KGW_ENABLE_WAYPOINT` setting still enables this feature if you do not set `KGW_INGRESS_USE_WAYPOINTS`.

> [!NOTE]
> The controller ClusterRole still grants `get`, `list`, and `watch` permissions on `authorizationpolicies.security.istio.io` APIs, so that upgrades are safe. However, {{< reuse "kgw-docs/snippets/kgateway.md" >}} no longer uses them. The permissions are removed in the next minor release. If you maintain a custom ClusterRole, or use these permissions for something else, plan for their removal.

#### HTTPListenerPolicy removed {#v25-httplistenerpolicy-removed}

The deprecated HTTPListenerPolicy custom resource definition (CRD) is removed. Versions 2.4.x and earlier install this CRD, and version 2.5.x does not, so the upgrade deletes the CRD from your cluster. Kubernetes then garbage-collects every remaining HTTPListenerPolicy object in the cluster. 

Any HTTPListenerPolicy resource that exists in your cluster at the time of the upgrade is deleted along with the CRD, and the listener configuration that it applied stops taking effect.

**Required action**: Migrate your configuration to the ListenerPolicy resource **before** you upgrade {{< reuse "kgw-docs/snippets/kgateway.md" >}} by moving the policy spec under the `spec.default.httpSettings` block in your ListenerPolicy resource. If you already migrated to the ListenerPolicy in an earlier version, no action is needed. 

1. List the HTTPListenerPolicy resources in your cluster. 
   ```sh
   kubectl get httplistenerpolicies -A
   ```
   
2. For each resource, create an equivalent ListenerPolicy resource. You find the corresponding fields in the `spec.default.httpSettings` block. For more information about the policy and supported fields, see [ListenerPolicy]({{< link-hextra path="/reference/api/#listenerpolicy" >}}). For the field-by-field mapping, see the [HTTPListenerPolicy to ListenerPolicy migration guide](https://github.com/kgateway-dev/kgateway/blob/main/docs/guides/migrating-httplistenerpolicy-to-listenerpolicy.md) in the kgateway open source project.

3. Confirm that the new resources are accepted and that your listeners behave as expected.
   ```sh
   kubectl get ListenerPolicy <name> -n <namespace> -o yaml
   ```

4. Delete the HTTPListenerPolicy objects. 
   ```sh
   kubectl delete HTTPListenerPolicy <name> -n <namespace>
   ```

5. Continue with the [upgrade]({{< link path="/operations/upgrade/" >}}).

#### Control plane metrics and Go functions removed {#v25-metrics-functions-removal}

The control plane no longer emits the following metrics. If your dashboards, alerts, or recording rules use any of them, update them. For more information, see [Control plane metrics]({{< link-hextra path="/observability/control-plane-metrics/" >}}).

* **Status sync metrics**: Use the new `kgateway_status_writes_total{kind, result}` metric instead of the following metrics. To catch status writes that still fail after all retries, alert on `result="error"`.
  * `kgateway_status_syncer_status_syncs_total`
  * `kgateway_status_syncer_status_sync_duration_seconds`
  * `kgateway_resources_status_syncs_started_total`
  * `kgateway_resources_status_syncs_completed_total`
  * `kgateway_resources_status_sync_duration_seconds`
* **High-cardinality metrics**: The following metrics and series are removed.
  * The `kgateway_translator_translations_running` gauge.
  * The `kgateway_controller_reconciliations_running` gauge.
  * The `translator="TranslateHTTPRoute"` series of the `kgateway_translator_translations_total` and `kgateway_translator_translation_duration_seconds` metrics.

If you build on kgateway as a Go library, the following functions are also removed. Stop using them in your code:

* `statussync.Writer.OnSync`
* `statussync.EndResourceStatusSyncOnWriteSuccess`
* `metrics.StartResourceStatusSync`
* `metrics.EndResourceStatusSync`

### 🌟 New features {#v25-new-features}

#### Preserve request paths {#v25-preserve-request-paths}

You can now disable Envoy's default path normalization and slash merging on a listener by using the `normalizePath` and `mergeSlashes` fields in the HTTP settings of a ListenerPolicy resource. Disable these settings for backends that depend on the original, unmodified request path, such as S3-compatible object stores that use object keys containing repeated slashes.

For more information, see [Preserve request paths]({{< link-hextra path="/traffic-management/preserve-request-paths/" >}}).

#### Handle escaped slashes in request paths {#v25-escaped-slashes}

You can now control how the gateway proxy handles escaped slashes (`%2F`) in request paths. In the `httpSettings` of a ListenerPolicy, set `pathWithEscapedSlashesAction` to `KeepUnchanged`, `RejectRequest`, `UnescapeAndRedirect`, or `UnescapeAndForward`. By default, the proxy keeps escaped slashes unchanged. This setting is useful if a backend decodes `%2F` itself and you want to prevent requests from bypassing your path-based rules. For more information, see [Handle escaped slashes]({{< link-hextra path="/traffic-management/preserve-request-paths/#escaped-slashes" >}}).

#### Strip trailing dots from hostnames {#v25-strip-trailing-host-dot}

You can now use the `stripTrailingHostDot` field in the HTTP settings of a ListenerPolicy resource to strip a trailing dot from the `Host` or `:authority` header before route matching. Use this policy when a client sends a fully qualified domain name with a trailing dot, such as `example.com.`, which does not otherwise match an HTTPRoute hostname of `example.com`.

For more information, see [Strip trailing dots from hostnames]({{< link-hextra path="/traffic-management/header-control/strip-trailing-host-dot/" >}}).

#### HTTP protocol upgrades {#v25-http-upgrades}
You can now allow WebSocket, `CONNECT`, and other HTTP protocol upgrades through your gateway proxy. Enable upgrade tokens listener-wide with a ListenerPolicy, or scope them to individual routes with a {{< reuse "kgw-docs/snippets/trafficpolicy.md" >}}, which is also the only way to terminate `CONNECT` requests at the gateway proxy. For more information, see [HTTP protocol upgrades]({{< link-hextra path="/traffic-management/http-upgrades/" >}}).

#### HTTP CONNECT tunnels for backend connections {#v25-http-connect-tunnels-for-backend-connections}

You can now tunnel connections from a Static {{< reuse "kgw-docs/snippets/backend.md" >}} through an HTTP forward proxy, such as an egress proxy. In a BackendConfigPolicy that targets the {{< reuse "kgw-docs/snippets/backend.md" >}}, use `spec.tunnel.proxy.backendRef` to reference the forward proxy. The gateway proxy sends an HTTP `CONNECT` request to the forward proxy, which opens the connection to the destination. You can also use `spec.tunnel.headers` to add headers, such as `Proxy-Authorization`, to the `CONNECT` request. Tunnels are supported for single-host Static {{< reuse "kgw-docs/snippets/backend.md" >}} destinations only. For more information, see [HTTP CONNECT tunnels]({{< link-hextra path="/traffic-management/http-connect-tunnels/" >}}).

#### Forward 100-continue requests to the backend {#v25-proxy-100-continue}

You can now use the `proxy100Continue` field in the HTTP settings of a ListenerPolicy resource to let the backend decide whether to accept a request body instead of having the gateway proxy respond automatically. When enabled, the gateway proxy forwards the `Expect: 100-continue` header to the backend and passes the backend's `100 Continue` response back to the client.

For more information, see [Forward 100-continue requests]({{< link-hextra path="/traffic-management/proxy-100-continue/" >}}).

#### Move the buffer filter before body-reading filters {#v25-buffer-filter-stage}

You can now use the `buffer.filterStage` field on a {{< reuse "kgw-docs/snippets/trafficpolicy.md" >}} resource to place the buffer filter at an earlier position in the HTTP filter chain. By default, the buffer filter runs after authentication, authorization, and rate limiting, so a filter that reads the request body first, such as external auth with request-body checks or ExtProc, can prevent `buffer.maxRequestSize` from being enforced. 

For more information, see [Move the buffer filter before body-reading filters]({{< link-hextra path="/traffic-management/buffering/#move-the-buffer-filter-before-body-reading-filters" >}}).

#### Session persistence in the BackendConfigPolicy {#v25-backend-session-persistence}

You can now configure session persistence, also known as sticky sessions, in the `sessionPersistence` field of a [BackendConfigPolicy]({{< link-hextra path="/about/policies/backendconfigpolicy/" >}}). The policy pins a client to one instance of a Service or Backend by using a cookie or a header, and applies to the HTTPRoutes and GRPCRoutes that route to it. It replaces session persistence in HTTPRoute rules, which the Gateway API version 1.7 deprecates. If you set both, the BackendConfigPolicy takes precedence. This feature is experimental. For more information, see [Session persistence]({{< link-hextra path="/traffic-management/session-affinity/session-persistence/" >}}).

#### gRPC statistics {#v25-grpc-stats}

You can now use the `grpcStats` field on a ListenerPolicy resource to add Envoy's `grpc_stats` HTTP filter to the listeners on a Gateway. The filter records per-service and per-method gRPC metrics, including the gRPC status code, which isn't visible in ordinary HTTP response-code metrics. Collect statistics for every gRPC method, or use an allow list to limit per-method statistics to a bounded set of methods.

For more information, see [gRPC statistics]({{< link-hextra path="/traffic-management/grpc-statistics/" >}}).

#### IPv6 and dual-stack support {#v25-ipv6-and-dual-stack-support}

You can now control IPv4 and IPv6 behavior in the following places. The API fields are experimental and might change in future releases.

* **Proxy Service**: Use `ipFamilyPolicy` and `ipFamilies` in the `spec.kube.service` field of a GatewayParameters resource to request an IPv4, IPv6, or dual-stack Service for the gateway proxy. For more information, see [Proxy Service IP families]({{< link-hextra path="/setup/customize/configs/#proxy-service-ip-families" >}}).
* **Backend DNS resolution**: Use `BackendConfigPolicy.spec.dns.lookupFamily` to choose which address families the gateway proxy resolves for a single Backend that is reached through DNS, such as a Static Backend with a hostname. The field overrides the controller-wide `KGW_DNS_LOOKUP_FAMILY` setting, which prefers IPv4 by default. For more information, see [DNS lookup family]({{< link-hextra path="/install/advanced/#dns-lookup-family" >}}).
* **Readiness and stats listeners**: The proxy readiness and stats listeners now follow the existing `KGW_LISTENER_BIND_IPV6` controller setting, which defaults to `true`, instead of always binding to IPv4. On nodes that disable the IPv6 kernel stack with `ipv6.disable=1`, set `KGW_LISTENER_BIND_IPV6=false` to keep an IPv4-only bootstrap. For more information, see [Listener bind address]({{< link-hextra path="/install/advanced/#listener-bind-address" >}}).

#### Control the Host header of mirrored requests {#v25-request-mirror-host}

The `requestMirror` section of a {{< reuse "kgw-docs/snippets/trafficpolicy.md" >}} now supports two new fields for controlling the `Host`/`:authority` header of requests that an HTTPRoute or GRPCRoute `RequestMirror` filter mirrors.

* **`disableShadowHostSuffixAppend`**: By default, Envoy appends `-shadow` to the `Host`/`:authority` header of mirrored requests. Set this field to `true` to send the original header unchanged. This is useful when the shadow destination has strict host-based routing rules that reject the modified header.
* **`hostRewriteLiteral`**: Replaces the `Host`/`:authority` header of mirrored requests with the specified value. Include a port if the shadow destination needs one, as the port from the original request is not carried over.

For more information, see [Mirroring]({{< link-hextra path="/resiliency/mirroring/#request-mirror" >}}).

#### Maximum connection duration {#v25-max-connection-duration}

You can now use the `maxConnectionDuration` field to set a maximum connection duration for downstream or upstream connections. 

For more information, see [Maximum connection duration]({{< link-hextra path="/resiliency/timeouts/max-connection-duration/" >}}).

#### Limit downstream connections {#v25-max-downstream-connections}

You can now set a global limit on the number of active downstream connections that the gateway proxy accepts across all listeners by using the `envoyContainer.bootstrap.maxDownstreamConnections` field in your {{< reuse "kgw-docs/snippets/gatewayparameters.md" >}} resource. By default, no limit is set. 

For more information, see [Limit downstream connections]({{< link-hextra path="/setup/customize/configs/#limit-downstream-connections" >}}).

#### Separate local-origin outlier detection failures {#v25-local-origin-outlier-detection}

The outlier detection policy that you can configure in the BackendConfigPolicy resource can now separate locally originated failures from externally generated HTTP 5xx responses. Set `splitExternalLocalOriginErrors` to `true`, then use `consecutiveLocalOriginFailure`, `enforcingConsecutiveLocalOriginFailure`, and `enforcingConsecutive5xx` to eject hosts for local-origin failures without ejecting hosts for external 5xx responses. For more information, see [Separate local-origin failures from 5xx responses]({{< link-hextra path="/resiliency/outlier-detection/#local-origin-outlier-detection" >}}).

#### Eject hosts after gateway failures {#v25-consecutive-gateway-failure}

In the `outlierDetection` of a BackendConfigPolicy, you can now set `consecutiveGatewayFailure` to eject a host after consecutive 502, 503, or 504 responses. Other 5xx responses do not count toward this threshold. When you set the field, the proxy always ejects the host after the threshold is reached. For more information, see [Eject hosts after gateway failures]({{< link-hextra path="/resiliency/outlier-detection/#gateway-failure-outlier-detection" >}}).

#### JWT enhancements {#v25-jwt-enhancements}

Several new fields extend the JWT provider in a GatewayExtension resource.

* **JWT verified token caching**: Enable Envoy's in-memory cache of successfully verified JWTs by using the `cache` field. For a successfully verified token that is presented more than once, the gateway proxy does not parse the token again, or perform a JWKS lookup and signature verification. Expired tokens are automatically removed from the cache. For more information, see [JWT caching]({{< link-hextra path="/security/jwt/simple/basic/#jwt-caching" >}}).
* **JWT clock skew tolerance**: Set how much clock drift the gateway tolerates when it verifies the `exp` and `nbf` claims of a JWT, by using the `clockSkew` field. Use this when a token that is still valid at the issuer arrives at the proxy as expired or not-yet-valid, such as when the identity provider runs outside the cluster or on a host with an unsynchronized clock. If unset, the gateway keeps Envoy's default tolerance of 60 seconds. For more information, see [Clock skew tolerance]({{< link-hextra path="/security/jwt/simple/basic/#clock-skew" >}}).
* **JWKS fetch timeout**: Set the `timeout` field on the `jwks.remote` settings to configure how long the gateway waits for the remote JWKS server to respond to a single fetch. For more information, see [JWKS fetch timeout]({{< link-hextra path="/security/jwt/simple/basic/#jwks-timeout" >}}).
* **Evaluate JWT policies without rejecting requests**: Set `validationMode: AllowMissingOrFailed` to verify tokens without rejecting requests that send a missing or invalid JWT. Use this mode to observe how a JWT policy behaves against live traffic before changing to `Strict`. Verification failures are also recorded in Envoy dynamic metadata at `envoy.filters.http.jwt_authn:failed_status`. For more information, see [Allow JWT verification without rejecting requests]({{< link-hextra path="/security/jwt/simple/basic/#allow-missing-or-failed" >}}).

#### BackendTLSPolicy supports TLS settings {#v25-backendtlspolicy-tls-settings}

You can now set TLS settings for upstream connections, such as ECDH curves, TLS versions, and signature algorithms, in the `spec.options` field of a BackendTLSPolicy. The options use the same `kgateway.dev/*` keys as Gateway listener TLS options.

For more information, see [TLS settings]({{< link-hextra path="/security/backend-tls/#tls-settings" >}}).

#### Share a local rate limit across Gateway replicas {#v25-share-local-ratelimit}

The {{< reuse "kgw-docs/snippets/trafficpolicy.md" >}} resource now supports the `shareAcrossGateway` field for local rate limiting. By default, each Envoy proxy replica enforces its own local token bucket, so the effective rate increases as the Gateway scales out. Set `shareAcrossGateway` to `true` to divide the token bucket evenly across all Gateway proxy replicas, so the configured rate applies to the Gateway as a whole.

For more information, see [Share a local rate limit across Gateway replicas]({{< link-hextra path="/security/ratelimit/local/#share-across-gateway" >}}).

#### Global rate limiting shadow mode {#v25-global-rate-limit-shadow}

GatewayExtension rate limit configuration now supports `percentEnabled` and `percentEnforced`, so you can trial global rate limit decisions before the gateway proxy denies live traffic. Set `percentEnabled: 100` and `percentEnforced: 0` to call the rate limit service and record its decision without blocking requests. For more information, see [Global rate limiting]({{< link-hextra path="/security/ratelimit/global/#gateway-extension" >}}).

#### Log ext-auth latency {#v25-extauth-latency-access-log}

External auth filters now expose per-request stats that you can reference in access logs. For example, use `%FILTER_STATE(ext_auth/<namespace>/<name>:FIELD:latency_us)%` to log how long the external auth check took. For more information, see [Log ext-auth latency]({{< link-hextra path="/security/access-logging/#extauth-latency" >}}).

#### Access logs for TCP and TLS listeners {#v25-tcp-access-log}

The ListenerPolicy now supports access logs for TCP and TLS listeners via the `tcpSettings.accessLog` field. For more information, see [Access logs for TCP and TLS listeners]({{< link-hextra path="/security/access-logging/#tcp-access-log" >}}).

#### Route change batching {#v25-route-change-batching}

The control plane now batches route changes before Gateway translation, so each affected Gateway rebuilds once per batch instead of once per route. Batching is enabled by default and waits `10ms` after the last change, up to a maximum of `100ms`. To adjust the timing, set the `KGW_TRANSLATION_DEBOUNCE` and `KGW_TRANSLATION_DEBOUNCE_MAX` environment variables on the controller. For more information, see [Tune route translation batching]({{< link-hextra path="/install/advanced/#route-translation-batching" >}}).

#### Scope xDS configuration per gateway {#v25-xds-scoping}

You can now configure the control plane to send each gateway's proxies only the clusters that the gateway's configuration references, instead of a cluster for every discovered backend. This reduces the size of the config dump and the number of stats of each proxy in clusters with many Services and few routed ones. To enable this experimental feature, set the `controller.xds.scoping.mode` Helm value to `REFERENCED`. The default is `ALL`. If you used a 2.5.0 beta with the `KGW_CLUSTER_DISCOVERY_MODE`, `KGW_CLUSTER_REFERENCE_AHEAD`, or `KGW_CLUSTER_DEREFERENCE_GRACE` setting, rename it to `KGW_XDS_SCOPING_MODE`, `KGW_XDS_SCOPING_REFERENCE_AHEAD`, or `KGW_XDS_SCOPING_DEREFERENCE_GRACE`. The control plane does not start while an old name is set. For more information, see [Scope xDS configuration per gateway]({{< link-hextra path="/install/advanced/#xds-scoping" >}}).

#### Configure leader election timings {#v25-leader-election-timings}

You can now configure the leader election timings of the controller with the `controller.leaderElection.*` Helm values. For more information, see [Leader election timings]({{< link-hextra path="/install/advanced/#leader-election-timings" >}}).

#### Controller Go memory limit tracking {#v25-controller-memory-limit}

The `controller.goMemLimitPercent` Helm value now keeps the controller's `GOMEMLIMIT` in sync with the container's memory limit as it changes, instead of setting it once at pod startup. The controller rereads the container's live memory limit every 30 seconds, so changes from a Kubernetes LimitRange resource or a Vertical Pod Autoscaler (VPA) resize take effect without restarting the pod. For more information, see [Tune the controller Go memory limit]({{< link-hextra path="/install/advanced/#controller-memory-limit" >}}).

#### Common labels on the controller pod template {#v25-controller-common-labels}

The `commonLabels` Helm value now applies to the controller pod template, in addition to the metadata of resources such as the controller Deployment. For more information, see [Common labels]({{< link-hextra path="/install/advanced/#common-labels" >}}).

#### Controller build information metric {#v25-controller-build-information-metric}

The control plane now emits the `kgateway_build_info` metric, so you can see which controller build is running from Prometheus. The metric always has the value `1`. The build details are in its labels: `version`, `revision` (Git commit), `goversion`, `goos`, and `goarch`. For more information, see [Control plane metrics]({{< link-hextra path="/observability/control-plane-metrics/#reference" >}}).

### 🔄 Feature changes {#v25-feature-changes}

#### Lambda backends set the Host header {#v25-lambda-host-header}

AWS Lambda backends now send the Lambda endpoint as the upstream `Host` header before the proxy signs the request. Previously, you had to send the `Host` header as part of your request. Now, the `Host` header is automatically generated in the format `lambda.<region>.amazonaws.com`. To use a different endpoint, set the `spec.aws.lambda.endpointURL` field of the Backend. For more information, see [Access AWS Lambda with a service account]({{< link-hextra path="/traffic-management/destination-types/backends/lambda/service-accounts/" >}}).

#### Ordered ADS delivery is on by default {#v25-ordered-ads}

The controller now sends Aggregated Discovery Service (ADS) responses to each proxy in a fixed order: clusters (CDS), endpoints (EDS), listeners (LDS), and routes (RDS). Before, responses that were ready at the same time on a busy stream could arrive out of order. A route could then reach a proxy before the cluster that the route references, and requests could fail with a transient `503` response that has the `NC` response flag.

You do not need to take any action. To restore the previous behavior, set the `KGW_ENABLE_ORDERED_ADS` environment variable to `"false"` on the controller. 

```yaml
controller:
  extraEnv:
    KGW_ENABLE_ORDERED_ADS: "false"
```

<!--

### ⚒️ Installation changes {#v2.2-installation-changes}

### 🔄 Feature changes {#v2.2-feature-changes}

### 🗑️ Deprecated or removed features {#v2.2-removed-features}

### 🚧 Known issues {#v2.2-known-issues}
-->
