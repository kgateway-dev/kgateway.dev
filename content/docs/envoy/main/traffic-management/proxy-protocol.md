---
title: Proxy protocol
weight: 20
---

Preserve connection information such as the client IP address and port for traffic that passes through your gateway proxy.

## About proxy protocol

[Proxy Protocol](https://www.haproxy.org/download/2.1/doc/proxy-protocol.txt) is used to preserve a client's IP address to ensure that upstream services receive the full network information, even when traffic is proxied through other components, such as an AWS Network Load Balancer or the gateway proxy itself. The gateway proxy and upstream services can then use this information to apply accurate rate limiting policies, make routing decisions, and properly log and audit traffic.

Without proxy protocol, the proxy removes the source IP address on incoming requests and instead adds its own IP address to it. Upstream services can therefore only see the IP address of the last proxy that handled the request, which can impact security measures and access control.

You can set up proxy protocol for the following traffic directions: 

* **Inbound**: Require PROXY protocol headers at the gateway proxy for traffic coming from downstream clients by configuring a ListenerPolicy. 
* **Outbound**: Send PROXY protocol headers to upstream backends by configuring a BackendConfigPolicy.

## Before you begin

{{< reuse "docs/snippets/prereq.md" >}}

## Inbound proxy protocol {#inbound}

Configure a ListenerPolicy to accept PROXY protocol headers on incoming connections to the gateway. When enabled, the gateway reads the PROXY header sent by the downstream client (for example, a load balancer) and makes the original client IP and port available to upstream services.

### Enable proxy protocol on a listener {#inbound-setup}

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

### Allow connections without proxy protocol headers {#allow-without-proxy-protocol}

By default, a listener that is configured with proxy protocol strictly requires all incoming connections to include a PROXY protocol header. Connections without a header are rejected. You can relax this requirement with the `allowRequestsWithoutProxyProtocol` field. This setting allows connections with and without a PROXY header for a particular listener.

This setting can be useful in environments where some clients send PROXY headers while others connect directly.

1. Update your ListenerPolicy to enable `allowRequestsWithoutProxyProtocol`.

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
       proxyProtocol:
         allowRequestsWithoutProxyProtocol: true
   EOF
   ```

2. Send an HTTP request to the gateway's LoadBalancer address without a PROXY protocol header and verify that it now succeeds. 

   ```sh
   INGRESS_GW_ADDRESS=$(kubectl get svc -n {{< reuse "docs/snippets/namespace.md" >}} http --output jsonpath='{.status.loadBalancer.ingress[0].ip}' 2>/dev/null || kubectl get svc -n {{< reuse "docs/snippets/namespace.md" >}} http --output jsonpath='{.status.loadBalancer.ingress[0].hostname}')
   curl -v http://$INGRESS_GW_ADDRESS/status/200 -H "host: www.example.com"
   ```

   Example output:

   ```
   * Connected to <INGRESS_GW_ADDRESS> port 80
   ...
   < HTTP/1.1 200 OK
   ```

### Cleanup {#inbound-cleanup}

```sh
kubectl delete listenerPolicy proxy-protocol -n {{< reuse "docs/snippets/namespace.md" >}}
```

## Outbound proxy protocol {#outbound}

Configure a BackendConfigPolicy to send PROXY protocol headers on outbound connections from the gateway proxy to an upstream backend. This allows the backend to see the original client's IP address and port, even after the connection is proxied through the gateway proxy.

Two PROXY protocol versions are supported:

| Version | Format | Use case |
|---|---|---|
| `V1` | Human-readable text | Maximum compatibility with older backends |
| `V2` | Binary | More efficient; preferred for modern backends that support it |

### Enable upstream proxy protocol {#outbound-setup}

To verify that the gateway sends PROXY protocol headers to an upstream backend, deploy a simple TCP echo server. Because the PROXY header is prepended at the TCP layer before any HTTP data is sent, a standard HTTP backend, such as httpbin cannot echo it back. The TCP echo server in this example prints the raw bytes it receives to its logs, including the PROXY header.

1. Deploy a TCP echo pod and Service. The pod runs `nc` in a loop and prints everything it receives on each connection.

   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: v1
   kind: Pod
   metadata:
     name: proxy-echo
     namespace: default
     labels:
       app: proxy-echo
   spec:
     containers:
     - name: echo
       image: busybox
       command: ['sh', '-c', 'while true; do nc -l -p 9090; done']
       ports:
       - containerPort: 9090
   ---
   apiVersion: v1
   kind: Service
   metadata:
     name: proxy-echo
     namespace: default
   spec:
     selector:
       app: proxy-echo
     ports:
     - port: 9090
       targetPort: 9090
   EOF
   ```

2. Create a BackendConfigPolicy that enables upstream proxy protocol for the echo service. This example uses PROXY protocol version v1. To use PROXY protocol v2 instead, set `version: V2`.

   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.kgateway.dev/v1alpha1
   kind: BackendConfigPolicy
   metadata:
     name: proxy-echo-upstream-pp
     namespace: default
   spec:
     targetRefs:
     - group: ""
       kind: Service
       name: proxy-echo
     upstreamProxyProtocol:
       version: V1
   EOF
   ```

   {{< callout type="info">}}
   When both `upstreamProxyProtocol` and `tls` are configured on the same `BackendConfigPolicy`, the PROXY protocol layer wraps the TLS transport socket. The gateway proxy sends the PROXY header before the TLS handshake begins.
   {{< /callout >}}

3. Create an HTTPRoute that routes traffic to the echo service.

   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.networking.k8s.io/v1
   kind: HTTPRoute
   metadata:
     name: proxy-echo
     namespace: default
   spec:
     parentRefs:
     - name: http
       namespace: {{< reuse "docs/snippets/namespace.md" >}}
     hostnames:
     - "echo.example.com"
     rules:
     - backendRefs:
       - name: proxy-echo
         port: 9090
   EOF
   ```

4. Send a request to the echo service through the gateway.

   {{< callout type="info" >}}
   Use the gateway's LoadBalancer address for this test, not `kubectl port-forward`. Envoy builds the PROXY header using the source IP of the incoming client connection. With port-forward, that source IP address is `127.0.0.1`, also referred to as a loopback. Envoy does not generate a standard PROXY header for loopback connections.
   {{< /callout >}}

   ```sh
   curl -vi http://$INGRESS_GW_ADDRESS:8080/ -H "host: echo.example.com"
   ```

   The request returns a 503 with `upstream connect error or disconnect/reset before headers. reset reason: connection termination`. This response code is expected as the TCP echo app does not send back HTTP headers. Here is what happens at the TCP level:

   1. The gateway proxy opens a TCP connection to `nc`.
   2. The gateway sends the PROXY header as the first bytes on the connection.
   3. The gateway sends the HTTP request.
   4. `nc` receives everything, prints it to stdout, and then exits.
   5. When `nc` exits, it closes the TCP connection without sending anything back.
   6. The gateway is waiting for an HTTP response, but the connection closes before any headers arrive. Envoy calls this "connection termination before headers" and returns a 503 to the client.

5. Check the echo pod logs to verify that the PROXY header was received by the backend.

   ```sh
   kubectl logs proxy-echo
   ```

   Example output:

   ```
   PROXY TCP4 10.244.X.X 10.245.X.X 16329 8080
   GET / HTTP/1.1
   host: echo.example.com
   user-agent: curl/8.7.1
   accept: */*
   x-forwarded-for: 10.244.0.1
   x-forwarded-proto: http
   x-envoy-external-address: 10.244.0.1
   x-request-id: de9fb90f-2960-41bb-8bc8-d19884e733b4
   x-envoy-expected-rq-timeout-ms: 15000
   ```

   The first line is the PROXY protocol v1 header. It contains the original client source IP (`10.244.X.X`), the gateway destination IP (`10.245.X.X`), and the source and destination ports. The subsequent lines are the HTTP request that was forwarded by the gateway.


### Cleanup {#outbound-cleanup}

```sh
kubectl delete pod proxy-echo -n default
kubectl delete service proxy-echo -n default
kubectl delete backendconfigpolicy proxy-echo-upstream-pp -n default
kubectl delete httproute proxy-echo -n default
```
