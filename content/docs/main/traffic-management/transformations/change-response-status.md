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

   {{< tabs items="Envoy-based kgateway,Agentgateway" tabTotal="2" >}}
   {{% tab tabName="Envoy-based kgateway" %}}
   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: {{< reuse "docs/snippets/trafficpolicy-apiversion.md" >}}
   kind: {{< reuse "docs/snippets/trafficpolicy.md" >}}
   metadata:
     name: transformation
     namespace: httpbin
   spec:
     targetRefs:
     - group: gateway.networking.k8s.io
       kind: HTTPRoute
       name: httpbin
     transformation:
       response:
         set:
         - name: ":status"
           value: '{% if header("foo") == "bar" %}401{% else %}403{% endif %}'
   EOF
   ```
   {{% /tab %}}
   {{% tab tabName="Agentgateway" %}}
   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: {{< reuse "docs/snippets/trafficpolicy-apiversion.md" >}}
   kind: {{< reuse "docs/snippets/trafficpolicy.md" >}}
   metadata:
     name: transformation
     namespace: httpbin
   spec:
     targetRefs:
     - group: gateway.networking.k8s.io
       kind: HTTPRoute
       name: httpbin
     transformation:
       response:
         set:
         - name: ":status"
           value: 'request.uri.contains("foo=bar") ? 401 : 403'
   EOF
   ```
   {{% /tab %}}
   {{< /tabs >}}

2. Send a request to the httpbin app and include the `foo:bar` query parameter. This query parameter automatically gets added as a response header and therefore triggers the transformation rule that you set up. Verify that you get back a 401 HTTP response code. 
   
   {{< tabs items="Cloud Provider LoadBalancer,Port-forward for local testing" tabTotal="2"  >}}
   {{% tab tabName="Cloud Provider LoadBalancer" %}}
   ```sh
   curl -vi http://$INGRESS_GW_ADDRESS:8080/response-headers?foo=bar \
    -H "host: www.example.com:8080" 
   ```
   {{% /tab %}}
   {{% tab tabName="Port-forward for local testing" %}}
   ```sh
   curl -vi "localhost:8080/response-headers?foo=bar" \
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

3. Send another request to the httpbin app. This time, you include the `foo:baz` query parameter. Verify that you get back a 403 HTTP response code. 
   
   {{< tabs items="Cloud Provider LoadBalancer,Port-forward for local testing" tabTotal="2"  >}}
   {{% tab tabName="Cloud Provider LoadBalancer" %}}
   ```sh
   curl -vi http://$INGRESS_GW_ADDRESS:8080/response-headers?foo=baz \
    -H "host: www.example.com:8080" 
   ```
   {{% /tab %}}
   {{% tab tabName="Port-forward for local testing" %}}
   ```sh
   curl -vi "localhost:8080/response-headers?foo=baz" \
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

```sh
kubectl delete {{< reuse "docs/snippets/trafficpolicy.md" >}} transformation -n httpbin
```