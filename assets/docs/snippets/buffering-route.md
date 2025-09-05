## Set up buffer limits per route

You can configure connection buffer limits using a {{< reuse "/docs/snippets/trafficpolicy.md" >}} to control how much data can be buffered per connection at the level of individual routes. This can provide more fine-grained control than applying the buffer limit at the Gateway, or can provide a method of overriding a buffer limit at the level of the Gateway.

1. If you did not already, create a {{< reuse "/docs/snippets/trafficpolicy.md" >}} called `transformation-buffer-body` that forces buffering by transforming the response from the httpbin sample app.
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

2. If you previously added the `kgateway.dev/per-connection-buffer-limit` annotation to the Gateway, remove that annotation. 
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
   
3. In a separate {{< reuse "/docs/snippets/trafficpolicy.md" >}}, apply a buffer limit of `maxRequestSize: '1024'` to the httpbin app. This setting limits the request payload to 1024 bytes.
   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: {{< reuse "/docs/snippets/trafficpolicy-apiversion.md" >}}
   kind: {{< reuse "/docs/snippets/trafficpolicy.md" >}}
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

5. Test the buffer limit again by sending a request with a small payload, `"hello world"`. This request succeeds with a normal response from httpbin because the payload size is within the 2Ki limit.
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