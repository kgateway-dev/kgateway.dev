Early request header modification allows you to add, set, or remove HTTP request headers at the listener level, before route selection and other request processing occurs.

This capability is especially useful for security and sanitization use cases, where you want to ensure that sensitive headers cannot be faked by downstream clients and are only set by trusted components such as external authentication services.

Early request header modification is configured on a `ListenerPolicy` using the `earlyRequestHeaderModifier` field. This policy is attached directly to a Gateway and applies header mutations before route selection.

The configuration uses the standard Gateway API `HTTPHeaderFilter` format and supports the following operations:

- `add`
- `set`
- `remove`

## Before you begin

{{< reuse "docs/snippets/prereq.md" >}}

## Remove a reserved header {#remove}

Remove a header that is reserved for use by another service, such as an external authentication service.

1. Send a test request to the sample httpbin app with a reserved header, such as `x-user-id`.

   {{< tabs items="Cloud Provider LoadBalancer,Port-forward for local testing" tabTotal="2" >}}
   {{% tab tabName="Cloud Provider LoadBalancer" %}}  
   ```sh
   curl -i http://$INGRESS_GW_ADDRESS:8080/headers -H "host: www.example.com:8080" -H "x-user-id: reserved-user"
   ```
   {{% /tab %}}
   {{% tab tabName="Port-forward for local testing"%}}
   ```sh
   curl -i localhost:8080/headers -H "host: www.example.com" -H "x-user-id: reserved-user"
   ```
   {{% /tab %}}
   {{< /tabs >}}

   Example output: Note that the `X-User-Id` header is present in the request.

   ```json {linenos=table,hl_lines=[27,28,29],linenostart=1}
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
         "d2076b1d-2e3e-49fb-a24f-703dbcd80665"
       ],
       "X-User-Id": [
         "reserved-user"
       ]
     }
   }
   ```

2. Create a ListenerPolicy to remove the `x-user-id` header.

   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.kgateway.dev/v1alpha1
   kind: ListenerPolicy
   metadata:
     name: remove-header
     namespace: {{< reuse "docs/snippets/namespace.md" >}}
   spec:
     targetRefs:
       - group: gateway.networking.k8s.io
         kind: Gateway
         name: http
     default:
       httpSettings:
         earlyRequestHeaderModifier:
           remove:
             - x-user-id
   EOF
   ```

   {{< reuse "docs/snippets/review-table.md" >}} For more information about the available fields, see the [API reference]({{< link-hextra path="/reference/api/#httplistenerpolicyspec" >}}).

   | Setting                    | Description                                              |
   |----------------------------|----------------------------------------------------------|
   | targetRefs                 | References the Gateway resources this policy applies to. |
   | earlyRequestHeaderModifier | Header mutations applied before route selection.         |

3. Repeat the test request to the sample httpbin app. The `x-user-id` header is no longer present in the response.

   {{< tabs items="Cloud Provider LoadBalancer,Port-forward for local testing" tabTotal="2" >}}
   {{% tab tabName="Cloud Provider LoadBalancer" %}}  
   ```sh
   curl -i http://$INGRESS_GW_ADDRESS:8080/headers -H "host: www.example.com:8080" -H "x-user-id: reserved-user"
   ```
   {{% /tab %}}
   {{% tab tabName="Port-forward for local testing"%}}
   ```sh
   curl -i localhost:8080/headers -H "host: www.example.com" -H "x-user-id: reserved-user"
   ```
   {{% /tab %}}
   {{< /tabs >}}

   Example output: Note that the `x-user-id` header is now removed.

   ```json {linenos=table,linenostart=1}
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
         "f4dcc321-d682-4874-b02f-b700854e2f6b"
       ]
     }
   }
   ```

## Cleanup

{{< reuse "docs/snippets/cleanup.md" >}}

```sh
kubectl delete listenerpolicy remove-header -n {{< reuse "docs/snippets/namespace.md" >}}
```
