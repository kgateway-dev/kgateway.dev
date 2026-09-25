---
title: gRPC statistics
description: Collect per-service and per-method gRPC metrics from Gateway listeners.
weight: 15
---

Use the `grpcStats` field on a ListenerPolicy resource to add Envoy's `grpc_stats` HTTP filter to the listeners on a Gateway. The filter records per-service and per-method gRPC metrics, including the gRPC status code that is not visible in ordinary HTTP response-code metrics.

## Before you begin {#before-you-begin}

{{< reuse "kgw-docs/snippets/prereq.md" >}}

Create or identify a Gateway that serves gRPC traffic. For an end-to-end example, see the [gRPC routing guide]({{< link-hextra path="/traffic-management/grpc/" >}}).

## Configure gRPC statistics {#configure-grpc-statistics}

Choose whether to collect statistics for every gRPC method or for a bounded list of methods. Collecting every method is useful for trusted services with known method names. An allow list is safer when client-supplied method names might create too many metric series.

1. Create a ListenerPolicy that enables the `grpcStats` filter on the Gateway.

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
       name: http
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

2. To collect statistics for only selected methods, use `methodAllowlist` instead of `statsForAllMethods`.

   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.kgateway.dev/v1alpha1
   kind: ListenerPolicy
   metadata:
     name: grpc-stats-allowlist
     namespace: {{< reuse "kgw-docs/snippets/namespace.md" >}}
   spec:
     targetRefs:
     - group: gateway.networking.k8s.io
       kind: Gateway
       name: http
     default:
       httpSettings:
         grpcStats:
           methodAllowlist:
           - /pkg.Foo/Get
           - /pkg.Foo/List
           - /pkg.Bar/Ping
   EOF
   ```

   | Field | Description |
   | --- | --- |
   | `methodAllowlist` | Fully qualified gRPC methods to record, in the `/package.Service/Method` format. The list must contain 1-128 methods. Do not set this field together with `statsForAllMethods`. |

3. Verify that the ListenerPolicy is accepted and attached to the Gateway.

   ```sh
   kubectl get listenerpolicy grpc-stats -n {{< reuse "kgw-docs/snippets/namespace.md" >}} -o yaml
   ```

   Example output:

   ```yaml
   status:
     ancestors:
     - conditions:
       - reason: Valid
         status: "True"
         type: Accepted
       - reason: Attached
         status: "True"
         type: Attached
   ```

4. Port-forward the gateway proxy admin port.

   ```sh
   kubectl port-forward deployment/http -n {{< reuse "kgw-docs/snippets/namespace.md" >}} 19000
   ```

5. Verify that the Envoy configuration includes the `grpc_stats` filter before the router filter.

   ```sh
   curl -s 127.0.0.1:19000/config_dump | jq '.. | .httpFilters? // empty'
   ```

   Example output:

   ```yaml
   - name: envoy.filters.http.grpc_stats
     typedConfig:
       '@type': type.googleapis.com/envoy.extensions.filters.http.grpc_stats.v3.FilterConfig
       enableUpstreamStats: true
       statsForAllMethods: true
   - name: envoy.filters.http.router
   ```

## Clean up {#cleanup}

Remove the ListenerPolicy resources that you created.

```sh
kubectl delete listenerpolicy grpc-stats grpc-stats-allowlist -n {{< reuse "kgw-docs/snippets/namespace.md" >}} --ignore-not-found
```
