Fine-tune connection speeds for read and write operations by setting a connection buffer limit. 

## About read and write buffer limits

By default, {{< reuse "/kgw-docs/snippets/kgateway.md" >}} is set up with 1MiB of request read and write buffer for each gateway. For large requests that must be buffered and that exceed the default buffer limit, {{< reuse "/kgw-docs/snippets/kgateway.md" >}} either disconnects the connection to the downstream service if headers were already sent, or returns a 413 HTTP response code. To make sure that large requests can be sent and received, you can specify the maximum number of bytes that can be buffered between the gateway and the downstream service. Alternatively, when using {{< reuse "/kgw-docs/snippets/kgateway.md" >}} as an edge proxy, configuring the buffer limit can be important when dealing with untrusted downstreams. By setting the limit to a small number, such as 32KiB, you can better guard against potential attacks or misconfigured downstreams that could excessively use the proxy's resources.

The connection buffer limit can be configured on the Gateway level{{< version exclude-if="2.0.x" >}} or on an individual route{{< /version >}}. 

## Considerations when using httpbin

When you use the httpbin sample app, keep in mind that httpbin limits the maximum body size to 1 mebibyte (1Mi). If you send a request to httpbin with a body size that is larger than that, httpbin automatically rejects the request with a 400 HTTP response code. 

## Before you begin

{{< reuse "kgw-docs/snippets/prereq.md" >}}

## Set up buffer limits per gateway

Use an annotation to set a per-connection buffer limit on your Gateway, which applies the buffer limit to all routes served by the Gateway. 

1. Create a {{< reuse "/kgw-docs/snippets/trafficpolicy.md" >}} called `transformation-buffer-body` that forces buffering by transforming the response from the httpbin sample app.
   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: {{< reuse "/kgw-docs/snippets/trafficpolicy-apiversion.md" >}}
   kind: {{< reuse "/kgw-docs/snippets/trafficpolicy.md" >}}
   metadata:
     name: transformation-buffer-body
     namespace: httpbin
   spec:
     targetRefs:
     - group: gateway.networking.k8s.io
       kind: HTTPRoute
       name: httpbin
     transformation:
       response:
         body:
           parseAs: AsString
           value: '{{ body() }}'
   EOF
   ```

2. Annotate the http Gateway resource to set a buffer limit of 1 kilobytes.
   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.kgateway.dev/v1alpha1
   kind: ListenerPolicy
   metadata:
     name: bufferlimits
     namespace: kgateway-system
   spec:
     targetRefs:
     - group: gateway.networking.k8s.io
       kind: Gateway
       name: http
     default:
       perConnectionBufferLimitBytes: 1024
   EOF
   ```

3. To test the buffer limit, create a payload in a temp file that exceeds the 1Ki buffer limit.
   ```sh
   dd if=/dev/zero bs=2048 count=1 | base64 -w 0 > /tmp/large_payload_2k.txt
   ```

4. Send a request to the `/anything` httpbin path with the large payload. Verify that the request fails with a connection error or timeout, indicating that the buffer limit was exceeded.
   {{< tabs >}}
   {{% tab name="Cloud Provider LoadBalancer" %}}
   ```sh
   curl -vik -X POST http://$INGRESS_GW_ADDRESS:8080/anything \
   -H "host: www.example.com:8080" \
   -H "Content-Type: text/plain" \
   -d "{\"payload\": \"$(< /tmp/large_payload_2k.txt)\"}"
   ```
   {{% /tab %}}
   {{% tab name="Port-forward for local testing" %}}
   ```sh
   curl -vik -X POST http://localhost:8080/anything \
   -H "host: www.example.com:8080" \
   -H "Content-Type: text/plain" \
   -d "{\"payload\": \"$(< /tmp/large_payload_2k.txt)\"}"
   ```
   {{% /tab %}}
   {{< /tabs >}}
   
   Example output: 
   ```
   * upload completely sent off: 2747 bytes
   < HTTP/1.1 413 Payload Too Large
   HTTP/1.1 413 Payload Too Large
   < access-control-allow-credentials: true
   access-control-allow-credentials: true
   < access-control-allow-origin: *
   access-control-allow-origin: *
   < x-envoy-upstream-service-time: 1
   x-envoy-upstream-service-time: 1
   < content-length: 17
   content-length: 17
   < server: envoy
   server: envoy
   ```

5. Test the buffer limit again by sending a request with a small payload, `"hello world"`. This request succeeds with a normal response from httpbin because the payload size is within the 1Ki limit.
   {{< tabs >}}
   {{% tab name="Cloud Provider LoadBalancer" %}}
   ```sh
   curl -vik -X POST http://$INGRESS_GW_ADDRESS:8080/anything \
      -H "host: www.example.com:8080" \
      -H "Content-Type: application/json" \
      -d "{\"payload\":  \"hello world\"}" 
   ```
   {{% /tab %}}
   {{% tab name="Port-forward for local testing" %}}
   ```sh
   curl -vik -X POST http://localhost:8080/anything \
      -H "host: www.example.com:8080" \
      -H "Content-Type: application/json" \
      -d "{\"payload\":  \"hello world\"}" 
   ```
   {{% /tab %}}
   {{< /tabs >}}

   Example output:

   ```json
   * upload completely sent off: 27 bytes
   < HTTP/1.1 200 OK
   HTTP/1.1 200 OK
   ...
     "url": "http://www.example.com:8080/anything",
     "data": "{\"payload\":  \"hello world\"}",
     "files": null,
     "form": null,
     "json": {
       "payload": "hello world"
     }
   }
   ```

## Set up buffer limits per route

You can configure connection buffer limits using a {{< reuse "/kgw-docs/snippets/trafficpolicy.md" >}} to control how much data can be buffered per connection at the level of individual routes. This can provide more fine-grained control than applying the buffer limit at the Gateway, or can provide a method of overriding a buffer limit at the level of the Gateway.

1. If you did not already, create a {{< reuse "/kgw-docs/snippets/trafficpolicy.md" >}} called `transformation-buffer-body` that forces buffering by transforming the response from the httpbin sample app.
   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: {{< reuse "/kgw-docs/snippets/trafficpolicy-apiversion.md" >}}
   kind: {{< reuse "/kgw-docs/snippets/trafficpolicy.md" >}}
   metadata:
     name: transformation-buffer-body
     namespace: httpbin
   spec:
     targetRefs:
     - group: gateway.networking.k8s.io
       kind: HTTPRoute
       name: httpbin
     transformation:
       response:
         body:
           parseAs: AsString
           value: '{{ body() }}'
   EOF
   ```

2. If you previously created the ListenerPolicy, remove it. 
   ```sh
   kubectl delete listenerpolicy bufferlimits -n {{< reuse "/kgw-docs/snippets/namespace.md" >}} 
   ``` 
   
3. In a separate {{< reuse "/kgw-docs/snippets/trafficpolicy.md" >}}, apply a buffer limit of `maxRequestSize: '1024'` to the httpbin app. This setting limits the request payload to 1024 bytes.
   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: {{< reuse "/kgw-docs/snippets/trafficpolicy-apiversion.md" >}}
   kind: {{< reuse "/kgw-docs/snippets/trafficpolicy.md" >}}
   metadata:
     name: transformation-buffer-limit
     namespace: httpbin
   spec:
     targetRefs:
     - group: gateway.networking.k8s.io
       kind: HTTPRoute
       name: httpbin
     buffer:
       maxRequestSize: '1024'
   EOF
   ```

4. To test the buffer limit, create a payload in a temp file that exceeds the 1Ki buffer limit.
   ```sh
   dd if=/dev/zero bs=2048 count=1 | base64 -w 0 > /tmp/large_payload_2k.txt
   ```

5. Send a request to the `/anything` httpbin path with the large payload. Verify that the request fails with a connection error or timeout, indicating that the buffer limit was exceeded.
   {{< tabs >}}
   {{% tab name="Cloud Provider LoadBalancer" %}}
   ```sh
   curl -vik -X POST http://$INGRESS_GW_ADDRESS:8080/anything \
   -H "host: www.example.com:8080" \
   -H "Content-Type: text/plain" \
   -d "{\"payload\": \"$(< /tmp/large_payload_2k.txt)\"}"
   ```
   {{% /tab %}}
   {{% tab name="Port-forward for local testing" %}}
   ```sh
   curl -vik -X POST http://localhost:8080/anything \
   -H "host: www.example.com:8080" \
   -H "Content-Type: text/plain" \
   -d "{\"payload\": \"$(< /tmp/large_payload_2k.txt)\"}"
   ```
   {{% /tab %}}
   {{< /tabs >}}

5. Test the buffer limit again by sending a request with a small payload, `"hello world"`. This request succeeds with a normal response from httpbin because the payload size is within the 2Ki limit.
   {{< tabs >}}
   {{% tab name="Cloud Provider LoadBalancer" %}}
   ```sh
   curl -vik -X POST http://$INGRESS_GW_ADDRESS:8080/anything \
      -H "host: www.example.com:8080" \
      -H "Content-Type: application/json" \
      -d "{\"payload\":  \"hello world\"}" 
   ```
   {{% /tab %}}
   {{% tab name="Port-forward for local testing" %}}
   ```sh
   curl -vik -X POST http://localhost:8080/anything \
      -H "host: www.example.com:8080" \
      -H "Content-Type: application/json" \
      -d "{\"payload\":  \"hello world\"}" 
   ```
   {{% /tab %}}
   {{< /tabs >}}


   Example output:

   ```json
   {
     "args": {},
     "data": "{\"payload\": \"hello world\"}",
     "files": {},
     "form": {},
     "headers": {
       ...
     },
     "json": {
       "payload": "hello world"
     },
     "method": "POST",
     "origin": "...",
     "url": "https://$INGRESS_GW_ADDRESS:8080/anything"
   }
   ```

{{< version exclude-if="2.1.x,2.2.x,2.3.x,2.4.x" >}}

## Move the buffer filter before body-reading filters

By default, the buffer filter runs late in the HTTP filter chain, after authentication, authorization, and rate limiting. Another filter can read or hold the body first, such as ExtAuth with request-body checks, ExtProc, or a body transformation. In that case, `buffer.maxRequestSize` might not reject an oversized request. Set `buffer.filterStage` to move the buffer filter earlier for the listener that serves the route.

Because {{< reuse "/kgw-docs/snippets/kgateway.md" >}} installs one buffer filter per filter chain, this placement applies to every route on the listener. If {{< reuse "/kgw-docs/snippets/trafficpolicy.md" >}} resources on the same filter chain ask for different stages, the earliest requested stage is used for the whole filter chain.

1. Update the route-level {{< reuse "/kgw-docs/snippets/trafficpolicy.md" >}} to place the buffer filter before the `AuthN` stage.
   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: {{< reuse "/kgw-docs/snippets/trafficpolicy-apiversion.md" >}}
   kind: {{< reuse "/kgw-docs/snippets/trafficpolicy.md" >}}
   metadata:
     name: transformation-buffer-limit
     namespace: httpbin
   spec:
     targetRefs:
     - group: gateway.networking.k8s.io
       kind: HTTPRoute
       name: httpbin
     buffer:
       maxRequestSize: "1024"
       filterStage:
         stage: AuthN
         predicate: Before
   EOF
   ```

   | Field | Description |
   | --- | --- |
   | `buffer.maxRequestSize` | Sets the maximum request body size that the buffer filter allows. Requests that exceed this value receive a 413 HTTP response code when the buffer filter processes the body first. |
   | `buffer.filterStage.stage` | Selects the HTTP filter-chain stage for the buffer filter. Valid values are `Fault`, `AuthN`, `AuthZ`, `RateLimit`, and `Route`. |
   | `buffer.filterStage.predicate` | Places the buffer filter before, during, or after the selected stage. Valid values are `Before`, `During`, and `After`. |

2. Keep the buffer stage consistent across routes on the same listener. To use different buffer-filter placements for different routes, serve those routes from different listeners.

3. Do not set `buffer.filterStage` on a {{< reuse "/kgw-docs/snippets/trafficpolicy.md" >}} that uses `buffer.disable`. The API rejects a buffer policy that sets both fields.

4. Do not set `buffer.filterStage.weight` to a nonzero value. Because a filter chain has only one buffer filter, the API rejects a nonzero `weight`.

{{< /version >}}

## Cleanup

{{< reuse "kgw-docs/snippets/cleanup.md" >}}

```sh
kubectl delete {{< reuse "/kgw-docs/snippets/trafficpolicy.md" >}} transformation-buffer-body -n httpbin 
kubectl delete {{< reuse "/kgw-docs/snippets/trafficpolicy.md" >}} transformation-buffer-limit -n httpbin 
kubectl delete listenerpolicy bufferlimits -n {{< reuse "/kgw-docs/snippets/namespace.md" >}} 
```
