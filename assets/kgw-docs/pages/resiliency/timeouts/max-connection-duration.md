## About maximum connection duration

By default, a connection has no maximum lifetime and stays open until it goes idle, or until one side closes it. This applies whether the connection is from a downstream client to the gateway proxy, or from the gateway proxy to a backend. You can use a ListenerPolicy or BackendConfigPolicy resource to set an upper limit on these connections. The policy updates the [`max_connection_duration` setting in Envoy](https://www.envoyproxy.io/docs/envoy/latest/api-v3/config/core/v3/protocol.proto#envoy-v3-api-field-config-core-v3-httpprotocoloptions-max-connection-duration).

The connection duration is measured from when the connection was established until the configured duration elapses, not from the last activity on it. When the limit is reached, Envoy starts a drain sequence to allow in-flighth requests to finish. To configure the maximum time an existing connection can stay idle without any activity before it is closed, see [idle timeout]({{< link-hextra path="/resiliency/timeouts/idle/" >}}). 

Setting a maximum connection duration is useful in cases where clients must reconnect periodically to pick up DNS changes and redistribute across gateway proxy replicas after a scale-up. It is also useful for connections to a backend, where it lets the gateway proxy rotate the connection before the backend closes it first, which otherwise results in `503 upstream_reset_before_response_started{connection_termination}` errors.

## Before you begin

{{< reuse "kgw-docs/snippets/prereq.md" >}}

## Set up a maximum connection duration

You can set a maximum connection duration on connections from a client to the gateway proxy (downstream), or on connections from the gateway proxy to a backend (upstream). 

### Downstream connections

1. Create a ListenerPolicy with your maximum connection duration. In this example, connections from downstream clients to the gateway proxy are drained 10 minutes after they are established.

   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.kgateway.dev/v1alpha1
   kind: ListenerPolicy
   metadata:
     name: max-connection-duration
     namespace: {{< reuse "kgw-docs/snippets/namespace.md" >}}
   spec:
     targetRefs:
     - group: gateway.networking.k8s.io
       kind: Gateway
       name: http
     default:
       httpSettings:
         maxConnectionDuration: "10m"
   EOF
   ```

   | Field | Description |
   | ----- | ----- |
   | `maxConnectionDuration` | How long a connection can stay open, measured from when it was established. When the limit is reached, Envoy starts the drain sequence. Accepts a duration string of up to 32 characters, such as `30s`, `10m`, or `1h30m`. If unset, no maximum connection duration is applied. |

2. Verify that the gateway proxy is configured with the maximum connection duration. Port-forward the gateway proxy on port 19000, then query the listeners config dump and find the `common_http_protocol_options` configuration.

   ```sh
   kubectl port-forward deployment/http -n {{< reuse "kgw-docs/snippets/namespace.md" >}} 19000 &
   sleep 2
   curl -s 127.0.0.1:19000/config_dump | jq '.configs[] | select(."@type" == "type.googleapis.com/envoy.admin.v3.ListenersConfigDump") | .. | objects | select(has("common_http_protocol_options"))'
   ```

   Example output:

   ```console
   {
     "common_http_protocol_options": {
       "max_connection_duration": "600s"
     }
   }
   ```

### Upstream connections

1. Create a BackendConfigPolicy with your maximum connection duration. In this example, connections from the gateway proxy to the `httpbin` service are drained 10 minutes after they are established.

   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.kgateway.dev/v1alpha1
   kind: BackendConfigPolicy
   metadata:
     name: max-connection-duration
     namespace: httpbin
   spec:
     targetRefs:
     - name: httpbin
       group: ""
       kind: Service
     commonHttpProtocolOptions:
       maxConnectionDuration: 10m
   EOF
   ```

   | Field | Description |
   | ----- | ----- |
   | `commonHttpProtocolOptions.maxConnectionDuration` | How long a connection to this backend can stay open, measured from when it was established. When the limit is reached, Envoy starts the drain sequence. Accepts a duration string of up to 32 characters, such as `30s`, `10m`, or `1h30m`. If unset, no maximum connection duration is applied. |

2. Verify that the gateway proxy is configured with the maximum connection duration. Port-forward the gateway proxy on port 19000, then query the config dump and find the `common_http_protocol_options` configuration for the `httpbin` cluster.

   ```sh
   kubectl port-forward deployment/http -n {{< reuse "kgw-docs/snippets/namespace.md" >}} 19000 &
   sleep 2
   curl -s 127.0.0.1:19000/config_dump | jq '[.. | objects | select(has("common_http_protocol_options")) | {common_http_protocol_options}]'
   ```

   Example output:

   ```console
   {
    "@type": "type.googleapis.com/envoy.extensions.upstreams.http.v3.HttpProtocolOptions",
     "common_http_protocol_options": {
    "max_connection_duration": "600s"
     },
     "explicit_http_config": {
       "http_protocol_options": {}
    }
   }
   ```

## Cleanup

{{< reuse "kgw-docs/snippets/cleanup.md" >}}

```sh
kubectl delete listenerpolicy max-connection-duration -n {{< reuse "kgw-docs/snippets/namespace.md" >}} --ignore-not-found
kubectl delete backendconfigpolicy max-connection-duration -n httpbin --ignore-not-found
```
