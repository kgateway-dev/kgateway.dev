Use the `ResponseHeaderModifier` filter to add, append, overwrite, or remove headers from a response before it is sent back to the client. 

For more information, see the [HTTPHeaderFilter specification](https://gateway-api.sigs.k8s.io/reference/spec/#httpheaderfilter).

## Before you begin

{{< reuse "docs/snippets/prereq.md" >}}

## Add response headers {#add-response-headers-route}

Add headers to incoming requests before they are sent back to the client. If the response already has the header set, the value of the header in the `ResponseHeaderModifier` filter is appended to the value of the header in the response. 

1. Set up a header modifier that adds a `my-response: hello` response header. Choose between the HTTPRoute for a Gateway API-native way, or {{< reuse "docs/snippets/trafficpolicy.md" >}} for more [flexible attachment options](../../../about/policies/trafficpolicy/) such as a gateway-level policy.
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
   {{% /tab %}}
   {{% tab tabName="EnterpriseKgatewayTrafficPolicy" %}}
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
   
   2. Create a {{< reuse "docs/snippets/trafficpolicy.md" >}} that adds a `my-response: hello` header to a response. The following example attaches the {{< reuse "docs/snippets/trafficpolicy.md" >}} to the http Gateway. 
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
          response:
            add:
            - name: my-response
              value: hello
      EOF
      ```
   {{% /tab %}}
   {{< /tabs >}}
   
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

1. Optional: Remove the resources that you created. 
   {{< tabs items="HTTPRoute,TrafficPolicy" tabTotal="2" >}}
   {{% tab tabName="HTTPRoute" %}}
   ```sh
   kubectl delete httproute httpbin-headers -n httpbin
   ```
   {{% /tab %}}
   {{% tab tabName="EnterpriseKgatewayTrafficPolicy" %}}
   ```sh
   kubectl delete httproute httpbin-headers -n httpbin
   kubectl delete {{< reuse "docs/snippets/trafficpolicy.md" >}} httpbin-headers -n {{< reuse "docs/snippets/namespace.md" >}}
   ```
   {{% /tab %}}
   {{< /tabs >}}

## Set response headers 

Setting headers is similar to adding headers. If the response does not include the header, it is added by the `ResponseHeaderModifier` filter. However, if the request already contains the header, its value is overwritten with the value from the `ResponseHeaderModifier` filter. 

1. Set up a header modifier that sets a `my-response: custom` response header. Choose between the HTTPRoute for a Gateway API-native way, or {{< reuse "docs/snippets/trafficpolicy.md" >}} for more [flexible attachment options](../../../about/policies/trafficpolicy/) such as a gateway-level policy. 
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
   |`spec.rules.filters.responseHeaderModifier.set`|The name and value of the response header that you want to set. |
   |`spec.rules.backendRefs`|The backend destination you want to forward traffic to. In this example, all traffic is forwarded to the httpbin app that you set up as part of the get started guide. |
   {{% /tab %}}
   {{% tab tabName="EnterpriseKgatewayTrafficPolicy" %}}
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
   
   2. Create a {{< reuse "docs/snippets/trafficpolicy.md" >}} that sets the `my-response` header to a `custom` value on a response. The following example attaches the {{< reuse "docs/snippets/trafficpolicy.md" >}} to the http Gateway. 
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
          response:
            set:
            - name: my-response
              value: custom
      EOF
      ```
   {{% /tab %}}
   {{< /tabs >}}

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

1. Optional: Remove the resources that you created. 
   {{< tabs items="HTTPRoute,TrafficPolicy" tabTotal="2" >}}
   {{% tab tabName="HTTPRoute" %}}
   ```sh
   kubectl delete httproute httpbin-headers -n httpbin
   ```
   {{% /tab %}}
   {{% tab tabName="EnterpriseKgatewayTrafficPolicy" %}}
   ```sh
   kubectl delete httproute httpbin-headers -n httpbin
   kubectl delete {{< reuse "docs/snippets/trafficpolicy.md" >}} httpbin-headers -n {{< reuse "docs/snippets/namespace.md" >}}
   ```
   {{% /tab %}}
   {{< /tabs >}}

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
   
2. Set up a header modifier that removes the `content-length` header from the response. Choose between the HTTPRoute for a Gateway API-native way, or {{< reuse "docs/snippets/trafficpolicy.md" >}} for more [flexible attachment options](../../../about/policies/trafficpolicy/) such as a gateway-level policy. 
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
   |`spec.parentRefs`| The name and namespace of the gateway that serves this HTTPRoute. In this example, you use the `http` gateway that was created as part of the get started guide. |
   |`spec.rules.filters.type`| The type of filter that you want to apply. In this example, the `ResponseHeaderModifier` filter is used.|
   |`spec.rules.filters.responseHeaderModifier.remove`|The name of the response header that you want to remove. |
   |`spec.rules.backendRefs`|The backend destination you want to forward traffic to. In this example, all traffic is forwarded to the httpbin app that you set up as part of the get started guide. |
   {{% /tab %}}
   {{% tab tabName="EnterpriseKgatewayTrafficPolicy" %}}
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
   
   2. Create a {{< reuse "docs/snippets/trafficpolicy.md" >}} that removes the `content-length` header from a response. The following example attaches the {{< reuse "docs/snippets/trafficpolicy.md" >}} to the http Gateway. 
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
          response:
            remove:
            - content-length
      EOF
      ```
   {{% /tab %}}
   {{< /tabs >}}

3. Send a request to the httpbin app on the `headers.example` domain . Verify that the `content-length` response header is removed. 
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

1. Optional: Remove the resources that you created. 
   {{< tabs items="HTTPRoute,TrafficPolicy" tabTotal="2" >}}
   {{% tab tabName="HTTPRoute" %}}
   ```sh
   kubectl delete httproute httpbin-headers -n httpbin
   ```
   {{% /tab %}}
   {{% tab tabName="EnterpriseKgatewayTrafficPolicy" %}}
   ```sh
   kubectl delete httproute httpbin-headers -n httpbin
   kubectl delete {{< reuse "docs/snippets/trafficpolicy.md" >}} httpbin-headers -n {{< reuse "docs/snippets/namespace.md" >}}
   ```
   {{% /tab %}}
   {{< /tabs >}}

{{< version include-if="2.3.x" >}}
## Use a value from a Secret {#header-from-secret}

If a response header value is sensitive, such as an audit signing key or a service-to-service token destined for a trusted client, you might not want to commit it to a manifest in plain text. You can source a response header value from a Kubernetes Secret by replacing `value` with `secretRef` on a `set` or `add` entry in a {{< reuse "docs/snippets/trafficpolicy.md" >}}. kgateway resolves the Secret at translation time, so the value never appears in the policy spec. If the Secret changes later, kgateway re-translates the affected policies automatically.

{{< callout type="info" >}}
This option is available only on the {{< reuse "docs/snippets/trafficpolicy.md" >}}. The Gateway API `HTTPRoute` `ResponseHeaderModifier` filter does not support `secretRef`.
{{< /callout >}}

The same defaulting rules and cross-namespace `ReferenceGrant` requirement that apply to [request headers from a Secret]({{< link-hextra path="/traffic-management/header-control/request-header/#header-from-secret" >}}) also apply here. The following example shows the basic flow for responses.

1. Create a Secret that holds the value you want to inject.
   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: v1
   kind: Secret
   metadata:
     name: response-signing
     namespace: {{< reuse "docs/snippets/namespace.md" >}}
   type: Opaque
   stringData:
     signing-key: my-response-signing-key
   EOF
   ```

2. Create an HTTPRoute for the httpbin app. The example selects the http Gateway that you created before you began.
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

3. Create a {{< reuse "docs/snippets/trafficpolicy.md" >}} that sets a response header from the `response-signing` Secret. The following example attaches the {{< reuse "docs/snippets/trafficpolicy.md" >}} to the http Gateway.
   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: {{< reuse "docs/snippets/trafficpolicy-apiversion.md" >}}
   kind: {{< reuse "docs/snippets/trafficpolicy.md" >}}
   metadata:
     name: httpbin-secret-response-headers
     namespace: {{< reuse "docs/snippets/namespace.md" >}}
   spec:
     targetRefs:
     - group: gateway.networking.k8s.io
       kind: Gateway
       name: http
     headerModifiers:
       response:
         set:
         - name: X-Response-Signature
           secretRef:
             name: response-signing
             key: signing-key
   EOF
   ```

   The {{< reuse "docs/snippets/trafficpolicy.md" >}} `targetRefs` field does not accept a `namespace`. The policy must live in the same namespace as the resource it targets. To scope this example to a single HTTPRoute instead of the whole Gateway, change `kind` to `HTTPRoute` and `name` to the route's name, and create the {{< reuse "docs/snippets/trafficpolicy.md" >}} (and the Secret) in the route's namespace.

   |Setting|Description|
   |--|--|
   |`headerModifiers.response.set.name`|The HTTP header name that the client receives. |
   |`headerModifiers.response.set.secretRef.name`|The name of the Kubernetes Secret to read the value from. If the Secret does not exist when the policy is applied, the policy reports `Accepted=False` and the affected route returns a 500 response. |
   |`headerModifiers.response.set.secretRef.key`|The key in the Secret's `data` to use as the header value. Optional. If `key` is omitted, it defaults to the value of `headerModifiers.response.set.name`. |
   |`headerModifiers.response.set.secretRef.namespace`|The namespace of the Secret. Optional. If `namespace` is omitted, it defaults to the namespace of the {{< reuse "docs/snippets/trafficpolicy.md" >}}. Cross-namespace references require a `ReferenceGrant`.  |

4. Send a request to the httpbin app on the `headers.example` domain and confirm that the response includes the `X-Response-Signature` header with the value from the Secret.

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
```sh
HTTP/1.1 200 OK
access-control-allow-credentials: true
access-control-allow-origin: *
content-type: application/json; encoding=utf-8
x-envoy-upstream-service-time: 0
x-response-signature: my-response-signing-key
server: envoy
```

5. Optional: When you are finished, clean up the resources that you created.

```sh
kubectl delete httproute httpbin-headers -n httpbin
kubectl delete {{< reuse "docs/snippets/trafficpolicy.md" >}} httpbin-secret-response-headers -n {{< reuse "docs/snippets/namespace.md" >}}
kubectl delete secret response-signing -n {{< reuse "docs/snippets/namespace.md" >}}
```

{{< /version >}}

## Dynamic response headers {#dynamic-response-header}

You can return dynamic information about the response in the response header. For more information, see the Envoy docs for [Custom request/response headers](https://www.envoyproxy.io/docs/envoy/latest/configuration/http/http_conn_man/headers.html#custom-request-response-headers).

{{< reuse "docs/snippets/dynamic-req-resp-headers.md" >}}

{{< callout >}}
{{< reuse "docs/snippets/proxy-kgateway.md" >}}
{{< /callout >}} 

1. Set up a header modifier that sets the `X-Response-Code` header with the value of the HTTP response code. Choose between the HTTPRoute for a Gateway API-native way, or {{< reuse "docs/snippets/trafficpolicy.md" >}} for more [flexible attachment options](../../../about/policies/trafficpolicy/) such as a gateway-level policy. 
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
           - type: ResponseHeaderModifier
             responseHeaderModifier:
               set: 
                 - name: x-response-code
                   value: "%RESPONSE_CODE%"
         backendRefs:
           - name: httpbin
             port: 8000
   EOF
   ```
   
   |Setting|Description|
   |--|--|
   |`spec.parentRefs`| The name and namespace of the gateway that serves this HTTPRoute. In this example, you use the `http` Gateway that was created as part of the get started guide. |
   |`spec.rules.filters.type`| The type of filter that you want to apply to responses. In this example, the `ResponseHeaderModifier` filter is used.|
   |`spec.rules.filters.responseHeaderModifier.set`|The response header that you want to set. In this example, the `x-response-code` header is set to the HTTP response code. For more potential values, see [Command operators in the Envoy docs](https://www.envoyproxy.io/docs/envoy/latest/configuration/observability/access_log/usage.html#command-operators). |
   |`spec.rules.backendRefs`|The backend destination you want to forward traffic to. In this example, all traffic is forwarded to the httpbin app that you set up as part of the get started guide. |
   {{% /tab %}}
   {{% tab tabName="EnterpriseKgatewayTrafficPolicy" %}}  
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
   
   2. Create a {{< reuse "docs/snippets/trafficpolicy.md" >}} that sets the `x-response-code` header to the HTTP response code. For more potential values, see [Command operators in the Envoy docs](https://www.envoyproxy.io/docs/envoy/latest/configuration/observability/access_log/usage.html#command-operators). The following example attaches the {{< reuse "docs/snippets/trafficpolicy.md" >}} to the http Gateway.
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
          response:
            set:
            - name: x-response-code
              value: "%RESPONSE_CODE%"
      EOF
      ```
   {{% /tab %}}
   {{< /tabs >}}

2. Send a request to the httpbin app on the `headers.example` domain. Verify that the `x-response-code` response header is set to the HTTP response code. 
   {{< tabs items="Cloud Provider LoadBalancer,Port-forward for local testing" tabTotal="2" >}}
   {{% tab tabName="Cloud Provider LoadBalancer" %}}
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
   ```sh
   HTTP/1.1 200 OK
   access-control-allow-credentials: true
   access-control-allow-origin: *
   content-type: application/json; encoding=utf-8
   date: Tue, 23 Sep 2025 20:05:29 GMT
   content-length: 479
   x-envoy-upstream-service-time: 0
   x-response-code: 200
   server: envoy
   ```

1. Optional: Clean up the resources that you created.  
   {{< tabs items="HTTPRoute,TrafficPolicy" tabTotal="2" >}}
   {{% tab tabName="HTTPRoute" %}}
   ```sh
   kubectl delete httproute httpbin-headers -n httpbin
   ```
   {{% /tab %}}
   {{% tab tabName="EnterpriseKgatewayTrafficPolicy" %}}
   ```sh
   kubectl delete httproute httpbin-headers -n httpbin
   kubectl delete {{< reuse "docs/snippets/trafficpolicy.md" >}} httpbin-headers -n {{< reuse "docs/snippets/namespace.md" >}}
   ```
   {{% /tab %}}
   {{< /tabs >}}


