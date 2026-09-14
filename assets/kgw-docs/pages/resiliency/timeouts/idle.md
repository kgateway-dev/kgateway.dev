Customize the default idle timeout of 1 hour (3600s). 

## About idle timeouts

By default, Envoy terminates the connection to a downstream or upstream service after one hour if there are no active streams. You can customize this idle timeout with a ListenerPolicy. The policy updates the [`common_http_protocol_options` setting in Envoy](https://www.envoyproxy.io/docs/envoy/latest/api-v3/extensions/upstreams/http/v3/http_protocol_options.proto).

Note that the idle timeout configures the timeout for the entire connection from a downstream service to the gateway proxy, and to the upstream service. If you want to set a timeout for a single stream, configure the [idle stream timeout]({{< link-hextra path="/resiliency/timeouts/idle-stream/" >}}) instead. 

## Before you begin

{{< reuse "kgw-docs/snippets/prereq.md" >}}

## Set up idle timeouts

1. Create a ListenerPolicy with your idle timeout configuration. In this example, you apply an idle timeout of 30 seconds.

   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.kgateway.dev/v1alpha1
   kind: ListenerPolicy
   metadata:
     name: idle-time
     namespace: {{< reuse "kgw-docs/snippets/namespace.md" >}}
   spec:
     targetRefs:
     - group: gateway.networking.k8s.io
       kind: Gateway
       name: http
     default:
       httpSettings:
         idleTimeout: "30s"
   EOF
   ```

2. Verify that the gateway proxy is configured with the idle timeout.
   1. Port-forward the gateway proxy on port 19000.

      ```sh
      kubectl port-forward deployment/http -n {{< reuse "kgw-docs/snippets/namespace.md" >}} 19000
      ```

   2. Query the config dump and find the `http_connection_manager` configuration. Verify that the timeout policy is set as you configured it.

      ```sh
      curl -s 127.0.0.1:19000/config_dump | jq '.configs[]
      | select(."@type" == "type.googleapis.com/envoy.admin.v3.ListenersConfigDump")
      | .dynamic_listeners[].active_state.listener.filter_chains[].filters[]
      | select(.name == "envoy.filters.network.http_connection_manager")'
      ```
      
      Example output: 
      ```console{hl_lines=[25]}
      {
        "name": "envoy.filters.network.http_connection_manager",
        "typed_config": {
            "@type": "type.googleapis.com/envoy.extensions.filters.network.http_connection_manager.v3.HttpConnectionManager",
            "stat_prefix": "http",
            "rds": {
            "config_source": {
                "ads": {},
                "resource_api_version": "V3"
            },
            "route_config_name": "listener~8080"
            },
            "http_filters": [
            {
                "name": "envoy.filters.http.router",
                "typed_config": {
                "@type": "type.googleapis.com/envoy.extensions.filters.http.router.v3.Router"
                }
            }
            ],
            "use_remote_address": true,
            "normalize_path": true,
            "merge_slashes": true,
            "common_http_protocol_options": {
            "idle_timeout": "30s"
            }
        }
      }
      ```
      
{{< version exclude-if="2.1.x,2.2.x,2.3.x,2.4.x" >}}

## Limit the total duration of a connection {#max-connection-duration}

An idle timeout closes a connection only when that connection has no active requests. A long-lived connection that keeps sending requests stays open indefinitely. To place an upper bound on how long any connection can live, regardless of how busy it is, set `maxConnectionDuration` alongside `idleTimeout`.

The duration is measured from the moment the connection is established. When the duration is reached, the gateway starts a drain sequence rather than dropping the connection abruptly, so in-flight requests are allowed to finish. Clients then reconnect. This behavior is useful when you want long-lived HTTP/2 and gRPC connections to be periodically redistributed across gateway pods, because an L4 load balancer such as an AWS Network Load Balancer spreads load across pods only when connections are re-established.

If you do not set this field, connections have no maximum duration.

1. Update the ListenerPolicy to add a maximum connection duration of 10 minutes.

   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.kgateway.dev/v1alpha1
   kind: ListenerPolicy
   metadata:
     name: idle-time
     namespace: {{< reuse "kgw-docs/snippets/namespace.md" >}}
   spec:
     targetRefs:
     - group: gateway.networking.k8s.io
       kind: Gateway
       name: http
     default:
       httpSettings:
         idleTimeout: "30s"
         maxConnectionDuration: "600s"
   EOF
   ```

2. Port-forward the gateway proxy on port 19000.

   ```sh
   kubectl port-forward deployment/http -n {{< reuse "kgw-docs/snippets/namespace.md" >}} 19000
   ```

3. Query the config dump and verify that both settings are applied to the `http_connection_manager`.

   ```sh
   curl -s 127.0.0.1:19000/config_dump | jq '.configs[]
   | select(."@type" == "type.googleapis.com/envoy.admin.v3.ListenersConfigDump")
   | .dynamic_listeners[].active_state.listener.filter_chains[].filters[]
   | select(.name == "envoy.filters.network.http_connection_manager")
   | .typed_config.common_http_protocol_options'
   ```

   Example output:

   ```console
   {
     "idle_timeout": "30s",
     "max_connection_duration": "600s"
   }
   ```

> [!NOTE]
> To bound the duration of connections between the gateway and an upstream service instead, set `maxConnectionDuration` in the `commonHttpProtocolOptions` section of a BackendConfigPolicy. For more information, see [Connection settings]({{< link-hextra path="/resiliency/connection/" >}}).

{{< /version >}}

## Cleanup

{{< reuse "kgw-docs/snippets/cleanup.md" >}}
   
```sh
kubectl delete listenerpolicy idle-time -n {{< reuse "kgw-docs/snippets/namespace.md" >}}
```


