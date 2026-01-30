Rewrite path prefixes in requests by using the `URLRewrite` filter. 

For more information, see the [{{< reuse "docs/snippets/k8s-gateway-api-name.md" >}} documentation](https://gateway-api.sigs.k8s.io/reference/spec/#gateway.networking.k8s.io/v1.HTTPURLRewriteFilter).

## Before you begin

{{< reuse "docs/snippets/prereq.md" >}}

## Rewrite prefix path

Use the [HTTPPathModifier](https://gateway-api.sigs.k8s.io/reference/spec/#gateway.networking.k8s.io/v1.HTTPPathModifierType) to rewrite path prefixes. 

### In-cluster services

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
       namespace: {{< reuse "docs/snippets/namespace.md" >}}
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
   {{< tabs items="Cloud Provider LoadBalancer,Port-forward for local testing" tabTotal="2"  >}}
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
   ```console {hl_lines=[3]}
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
   {{< tabs items="Cloud Provider LoadBalancer,Port-forward for local testing" tabTotal="2"  >}}
   {{% tab tabName="Cloud Provider LoadBalancer" %}}
   ```sh
   curl -vi http://$INGRESS_GW_ADDRESS:8080/headers/200 -H "host: rewrite.example:8080"
   ```
   {{% /tab %}}
   {{% tab tabName="Port-forward for local testing" %}}
   ```sh
   curl -vi localhost:8080/headers/200 -H "host: rewrite.example"
   ```
   {{% /tab %}}
   {{< /tabs >}}
   
   Example output: 
   ```console {hl_lines=[3]}
   ...
   "origin": "10.0.9.36:50660",
   "url": "http://rewrite.example:8080/anything/200",
   "data": "",
   "files": null,
   "form": null,
   "json": null
   ...
   ```

### External services

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
   
2. Create an HTTPRoute resource that matches incoming traffic on the `/headers` path for the `external-rewrite.example` domain and forwards traffic to the Backend that you created. Because the Backend expects a different domain, you use the `URLRewrite` filter to rewrite the hostname from `external-rewrite.example` to `httpbin.org`. In addition, you rewrite the `/headers` path prefix to `/anything`. 
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
        - matches:
          - path:
              type: PathPrefix
              value: /headers
          filters:
          - type: URLRewrite
            urlRewrite:
              hostname: "httpbin.org"
              path: 
                type: ReplacePrefixMatch
                replacePrefixMatch: /anything   
          backendRefs:
          - name: httpbin
            kind: Backend
            group: gateway.kgateway.dev
   EOF
   ```

2. Send a request to the `external-rewrite.example` domain on the `/headers` path. Verify that you get back a 200 HTTP response code and that the request was rewritten to `httpbin.org/anything`. 
   
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
   ```console {hl_lines=[2,3,25,34]}
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
     "args": {}, 
     "data": "", 
    "files": {}, 
     "form": {}, 
     "headers": {
       "Accept": "*/*", 
       "Host": "httpbin.org", 
       "User-Agent": "curl/8.7.1", 
       "X-Amzn-Trace-Id": "Root=1-68599cdc-5d3c0d9a1ac2aa482effb24b", 
       "X-Envoy-Expected-Rq-Timeout-Ms": "15000", 
       "X-Envoy-External-Address": "10.0.15.215", 
       "X-Envoy-Original-Path": "/"
     }, 
     "json": null, 
     "method": "GET", 
     "url": "http://httpbin.org/anything"
   }
   ```


## Rewrite full path

Use the [HTTPPathModifier](https://gateway-api.sigs.k8s.io/reference/spec/#gateway.networking.k8s.io/v1.HTTPPathModifierType) to rewrite full paths. 

### In-cluster services

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
       namespace: {{< reuse "docs/snippets/namespace.md" >}}
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
   {{< tabs items="Cloud Provider LoadBalancer,Port-forward for local testing" tabTotal="2">}}
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
   ```console {hl_lines=[3]}
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
   {{< tabs items="Cloud Provider LoadBalancer,Port-forward for local testing" tabTotal="2"  >}}
   {{% tab tabName="Cloud Provider LoadBalancer" %}}
   ```sh
   curl -vi http://$INGRESS_GW_ADDRESS:8080/headers/200 -H "host: rewrite.example:8080"
   ```
   {{% /tab %}}
   {{% tab tabName="Port-forward for local testing" %}}
   ```sh
   curl -vi localhost:8080/headers/200 -H "host: rewrite.example"
   ```
   {{% /tab %}}
   {{< /tabs >}}
   
   Example output: 
   ```console {hl_lines=[3]}
   ...
   "origin": "10.0.9.36:50660",
   "url": "http://rewrite.example:8080/anything",
   "data": "",
   "files": null,
   "form": null,
   "json": null
   ...
   ```

### External services

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
   
2. Create an HTTPRoute resource that matches incoming traffic on the `external-rewrite.example` domain and forwards traffic to the Backend that you created. Because the Backend expects a different domain, you use the `URLRewrite` filter to rewrite the hostname from `external-rewrite.example` to `httpbin.org`. In addition, you rewrite any existing paths to `/anything`. 
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
              path:
                type: ReplaceFullPath
                replaceFullPath: /anything 
          backendRefs:
          - name: httpbin
            kind: Backend
            group: gateway.kgateway.dev
   EOF
   ```

2. Send a request to the `external-rewrite.example` domain on the `/header` path. Verify that you get back a 200 HTTP response code and that the request was rewritten to `httpbin.org/anything`. 
   
   {{< tabs items="Cloud Provider LoadBalancer,Port-forward for local testing" tabTotal="2" >}}
   {{% tab tabName="Cloud Provider LoadBalancer" %}}
   ```sh
   curl -vi http://$INGRESS_GW_ADDRESS:8080/header -H "host: external-rewrite.example:8080"
   ```
   {{% /tab %}}
   {{% tab tabName="Port-forward for local testing" %}}
   ```sh
   curl -vi localhost:8080/header -H "host: external-rewrite.example"
   ```
   {{% /tab %}}
   {{< /tabs >}}
   
   Example output: 
   ```console {hl_lines=[2,3,25,34]}
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
     "args": {}, 
     "data": "", 
    "files": {}, 
     "form": {}, 
     "headers": {
       "Accept": "*/*", 
       "Host": "httpbin.org", 
       "User-Agent": "curl/8.7.1", 
       "X-Amzn-Trace-Id": "Root=1-68599cdc-5d3c0d9a1ac2aa482effb24b", 
       "X-Envoy-Expected-Rq-Timeout-Ms": "15000", 
       "X-Envoy-External-Address": "10.0.15.215", 
       "X-Envoy-Original-Path": "/"
     }, 
     "json": null, 
     "method": "GET", 
     "url": "http://httpbin.org/anything"
   }
   ```

## Regex rewrite

Use a {{< reuse "docs/snippets/trafficpolicy.md" >}} to rewrite full paths with a regular expression (regex). The regex pattern and substitution that you define must follow the [RE2 syntax](https://github.com/google/re2/wiki/Syntax).

### In-cluster services

1. Create an HTTPRoute resource that routes incoming requests on the `rewrite.example` domain to the httpbin app. 

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
       - matches:
         - path:
             type: PathPrefix
             value: /
         backendRefs:
           - name: httpbin
             port: 8000
   EOF
   ```

2. Create a {{< reuse "docs/snippets/trafficpolicy.md" >}} to define your path rewrite rules by using regular expressions. The following policy finds a path that matches the `^/anything/stores/(.*)/entities` pattern, such as: 
   * **Allowed**: `/anything/stores/us/entities` or `/anything/stores/dummy/entities`
   * **Not allowed**: `/anything/stores/us/buildings` or `/get/stores/us/entities` 
   
   Note that the `pattern` regex must match the entire request path. For example, if you want to replace only a portion of the request path, you must still capture the entire with, such as with a `/([^/]+)/([^/]+)/([^/]+)/([^/]+)` pattern. If a matching path is found, it is rewritten to the `substitution` value. In this example, the path is rewritten to the `/anything/rewrite/path`/ path. 
   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: {{< reuse "/docs/snippets/trafficpolicy-apiversion.md" >}}
   kind: {{< reuse "/docs/snippets/trafficpolicy.md" >}}
   metadata:
     name: httpbin-rewrite-regex
     namespace: httpbin
   spec:
     targetRefs:
     - group: gateway.networking.k8s.io
       kind: HTTPRoute
       name: httpbin-rewrite
     urlRewrite:
       pathRegex: 
         pattern: "^/anything/stores/(.*)/entities"
         substitution: "/anything/rewrite/path"
   EOF
   ```

3. Send a request to the httpbin app along the `/anything/stores/us/entities` path that matches the regex pattern in your {{< reuse "/docs/snippets/trafficpolicy.md" >}}. Verify that you get back a 200 HTTP response code and that your request is rewritten to the `/anything/rewrite/path` path. 
   {{< tabs items="Cloud Provider LoadBalancer,Port-forward for local testing" tabTotal="2">}}
   {{% tab tabName="Cloud Provider LoadBalancer" %}}
   ```sh
   curl -vi http://$INGRESS_GW_ADDRESS:8080/anything/stores/us/entities -H "host: rewrite.example:8080"
   ```
   {{% /tab %}}
   {{% tab tabName="Port-forward for local testing" %}}
   ```sh
   curl -vi localhost:8080/anything/stores/us/entities -H "host: rewrite.example"
   ```
   {{% /tab %}}
   {{< /tabs >}}
   
   Example output: 
   ```console {hl_lines=[3]}
   ...
   "origin": "10.0.9.36:50660",
   "url": "http://rewrite.example/anything/rewrite/path",
   "data": "",
   "files": null,
   "form": null,
   "json": null
   ...
   ```

4. Send another request to the httpbin app. This time, you send it along the `/anything/stores/us/buildings` path that does not match the regex pattern. Verify that you also get back a 200 HTTP response code and that the path **is not** rewritten to the `/anything/rewrite/path` path. 
   {{< tabs items="Cloud Provider LoadBalancer,Port-forward for local testing" tabTotal="2"  >}}
   {{% tab tabName="Cloud Provider LoadBalancer" %}}
   ```sh
   curl -vi http://$INGRESS_GW_ADDRESS:8080/anything/stores/us/buildings -H "host: rewrite.example"
   ```
   {{% /tab %}}
   {{% tab tabName="Port-forward for local testing" %}}
   ```sh
   curl -vi localhost:8080/anything/stores/us/buildings -H "host: rewrite.example"
   ```
   {{% /tab %}}
   {{< /tabs >}}
   
   Example output: 
   ```console {hl_lines=[3]}
   ...
   "origin": "10.0.9.36:50660",
   "url": "http://rewrite.example/anything/stores/us/buildings",
   "data": "",
   "files": null,
   "form": null,
   "json": null
   ...
   ```

### External services

1. Create a Backend that represents your external service. The following example creates a Backend for the `httpbin.org` domain. 
   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.kgateway.dev/v1alpha1
   kind: Backend
   metadata:
     name: httpbin
     namespace: httpbin
   spec:
     type: Static
     static:
       hosts:
         - host: httpbin.org
           port: 80
   EOF
   ```
   
2. Create an HTTPRoute resource that forwards traffic to the Backend that you created and rewrites the hostname from `external-rewrite.example` to `httpbin.org` that is expected by the Backend.
   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.networking.k8s.io/v1
   kind: HTTPRoute
   metadata:
     name: backend-rewrite
     namespace: httpbin
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

3. Create a {{< reuse "docs/snippets/trafficpolicy.md" >}} to define your path rewrite rules by using regular expressions. The following policy finds a path that matches the `^/anything/stores/(.*)/entities` pattern, such as: 
   * **Allowed**: `/anything/stores/us/entities` or `/anything/stores/dummy/entities`
   * **Not allowed**: `/anything/stores/us/buildings` or `/get/stores/us/entities` 
   
   Note that the `pattern` regex must match the entire request path. For example, if you want to replace only a portion of the request path, you must still capture the entire with, such as with a `/([^/]+)/([^/]+)/([^/]+)/([^/]+)` pattern. If a matching path is found, it is rewritten to the `substitution` value. In this example, the path is rewritten to the `/anything`/ path. 
   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: {{< reuse "/docs/snippets/trafficpolicy-apiversion.md" >}}
   kind: {{< reuse "/docs/snippets/trafficpolicy.md" >}}
   metadata:
     name: httpbin-rewrite-regex
     namespace: httpbin
   spec:
     targetRefs:
     - group: gateway.networking.k8s.io
       kind: HTTPRoute
       name: backend-rewrite
     urlRewrite:
       pathRegex: 
         pattern: "^/anything/stores/(.*)/entities"
         substitution: "/anything"
   EOF
   ```

4. Send a request to the `external-rewrite.example` domain on the `/anything/stores/us/entities` path. Verify that you get back a 200 HTTP response code and that the request path and host were rewritten to `httpbin.org/anything`. 
   
   {{< tabs items="Cloud Provider LoadBalancer,Port-forward for local testing" tabTotal="2" >}}
   {{% tab tabName="Cloud Provider LoadBalancer" %}}
   ```sh
   curl -vi http://$INGRESS_GW_ADDRESS:8080/anything/stores/us/entities -H "host: external-rewrite.example:8080"
   ```
   {{% /tab %}}
   {{% tab tabName="Port-forward for local testing" %}}
   ```sh
   curl -vi localhost:8080/anything/stores/us/entities -H "host: external-rewrite.example"
   ```
   {{% /tab %}}
   {{< /tabs >}}
   
   Example output: 
   ```console {hl_lines=[2,3,25,34]}
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
     "args": {}, 
     "data": "", 
    "files": {}, 
     "form": {}, 
     "headers": {
       "Accept": "*/*", 
       "Host": "httpbin.org", 
       "User-Agent": "curl/8.7.1", 
       "X-Amzn-Trace-Id": "Root=1-68599cdc-5d3c0d9a1ac2aa482effb24b", 
       "X-Envoy-Expected-Rq-Timeout-Ms": "15000", 
       "X-Envoy-External-Address": "10.0.15.215", 
       "X-Envoy-Original-Path": "/"
     }, 
     "json": null, 
     "method": "GET", 
     "url": "http://httpbin.org/anything"
   }
   ```

   
## Cleanup

{{< reuse "docs/snippets/cleanup.md" >}}

```sh
kubectl delete httproute httpbin-rewrite -n httpbin
kubectl delete backend httpbin -n httpbin
kubectl delete {{< reuse "docs/snippets/trafficpolicy.md" >}} httpbin-rewrite-regex -n httpbin
kubectl delete httproute backend-rewrite -n httpbin
```



