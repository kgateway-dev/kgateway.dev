---
title: Request headers 
weight: 10
---

Use the {{< reuse "docs/snippets/product-name.md" >}} VirtualHostOption or RouteOption resources to add, append, overwrite, or remove request headers for a specific route or all requests that the gateway serves. 

For more information, see the [Header manipulation API](/docs/reference/api/headers).

## Before you begin

{{< reuse "docs/snippets/prereq.md" >}}

## Add request headers {#add-request-header}

Add request headers to incoming requests.

{{< tabs items="Gateway-level configuration,Route-level configuration" >}}
{{% tab %}}

Use a VirtualHostOption resource to add request headers to all requests that the gateway serves. 

1. Create a VirtualHostOption custom resource to specify your header manipulation rules. In the following example, the `my-header: kgateway` header is added to each request.  
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
         requestHeadersToAdd: 
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

2. Send a request to the httpbin app. Verify that you get back a 200 HTTP response code and that you see the added request header. 
   * **LoadBalancer IP address or hostname**: 
     ```sh
      curl -vik http://$INGRESS_GW_ADDRESS:8080/headers -H "host: www.example.com:8080"
      ```
   * **Port-forward for local testing**: 
     ```sh
     curl -vik localhost:8080/headers -H "host: www.example.com:8080"
     curl -vik localhost:8080/headers -H "host: headers.example"
     ```

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
        "www.example.com:8080"
      ],
      "My-Header": [
        "kgateway"
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
        "0338830c-4e0a-4821-9a08-48c5a7b44091"
      ]
     }
   }
   ...
   ```

3. Optional: Remove the resources that you created. 
   ```sh
   kubectl delete virtualhostoption header-manipulation -n {{< reuse "docs/snippets/ns-system.md" >}}
   ```

{{% /tab %}}
{{% tab %}}
   
Use a RouteOption resource to add request headers for incoming requests to a specific route. 

1. Create a RouteOption custom resource to specify your header manipulation rules. In the following example, the `myheader: kgateway` header is added to each request. If this header is already present in the request, the value is overwritten with `kgateway` (`append: false`). 
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
         requestHeadersToAdd:
           - header:
               key: "my-header"
               value: "kgateway"
             append: false
   EOF
   ```

2. Create an HTTPRoute resource for the httpbin app that references the RouteOption resource that you created. 
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

   |Setting|Description|
   |--|--|
   |`spec.parentRefs`| The name and namespace of the gateway that services this HTTP route. In this example, you use the HTTP gateway that was created as part of the get started guide. |
   |`spec.rules.filters.type`| The type of filter that you want to apply to incoming requests. In this example, the `ExternsionRef` filter is used.|
   |`spec.rules.filters.extenstionRef`|The reference to the RouteOption resource that you created earlier. |
   |`spec.rules.backendRefs`|The Kubernetes service you want to forward traffic to. In this example, all traffic is forwarded to the httpbin app that you set up as part of the get started guide. |

3. Send a request to the httpbin app on the `headers.example` domain and verify that you get back a 200 HTTP response code. 
   * **LoadBalancer IP address or hostname**
     ```sh
     curl -vik http://$INGRESS_GW_ADDRESS:8080/headers -H "host: headers.example:8080"
     ```
   * **Port-forward for local testing**
     ```sh
     curl -vik localhost:8080/headers -H "host: headers.example"
     ```

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
         "kgateway"
       ],
      "User-Agent": [
         "curl/7.77.0"
       ],
   ...

4. Optional: Remove the resources that you created. 
   ```sh
   kubectl delete httproute httpbin-headers -n httpbin
   kubectl delete routeoption header-manipulation -n httpbin
   ```

{{% /tab %}}
{{< /tabs >}}


## Add headers from a secret {#add-request-header-secret}

Instead of specifying the headers in your VirtualHostOption or RouteOption resource directly, you can save them to a Kubernetes secret. 

{{< tabs items="Gateway-level configuration,Route-level configuration" >}}
{{% tab %}}

Add headers from a Kubernetes secret to each request that the gateway serves. 

1. Create a Kubernetes secret of type `gateway.kgateway.dev/header` or `Opaque` that contains the headers that you want to add to a request. The following command creates a Kubernetes secret of type `gateway.kgateway.dev/header` with two headers `x-header-1: one` and `x-header-2: two`. 
   ```sh
   {{< reuse "docs/snippets/cli-name.md" >}} create secret header my-headers --headers x-header-1=one,x-header-2=two -n {{< reuse "docs/snippets/ns-system.md" >}}
   ```
   
   {{< callout type="info" >}}
   Make sure that the secret is created in the same namespace that your gateway is deployed to.
   {{< /callout >}}

2. Create a VirtualHostOption custom resource to specify your header manipulation rules. In the following example, the `myheader: kgateway` header is added to each request.  
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
         requestHeadersToAdd: 
           - headerSecretRef:
               name: my-headers
               namespace: {{< reuse "docs/snippets/ns-system.md" >}}
     targetRefs:
       group: gateway.networking.k8s.io
       kind: Gateway
       name: http
       namespace: {{< reuse "docs/snippets/ns-system.md" >}}
   EOF
   ```

3. Send a request to the httpbin app. Verify that you get back a 200 HTTP response code and that you see the added request header. 
   * **LoadBalancer IP address or hostname**
     ```sh
     curl -vik http://$INGRESS_GW_ADDRESS:8080/headers -H "host: www.example.com:8080"
     ```
   * **Port-forward for local testing**
     ```sh
     curl -vik localhost:8080/headers -H "host: www.example.com:8080"
     curl -vik localhost:8080/headers -H "host: headers.example"
     ```

   Example output: 
   ```yaml {linenos=table,hl_lines=[22,23,24,25,26],linenostart=1}
   * Mark bundle as not supporting multiuse
   < HTTP/1.1 200 OK
   HTTP/1.1 200 OK
   ..
   {
      "headers": {
        "Accept": [
          "*/*"
        ],
        "Host": [
          "headers.example:8080"
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
        "X-Header-1": [
          "one"
        ],
        "X-Header-2": [
          "two"
        ],
        "X-Request-Id": [
          "a7b891d2-93a2-4029-bd98-cd46dd414d03"
        ]
      }
   }
   ...

4. Optional: Remove the resources that you created. 
   ```sh
   kubectl delete virtualhostoption header-manipulation -n {{< reuse "docs/snippets/ns-system.md" >}}
   kubectl delete secret my-headers -n {{< reuse "docs/snippets/ns-system.md" >}}
   ```
   
{{% /tab %}}
{{% tab %}}

Add headers from a Kubernetes secret for requests to a specific route. 

1. Create a Kubernetes secret of type `gateway.kgateway.dev/header` or `Opaque` that contains the headers that you want to add to a request. The following command creates a Kubernetes secret of type `gateway.kgateway.dev/header` with two headers `x-header-1: one` and `x-header-2: two`. 
   ```sh
   {{< reuse "docs/snippets/cli-name.md" >}} create secret header my-headers --headers x-header-1=one,x-header-2=two -n httpbin
   ```
   
   {{< callout type="info" >}}
   Make sure that the secret is created in the same namespace that your gateway is deployed to.
   {{< /callout >}}
   
2. Create a RouteOption custom resource to specify your header manipulation rules. In the following example, the `myheader: kgateway` header is added to each request. If this header is already present in the request, the value is overwritten with `kgateway` (`append: false`). 
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
         requestHeadersToAdd:
           - headerSecretRef:
               name: my-headers
               namespace: httpbin
   EOF
   ```
   
3. Create an HTTPRoute resource for the httpbin app that references the RouteOption resource that you created. 
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

4. Send a request to the httpbin app on the `headers.example` domain and verify that you get back a 200 HTTP response code and the headers that you added to the secret. 
   * **LoadBalancer IP address or hostname**
     ```sh
     curl -vik http://$INGRESS_GW_ADDRESS:8080/headers -H "host: headers.example:8080"
     ```
   * **Port-forward for local testing**
     ```sh
     curl -vik localhost:8080/headers -H "host: headers.example"
     ```

   Example output: 
   ```yaml {linenos=table,hl_lines=[22,23,24,25,26],linenostart=1}
   * Mark bundle as not supporting multiuse
   < HTTP/1.1 200 OK
   HTTP/1.1 200 OK
   ..
   {
      "headers": {
        "Accept": [
          "*/*"
        ],
        "Host": [
          "headers.example:8080"
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
        "X-Header-1": [
          "one"
        ],
        "X-Header-2": [
          "two"
        ],
        "X-Request-Id": [
          "a7b891d2-93a2-4029-bd98-cd46dd414d03"
        ]
      }
   }
   ...
   ```

5. Optional: Remove the resources that you created. 
   ```sh
   kubectl delete httproute httpbin-headers -n httpbin
   kubectl delete routeoption header-manipulation -n httpbin
   kubectl delete secret my-headers -n httpbin
   ```

{{% /tab %}}
{{< /tabs >}}

## Remove request headers {#remove-request-header}

You can remove HTTP headers from a request before the request is forwarded to the target service in the cluster. 

{{< tabs items="Gateway-level configuration,Route-level configuration" >}}
{{% tab %}}

Remove specific headers from all requests to the routes that the gateway serves. 

1. Send a request to the httpbin app and find the `User-Agent` header. 
   * **LoadBalancer IP address or hostname**
     ```sh
     curl -vik http://$INGRESS_GW_ADDRESS:8080/headers -H "host: www.example.com:8080"
     ```
   * **Port-forward for local testing**
     ```sh
     curl -vik localhost:8080/headers -H "host: www.example.com"
     ```

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

2. Create a VirtualHostOption custom resource to specify your header manipulation rules. In the following example, the `User-Agent` header is removed from each request.  
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
         requestHeadersToRemove: ["User-Agent"] 
     targetRefs:
       group: gateway.networking.k8s.io
       kind: Gateway
       name: http
       namespace: {{< reuse "docs/snippets/ns-system.md" >}}
   EOF
   ```

3. Send a request to the httpbin app and verify that the `User-Agent` header is now removed. 
   * **LoadBalancer IP address or hostname**
     ```sh
     curl -vik http://$INGRESS_GW_ADDRESS:8080/headers -H "host: www.example.com:8080"
     ```
   * **Port-forward for local testing**
     ```sh
     curl -vik localhost:8080/headers -H "host: www.example.com"
     ```

   Example output: 
   ```json
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

4. Optional: Clean up the resources that you created.  
   ```sh
   kubectl delete virtualhostoption header-manipulation -n {{< reuse "docs/snippets/ns-system.md" >}}
   ```
   
{{% /tab %}}
{{% tab %}}

Remove specific headers from requests to a specific route. 

1. Send a request to the httpbin app and find the `User-Agent` header. 
   * **LoadBalancer IP address or hostname**
     ```sh
     curl -vik http://$INGRESS_GW_ADDRESS:8080/headers -H "host: www.example.com:8080"
     ```
   * **Port-forward for local testing**
     ```sh
     curl -vik localhost:8080/headers -H "host: www.example.com"
     ```

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

2. Create a RouteOption custom resource to specify your header manipulation rules. In the following example, the `User-Agent` header is removed from the request. 
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
         requestHeadersToRemove:
           - User-Agent
   EOF
   ```

3. Create the HTTPRoute resource for the httpbin app that removes the `User-Agent` header when requests are sent to the `headers.example` domain. 
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

4. Send a request to the httpbin app on the `headers.example` domain . Verify that the `User-Agent` request header is removed. 
   * **LoadBalancer IP address or hostname**
     ```sh
     curl -vik http://$INGRESS_GW_ADDRESS:8080/headers -H "host: headers.example:8080"
     ```
   * **Port-forward for local testing**
     ```sh
     curl -vik localhost:8080/headers -H "host: headers.example"
     ```

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

5. Optional: Clean up the resources that you created.  
   ```sh
   kubectl delete httproute httpbin-headers -n httpbin
   kubectl delete routeoption header-manipulation -n httpbin
   ```
   
{{% /tab %}}
{{< /tabs >}}