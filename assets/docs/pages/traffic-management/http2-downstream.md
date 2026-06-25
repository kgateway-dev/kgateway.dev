Tune how the gateway handles HTTP/2 connections from downstream clients by configuring the `http2ProtocolOptions` field on a ListenerPolicy resource. You can control stream and connection flow-control window sizes and the maximum number of concurrent streams per connection.

## Before you begin

{{< reuse "docs/snippets/prereq.md" >}}

## Configure downstream HTTP/2 settings

1. Create a ListenerPolicy that sets downstream HTTP/2 options on the gateway.
   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.kgateway.dev/v1alpha1
   kind: ListenerPolicy
   metadata:
     name: http2-settings
     namespace: {{< reuse "docs/snippets/namespace.md" >}}
   spec:
     targetRefs:
     - group: gateway.networking.k8s.io
       kind: Gateway
       name: http
     default:
       httpSettings:
         http2ProtocolOptions:
           initialStreamWindowSize: 128Ki
           initialConnectionWindowSize: 256Ki
           maxConcurrentStreams: 100
   EOF
   ```

   | Setting | Description |
   | -- | -- |
   | `initialStreamWindowSize` | Initial flow-control window size for each HTTP/2 stream in bytes. Valid values: 65535–2147483647. Defaults to 268435456 (256 MiB). Accepts Kubernetes resource quantity strings, such such as `128Ki`. |
   | `initialConnectionWindowSize` | Initial flow-control window size for the HTTP/2 connection in bytes. Same valid range and default as `initialStreamWindowSize`. Accepts Kubernetes resource quantity strings such as `256Ki`. |
   | `maxConcurrentStreams` | Maximum number of concurrent HTTP/2 streams per connection in bytes. Valid values: 1–2147483647. Envoy defaults to 1024. |

2. Port-forward the gateway proxy on port 19000.
   ```sh
   kubectl port-forward deployment/http -n {{< reuse "docs/snippets/namespace.md" >}} 19000
   ```

3. Get the `http2_protocol_options` values that are applied to the listener from the proxy's config dump.
   ```sh
   curl -s 127.0.0.1:19000/config_dump | jq '.. | .http2_protocol_options? // empty | select(. != {})'
   ```

   Example output:
   ```console
   {
     "initial_stream_window_size": 131072,
     "initial_connection_window_size": 262144,
     "max_concurrent_streams": 100
   }
   ```

## Cleanup

{{< reuse "docs/snippets/cleanup.md" >}}

```sh
kubectl delete listenerpolicy http2-settings -n {{< reuse "docs/snippets/namespace.md" >}}
```
