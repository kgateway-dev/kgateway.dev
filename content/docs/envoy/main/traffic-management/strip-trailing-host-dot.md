---
title: Strip trailing dots from hostnames
description: Strip a trailing dot from Host and authority headers so that fully qualified domain name requests match routes without dotted hostnames.
weight: 20
---

## About trailing host dots {#about-trailing-host-dots}

Some clients send a fully qualified domain name (FQDN) with a trailing dot in the `Host` or `:authority` header, such as `www.example.com.`. Gateway API hostnames cannot include the trailing dot, so an HTTPRoute with `www.example.com` does not match the dotted request by default. The gateway proxy returns a `404` response with the `NR` response flag because no route matches the request.

Use a ListenerPolicy to set `spec.default.httpSettings.stripTrailingHostDot` to `true`. The gateway proxy strips the trailing dot before filter processing and route matching, and forwards the stripped host value upstream. If you omit the field or set it to `false`, the gateway proxy keeps the trailing dot.

## Before you begin {#before-you-begin}

{{< reuse "kgw-docs/snippets/prereq.md" >}}

## Strip trailing dots before route matching {#strip-trailing-dots-before-route-matching}

Configure a route hostname without a trailing dot, and attach a ListenerPolicy to the Gateway that serves the route. The policy applies to all HTTP and HTTPS listeners on the Gateway.

1. Create an HTTPRoute for `www.example.com`, and create a ListenerPolicy that strips trailing dots from hostnames.

   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.networking.k8s.io/v1
   kind: HTTPRoute
   metadata:
     name: strip-trailing-host-dot
     namespace: httpbin
   spec:
     parentRefs:
     - name: http
       namespace: {{< reuse "kgw-docs/snippets/namespace.md" >}}
     hostnames:
     - "www.example.com"
     rules:
     - backendRefs:
       - name: httpbin
         port: 8000
   ---
   apiVersion: gateway.kgateway.dev/v1alpha1
   kind: ListenerPolicy
   metadata:
     name: strip-trailing-host-dot
     namespace: {{< reuse "kgw-docs/snippets/namespace.md" >}}
   spec:
     targetRefs:
     - group: gateway.networking.k8s.io
       kind: Gateway
       name: http
     default:
       httpSettings:
         stripTrailingHostDot: true
   EOF
   ```

   {{< reuse "kgw-docs/snippets/review-table.md" >}}

   | Field | Description |
   | ----- | ----------- |
   | `spec.targetRefs` | Attaches the ListenerPolicy to the `http` Gateway. The policy applies to all HTTP and HTTPS listeners on that Gateway. |
   | `spec.default.httpSettings.stripTrailingHostDot` | Set to `true` to strip one trailing dot from the `Host` or `:authority` header before filter processing and route matching. The stripped value is also forwarded upstream. Omit the field or set it to `false` to keep the trailing dot. |

2. Port-forward the gateway proxy on port 19000, and verify that the Envoy HTTP connection manager strips trailing host dots.

   ```sh
   kubectl port-forward deploy/http -n {{< reuse "kgw-docs/snippets/namespace.md" >}} 19000 &
   PF_PID=$!

   sleep 2

   curl -s localhost:19000/config_dump | jq '
     .configs[]
     | select(.["@type"] == "type.googleapis.com/envoy.admin.v3.ListenersConfigDump")
     | .dynamic_listeners[]
     | .active_state.listener.filter_chains[].filters[]
     | select(.name == "envoy.filters.network.http_connection_manager")
     | .typed_config
     | {strip_trailing_host_dot}
   '

   kill $PF_PID
   ```

   Example output:

   ```console
   {
     "strip_trailing_host_dot": true
   }
   ```

3. Send a request whose `Host` header has a trailing dot. The request matches the HTTPRoute hostname `www.example.com`.

   {{< tabs >}}
   {{% tab name="Cloud Provider LoadBalancer" %}}
   ```sh
   curl -i http://$INGRESS_GW_ADDRESS:8080/headers -H "host: www.example.com."
   ```
   {{% /tab %}}
   {{% tab name="Port-forward for local testing" %}}
   ```sh
   curl -i localhost:8080/headers -H "host: www.example.com."
   ```
   {{% /tab %}}
   {{< /tabs >}}

   Example output:

   ```console
   HTTP/1.1 200 OK
   ```

## Cleanup {#cleanup}

{{< reuse "kgw-docs/snippets/cleanup.md" >}}

```sh
kubectl delete httproute strip-trailing-host-dot -n httpbin --ignore-not-found
kubectl delete listenerpolicy strip-trailing-host-dot -n {{< reuse "kgw-docs/snippets/namespace.md" >}} --ignore-not-found
```
