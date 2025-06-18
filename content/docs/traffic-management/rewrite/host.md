---
title: Host rewrites
weight: 461
description: Replace the host header value before forwarding a request to a backend service. 
---
Replace the host header value before forwarding a request to a backend service by using the `URLRewrite` filter. 

For more information, see the [{{< reuse "docs/snippets/k8s-gateway-api-name.md" >}} documentation](https://gateway-api.sigs.k8s.io/reference/spec/#gateway.networking.k8s.io/v1.HTTPURLRewriteFilter).

## Before you begin

{{< reuse "docs/snippets/prereq.md" >}}

## Rewrite hosts

1. Create an HTTPRoute resource for the httpbin app that uses the `URLRewrite` filter to rewrite the hostname of th request. In this example, all incoming requests on the `rewrite.example` domain are rewritten to the `www.example.com` host.
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
       namespace: {{< reuse "docs/snippets/namespace.md" >}}
     hostnames:
       - rewrite.example
     rules:
        - filters:
          - type: URLRewrite
            urlRewrite:
              hostname: "www.example.com"
          backendRefs:
           - name: httpbin
             port: 8000
   EOF
   ```
   
   |Setting|Description|
   |--|--|
   |`spec.parentRefs`| The name and namespace of the Gateway that serves this HTTPRoute. In this example, you use the `http` gateway that was created as part of the get started guide. |
   |`spec.rules.filters.type`| The type of filter that you want to apply to incoming requests. In this example, the `URLRewrite` filter is used.|
   |`spec.rules.filters.urlRewrite.hostname`| The hostname that you want to rewrite requests to. |
   |`spec.rules.backendRefs`|The backend destination you want to forward traffic to. In this example, all traffic is forwarded to the httpbin app that you set up as part of the get started guide. |

2. Send a request to the httpbin app on the `rewrite.example` domain. Verify that you get back a 200 HTTP response code and that you see the `Host: www.example.com` header in your response. 

   {{< callout type="info" >}}
   The following request returns a 200 HTTP response code, because you set up an HTTPRoute for the httpbin app on the `www.example.com` domain as part of the [Getting started guide](/docs/quickstart/). If you chose a different domain for your example, make sure that you have an HTTPRoute that can be reached under the host you want to rewrite to. 
   {{< /callout >}}
   
   {{< tabs items="Cloud Provider LoadBalancer,Port-forward for local testing" tabTotal="2" >}}
   {{% tab tabName="Cloud Provider LoadBalancer" %}}
   ```sh
   curl -vi http://$INGRESS_GW_ADDRESS:8080/headers -H "host: rewrite.example:8080"
   ```
   {{% /tab %}}
   {{% tab tabName="Port-forward for local testing" %}}
   ```sh
   curl -vi localhost:8080/headers -H "host: rewrite.example"
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

## Cleanup

{{< reuse "docs/snippets/cleanup.md" >}}

```sh
kubectl delete httproute httpbin-rewrite -n httpbin
```
