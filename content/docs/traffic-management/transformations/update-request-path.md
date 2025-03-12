---
title: Update request paths and methods
weight: 50
description: Change the request path and HTTP method when a request header is present. 
---

To update the path and HTTP method the `:path` and `:method` pseudo headers are used. 

## Before you begin

{{< reuse "docs/snippets/prereq.md" >}}

## Update request paths and HTTP methods
   
1. Create a RoutePolicy resource with your transformation rules. Make sure to create the RoutePolicy in the same namespace as the HTTPRoute resource. In the following example, you change the request path and HTTP method when a `foo: bar` header is present in the request.   

   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.kgateway.dev/v1alpha1
   kind: RoutePolicy
   metadata:
     name: transformation
     namespace: httpbin
   spec:
     transformation:
       response:
         set:
         - name: ":path"
           value: '{% if request_header("foo") == "bar" %}/post{% else %}{{ request_header(":path") }}{% endif %}'
         - name: ":method"
           value: '{% if request_header("foo") == "bar" %}POST{% else %}{{ request_header(":method") }}{% endif %}'
   EOF
   ```

2. Update the HTTPRoute resource to apply the RoutePolicy to the httpbin route by using an `extensionRef` filter.

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

3. Send a request to the `/get` endpoint of the httpbin app. Include the `foo: bar` request header to trigger the request transformation. Verify that you get back a 200 HTTP response code and that your request path is rewritten to the `/post` endpoint. The `/post` endpoint accepts requests only if the HTTP POST method is used. The 200 HTTP response code therefore also indicates that the HTTP method was successfully changed from GET to POST. 
   {{< tabs items="Cloud Provider LoadBalancer,Port-forward for local testing" >}}
   {{% tab %}}
   ```sh
   curl -vik http://$INGRESS_GW_ADDRESS:8080/get \
    -H "foo: bar" \
    -H "host: www.example.com:8080" 
   ```
   {{% /tab %}}
   {{% tab %}}
   ```sh
   curl -vik localhost:8080/get \
   -H "foo: bar" \
   -H "host: www.example.com" \
   ```
   {{% /tab %}}
   {{< /tabs >}}
   
   Example output: 
   ```yaml {linenos=table,hl_lines=[1,2,39],linenostart=1}
   < HTTP/1.1 200 OK
   HTTP/1.1 200 OK
   ...  
   {
     "args": {},
     "headers": {
        "Accept": [
          "*/*"
        ],
        "Content-Length": [
        "0"
        ],
        "Foo": [
        "bar"
        ],
        "Host": [
        "www.example.com:8080"
        ],
        "User-Agent": [
        "curl/7.77.0"
        ],
        "X-B3-Sampled": [
        "0"
        ],
        "X-B3-Spanid": [
        "5f36d131289dba78"
        ],
        "X-B3-Traceid": [
        "590047a63783206e5f36d131289dba78"
        ],
        "X-Forwarded-Proto": [
        "http"
        ],
        "X-Request-Id": [
        "6b7debde-6a8a-4d9e-90a4-33a9a35937d3"
        ]
    },
    "origin": "127.0.0.6:48539",
    "url": "http://www.example.com:8080/post",
    "data": "",
    "files": null,
    "form": null,
    "json": null
   }  
   ```
   
4. Send another request to the `/get` endpoint of the httpbin app. This time, you omit the `foo: bar` header. Verify that you get back a 200 HTTP response code and that the request path is not rewritten to the `/post` endpoint. The `/get` endpoint accepts requests only if the HTTP GET method is used. A 200 HTTP response code therefore also verifies that the HTTP method was not changed. 
   {{< tabs items="Cloud Provider LoadBalancer,Port-forward for local testing" >}}
   {{% tab %}}
   ```sh
   curl -vik http://$INGRESS_GW_ADDRESS:8080/get \
    -H "host: www.example.com:8080" 
   ```
   {{% /tab %}}
   {{% tab %}}
   ```sh
   curl -vik localhost:8080/get \
   -H "host: www.example.com" \
   ```
   {{% /tab %}}
   {{< /tabs >}}
   
   Example output: 
   ```yaml {linenos=table,hl_lines=[1,2,34],linenostart=1}
   < HTTP/1.1 200 OK
   HTTP/1.1 200 OK
   ...

   {
    "args": {},
    "headers": {
        "Accept": [
        "*/*"
        ],
        "Host": [
        "www.example.com:8080"
        ],
        "User-Agent": [
        "curl/7.77.0"
        ],
        "X-B3-Sampled": [
        "0"
        ],
        "X-B3-Spanid": [
        "a83c35458cc4a47b"
        ],
        "X-B3-Traceid": [
        "bf14b3d3098cd639a83c35458cc4a47b"
        ],
        "X-Forwarded-Proto": [
        "http"
        ],
        "X-Request-Id": [
        "b91ecfcf-4f79-4b65-9727-09aafcaeb40e"
        ]
    },
    "origin": "127.0.0.6:46209",
    "url": "http://www.example.com:8080/get"
   }
   ```
   
## Cleanup

{{< reuse "docs/snippets/cleanup.md" >}}

1. Delete the RoutePolicy resource.

   ```sh
   kubectl delete RoutePolicy transformation -n httpbin
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
         namespace: {{< reuse "docs/snippets/ns-system.md" >}}
     hostnames:
       - "www.example.com"
     rules:
       - backendRefs:
           - name: httpbin
             port: 8000
   EOF
   ```
   