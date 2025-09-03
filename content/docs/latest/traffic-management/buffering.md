---
title: Buffering
weight: 20
next: /docs/traffic-management/header-control
prev: /docs/traffic-management/route-delegation
---

Fine-tune connection speeds for read and write operations by setting a connection buffer limit. 

{{< callout >}}
{{< reuse "docs/snippets/proxy-kgateway.md" >}}
{{< /callout >}}

## About read and write buffer limits

By default, {{< reuse "/docs/snippets/kgateway.md" >}} is set up with 1MiB of request read and write buffer for each gateway. For large requests that must be buffered and that exceed the default buffer limit, {{< reuse "/docs/snippets/kgateway.md" >}} either disconnects the connection to the downstream service if headers were already sent, or returns a 500 HTTP response code. To make sure that large requests can be sent and received, you can specify the maximum number of bytes that can be buffered between the gateway and the downstream service. Alternatively, when using {{< reuse "/docs/snippets/kgateway.md" >}} as an edge proxy, configuring the buffer limit can be important when dealing with untrusted downstreams. By setting the limit to a small number, such as 32KiB, you can better guard against potential attacks or misconfigured downstreams that could excessively use the proxy's resources.

The connection buffer limit can be configured at both the Gateway level and the {{< reuse "/docs/snippets/trafficpolicy.md" >}} level, providing flexibility in how you manage buffer limits in your applications.

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
     namespace: {{< reuse "docs/snippets/namespace.md" >}}
   spec:
     targetRefs:
     - group: gateway.networking.k8s.io
       kind: HTTPRoute
       name: httpbin
     transformation:
       response:
         body:
           parseAs: AsString
           value: '{% raw %}{{ body() }}{% endraw %}'
   EOF
   ```

2. Annotate the http Gateway resource to set a buffer limit of 2 kilobytes.
   ```yaml
   kubectl apply -f- <<EOF
   kind: Gateway
   apiVersion: gateway.networking.k8s.io/v1
   metadata:
     name: http
     namespace: {{< reuse "docs/snippets/namespace.md" >}}
     annotations:
       kgateway.dev/per-connection-buffer-limit: 2Ki
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

3. To test the buffer limit, create a payload in a temp file that exceeds the 2Ki buffer limit.
   ```sh
   dd if=/dev/zero bs=2048 count=1 | base64 -w 0 > /tmp/large_payload_2k.txt
   ```

4. Send a request to the `/anything` httpbin path with the large payload. Verify that the request fails with a connection error or timeout, indicating that the buffer limit was exceeded.
   {{< tabs items="Cloud Provider LoadBalancer,Port-forward for local testing" tabTotal="2" >}}
   {{% tab tabName="Cloud Provider LoadBalancer" %}}
   ```sh
   curl -k -X POST \
      -H "Content-Type: application/json" \
      -d "{\"payload\": \"$(< /tmp/large_payload_2k.txt)\"}" \
      http://$INGRESS_GW_ADDRESS:8080/anything -v
   ```
   {{% /tab %}}
   {{% tab tabName="Port-forward for local testing" %}}
   ```sh
   curl -k -X POST \
      -H "Content-Type: application/json" \
      -d "{\"payload\": \"$(< /tmp/large_payload_2k.txt)\"}" \
      http://localhost:8080/anything -v
   ```
   {{% /tab %}}
   {{< /tabs >}}

5. Test the buffer limit again by sending a request with a small payload, `"hello world"`. This request succeeds with a normal response from httpbin because the payload size is within the 2Ki limit.
   {{< tabs items="Cloud Provider LoadBalancer,Port-forward for local testing" tabTotal="2" >}}
   {{% tab tabName="Cloud Provider LoadBalancer" %}}
   ```sh
   curl -k -X POST \
      -H "Content-Type: application/json" \
      -d "{\"payload\": \"hello world\"}" \
      https://$INGRESS_GW_ADDRESS:8080/anything
   ```
   {{% /tab %}}
   {{% tab tabName="Port-forward for local testing" %}}
   ```sh
   curl -k -X POST \
      -H "Content-Type: application/json" \
      -d "{\"payload\": \"hello world\"}" \
      http://localhost:8080/anything -v
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

## Set up buffer limits per route

You can configure connection buffer limits using a {{< reuse "/docs/snippets/trafficpolicy.md" >}} to control how much data can be buffered per connection at the level of individual routes. This can provide more fine-grained control than applying the buffer limit at the Gateway, or can provide a method of overriding a buffer limit at the level of the Gateway.

1. If you did not already, create a {{< reuse "/docs/snippets/trafficpolicy.md" >}} called `transformation-buffer-body` that forces buffering by transforming the response from the httpbin sample app.
   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: {{< reuse "/docs/snippets/trafficpolicy-apiversion.md" >}}
   kind: {{< reuse "/docs/snippets/trafficpolicy.md" >}}
   metadata:
     name: transformation-buffer-body
     namespace: {{< reuse "docs/snippets/namespace.md" >}}
   spec:
     targetRefs:
     - group: gateway.networking.k8s.io
       kind: HTTPRoute
       name: httpbin
     transformation:
       response:
         body:
           parseAs: AsString
           value: '{% raw %}{{ body() }}{% endraw %}'
   EOF
   ```

2. In a separate {{< reuse "/docs/snippets/trafficpolicy.md" >}}, apply a buffer limit of `maxRequestSize: '1024'`, which sets the limit to 1024 bytes.
   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: {{< reuse "/docs/snippets/trafficpolicy-apiversion.md" >}}
   kind: {{< reuse "/docs/snippets/trafficpolicy.md" >}}
   metadata:
     name: transformation-buffer-limit
     namespace: {{< reuse "docs/snippets/namespace.md" >}}
   spec:
     targetRefs:
     - group: gateway.networking.k8s.io
       kind: HTTPRoute
       name: httpbin
     buffer:
       maxRequestSize: '1024'
   EOF
   ```

3. To test the buffer limit, create a payload in a temp file that exceeds the 1024 byte buffer limit.
   ```sh
   dd if=/dev/zero bs=1024 count=2 | base64 -w 0 > /tmp/large_payload.txt
   ```

4. Send a request to the `/anything` httpbin path with the large payload. Verify that the request fails with a connection error or timeout, indicating that the buffer limit was exceeded.
   {{< tabs items="Cloud Provider LoadBalancer,Port-forward for local testing" tabTotal="2" >}}
   {{% tab tabName="Cloud Provider LoadBalancer" %}}
   ```sh
   curl -k -X POST \
      -H "Content-Type: application/json" \
      -d "{\"payload\": \"$(< /tmp/large_payload.txt)\"}" \
      http://$INGRESS_GW_ADDRESS:8080/anything -v
   ```
   {{% /tab %}}
   {{% tab tabName="Port-forward for local testing" %}}
   ```sh
   curl -k -X POST \
      -H "Content-Type: application/json" \
      -d "{\"payload\": \"$(< /tmp/large_payload.txt)\"}" \
      http://localhost:8080/anything -v
   ```
   {{% /tab %}}
   {{< /tabs >}}

5. Test the buffer limit again by sending a request with a small payload, `"hello world"`. This request succeeds with a normal response from httpbin because the payload size is within the 2Ki limit.
   {{< tabs items="Cloud Provider LoadBalancer,Port-forward for local testing" tabTotal="2" >}}
   {{% tab tabName="Cloud Provider LoadBalancer" %}}
   ```sh
   curl -k -X POST \
      -H "Content-Type: application/json" \
      -d "{\"payload\": \"hello world\"}" \
      https://$INGRESS_GW_ADDRESS:8080/anything
   ```
   {{% /tab %}}
   {{% tab tabName="Port-forward for local testing" %}}
   ```sh
   curl -k -X POST \
      -H "Content-Type: application/json" \
      -d "{\"payload\": \"hello world\"}" \
      http://localhost:8080/anything -v
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

## Cleanup

{{< reuse "docs/snippets/cleanup.md" >}}

1. Delete the {{< reuse "/docs/snippets/trafficpolicy.md" >}} resources.
   ```sh
   kubectl delete {{< reuse "/docs/snippets/trafficpolicy.md" >}} transformation-buffer-body -n {{< reuse "docs/snippets/namespace.md" >}}
   kubectl delete {{< reuse "/docs/snippets/trafficpolicy.md" >}} transformation-buffer-limit -n {{< reuse "docs/snippets/namespace.md" >}}
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