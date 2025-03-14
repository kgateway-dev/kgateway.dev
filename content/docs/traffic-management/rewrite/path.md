---
title: Path rewrites
weight: 462
description: Rewrite path prefixes in requests. 
---

Rewrite path prefixes in requests by using the `URLRewrite` filter. 

For more information, see the [{{< reuse "docs/snippets/k8s-gateway-api-name.md" >}} documentation](https://gateway-api.sigs.k8s.io/reference/spec/#gateway.networking.k8s.io/v1.HTTPURLRewriteFilter).

## Before you begin

{{< reuse "docs/snippets/prereq.md" >}}

## Rewrite prefix path

Path rewrites use the [HTTPPathModifier](https://gateway-api.sigs.k8s.io/reference/spec/#gateway.networking.k8s.io/v1.HTTPPathModifierType) to rewrite either an entire path or path prefixes. 

### Rewrite prefix path

1. Create an HTTPRoute resource for the httpbin app that configures an `URLRewrite` filter to rewrite prefix paths. In this example, all incoming requests that match the `/headers` prefix path on the `rewrite.example` domain are rewritten to the `/anything` prefix path. 
    
   Because the `ReplacePrefixPath` path modifier is used, only the path prefix is replaced during the rewrite. For example, requests to `http://rewrite.example/headers` are rewritten to `https://rewrite.example/anything`. However, for longer paths, such as in `http://rewrite.example/headers/200`, only the prefix is replaced and the path is rewritten to `http://rewrite.example/anything/200`. 
   
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
       - matches:
         - path:
             type: PathPrefix
             value: /headers
         filters:
           - type: URLRewrite
             urlRewrite:
               path:
                 type: ReplacePrefixMatch
                 replacePrefixMatch: /anything
         backendRefs:
           - name: httpbin
             port: 8000
   EOF
   ```
   
   |Setting|Description|
   |--|--|
   |`spec.parentRefs`| The name and namespace of the Gateway that serves this HTTPRoute. In this example, you use the `http` gateway that was created as part of the get started guide. |
   |`spec.rules.filters.type`| The type of filter that you want to apply to incoming requests. In this example, the `URLRewrite` filter is used.|
   |`spec.rules.filters.urlRewrite.path.type`| The type of HTTPPathModifier that you want to use. In this example, `ReplacePrefixMatch` is used, which replaces only the path prefix.  |
   | `spec.rules.filters.urlRewrite.path.replacePrefixMatch` | The path prefix you want to rewrite to. In this example, you replace the prefix path with the `/anything` prefix path. | 
   |`spec.rules.backendRefs`|The backend destination you want to forward traffic to. In this example, all traffic is forwarded to the httpbin app that you set up as part of the get started guide. |

2. Send a request to the httpbin app along the `/headers` path on the `rewrite.example` domain. Verify that you get back a 200 HTTP response code and that your request is rewritten to the `/anything` path. 
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
   "origin": "10.0.9.36:50660",
   "url": "http://rewrite.example:8080/anything",
   "data": "",
   "files": null,
   "form": null,
   "json": null
   ...
   ```

3. Send another request to the httpbin app. This time, you send it along the `/headers/200` path on the `rewrite.example` domain. Verify that you get back a 200 HTTP response code and that your request path is rewritten to `/anything/200`.  
   {{< tabs items="Cloud Provider LoadBalancer,Port-forward for local testing" >}}
   {{% tab %}}
   ```sh
   curl -vik http://$INGRESS_GW_ADDRESS:8080/headers/200 -H "host: rewrite.example:8080"
   ```
   {{% /tab %}}
   {{% tab %}}
   ```sh
   curl -vik localhost:8080/headers/200 -H "host: rewrite.example"
   ```
   {{% /tab %}}
   {{< /tabs >}}
   
   Example output: 
   ```
   ...
   "origin": "10.0.9.36:50660",
   "url": "http://rewrite.example:8080/anything/200",
   "data": "",
   "files": null,
   "form": null,
   "json": null
   ...
   ```

4. Optional: Clean up the HTTPRoute that you created. 
   ```sh
   kubectl delete httproute httpbin-rewrite -n httpbin
   ```

### Rewrite full path

1. Create an HTTPRoute resource for the httpbin app that configures an `URLRewrite` filter to rewrite prefix paths. In this example, all incoming requests that match the `/headers` prefix path on the `rewrite.example` domain are rewritten to `/anything`. 
    
   Because the `ReplaceFullPath` path modifier is used, requests to `http://rewrite.example/headers` and `http://rewrite.example/headers/200` both are rewritten to `https://rewrite.example/anything`.
   
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
       - matches:
         - path:
             type: PathPrefix
             value: /headers
         filters:
           - type: URLRewrite
             urlRewrite:
               path:
                 type: ReplaceFullPath
                 replaceFullPath: /anything
         backendRefs:
           - name: httpbin
             port: 8000
   EOF
   ```
   
   |Setting|Description|
   |--|--|
   |`spec.parentRefs`| The name and namespace of the Gateway that serves this HTTPRoute. In this example, you use the `http` gateway that was created as part of the get started guide. |
   |`spec.rules.filters.type`| The type of filter that you want to apply to incoming requests. In this example, the `URLRewrite` filter is used.|
   |`spec.rules.filters.urlRewrite.path.type`| The type of HTTPPathModifier that you want to use. In this example, `ReplaceFullPath` is used, which replaces the full path prefix.  |
   | `spec.rules.filters.urlRewrite.path.replaceFullPath` | The path prefix you want to rewrite to. In this example, you replace the full prefix path with the `/anything` prefix path. | 
   |`spec.rules.backendRefs`|The backend destination you want to forward traffic to. In this example, all traffic is forwarded to the httpbin app that you set up as part of the get started guide. |

3. Send a request to the httpbin app along the `/headers` path on the `rewrite.example` domain. Verify that you get back a 200 HTTP response code and that your request is rewritten to the `/anything` path. 
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
   "origin": "10.0.9.36:50660",
   "url": "http://rewrite.example:8080/anything",
   "data": "",
   "files": null,
   "form": null,
   "json": null
   ...
   ```

4. Send another request to the httpbin app. This time, you send it along the `/headers/200` path on the `rewrite.example` domain. Verify that you also get back a 200 HTTP response code and that the full path is rewritten to the `/anything` path. 
   {{< tabs items="Cloud Provider LoadBalancer,Port-forward for local testing" >}}
   {{% tab %}}
   ```sh
   curl -vik http://$INGRESS_GW_ADDRESS:8080/headers/200 -H "host: rewrite.example:8080"
   ```
   {{% /tab %}}
   {{% tab %}}
   ```sh
   curl -vik localhost:8080/headers/200 -H "host: rewrite.example"
   ```
   {{% /tab %}}
   {{< /tabs >}}
   
   Example output: 
   ```
   ...
   "origin": "10.0.9.36:50660",
   "url": "http://rewrite.example:8080/anything",
   "data": "",
   "files": null,
   "form": null,
   "json": null
   ...
   ```

5. Optional: Clean up the HTTPRoute that you created. 
   ```sh
   kubectl delete httproute httpbin-rewrite -n httpbin
   ```
