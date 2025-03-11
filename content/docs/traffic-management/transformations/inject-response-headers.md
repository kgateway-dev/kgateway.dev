---
title: Inject response headers
weight: 20
description: Extract values from a request header and inject it as a header to your response. 
---

The following example walks you through how to use an Inja template to extract a value from a request header and to add this value as a header to your responses. 

## Before you begin

{{< reuse "docs/snippets/prereq.md" >}}

## Inject response headers
   
1. Create a RoutePolicy resource with your transformation rules. In the following example, you use the value from the `x-solo-request` request header and populate the value of that header into an `x-solo-response` response header.
   
   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.kgateway.dev/v1alpha1
   kind: RoutePolicy
   metadata:
     name: transformation
     namespace: {{< reuse "docs/snippets/ns-system.md" >}}
   spec:
     transformation:
       response:
         set:
         - name: x-solo-response
           value: '{{ request_header("x-solo-request") }}' 
   EOF
   ```

2. Update the HTTPRoute resource to apply the RoutePolicy to the httpbin route.

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
         namespace: {{< reuse "docs/snippets/ns-system.md" >}}
     hostnames:
       - "www.example.com"
     rules:
       - backendRefs:
           - name: httpbin
             port: 8000
         filters:
         - type: ExtensionRef
           extensionRef:
             group: gateway.kgateway.dev
             kind: RoutePolicy
             name: transformation
   EOF
   ```

3. Send a request to the httpbin app and include the `x-solo-request` request header. Verify that you get back a 200 HTTP response code and that the value of the `x-solo-request` header was added to the `x-solo-response` response header. 
   
   {{< tabs items="Cloud Provider LoadBalancer,Port-forward for local testing" >}}
   {{% tab %}}
   ```sh
   curl -vik http://$INGRESS_GW_ADDRESS:8080/response-headers \
    -H "host: www.example.com:8080" \
    -H "x-solo-request: my custom request header" 
   ```
   {{% /tab %}}
   {{% tab %}}
   ```sh
   curl -vik localhost:8080/response-headers \
   -H "host: www.example.com" \
   -H "x-solo-request: my custom request header"
   ```
   {{% /tab %}}
   {{< /tabs >}}
   
   Example output: 
   ```yaml {linenos=table,hl_lines=[20,21],linenostart=1}
   * Mark bundle as not supporting multiuse
   < HTTP/1.1 200 OK
   HTTP/1.1 200 OK
   < access-control-allow-credentials: true
   access-control-allow-credentials: true
   < access-control-allow-origin: *
   access-control-allow-origin: *
   < content-type: application/json; encoding=utf-8
   content-type: application/json; encoding=utf-8
   < date: Wed, 26 Jun 2024 02:54:48 GMT
   date: Wed, 26 Jun 2024 02:54:48 GMT
   < content-length: 3
   content-length: 3
   < x-envoy-upstream-service-time: 2
   x-envoy-upstream-service-time: 2
   < server: envoy
   server: envoy
   < x-envoy-decorator-operation: httpbin.httpbin.svc.cluster.local:8000/*
   x-envoy-decorator-operation: httpbin.httpbin.svc.cluster.local:8000/*
   < x-solo-response: my custom request header
   x-solo-response: my custom request header
   ```
   
## Cleanup

{{< reuse "docs/snippets/cleanup.md" >}}

```sh
kubectl delete RoutePolicy transformation -n {{< reuse "docs/snippets/ns-system.md" >}}
```
   