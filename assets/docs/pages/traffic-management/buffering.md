Fine-tune connection speeds for read and write operations by setting a connection buffer limit. 

{{< callout >}}
{{< reuse "docs/snippets/proxy-kgateway.md" >}}
{{< /callout >}}

## About read and write buffer limits

By default, {{< reuse "/docs/snippets/kgateway.md" >}} is set up with 1MiB of request read and write buffer for each gateway. For large requests that must be buffered and that exceed the default buffer limit, {{< reuse "/docs/snippets/kgateway.md" >}} either disconnects the connection to the downstream service if headers were already sent, or returns a 413 HTTP response code. To make sure that large requests can be sent and received, you can specify the maximum number of bytes that can be buffered between the gateway and the downstream service. Alternatively, when using {{< reuse "/docs/snippets/kgateway.md" >}} as an edge proxy, configuring the buffer limit can be important when dealing with untrusted downstreams. By setting the limit to a small number, such as 32KiB, you can better guard against potential attacks or misconfigured downstreams that could excessively use the proxy's resources.

The connection buffer limit can be configured on the Gateway level{{% version include-if="2.1.x" %}} or on an individual route{{% /version %}}. 

## Considerations when using httpbin

When you use the httpbin sample app, keep in mind that httpbin limits the maximum body size to 1 mebibyte (1Mi). If you send a request to httpbin with a body size that is larger than that, httpbin automatically rejects the request with a 400 HTTP response code. 

## Before you begin

{{< reuse "docs/snippets/prereq.md" >}}

## Set up buffer limits per gateway

Use an annotation to set a per-connection buffer limit on your Gateway, which applies the buffer limit to all routes served by the Gateway. 

1. Create a {{< reuse "/docs/snippets/trafficpolicy.md" >}} called `transformation-buffer-body` that forces buffering by transforming the response from the httpbin sample app.
   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: {{< reuse "/docs/snippets/trafficpolicy-apiversion.md" >}}
   kind: {{< reuse "/docs/snippets/trafficpolicy.md" >}}
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
   kind: Gateway
   apiVersion: gateway.networking.k8s.io/v1
   metadata:
     name: http
     namespace: {{< reuse "docs/snippets/namespace.md" >}}
     annotations:
       kgateway.dev/per-connection-buffer-limit: '1Ki'
   spec:
     gatewayClassName: {{< reuse "/docs/snippets/gatewayclass.md" >}}
     listeners:
     - protocol: HTTP
       port: 8080
       name: http
       allowedRoutes:
         namespaces:
           from: All
   EOF
   ```

3. To test the buffer limit, create a payload in a temp file that exceeds the 1Ki buffer limit.
   ```sh
   dd if=/dev/zero bs=2048 count=1 | base64 -w 0 > /tmp/large_payload_2k.txt
   ```

4. Send a request to the `/anything` httpbin path with the large payload. Verify that the request fails with a connection error or timeout, indicating that the buffer limit was exceeded.
   {{< tabs items="Cloud Provider LoadBalancer,Port-forward for local testing" tabTotal="2" >}}
   {{% tab tabName="Cloud Provider LoadBalancer" %}}
   ```sh
   curl -vik -X POST http://$INGRESS_GW_ADDRESS:8080/anything \
   -H "host: www.example.com:8080" \
   -H "Content-Type: text/plain" \
   -d "{\"payload\": \"$(< /tmp/large_payload_2k.txt)\"}"
   ```
   {{% /tab %}}
   {{% tab tabName="Port-forward for local testing" %}}
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
   {{< tabs items="Cloud Provider LoadBalancer,Port-forward for local testing" tabTotal="2" >}}
   {{% tab tabName="Cloud Provider LoadBalancer" %}}
   ```sh
   curl -vik -X POST http://$INGRESS_GW_ADDRESS:8080/anything \
      -H "host: www.example.com:8080" \
      -H "Content-Type: application/json" \
      -d "{\"payload\":  \"hello world\"}" 
   ```
   {{% /tab %}}
   {{% tab tabName="Port-forward for local testing" %}}
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
   
{{< version include-if="2.1.x" >}}
{{< reuse "docs/snippets/buffering-route.md" >}}
{{< /version >}}

## Cleanup

{{< reuse "docs/snippets/cleanup.md" >}}

1. Delete the {{< reuse "/docs/snippets/trafficpolicy.md" >}} resources.
   ```sh
   kubectl delete {{< reuse "/docs/snippets/trafficpolicy.md" >}} transformation-buffer-body -n httpbin {{% version include-if="2.1.x" %}}
   kubectl delete {{< reuse "/docs/snippets/trafficpolicy.md" >}} transformation-buffer-limit -n httpbin {{% /version %}}
   ```

2. Remove the buffer limit annotation from the http Gateway resource.
   ```yaml
   kubectl apply -f- <<EOF
   kind: Gateway
   apiVersion: gateway.networking.k8s.io/v1
   metadata:
     name: http
     namespace: {{< reuse "docs/snippets/namespace.md" >}}
   spec:
     gatewayClassName: {{< reuse "/docs/snippets/gatewayclass.md" >}}
     listeners:
     - protocol: HTTP
       port: 8080
       name: http
       allowedRoutes:
         namespaces:
           from: All
   EOF
   ```