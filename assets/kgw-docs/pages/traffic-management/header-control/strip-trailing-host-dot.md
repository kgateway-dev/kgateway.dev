Some clients send a fully qualified domain name (FQDN) with a trailing dot in the `Host` or `:authority` header, such as `www.example.com.`. Gateway API hostnames cannot include the trailing dot, so an HTTPRoute with the `www.example.com` hostname does not match the trailing dot hostname by default. 

To strip the trailing dot, create a ListenerPolicy and set `spec.default.httpSettings.stripTrailingHostDot` to `true`. The gateway proxy strips the trailing dot before filter processing and route matching, and forwards the stripped host value upstream. If you omit the field or set it to `false`, the gateway proxy keeps the trailing dot.

## Before you begin

{{< reuse "kgw-docs/snippets/prereq.md" >}}

## Strip trailing dots {#strip-trailing-dots}

Attach a ListenerPolicy to the Gateway that serves the `www.example.com` route from the sample app. The policy applies to all HTTP and HTTPS listeners on the Gateway.

1. Create a ListenerPolicy that strips trailing dots from hostnames.

   ```yaml
   kubectl apply -f- <<EOF
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

2. Send a request to the httpbin app and include a `Host` header with a trailing dot. Verify that the request succeeds and that the dot is removed in the `Host` header that is returned in your CLI output.

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

   ```console {hl_lines=[14,15]}
   HTTP/1.1 200 OK
   access-control-allow-credentials: true
   access-control-allow-origin: *
   content-type: application/json; encoding=utf-8 
   x-envoy-upstream-service-time: 16
   content-length: 440
   server: envoy

   {
     "headers": {
       "Accept": [
         "*/*"
       ],
       "Host": [
         "www.example.com"
       ],
       "User-Agent": [
         "curl/8.7.1"
       ],
       "X-Envoy-Expected-Rq-Timeout-Ms": [
         "15000"
       ],
       "X-Envoy-External-Address": [
         "127.0.0.1"
       ],
       "X-Forwarded-For": [
         "10.244.0.7"
       ],
       "X-Forwarded-Proto": [
         "http"
       ],
       "X-Request-Id": [
         "6abca5b7-9028-44bb-a694-66ad86cedfe2"
       ]
     }
   }
   ```

## Cleanup

{{< reuse "kgw-docs/snippets/cleanup.md" >}}

```sh
kubectl delete listenerpolicy strip-trailing-host-dot -n {{< reuse "kgw-docs/snippets/namespace.md" >}} --ignore-not-found
```
