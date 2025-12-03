Customize the default idle timeout of 1 hour (3600s). 

## About idle timeouts

By default, Envoy terminates the connection to a downstream or upstream service after one hour if there are no active streams. You can customize this idle timeout with an HTTPListenerPolicy. The policy updates the [`common_http_protocol_options` setting in Envoy](https://www.envoyproxy.io/docs/envoy/latest/api-v3/extensions/upstreams/http/v3/http_protocol_options.proto).

Note that the idle timeout configures the timeout for the entire connection from a downstream service to the gateway proxy, and to the upstream service. If you want to set a timeout for a single stream, configure the [idle stream timeout]({{< link-hextra path="/resiliency/timeouts/idle-stream/" >}}) instead. 

{{< callout >}}
{{< reuse "docs/snippets/proxy-kgateway.md" >}}
{{< /callout >}}


## Before you begin

{{< reuse "docs/snippets/prereq.md" >}}

## Set up idle timeouts

1. Create an HTTPListenerPolicy with your idle timeout configuration. In this example, you apply an idle timeout of 30 seconds.

   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.kgateway.dev/v1alpha1
   kind: HTTPListenerPolicy
   metadata:
     name: idle-time
     namespace: {{< reuse "docs/snippets/namespace.md" >}}
   spec:
     targetRefs:
     - group: gateway.networking.k8s.io
       kind: Gateway
       name: http
     idleTimeout: "30s"
   EOF
   ```

2. Verify that the gateway proxy is configured with the idle timeout.
   1. Port-forward the gateway proxy on port 19000.

      ```sh
      kubectl port-forward deployment/http -n {{< reuse "docs/snippets/namespace.md" >}} 19000
      ```

   2. Get the configuration of your gateway proxy as a config dump.

      ```sh
      curl -X POST 127.0.0.1:19000/config_dump\?include_eds > gateway-config.json
      ```

   3. Open the config dump and find the `http_connection_manager` configuration. Verify that the timeout policy is set as you configured it.
      
      Example `jq` command:
      ```sh
      jq '.configs[] 
      | select(."@type" == "type.googleapis.com/envoy.admin.v3.ListenersConfigDump") 
      | .dynamic_listeners[].active_state.listener.filter_chains[].filters[] 
      | select(.name == "envoy.filters.network.http_connection_manager")' gateway-config.json
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
      
## Cleanup

{{< reuse "docs/snippets/cleanup.md" >}}
   
```sh
kubectl delete httplistenerpolicy idle-time -n {{< reuse "docs/snippets/namespace.md" >}} 
```