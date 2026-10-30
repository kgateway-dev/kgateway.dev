By default, {{< reuse "/kgw-docs/snippets/kgateway.md" >}} exposes metrics in Prometheus format for the data plane of each gateway proxy. You can use these metrics to monitor the health and performance of your gateway environment.

## View default data plane metrics in Prometheus {#prometheus-metrics}

The following steps show you how to quickly view the metrics endpoint of the gateway proxy deployment.{{< version exclude-if="2.0.x" >}} To integrate the Prometheus metrics into your observability stack, see the [OpenTelemetry guide]({{< link-hextra path="/observability/otel-stack/" >}}).{{< /version >}}

1. Port-forward the gateway deployment on port 19000.
   
   ```sh
   kubectl -n {{< reuse "kgw-docs/snippets/namespace.md" >}} port-forward deployment/http 19000
   ```

2. Access the gateway metrics by reviewing the [Prometheus statistics `/stats/prometheus` endpoint](http://localhost:19000/stats/prometheus).

   Example output:

   ```console
   # TYPE envoy_cluster_external_upstream_rq counter
   envoy_cluster_external_upstream_rq{envoy_response_code="200",envoy_cluster_name="kube_httpbin_httpbin_8000"} 5
   ```

{{< version exclude-if="2.0.x,2.1.x,2.2.x,2.3.x,2.4.x" >}}
## Per-listener metrics {#listener-metrics}

The gateway proxy reports the HTTP connection manager and TCP proxy stats for each listener separately. Envoy names these stats with a stat prefix that {{< reuse "kgw-docs/snippets/kgateway.md" >}} sets for each listener. In Prometheus, the stat prefix is the value of the `envoy_http_conn_manager_prefix` label for HTTP and HTTPS listeners, and of the `envoy_tcp_prefix` label for TCPRoutes and TLSRoutes. In the Envoy admin stats, it is part of the stat name, such as `http.http_8080.downstream_rq_total` or `tcp.tcp_8000_<namespace>_<route>.downstream_cx_total`. In earlier versions, all HTTP and HTTPS listeners shared the stat prefix `http`.

The stat prefix has the following format.

| Listener | Stat prefix |
| -- | -- |
| HTTP | `http_<port>` |
| HTTPS | `https_<port>_<listener>` |
| HTTPS listener of a ListenerSet | `https_<port>_<namespace>_<listenerset>_<listener>` |
| TCPRoute | `tcp_<port>_<namespace>_<route>` |
| TLSRoute | `tls_<port>_<namespace>_<route>` |

For example, a Gateway with an HTTP listener on port 8080 and an HTTPS listener named `tenant-a` on port 8443 reports the stat prefixes `http_8080` and `https_8443_tenant-a`.

Use the stat prefix to query the metrics of a single listener, or of all listeners.

```
# Requests of the tenant-a listener only
sum(rate(envoy_http_downstream_rq_total{envoy_http_conn_manager_prefix="https_8443_tenant-a"}[5m]))

# Requests of all HTTP and HTTPS listeners
sum(rate(envoy_http_downstream_rq_total{envoy_http_conn_manager_prefix=~"http_.*|https_.*"}[5m]))

# Connections of a TCPRoute
sum(rate(envoy_tcp_downstream_cx_total{envoy_tcp_prefix="tcp_8000_<namespace>_<route>"}[5m]))
```

Update the Prometheus queries and dashboards that filter on the earlier prefix, such as `envoy_http_conn_manager_prefix="http"`. These queries no longer return data.

To reduce the stats that the proxy tracks to the stats of one listener, use a stats matcher, such as `prefix: "http.https_8443_tenant-a."`. For more information, see [Filter Envoy stats](#filter-stats). A stats matcher that uses the earlier prefix, such as `prefix: "http.http."`, no longer matches any stats. Use the prefix of each listener instead, such as `http.http_8080.`.

A Gateway with many HTTPS listeners or ListenerSets exposes more HTTP connection manager series, one set for each listener.

{{< /version >}}

## Filter stats at query time {#filter-query-time}

By default, {{< reuse "kgw-docs/snippets/kgateway.md" >}} configures the stats endpoint at `/stats/prometheus?usedonly`. The `?usedonly` query parameter tells Envoy to omit stats with default (zero) values when responding to a Prometheus scrape request. This reduces the size of each scrape response without affecting what Envoy tracks internally.

You can customize this path with the `spec.kube.stats.routePrefixRewrite` field in the {{< reuse "kgw-docs/snippets/gatewayparameters.md" >}} resource.

| Value | Behavior |
| -- | -- |
| `/stats/prometheus?usedonly` | Return only stats with non-zero values (default). |
| `/stats/prometheus` | Return all stats, including zero-valued ones. |

The following example sets a custom `routePrefixRewrite` value on a {{< reuse "kgw-docs/snippets/gatewayparameters.md" >}} resource.

```yaml
kubectl apply -f- <<EOF
apiVersion: {{< reuse "kgw-docs/snippets/gatewayparam-apiversion.md" >}}
kind: {{< reuse "kgw-docs/snippets/gatewayparameters.md" >}}
metadata:
  name: gwp-stats-filter
  namespace: {{< reuse "kgw-docs/snippets/namespace.md" >}}
spec:
  kube:
    stats:
      enabled: true
      routePrefixRewrite: "/stats/prometheus?usedonly"
EOF
```

> [!NOTE]
> Query-time filtering reduces the amount of stats that are scraped when a Prometheus scrape query is received. However, Envoy still tracks all stats in memory. To reduce memory and CPU overhead on the gateway proxy itself, use the `matcher` field instead. For more information, see [Filter Envoy stats](#filter-stats).

## Filter Envoy stats {#filter-stats}

In high-scale environments, Envoy can emit thousands of individual stats. You can use the `spec.kube.stats.matcher` field in the {{< reuse "kgw-docs/snippets/gatewayparameters.md" >}} resource to control which stats Envoy emits at the source to reduce memory and CPU overhead on the gateway proxy.

> [!NOTE]
> Stats filtering applies at bootstrap time in the Envoy proxy. This is different from [query-time filtering](#filter-query-time) using `routePrefixRewrite`, which only reduces scrape response size but still tracks all stats in memory.

You can configure either an inclusion list (emit only matching stats) or an exclusion list (emit all stats except matching ones). Only one list can be set at a time, and each list supports up to 16 entries.

Each entry uses a `StringMatcher` with exactly one of the following match types:

| Field | Description |
| -- | -- |
| `exact` | The stat name must match the value exactly. |
| `prefix` | The stat name must begin with the value. |
| `suffix` | The stat name must end with the value. |
| `contains` | The stat name must contain the value as a substring. |
| `safeRegex` | The stat name must match a [Google RE2 regular expression](https://github.com/google/re2/wiki/Syntax). |

Set `ignoreCase: true` on any entry to make the match case-insensitive. This flag has no effect on `safeRegex` matches.

**Inclusion list**

The following example configures a {{< reuse "kgw-docs/snippets/gatewayparameters.md" >}} resource to emit only stats that match the inclusion list, then attaches it to a Gateway.

```yaml
kubectl apply -f- <<EOF
apiVersion: {{< reuse "kgw-docs/snippets/gatewayparam-apiversion.md" >}}
kind: {{< reuse "kgw-docs/snippets/gatewayparameters.md" >}}
metadata:
  name: gwp-stats-filter
  namespace: {{< reuse "kgw-docs/snippets/namespace.md" >}}
spec:
  kube:
    stats:
      enabled: true
      matcher:
        inclusionList:
          - prefix: "http."
          - suffix: ".rq_total"
          - safeRegex: "^cluster\\..*\\.upstream_cx_active$"
---
apiVersion: gateway.networking.k8s.io/v1
kind: Gateway
metadata:
  name: http
  namespace: {{< reuse "kgw-docs/snippets/namespace.md" >}}
spec:
  gatewayClassName: {{< reuse "kgw-docs/snippets/gatewayclass.md" >}}
  infrastructure:
    parametersRef:
      group: {{< reuse "kgw-docs/snippets/gatewayparam-group.md" >}}
      kind: {{< reuse "kgw-docs/snippets/gatewayparameters.md" >}}
      name: gwp-stats-filter
  listeners:
    - protocol: HTTP
      port: 8080
      name: http
      allowedRoutes:
        namespaces:
          from: All
EOF
```

The stats matcher is part of the bootstrap configuration of the gateway proxy, which the proxy reads only when it starts. Restart the gateway proxy to apply the matcher.

```sh
kubectl rollout restart deployment/http -n {{< reuse "kgw-docs/snippets/namespace.md" >}}
kubectl rollout status deployment/http -n {{< reuse "kgw-docs/snippets/namespace.md" >}}
```

**Exclusion list**

The following example suppresses a specific set of stats while allowing all others through.

```yaml
kubectl apply -f- <<EOF
apiVersion: {{< reuse "kgw-docs/snippets/gatewayparam-apiversion.md" >}}
kind: {{< reuse "kgw-docs/snippets/gatewayparameters.md" >}}
metadata:
  name: gwp-stats-filter
  namespace: {{< reuse "kgw-docs/snippets/namespace.md" >}}
spec:
  kube:
    stats:
      enabled: true
      matcher:
        exclusionList:
          - prefix: "server."
          - suffix: ".min_heating_duration_us"
          - exact: "http.async-client.no_cluster"
---
apiVersion: gateway.networking.k8s.io/v1
kind: Gateway
metadata:
  name: http
  namespace: {{< reuse "kgw-docs/snippets/namespace.md" >}}
spec:
  gatewayClassName: {{< reuse "kgw-docs/snippets/gatewayclass.md" >}}
  infrastructure:
    parametersRef:
      group: {{< reuse "kgw-docs/snippets/gatewayparam-group.md" >}}
      kind: {{< reuse "kgw-docs/snippets/gatewayparameters.md" >}}
      name: gwp-stats-filter
  listeners:
    - protocol: HTTP
      port: 8080
      name: http
      allowedRoutes:
        namespaces:
          from: All
EOF
```

The stats matcher is part of the bootstrap configuration of the gateway proxy, which the proxy reads only when it starts. Restart the gateway proxy to apply the matcher.

```sh
kubectl rollout restart deployment/http -n {{< reuse "kgw-docs/snippets/namespace.md" >}}
kubectl rollout status deployment/http -n {{< reuse "kgw-docs/snippets/namespace.md" >}}
```

{{< version exclude-if="2.0.x,2.1.x,2.2.x,2.3.x" >}}

## Per-route statistics {#per-route-stats}

By default, Envoy groups route-level metrics under a shared virtual host label, making it hard to isolate traffic for a specific route. Use the `statPrefix` field in a {{< reuse "kgw-docs/snippets/trafficpolicy.md" >}} to set a per-route stat prefix so that Envoy emits metrics under a distinct label:

```
vhost.<vhost_name>.route.<statPrefix>.*
```

The `statPrefix` value supports the following template variables that {{< reuse "kgw-docs/snippets/kgateway.md" >}} resolves at translation time from the targeted route's metadata:

| Variable | Description |
|---|---|
| `{{route_name}}` | The name of the HTTPRoute or GRPCRoute resource. |
| `{{route_namespace}}` | The namespace of the HTTPRoute or GRPCRoute resource. |
| `{{rule_name}}` | The name of the matched route rule. Empty segments from unnamed rules are dropped automatically. |

The field is only honored for **HTTPRoute** and **GRPCRoute** targets. Setting it on any other target type is rejected at admission.

The following example sets a stat prefix that includes the route namespace, name, and rule name.

```yaml
kubectl apply -f- <<EOF
apiVersion: {{< reuse "kgw-docs/snippets/trafficpolicy-apiversion.md" >}}
kind: {{< reuse "kgw-docs/snippets/trafficpolicy.md" >}}
metadata:
  name: httpbin-stat-prefix
  namespace: httpbin
spec:
  targetRefs:
  - group: gateway.networking.k8s.io
    kind: HTTPRoute
    name: httpbin
  statPrefix: "{{route_namespace}}.{{route_name}}.{{rule_name}}"
EOF
```

| Setting | Description |
|---|---|
| `spec.targetRefs` | The HTTPRoute or GRPCRoute to apply this policy to. |
| `spec.statPrefix` | The stat prefix to set on the Envoy route. Supports `{{route_name}}`, `{{route_namespace}}`, and `{{rule_name}}` template variables. Maximum length is 256 characters. |

## Disable stats {#disable-stats}

To disable the Prometheus scrape endpoint on the gateway proxy, set `spec.kube.stats.enabled: false` in a {{< reuse "kgw-docs/snippets/gatewayparameters.md" >}} resource and attach it to your Gateway. When disabled, the dedicated Prometheus listener on port 9091 is removed from the Envoy bootstrap config and Prometheus scrape annotations are not added to the proxy pod. Envoy continues to collect stats internally, and they remain accessible via the Envoy admin interface on port 19000.

```yaml
kubectl apply -f- <<EOF
apiVersion: {{< reuse "kgw-docs/snippets/gatewayparam-apiversion.md" >}}
kind: {{< reuse "kgw-docs/snippets/gatewayparameters.md" >}}
metadata:
  name: gwp-stats-disabled
  namespace: {{< reuse "kgw-docs/snippets/namespace.md" >}}
spec:
  kube:
    stats:
      enabled: false
---
apiVersion: gateway.networking.k8s.io/v1
kind: Gateway
metadata:
  name: http
  namespace: {{< reuse "kgw-docs/snippets/namespace.md" >}}
spec:
  gatewayClassName: kgateway
  infrastructure:
    parametersRef:
      group: {{< reuse "kgw-docs/snippets/gatewayparam-group.md" >}}
      kind: {{< reuse "kgw-docs/snippets/gatewayparameters.md" >}}
      name: gwp-stats-disabled
  listeners:
    - protocol: HTTP
      port: 8080
      name: http
      allowedRoutes:
        namespaces:
          from: All
EOF
```



{{< /version >}}

## Gateway proxy metrics reference {#reference}

For more details about the collected metrics, see the [Envoy statistics reference docs](https://www.envoyproxy.io/docs/envoy/latest/operations/stats_overview).
