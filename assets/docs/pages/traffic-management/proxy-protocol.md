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

3. Send a request to the httpbin app without a proxy protocol header. Verify that the request fails.

   {{< callout type="info" >}}
   PROXY protocol is enforced at the TCP listener level. Envoy closes the connection before any HTTP processing occurs. Because of that, no HTTP status code is returned in the response. Note that you must use the gateway proxy's load balancer IP address to send the request. If you port-forward the proxy on your local machine instead, you bypass Envoy's listener filters and cannot test the proxy protocol capability. To assign a load balancer IP address in local test setups, consider using [`cloud-provider-kind`](https://github.com/kubernetes-sigs/cloud-provider-kind).  
   {{< /callout >}}

   ```sh
   curl -vik \
    http://$INGRESS_GW_ADDRESS:8080/headers \
    -H "host: www.example.com:8080"
   ```

   Example output: 
   ```console
   * Request completely sent off
   * Empty reply from server
   * Closing connection
   curl: (52) Empty reply from server
   ```

4. Repeat the request with a proxy protocol header. Verify that this time, the request succeeds. 
   ```sh
   curl -vik \
    --haproxy-protocol http://$INGRESS_GW_ADDRESS:8080/headers \
    -H "host: www.example.com:8080"
   ```

   Example output: 
   ```console
   < HTTP/1.1 200 OK
   HTTP/1.1 200 OK
   ...
   ```
  

## Cleanup

{{< reuse "docs/snippets/cleanup.md" >}}

```sh
kubectl delete listenerPolicy proxy-protocol -n {{< reuse "docs/snippets/namespace.md" >}}
```
