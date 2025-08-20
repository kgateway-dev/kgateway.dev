---
title: Response headers
weight: 20
---

Use the `ResponseHeaderModifier` filter to add, append, overwrite, or remove headers from a response before it is sent back to the client. 

For more information, see the [HTTPHeaderFilter specification](https://gateway-api.sigs.k8s.io/reference/spec/#gateway.networking.k8s.io/v1.HTTPHeaderFilter).

## Before you begin

{{< reuse "docs/snippets/prereq.md" >}}

## Add response headers {#add-response-headers-route}

Add headers to incoming requests before they are sent back to the client. If the response already has the header set, the value of the header in the `ResponseHeaderModifier` filter is appended to the value of the header in the response. 

1. Create an HTTPRoute resource for the httpbin app with an `ResponseHeaderModifier`. In this example, you want to add the `my-response: hello` response header. 
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
       namespace: {{< reuse "docs/snippets/namespace.md" >}}
     hostnames:
       - headers.example
     rules:
       - filters:
           - type: ResponseHeaderModifier
             responseHeaderModifier:
               add: 
               - name: my-response
                 value: hello
         backendRefs:
           - name: httpbin
             port: 8000
   EOF
   ```
   
   |Setting|Description|
   |--|--|
   |`spec.parentRefs`| The name and namespace of the gateway that serves this HTTPRoute. In this example, you use the `http` gateway that was created as part of the get started guide. |
   |`spec.rules.filters.type`| The type of filter that you want to apply to incoming requests. In this example, the `ResponseHeaderModifier` filter is used.|
   |`spec.rules.filters.responseHeaderModifier.add`|The name and value of the response header that you want to add. |
   |`spec.rules.backendRefs`|The backend destination you want to forward traffic to. In this example, all traffic is forwarded to the httpbin app that you set up as part of the get started guide. |
   
2. Send a request to the httpbin app on the `headers.example` domain. Verify that you get back a 200 HTTP response code and that you see the `my-response` header in the response. 
   {{< tabs items="Cloud Provider Loadbalancer,Port-forward for local testing" tabTotal="2" >}}
{{% tab tabName="Cloud Provider Loadbalancer" %}}
```sh
curl -vi http://$INGRESS_GW_ADDRESS:8080/response-headers -H "host: headers.example:8080"
```
{{% /tab %}}
{{% tab tabName="Port-forward for local testing" %}}
```sh
curl -vi localhost:8080/response-headers -H "host: headers.example"
```
{{% /tab %}}
   {{< /tabs >}}

   Example output: 
   ```yaml {linenos=table,hl_lines=[14,15],linenostart=1}
   * Mark bundle as not supporting multiuse
   < HTTP/1.1 200 OK
   HTTP/1.1 200 OK
   < access-control-allow-credentials: true
   access-control-allow-credentials: true
   < access-control-allow-origin: *
   access-control-allow-origin: *
   < content-type: application/json; encoding=utf-8
   content-type: application/json; encoding=utf-8
   < content-length: 3
   content-length: 3
   < x-envoy-upstream-service-time: 0
   x-envoy-upstream-service-time: 0
   < my-response: hello
   my-response: hello
   < server: envoy
   server: envoy
   ```

4. Optional: Remove the HTTPRoute that you created. 
   ```sh
   kubectl delete httproute httpbin-headers -n httpbin
   ```

## Set response headers 

Setting headers is similar to adding headers. If the response does not include the header, it is added by the `ResponseHeaderModifier` filter. However, if the request already contains the header, its value is overwritten with the value from the `ResponseHeaderModifier` filter. 

1. Create an HTTPRoute resource for the httpbin app with an `ResponseHeaderModifier`. In this example, you want to set the `my-response` response header to the value `custom`. 
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
       namespace: {{< reuse "docs/snippets/namespace.md" >}}
     hostnames:
       - headers.example
     rules:
       - filters:
           - type: ResponseHeaderModifier
             responseHeaderModifier:
               set: 
               - name: my-response
                 value: custom
         backendRefs:
           - name: httpbin
             port: 8000
   EOF
   ```

   |Setting|Description|
   |--|--|
   |`spec.parentRefs`| The name and namespace of the gateway that serves this HTTPRoute. In this example, you use the `http` Gateway that was created as part of the get started guide. |
   |`spec.rules.filters.type`| The type of filter that you want to apply to incoming requests. In this example, the `ResponseHeaderModifier` filter is used.|
   |`spec.rules.filters.requestHeaderModifier.set`|The name and value of the response header that you want to set. |
   |`spec.rules.backendRefs`|The backend destination you want to forward traffic to. In this example, all traffic is forwarded to the httpbin app that you set up as part of the get started guide. |

2. Send a request to the httpbin app on the `headers.example` domain. Verify that you get back a 200 HTTP response code and that the `my-response: custom` header was set. 
   {{< tabs items="Cloud Provider Loadbalancer,Port-forward for local testing" tabTotal="2" >}}
{{% tab tabName="Cloud Provider Loadbalancer" %}}
```sh
curl -vi http://$INGRESS_GW_ADDRESS:8080/response-headers -H "host: headers.example:8080"
```
{{% /tab %}}
{{% tab tabName="Port-forward for local testing" %}}
```sh
curl -vi localhost:8080/response-headers -H "host: headers.example"
```
{{% /tab %}}
   {{< /tabs >}}

   Example output: 
   ```yaml {linenos=table,hl_lines=[10,11],linenostart=1}
   ...
   * Request completely sent off
   < HTTP/1.1 200 OK
   HTTP/1.1 200 OK
   < access-control-allow-credentials: true
   access-control-allow-credentials: true
   < access-control-allow-origin: *
   access-control-allow-origin: *
   ...
   < my-response: custom
   my-response: custom
   < server: envoy
   server: envoy
   ```

3. Optional: Remove the HTTPRoute that you created. 
   ```sh
   kubectl delete httproute httpbin-headers -n httpbin
   ```

## Remove response headers {#remove-response-headers}

You can remove HTTP headers from a response before the response is sent back to the client. 

1. Send a request to the httpbin app and find the `content-length` header. 
   {{< tabs items="Cloud Provider Loadbalancer,Port-forward for local testing" tabTotal="2" >}}
{{% tab tabName="Cloud Provider Loadbalancer" %}}
```sh
curl -vi http://$INGRESS_GW_ADDRESS:8080/response-headers -H "host: www.example.com:8080"
```
{{% /tab %}}
{{% tab tabName="Port-forward for local testing" %}}
```sh
curl -vi localhost:8080/response-headers -H "host: www.example.com"
```
{{% /tab %}}
   {{< /tabs >}}

   Example output: 
   ```yaml {linenos=table,hl_lines=[11,12],linenostart=1}
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
   < content-length: 3
   content-length: 3
   < x-envoy-upstream-service-time: 0
   x-envoy-upstream-service-time: 0
   < server: envoy
   server: envoy
   ```
   
2. Create an HTTPRoute resource for the httpbin app that removes the `content-length` header from the response. 

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
       namespace: {{< reuse "docs/snippets/namespace.md" >}}
     hostnames:
       - headers.example
     rules:
       - filters:
           - type: ResponseHeaderModifier
             responseHeaderModifier:
               remove: 
               - content-length
         backendRefs:
           - name: httpbin
             port: 8000
   EOF
   ```
   
   |Setting|Description|
   |--|--|
   |`spec.parentRefs`| The name and namespace of the gateway that servesthis HTTPRoute. In this example, you use the `http` gateway that was created as part of the get started guide. |
   |`spec.rules.filters.type`| The type of filter that you want to apply. In this example, the `ResponseHeaderModifier` filter is used.|
   |`spec.rules.filters.responseHeaderModifier.remove`|The name of the response header that you want to remove. |
   |`spec.rules.backendRefs`|The backend destination you want to forward traffic to. In this example, all traffic is forwarded to the httpbin app that you set up as part of the get started guide. |

3. Send a request to the httpbin app on the `headers.example` domain . Verify that the `content-length` response header is removed. 
   {{< tabs items="Cloud Provider Loadbalancer,Port-forward for local testing" tabTotal="2" >}}
{{% tab tabName="Cloud Provider Loadbalancer" %}}
```sh
curl -vi http://$INGRESS_GW_ADDRESS:8080/response-headers -H "host: headers.example:8080"
```
{{% /tab %}}
{{% tab tabName="Port-forward for local testing" %}}
```sh
curl -vi localhost:8080/reesponse-headers -H "host: headers.example"
```
{{% /tab %}}
   {{< /tabs >}}

   Example output: 
   ```
   * Mark bundle as not supporting multiuse
   < HTTP/1.1 200 OK
   HTTP/1.1 200 OK
   < access-control-allow-credentials: true
   access-control-allow-credentials: true
   < access-control-allow-origin: *
   access-control-allow-origin: *
   < content-type: application/json; encoding=utf-8
   content-type: application/json; encoding=utf-8
   < x-envoy-upstream-service-time: 0
   x-envoy-upstream-service-time: 0
   < server: envoy
   server: envoy
   < transfer-encoding: chunked
   transfer-encoding: chunked
   ```

4. Optional: Remove the HTTPRoute that you created. 
   ```sh
   kubectl delete httproute httpbin-headers -n httpbin
   ```

