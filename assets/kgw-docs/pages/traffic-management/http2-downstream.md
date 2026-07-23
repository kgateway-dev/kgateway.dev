Tune how the gateway handles HTTP/2 connections from downstream clients by configuring the `http2ProtocolOptions` field on a ListenerPolicy resource. You can control stream and connection flow-control window sizes and the maximum number of concurrent streams per connection.

## Before you begin

{{< reuse "kgw-docs/snippets/prereq.md" >}}

## Configure downstream HTTP/2 settings

1. Create a ListenerPolicy that sets downstream HTTP/2 options on the gateway.
   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.kgateway.dev/v1alpha1
   kind: ListenerPolicy
   metadata:
     name: http2-settings
     namespace: {{< reuse "kgw-docs/snippets/namespace.md" >}}
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
   | `initialStreamWindowSize` | Initial flow-control window size for each HTTP/2 stream in bytes. Valid values: 65535–2147483647. Defaults to 268435456 (256 MiB). Accepts Kubernetes resource quantity strings, such as `128Ki`. |
   | `initialConnectionWindowSize` | Initial flow-control window size for the HTTP/2 connection in bytes. Same valid range and default as `initialStreamWindowSize`. Accepts Kubernetes resource quantity strings such as `256Ki`. |
   | `maxConcurrentStreams` | Maximum number of concurrent HTTP/2 streams per connection in bytes. Valid values: 1–2147483647. Envoy defaults to 1024. |

2. Port-forward the gateway proxy on port 19000.
   ```sh
   kubectl port-forward deployment/http -n {{< reuse "kgw-docs/snippets/namespace.md" >}} 19000
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

{{< version include-if="2.4.x,2.5.x" >}}
## Other configurations {#other}

### WebSocket over HTTP/2 {#allow-connect}

By default, Envoy rejects Extended CONNECT requests (RFC 8441), which are used by some clients, such as Firefox, to establish WebSocket connections over HTTP/2. To allow these connections, set `allowConnect: true` in the `http2ProtocolOptions` field of a ListenerPolicy.

```yaml
kubectl apply -f- <<EOF
apiVersion: gateway.kgateway.dev/v1alpha1
kind: ListenerPolicy
metadata:
  name: http2-settings
  namespace: {{< reuse "kgw-docs/snippets/namespace.md" >}}
spec:
  targetRefs:
  - group: gateway.networking.k8s.io
    kind: Gateway
    name: http
  default:
    httpSettings:
      http2ProtocolOptions:
        allowConnect: true
EOF
```

| Setting | Description |
| -- | -- |
| `allowConnect` | Enables RFC 8441 Extended CONNECT support on the HTTP/2 listener. Set to `true` to allow clients that use WebSocket-over-HTTP/2, such as Firefox, to establish WebSocket connections. Envoy translates the Extended CONNECT request into an HTTP/1.1 Upgrade before forwarding it to the upstream service. Defaults to `false`. |
{{< /version >}}

## Cleanup

{{< reuse "kgw-docs/snippets/cleanup.md" >}}

```sh
kubectl delete listenerpolicy http2-settings -n {{< reuse "kgw-docs/snippets/namespace.md" >}}
```
