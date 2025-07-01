---
title: Change response status
weight: 75
description: Update the response status based on headers being present in a response.
---

Update the response status based on headers being present in a response.

## Before you begin

{{< reuse "docs/snippets/prereq.md" >}}


## Change the response status

1. Create a {{< reuse "docs/snippets/trafficpolicy.md" >}} resource with your transformation rules. In this example, you change the value of the `:status` pseudo response header to 401 if the response header `foo:bar` is present. If the `foo:bar` response header is not present, you return a 403 HTTP response code. 

   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: {{< reuse "docs/snippets/trafficpolicy-apiversion.md" >}}
   kind: {{< reuse "docs/snippets/trafficpolicy.md" >}}
   metadata:
     name: transformation
     namespace: httpbin
   spec:
     transformation:
       response:
         set:
         - name: ":status"
           value: '{% if header("foo") == "bar" %}401{% else %}403{% endif %}'
   EOF
   ```

3. Update the HTTPRoute resource to apply the {{< reuse "docs/snippets/trafficpolicy.md" >}} to the httpbin route by using an `extensionRef` filter.

   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.networking.k8s.io/v1
   kind: HTTPRoute
   metadata:
     name: httpbin
     namespace: httpbin
     labels:
       example: httpbin-route
   spec:
     parentRefs:
       - name: http
         namespace: {{< reuse "docs/snippets/namespace.md" >}}
     hostnames:
       - "www.example.com"
     rules:
       - backendRefs:
           - name: httpbin
             port: 8000
         filters:
         - type: ExtensionRef
           extensionRef:
             group: {{< reuse "docs/snippets/trafficpolicy-group.md" >}}
             kind: {{< reuse "docs/snippets/trafficpolicy.md" >}}
             name: transformation
   EOF
   ```

4. Send a request to the httpbin app and include the `foo:bar` query parameter. This query parameter automatically gets added as a response header and therefore triggers the transformation rule that you set up. Verify that you get back a 401 HTTP response code. 
   
   {{< tabs items="Cloud Provider LoadBalancer,Port-forward for local testing" tabTotal="2"  >}}
   {{% tab tabName="Cloud Provider LoadBalancer" %}}
   ```sh
   curl -vi http://$INGRESS_GW_ADDRESS:8080/response-headers?foo=bar \
    -H "host: www.example.com:8080" 
   ```
   {{% /tab %}}
   {{% tab tabName="Port-forward for local testing" %}}
   ```sh
   curl -vi localhost:8080/response-headers?foo=bar \
   -H "host: www.example.com" 
   ```
   {{% /tab %}}
   {{< /tabs >}}
   
   Example output: 
   ```console {hl_lines=[1,2,20,21]}
   < HTTP/1.1 401 Unauthorized
   HTTP/1.1 401 Unauthorized
   < access-control-allow-credentials: true
   access-control-allow-credentials: true
   < access-control-allow-origin: *
   access-control-allow-origin: *
   < content-type: application/json; encoding=utf-8
   content-type: application/json; encoding=utf-8
   < foo: bar
   foo: bar
   < content-length: 29
   content-length: 29
   < x-envoy-upstream-service-time: 4
   x-envoy-upstream-service-time: 4
   < server: envoy
   server: envoy
   < 

   {
     "foo": [
       "bar"
     ]
   }
   ```

5. Send another request to the httpbin app. This time, you include the `foo:bar2` query parameter. Verify that you get back a 403 HTTP response code. 
   
   {{< tabs items="Cloud Provider LoadBalancer,Port-forward for local testing" tabTotal="2"  >}}
   {{% tab tabName="Cloud Provider LoadBalancer" %}}
   ```sh
   curl -vi http://$INGRESS_GW_ADDRESS:8080/response-headers?foo=bar2 \
    -H "host: www.example.com:8080" 
   ```
   {{% /tab %}}
   {{% tab tabName="Port-forward for local testing" %}}
   ```sh
   curl -vi localhost:8080/response-headers?foo=bar2 \
   -H "host: www.example.com" 
   ```
   {{% /tab %}}
   {{< /tabs >}}
   
   Example output: 
   ```console {hl_lines=[1,2,20,21]}
   < HTTP/1.1 403 Forbidden
   HTTP/1.1 403 Forbidden
   < access-control-allow-credentials: true
   access-control-allow-credentials: true
   < access-control-allow-origin: *
   access-control-allow-origin: *
   < content-type: application/json; encoding=utf-8
   content-type: application/json; encoding=utf-8
   < foo: bar
   foo: bar
   < content-length: 29
   content-length: 29
   < x-envoy-upstream-service-time: 4
   x-envoy-upstream-service-time: 4
   < server: envoy
   server: envoy
   < 

   {
     "foo": [
       "bar2"
     ]
   }
   ```

## Cleanup

{{< reuse "docs/snippets/cleanup.md" >}}

1. Delete the {{< reuse "docs/snippets/trafficpolicy.md" >}} resource.

   ```sh
   kubectl delete {{< reuse "docs/snippets/trafficpolicy.md" >}} transformation -n httpbin
   ```

2. Remove the `extensionRef` filter from the HTTPRoute resource.

   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.networking.k8s.io/v1
   kind: HTTPRoute
   metadata:
     name: httpbin
     namespace: httpbin
     labels:
       example: httpbin-route
   spec:
     parentRefs:
       - name: http
         namespace: {{< reuse "docs/snippets/namespace.md" >}}
     hostnames:
       - "www.example.com"
     rules:
       - backendRefs:
           - name: httpbin
             port: 8000
   EOF
   ```