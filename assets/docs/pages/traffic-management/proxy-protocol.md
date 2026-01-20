Preserve connection information such as the client IP address and port for traffic that goes through your gateway proxy.

## About proxy protocol

[Proxy Protocol](https://www.haproxy.org/download/2.1/doc/proxy-protocol.txt) is used to preserve a client’s IP address to ensure that upstream services receive the full network information, even when traffic is proxied through other components, such as an AWS Network Load Balancer or the gateway proxy itself. The gateway proxy and upstream services can then use this information to apply accurate rate limiting policies, make routing decisions, and properly log and audit traffic. 

Without proxy protocol, the proxy removes the source IP address on incoming requests and instead adds its own IP address to it. Upstream services can therefore only see the IP address of the last proxy that handled the request, which can impact security measures and access control. 


## Before you begin

{{< reuse "docs/snippets/prereq.md" >}}

## Setup

1. Create a ListenerPolicy resource to enable proxy protocol for the listeners on your gateway proxy. The following example enables proxy protocol on all listeners that are configured on the gateway.    
   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.kgateway.dev/v1alpha1
   kind: ListenerPolicy
   metadata:
     name: proxy-protocol
     namespace: {{< reuse "docs/snippets/namespace.md" >}}
   spec:
     targetRefs:
     - group: gateway.networking.k8s.io
       kind: Gateway
       name: http
     default: 
       proxyProtocol: {}   
   EOF
   ```

2. Verify that your configuration is applied by reviewing the Envoy configuration. 
   ```sh
   kubectl port-forward deploy/http -n kgateway-system 19000 &
   PF_PID=$!

   sleep 2

   curl -s http://localhost:19000/config_dump | \
   jq '.configs[]
    | select(.["@type"] == "type.googleapis.com/envoy.admin.v3.ListenersConfigDump")
    | .static_listeners[].listener.listener_filters?,
    .dynamic_listeners[].active_state.listener.listener_filters?'

   kill $PF_PID
   ```
  
   Example output: 
   ```
   [
     {
       "name": "envoy.filters.listener.proxy_protocol",
       "typed_config": {
         "@type": "type.googleapis.com/envoy.extensions.filters.listener.proxy_protocol.v3.ProxyProtocol",
         "stat_prefix": "kgateway-system_proxy-protocol"
       }
     }
   ]
   ```
  
## Cleanup

{{< reuse "docs/snippets/cleanup.md" >}}

```sh
kubectl delete listenerPolicy proxy-protocol -n {{< reuse "docs/snippets/namespace.md" >}}
```
