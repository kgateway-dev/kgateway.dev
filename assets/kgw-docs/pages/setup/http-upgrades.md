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

Use a {{< reuse "kgw-docs/snippets/trafficpolicy.md" >}} when an upgrade applies to particular routes rather than to the whole listener or when you need to terminate `CONNECT`.

1. Create a {{< reuse "kgw-docs/snippets/trafficpolicy.md" >}} with the `httpUpgrade` list.

   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.kgateway.dev/v1alpha1
   kind: TrafficPolicy
   metadata:
     name: tunnel-connect
     namespace: {{< reuse "kgw-docs/snippets/namespace.md" >}}
   spec:
     targetRefs:
     - group: gateway.networking.k8s.io
       kind: HTTPRoute
       name: httpbin
     httpUpgrade:
     - type: websocket
     - type: CONNECT
       connect:
         terminate: true
   EOF
   ```

   | Field | Description |
   | ----- | ----- |
   | `httpUpgrade[].type` | The upgrade token, such as `websocket`, `CONNECT`, or `spdy/3.1`. Required, and case-insensitive. Do not list the same token twice, including variants that differ only in letter case. Up to 16 entries. |
   | `httpUpgrade[].connect.terminate` | Terminates the `CONNECT` request at the gateway and forwards the payload upstream as raw TCP data. When omitted or `false`, the request is proxied upstream without termination. Valid only when `type` is `CONNECT`. |

2. Send an upgrade request and confirm that the gateway accepts it.

   ```sh
   curl -i http://$INGRESS_GW_ADDRESS:8080/ -H "host: www.example.com" \
     -H "Connection: Upgrade" -H "Upgrade: websocket"
   ```

   Example output, where `101` shows that the protocol was switched:

   ```console
   HTTP/1.1 101 Switching Protocols
   upgrade: websocket
   connection: Upgrade
   ```

## Considerations

- **`CONNECT` termination is per route.** It cannot be set on a listener, so it always needs a {{< reuse "kgw-docs/snippets/trafficpolicy.md" >}}.
- **Terminating `CONNECT` forwards raw bytes.** If you configure TLS for the selected backend, those bytes are wrapped in a separate upstream TLS session. Leave backend TLS disabled when the payload must reach the upstream unchanged.
- **Do not combine upgrades with request buffering.** Buffering a request that becomes a long-lived tunnel holds the payload in memory.

## Cleanup

{{< reuse "kgw-docs/snippets/cleanup.md" >}}

```sh
kubectl delete listenerpolicy enable-upgrades -n {{< reuse "kgw-docs/snippets/namespace.md" >}}
kubectl delete trafficpolicy tunnel-connect -n {{< reuse "kgw-docs/snippets/namespace.md" >}}
```
