Manage idle and stale connections with TCP keepalive.

## About TCP keepalive

With keepalive, the kernel sends probe packets with only an acknowledgement flag (ACK) to the TCP socket of the destination after the connection was idle for a specific amount of time. This way, the connection does not have to be re-established repeatedly, which could otherwise lead to latency spikes. If the destination returns the packet with an acknowledgement flag (ACK), the connection is determined to be alive. If not, the probe can fail a certain number of times before the connection is considered stale. The proxy can then close the stale connection, which can help avoid longer timeouts and retries on broken or stale connections.

You can configure TCP keepalive for the following connection directions:

* **Downstream**: Configure keepalive for connections from downstream clients to the gateway listener by using a ListenerPolicy.
* **Upstream**: Configure keepalive for connections from the gateway to upstream backends by using a BackendConfigPolicy.

## Before you begin

{{< reuse "kgw-docs/snippets/prereq.md" >}}

## Downstream TCP keepalive {#downstream}

Configure a ListenerPolicy to enable TCP keepalive on connections that downstream clients make to the gateway listener.

1. Create a ListenerPolicy that sets TCP keepalive on the gateway listener.

   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.kgateway.dev/v1alpha1
   kind: ListenerPolicy
   metadata:
     name: listener-keepalive
     namespace: {{< reuse "kgw-docs/snippets/namespace.md" >}}
   spec:
     targetRefs:
     - group: gateway.networking.k8s.io
       kind: Gateway
       name: http
     default:
       tcpKeepalive:
         keepAliveProbes: 3
         keepAliveTime: 20m
         keepAliveInterval: 60s
   EOF
   ```

   | Setting | Description |
   | -- | -- |
   | `keepAliveProbes` | The maximum number of keepalive probes to send without a response before a connection is considered stale. |
   | `keepAliveTime` | The amount of time a connection needs to be idle before keepalive probes are sent. |
   | `keepAliveInterval` | The amount of time between keepalive probes. |

2. Get the TCP keepalive settings from the listener config dump and verify they match your ListenerPolicy.

   ```sh
   kubectl port-forward deployment/http -n {{< reuse "kgw-docs/snippets/namespace.md" >}} 19000:19000 &
   PF_PID=$!
   sleep 2
   curl -s 127.0.0.1:19000/config_dump | \
   jq '.configs[]
     | select(.["@type"] == "type.googleapis.com/envoy.admin.v3.ListenersConfigDump")
     | .dynamic_listeners[].active_state.listener
     | select(.name | startswith("listener~"))
     | {name, tcp_keepalive}'
   kill $PF_PID
   ```

   Example output:

   ```console
   {
     "name": "listener~80",
     "tcp_keepalive": {
       "keepalive_probes": 3,
       "keepalive_time": 1200,
       "keepalive_interval": 60
     }
   }
   ```

## Upstream TCP keepalive {#upstream}

Configure a BackendConfigPolicy to enable TCP keepalive on connections from the gateway to an upstream backend service.

1. Create a BackendConfigPolicy that applies TCP keepalive settings to the httpbin service.

   ```yaml
   kubectl apply -f- <<EOF
   kind: BackendConfigPolicy
   apiVersion: gateway.kgateway.dev/v1alpha1
   metadata:
     name: httpbin-keepalive
     namespace: httpbin
   spec:
     targetRefs:
       - name: httpbin
         group: ""
         kind: Service
     tcpKeepalive:
       keepAliveProbes: 3
       keepAliveTime: 30s
       keepAliveInterval: 5s
   EOF
   ```

   | Setting | Description |
   | -- | -- |
   | `keepAliveProbes` | The maximum number of keepalive probes to send without a response before a connection is considered stale. |
   | `keepAliveTime` | The amount of time a connection needs to be idle before keepalive probes are sent. |
   | `keepAliveInterval` | The amount of time between keepalive probes. |

2. Port-forward the gateway proxy on port 19000.

   ```sh
   kubectl port-forward deployment/http -n {{< reuse "kgw-docs/snippets/namespace.md" >}} 19000
   ```

3. Get the configuration of your gateway proxy as a config dump.

   ```sh
   curl -X POST 127.0.0.1:19000/config_dump\?include_eds > gateway-config.json
   ```

4. Open the config dump and find the `kube_httpbin_httpbin_8000` cluster. Verify that you see all the connection settings that you enabled in your BackendConfigPolicy.

   Example output:

   ```console {hl_lines=[5,6,7,8]}
   ...
      "connect_timeout": "5s",
      "metadata": {},
      "upstream_connection_options": {
       "tcp_keepalive": {
        "keepalive_probes": 3,
        "keepalive_time": 30,
        "keepalive_interval": 5
       }
      }
     },
   ...
   ```

## Cleanup

{{< reuse "kgw-docs/snippets/cleanup.md" >}}

```sh
kubectl delete listenerpolicy listener-keepalive -n {{< reuse "kgw-docs/snippets/namespace.md" >}} --ignore-not-found
kubectl delete backendconfigpolicy httpbin-keepalive -n httpbin --ignore-not-found
```
