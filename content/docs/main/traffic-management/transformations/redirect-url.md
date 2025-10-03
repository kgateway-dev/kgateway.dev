---
title: Create redirect URLs
weight: 70
description:
---

Extract the values of common headers to generate a redirect URL.

<!--TODO agentgateway transformation
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
       request:  
         add:
         - name: x-forwarded-uri
           value: 'https://{{ request_header(":authority") }}{{ request_header(":path") }}'
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
       request:  
         add:
         - name: x-forwarded-uri
           value: '"https://" + request.headers["host"] + request.path'
   EOF
   ```
   {{% /tab %}}
   {{< /tabs >}}
-->

## About pseudo headers 

Pseudo headers are special headers that are used in HTTP/2 to provide metadata about the request or response in a structured way. Although they look like traditional HTTP/1.x headers, they come with specific characteristics:

* Must always start with a colon (`:`).
* Must appear before regular headers in the HTTP/2 frame.
* Contain details about the request or response.

Common pseudo headers include:
* `:method`: The HTTP method that is used, such as GET or POST.
* `:scheme`: The protocol that is used, such as http or https.
* `:authority`: The hostname and port number that the request is sent to.
* `:path`: The path of the request.

## Before you begin

{{< reuse "docs/snippets/prereq.md" >}}

## Set up redirect URLs

1. Create a {{< reuse "docs/snippets/trafficpolicy.md" >}} resource with the following transformation rules:
   * Build a redirect URL with the values of the `:authority` and `:path` pseudo headers. These headers are extracted from the request with the `request_header` function that is provided in {{< reuse "docs/snippets/kgateway.md" >}}.
   * The `:authority` pseudo header contains the hostname that the request is sent to.
   * The `:path` pseudo header is set to the request path.
   * The redirect URL is added to the `x-forwarded-uri` response header.

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
       request:  
         add:
         - name: x-forwarded-uri
           value: 'https://{{ request_header(":authority") }}{{ request_header(":path") }}'
   EOF
   ```

2. Send a request to the httpbin app. Verify that you get back a 200 HTTP response code and that you see the redirect URL in the `x-forwarded-uri` response header. 
   
   {{< tabs items="Cloud Provider LoadBalancer,Port-forward for local testing" tabTotal="2" >}}
   {{% tab tabName="Cloud Provider LoadBalancer" %}}
   ```sh
   curl -vi http://$INGRESS_GW_ADDRESS:8080/get \
    -H "host: www.example.com:8080" 
   ```
   {{% /tab %}}
   {{% tab tabName="Port-forward for local testing" %}}
   ```sh
   curl -vi localhost:8080/get \
   -H "host: www.example.com" 
   ```
   {{% /tab %}}
   {{< /tabs >}}
   
   Example output: 
   ```console {hl_lines=[2,3,30,31]}
   ...
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
         "curl/8.7.1"
       ],
       "X-Envoy-Expected-Rq-Timeout-Ms": [
         "15000"
       ],
       "X-Envoy-External-Address": [
         "10.0.9.76"
       ],
       "X-Forwarded-For": [
         "10.0.9.76"
       ],
       "X-Forwarded-Proto": [
         "http"
       ],
       "X-Forwarded-Uri": [
         "https://www.example.com:8080/get"
       ],
       "X-Request-Id": [
         "55140fab-c68e-44d3-a4fc-7f6242ba8194"
       ]
     },
     "origin": "10.0.9.76",
     "url": "http://www.example.com:8080/get"
   }
   ```
   
## Cleanup

{{< reuse "docs/snippets/cleanup.md" >}}

```sh
kubectl delete {{< reuse "docs/snippets/trafficpolicy.md" >}} transformation -n httpbin
```