---
title: Host rewrites
weight: 461
description: Replace the host header value before forwarding a request to a backend service. 
---
Replace the host header value before forwarding a request to a backend service. 

For more information, see the [{{< reuse "docs/snippets/k8s-gateway-api-name.md" >}} documentation](https://gateway-api.sigs.k8s.io/api-types/httproute/#filters-optional).

## Before you begin

{{< reuse "docs/snippets/prereq.md" >}}

## Rewrite hosts

Path rewrites use the HTTP path modifier to rewrite <!--either an entire path or -->path prefixes. 

1. Create a RouteOption resource to define your rewrite rules. In the following example the host request header is rewritten to the `www.example.com` host. 
   ```yaml
   kubectl apply -n httpbin -f- <<EOF
   apiVersion: gateway.kgateway.dev/v1alpha1
   kind: RouteOption
   metadata:
     name: rewrite
     namespace: httpbin
   spec:
     options:
       hostRewrite: 'www.example.com'
   EOF
   ```

2. Create an HTTPRoute resource for the httpbin app that references the RouteOption resource that you created. In this example, all incoming requests on the `rewrite.example` domain are rewritten to the `www.example.com` host as defined in the referenced RouteOption resource.
   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.networking.k8s.io/v1
   kind: HTTPRoute
   metadata:
     name: httpbin-rewrite
     namespace: httpbin
   spec:
     parentRefs:
     - name: http
       namespace: {{< reuse "docs/snippets/ns-system.md" >}}
     hostnames:
       - rewrite.example
     rules:
        - filters:
          - type: ExtensionRef
            extensionRef:
              group: gateway.solo.io
              kind: RouteOption
              name: rewrite
          backendRefs:
           - name: httpbin
             port: 8000
   EOF
   ```

3. Send a request to the httpbin app on the `rewrite.example` domain. Verify that you get back a 200 HTTP response code and that you see the `Host: www.example.com` header in your response. 

   {{< callout type="info" >}}
   The following request returns a 200 HTTP response code, because you set up an HTTPRoute for the httpbin app on the `www.example.com` domain as part of the [Getting started guide](/docs/quickstart/). If you chose a different domain for your example, make sure that you have an HTTPRoute that can be reached under the host you want to rewrite to. 
   {{< /callout >}}
   
   {{< tabs items="Cloud Provider LoadBalancer,Port-forward for local testing" >}}
   {{% tab %}}
   ```sh
   curl -vik http://$INGRESS_GW_ADDRESS:8080/headers -H "host: rewrite.example:8080"
   ```
   {{% /tab %}}
   {{% tab %}}
   ```sh
   curl -vik localhost:8080/headers -H "host: rewrite.example"
   ```
   {{% /tab %}}
   {{< /tabs >}}
   
   Example output: 
   ```
   ...
   {
    "headers": {
      "Accept": [
        "*/*"
      ],
      "Host": [
        "www.example.com"
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
        "ffc55a3e-60ae-4c90-9a5c-62c8a1ba1076"
      ]
    }
   }
   ```

4. Optional: Clean up the resources that you created. 
   ```sh
   kubectl delete routeoption rewrite -n httpbin
   kubectl delete httproute httpbin-rewrite -n httpbin
   ```
