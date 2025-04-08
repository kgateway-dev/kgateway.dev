---
title: Disable transformation on a route
weight: 100
description: Disable a transformation for a particular route.
---

You might apply a TrafficPolicy to an entire gateway so that all the routes undergo the same transformation, such as injecting a uniform header across routes. Sometimes, you might want to disable the transformation on a per-route basis. For example, you might have a particular route that requires custom header logic that a global policy would otherwise interfere with. 

You can disable transformation for a specific route by setting the `transformation.request` or `transformation.response` to an empty object (`{}`) for the selected route in the TrafficPolicy.

## Before you begin

{{< reuse "docs/snippets/prereq.md" >}}

## Disable transformation on a route {#steps}
   
1. Create a TrafficPolicy resource with your transformation rules for the entire Gateway. Make sure to create the TrafficPolicy in the same namespace as the Gateway resource. In the following example, you set an `x-kgateway-request` request header to `hello` and an `x-kgateway-response` response header to `goodbye`.
   
   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.kgateway.dev/v1alpha1
   kind: TrafficPolicy
   metadata:
     name: transformation
     namespace: kgateway-system
   spec:
     targetRefs: 
     - group: gateway.networking.k8s.io
       kind: Gateway
       name: http     
     transformation:
       request:
         set:
           - name: x-kgateway-request
             value: 'hello'       
       response:
         set:
         - name: x-kgateway-response
           value: 'goodbye'
   EOF
   ```

2. Create an HTTPRoute for the route that you want to exclude from transformation, such as `/anything` on the `httpbin` app.

   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.networking.k8s.io/v1
   kind: HTTPRoute
   metadata:
     name: httpbin-anything
     namespace: httpbin
   spec:
     parentRefs:
     - name: http
       namespace: kgateway-system
     hostnames:
     - www.example.com
     rules:
     - matches:
       - path:
           type: PathPrefix
           value: /anything
       backendRefs:
       - name: httpbin
         port: 8000
         namespace: httpbin
   EOF
   ```

3. Send a request to the httpbin app along the `/anything` path.
   
   {{< tabs items="Cloud Provider LoadBalancer,Port-forward for local testing" >}}
   {{% tab %}}
   ```sh
   curl -vi http://$INGRESS_GW_ADDRESS:8080/anything \
    -H "host: www.example.com:8080"
   ```
   {{% /tab %}}
   {{% tab %}}
   ```sh
   curl -vi localhost:8080/anything \
   -H "host: www.example.com"
   ```
   {{% /tab %}}
   {{< /tabs >}}
   
   In the example output, verify the following:
   
   * The `x-kgateway-request` header is added and set to `hello`.
   * The request is successful and returns a 200 HTTP response code.
   * The `x-kgateway-response` header is added and set to `goodbye`.

   ```yaml {linenos=table,hl_lines=[4,18],linenostart=1}
   ...
   * Request completely sent off
   < HTTP/1.1 200 OK
   HTTP/1.1 200 OK
   < access-control-allow-credentials: true
   access-control-allow-credentials: true
   < access-control-allow-origin: *
   access-control-allow-origin: *
   < content-type: application/json; encoding=utf-8
   content-type: application/json; encoding=utf-8
   < date: Tue, 08 Apr 2025 16:12:49 GMT
   date: Tue, 08 Apr 2025 16:12:49 GMT
   < content-length: 636
   content-length: 636
   < x-envoy-upstream-service-time: 2
   x-envoy-upstream-service-time: 2
   < x-kgateway-response: goodbye
   x-kgateway-response: goodbye
   < server: envoy
   server: envoy
   < 
   ```
   ```json {linenos=table,hl_lines=[25,26,27]}
   {
     "args": {},
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
         "10.xxx.x.x"
       ],
       "X-Forwarded-Proto": [
         "http"
       ],
       "X-Kgateway-Request": [
         "hello"
       ],
       "X-Request-Id": [
         "e003a446-d40c-4fac-9402-ab36acd9bd35"
       ]
     },
     "origin": "10.244.0.9",
     "url": "http://www.example.com/anything",
     "data": "",
     "files": null,
     "form": null,
     "json": null
   }
   ```

4. Create a TrafficPolicy to disable transformation for the HTTPRoute. Create the TrafficPolicy in the same namespace as the HTTPRoute.

   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.kgateway.dev/v1alpha1
   kind: TrafficPolicy
   metadata:
     name: disable-transformation
     namespace: httpbin
   spec:
     targetRefs:
     - group: gateway.networking.k8s.io
       kind: HTTPRoute
       name: httpbin-anything
     transformation:
       request:
         set:
           - name: x-kgateway-request
             value: 'abc'       
       response:
         set:
         - name: x-kgateway-response
           value: 'xyz'
   EOF
   ```

5. Repeat the request. This time, the request and response headers are not added because the HTTPRoute is excluded from transformation.

   {{< tabs items="Cloud Provider LoadBalancer,Port-forward for local testing" >}}
   {{% tab %}}
   ```sh
   curl -vi http://$INGRESS_GW_ADDRESS:8080/anything \
    -H "host: www.example.com:8080" \
    -H "x-kgateway-request: my custom request header" 
   ```
   {{% /tab %}}
   {{% tab %}}
   ```sh
   curl -vi localhost:8080/anything \
   -H "host: www.example.com" \
   -H "x-kgateway-request: my custom request header"
   ```
   {{% /tab %}}
   {{< /tabs >}}

   Example output:

   ```
   < HTTP/1.1 200 OK
   HTTP/1.1 200 OK   
   ...
   ```

## Cleanup

{{< reuse "docs/snippets/cleanup.md" >}}

```sh
kubectl delete TrafficPolicy transformation -n kgateway-system
kubectl delete HTTPRoute httpbin-anything -n httpbin
kubectl delete TrafficPolicy disable-transformation -n httpbin
```   
