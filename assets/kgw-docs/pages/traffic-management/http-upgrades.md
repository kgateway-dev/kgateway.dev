## About HTTP protocol upgrades

An HTTP upgrade lets a client switch an ordinary HTTP request onto another protocol over the same connection. The most common use case includes WebSocket upgrades or `CONNECT` requests. In a `CONNECT` request, instead of upgrading a request in place, the client asks the proxy to open a tunnel to a destination, through which it can send any protocol as raw bytes.

By default, the gateway proxy rejects upgrade requests from clients. To enable upgrades, you can create one of the following resources. 

| Resource | Applied to | Field | What it does |
| -------- | ----- | ----- | ------------ |
| ListenerPolicy | Gateway listener | `spec.default.httpSettings.upgradeConfig.enabledUpgrades` | Lists the `Upgrade` header values the listener accepts. Needs at least one entry. |
| {{< reuse "kgw-docs/snippets/trafficpolicy.md" >}} | Gateway, HTTPRoute, or ListenerSet | `spec.httpUpgrade` | Configures upgrades for the Gateway, HTTPRoute, or ListenerSet that the policy targets, and is the only place `CONNECT` termination can be set. |

> [!WARNING]
> **After an upgrade is established, the tunneled payload is not inspected by HTTP filters.** Authenticate and authorize the initial upgrade request, enable upgrades only for clients you trust, and do not enable request buffering on a route that carries upgrades.

### Considerations

- **`CONNECT` termination is per route.** You cannot configure `CONNECT` termination on a listener by using a ListenerPolicy. Always use the {{< reuse "kgw-docs/snippets/trafficpolicy.md" >}} resource instead.
- **Terminating `CONNECT` requests forwards raw bytes.** If you configure TLS for the selected backend, those bytes are wrapped in a separate upstream TLS session. Leave backend TLS disabled when the payload must reach the backend unchanged.
- **You cannot combine upgrades with request buffering.** A {{< reuse "kgw-docs/snippets/trafficpolicy.md" >}} that sets both `httpUpgrade` and `buffer` is rejected, unless the `buffer` setting disables buffering.
- **WebSocket over HTTP/2 needs an additional listener setting.** Clients such as Firefox open WebSocket connections over HTTP/2 with Extended CONNECT requests that the listener rejects by default. Allowing Extended CONNECT requests is a separate setting from the upgrade configuration on this page. You need set the `allowConnect` field on the listener's `http2ProtocolOptions`, and enable Websocket upgrades on the gateway listener or route. Envoy converts an accepted Extended CONNECT request into a regular `websocket` upgrade internally, so it still has to accept the same upgrade token as any other WebSocket request. For more information, see [WebSocket over HTTP/2]({{< link-hextra path="/traffic-management/http2-downstream/#allow-connect" >}}).

## Before you begin

{{< reuse "kgw-docs/snippets/prereq.md" >}}

## Enable upgrades for a listener

Configure a gateway listener to accept protocol upgrade requests.

1. Send an upgrade request through the gateway proxy, and confirm that it is rejected with a 403 HTTP response. By default, the gateway proxy does not allow protocol upgrades. 

   {{< tabs >}}
   {{% tab name="Cloud Provider LoadBalancer" %}}
   ```sh
   curl -v --max-time 5 \
     -H "Host: www.example.com" \
     -H "Connection: Upgrade" \
     -H "Upgrade: websocket" \
     -H "Sec-WebSocket-Version: 13" \
     -H "Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==" \
     http://$INGRESS_GW_ADDRESS:8080/get
   ```
   {{% /tab %}}
   {{% tab name="Port-forward for local testing" %}}
   ```sh
   curl -v --max-time 5 \
     -H "Host: www.example.com" \
     -H "Connection: Upgrade" \
     -H "Upgrade: websocket" \
     -H "Sec-WebSocket-Version: 13" \
     -H "Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==" \
     http://localhost:8080/get
   ```
   {{% /tab %}}
   {{< /tabs >}}

   Example output:

   ```console
   < HTTP/1.1 403 Forbidden
   < content-length: 0
   < server: envoy
   < connection: close
   ```

2. Create a ListenerPolicy that lists the upgrade header values that you want the gateway proxy to accept. 

   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.kgateway.dev/v1alpha1
   kind: ListenerPolicy
   metadata:
     name: enable-upgrades
     namespace: {{< reuse "kgw-docs/snippets/namespace.md" >}}
   spec:
     targetRefs:
     - group: gateway.networking.k8s.io
       kind: Gateway
       name: http
     default:
       httpSettings:
         upgradeConfig:
           enabledUpgrades:
           - websocket
   EOF
   ```

   | Field | Description |
   | ----- | ----- |
   | `enabledUpgrades` | The upgrade tokens that the listener accepts, such as `websocket` or `CONNECT`. Tokens are case-insensitive. List at least one. Enabling `CONNECT` here proxies CONNECT requests upstream without terminating them. |

3. Send the same upgrade request again, and confirm that the gateway proxy now forwards it instead of rejecting it. Note that the sample httpbin app does not implement WebSocket, so it never completes the handshake with a `101 Switching Protocols` response. Instead, the gateway proxy now accepts the upgrade and holds the connection open, waiting on the httpbin backend, until curl times out after 5 seconds. Getting a timeout instead of a `403` is the proof that the gateway proxy forwarded the request.

   {{< tabs >}}
   {{% tab name="Cloud Provider LoadBalancer" %}}
   ```sh
   curl -v --max-time 5 \
     -H "Host: www.example.com" \
     -H "Connection: Upgrade" \
     -H "Upgrade: websocket" \
     -H "Sec-WebSocket-Version: 13" \
     -H "Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==" \
     http://$INGRESS_GW_ADDRESS:8080/get
   ```
   {{% /tab %}}
   {{% tab name="Port-forward for local testing" %}}
   ```sh
   curl -v --max-time 5 \
     -H "Host: www.example.com" \
     -H "Connection: Upgrade" \
     -H "Upgrade: websocket" \
     -H "Sec-WebSocket-Version: 13" \
     -H "Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==" \
     http://localhost:8080/get
   ```
   {{% /tab %}}
   {{< /tabs >}}

   Example output:

   ```console
   * Request completely sent off
   * Operation timed out after 5001 milliseconds with 0 bytes received
   ```

## Enable WebSocket on a route {#websocket-route}

Use the {{< reuse "kgw-docs/snippets/trafficpolicy.md" >}} resource instead of a ListenerPolicy when you want WebSocket enabled for only one route rather than every route on the listener. The route-level setting takes precedence over the listener-level setting, so a route can accept an upgrade that the listener does not list.

The {{< reuse "kgw-docs/snippets/trafficpolicy.md" >}} resource must be in the same namespace as the route that it targets. You can also choose to target a Gateway or ListenerSet instead. 

1. If you followed the [Enable upgrades for a listener](#enable-upgrades-for-a-listener) guide, remove the ListenerPolicy that you created. 

   ```sh
   kubectl delete listenerpolicy enable-upgrades -n {{< reuse "kgw-docs/snippets/namespace.md" >}}
   ```

2. Create the {{< reuse "kgw-docs/snippets/trafficpolicy.md" >}} resource that enables WebSocket upgrades on the httpbin route.

   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: {{< reuse "kgw-docs/snippets/trafficpolicy-apiversion.md" >}}
   kind: {{< reuse "kgw-docs/snippets/trafficpolicy.md" >}}
   metadata:
     name: websocket-upgrade
     namespace: httpbin
   spec:
     targetRefs:
     - group: gateway.networking.k8s.io
       kind: HTTPRoute
       name: httpbin
     httpUpgrade:
     - type: websocket
   EOF
   ```

   | Field | Description |
   | ----- | ----- |
   | `httpUpgrade[].type` | The upgrade token, such as `websocket`, `CONNECT`, or `spdy/3.1`. Required, and case-insensitive. Do not list the same token twice, including variants that differ only in letter case. Up to 16 entries. |

3. Send an upgrade request to the httpbin route. Because the sample httpbin app does not implement WebSocket, the connection times out instead of completing a `101 Switching Protocols` handshake. 
   {{< tabs >}}
   {{% tab name="Cloud Provider LoadBalancer" %}}
   ```sh
   curl -v --max-time 5 \
     -H "Host: www.example.com" \
     -H "Connection: Upgrade" \
     -H "Upgrade: websocket" \
     -H "Sec-WebSocket-Version: 13" \
     -H "Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==" \
     http://$INGRESS_GW_ADDRESS:8080/get
   ```
   {{% /tab %}}
   {{% tab name="Port-forward for local testing" %}}
   ```sh
   curl -v --max-time 5 \
     -H "Host: www.example.com" \
     -H "Connection: Upgrade" \
     -H "Upgrade: websocket" \
     -H "Sec-WebSocket-Version: 13" \
     -H "Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==" \
     http://localhost:8080/get
   ```
   {{% /tab %}}
   {{< /tabs >}}

   Example output:

   ```console
   * Request completely sent off
   * Operation timed out after 5001 milliseconds with 0 bytes received
   ```

4. Delete the {{< reuse "kgw-docs/snippets/trafficpolicy.md" >}}, and send the same request again. Verify that this time, the gateway proxy rejects the request with a 403 HTTP response, because neither the gateway proxy nor the route accept WebSocket upgrades. 

   ```sh
   kubectl delete {{< reuse "kgw-docs/snippets/trafficpolicy.md" >}} websocket-upgrade -n httpbin
   ```

   {{< tabs >}}
   {{% tab name="Cloud Provider LoadBalancer" %}}
   ```sh
   curl -v --max-time 5 \
     -H "Host: www.example.com" \
     -H "Connection: Upgrade" \
     -H "Upgrade: websocket" \
     -H "Sec-WebSocket-Version: 13" \
     -H "Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==" \
     http://$INGRESS_GW_ADDRESS:8080/get
   ```
   {{% /tab %}}
   {{% tab name="Port-forward for local testing" %}}
   ```sh
   curl -v --max-time 5 \
     -H "Host: www.example.com" \
     -H "Connection: Upgrade" \
     -H "Upgrade: websocket" \
     -H "Sec-WebSocket-Version: 13" \
     -H "Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==" \
     http://localhost:8080/get
   ```
   {{% /tab %}}
   {{< /tabs >}}

   Example output:

   ```console
   < HTTP/1.1 403 Forbidden
   < content-length: 0
   < server: envoy
   < connection: close
   ```

## Terminate CONNECT requests on a route {#connect-termination}

Use the {{< reuse "kgw-docs/snippets/trafficpolicy.md" >}} resource to allow incoming `CONNECT` upgrades for a specific route and to terminate them at the gateway proxy. When the gateway proxy terminates a `CONNECT` request, the proxy responds to the client. Then, the proxy forwards the client's subsequent bytes, an ordinary HTTP request, as a separate connection to the backend.

> [!NOTE]
> `CONNECT` upgrades must be configured with the {{< reuse "kgw-docs/snippets/trafficpolicy.md" >}} resource. You cannot use a ListenerPolicy to configure `CONNECT` upgrades for a gateway listener. 

1. Create an HTTPRoute for `CONNECT` requests. A `CONNECT` request carries a host and port instead of a path, so it matches a route rule only if the rule matches on `method: CONNECT` without a path.

   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.networking.k8s.io/v1
   kind: HTTPRoute
   metadata:
     name: httpbin-connect
     namespace: httpbin
   spec:
     parentRefs:
     - name: http
       namespace: {{< reuse "kgw-docs/snippets/namespace.md" >}}
     hostnames:
     - connect.example
     rules:
     - name: connect
       matches:
       - method: CONNECT
       backendRefs:
       - name: httpbin
         port: 8000
   EOF
   ```

2. Create a {{< reuse "kgw-docs/snippets/trafficpolicy.md" >}} that terminates `CONNECT` requests on that HTTPRoute rule.

   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: {{< reuse "kgw-docs/snippets/trafficpolicy-apiversion.md" >}}
   kind: {{< reuse "kgw-docs/snippets/trafficpolicy.md" >}}
   metadata:
     name: connect-termination
     namespace: httpbin
   spec:
     targetRefs:
     - group: gateway.networking.k8s.io
       kind: HTTPRoute
       name: httpbin-connect
       sectionName: connect
     httpUpgrade:
     - type: CONNECT
       connect:
         terminate: true
   EOF
   ```

   | Field | Description |
   | ----- | ----- |
   | `targetRefs[].sectionName` | The name of the HTTPRoute rule to apply the policy to. |
   | `httpUpgrade[].connect.terminate` | Terminates the `CONNECT` request at the gateway proxy and forwards the payload to the backend as raw TCP data. When omitted or `false`, the gateway proxy forwards the `CONNECT` request to the backend without terminating it. Valid only when `type` is `CONNECT`. |

3. Send a request through the tunnel. The `-p` and `-x` options open a `CONNECT` tunnel between curl and the gateway proxy. The proxy terminates the `CONNECT` request and forwards the client's subsequent bytes, an ordinary HTTP request, to the httpbin app as a separate connection.

   Verify that you see two `200 OK` responses in the output. The first response is the gateway proxy accepting the `CONNECT` request and establishing the tunnel. The second is the httpbin app responding to the `GET /headers` request that curl sent over that tunnel.

   {{< tabs >}}
   {{% tab name="Cloud Provider LoadBalancer" %}}
   ```sh
   curl -v -p -x http://$INGRESS_GW_ADDRESS:8080 http://connect.example:8000/headers
   ```
   {{% /tab %}}
   {{% tab name="Port-forward for local testing" %}}
   ```sh
   curl -v -p -x http://localhost:8080 http://connect.example:8000/headers
   ```
   {{% /tab %}}
   {{< /tabs >}}

   Example output: 
   ```console {hl_lines=[4,5,6,7]}
   < HTTP/1.1 200 OK
   < server: envoy
   < 
   * CONNECT phase completed
   * CONNECT tunnel established, response 200
   > GET /headers HTTP/1.1
   > Host: connect.example:8000
   > User-Agent: curl/8.7.1
   > Accept: */*
   > 
   * Request completely sent off
   < HTTP/1.1 200 OK
   < Access-Control-Allow-Credentials: true
   < Access-Control-Allow-Origin: *
   < Content-Type: application/json; encoding=utf-8
   < Content-Length: 153
   < 
   {
     "headers": {
       "Accept": [
        "*/*"
       ],
       "Host": [
         "connect.example:8000"
       ],
       "User-Agent": [
         "curl/8.7.1"
       ]
     }
   }
   ```

4. Remove the `terminate` setting, and send the same request again. Without termination, the gateway proxy forwards the raw `CONNECT` request to httpbin instead of terminating it. The httpbin app is a plain HTTP server with no `CONNECT` support, so the request fails.

   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: {{< reuse "kgw-docs/snippets/trafficpolicy-apiversion.md" >}}
   kind: {{< reuse "kgw-docs/snippets/trafficpolicy.md" >}}
   metadata:
     name: connect-termination
     namespace: httpbin
   spec:
     targetRefs:
     - group: gateway.networking.k8s.io
       kind: HTTPRoute
       name: httpbin-connect
       sectionName: connect
     httpUpgrade:
     - type: CONNECT
   EOF
   ```

   {{< tabs >}}
   {{% tab name="Cloud Provider LoadBalancer" %}}
   ```sh
   curl -v -p -x http://$INGRESS_GW_ADDRESS:8080 http://connect.example:8000/headers
   ```
   {{% /tab %}}
   {{% tab name="Port-forward for local testing" %}}
   ```sh
   curl -v -p -x http://localhost:8080 http://connect.example:8000/headers
   ```
   {{% /tab %}}
   {{< /tabs >}}

   Example output: 
   ```console
   < HTTP/1.1 404 Not Found
   < access-control-allow-credentials: true
   < access-control-allow-origin: *
   < content-type: text/plain; charset=utf-8
   < x-content-type-options: nosniff
   < content-length: 19
   < server: envoy
   < connection: close
   < 
   * CONNECT tunnel failed, response 404
   * Closing connection
   curl: (56) CONNECT tunnel failed, response 404
   ```

## Cleanup

{{< reuse "kgw-docs/snippets/cleanup.md" >}}

```sh
kubectl delete listenerpolicy enable-upgrades -n {{< reuse "kgw-docs/snippets/namespace.md" >}} --ignore-not-found
kubectl delete {{< reuse "kgw-docs/snippets/trafficpolicy.md" >}} websocket-upgrade connect-termination -n httpbin --ignore-not-found
kubectl delete httproute httpbin-connect -n httpbin --ignore-not-found
```
