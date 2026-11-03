---
title: "kgateway v2.5: Gateway API 1.7, scoped xDS, and CONNECT tunneling"
toc: false
publishDate: 2026-11-03T10:00:00-00:00
author: Duncan Doyle
excludeSearch: true
---

The kgateway team is happy to announce the release of kgateway v2.5.0! Since we haven't published a release blog for a while, this post covers v2.3, v2.4 and v2.5 together. A few of the features below carry an "available since" note rather than being new today.

Two things to check first. **The minimum supported Kubernetes version is now 1.33**, and that one is not optional. The release is built against **Gateway API v1.7.0** and still supports 1.5 and 1.6, so moving to 1.7 is your call. Gateway API CRDs are not part of the kgateway chart, so you apply them yourself. If you do move to 1.7 and you use session persistence in your HTTPRoutes, which is still experimental in Gateway API, there is a migration step.

Let's start with the breaking changes. There are more of them than usual this cycle. One policy CRD, `HTTPListenerPolicy`, is removed, so its resources need migrating before you upgrade. We've cleaned up our stats and metrics, so any dashboards built on them might need an update.

## Breaking changes and removals

**Kubernetes 1.33 is now the minimum**. We raised it alongside the Gateway API 1.7.0 bump.

**The `HTTPListenerPolicy` CRD is removed.** Everything it configured now lives on `ListenerPolicy` under `spec.default.httpSettings`, with no field renamed, retyped or dropped. In most cases you change `kind` and re-indent:

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

Migrate before you upgrade: the CRD is removed from the `kgateway-crds` chart, so the upgrade deletes any remaining `HTTPListenerPolicy` objects and the configuration they were applying along with them. The [migration guide](https://github.com/kgateway-dev/kgateway/blob/main/docs/guides/migrating-httplistenerpolicy-to-listenerpolicy.md) has the full field mapping and the upgrade ordering.

**kgateway v2.5 is built against Gateway API v1.7.0**, and supports 1.5 and 1.6 as well. If you move to 1.7, apply its CRDs yourself: they are not part of the kgateway chart. Route `sessionPersistence` now uses `cookie.name`, `cookie` and `header.name`, and `sessionName` and `cookieConfig` are gone, so migrate those first. With `cookie.lifetimeType` unset the cookie becomes a Session cookie and `absoluteTimeout` stops applying; set `lifetimeType: Permanent` to keep the `Max-Age`.

**Backends with a `BackendTLSPolicy` and no `appProtocol` now negotiate HTTP/2 over ALPN.** This one applies whichever Gateway API version you are on, because it is kgateway's own translation rather than anything in the CRDs. It fixes backends that only accept HTTP/2 over TLS, gRPC being the common case. Set `appProtocol: http` on the Service to stay on HTTP/1.1.

**Listener stats now tell you which listener they came from.** Every HTTP and HTTPS listener used to share `stat_prefix: http`, and route prefixes contained dots that split them across metric names, so the numbers were hard to attribute and sometimes hard to query at all. HTTP connection manager and TCP proxy stats now carry a stable per-listener prefix: `http_<port>`, `https_<port>_<listener>`, and `tcp_<port>_<namespace>_<route>` or `tls_<port>_<namespace>_<route>` for TCPRoutes and TLSRoutes. If you use any of these stats in your queries, you will need to update them. Queries matching `envoy_http_conn_manager_prefix="http"` or the old per-route `envoy_tcp_*` names need repointing, as do `GatewayParameters` `stats.matcher` entries matching raw names such as `http.http.`. Aggregations that ignore these labels are unaffected. On the controller side, `kgateway_status_writes_total{kind, result}` replaces the status syncer metrics, and we removed three series that cost real CPU to record on every route of every translation.

The rest is smaller:

- **The proxy now drains in 60s with the `immediate` strategy** rather than Envoy's 600s gradual default, releasing the memory held by old listener configuration much sooner. Long-lived connections on a modified listener may now be closed after 60s. Restore the old behavior with `--drain-time-s 600 --drain-strategy gradual` in `GatewayParameters` `spec.kube.envoyContainer.extraArgs`.
- **Changing a listener port no longer restarts the proxy pods**, and listener ports are no longer container ports on the Deployment. Switch any reference to the named ports (`listener-<port>`) to port numbers before upgrading. If you run the proxy with `hostNetwork`, add the ports back with a `deploymentOverlay`.
- **Ordered ADS is now the default.** The snapshot cache has always built responses in dependency order, CDS then EDS then LDS then RDS, but the xDS server did not always preserve that order on the wire. With several responses ready at once, a route update could reach Envoy ahead of the cluster update it referenced, and Envoy would briefly hold a valid route pointing at a cluster that had not arrived yet, answering with a transient `503 NC`. Busy streams are common: a backend change updates CDS and EDS together, a route or listener change updates LDS and RDS together, and proxy startup answers every watch from one snapshot. Ordered ADS sends all types down a single path, so the order the cache produces is the order Envoy sees. `KGW_ENABLE_ORDERED_ADS=false` returns to the previous behavior.
- **Route source metadata changed shape.** `rule` now carries the originating xRoute's rule name where it has one, falling back to a generated value reflecting the rule's index, and the match's index is exposed as a new `match` field. Access logs and trace pipelines parsing `io.kgateway.route_source` need updating.
- **The SDS sidecar binds to `127.0.0.1:8234`** rather than `0.0.0.0:8234`. Set `SDS_SERVER_ADDRESS` if you reach it from elsewhere on the cluster network.

One feature is removed: running kgateway as an Istio ambient waypoint, taking the `kgateway-waypoint` GatewayClass, Istio `AuthorizationPolicy` translation and `KGW_WAYPOINT_LOCAL_BINDING` with it. The [waypoint migration guide](https://github.com/kgateway-dev/kgateway/blob/main/docs/guides/migrating-kgateway-waypoints.md) covers the move to Istio waypoints. Sending ingress traffic through an Istio waypoint is still supported, though `KGW_INGRESS_USE_WAYPOINTS` now defaults to `false`.

## Zone-aware routing and priority group failover

Two traffic management features landed in v2.4, both experimental, which means they can be subject to breaking changes in future releases until they are promoted to GA. We do encourage users to try out these new features and give us feedback. `BackendConfigPolicy` gained zone-aware routing built on Envoy's native prefer-local and force-local support, with the proxy's locality wired into its bootstrap so Envoy can tell which zone an endpoint shares with the gateway instance talking to it. Prefer-local keeps traffic in the local zone while enough healthy endpoints are available there and spills over when they are not. Force-local keeps it local unconditionally.

The second is a new `priorityGroups` Backend type, which turns an ordered list of Backends into Envoy priority levels for active and passive failover:

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

Referenced Backends must live in the same namespace and must not themselves be `priorityGroups` Backends. Failover is driven by health, so pair the Backend with an active health check in `BackendConfigPolicy`, otherwise Envoy has nothing to mark unhealthy and the first group keeps receiving traffic.

Both are aimed at the same thing: keeping traffic close, and keeping it flowing when something fails. Zone-aware routing addresses cross-zone data transfer cost and the latency of leaving an availability zone, which on a busy gateway adds up on both counts. Priority groups handle active/passive setups: a disaster recovery site, or an old system kept running behind its replacement, that should only see traffic when the primary is unhealthy.

## Scaling the control plane

Most of this release went into what the control plane does at scale, and two changes stand out.

**xDS scoping** changes what each proxy has to carry. By default every gateway proxy receives a cluster for every backend the controller discovers, and that default is deliberate. Route and cluster updates reach Envoy independently, so when a route changes destination, say `/foo` moving from `service-a` to `service-b`, a proxy that learns the new route before the new cluster drops requests in the gap. Publishing every cluster up front means the destination is always already there, which is the behavior you want on a gateway carrying business-critical traffic. The cost is that a Kubernetes cluster with thousands of Services has every proxy holding all of them in memory, in its config dump and in its per-cluster stats, even when that gateway routes to a dozen. The new `REFERENCED` mode sends a proxy only the clusters its gateway's configuration references, together with those backends' endpoints, listeners and secrets, and is designed to keep that guarantee:

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

The saving scales with how little of the cluster a gateway actually uses. A gateway that routes to 16 Services in a cluster of 300 carries 16 clusters instead of 300: in the memory of every one of its proxy replicas, in its config dump, and in its `/stats`, where each cluster contributes a whole family of series. Smaller snapshots are also less to push, and less for a restarting proxy to take in.

Three things are meant to keep it as safe as the default. A cluster a route is about to need is sent before that route, and one nothing references any more is kept for a while afterwards, so the two changes do not cross. When the controller is unsure whether a cluster is needed it keeps it, because one cluster nobody uses costs a little memory while a missing one is an outage. And a gateway that picks its destination at request time, where there is no way to know up front what it will need, keeps receiving everything. Both of those windows are timers, so give them room if updates are slow to reach your proxies.

It is experimental and off by default. Three metrics report what it is doing, each labelled by gateway and namespace. `kgateway_xds_scoping_dropped_clusters` is the most clusters any one of a gateway's proxy groups is withholding. `kgateway_xds_scoping_disabled_gateways` is 1 while any of them has reverted to sending everything, and is worth an alert, because the fallback is otherwise silent. `kgateway_xds_scoping_transitions_total` counts the clusters whose change needed a window, which is how you tell whether the windows are sized right.

**Redundant Gateway rebuilds are now skipped during route churn.** When a burst of input events queues several recomputes for the same key, KRT skips any whose change a later recomputation has already taken in, so a burst of route updates no longer rebuilds the same Gateway several times over. The same dependency bump also shrinks KRT's maps after a large de-allocation, so memory freed at scale is returned rather than held.

Underneath both, the controller does less work per connected proxy. Config that is identical for every proxy is now built once and shared instead of being rebuilt for each one, and validation results are reused when the cluster has not changed. The practical effect is that the controller's memory and CPU grow far more slowly as you add proxies. A hashing fix also stops backends with more than one label from publishing a new endpoint version on every recomputation, which was pushing updates to every connected proxy when nothing had actually changed.

Finally, `controller.goMemLimitPercent` keeps the Go runtime's memory at a percentage of the controller container's memory limit, and follows that limit while the pod runs, so an in-place resize is picked up instead of being ignored until the next restart. It is `0` by default, which keeps reading the limit once at startup. Set it to a value between 1 and 100 to turn it on, with 90 a good starting point:

```yaml
controller:
  # Percentage of the container's live cgroup memory limit, refreshed every 30s.
  # Lower it if a lot of memory is allocated outside the Go runtime.
  goMemLimitPercent: 90
```

Envoy moves to v1.39.6.

## Egress through an HTTP CONNECT proxy

Plenty of environments require outbound traffic to leave through a forward proxy. Gloo Gateway has supported this for years, and for teams that depend on it the absence of an equivalent in kgateway was enough to hold up a migration. That gap is closed. `BackendConfigPolicy.spec.tunnel` points a Backend at the proxy: the gateway sends `CONNECT` to it, and the proxy opens the connection to the destination.

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

Credentials belong in a Secret, and kgateway redacts them from xDS snapshots, KRT dumps, policy diagnostics and validation errors rather than echoing them back in a config dump. Destination TLS and proxy TLS stay separate, so tunneling does not change how the destination is verified.

The constraints are worth knowing before you plan around it. The destination must be a static Backend with exactly one host, the proxy must be a Service or a static Backend, and you cannot tunnel to the proxy itself. `healthCheck`, `tcpKeepalive` and `upstreamProxyProtocol` cannot be set on a tunneled Backend. The [documentation](https://kgateway.dev/docs/envoy/latest/traffic-management/http-connect-tunnels/) walks the whole thing through against a Squid proxy, including reading the `CONNECT` out of the proxy access log.

The other direction is new too: accepting `CONNECT` at the gateway and terminating it, configured per route with `TrafficPolicy.spec.httpUpgrade` and `connect.terminate: true`.

## Also in this release

The [release notes](https://github.com/kgateway-dev/kgateway/releases/tag/v2.5.0) have the full list. The items most likely to matter to you:

- **Authentication.** A third JWT validation mode, `AllowMissingOrFailed`, verifies every token and rejects nothing, so a policy can be measured against live traffic before it is enforced. JWT providers also gained a verified-token `cache` and a `clockSkew` tolerance, and OAuth2 discovery now retries in the background rather than waiting for a control-plane restart when the provider was unreachable at startup.
- **Experimental: IPv6 and dual-stack.** `GatewayParameters.spec.kube.service` takes `ipFamilies` and `ipFamilyPolicy`, and `BackendConfigPolicy.spec.dns.lookupFamily` overrides the DNS lookup family for one backend. One part is not experimental: `KGW_LISTENER_BIND_IPV6` defaults to `true`, so the readiness and stats listeners now bind `[::]` with IPv4 compatibility, and a node with `ipv6.disable=1` needs it set to `false`.
- **Traffic management.** Session persistence and `healthCheck.noTrafficInterval` on `BackendConfigPolicy`, outlier detection on `consecutiveGatewayFailure`, the `kgateway.dev/*` TLS options on `BackendTLSPolicy`, and shadow mode for global rate limiting via `percentEnabled` and `percentEnforced`.
- **Observability.** Per-connection access logging on TCP and TLS listeners, `grpcStats` for per-service gRPC metrics, ext-auth latency through filter state, and a `kgateway_build_info` gauge.

## Upgrading

Install or upgrade with the charts:

```bash
helm upgrade -i kgateway-crds oci://cr.kgateway.dev/kgateway-dev/charts/kgateway-crds \
  --version v2.5.0 --namespace kgateway-system --create-namespace
helm upgrade -i kgateway oci://cr.kgateway.dev/kgateway-dev/charts/kgateway \
  --version v2.5.0 --namespace kgateway-system --create-namespace
```

Migrate `HTTPListenerPolicy` first, and if you are moving to Gateway API v1.7.0, apply its CRDs and migrate route `sessionPersistence` before the chart goes in. The [release notes](https://github.com/kgateway-dev/kgateway/releases/tag/v2.5.0) carry the complete list, and the [documentation](https://kgateway.dev/docs/envoy/latest/) covers every field mentioned here.

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
