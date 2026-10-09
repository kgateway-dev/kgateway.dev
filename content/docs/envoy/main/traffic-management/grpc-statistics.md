---
title: gRPC statistics
description: Collect per-service and per-method gRPC metrics from Gateway listeners.
weight: 15
---

Use the `grpcStats` field on a ListenerPolicy resource to add Envoy's `grpc_stats` HTTP filter to the listeners on a Gateway. The filter records per-service and per-method gRPC metrics, including the gRPC status code that is not visible in ordinary HTTP response-code metrics.

## Before you begin {#before-you-begin}

Follow the [gRPC routing guide]({{< link-hextra path="/traffic-management/grpc/" >}}) to set up the `grpc` Gateway, the sample `yages.Echo` service, and the `grpcurl-client` pod. The steps in this guide reuse that setup to generate the gRPC traffic that the `grpc_stats` filter counts.

## Show statistics for all methods {#all-methods}

Set `statsForAllMethods` to `true` to emit per-method statistics for every gRPC method that the listener sees. This option is useful for trusted services with a known, bounded set of method names. If client-supplied method names might create too many metric series, use an allow list instead so that you [show statistics for specific methods](#specific-methods).

1. Create a ListenerPolicy that enables the `grpcStats` filter on the Gateway for all gRPC methods.

   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.kgateway.dev/v1alpha1
   kind: ListenerPolicy
   metadata:
     name: grpc-stats
     namespace: {{< reuse "kgw-docs/snippets/namespace.md" >}}
   spec:
     targetRefs:
     - group: gateway.networking.k8s.io
       kind: Gateway
       name: grpc
     default:
       httpSettings:
         grpcStats:
           statsForAllMethods: true
           enableUpstreamStats: true
   EOF
   ```

   | Field | Description |
   | --- | --- |
   | `spec.targetRefs` | The Gateway to apply this listener policy to. |
   | `spec.default.httpSettings.grpcStats` | Adds Envoy's `grpc_stats` HTTP filter to the listener filter chain. Omit this block to leave the filter disabled. An empty block is rejected. |
   | `statsForAllMethods` | Set to `true` to emit per-method statistics for every gRPC method that the listener sees. Do not set this field together with `methodAllowlist`. |
   | `enableUpstreamStats` | Optional. Emits a histogram for the upstream wire latency of each request. |


2. Port-forward the gateway proxy admin port.

   ```sh
   kubectl port-forward deployment/grpc -n {{< reuse "kgw-docs/snippets/namespace.md" >}} 19000
   ```

3. Verify that the Envoy configuration includes the `grpc_stats` filter before the router filter.

   ```sh
   curl -s 127.0.0.1:19000/config_dump | \
   jq '.configs[]
     | select(.["@type"] == "type.googleapis.com/envoy.admin.v3.ListenersConfigDump")
     | .dynamic_listeners[].active_state.listener.filter_chains[].filters[].typed_config.http_filters'
   ```

   Example output:

   ```json
   [
     {
       "name": "envoy.filters.http.grpc_stats",
       "typed_config": {
         "@type": "type.googleapis.com/envoy.extensions.filters.http.grpc_stats.v3.FilterConfig",
         "enable_upstream_stats": true,
         "stats_for_all_methods": true
       }
     },
     {
       "name": "envoy.filters.http.router",
       "typed_config": {
         "@type": "type.googleapis.com/envoy.extensions.filters.http.router.v3.Router"
       }
     }
   ]
   ```

4. Send a gRPC request through the Gateway. The `-vv` flag makes `grpcurl` issue a `ServerReflectionInfo` call first to resolve the method signature, so you see stats for both calls.

   ```sh
   kubectl exec -n {{< reuse "kgw-docs/snippets/namespace.md" >}} grpcurl-client -c grpcurl -- \
     grpcurl -plaintext -authority grpc.com -vv grpc:80 yages.Echo/Ping
   ```

5. Query the admin stats endpoint for the per-method `grpc.` stats. Scope the search to the backend's cluster so that you don't also match the kgateway control plane's own `cluster.grpc.<namespace>` cluster, which happens to contain the same `.grpc.` substring.

   ```sh
   curl -s 127.0.0.1:19000/stats | grep '^cluster\.kube_.*\.grpc\.'
   ```

   Example output. The `kube_<namespace>_<service>_<port>` cluster name prefix depends on your backend.

   ```console
   cluster.kube_kgateway-system_grpc-echo-svc_3000.grpc.grpc.reflection.v1alpha.ServerReflection.ServerReflectionInfo.0: 1
   cluster.kube_kgateway-system_grpc-echo-svc_3000.grpc.grpc.reflection.v1alpha.ServerReflection.ServerReflectionInfo.request_message_count: 1
   cluster.kube_kgateway-system_grpc-echo-svc_3000.grpc.grpc.reflection.v1alpha.ServerReflection.ServerReflectionInfo.response_message_count: 1
   cluster.kube_kgateway-system_grpc-echo-svc_3000.grpc.grpc.reflection.v1alpha.ServerReflection.ServerReflectionInfo.success: 1
   cluster.kube_kgateway-system_grpc-echo-svc_3000.grpc.grpc.reflection.v1alpha.ServerReflection.ServerReflectionInfo.total: 1
   cluster.kube_kgateway-system_grpc-echo-svc_3000.grpc.yages.Echo.Ping.0: 1
   cluster.kube_kgateway-system_grpc-echo-svc_3000.grpc.yages.Echo.Ping.request_message_count: 1
   cluster.kube_kgateway-system_grpc-echo-svc_3000.grpc.yages.Echo.Ping.response_message_count: 1
   cluster.kube_kgateway-system_grpc-echo-svc_3000.grpc.yages.Echo.Ping.success: 1
   cluster.kube_kgateway-system_grpc-echo-svc_3000.grpc.yages.Echo.Ping.total: 1
   cluster.kube_kgateway-system_grpc-echo-svc_3000.grpc.yages.Echo.Ping.upstream_rq_time: P0(nan,0) P25(nan,0) P50(nan,0) P75(nan,0) P90(nan,0) P95(nan,0) P99(nan,0) P99.5(nan,0) P99.9(nan,0) P100(nan,0)
   ```

   | Stat | Description |
   | ---- | ----------- |
   | `<status-code>` (for example `.0`) | Counter for calls to this method that returned the given gRPC status code. `0` is `OK`. |
   | `success` | Number of calls to this method that completed with a gRPC status that indicates success. |
   | `failure` | Number of calls to this method that completed with a gRPC status that indicates failure. Envoy only creates a counter the first time it is incremented, so `failure` doesn't appear until at least one call fails. |
   | `total` | Total number of calls to this method, equal to `success` plus `failure`. |
   | `request_message_count` / `response_message_count` | Number of request or response messages sent for this method. |
   | `upstream_rq_time` | Histogram of the upstream wire latency for calls to this method. Only emitted when `enableUpstreamStats` is `true`. |

## Show statistics for specific methods {#specific-methods}

Set `methodAllowlist` to record per-method statistics for only the gRPC methods that you specify. Use this option instead of `statsForAllMethods` when client-supplied method names might otherwise create too many metric series.

1. Create a ListenerPolicy that enables the `grpcStats` filter on the Gateway. Set the `methodAllowlist` field to the methods that you want to track.

   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.kgateway.dev/v1alpha1
   kind: ListenerPolicy
   metadata:
     name: grpc-stats
     namespace: {{< reuse "kgw-docs/snippets/namespace.md" >}}
   spec:
     targetRefs:
     - group: gateway.networking.k8s.io
       kind: Gateway
       name: grpc
     default:
       httpSettings:
         grpcStats:
           methodAllowlist:
           - /yages.Echo/Ping
   EOF
   ```

   | Field | Description |
   | --- | --- |
   | `spec.targetRefs` | The Gateway to apply this listener policy to. |
   | `spec.default.httpSettings.grpcStats` | Adds Envoy's `grpc_stats` HTTP filter to the listener filter chain. Omit this block to leave the filter disabled. An empty block is rejected. |
   | `methodAllowlist` | Fully qualified gRPC methods to record, in the `/package.Service/Method` format. The list must contain 1-128 methods. Do not set this field together with `statsForAllMethods`. |


2. Port-forward the gateway proxy admin port.

   ```sh
   kubectl port-forward deployment/grpc -n {{< reuse "kgw-docs/snippets/namespace.md" >}} 19000
   ```

3. Verify that the Envoy configuration includes the `grpc_stats` filter before the router filter.

   ```sh
   curl -s 127.0.0.1:19000/config_dump | \
   jq '.configs[]
     | select(.["@type"] == "type.googleapis.com/envoy.admin.v3.ListenersConfigDump")
     | .dynamic_listeners[].active_state.listener.filter_chains[].filters[].typed_config.http_filters'
   ```

   Example output:

   ```json
   [
     {
       "name": "envoy.filters.http.grpc_stats",
       "typed_config": {
         "@type": "type.googleapis.com/envoy.extensions.filters.http.grpc_stats.v3.FilterConfig",
         "individual_method_stats_allowlist": {
           "services": [
             {
               "service_name": "yages.Echo",
               "method_names": ["Ping"]
             }
           ]
         }
       }
     },
     {
       "name": "envoy.filters.http.router",
       "typed_config": {
         "@type": "type.googleapis.com/envoy.extensions.filters.http.router.v3.Router"
       }
     }
   ]
   ```

4. Call the allow-listed method and a different method that is not on the allow list. `grpcurl`'s `list` subcommand calls the gRPC reflection service, which is a different method (`ServerReflectionInfo`) than the one you allowed in the `methodAllowlist` field.

   ```sh
   kubectl exec -n {{< reuse "kgw-docs/snippets/namespace.md" >}} grpcurl-client -c grpcurl -- \
     grpcurl -plaintext -authority grpc.com -vv grpc:80 yages.Echo/Ping

   kubectl exec -n {{< reuse "kgw-docs/snippets/namespace.md" >}} grpcurl-client -c grpcurl -- \
     grpcurl -plaintext -authority grpc.com -vv grpc:80 list
   ```

5. Query the admin stats endpoint for the per-method `grpc.` stats. Verify that you see stats for the `yages.Echo.Ping` method by name. The `ServerReflectionInfo` call still counts toward the cluster's aggregate `grpc.*` stats, but doesn't get its own `grpc.<service>.<method>.*` breakdown because it isn't listed in the `methodAllowlist` field.

   ```sh
   curl -s 127.0.0.1:19000/stats | grep '^cluster\.kube_.*\.grpc\.'
   ```

   Example output:

   ```console
   cluster.kube_kgateway-system_grpc-echo-svc_3000.grpc.0: 2
   cluster.kube_kgateway-system_grpc-echo-svc_3000.grpc.request_message_count: 2
   cluster.kube_kgateway-system_grpc-echo-svc_3000.grpc.response_message_count: 2
   cluster.kube_kgateway-system_grpc-echo-svc_3000.grpc.success: 2
   cluster.kube_kgateway-system_grpc-echo-svc_3000.grpc.total: 2
   cluster.kube_kgateway-system_grpc-echo-svc_3000.grpc.yages.Echo.Ping.0: 1
   cluster.kube_kgateway-system_grpc-echo-svc_3000.grpc.yages.Echo.Ping.request_message_count: 1
   cluster.kube_kgateway-system_grpc-echo-svc_3000.grpc.yages.Echo.Ping.response_message_count: 1
   cluster.kube_kgateway-system_grpc-echo-svc_3000.grpc.yages.Echo.Ping.success: 1
   cluster.kube_kgateway-system_grpc-echo-svc_3000.grpc.yages.Echo.Ping.total: 1
   ```

   | Stat | Description |
   | ---- | ----------- |
   | `grpc.<stat>` (no service or method in the name) | Aggregate count across every gRPC call on this cluster, including calls to methods that aren't in `methodAllowlist`, such as `ServerReflectionInfo` here. |
   | `grpc.<service>.<method>.<status-code>` (for example `.0`) | Counter for calls to this method that returned the given gRPC status code. `0` is `OK`. |
   | `success` | Number of calls that completed with a gRPC status that indicates success. |
   | `failure` | Number of calls that completed with a gRPC status that indicates failure. Envoy only creates a counter the first time it is incremented, so `failure` doesn't appear until at least one call fails. |
   | `total` | Total number of calls, equal to `success` plus `failure`. |
   | `request_message_count` / `response_message_count` | Number of request or response messages sent. |

   > [!TIP]
   > Envoy never clears a stat that it already created, even after you change the ListenerPolicy. If you completed [Show statistics for all methods](#all-methods) against the same Gateway, Envoy already created individual stats for `ServerReflectionInfo` and other methods it saw. Switching to `methodAllowlist` only stops Envoy from breaking out *new* methods by name going forward. It does not remove the stats that already exist. To start from a clean set of stats, restart the gateway proxy.

## Clean up {#cleanup}

Remove the ListenerPolicy resources that you created.

```sh
kubectl delete listenerpolicy grpc-stats grpc-stats-allowlist -n {{< reuse "kgw-docs/snippets/namespace.md" >}} --ignore-not-found
```
