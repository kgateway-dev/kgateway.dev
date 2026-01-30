<!-- you could potentially also create the HTTPRoute without the annotation, do the curl and verify that you see the 302 redirect code. Then, you apply the HTTPRoute with the annotation, do the same curl and now you get back a 307 response code -->

Create custom HTTP redirect status codes.

For more information, see the [{{< reuse "docs/snippets/k8s-gateway-api-name.md" >}} documentation](https://gateway-api.sigs.k8s.io/reference/spec/#gateway.networking.k8s.io/v1.HTTPRequestRedirectFilter).

## Before you begin

{{< reuse "docs/snippets/prereq.md" >}}


## Setting custom HTTP redirect status codes

Use the `kgateway.dev/http-redirect-status-code` annotation to configure allowed HTTP redirect status codes. The annotation overrides any redirect codes that are set in the `RequestRedirect` filter on the HTTPRoute. 

1. Create an HTTPRoute that redirects the `/get` and `/post` httpbin paths to the `/anything` path with a 302 HTTP redirect code. To override the path-specific redirect code with a 307 HTTP response code, you add the `kgateway.dev/http-redirect-status-code` annotation. 

   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.networking.k8s.io/v1
   kind: HTTPRoute
   metadata:
     name: httpbin-redirect
     namespace: httpbin
     annotations:
       kgateway.dev/http-redirect-status-code: "307"
   spec:
     parentRefs:
       - name: http
         namespace: {{< reuse "docs/snippets/namespace.md" >}}
     hostnames:
       - redirect.example
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
                 replacePrefixMatch: /anything
               statusCode: 302
       - matches:
           - path:
               type: PathPrefix
               value: /post
         filters:
           - type: RequestRedirect
             requestRedirect:
               path:
                 type: ReplacePrefixMatch
                 replacePrefixMatch: /anything
               statusCode: 302
   EOF
   ```

2. Send an HTTP request to the httpbin app on the `redirect.example` domain. Verify that you get back a 307 HTTP response code. 
   {{< tabs items="Cloud Provider LoadBalancer,Port-forward for local testing" tabTotal="2" >}}
   {{% tab tabName="Cloud Provider LoadBalancer" %}}
   ```sh
   curl -vik http://$INGRESS_GW_ADDRESS:8080/get -H "host: redirect.example"
   ```
   {{% /tab %}}
   {{% tab tabName="Port-forward for local testing" %}}
   ```sh
   curl -vi localhost:8080/get -H "host: redirect.example"
   ```
   {{% /tab %}}
   {{< /tabs >}}
   
   Example output: 
   ```
   * Mark bundle as not supporting multiuse
   < HTTP/1.1 307 Temporary Redirect
   HTTP/1.1 307 Temporary Redirect
   < location: http://redirect.example/anything
   location: http://redirect.example/anything
   < date: Mon, 06 Nov 2024 01:48:12 GMT
   date: Mon, 06 Nov 2024 01:48:12 GMT
   < content-length: 0
   content-length: 0
   ```


## Cleanup

{{< reuse "docs/snippets/cleanup.md" >}}
  
Remove the HTTPRoute.
```sh
kubectl delete httproute httpbin-redirect -n httpbin
```
