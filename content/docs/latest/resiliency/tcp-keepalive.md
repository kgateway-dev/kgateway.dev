---
title: TCP keepalive
weight: 10
description: Manage idle and stale connections with TCP keepalive. 
---

Manage idle and stale connections with TCP keepalive.

{{< callout type="warning" >}} 
{{< reuse "docs/versions/warn-2-1-only.md" >}} {{< reuse "docs/versions/warn-experimental.md" >}}
{{< /callout >}}

{{< callout >}}
{{< reuse "docs/snippets/proxy-kgateway.md" >}}
{{< /callout >}}

## About TCP keepalive

With keepalive, the kernel sends probe packets with only an acknowledgement flag (ACK) to the TCP socket of the destination after the connection was idle for a specific amount of time. This way, the connection does not have to be re-established repeatedly, which could otherwise lead to latency spikes. If the destination returns the packet with an acknowledgement flag (ACK), the connection is determined to be alive. If not, the probe can fail a certain number of times before the connection is considered stale. {{< reuse "docs/snippets/kgateway-capital.md" >}} can then close the stale connection, which can help avoid longer timeouts and retries on broken or stale connections.

## Before you begin

{{< reuse "docs/snippets/prereq.md" >}}

## Set up TCP keepalive

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
   | `keepAliveTime` | The number of seconds a connection needs to be idle before keep-alive probes are sent. |
   | `keepAliveInterval` | The number of seconds between keep-alive probes.  |  

2. Port-forward the gateway proxy on port 19000. 
   ```sh
   kubectl port-forward deployment/http -n {{< reuse "docs/snippets/namespace.md" >}} 19000
   ```
   
3. Get the configuration of your gateway proxy as a config dump. 
   ```sh
   curl -X POST 127.0.0.1:19000/config_dump\?include_eds > gateway-config.json
   ```
   
4. Open the config dump and find the `kube_httpbin_httpbin_8000` cluster. Verify that you see all the connection settings that you enabled in your BackendConfigPolicy. 
   
   Example output
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

{{< reuse "docs/snippets/cleanup.md" >}}

```sh
kubectl delete backendconfigpolicy httpbin-keepalive -n httpbin
```
