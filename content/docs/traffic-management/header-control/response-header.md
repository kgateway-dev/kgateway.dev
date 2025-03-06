---
title: Response headers
weight: 20
---

Use the {{< reuse "docs/snippets/product-name.md" >}} VirtualHostOption or RouteOption resources to add or remove response headers for a specific route or all routes that the gateway serves. 

For more information, see the [Header manipulation API](/docs/reference/api/headers).

## Before you begin

{{< reuse "docs/snippets/prereq.md" >}}

## Add response headers {#add-response-headers-route}

Add response headers to responses before they are sent back to the client.

{{< tabs items="Gateway-level configuration,Route-level configuration" >}}
{{% tab %}}

Use a VirtualHostOption resource to add response headers for responses from all routes that the gateway serves.

1. Create a VirtualHostOption custom resource to specify your header manipulation rules. In the following example, the `my-header: kgateway` header is added to each response.  
   ```yaml
   kubectl apply -n {{< reuse "docs/snippets/ns-system.md" >}} -f- <<EOF
   apiVersion: gateway.kgateway.dev/v1alpha1
   kind: VirtualHostOption
   metadata:
     name: header-manipulation
     namespace: {{< reuse "docs/snippets/ns-system.md" >}}
   spec:
     options:
       headerManipulation:
         responseHeadersToAdd: 
           - header:
               key: "my-header"
               value: "kgateway"
     targetRefs:
       group: gateway.networking.k8s.io
       kind: Gateway
       name: http
       namespace: {{< reuse "docs/snippets/ns-system.md" >}}
   EOF
   ```

2. Send a request to the httpbin app and verify that the `my-header` header is added to the response. 
   * **LoadBalancer IP address or hostname**
     ```sh
     curl -vik http://$INGRESS_GW_ADDRESS:8080/response-headers -H "host: www.example.com:8080"
     ```
   * **Port-forward for local testing**
     ```sh
     curl -vik localhost:8080/response-headers -H "host: www.example.com"
     ```
     
   Example output: 
   ```yaml {linenos=table,hl_lines=[16,17],linenostart=1}
   * Mark bundle as not supporting multiuse
   < HTTP/1.1 200 OK
   HTTP/1.1 200 OK
   < access-control-allow-credentials: true
   access-control-allow-credentials: true
   < access-control-allow-origin: *
   access-control-allow-origin: *
   < content-type: application/json; encoding=utf-8
   content-type: application/json; encoding=utf-8
   < date: Fri, 19 Apr 2024 13:26:23 GMT
   date: Fri, 19 Apr 2024 13:26:23 GMT
   < content-length: 3
   content-length: 3
   < x-envoy-upstream-service-time: 0
   x-envoy-upstream-service-time: 0
   < my-header: kgateway
   my-header: kgateway
   < server: envoy
   server: envoy
   ```
   
3. Optional: Clean up the resources that you created. 
   ```sh
   kubectl delete virtualhostoption header-manipulation -n {{< reuse "docs/snippets/ns-system.md" >}}
   ```

{{% /tab %}}
{{% tab %}}
   
Use a RouteOption resource to add response headers to responses from a specific route.

1. Create a RouteOption custom resource to specify your header manipulation rules. In the following example, the `my-response: kgateway` header is added to each response.  
   ```yaml
   kubectl apply -n httpbin -f- <<EOF
   apiVersion: gateway.kgateway.dev/v1alpha1
   kind: RouteOption
   metadata:
     name: header-manipulation
     namespace: httpbin
   spec:
     options:
       headerManipulation:
         responseHeadersToAdd:
           - header:
               key: "my-response"
               value: "kgateway"
   EOF
   ```
2. Create an HTTPRoute resource for the httpbin app that references the RouteOptions that you just created. 

   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.networking.k8s.io/v1
   kind: HTTPRoute
   metadata:
     name: httpbin-headers
     namespace: httpbin
   spec:
     parentRefs:
     - name: http
       namespace: {{< reuse "docs/snippets/ns-system.md" >}}
     hostnames:
       - headers.example
     rules:
       - filters:
           - type: ExtensionRef
             extensionRef:
               group: gateway.solo.io
               kind: RouteOption
               name: header-manipulation
         backendRefs:
           - name: httpbin
             port: 8000
   EOF
   ```
   
3. Send a request to the httpbin app on the `headers.example` domain. Verify that you get back a 200 HTTP response code and that you see the `my-response` header in the response. 
   * **LoadBalancer IP address or hostname**
     ```sh
     curl -vik http://$INGRESS_GW_ADDRESS:8080/response-headers -H "host: headers.example:8080"
     ```
   * **Port-forward for local testing**
     ```sh
     curl -vik localhost:8080/response-headers -H "host: headers.example"
     ```

   Example output: 
   ```yaml {linenos=table,hl_lines=[16,17],linenostart=1}
   * Mark bundle as not supporting multiuse
   < HTTP/1.1 200 OK
   HTTP/1.1 200 OK
   < access-control-allow-credentials: true
   access-control-allow-credentials: true
   < access-control-allow-origin: *
   access-control-allow-origin: *
   < content-type: application/json; encoding=utf-8
   content-type: application/json; encoding=utf-8
   < date: Fri, 19 Apr 2024 02:23:58 GMT
   date: Fri, 19 Apr 2024 02:23:58 GMT
   < content-length: 3
   content-length: 3
   < x-envoy-upstream-service-time: 0
   x-envoy-upstream-service-time: 0
   < my-response: kgateway
   my-response: kgateway
   < server: envoy
   server: envoy
   ```

4. Optional: Remove the resources that you created. 
   ```sh
   kubectl delete httproute httpbin-headers -n httpbin
   kubectl delete routeoption header-manipulation -n httpbin
   ```

{{% /tab %}}
{{< /tabs >}}

## Remove response headers {#remove-response-headers}

You can remove HTTP headers from a response before the response is sent back to the client. 

{{< tabs items="Gateway-level configuration,Route-level configuration" >}}
{{% tab %}}

Remove specific headers from all responses from the routes that the gateway serves.

1. Send a request to the httpbin app and find the `content-length` header. 
   * **LoadBalancer IP address or hostname**
     ```sh
     curl -vik http://$INGRESS_GW_ADDRESS:8080/response-headers -H "host: www.example.com:8080"
     ```
   * **Port-forward for local testing**
     ```sh
     curl -vik localhost:8080/response-headers -H "host: www.example.com"
     ```

   Example output: 
   ```yaml {linenos=table,hl_lines=[9,10],linenostart=1}
   ...
   * Mark bundle as not supporting multiuse
   < HTTP/1.1 200 OK
   HTTP/1.1 200 OK
   < access-control-allow-credentials: true
   access-control-allow-credentials: true
   < access-control-allow-origin: *
   access-control-allow-origin: *
   < content-type: application/json; encoding=utf-8
   content-type: application/json; encoding=utf-8
   < date: Fri, 19 Apr 2024 13:37:36 GMT
   date: Fri, 19 Apr 2024 13:37:36 GMT
   < content-length: 3
   content-length: 3
   < x-envoy-upstream-service-time: 0
   x-envoy-upstream-service-time: 0
   < server: envoy
   server: envoy
   ```
   
2. Create a VirtualHostOption custom resource to specify your header manipulation rules. In the following example, the `content-length` header is removed from each response.  
   ```yaml
   kubectl apply -n {{< reuse "docs/snippets/ns-system.md" >}} -f- <<EOF
   apiVersion: gateway.kgateway.dev/v1alpha1
   kind: VirtualHostOption
   metadata:
     name: header-manipulation
     namespace: {{< reuse "docs/snippets/ns-system.md" >}}
   spec:
     options:
       headerManipulation:
         responseHeadersToRemove: ["content-length"] 
     targetRefs:
       group: gateway.networking.k8s.io
       kind: Gateway
       name: http
       namespace: {{< reuse "docs/snippets/ns-system.md" >}}
   EOF
   ```

3. Send a request to the httpbin app and verify that the `content-length` header is removed from the response. 
   * **LoadBalancer IP address or hostname**
     ```sh
     curl -vik http://$INGRESS_GW_ADDRESS:8080/response-headers -H "host: www.example.com:8080"
     ```
   * **Port-forward for local testing**
     ```sh
     curl -vik localhost:8080/response-headers -H "host: www.example.com"
     ```
   
   Example output: 
   ```console
   * Mark bundle as not supporting multiuse
   < HTTP/1.1 200 OK
   HTTP/1.1 200 OK
   < access-control-allow-credentials: true
   access-control-allow-credentials: true
   < access-control-allow-origin: *
   access-control-allow-origin: *
   < content-type: application/json; encoding=utf-8
   content-type: application/json; encoding=utf-8
   < date: Fri, 19 Apr 2024 13:51:53 GMT
   date: Fri, 19 Apr 2024 13:51:53 GMT
   < x-envoy-upstream-service-time: 0
   x-envoy-upstream-service-time: 0
   < server: envoy
   server: envoy
   < transfer-encoding: chunked
   transfer-encoding: chunked
   ```

4. Optional: Clean up the resources that you created. 
   ```sh
   kubectl delete virtualhostoption header-manipulation -n {{< reuse "docs/snippets/ns-system.md" >}}
   ```

{{% /tab %}}
{{% tab %}}
   
You can remove HTTP headers from a response of a specific route before the response is sent back to the client. 


1. Send a request to the httpbin app and find the `content-length` header. 
   * **LoadBalancer IP address or hostname**
     ```sh
     curl -vik http://$INGRESS_GW_ADDRESS:8080/response-headers -H "host: www.example.com:8080"
     ```
   * **Port-forward for local testing**
     ```sh
     curl -vik localhost:8080/response-headers -H "host: www.example.com"
     ```

   Example output: 
   ```yaml {linenos=table,hl_lines=[9,10],linenostart=1}
   ...
   * Mark bundle as not supporting multiuse
   < HTTP/1.1 200 OK
   HTTP/1.1 200 OK
   < access-control-allow-credentials: true
   access-control-allow-credentials: true
   < access-control-allow-origin: *
   access-control-allow-origin: *
   < content-type: application/json; encoding=utf-8
   content-type: application/json; encoding=utf-8
   < date: Fri, 19 Apr 2024 16:40:01 GMT
   date: Fri, 19 Apr 2024 16:40:01 GMT
   < content-length: 3
   content-length: 3
   < x-envoy-upstream-service-time: 0
   x-envoy-upstream-service-time: 0
   < server: envoy
   server: envoy
   ```

2. Create a RouteOption resource to specify your header manipulation rules. In this example, you remove the `content-length` response header from each response. 
   ```yaml
   kubectl apply -n httpbin -f- <<EOF
   apiVersion: gateway.kgateway.dev/v1alpha1
   kind: RouteOption
   metadata:
     name: header-manipulation
     namespace: httpbin
   spec:
     options:
       headerManipulation:
         responseHeadersToRemove: ["content-length"]
   EOF
   ```
   
3. Create an HTTPRoute resource for the httpbin app that references the RouteOptions that you just created. 

   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.networking.k8s.io/v1
   kind: HTTPRoute
   metadata:
     name: httpbin-headers
     namespace: httpbin
   spec:
     parentRefs:
     - name: http
       namespace: {{< reuse "docs/snippets/ns-system.md" >}}
     hostnames:
       - headers.example
     rules:
       - filters:
           - type: ExtensionRef
             extensionRef:
               group: gateway.solo.io
               kind: RouteOption
               name: header-manipulation
         backendRefs:
           - name: httpbin
             port: 8000
   EOF
   ```

4. Send a request to the httpbin app on the `headers.example` domain . Verify that the `content-length` response header is removed. 
   * **LoadBalancer IP address or hostname**
     ```sh
     curl -vik http://$INGRESS_GW_ADDRESS:8080/response-headers -H "host: headers.example:8080"
     ```
   * **Port-forward for local testing**
     ```sh
     curl -vik localhost:8080/reesponse-headers -H "host: headers.example"
     ```

   Example output: 
   ```console
   * Mark bundle as not supporting multiuse
   < HTTP/1.1 200 OK
   HTTP/1.1 200 OK
   < access-control-allow-credentials: true
   access-control-allow-credentials: true
   < access-control-allow-origin: *
   access-control-allow-origin: *
   < content-type: application/json; encoding=utf-8
   content-type: application/json; encoding=utf-8
   < date: Fri, 19 Apr 2024 13:51:53 GMT
   date: Fri, 19 Apr 2024 13:51:53 GMT
   < x-envoy-upstream-service-time: 0
   x-envoy-upstream-service-time: 0
   < server: envoy
   server: envoy
   < transfer-encoding: chunked
   transfer-encoding: chunked
   ```

5. Optional: Remove the resources that you created. 
   ```sh
   kubectl delete httproute httpbin-headers -n httpbin
   kubectl delete routeoption header-manipulation -n httpbin
   ```

{{% /tab %}}
{{< /tabs >}}