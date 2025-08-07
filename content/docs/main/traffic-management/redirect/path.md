---
title: Path redirects
weight: 443
description: Redirect requests to a different path prefix. 
---

Redirect requests to a different path prefix. 

For more information, see the [{{< reuse "docs/snippets/k8s-gateway-api-name.md" >}} documentation](https://gateway-api.sigs.k8s.io/reference/spec/#gateway.networking.k8s.io/v1.HTTPRequestRedirectFilter).

## Before you begin

{{< reuse "docs/snippets/prereq.md" >}}
## Set up path redirects

Path redirects use the HTTP path modifier to replace either an entire path or path prefixes. 

### Replace prefix path

1. Create an HTTPRoute for the httpbin app. In the following example, requests to the `/get` path are redirected to the `/status/200` path, and a 302 HTTP response code is returned to the user.

   Because the `ReplacePrefixPath` path modifier is used, only the path prefix is replaced during the redirect. For example, requests to `http://path.redirect.example/get` result in the `https://path.redirect.example/status/200` redirect location. However, for longer paths, such as in `http://path.redirect.example/get/headers`, only the prefix is replaced and a redirect location of `https://path.redirect.example/status/200/headers` is returned.

   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.networking.k8s.io/v1
   kind: HTTPRoute
   metadata:
     name: httpbin-redirect
     namespace: httpbin
   spec:
     parentRefs:
       - name: http
         namespace: {{< reuse "docs/snippets/namespace.md" >}}
     hostnames:
       - path.redirect.example
     rules:
       - matches:
           - path:
               type: PathPrefix
               value: /get
         filters:
           - type: RequestRedirect
             requestRedirect:
               path:
                 type: ReplacePrefixMatch
                 replacePrefixMatch: /status/200
               statusCode: 302
   EOF
   ```

   |Setting|Description|
   |--|--|
   |`spec.parentRefs.name` </br> `spec.parentRefs.namespace`|The name and namespace of the Gateway resource that serves the route. In this example, you use the Gateway that you created earlier. |
   |`spec.hostnames`| The hostname for which you want to apply the redirect.|
   |`spec.rules.matches.path`|The prefix path that you want to redirect. In this example, you want to redirect all requests to the `/get` path. |
   |`spec.rules.filters.type`|The type of filter that you want to apply to incoming requests. In this example, the `RequestRedirect` is used.|
   |`spec.rules.filters.requestRedirect.path.type`|The type of path modifier that you want to apply. In this example, you want to replace only the prefix path.  |
   |`spec.rules.filters.requestRedirect.path.replacePrefixPath`|The prefix path you want to redirect to. In this example, all requests to the `/get` prefix path are redirected to the `/status/200` prefix path.  |
   |`spec.rules.filters.requestRedirect.statusCode`| The HTTP status code that you want to return to the client in case of a redirect. For non-permanent redirects, use the 302 HTTP response code. |

2. Send a request to the httpbin app on the `path.redirect.example` domain. Verify that you get back a 302 HTTP response code and the `path.redirect.example:8080/status/200` redirect location. 
   {{< tabs items="Cloud Provider LoadBalancer,Port-forward for local testing" tabTotal="2"  >}}
   {{% tab tabName="Cloud Provider LoadBalancer" %}}
   ```sh
   curl -vi http://$INGRESS_GW_ADDRESS:8080/get -H "host: path.redirect.example:8080"
   ```
   {{% /tab %}}
   {{% tab tabName="Port-forward for local testing" %}}
   ```sh
   curl -vi localhost:8080/get -H "host: path.redirect.example"
   ```
   {{% /tab %}}
   {{< /tabs >}}

   Example output: 
   ```
   * Mark bundle as not supporting multiuse
   < HTTP/1.1 302 Found
   HTTP/1.1 302 Found
   < location: http://path.redirect.example:8080/status/200
   location: http://path.redirect.example:8080/status/200
   < server: envoy
   server: envoy
   < content-length: 0
   content-length: 0
   ```

3. Send another request to the httpbin app on the `path.redirect.example` domain. This time, you send the request to the `/get/headers` path. Verify that you get back a 302 HTTP response code and the redirect location `path.redirect.example:8080/status/200/headers`. 
   {{< tabs items="Cloud Provider LoadBalancer,Port-forward for local testing" tabTotal="2" >}}
   {{% tab tabName="Cloud Provider LoadBalancer" %}}
   ```sh
   curl -vi http://$INGRESS_GW_ADDRESS:8080/get/headers -H "host: path.redirect.example:8080"
   ```
   {{% /tab %}}
   {{% tab tabName="Port-forward for local testing" %}}
   ```sh
   curl -vi localhost:8080/get/headers -H "host: path.redirect.example"
   ```
   {{% /tab %}}
   {{< /tabs >}}

   Example output: 
   ```
   * Mark bundle as not supporting multiuse
   < HTTP/1.1 302 Found
   HTTP/1.1 302 Found
   < location: http://path.redirect.example:8080/status/200/headers
   location: http://path.redirect.example:8080/status/200/headers
   < server: envoy
   server: envoy
   < content-length: 0
   content-length: 0
   ```

### Replace full path

1. Create an HTTPRoute for the httpbin app. In the following example, requests to the `/get` path are redirected to the `/status/200` path, and a 302 HTTP response code is returned to the user.

   Because the `ReplaceFullPath` path modifier is used, requests to `http://path.redirect.example/get` and `http://path.redirect.example/get/headers` both receive `https://path.redirect.example/status/200` as the redirect location.

   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.networking.k8s.io/v1
   kind: HTTPRoute
   metadata:
     name: httpbin-redirect
     namespace: httpbin
   spec:
     parentRefs:
       - name: http
         namespace: {{< reuse "docs/snippets/namespace.md" >}}
     hostnames:
       - path.redirect.example
     rules:
       - matches:
           - path:
               type: PathPrefix
               value: /get
         filters:
           - type: RequestRedirect
             requestRedirect:
               path:
                 type: ReplaceFullPath
                 replaceFullPath: /status/200
               statusCode: 302
   EOF
   ```

   |Setting|Description|
   |--|--|
   |`spec.parentRefs.name` </br> `spec.parentRefs.namespace` |The name and namespace of the Gateway resource that serves the route. In this example, you use the Gateway that you created earlier. |
   |`spec.hostnames`| The hostname for which you want to apply the redirect.|
   |`spec.rules.matches.path`|The prefix path that you want to redirect. In this example, you want to redirect all requests to the `/get` path. |
   |`spec.rules.filters.type`|The type of filter that you want to apply to incoming requests. In this example, the `RequestRedirect` is used.|
   |`spec.rules.filters.requestRedirect.path.type`|The type of path modifier that you want to apply. In this example, you want to replace the full path..  |
   |`spec.rules.filters.requestRedirect.path.replaceFullPath`|The path that you want to redirect to. In this example, all requests to the `/get` prefix path are redirected to the `/status/200` prefix path.  |
   |`spec.rules.filters.requestRedirect.statusCode`| The HTTP status code that you want to return to the client in case of a redirect. For non-permanent redirects, use the 302 HTTP response code. |

2. Send a request to the httpbin app on the `path.redirect.example` domain. Verify that you get back a 302 HTTP response code and the redirect location `path.redirect.example:8080/status/200`. 
   {{< tabs items="Cloud Provider LoadBalancer,Port-forward for local testing" tabTotal="2" >}}
   {{% tab tabName="Cloud Provider LoadBalancer" %}}
   ```sh
   curl -vi http://$INGRESS_GW_ADDRESS:8080/get -H "host: path.redirect.example:8080"
   ```
   {{% /tab %}}
   {{% tab tabName="Port-forward for local testing" %}}
   ```sh
   curl -vi localhost:8080/get -H "host: path.redirect.example"
   ```
   {{% /tab %}}
   {{< /tabs >}}

   Example output: 
   ```
   * Mark bundle as not supporting multiuse
   < HTTP/1.1 302 Found
   HTTP/1.1 302 Found
   < location: http://path.redirect.example:8080/status/200
   location: http://path.redirect.example:8080/status/200
   < server: envoy
   server: envoy
   < content-length: 0
   content-length: 0
   ```

3. Send another request to the httpbin app on the `path.redirect.example` domain. This time, you send the request to the `/get/headers` path. Verify that you get back a 302 HTTP response code and the same redirect location as in the previous example (`path.redirect.example:8080/status/200`). 
   {{< tabs items="Cloud Provider LoadBalancer,Port-forward for local testing" tabTotal="2"  >}}
   {{% tab tabName="Cloud Provider LoadBalancer" %}}
   ```sh
   curl -vi http://$INGRESS_GW_ADDRESS:8080/get/headers -H "host: path.redirect.example:8080"
   ```
   {{% /tab %}}
   {{% tab tabName="Port-forward for local testing" %}}
   ```sh
   curl -vi localhost:8080/get/headers -H "host: path.redirect.example"
   ```
   {{% /tab %}}
   {{< /tabs >}}

   Example output: 
   ```
   * Mark bundle as not supporting multiuse
   < HTTP/1.1 302 Found
   HTTP/1.1 302 Found
   < location: http://path.redirect.example:8080/status/200
   location: http://path.redirect.example:8080/status/200
   < server: envoy
   server: envoy
   < content-length: 0
   content-length: 0
   ```

## Cleanup

{{< reuse "docs/snippets/cleanup.md" >}}
  
```sh
kubectl delete httproute httpbin-redirect -n httpbin
```