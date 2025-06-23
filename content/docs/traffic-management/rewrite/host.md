---
title: Host rewrites
weight: 461
description: Replace the host header value before forwarding a request to a backend service. 
---
Replace the host header value before forwarding a request to a backend service by using the `URLRewrite` filter. 

For more information, see the [{{< reuse "docs/snippets/k8s-gateway-api-name.md" >}} documentation](https://gateway-api.sigs.k8s.io/reference/spec/#gateway.networking.k8s.io/v1.HTTPURLRewriteFilter).

## Before you begin

{{< reuse "docs/snippets/prereq.md" >}}

## In-cluster service host rewrites

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
   The following request returns a 200 HTTP response code, because you set up an HTTPRoute for the httpbin app on the `www.example.com` domain as part of the getting started guide. If you chose a different domain for your example, make sure that you have an HTTPRoute that can be reached under the host you want to rewrite to. 
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
   ```console {hl_lines=[7,8]}
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
   
## External service host rewrites

1. Create a Backend that represents your external service. The following example creates a Backend for the `httpbin.org` domain. 
   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.kgateway.dev/v1alpha1
   kind: Backend
   metadata:
     name: httpbin
     namespace: default
   spec:
     type: Static
     static:
       hosts:
         - host: httpbin.org
           port: 80
   EOF
   ```
   
2. Create an HTTPRoute resource that matches incoming traffic on the `external-rewrite.example` domain and forwards traffic to the Backend that you created. Because the Backend expects a different domain, you use the `URLRewrite` filter to rewrite the hostname from `external-rewrite.example` to `httpbin.org`. 
   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.networking.k8s.io/v1
   kind: HTTPRoute
   metadata:
     name: backend-rewrite
     namespace: default
   spec:
     parentRefs:
     - name: http
       namespace: {{< reuse "docs/snippets/namespace.md" >}}
     hostnames:
       - external-rewrite.example
     rules:
        - filters:
          - type: URLRewrite
            urlRewrite:
              hostname: "httpbin.org"
          backendRefs:
          - name: httpbin
            kind: Backend
            group: gateway.kgateway.dev
   EOF
   ```

2. Send a request to the `external-rewrite.example` domain. Verify that you get back a 200 HTTP response code and that you see the `Host: httpbin.org` header in your response. 
   
   {{< tabs items="Cloud Provider LoadBalancer,Port-forward for local testing" tabTotal="2" >}}
   {{% tab tabName="Cloud Provider LoadBalancer" %}}
   ```sh
   curl -vi http://$INGRESS_GW_ADDRESS:8080/headers -H "host: external-rewrite.example:8080"
   ```
   {{% /tab %}}
   {{% tab tabName="Port-forward for local testing" %}}
   ```sh
   curl -vi localhost:8080/headers -H "host: external-rewrite.example"
   ```
   {{% /tab %}}
   {{< /tabs >}}
   
   Example output: 
   ```console {hl_lines=[2,3,21]}
   * Request completely sent off
   < HTTP/1.1 200 OK
   HTTP/1.1 200 OK
   < content-type: application/json
   content-type: application/json
   < content-length: 268
   content-length: 268
   < server: envoy
   server: envoy
   < access-control-allow-origin: *
   access-control-allow-origin: *
   < access-control-allow-credentials: true
   access-control-allow-credentials: true
   < x-envoy-upstream-service-time: 2416
   x-envoy-upstream-service-time: 2416
   < 

   {
     "headers": {
       "Accept": "*/*", 
       "Host": "httpbin.org", 
       "User-Agent": "curl/8.7.1", 
       "X-Amzn-Trace-Id": "Root=1-6859932a-1fb1dc706dadcc183b407d4d", 
       "X-Envoy-Expected-Rq-Timeout-Ms": "15000", 
      "X-Envoy-External-Address": "10.0.15.215"
     }
   }   
   ```

## Cleanup

{{< reuse "docs/snippets/cleanup.md" >}}

```sh
kubectl delete httproute httpbin-rewrite -n httpbin
kubectl delete httproute backend-rewrite 
kubectl delete backend httpbin
```
