---
title: Request headers 
weight: 10
---

Use the `RequestHeaderModifier` filter to add, append, overwrite, or remove request headers for a specific route. 

For more information, see the [HTTPHeaderFilter specification](https://gateway-api.sigs.k8s.io/reference/spec/#gateway.networking.k8s.io/v1.HTTPHeaderFilter).

## Before you begin

{{< reuse "docs/snippets/prereq.md" >}}

## Add and append request headers {#add-request-header}

Add headers to incoming requests before they are forwarded to an upstream service. If the request already has the header set, the value of the header in the `RequestHeaderModifier` filter is appended to the value of the header in the request. 

1. Set up a header modifier that adds a `my-header: hello` request header. Choose between the HTTPRoute for a Gateway API-native way, or {{< reuse "docs/snippets/trafficpolicy.md" >}} for more [flexible attachment options](../../../about/policies/trafficpolicy/) such as a gateway-level policy.
   {{< tabs items="HTTPRoute,TrafficPolicy" tabTotal="2" >}}
   {{% tab tabName="HTTPRoute" %}}
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
           - type: RequestHeaderModifier
             requestHeaderModifier:
               add: 
               - name: my-header
                 value: hello
         backendRefs:
           - name: httpbin
             port: 8000
   EOF
   ```
   
   |Setting|Description|
   |--|--|
   |`spec.parentRefs`| The name and namespace of the gateway that serves this HTTPRoute. In this example, you use the `http` Gateway that was created as part of the get started guide. |
   |`spec.rules.filters.type`| The type of filter that you want to apply to incoming requests. In this example, the `RequestHeaderModifier` filter is used.|
   |`spec.rules.filters.requestHeaderModifier.add`|The name and value of the request header that you want to add. |
   |`spec.rules.backendRefs`|The backend destination you want to forward traffic to. In this example, all traffic is forwarded to the httpbin app that you set up as part of the get started guide. |
   {{% /tab %}}
   {{% tab tabName="GlooTrafficPolicy" %}}
   **Note**: {{< reuse "docs/snippets/proxy-kgateway.md" >}}

   1. Create an HTTPRoute resource for the route that you want to modify. Note that the example selects the http Gateway that you created before you began.
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
          - backendRefs:
              - name: httpbin
                port: 8000
      EOF
      ```
   
   2. Create a {{< reuse "docs/snippets/trafficpolicy.md" >}} that adds a `my-header: hello` header to a request. The following example attaches the {{< reuse "docs/snippets/trafficpolicy.md" >}} to the http Gateway. 
      ```yaml
      kubectl apply -f- <<EOF
      apiVersion: {{< reuse "docs/snippets/trafficpolicy-apiversion.md" >}}
      kind: {{< reuse "docs/snippets/trafficpolicy.md" >}}
      metadata:
        name: httpbin-headers
        namespace: {{< reuse "docs/snippets/namespace.md" >}}
      spec:
        targetRefs:
        - group: gateway.networking.k8s.io
          kind: Gateway
          name: http
        headerModifiers:
          request:
            add:
            - name: my-header
              value: hello
      EOF
      ```
   {{% /tab %}}
   {{< /tabs >}}

2. Send a request to the httpbin app on the `headers.example` domain and verify that you get back a 200 HTTP response code and that you see the `my-header` request header. 
   {{< tabs items="Cloud Provider LoadBalancer,Port-forward for local testing" tabTotal="2" >}}
{{% tab tabName="Cloud Provider LoadBalancer" %}}
```sh
curl -vi http://$INGRESS_GW_ADDRESS:8080/headers -H "host: headers.example:8080"
```
{{% /tab %}}
{{% tab tabName="Port-forward for local testing" %}}
```sh
curl -vi localhost:8080/headers -H "host: headers.example"
```
{{% /tab %}}
   {{< /tabs >}}

   Example output: 
   ```yaml {linenos=table,hl_lines=[13,14],linenostart=1}
   * Mark bundle as not supporting multiuse
   < HTTP/1.1 200 OK
   HTTP/1.1 200 OK
   ...
   {
     "headers": {
       "Accept": [
         "*/*"
      ],
       "Host": [
         "headers.example:8080"
       ],
       "My-Header": [
         "hello"
       ],
      "User-Agent": [
         "curl/7.77.0"
       ],
   ...
   ```

1. Send another request to the httpbin app. This time, you already include the `my-header` header in your request. Verify that you get back a 200 HTTP response code and that your `my-header` header value is appended with the value from the `RequestHeaderModifier` filter. 
   {{< tabs items="Cloud Provider LoadBalancer,Port-forward for local testing" tabTotal="2" >}}
{{% tab tabName="Cloud Provider LoadBalancer" %}}
```sh
curl -vi http://$INGRESS_GW_ADDRESS:8080/headers -H "host: headers.example:8080" \
-H "my-header: foo"
```
{{% /tab %}}
{{% tab tabName="Port-forward for local testing" %}}
```sh
curl -vi localhost:8080/headers -H "host: headers.example" \
-H "my-header: foo" 
```
{{% /tab %}}
   {{< /tabs >}}
   
   Example output: 
   ```yaml {linenos=table,hl_lines=[13,14,15],linenostart=1}
   * Mark bundle as not supporting multiuse
   < HTTP/1.1 200 OK
   HTTP/1.1 200 OK
   ...
   {
     "headers": {
        "Accept": [
         "*/*"
       ],
       "Host": [
         "headers.example:8080"
       ],
       "My-Header": [
         "foo",
         "hello"
       ],
   ...
   ```

1. Optional: Remove the resources that you created. 
   {{< tabs items="HTTPRoute,TrafficPolicy" tabTotal="2" >}}
   {{% tab tabName="HTTPRoute" %}}
   ```sh
   kubectl delete httproute httpbin-headers -n httpbin
   ```
   {{% /tab %}}
   {{% tab tabName="GlooTrafficPolicy" %}}
   ```sh
   kubectl delete httproute httpbin-headers -n httpbin
   kubectl delete {{< reuse "docs/snippets/trafficpolicy.md" >}} httpbin-headers -n {{< reuse "docs/snippets/namespace.md" >}}
   ```
   {{% /tab %}}
   {{< /tabs >}}

## Set request headers {#set-request-header}

Setting headers is similar to adding headers. If the request does not include the header, it is added by the `RequestHeaderModifier` filter. However, if the request already contains the header, its value is overwritten with the value from the `RequestHeaderModifier` filter. 

1. Set up a header modifier that sets a `my-header: hello` request header. Choose between the HTTPRoute for a Gateway API-native way, or {{< reuse "docs/snippets/trafficpolicy.md" >}} for more [flexible attachment options](../../../about/policies/trafficpolicy/) such as a gateway-level policy. 
   {{< tabs items="HTTPRoute,TrafficPolicy" tabTotal="2" >}}
   {{% tab tabName="HTTPRoute" %}}
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
           - type: RequestHeaderModifier
             requestHeaderModifier:
               set: 
               - name: my-header
                 value: hello
         backendRefs:
           - name: httpbin
             port: 8000
   EOF
   ```
   
   |Setting|Description|
   |--|--|
   |`spec.parentRefs`| The name and namespace of the gateway that serves this HTTPRoute. In this example, you use the `http` Gateway that was created as part of the get started guide. |
   |`spec.rules.filters.type`| The type of filter that you want to apply to incoming requests. In this example, the `RequestHeaderModifier` filter is used.|
   |`spec.rules.filters.requestHeaderModifier.set`|The name and value of the request header that you want to set. |
   |`spec.rules.backendRefs`|The Kubernetes service you want to forward traffic to. In this example, all traffic is forwarded to the httpbin app that you set up as part of the get started guide. |
   {{% /tab %}}
   {{% tab tabName="GlooTrafficPolicy" %}}
   **Note**: {{< reuse "docs/snippets/proxy-kgateway.md" >}}
   1. Create an HTTPRoute resource for the route that you want to modify. Note that the example selects the http Gateway that you created before you began.
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
          - backendRefs:
              - name: httpbin
                port: 8000
      EOF
      ```
   
   2. Create a {{< reuse "docs/snippets/trafficpolicy.md" >}} that sets the `my-header` header value to `hello` on a request. The following example attaches the {{< reuse "docs/snippets/trafficpolicy.md" >}} to the http Gateway. 
      ```yaml
      kubectl apply -f- <<EOF
      apiVersion: {{< reuse "docs/snippets/trafficpolicy-apiversion.md" >}}
      kind: {{< reuse "docs/snippets/trafficpolicy.md" >}}
      metadata:
        name: httpbin-headers
        namespace: {{< reuse "docs/snippets/namespace.md" >}}
      spec:
        targetRefs:
        - group: gateway.networking.k8s.io
          kind: Gateway
          name: http
        headerModifiers:
          request:
            set:
            - name: my-header
              value: hello
      EOF
      ```
   {{% /tab %}}
   {{< /tabs >}}

2. Send a request to the httpbin app on the `headers.example` domain. Verify that you get back a 200 HTTP response code and that the `my-header: hello` header was added. 
   {{< tabs items="Cloud Provider LoadBalancer,Port-forward for local testing" tabTotal="2" >}}
{{% tab tabName="Cloud Provider LoadBalancer" %}}
```sh
curl -vi http://$INGRESS_GW_ADDRESS:8080/headers -H "host: headers.example:8080"
```
{{% /tab %}}
{{% tab tabName="Port-forward for local testing" %}}
```sh
curl -vi localhost:8080/headers -H "host: headers.example"
```
{{% /tab %}}
   {{< /tabs >}}

   Example output: 
   ```yaml {linenos=table,hl_lines=[13,14],linenostart=1}
   * Mark bundle as not supporting multiuse
   < HTTP/1.1 200 OK
   HTTP/1.1 200 OK
   ...
   {
     "headers": {
       "Accept": [
         "*/*"
      ],
       "Host": [
         "headers.example:8080"
       ],
       "My-Header": [
         "hello"
       ],
      "User-Agent": [
         "curl/7.77.0"
       ],
   ...
   ```

1. Send another request to the httpbin app. This time, you already include the `my-header` header in your request. Verify that you get back a 200 HTTP response code and that your `my-header` header value is overwritten with the value from the `RequestHeaderModifier` filter. 
   {{< tabs items="Cloud Provider LoadBalancer,Port-forward for local testing" tabTotal="2" >}}
{{% tab tabName="Cloud Provider LoadBalancer" %}}
```sh
curl -vi http://$INGRESS_GW_ADDRESS:8080/headers -H "host: headers.example:8080" \
-H "my-header: foo"
```
{{% /tab %}}
{{% tab tabName="Port-forward for local testing" %}}
```sh
curl -vi localhost:8080/headers -H "host: headers.example" \
-H "my-header: foo" 
```
{{% /tab %}}
   {{< /tabs >}}
   
   Example output: 
   ```yaml {linenos=table,hl_lines=[13,14],linenostart=1}
   * Mark bundle as not supporting multiuse
   < HTTP/1.1 200 OK
   HTTP/1.1 200 OK
   ...
   {
     "headers": {
        "Accept": [
         "*/*"
       ],
       "Host": [
         "headers.example:8080"
       ],
       "My-Header": [
         "hello"
       ],
   ...
   ```

1. Optional: Remove the resources that you created. 
   {{< tabs items="HTTPRoute,TrafficPolicy" tabTotal="2" >}}
   {{% tab tabName="HTTPRoute" %}}
   ```sh
   kubectl delete httproute httpbin-headers -n httpbin
   ```
   {{% /tab %}}
   {{% tab tabName="GlooTrafficPolicy" %}}
   ```sh
   kubectl delete httproute httpbin-headers -n httpbin
   kubectl delete {{< reuse "docs/snippets/trafficpolicy.md" >}} httpbin-headers -n {{< reuse "docs/snippets/namespace.md" >}}
   ```
   {{% /tab %}}
   {{< /tabs >}}

## Remove request headers {#remove-request-header}

You can remove HTTP headers from a request before the request is forwarded to the target service in the cluster. 

1. Send a request to the httpbin app and find the `User-Agent` header. 
   {{< tabs items="Cloud Provider LoadBalancer,Port-forward for local testing" tabTotal="2"  >}}
{{% tab tabName="Cloud Provider LoadBalancer" %}}
```sh
curl -vi http://$INGRESS_GW_ADDRESS:8080/headers -H "host: www.example.com:8080"
```
{{% /tab %}}
{{% tab tabName="Port-forward for local testing" %}}
```sh
curl -vi localhost:8080/headers -H "host: www.example.com"
```
{{% /tab %}}
   {{< /tabs >}}

   Example output: 
   ```yaml {linenos=table,hl_lines=[10,11],linenostart=1}
   ...
   {
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
       "X-Envoy-Expected-Rq-Timeout-Ms": [
         "15000"
       ],
       "X-Forwarded-Proto": [
         "http"
       ],
       "X-Request-Id": [
         "5b14c790-3870-4f73-a12e-4cba9a7eccd7"
       ]
     }
   }
   ```

2. Set up a header modifier that removes the `User-Agent` header when requests are sent to the `headers.example` domain. Choose between the HTTPRoute for a Gateway API-native way, or {{< reuse "docs/snippets/trafficpolicy.md" >}} for more [flexible attachment options](../../../about/policies/trafficpolicy/) such as a gateway-level policy. 
   {{< tabs items="HTTPRoute,TrafficPolicy" tabTotal="2" >}}
   {{% tab tabName="HTTPRoute" %}}
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
           - type: RequestHeaderModifier
             requestHeaderModifier:
               remove: 
                 - User-Agent
         backendRefs:
           - name: httpbin
             port: 8000
   EOF
   ```
   
   |Setting|Description|
   |--|--|
   |`spec.parentRefs`| The name and namespace of the gateway that serves this HTTPRoute. In this example, you use the `http` Gateway that was created as part of the get started guide. |
   |`spec.rules.filters.type`| The type of filter that you want to apply to incoming requests. In this example, the `RequestHeaderModifier` filter is used.|
   |`spec.rules.filters.requestHeaderModifier.remove`|The name of the request header that you want to remove. |
   |`spec.rules.backendRefs`|The backend destination you want to forward traffic to. In this example, all traffic is forwarded to the httpbin app that you set up as part of the get started guide. |
   {{% /tab %}}
   {{% tab tabName="GlooTrafficPolicy" %}}
   **Note**: {{< reuse "docs/snippets/proxy-kgateway.md" >}}
   1. Create an HTTPRoute resource for the route that you want to modify. Note that the example selects the http Gateway that you created before you began.
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
          - backendRefs:
              - name: httpbin
                port: 8000
      EOF
      ```
   
   2. Create a {{< reuse "docs/snippets/trafficpolicy.md" >}} that removes the `User-Agent` header from a request. The following example attaches the {{< reuse "docs/snippets/trafficpolicy.md" >}} to the http Gateway. 
      ```yaml
      kubectl apply -f- <<EOF
      apiVersion: {{< reuse "docs/snippets/trafficpolicy-apiversion.md" >}}
      kind: {{< reuse "docs/snippets/trafficpolicy.md" >}}
      metadata:
        name: httpbin-headers
        namespace: {{< reuse "docs/snippets/namespace.md" >}}
      spec:
        targetRefs:
        - group: gateway.networking.k8s.io
          kind: Gateway
          name: http
        headerModifiers:
          request:
            remove:
            - User-Agent
      EOF
      ```
   {{% /tab %}}
   {{< /tabs >}}

3. Send a request to the httpbin app on the `headers.example` domain . Verify that the `User-Agent` request header is removed. 
   {{< tabs items="Cloud Provider LoadBalancer,Port-forward for local testing" tabTotal="2" >}}
{{% tab tabName="Cloud Provider LoadBalancer" %}}
```sh
curl -vi http://$INGRESS_GW_ADDRESS:8080/headers -H "host: headers.example:8080"
```
{{% /tab %}}
{{% tab tabName="Port-forward for local testing" %}}
```sh
curl -vi localhost:8080/headers -H "host: headers.example"
```
{{% /tab %}}
   {{< /tabs >}}

   Example output: 
   ```sh
   {
     "headers": {
       "Accept": [
         "*/*"
       ],
       "Host": [
         "headers.example:8080"
       ],
       "X-Envoy-Expected-Rq-Timeout-Ms": [
         "15000"
       ],
       "X-Forwarded-Proto": [
         "http"
       ],
       "X-Request-Id": [
         "f83bb750-67f7-47dc-8c79-4a582892034c"
       ]
     }
   }
   ```

1. Optional: Clean up the resources that you created.  
   {{< tabs items="HTTPRoute,TrafficPolicy" tabTotal="2" >}}
   {{% tab tabName="HTTPRoute" %}}
   ```sh
   kubectl delete httproute httpbin-headers -n httpbin
   ```
   {{% /tab %}}
   {{% tab tabName="GlooTrafficPolicy" %}}
   ```sh
   kubectl delete httproute httpbin-headers -n httpbin
   kubectl delete {{< reuse "docs/snippets/trafficpolicy.md" >}} httpbin-headers -n {{< reuse "docs/snippets/namespace.md" >}}
   ```
   {{% /tab %}}
   {{< /tabs >}}

## Dynamic request headers {#dynamic-request-header}

You can return dynamic information about the request in the request header. For more information, see the Envoy docs for [Custom request/response headers](https://www.envoyproxy.io/docs/envoy/latest/configuration/http/http_conn_man/headers.html#custom-request-response-headers).

{{< reuse "docs/snippets/dynamic-req-resp-headers.md" >}}

{{< callout >}}
{{< reuse "docs/snippets/proxy-kgateway.md" >}}
{{< /callout >}} 

1. Set up a header modifier that sets the `X-Client-Ip` header with the value of the downstream remote address. Choose between the HTTPRoute for a Gateway API-native way, or {{< reuse "docs/snippets/trafficpolicy.md" >}} for more [flexible attachment options](../../../about/policies/trafficpolicy/) such as a gateway-level policy. 
   {{< tabs items="HTTPRoute,TrafficPolicy" tabTotal="2" >}}
   {{% tab tabName="HTTPRoute" %}}
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
           - type: RequestHeaderModifier
             requestHeaderModifier:
               set: 
                 - name: x-client-ip
                   value: "%DOWNSTREAM_REMOTE_ADDRESS_WITHOUT_PORT%"
         backendRefs:
           - name: httpbin
             port: 8000
   EOF
   ```
   
   |Setting|Description|
   |--|--|
   |`spec.parentRefs`| The name and namespace of the gateway that serves this HTTPRoute. In this example, you use the `http` Gateway that was created as part of the get started guide. |
   |`spec.rules.filters.type`| The type of filter that you want to apply to incoming requests. In this example, the `RequestHeaderModifier` filter is used.|
   |`spec.rules.filters.requestHeaderModifier.set`|The request header that you want to set. In this example, the `x-client-ip` header is set to the downstream remote address without the port. For more potential values, see [Command operators in the Envoy docs](https://www.envoyproxy.io/docs/envoy/latest/configuration/observability/access_log/usage.html#command-operators). |
   |`spec.rules.backendRefs`|The backend destination you want to forward traffic to. In this example, all traffic is forwarded to the httpbin app that you set up as part of the get started guide. |
   {{% /tab %}}
   {{% tab tabName="GlooTrafficPolicy" %}}  
   1. Create an HTTPRoute resource for the route that you want to modify. Note that the example selects the http Gateway that you created before you began.
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
          - backendRefs:
              - name: httpbin
                port: 8000
      EOF
      ```
   
   2. Create a {{< reuse "docs/snippets/trafficpolicy.md" >}} that sets the `x-client-ip` header to the downstream remote address without the port for a request. For more potential values, see [Command operators in the Envoy docs](https://www.envoyproxy.io/docs/envoy/latest/configuration/observability/access_log/usage.html#command-operators). The following example attaches the {{< reuse "docs/snippets/trafficpolicy.md" >}} to the http Gateway. 
      ```yaml
      kubectl apply -f- <<EOF
      apiVersion: {{< reuse "docs/snippets/trafficpolicy-apiversion.md" >}}
      kind: {{< reuse "docs/snippets/trafficpolicy.md" >}}
      metadata:
        name: httpbin-headers
        namespace: {{< reuse "docs/snippets/namespace.md" >}}
      spec:
        targetRefs:
        - group: gateway.networking.k8s.io
          kind: Gateway
          name: http
        headerModifiers:
          request:
            set:
            - name: x-client-ip
              value: "%DOWNSTREAM_REMOTE_ADDRESS_WITHOUT_PORT%"
      EOF
      ```
   {{% /tab %}}
   {{< /tabs >}}

2. Send a request to the httpbin app on the `headers.example` domain. Verify that the `X-Client-Ip` request header is set to the downstream remote address without the port. 
   {{< tabs items="Cloud Provider LoadBalancer,Port-forward for local testing" tabTotal="2" >}}
{{% tab tabName="Cloud Provider LoadBalancer" %}}
```sh
curl -vi http://$INGRESS_GW_ADDRESS:8080/headers -H "host: headers.example:8080"
```
{{% /tab %}}
{{% tab tabName="Port-forward for local testing" %}}
```sh
curl -vi localhost:8080/headers -H "host: headers.example"
```
{{% /tab %}}
   {{< /tabs >}}

   Example output: 
   ```sh
   {
     "headers": {
       "Accept": [
         "*/*"
       ],
       "Host": [
         "headers.example:8080"
       ],
       "X-Client-Ip": [
         "127.0.0.1"
       ],
       "X-Envoy-Expected-Rq-Timeout-Ms": [
         "15000"
       ],
       "X-Forwarded-Proto": [
         "http"
       ],
       "X-Request-Id": [
         "f83bb750-67f7-47dc-8c79-4a582892034c"
       ]
     }
   }
   ```

1. Optional: Clean up the resources that you created.  
   {{< tabs items="HTTPRoute,TrafficPolicy" tabTotal="2" >}}
   {{% tab tabName="HTTPRoute" %}}
   ```sh
   kubectl delete httproute httpbin-headers -n httpbin
   ```
   {{% /tab %}}
   {{% tab tabName="GlooTrafficPolicy" %}}
   ```sh
   kubectl delete httproute httpbin-headers -n httpbin
   kubectl delete {{< reuse "docs/snippets/trafficpolicy.md" >}} httpbin-headers -n {{< reuse "docs/snippets/namespace.md" >}}
   ```
   {{% /tab %}}
   {{< /tabs >}}