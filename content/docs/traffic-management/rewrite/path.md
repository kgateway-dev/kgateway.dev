---
title: Path rewrites
weight: 462
description: Rewrite path prefixes in requests. 
---

Rewrite path prefixes in requests. 

For more information, see the [{{< reuse "docs/snippets/k8s-gateway-api-name.md" >}} documentation](https://gateway-api.sigs.k8s.io/api-types/httproute/#filters-optional).

## Before you begin

{{< reuse "docs/snippets/prereq.md" >}}

## Rewrite prefix path

Path rewrites use the HTTP path modifier to rewrite <!--either an entire path or -->path prefixes. 

1. Create a RouteOption resource to define your rewrite rules. In the following example all incoming request paths are rewritten to the `/anything` path.
   ```yaml
   kubectl apply -n httpbin -f- <<EOF
   apiVersion: gateway.kgateway.dev/v1alpha1
   kind: RouteOption
   metadata:
     name: rewrite
     namespace: httpbin
   spec:
     options:
       prefixRewrite: '/anything'
   EOF
   ```

2. Create an HTTPRoute resource for the httpbin app that references the RouteOption resource that you created. In this example, all incoming requests that match the `/headers` path on the `rewrite.example` domain are rewritten according to the rules that are defined in the RouteOption resource.
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
             type: Exact
             value: /headers
         filters:
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

4. Optional: Clean up the resources that you created. 
   ```sh
   kubectl delete routeoption rewrite -n httpbin
   kubectl delete httproute httpbin-rewrite -n httpbin
   ```
 
## Rewrite full or prefix path with regex

1. Create a RouteOption resource to define your rewrite rules. In the following example all incoming request paths are evaluated against the regex pattern. If `headers` is part of the request path, it is replaced with `anything`. 
   ```yaml
   kubectl apply -n httpbin -f- <<EOF
   apiVersion: gateway.kgateway.dev/v1alpha1
   kind: RouteOption
   metadata:
     name: rewrite
     namespace: httpbin
   spec:
     options:
       regexRewrite: 
         pattern:
           regex: 'headers'
         substitution: 'anything'
   EOF
   ```

2. Create an HTTPRoute resource for the httpbin app that references the RouteOption resource that you created. In this example, all incoming requests along the `/headers` path on the `rewrite.example` domain are evaluated against the regex pattern that you defined in the RouteOption resource.  
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
             type: Exact
             value: /headers
         filters:
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

4. Optional: Clean up the resources that you created. 
   ```sh
   kubectl delete routeoption rewrite -n httpbin
   kubectl delete httproute httpbin-rewrite -n httpbin
   ```