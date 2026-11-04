---
title: "kgateway v2.5: Gateway API 1.7, scoped xDS, and CONNECT tunneling"
toc: false
publishDate: 2026-11-03T10:00:00-00:00
author: Duncan Doyle, Nadine Spies
excludeSearch: true
---

The kgateway team is happy to announce the release of kgateway v2.5.0! Everything below is new in v2.5, apart from the "Catching up" section. Since we haven't published a release blog for a while, that section covers the features from v2.3 and v2.4 you may have missed.

xDS scoping leads this release. It cuts down what every proxy has to carry in a large cluster. Close behind is HTTP CONNECT egress: `BackendConfigPolicy` can now send outbound traffic through a forward proxy. There are also more breaking changes than usual, one of them a CRD removal, so read that section before you upgrade.

## Highlights

### Scaling the control plane

A lot of the work in v2.5 went into improving control plane performance at scale.

**xDS scoping** changes the configuration that each proxy has to carry. By default, every gateway proxy receives a cluster and its endpoints for every backend the controller discovers, whether or not a route uses it. That default was a deliberate choice. Route and cluster updates reach Envoy independently, so sending every cluster upfront guarantees that the destination is already there and can be referenced in a route. In a Kubernetes cluster with 300 Services where a gateway routes to only 16 of them, every proxy replica still carries all 300 Services in memory, in its config dump, and in its stats. With the xDS `REFERENCED` scoping mode, you can now send a proxy only the clusters its gateway's configuration references, along with those backends' endpoints, listeners and secrets. This setting significantly reduces the size of the config dump, the memory the proxy needs, and the stats it emits. Smaller xDS snapshots are also quicker to push and quicker for a restarting proxy to take in.

To enable this feature, use the `controller.xds.scoping` Helm value as shown in the following example:

```yaml
controller:
  xds:
    scoping:
      # ALL (the default) sends every discovered backend to every proxy.
      # REFERENCED sends only what this gateway's config names.
      mode: REFERENCED
      # A newly referenced cluster is published this long before the route
      # that names it, and a de-referenced one is held this long after.
      referenceAhead: 2s
      dereferenceGrace: 5s
```

The two windows give Envoy time to receive changes in the right order. `referenceAhead` holds back a route that names a new cluster, and `dereferenceGrace` keeps a cluster published for a while after the route update that stops naming it. Raise them if updates are slow to reach your proxies. If the controller cannot tell what a gateway needs, for example when it picks its destination at request time, it falls back to sending that gateway everything.

Scoping is [experimental](https://kgateway.dev/docs/envoy/latest/reference/feature-maturity/) and off by default. To monitor the configuration that proxies receive, you can use the following metrics. Each metric is labeled by gateway and namespace:

- `kgateway_xds_scoping_dropped_clusters`: the most clusters any one of a gateway's proxy groups is withholding.
- `kgateway_xds_scoping_disabled_gateways`: 1 while any of a gateway's proxy groups has reverted to sending everything. Worth an alert, because the fallback is otherwise silent.
- `kgateway_xds_scoping_transitions_total`: how many clusters needed a `referenceAhead` or `dereferenceGrace` window, which tells you whether the windows are sized right.

To learn more about this feature, check out [Scope xDS configuration per gateway](https://kgateway.dev/docs/envoy/latest/install/advanced/#xds-scoping).

**Ordered ADS is now the default.** The snapshot cache has always built responses in dependency order, CDS then EDS then LDS then RDS, but the xDS server did not always preserve that order on the wire. With several responses ready at once, a route update could reach Envoy ahead of the cluster update it referenced, and the proxy would answer with a transient `503 NC`. Ordered ADS sends all types down a single path, so the order the cache produces is the order Envoy sees. Set `KGW_ENABLE_ORDERED_ADS=false` on the control plane to return to the previous behavior.

**The controller now skips stale recomputes** during bursts of route updates and keeps only the latest, instead of rebuilding the same Gateway several times. Config that is identical for every proxy is also built once and shared, and validation results are reused until the cluster changes, so controller memory and CPU grow more slowly as you add proxies.

**The controller can now set its Go memory limit (GOMEMLIMIT)** as a percentage of its container's memory limit, and follows it while the pod runs. This feature is off by default. To turn it on, set the `controller.goMemLimitPercent` Helm value to a value between 1 and 100, with 90 as a good starting point. Use a lower value, such as 80, if a lot of memory is allocated outside the Go runtime or you want extra headroom against out-of-memory kills.

```yaml
controller:
  # Percentage of the container's live cgroup memory limit, refreshed every 30s.
  goMemLimitPercent: 90
```

### Egress through an HTTP CONNECT proxy

Plenty of environments require outbound traffic to leave through a forward proxy, so that egress is filtered, logged and allowlisted in one place. kgateway can now route through one natively. The `BackendConfigPolicy.spec.tunnel` field points a Backend at the forward proxy. When enabled, the gateway proxy sends an HTTP `CONNECT` request to the forward proxy, which opens the connection to the destination.

```yaml
apiVersion: gateway.kgateway.dev/v1alpha1
kind: BackendConfigPolicy
metadata:
  name: via-corp-proxy
spec:
  # tunnel attaches to Backends by targetRefs only, not targetSelectors
  targetRefs:
  - group: gateway.kgateway.dev
    kind: Backend
    name: httpbin
  tunnel:
    proxy:
      backendRef:
        name: squid        # a Service, or another Backend
        port: 3128
    headers:
    # Headers go only to the proxy, never to the destination.
    - name: Proxy-Authorization
      secretRef:
        name: proxy-creds
        key: proxy-authorization   # omit key and the header name is used as the key
```

Proxy credentials can come from a Secret, and kgateway keeps them out of config dumps and error messages. Destination TLS and proxy TLS stay separate, so tunneling does not change how the destination is verified.

A few constraints to plan around. The destination must be a static Backend with exactly one host, the proxy must be a Service or a static Backend, and you cannot tunnel to the proxy itself. `healthCheck`, `tcpKeepalive` and `upstreamProxyProtocol` cannot be set on a tunneled Backend. The [documentation](https://kgateway.dev/docs/envoy/latest/traffic-management/http-connect-tunnels/) walks the whole thing through against a Squid proxy, including reading the `CONNECT` out of the proxy access log.

The other direction is new too. You can now accept `CONNECT` requests at the gateway and terminate them for each route with the [`TrafficPolicy.spec.httpUpgrade`](https://kgateway.dev/docs/envoy/latest/traffic-management/http-upgrades/) setting.

## Breaking changes and removals

There are more of these than usual this cycle, so work through them before you upgrade.

**Kubernetes 1.33 is now the minimum.** We raised it alongside the Gateway API 1.7.0 bump. The [supported versions page](https://kgateway.dev/docs/envoy/latest/reference/versions/) has the full matrix.

**The HTTPListenerPolicy CRD is removed.** Everything it configured now lives under the `spec.default.httpSettings` block on the [ListenerPolicy](https://kgateway.dev/docs/envoy/latest/about/policies/listenerpolicy/) resource, with no field renamed, retyped or dropped. In most cases you change the resource `kind` and re-indent your existing fields:

```yaml
# The same fields, nested under default.httpSettings.
# apiVersion is unchanged; targetRefs and targetSelectors stay where they are.
apiVersion: gateway.kgateway.dev/v1alpha1
kind: ListenerPolicy
metadata:
  name: my-policy
spec:
  targetRefs:
  - group: gateway.networking.k8s.io
    kind: Gateway
    name: my-gateway
  default:
    httpSettings:
      useRemoteAddress: true
      xffNumTrustedHops: 2
      streamIdleTimeout: 30s
```

Migrate before you upgrade. The HTTPListenerPolicy CRD is removed from the `kgateway-crds` chart, so the upgrade deletes any remaining HTTPListenerPolicy resources, including the configuration that they applied. Refer to the [migration guide](https://github.com/kgateway-dev/kgateway/blob/main/docs/guides/migrating-httplistenerpolicy-to-listenerpolicy.md) for the full field mapping and the upgrade ordering.

**kgateway v2.5 is built against Gateway API v1.7.0**, and supports 1.5 and 1.6 as well. Moving to 1.7 is optional. If you do move, apply its CRDs yourself, because they are not part of the kgateway chart.

Note that if you use session persistence in your HTTPRoutes, which is still experimental in Gateway API version 1.7, several fields were renamed. Make sure to update those routes before you apply the new CRDs. The change that is easiest to miss is the cookie lifetime. If you set `absoluteTimeout` and leave `cookie.lifetimeType` unset, the cookie is now a session cookie and the timeout no longer applies. To keep the timeout in effect, set `lifetimeType: Permanent`. See the [session affinity guide](https://kgateway.dev/docs/envoy/latest/traffic-management/session-affinity/) for examples that include the new fields.

**Backends with a [`BackendTLSPolicy`](https://kgateway.dev/docs/envoy/latest/security/backend-tls/) and no `appProtocol` now negotiate HTTP/2 over ALPN.** This one applies whichever Gateway API version you are on, because it comes from kgateway's own translation, not from the CRDs. It fixes backends that only accept HTTP/2 over TLS, gRPC being the common case. Set `appProtocol: http` on the Service to stay on HTTP/1.1.

**Listener stats now tell you which listener they came from.** Every HTTP and HTTPS listener used to share the `stat_prefix: http`, and route prefixes contained dots that split them across metric names, so the numbers were hard to attribute and sometimes hard to query at all. HTTP connection manager and TCP proxy stats now carry a stable per-listener prefix: `http_<port>`, `https_<port>_<listener>`, and `tcp_<port>_<namespace>_<route>` or `tls_<port>_<namespace>_<route>` for TCPRoutes and TLSRoutes. If you use any of these stats in your queries, you will need to update them. Queries matching `envoy_http_conn_manager_prefix="http"` or the old per-route `envoy_tcp_*` names need repointing, as do `GatewayParameters` `stats.matcher` entries matching raw names such as `http.http.`. Aggregations that ignore these labels are unaffected. On the controller side, `kgateway_status_writes_total{kind, result}` replaces the status syncer metrics, and we removed several series that cost real CPU to record on every route of every translation. The [gateway](https://kgateway.dev/docs/envoy/latest/observability/gateway-metrics/) and [control plane](https://kgateway.dev/docs/envoy/latest/observability/control-plane-metrics/) metrics guides list what is published now.

Other highlights:

- **The proxy now drains in 60s with the `immediate` strategy** instead of Envoy's 600s gradual default, releasing the memory held by old listener configuration much sooner. Long-lived connections on a modified listener might now be closed after 60s. Restore the old behavior with `--drain-time-s 600 --drain-strategy gradual` in the `spec.kube.envoyContainer.extraArgs` block of your [`GatewayParameters`](https://kgateway.dev/docs/envoy/latest/setup/customize/envoy/) resource.
- **Changing a listener port no longer restarts the proxy pods**, and listener ports are no longer container ports on the Deployment. Switch any reference to the named ports (`listener-<port>`) to port numbers before upgrading. If you run the proxy with `hostNetwork`, add the ports back with a [`deploymentOverlay`](https://kgateway.dev/docs/envoy/latest/setup/customize/configs/#host-network-ports).
- **Route source metadata changed shape.** The `rule` field now holds the rule name from the originating xRoute when it has one, and a generated value based on the rule's index otherwise. A new `match` field holds the index of the originating match. Update any access log or trace pipeline that parses this metadata. For details, see the [access logging guide](https://kgateway.dev/docs/envoy/latest/security/access-logging/#route-source-metadata).
- **The SDS sidecar binds to `127.0.0.1:8234`** instead of `0.0.0.0:8234`. Set the `SDS_SERVER_ADDRESS` environment variable on the SDS container if you reach it from elsewhere on the cluster network. For details, see the [SDS bind address settings](https://kgateway.dev/docs/envoy/latest/setup/customize/configs/#sds-bind-address).

One deprecated feature is removed: running kgateway as an Istio ambient waypoint, taking the `kgateway-waypoint` GatewayClass, Istio `AuthorizationPolicy` translation and `KGW_WAYPOINT_LOCAL_BINDING` with it. The [waypoint migration guide](https://github.com/kgateway-dev/kgateway/blob/main/docs/guides/migrating-kgateway-waypoints.md) covers the move to Istio waypoints. Sending ingress traffic through an Istio waypoint is still supported, though `KGW_INGRESS_USE_WAYPOINTS` now defaults to `false`.

## Also in v2.5

The [release notes](https://github.com/kgateway-dev/kgateway/releases/tag/v2.5.0) have the full list, and the [API reference](https://kgateway.dev/docs/envoy/latest/reference/api/) covers every field. A few more to call out:

- **[Authentication](https://kgateway.dev/docs/envoy/latest/security/jwt/).** A third JWT validation mode, `AllowMissingOrFailed`, verifies every token and rejects nothing, so a policy can be measured against live traffic before it is enforced. JWT providers also gained a verified-token `cache` and a `clockSkew` tolerance, and OAuth2 discovery now retries in the background, so a provider that was unreachable at startup no longer costs you a control-plane restart.
- **[Experimental: IPv6 and dual-stack](https://kgateway.dev/docs/envoy/latest/setup/customize/configs/#proxy-service-ip-families).** `GatewayParameters.spec.kube.service` takes `ipFamilies` and `ipFamilyPolicy`, and `BackendConfigPolicy.spec.dns.lookupFamily` overrides the DNS lookup family for one backend. One part is not experimental: `KGW_LISTENER_BIND_IPV6` defaults to `true`, so the readiness and stats listeners now bind `[::]` with IPv4 compatibility, and a node with `ipv6.disable=1` needs it set to `false`.
- **Traffic management.** [Session persistence](https://kgateway.dev/docs/envoy/latest/traffic-management/session-affinity/) and [`healthCheck.noTrafficInterval`](https://kgateway.dev/docs/envoy/latest/traffic-management/health-checks/) on `BackendConfigPolicy`, outlier detection on [`consecutiveGatewayFailure`](https://kgateway.dev/docs/envoy/latest/resiliency/outlier-detection/#gateway-failure-outlier-detection), the `kgateway.dev/*` TLS options on `BackendTLSPolicy`, and [shadow mode for global rate limiting](https://kgateway.dev/docs/envoy/latest/security/ratelimit/global/) via `percentEnabled` and `percentEnforced`.
- **Observability.** Per-connection access logging on [TCP and TLS listeners](https://kgateway.dev/docs/envoy/latest/security/access-logging/#tcp-access-log), [`grpcStats`](https://kgateway.dev/docs/envoy/latest/traffic-management/grpc-statistics/) for per-service gRPC metrics, [ext-auth latency](https://kgateway.dev/docs/envoy/latest/security/access-logging/#extauth-latency) through filter state, and a `kgateway_build_info` gauge.
- **Envoy v1.39.6.** The gateway proxy moves up from v1.38.3.

## Catching up: highlights from v2.3 and v2.4

Two traffic management features landed in v2.4, both experimental, which means they can be subject to breaking changes in future releases until they are promoted to GA. We do encourage users to try them out and give us feedback. `BackendConfigPolicy` gained [zone-aware routing](https://kgateway.dev/docs/envoy/latest/traffic-management/zone-routing/) built on Envoy's native prefer-local and force-local support, with the proxy's locality wired into its bootstrap so Envoy can tell which zone an endpoint shares with the gateway instance talking to it. Prefer-local keeps traffic in the local zone while enough healthy endpoints are available there and spills over when they are not. Force-local keeps it local unconditionally. It addresses cross-zone data transfer cost and the latency of leaving an availability zone, which adds up on a busy gateway.

The second is a new [`priorityGroups`](https://kgateway.dev/docs/envoy/latest/traffic-management/destination-types/backends/priority-groups/) Backend type, which turns an ordered list of Backends into Envoy priority levels for active and passive failover:

```yaml
apiVersion: gateway.kgateway.dev/v1alpha1
kind: Backend
metadata:
  name: payments
spec:
  # Groups are tried in order. Traffic moves to the next group only when the
  # endpoints in the preceding groups are unhealthy, and returns automatically
  # once they recover. Up to 16 groups, each with up to 16 backend refs.
  priorityGroups:
  - backendRefs:
    - name: payments-primary
  - backendRefs:
    - name: payments-standby
```

Referenced Backends must live in the same namespace and must not themselves be `priorityGroups` Backends. Failover is driven by health, so pair the Backend with an active health check in `BackendConfigPolicy`, otherwise Envoy has nothing to mark unhealthy and the first group keeps receiving traffic. Priority groups handle active/passive setups: a disaster recovery site, or an old system kept running behind its replacement, that should only see traffic when the primary is unhealthy.

v2.3:

- **[Fault injection](https://kgateway.dev/docs/envoy/latest/resiliency/fault-injection/)** on TrafficPolicy: Delays and HTTP or gRPC aborts for resiliency testing, with a per-route override to turn it off.
- **TLS termination for TLSRoute**, and [per-listener client certificate validation](https://kgateway.dev/docs/envoy/latest/security/mtls-listener/).
- **[Per-route tracing](https://kgateway.dev/docs/envoy/latest/observability/tracing/)** on TrafficPolicy: Sampling overrides, custom attributes, or tracing switched off for one route.
- **GRPCRoute policy attachment**, so TrafficPolicy applies to gRPC routes, and GRPCRoutes can attach to HTTPS listeners.
- **[Data plane overlays](https://kgateway.dev/docs/envoy/latest/setup/customize/envoy/)** in GatewayParameters: A strategic merge patch over the generated Envoy resources, plus PodDisruptionBudget, HPA and VPA support.
- **GCP Backends** for routing to Cloud Run and other Google Cloud services.

## Upgrading

Install or upgrade with the charts:

```bash
helm upgrade -i kgateway-crds oci://cr.kgateway.dev/kgateway-dev/charts/kgateway-crds \
  --version v2.5.0 --namespace kgateway-system --create-namespace
helm upgrade -i kgateway oci://cr.kgateway.dev/kgateway-dev/charts/kgateway \
  --version v2.5.0 --namespace kgateway-system --create-namespace
```

Migrate HTTPListenerPolicy first, and if you are moving to Gateway API v1.7.0, apply its CRDs and migrate route `sessionPersistence` before the chart goes in. The [release notes](https://github.com/kgateway-dev/kgateway/releases/tag/v2.5.0) carry the complete list, and the [documentation](https://kgateway.dev/docs/envoy/latest/) covers every field mentioned here.

## Availability

kgateway v2.5.0 is available for download on [GitHub](https://github.com/kgateway-dev/kgateway). If you are new to the project, the [getting started guide](https://kgateway.dev/docs/envoy/latest/quickstart/) is the quickest way in, and the [labs](https://www.solo.io/resources/lab?product=kgateway) walk through it hands-on.

## Get Involved

The simplest way to get involved with kgateway is to join us on [Slack](https://kgateway.dev/slack/) and at the [community meetings](https://github.com/kgateway-dev/community?tab=readme-ov-file#community-meetings). If you are trying the experimental features, xDS scoping and dual-stack especially, we would love to hear how they work for you. Feedback is what shapes where they go next, and bug reports and use cases are equally welcome on [GitHub](https://github.com/kgateway-dev/kgateway/issues).

## Contributors

This release had 35 contributors. Thank you, all of you.

<div style="display:flex;flex-wrap:wrap;gap:8px;margin-top:1rem;">
<a href="https://github.com/alex1989hu" title="alex1989hu"><img src="https://github.com/alex1989hu.png?size=96" alt="alex1989hu" width="48" height="48" style="display:block;border-radius:50%;" /></a>
<a href="https://github.com/alexliu541" title="alexliu541"><img src="https://github.com/alexliu541.png?size=96" alt="alexliu541" width="48" height="48" style="display:block;border-radius:50%;" /></a>
<a href="https://github.com/andy-fong" title="andy-fong"><img src="https://github.com/andy-fong.png?size=96" alt="andy-fong" width="48" height="48" style="display:block;border-radius:50%;" /></a>
<a href="https://github.com/ayushi-work" title="ayushi-work"><img src="https://github.com/ayushi-work.png?size=96" alt="ayushi-work" width="48" height="48" style="display:block;border-radius:50%;" /></a>
<a href="https://github.com/blacksoxx" title="blacksoxx"><img src="https://github.com/blacksoxx.png?size=96" alt="blacksoxx" width="48" height="48" style="display:block;border-radius:50%;" /></a>
<a href="https://github.com/chandler-solo" title="chandler-solo"><img src="https://github.com/chandler-solo.png?size=96" alt="chandler-solo" width="48" height="48" style="display:block;border-radius:50%;" /></a>
<a href="https://github.com/chris530" title="chris530"><img src="https://github.com/chris530.png?size=96" alt="chris530" width="48" height="48" style="display:block;border-radius:50%;" /></a>
<a href="https://github.com/christianscott" title="christianscott"><img src="https://github.com/christianscott.png?size=96" alt="christianscott" width="48" height="48" style="display:block;border-radius:50%;" /></a>
<a href="https://github.com/CodingRI" title="CodingRI"><img src="https://github.com/CodingRI.png?size=96" alt="CodingRI" width="48" height="48" style="display:block;border-radius:50%;" /></a>
<a href="https://github.com/davidjumani" title="davidjumani"><img src="https://github.com/davidjumani.png?size=96" alt="davidjumani" width="48" height="48" style="display:block;border-radius:50%;" /></a>
<a href="https://github.com/davidxia" title="davidxia"><img src="https://github.com/davidxia.png?size=96" alt="davidxia" width="48" height="48" style="display:block;border-radius:50%;" /></a>
<a href="https://github.com/devennavani" title="devennavani"><img src="https://github.com/devennavani.png?size=96" alt="devennavani" width="48" height="48" style="display:block;border-radius:50%;" /></a>
<a href="https://github.com/DuncanDoyle" title="DuncanDoyle"><img src="https://github.com/DuncanDoyle.png?size=96" alt="DuncanDoyle" width="48" height="48" style="display:block;border-radius:50%;" /></a>
<a href="https://github.com/haoqixu" title="haoqixu"><img src="https://github.com/haoqixu.png?size=96" alt="haoqixu" width="48" height="48" style="display:block;border-radius:50%;" /></a>
<a href="https://github.com/harkirath1511" title="harkirath1511"><img src="https://github.com/harkirath1511.png?size=96" alt="harkirath1511" width="48" height="48" style="display:block;border-radius:50%;" /></a>
<a href="https://github.com/Harsh-2005d" title="Harsh-2005d"><img src="https://github.com/Harsh-2005d.png?size=96" alt="Harsh-2005d" width="48" height="48" style="display:block;border-radius:50%;" /></a>
<a href="https://github.com/JCigan" title="JCigan"><img src="https://github.com/JCigan.png?size=96" alt="JCigan" width="48" height="48" style="display:block;border-radius:50%;" /></a>
<a href="https://github.com/jenshu" title="jenshu"><img src="https://github.com/jenshu.png?size=96" alt="jenshu" width="48" height="48" style="display:block;border-radius:50%;" /></a>
<a href="https://github.com/joerauschenbusch" title="joerauschenbusch"><img src="https://github.com/joerauschenbusch.png?size=96" alt="joerauschenbusch" width="48" height="48" style="display:block;border-radius:50%;" /></a>
<a href="https://github.com/justaparth" title="justaparth"><img src="https://github.com/justaparth.png?size=96" alt="justaparth" width="48" height="48" style="display:block;border-radius:50%;" /></a>
<a href="https://github.com/kamilblaz360" title="kamilblaz360"><img src="https://github.com/kamilblaz360.png?size=96" alt="kamilblaz360" width="48" height="48" style="display:block;border-radius:50%;" /></a>
<a href="https://github.com/kanywst" title="kanywst"><img src="https://github.com/kanywst.png?size=96" alt="kanywst" width="48" height="48" style="display:block;border-radius:50%;" /></a>
<a href="https://github.com/kristin-kronstain-brown" title="kristin-kronstain-brown"><img src="https://github.com/kristin-kronstain-brown.png?size=96" alt="kristin-kronstain-brown" width="48" height="48" style="display:block;border-radius:50%;" /></a>
<a href="https://github.com/marvin-roesch" title="marvin-roesch"><img src="https://github.com/marvin-roesch.png?size=96" alt="marvin-roesch" width="48" height="48" style="display:block;border-radius:50%;" /></a>
<a href="https://github.com/MaxFreedomPollard" title="MaxFreedomPollard"><img src="https://github.com/MaxFreedomPollard.png?size=96" alt="MaxFreedomPollard" width="48" height="48" style="display:block;border-radius:50%;" /></a>
<a href="https://github.com/praneshnikhar" title="praneshnikhar"><img src="https://github.com/praneshnikhar.png?size=96" alt="praneshnikhar" width="48" height="48" style="display:block;border-radius:50%;" /></a>
<a href="https://github.com/puertomontt" title="puertomontt"><img src="https://github.com/puertomontt.png?size=96" alt="puertomontt" width="48" height="48" style="display:block;border-radius:50%;" /></a>
<a href="https://github.com/rishabhsai" title="rishabhsai"><img src="https://github.com/rishabhsai.png?size=96" alt="rishabhsai" width="48" height="48" style="display:block;border-radius:50%;" /></a>
<a href="https://github.com/Roniscend" title="Roniscend"><img src="https://github.com/Roniscend.png?size=96" alt="Roniscend" width="48" height="48" style="display:block;border-radius:50%;" /></a>
<a href="https://github.com/RosieOh" title="RosieOh"><img src="https://github.com/RosieOh.png?size=96" alt="RosieOh" width="48" height="48" style="display:block;border-radius:50%;" /></a>
<a href="https://github.com/saylee21" title="saylee21"><img src="https://github.com/saylee21.png?size=96" alt="saylee21" width="48" height="48" style="display:block;border-radius:50%;" /></a>
<a href="https://github.com/sheidkamp" title="sheidkamp"><img src="https://github.com/sheidkamp.png?size=96" alt="sheidkamp" width="48" height="48" style="display:block;border-radius:50%;" /></a>
<a href="https://github.com/Tazmainiandevil" title="Tazmainiandevil"><img src="https://github.com/Tazmainiandevil.png?size=96" alt="Tazmainiandevil" width="48" height="48" style="display:block;border-radius:50%;" /></a>
<a href="https://github.com/UchihaIthachi" title="UchihaIthachi"><img src="https://github.com/UchihaIthachi.png?size=96" alt="UchihaIthachi" width="48" height="48" style="display:block;border-radius:50%;" /></a>
<a href="https://github.com/ziv-yatzik" title="ziv-yatzik"><img src="https://github.com/ziv-yatzik.png?size=96" alt="ziv-yatzik" width="48" height="48" style="display:block;border-radius:50%;" /></a>
</div>
