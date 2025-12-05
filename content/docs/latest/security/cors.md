---
title: CORS
weight: 10
description: Enforce client-site access controls with cross-origin resource sharing (CORS).
---

Enforce client-site access controls with cross-origin resource sharing (CORS).

{{< callout type="warning" >}} 
{{< reuse "docs/versions/warn-2-1-only.md" >}} {{< reuse "docs/versions/warn-experimental.md" >}}
{{< /callout >}}

## About CORS

Cross-Origin Resource Sharing (CORS) is a security feature that is implemented by web browsers and that controls how web pages in one domain can request and interact with resources that are hosted on a different domain. By default, web browsers only allow requests to resources that are hosted on the same domain as the web page that served the original request. Access to web pages or resources that are hosted on a different domain is restricted to prevent potential security vulnerabilities, such as cross-site request forgery (CRSF).

When CORS is enabled in a web browser and a request for a different domain comes in, the web browser checks whether this request is allowed or not. To do that, it typically sends a preflight request (HTTP `OPTIONS` method) to the server or service that serves the requested resource. The service returns the methods that are permitted to send the actual cross-origin request, such as GET, POST, etc. If the request to the different domain is allowed, the response includes CORS-specific headers that instruct the web browser how to make the cross-origin request. For example, the CORS headers typically include the origin that is allowed to access the resource, and the credentials or headers that must be included in the cross-origin request.

Note that the preflight request is optional. Web browsers can also be configured to send the cross-origin directly. However, access to the request resource is granted only if CORS headers were returned in the response. If no headers are returned during the preflight request, the web browser denies access to the resource in the other domain.

CORS policies are typically implemented to limit access to server resources for JavaScripts that are embedded in a web page, such as:

* A JavaScript on a web page at `example.com` tries to access a different domain, such as `api.com`.
* A JavaScript on a web page at `example.com` tries to access a different subdomain, such as `api.example.com`.
* A JavaScript on a web page at `example.com` tries to access a different port, such as `example.com:3001`.
* A JavaScript on a web page at `https://example.com` tries to access the resources by using a different protocol, such as `http://example.com`.

### Configuration options {#options}

You can configure the CORS policy at two levels:

* **HTTPRoute**: For the native way in Kubernetes Gateway API, configure a CORS policy in the HTTPRoute. You can choose to apply the CORS policy to all the routes that are defined in the HTTPRoute, or to a selection of `backendRefs`. This route-level policy takes precedence over any {{< reuse "docs/snippets/trafficpolicy.md" >}} CORS that you might configure. For more information, see the [Kubernetes Gateway API docs](https://gateway-api.sigs.k8s.io/reference/spec/#httpcorsfilter) and [CORS design docs](https://gateway-api.sigs.k8s.io/geps/gep-1767/).
* **{{< reuse "docs/snippets/trafficpolicy.md" >}}**: For more flexibility to reuse the CORS policy across HTTPRoutes, specific routes and Gateways, configure a CORS policy in the {{< reuse "docs/snippets/trafficpolicy.md" >}}. You can attach a {{< reuse "docs/snippets/trafficpolicy.md" >}} to a Gateway, all HTTPRoutes via `targetRefs`, or an individual route via `extensionRef`. To attach to a `backendRef`, use a CORS policy in the HTTPRoute instead. For more information about attachment and merging rules, see the [{{< reuse "docs/snippets/trafficpolicy.md" >}} concept docs](../../about/policies/trafficpolicy/).

## Before you begin

{{< reuse "docs/snippets/prereq-x-channel.md" >}}

## Set up CORS policies

Create a CORS policy for the httpbin app in an HTTPRoute or {{< reuse "docs/snippets/trafficpolicy.md" >}}.

{{< tabs tabTotal="2" items="CORS in HTTPRoute,CORS in TrafficPolicy" >}}
{{% tab tabName="CORS in HTTPRoute" %}}
Create an HTTPRoute resource for the httpbin app that applies a CORS filter. The following example allows requests from the `https://example.com/` origin.

```yaml
kubectl apply -f- <<EOF
apiVersion: gateway.networking.k8s.io/v1
kind: HTTPRoute
metadata:
  name: httpbin-cors
  namespace: httpbin
spec:
  parentRefs:
    - name: http
      namespace: {{< reuse "docs/snippets/namespace.md" >}}
  hostnames:
    - cors.example
  rules:
    - filters:
        - type: CORS
          cors:
            allowCredentials: true
            allowHeaders:
              - Origin               
            allowMethods:
              - GET
              - POST
              - OPTIONS               
            allowOrigins:
              - "https://example.com/"
            exposeHeaders:
            - Origin
            - X-HTTPRoute-Header
            maxAge: 86400
      backendRefs:
        - name: httpbin
          port: 8000
EOF
```
{{% /tab %}}
{{% tab tabName="CORS in GlooTrafficPolicy" %}}
1. Create a {{< reuse "docs/snippets/trafficpolicy.md" >}} resource for the httpbin app that applies a CORS filter. The following example allows requests from the `https://example.com/` origin.

   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: {{< reuse "docs/snippets/trafficpolicy-apiversion.md" >}}
   kind: {{< reuse "docs/snippets/trafficpolicy.md" >}}
   metadata:
     name: httpbin-cors
     namespace: httpbin
   spec:
     cors:
       allowCredentials: true
       allowHeaders:
         - "Origin"
         - "Authorization"
         - "Content-Type"             
       allowMethods:
         - "GET"
         - "POST"
         - "OPTIONS"               
       allowOrigins:
         - "https://example.com/"
       exposeHeaders:
       - "Origin"
       - "X-TrafficPolicy-Header"
       maxAge: 86400
   EOF
   ```

2. Attach the {{< reuse "docs/snippets/trafficpolicy.md" >}} to a route or Gateway. The following example creates an HTTPRoute for the httpbin app that has the {{< reuse "docs/snippets/trafficpolicy.md" >}} attached via the `extensionRef` filter. For more information about attachment and merging rules, see the [{{< reuse "docs/snippets/trafficpolicy.md" >}} concept docs](/docs/about/policies/trafficpolicy/).

   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.networking.k8s.io/v1
   kind: HTTPRoute
   metadata:
     name: httpbin-cors
     namespace: httpbin
   spec:
     parentRefs:
       - name: http
         namespace: {{< reuse "docs/snippets/namespace.md" >}}
     hostnames:
       - cors.example
     rules:
       - filters:
           - type: ExtensionRef
             extensionRef:
               group: {{< reuse "docs/snippets/trafficpolicy-group.md" >}}
               kind: {{< reuse "docs/snippets/trafficpolicy.md" >}}
               name: httpbin-cors
         backendRefs:
           - name: httpbin
             port: 8000
   EOF
   ```

{{% /tab %}}
{{< /tabs >}}

## Test CORS policies

Now that you have CORS policies applied via an HTTPRoute or {{< reuse "docs/snippets/trafficpolicy.md" >}}, you can test the policies.

1. Send a request to the httpbin app on the `cors.example` domain and use `https://example.com/` as the origin. Verify that your request succeeds and that you get back the configured CORS headers.
   
   {{< tabs tabTotal="2" items="Cloud Provider LoadBalancer,Port-forward for local testing" >}}
   {{% tab tabName="Cloud Provider LoadBalancer" %}}
   ```sh
   curl -I -X OPTIONS http://$INGRESS_GW_ADDRESS:8080/get -H "host: cors.example:8080" \
    -H "Origin: https://example.com/" \
    -H "Access-Control-Request-Method: POST" \
    -H "Access-Control-Request-Headers: Origin"
   ```
   {{% /tab %}}
   {{% tab tabName="Port-forward for local testing" %}}
   ```sh
   curl -I -X OPTIONS GET localhost:8080/headers -H "host: cors.example:8080" \
    -H "Origin: https://example.com/" \
    -H "Access-Control-Request-Method: POST" \
    -H "Access-Control-Request-Headers: Origin"
   ```
   {{% /tab %}}
   {{< /tabs >}}
   
   Example output: Notice that the `access-control-*` values reflect your CORS policy and change depending on the resources that you created.
   * If you created an HTTPRoute with a CORS filter, you see the `Origin` and `X-HTTPRoute-Header` headers.
   * If you created a TrafficPolicy with a CORS filter, you see the `Origin` and `X-TrafficPolicy-Header` headers.

   {{< tabs tabTotal="2" items="CORS in HTTPRoute,CORS in TrafficPolicy" >}}
   {{% tab tabName="CORS in HTTPRoute" %}}

   ```console {hl_lines=[7,8,9]}
   HTTP/1.1 200 OK
   x-correlation-id: aaaaaaaa
   date: Tue, 24 Jun 2025 13:19:53 GMT
   content-length: 0
   
   HTTP/1.1 200 OK
   access-control-allow-origin: https://example.com/
   access-control-allow-credentials: true
   access-control-allow-methods: GET, POST, OPTIONS
   access-control-allow-headers: Origin, Authorization, Content-Type
   access-control-max-age: 86400
   access-control-expose-headers: Origin, X-HTTPRoute-Header
   date: Tue, 24 Jun 2025 13:19:53 GMT
   server: envoy
   content-length: 0
   ...
   ```
   {{% /tab %}}
   {{% tab tabName="CORS in GlooTrafficPolicy" %}}
   ```console {hl_lines=[7,8,9]}
   HTTP/1.1 200 OK
   x-correlation-id: aaaaaaaa
   date: Tue, 24 Jun 2025 13:19:53 GMT
   content-length: 0
   
   HTTP/1.1 200 OK
   access-control-allow-origin: https://example.com/
   access-control-allow-credentials: true
   access-control-allow-methods: GET, POST, OPTIONS
   access-control-allow-headers: Origin, Authorization, Content-Type
   access-control-max-age: 86400
   access-control-expose-headers: Origin, X-TrafficPolicy-Header
   date: Tue, 24 Jun 2025 13:19:53 GMT
   server: envoy
   content-length: 0
   ```
   {{% /tab %}}
   {{< /tabs >}}

2. Send another request to the httpbin app. This time, you use `notallowed.com` as your origin. Although the request succeeds, you do not get back your configured CORS settings such as max age, allowed orgin, or allowed methods, because `notallowed.com` is not configured as a supported origin.  
   
   {{< tabs tabTotal="2" items="Cloud Provider LoadBalancer,Port-forward for local testing" >}}
   {{% tab tabName="Cloud Provider LoadBalancer" %}}
   ```sh
   curl -I -X OPTIONS http://$INGRESS_GW_ADDRESS:8080/get -H "host: cors.example:8080" \
    -H "Origin: https://notallowed.com/" \
    -H "Access-Control-Request-Method: POST" \
    -H "Access-Control-Request-Headers: Origin"
   ```
   {{% /tab %}}
   {{% tab tabName="Port-forward for local testing" %}}
   ```sh
   curl -I -X OPTIONS GET localhost:8080/headers -H "host: cors.example:8080" \
    -H "Origin: https://notallowed.com/" \
    -H "Access-Control-Request-Method: POST" \
    -H "Access-Control-Request-Headers: Origin"
   ```
   {{% /tab %}}
   {{< /tabs >}}
   
   Example output: 
   ```console
   HTTP/1.1 200 OK
   x-correlation-id: aaaaaaaa
   date: Tue, 24 Jun 2025 13:21:20 GMT
   content-length: 0
   
   HTTP/1.1 200 OK
   access-control-allow-credentials: true
   access-control-allow-headers: Origin
   access-control-allow-methods: GET, POST, HEAD, PUT, DELETE, PATCH, OPTIONS
   access-control-allow-origin: https://notallowed.com/
   access-control-max-age: 3600
   date: Tue, 24 Jun 2025 13:21:20 GMT
   content-length: 0
   x-envoy-upstream-service-time: 1
   server: envoy
   ```

## Cleanup

{{< reuse "docs/snippets/cleanup.md" >}}

{{< tabs tabTotal="2" items="CORS in HTTPRoute,CORS in TrafficPolicy" >}}
{{% tab tabName="CORS in HTTPRoute" %}}
```sh
kubectl delete httproute httpbin-cors -n httpbin
```
{{% /tab %}}
{{% tab tabName="CORS in GlooTrafficPolicy" %}}
```sh
kubectl delete httproute httpbin-cors -n httpbin
kubectl delete {{< reuse "docs/snippets/trafficpolicy.md" >}} httpbin-cors -n httpbin
```
{{% /tab %}}
{{< /tabs >}}
