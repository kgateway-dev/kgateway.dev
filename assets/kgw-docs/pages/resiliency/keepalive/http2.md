Detect half-dead HTTP/2 and gRPC upstream connections with PING-based keepalive.

## About HTTP/2 keepalive

TCP keepalive operates at the OS level and detects connection loss at the network layer. However, it cannot detect connections that remain open at the TCP level, but are no longer functional at the HTTP/2 level. For example, if a cloud load balancer silently drops a long-lived connection after its idle timeout expires without sending a TCP reset, the gateway proxy has no way to know the connection is broken until it tries to use it.

For HTTP/2 and gRPC connections, you can configure HTTP/2 PING-based keepalive in a BackendConfigPolicy resource. Envoy sends periodic PING frames over the connection. If no response arrives within the configured timeout, Envoy closes the connection and the event is recorded in the `http2.keepalive_timeout` cluster statistic.

## Before you begin

{{< reuse "kgw-docs/snippets/prereq.md" >}}

## Configure HTTP/2 keepalive {#configure}

HTTP/2 keepalive only applies when the gateway proxy uses HTTP/2 to connect to the backend. To enable this, set `appProtocol: kubernetes.io/h2c` on the Service port so that kgateway treats the upstream as an HTTP/2 backend.

1. Patch the httpbin Service to use HTTP/2 on port 8000.

   ```sh
   kubectl patch service httpbin -n httpbin --type='json' \
     -p='[{"op":"add","path":"/spec/ports/0/appProtocol","value":"kubernetes.io/h2c"}]'
   ```

2. Create a BackendConfigPolicy that applies HTTP/2 keepalive settings to the httpbin service.

   ```yaml
   kubectl apply -f- <<EOF
   kind: BackendConfigPolicy
   apiVersion: gateway.kgateway.dev/v1alpha1
   metadata:
     name: httpbin-http2-keepalive
     namespace: httpbin
   spec:
     targetRefs:
       - name: httpbin
         group: ""
         kind: Service
     http2ProtocolOptions:
       connectionKeepalive:
         timeout: 5s
         interval: 30s
         connectionIdleInterval: 60s
   EOF
   ```

   | Setting | Description |
   | -- | -- |
   | `timeout` | How long to wait for a PING response before closing the connection. Required. |
   | `interval` | How often to send PING frames over the connection. Optional. |
   | `connectionIdleInterval` | How long a connection must be idle before PING frames start. Optional. |

3. Port-forward the gateway proxy and verify that `connection_keepalive` appears in the httpbin cluster config.

   ```sh
   kubectl port-forward deployment/http -n {{< reuse "kgw-docs/snippets/namespace.md" >}} 19000:19000 &
   PF_PID=$!
   sleep 2
   curl -s "127.0.0.1:19000/config_dump?include_eds" | \
   jq '.configs[]
     | select(.["@type"] == "type.googleapis.com/envoy.admin.v3.ClustersConfigDump")
     | .dynamic_active_clusters[].cluster
     | select(.name | contains("httpbin"))
     | .typed_extension_protocol_options
       ["envoy.extensions.upstreams.http.v3.HttpProtocolOptions"]
       .explicit_http_config.http2_protocol_options.connection_keepalive'
   kill $PF_PID
   ```

   Example output:

   ```console
   {
     "interval": "30s",
     "timeout": "5s",
     "connection_idle_interval": "60s"
   }
   ```

## Cleanup

{{< reuse "kgw-docs/snippets/cleanup.md" >}}

```sh
kubectl delete backendconfigpolicy httpbin-http2-keepalive -n httpbin --ignore-not-found
kubectl patch service httpbin -n httpbin --type='json' \
  -p='[{"op":"remove","path":"/spec/ports/0/appProtocol"}]'
```
