Allow WebSocket, CONNECT, and other HTTP protocol upgrades through your gateway proxy.

## About HTTP protocol upgrades

An HTTP upgrade lets a client switch an ordinary HTTP request onto another protocol over the same connection. WebSocket is the common case, and `CONNECT` is used to tunnel arbitrary traffic through a proxy.

Gateway proxies reject upgrade requests unless the upgrade token is enabled, so enabling an upgrade is a deliberate choice rather than a default. Two resources take part:

| Resource | Field | What it does |
| -------- | ----- | ------------ |
| ListenerPolicy | `spec.default.httpSettings.upgradeConfig.enabledUpgrades` | Lists the upgrade tokens the listener accepts. Needs at least one entry. |
| {{< reuse "kgw-docs/snippets/trafficpolicy.md" >}} | `spec.httpUpgrade` | Configures upgrades for the Gateway, HTTPRoute, or ListenerSet that the policy targets, and is the only place `CONNECT` termination can be set. |

> [!WARNING]
> **After an upgrade is established, the tunneled payload is not inspected by HTTP filters.** Authenticate and authorize the initial upgrade request, enable upgrades only for clients you trust, and do not enable request buffering on a route that carries upgrades.

## Before you begin

{{< reuse "kgw-docs/snippets/prereq-listeners.md" >}}

## Enable an upgrade on a listener

1. Create a ListenerPolicy that lists the upgrade tokens to accept. In the `targetRefs`, attach the policy to the Gateway that serves the traffic.

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

2. Port-forward the gateway proxy on port 19000 to open the Envoy admin interface.

   ```sh
   kubectl port-forward deploy/http -n {{< reuse "kgw-docs/snippets/namespace.md" >}} 19000
   ```

3. Check the filter chain for the upgrade configuration.

   ```sh
   curl -s localhost:19000/config_dump | jq '[.. | objects | select(has("upgrade_configs")) | {upgrade_configs}]'
   ```

   Example output:

   ```console
   "upgrade_configs": [
     {
       "upgrade_type": "websocket"
     }
   ]
   ```

## Configure upgrades for a route {#traffic-policy}

Use a {{< reuse "kgw-docs/snippets/trafficpolicy.md" >}} when an upgrade applies to particular routes rather than to the whole listener or when you need to terminate `CONNECT`. For each upgrade type, the route-level setting takes precedence over the listener-level setting. As a result, a route can accept an upgrade that the listener does not list in `enabledUpgrades`.

The {{< reuse "kgw-docs/snippets/trafficpolicy.md" >}} must be in the same namespace as the route that it targets, and must target a Gateway, HTTPRoute, or ListenerSet.

### Enable WebSocket on a route {#websocket-route}

1. Create a {{< reuse "kgw-docs/snippets/trafficpolicy.md" >}} that enables WebSocket upgrades on the httpbin route.

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

2. Check the route configuration for the upgrade. If you closed the port-forward from the previous section, port-forward the gateway proxy on port 19000 again.

   ```sh
   curl -s localhost:19000/config_dump | jq '[.. | objects | select(has("cluster") and has("upgrade_configs")) | .upgrade_configs]'
   ```

   Example output:

   ```console
   [
     [
       {
         "upgrade_type": "websocket"
       }
     ]
   ]
   ```

   The sample httpbin app does not serve WebSocket connections. To test the upgrade end to end, route the traffic to a backend that accepts WebSocket connections, and send an upgrade request with a WebSocket client.

### Terminate CONNECT on a route {#connect-termination}

When the gateway proxy terminates a `CONNECT` request, the proxy responds to the client, and forwards everything that the client sends afterward to the backend as raw TCP data.

1. Create an HTTPRoute for `CONNECT` requests. A `CONNECT` request carries a host and port instead of a path, so it matches a route rule only if the rule matches on `method: CONNECT` without a path. A rule that also sets a non-default path stays a method and path match, which applies to Extended CONNECT requests such as WebSocket over HTTP/2 instead.

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

2. Create a {{< reuse "kgw-docs/snippets/trafficpolicy.md" >}} that terminates `CONNECT` on that rule.

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

3. Send a request through the tunnel. The `-p` and `-x` options make curl open a `CONNECT` tunnel through the gateway proxy, and then send an ordinary HTTP request to the httpbin app inside that tunnel.

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

   Example output: The first response is the gateway proxy accepting the `CONNECT` request. The second response comes from the httpbin app, through the tunnel.

   ```console
   > CONNECT connect.example:8000 HTTP/1.1
   > Host: connect.example:8000
   ...
   < HTTP/1.1 200 OK
   ...
   * CONNECT tunnel established, response 200
   > GET /headers HTTP/1.1
   > Host: connect.example:8000
   ...
   < HTTP/1.1 200 OK
   ```

## Considerations

- **`CONNECT` termination is per route.** You cannot configure `CONNECT` termination on a listener, so it always needs a {{< reuse "kgw-docs/snippets/trafficpolicy.md" >}}.
- **Terminating `CONNECT` forwards raw bytes.** If you configure TLS for the selected backend, those bytes are wrapped in a separate upstream TLS session. Leave backend TLS disabled when the payload must reach the backend unchanged.
- **You cannot combine upgrades with request buffering.** A {{< reuse "kgw-docs/snippets/trafficpolicy.md" >}} that sets both `httpUpgrade` and `buffer` is rejected, unless the `buffer` setting disables buffering.
- **WebSocket over HTTP/2 needs a listener setting.** Clients such as Firefox open WebSocket connections over HTTP/2 with Extended CONNECT, which the listener rejects by default. For more information, see [WebSocket over HTTP/2]({{< link-hextra path="/traffic-management/http2-downstream/#allow-connect" >}}).

## Cleanup

{{< reuse "kgw-docs/snippets/cleanup.md" >}}

```sh
kubectl delete listenerpolicy enable-upgrades -n {{< reuse "kgw-docs/snippets/namespace.md" >}}
kubectl delete {{< reuse "kgw-docs/snippets/trafficpolicy.md" >}} websocket-upgrade connect-termination -n httpbin
kubectl delete httproute httpbin-connect -n httpbin
```
