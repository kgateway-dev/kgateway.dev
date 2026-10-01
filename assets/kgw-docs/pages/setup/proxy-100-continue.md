Forward `Expect: 100-continue` requests to the backend so that the backend decides whether to accept the request body.

## About 100-continue {#about}

A client that is about to send a large request body can first send the request headers with an `Expect: 100-continue` header. The client then waits for a `100 Continue` response before it sends the body. Then the server can reject the request before the client uploads the body because the client is not authorized or the body is too large.

By default, the gateway proxy handles this exchange itself. The gateway proxy removes the `Expect` header, immediately returns `100 Continue` to the client, and forwards the request without the header. As a result, the backend cannot reject the request before the client sends the body.

To let the backend make that decision, set the `proxy100Continue` field in a ListenerPolicy. The gateway proxy then forwards the `Expect: 100-continue` header to the backend, and passes the `100 Continue` response from the backend back to the client.

## Before you begin

{{< reuse "kgw-docs/snippets/prereq.md" >}}

## Forward 100-continue requests {#forward}

1. Send a request with an `Expect: 100-continue` header to the httpbin app. The httpbin app returns the request headers that it received in the response body.

   {{< tabs >}}
   {{% tab name="Cloud Provider LoadBalancer" %}}
   ```sh
   curl -v -X POST http://$INGRESS_GW_ADDRESS:8080/anything \
     -H "host: www.example.com" \
     -H "Expect: 100-continue" \
     --data-binary 'hello'
   ```
   {{% /tab %}}
   {{% tab name="Port-forward for local testing" %}}
   ```sh
   curl -v -X POST localhost:8080/anything \
     -H "host: www.example.com" \
     -H "Expect: 100-continue" \
     --data-binary 'hello'
   ```
   {{% /tab %}}
   {{< /tabs >}}

   In the output, the gateway proxy returns `100 Continue`. The `headers` in the response body do not include an `Expect` header, because the gateway proxy removed the header before it forwarded the request.

   ```console
   < HTTP/1.1 100 Continue
   < HTTP/1.1 200 OK
   ...
   ```

2. Create a ListenerPolicy with the `proxy100Continue` field. In the `targetRefs`, attach the policy to the Gateway that you want to forward 100-continue requests for.

   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.kgateway.dev/v1alpha1
   kind: ListenerPolicy
   metadata:
     name: proxy-100-continue
     namespace: {{< reuse "kgw-docs/snippets/namespace.md" >}}
   spec:
     targetRefs:
     - group: gateway.networking.k8s.io
       kind: Gateway
       name: http
     default:
       httpSettings:
         proxy100Continue: true
   EOF
   ```

3. Send the same request again.

   {{< tabs >}}
   {{% tab name="Cloud Provider LoadBalancer" %}}
   ```sh
   curl -v -X POST http://$INGRESS_GW_ADDRESS:8080/anything \
     -H "host: www.example.com" \
     -H "Expect: 100-continue" \
     --data-binary 'hello'
   ```
   {{% /tab %}}
   {{% tab name="Port-forward for local testing" %}}
   ```sh
   curl -v -X POST localhost:8080/anything \
     -H "host: www.example.com" \
     -H "Expect: 100-continue" \
     --data-binary 'hello'
   ```
   {{% /tab %}}
   {{< /tabs >}}

   This time, the `headers` in the response body include the `Expect` header, which means that the gateway proxy forwarded the header to httpbin. The `100 Continue` response now comes from httpbin.

   ```console
   < HTTP/1.1 100 Continue
   < HTTP/1.1 200 OK
   ...
   {
     ...
     "headers": {
       ...
       "Expect": [
         "100-continue"
       ],
       ...
     }
   }
   ```

4. Optional: Check the setting in the Envoy configuration of the gateway proxy.
   1. Port-forward the gateway proxy on port 19000 to open the Envoy admin interface.
      ```sh
      kubectl port-forward deploy/http -n {{< reuse "kgw-docs/snippets/namespace.md" >}} 19000
      ```

   2. Verify that the `proxy_100_continue` field is set to `true` in the HTTP connection manager.
      ```sh
      curl -s localhost:19000/config_dump | grep proxy_100_continue
      ```

      Example output:
      ```console
            "proxy_100_continue": true,
      ```

## Cleanup

{{< reuse "kgw-docs/snippets/cleanup.md" >}}

```sh
kubectl delete listenerpolicy proxy-100-continue -n {{< reuse "kgw-docs/snippets/namespace.md" >}}
```
