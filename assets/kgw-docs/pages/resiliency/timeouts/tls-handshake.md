Set a timeout for TLS handshake completion to protect the gateway from clients that open connections but never finish the handshake.

## About the TLS handshake timeout

After a client opens a TCP connection to the gateway, the TLS handshake must complete before the connection can carry application traffic. If a client opens a connection and never finishes the handshake, the gateway keeps the connection open indefinitely, which consumes compute resources. To set a deadline for the handshake completion, set the `transportSocketConnectTimeout` field in a ListenerPolicy resource. If the timeout is reached, Envoy closes the connection. The timeout applies to every filter chain on the matched listener.

## Before you begin

{{< reuse "kgw-docs/snippets/prereq.md" >}}

## Set up the TLS handshake timeout

1. Create a ListenerPolicy with your TLS handshake timeout. In this example, you set a 10-second deadline for clients to complete the TLS handshake.

   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.kgateway.dev/v1alpha1
   kind: ListenerPolicy
   metadata:
     name: tls-handshake-timeout
     namespace: {{< reuse "kgw-docs/snippets/namespace.md" >}}
   spec:
     targetRefs:
     - group: gateway.networking.k8s.io
       kind: Gateway
       name: http
     default:
       transportSocketConnectTimeout: 10s
   EOF
   ```

2. Port-forward the gateway proxy and query the config dump to verify that `transport_socket_connect_timeout` is set on every filter chain.

   ```sh
   kubectl port-forward deployment/http -n {{< reuse "kgw-docs/snippets/namespace.md" >}} 19000:19000 &
   PF_PID=$!
   sleep 2
   curl -s 127.0.0.1:19000/config_dump | \
   jq '.configs[]
     | select(.["@type"] == "type.googleapis.com/envoy.admin.v3.ListenersConfigDump")
     | .dynamic_listeners[].active_state.listener
     | select(.name | startswith("listener~"))
     | {name, filter_chains: [.filter_chains[]
         | {transport_socket_connect_timeout}]}'
   kill $PF_PID
   ```

   Example output:

   ```console
   {
     "name": "listener~8080",
     "filter_chains": [
       {
         "transport_socket_connect_timeout": "10s"
       }
     ]
   }
   ```

## Cleanup

{{< reuse "kgw-docs/snippets/cleanup.md" >}}

```sh
kubectl delete listenerpolicy tls-handshake-timeout -n {{< reuse "kgw-docs/snippets/namespace.md" >}}
```
