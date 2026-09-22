Limit how long a connection stays open, however active it is.

## About maximum connection duration

By default, a connection to the gateway proxy has no maximum lifetime. It stays open until it goes idle, or until one side closes it. You can put an upper bound on it with a ListenerPolicy. The policy updates the [`max_connection_duration` setting in Envoy](https://www.envoyproxy.io/docs/envoy/latest/api-v3/config/core/v3/protocol.proto#envoy-v3-api-field-config-core-v3-httpprotocoloptions-max-connection-duration).

The duration is measured from when the connection was established, not from the last activity on it. When the limit is reached, Envoy starts the drain sequence rather than cutting the connection off, so in-flight requests are allowed to finish. This is what makes it different from the [idle timeout]({{< link-hextra path="/resiliency/timeouts/idle/" >}}), which only fires when nothing is happening on the connection: a busy connection never idles out, but it does reach its maximum duration.

Bounding connection lifetime is mostly useful for making clients reconnect periodically, so that they pick up DNS changes and redistribute across gateway proxy replicas after a scale-up.

To bound connections from the gateway proxy to a backend instead of connections from downstream clients, set `maxConnectionDuration` on a BackendConfigPolicy. For more information, see [BackendConfigPolicy]({{< link-hextra path="/about/policies/backendconfigpolicy/" >}}).

## Before you begin

{{< reuse "kgw-docs/snippets/prereq.md" >}}

## Set up a maximum connection duration

1. Create a ListenerPolicy with your maximum connection duration. In this example, connections are drained 10 minutes after they are established.

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
   | `maxConnectionDuration` | How long a connection may stay open, measured from when it was established. When the limit is reached, Envoy starts the drain sequence. Accepts a duration string of up to 32 characters, such as `30s`, `10m`, or `1h30m`. If unset, there is no maximum connection duration. |

2. Verify that the gateway proxy is configured with the maximum connection duration.

   1. Port-forward the gateway proxy on port 19000.

      ```sh
      kubectl port-forward deployment/http -n {{< reuse "kgw-docs/snippets/namespace.md" >}} 19000
      ```

   2. Query the config dump and find the `common_http_protocol_options` configuration.

      ```sh
      curl -s 127.0.0.1:19000/config_dump | jq '[.. | objects | select(has("common_http_protocol_options")) | {common_http_protocol_options}]'
      ```

      Example output:

      ```console
      "common_http_protocol_options": {
        "max_connection_duration": "600s"
      }
      ```

## Cleanup

{{< reuse "kgw-docs/snippets/cleanup.md" >}}

```sh
kubectl delete listenerpolicy max-connection-duration -n {{< reuse "kgw-docs/snippets/namespace.md" >}}
```
