Reduce response payload sizes and decompress incoming request bodies with gzip compression.

## About gzip compression

Gzip is an HTTP option that enables your gateway proxy to compress response data or decompress request data upon client request. Compression is useful in situations where large payloads need to be transmitted without compromising the response time.

Use the {{< reuse "docs/snippets/trafficpolicy.md" >}} resource to configure gzip compression and decompression per route. Choose between the following options: 

- **Response compression**: When enabled on a route, {{< reuse "docs/snippets/kgateway.md" >}} compresses HTTP responses by using gzip when the downstream client includes an `Accept-Encoding: gzip` header. The following content types are compressed by default:
  - `application/javascript`
  - `application/json`
  - `application/xhtml+xml`
  - `image/svg+xml`
  - `text/css`
  - `text/html`
  - `text/plain`
  - `text/xml`

- **Request decompression**: When enabled on a route, {{< reuse "docs/snippets/kgateway.md" >}} decompresses gzip-encoded request bodies before forwarding them to the backend service.

For more information about how Envoy handles compression, see the [Envoy compressor filter docs](https://www.envoyproxy.io/docs/envoy/latest/configuration/http/http_filters/compressor_filter).

## Before you begin

{{< reuse "docs/snippets/prereq.md" >}}

## Response compression {#response-compression}

Enable gzip compression on a route so that {{< reuse "docs/snippets/kgateway.md" >}} compresses responses for clients that support it.

1. Create an HTTPRoute that routes requests from the `compression.example` domain to the httpbin sample app.
   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.networking.k8s.io/v1
   kind: HTTPRoute
   metadata:
     name: httpbin-compression
     namespace: httpbin
   spec:
     parentRefs:
     - name: http
       namespace: {{< reuse "docs/snippets/namespace.md" >}}
     hostnames:
       - compression.example
     rules:
       - backendRefs:
           - name: httpbin
             port: 8000
   EOF
   ```

2. Create a {{< reuse "docs/snippets/trafficpolicy.md" >}} that enables response compression on the route.
   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: {{< reuse "docs/snippets/trafficpolicy-apiversion.md" >}}
   kind: {{< reuse "docs/snippets/trafficpolicy.md" >}}
   metadata:
     name: response-compression
     namespace: httpbin
   spec:
     targetRefs:
     - group: gateway.networking.k8s.io
       kind: HTTPRoute
       name: httpbin-compression
     compression:
       responseCompression: {}
   EOF
   ```

   | Setting | Description |
   |--|--|
   | `spec.targetRefs` | The HTTPRoute to apply this policy to. |
   | `spec.compression.responseCompression` | Enables gzip response compression. Responses are only compressed when the client sends an `Accept-Encoding: gzip` header and the response content type matches one of the supported types. |

3. Send a request to the `/html` httpbin path with the `Accept-Encoding: gzip` header. Verify that the response includes a `content-encoding: gzip` header, indicating that the response body is compressed.
   {{< tabs tabTotal="2" items="Cloud Provider LoadBalancer,Port-forward for local testing" >}}
   {{% tab tabName="Cloud Provider LoadBalancer" %}}
   ```sh
   curl -vik http://$INGRESS_GW_ADDRESS:8080/html \
     -H "host: compression.example:8080" \
     -H "Accept-Encoding: gzip"
   ```
   {{% /tab %}}
   {{% tab tabName="Port-forward for local testing" %}}
   ```sh
   curl -vik http://localhost:8080/html \
     -H "host: compression.example" \
     -H "Accept-Encoding: gzip"
   ```
   {{% /tab %}}
   {{< /tabs >}}

   Example output:
   ```console {hl_lines=[5]}
   < HTTP/1.1 200 OK
   HTTP/1.1 200 OK
   < content-type: text/html; charset=utf-8
   content-type: text/html; charset=utf-8
   < content-encoding: gzip
   content-encoding: gzip
   < transfer-encoding: chunked
   transfer-encoding: chunked
   < server: envoy
   server: envoy
   ```

4. Send the same request without the `Accept-Encoding: gzip` header. Verify that the response does **not** include a `content-encoding: gzip` header, confirming that compression is only applied when the client requests it.
   {{< tabs tabTotal="2" items="Cloud Provider LoadBalancer,Port-forward for local testing" >}}
   {{% tab tabName="Cloud Provider LoadBalancer" %}}
   ```sh
   curl -vik http://$INGRESS_GW_ADDRESS:8080/html \
     -H "host: compression.example:8080"
   ```
   {{% /tab %}}
   {{% tab tabName="Port-forward for local testing" %}}
   ```sh
   curl -vik http://localhost:8080/html \
     -H "host: compression.example"
   ```
   {{% /tab %}}
   {{< /tabs >}}

   Example output:
   ```console
   < HTTP/1.1 200 OK
   HTTP/1.1 200 OK
   < content-type: text/html; charset=utf-8
   content-type: text/html; charset=utf-8
   < content-length: 3741
   content-length: 3741
   < server: envoy
   server: envoy
   ```

## Request decompression {#request-decompression}

Enable gzip decompression on a route so that {{< reuse "docs/snippets/kgateway.md" >}} decompresses request bodies before forwarding them to the backend service. This setup is useful when clients send gzip-encoded request bodies.

1. Create an HTTPRoute that routes requests from the `decompression.example` domain to the httpbin sample app.
   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.networking.k8s.io/v1
   kind: HTTPRoute
   metadata:
     name: httpbin-decompression
     namespace: httpbin
   spec:
     parentRefs:
     - name: http
       namespace: {{< reuse "docs/snippets/namespace.md" >}}
     hostnames:
       - decompression.example
     rules:
       - backendRefs:
           - name: httpbin
             port: 8000
   EOF
   ```

2. Create a {{< reuse "docs/snippets/trafficpolicy.md" >}} that enables request decompression on the route.
   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: {{< reuse "docs/snippets/trafficpolicy-apiversion.md" >}}
   kind: {{< reuse "docs/snippets/trafficpolicy.md" >}}
   metadata:
     name: request-decompression
     namespace: httpbin
   spec:
     targetRefs:
     - group: gateway.networking.k8s.io
       kind: HTTPRoute
       name: httpbin-decompression
     compression:
       requestDecompression: {}
   EOF
   ```

   | Setting | Description |
   |--|--|
   | `spec.targetRefs` | The HTTPRoute to apply this policy to. |
   | `spec.compression.requestDecompression` | Enables gzip request decompression. When a request arrives with a `Content-Encoding: gzip` header, {{< reuse "docs/snippets/kgateway.md" >}} decompresses the body before forwarding the request to the backend. |

3. Create a gzip-compressed payload to use in the test.
   ```sh
   echo -n 'Hello, world!' | gzip > /tmp/payload.gz
   ```

4. Send the compressed payload to the `/post` httpbin path with the `Content-Encoding: gzip` header. Verify that the `data` field in the response shows the decompressed string `Hello, world!`, confirming that {{< reuse "docs/snippets/kgateway.md" >}} decompressed the request body before forwarding it to httpbin.
   {{< tabs tabTotal="2" items="Cloud Provider LoadBalancer,Port-forward for local testing" >}}
   {{% tab tabName="Cloud Provider LoadBalancer" %}}
   ```sh
   curl -vik -X POST http://$INGRESS_GW_ADDRESS:8080/post \
     -H "host: decompression.example:8080" \
     -H "Content-Type: text/plain" \
     -H "Content-Encoding: gzip" \
     --data-binary @/tmp/payload.gz
   ```
   {{% /tab %}}
   {{% tab tabName="Port-forward for local testing" %}}
   ```sh
   curl -vik -X POST http://localhost:8080/post \
     -H "host: decompression.example" \
     -H "Content-Type: text/plain" \
     -H "Content-Encoding: gzip" \
     --data-binary @/tmp/payload.gz
   ```
   {{% /tab %}}
   {{< /tabs >}}

   Example output:
   ```json {hl_lines=[3]}
   {
     ...
     "data": "Hello, world!",
     "headers": {
       "Content-Type": [
         "text/plain"
       ],
       ...
     }
   }
   ```

## Cleanup

{{< reuse "docs/snippets/cleanup.md" >}}

```sh
kubectl delete trafficpolicy response-compression -n httpbin
kubectl delete httproute httpbin-compression -n httpbin
kubectl delete trafficpolicy request-decompression -n httpbin
kubectl delete httproute httpbin-decompression -n httpbin
```
