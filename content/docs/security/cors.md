---
title: CORS
weight: 10
description: Enforce client-site access controls with cross-origin resource sharing (CORS).
---

Enforce client-site access controls with cross-origin resource sharing (CORS).

{{% callout type="warning" %}} 
{{< reuse "docs/versions/warn-2-1-only.md" >}}
{{% /callout %}}

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

* HTTPRoute: For the native way in Kubernetes Gateway API, configure a CORS policy in the HTTPRoute. The policy is applied to all the routes that are defined in the HTTPRoute.This route-level policy takes precedence over any TrafficPolicy CORS that you might configure. For more information, see the [Kubernetes Gateway API docs](https://gateway-api.sigs.k8s.io/reference/spec/#httpcorsfilter) and [CORS design docs](https://gateway-api.sigs.k8s.io/geps/gep-1767/).
* TrafficPolicy: For more flexibility to reuse the CORS policy across HTTPRoutes, specific routes and Gateways, configure a CORS policy in the TrafficPolicy. For more information about attachment and merging rules, see the [TrafficPolicy concept docs](/docs/about/policies/trafficpolicy/).

## Before you begin

{{< reuse "docs/snippets/prereq.md" >}}

{{% callout type="info" %}} 
Some apps, such as `httpbin`, have built-in CORS policies that allow all origins. These policies take precedence over CORS policies that you might configure in kgateway. 
{{% /callout %}}

### Set up your environment to test CORS {#setup-env}

Set up the {{< reuse "docs/snippets/k8s-gateway-api-name.md" >}} CRDs and the Petstore app to test CORS policies.

1. Install the experimental channel of the {{< reuse "docs/snippets/k8s-gateway-api-name.md" >}} at version 1.3.0 or later so that you can use CORS.

   ```shell
   kubectl apply -f https://github.com/kubernetes-sigs/gateway-api/releases/download/v1.3.0/experimental-install.yaml
   ```

2. Deploy the sample Petstore app. You cannot use the sample httpbin app, because httpbin has built-in CORS policies that allow all origins. These policies take precedence over CORS policies that you configure in kgateway.
   
   ```sh
   kubectl apply -f https://raw.githubusercontent.com/kgateway-dev/kgateway.dev/refs/heads/main/assets/docs/examples/petstore.yaml
   ```
   
   Example output: 
   
   ```console
   deployment.apps/petstore created
   service/petstore created
   ```

3. Verify that the Petstore app is up and running. 
   
   ```sh
   kubectl get pods   
   ```
   
   Example output: 
   ```console                                                                              
   NAME                        READY   STATUS    RESTARTS   AGE
   petstore-66cddd5bb4-x7vdd   1/1     Running   0          26s
   ```


## Set up CORS policies

Create a CORS policy for the Petstore app in an HTTPRoute or TrafficPolicy.

{{< tabs items="CORS in HTTPRoute,CORS in TrafficPolicy" >}}
{{% tab %}}
Create an HTTPRoute resource for the Petstore app that applies a CORS filter. The following example allows requests from the `example.com/` and `*.example.com` origins.

```yaml
kubectl apply -f- <<EOF
apiVersion: gateway.networking.k8s.io/v1
kind: HTTPRoute
metadata:
  name: petstore-cors
  namespace: default
spec:
  parentRefs:
    - name: http
      namespace: kgateway-system
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
              - "https://example.com"
              - "https://*.example.com"
            exposeHeaders:
            - Origin
            - X-HTTPRoute-Header
            maxAge: 86400
      backendRefs:
        - name: petstore
          port: 8080
EOF
```
{{% /tab %}}
{{% tab %}}
1. Create a TrafficPolicy resource for the Petstore app that applies a CORS filter. The following example allows requests from the `example.com` and `*.example.com` origins.

   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.kgateway.dev/v1alpha1
   kind: TrafficPolicy
   metadata:
     name: petstore-cors
     namespace: default
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
         - "https://example.com"
         - "https://*.example.com"
       exposeHeaders:
       - "Origin"
       - "X-TrafficPolicy-Header"
       maxAge: 86400
   EOF
   ```

2. Attach the TrafficPolicy to a route or Gateway. The following example create an HTTPRoute for the Petstore app that has the TrafficPolicy attached. For more information about attachment and merging rules, see the [TrafficPolicy concept docs](/docs/about/policies/trafficpolicy/).

   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.networking.k8s.io/v1
   kind: HTTPRoute
   metadata:
     name: petstore-cors
     namespace: default
   spec:
     parentRefs:
       - name: http
         namespace: kgateway-system
     hostnames:
       - cors.example
     rules:
       - filters:
           - type: ExtensionRef
             extensionRef:
               group: gateway.kgateway.dev
               kind: TrafficPolicy
               name: petstore-cors
         backendRefs:
           - name: petstore
             port: 8080
   EOF
   ```

{{% /tab %}}
{{< /tabs >}}

## Test CORS policies

Now that you have CORS policies applied via an HTTPRoute or TrafficPolicy, you can test the policies.

1. Send a request to the Petstore app on the `cors.example` domain and use `https://example.com/` as the origin. Verify that your request succeeds and that you get back CORS headers, such as `access-control-allow-origin`, `access-control-allow-credentials`, and `access-control-expose-headers`. 
   
   {{< tabs items="LoadBalancer IP address or hostname,Port-forward for local testing" >}}
   {{% tab  %}}
   ```sh
   curl -v -X GET http://$INGRESS_GW_ADDRESS:8080/api/pets -H "host: cors.example:8080" \
    -H "Origin: https://example.com" -H "Access-Control-Request-Method: GET"
   ```
   {{% /tab %}}
   {{% tab  %}}
   ```sh
   curl -v -X GET localhost:8080/api/pets -H "host: cors.example:8080" \
    -H "Origin: https://example.com" -H "Access-Control-Request-Method: GET"
   ```
   {{% /tab %}}
   {{< /tabs >}}
   
   Example output: Notice that the `access-control-expose-headers` value changes depending on the resources that you created.
   * If you created an HTTPRoute with a CORS filter, you see the `Origin` and `X-HTTPRoute-Header` headers.
   * If you created a TrafficPolicy with a CORS filter, you see the `Origin` and `X-TrafficPolicy-Header` headers.

   {{< tabs items="CORS in HTTPRoute,CORS in TrafficPolicy" >}}
   {{% tab %}}

   ```console {hl_lines=[7,8,9]}
   * Mark bundle as not supporting multiuse
   < HTTP/1.1 200 OK
   < content-type: text/xml
   < date: Mon, 03 Jun 2024 17:05:31 GMT
   < content-length: 86
   < x-envoy-upstream-service-time: 7
   < access-control-allow-origin: https://example.com
   < access-control-allow-credentials: true
   < access-control-expose-headers: Origin, X-HTTPRoute-Header
   < server: envoy
   < 
   [{"id":1,"name":"Dog","status":"available"},{"id":2,"name":"Cat","status":"pending"}]
   ```
   {{% /tab %}}
   {{% tab  %}}
   ```console {hl_lines=[7,8,9]}
   * Mark bundle as not supporting multiuse
   < HTTP/1.1 200 OK
   < content-type: text/xml
   < date: Mon, 03 Jun 2024 17:05:31 GMT
   < content-length: 86
   < x-envoy-upstream-service-time: 7
   < access-control-allow-origin: https://example.com
   < access-control-allow-credentials: true
   < access-control-expose-headers: Origin, X-TrafficPolicy-Header
   < server: envoy
   < 
   [{"id":1,"name":"Dog","status":"available"},{"id":2,"name":"Cat","status":"pending"}]
   ```
   {{% /tab %}}
   {{< /tabs >}}

2. Send another request to the Petstore app. This time, you use `notallowed.com` as your origin. Although the request succeeds, you do not get back any CORS headers, because `notallowed.com` is not configured as a supported origin.  
   
   {{< tabs items="LoadBalancer IP address or hostname,Port-forward for local testing" >}}
   {{% tab %}}
   ```sh
   curl -v -X GET http://$INGRESS_GW_ADDRESS:8080/api/pets -H "host: cors.example:8080" \
    -H "Origin: https://notallowed.com/" -H "Access-Control-Request-Method: GET"
   ```
   {{% /tab %}}
   {{% tab  %}}
   ```sh
   curl -v -X GET localhost:8080/api/pets -H "host: cors.example:8080" \
    -H "Origin: https://notallowed.com/" -H "Access-Control-Request-Method: GET"
   ```
   {{% /tab %}}
   {{< /tabs >}}
   
   Example output: 
   ```console
   * Mark bundle as not supporting multiuse
   < HTTP/1.1 200 OK
   < content-type: text/xml
   < date: Mon, 03 Jun 2024 17:20:10 GMT
   < content-length: 86
   < x-envoy-upstream-service-time: 3
   < server: envoy
   < 
   [{"id":1,"name":"Dog","status":"available"},{"id":2,"name":"Cat","status":"pending"}]
   ```
   
## Cleanup

{{< reuse "docs/snippets/cleanup.md" >}}

{{< tabs items="CORS in HTTPRoute,CORS in TrafficPolicy" >}}
{{% tab %}}
```sh
kubectl delete -f https://raw.githubusercontent.com/kgateway-dev/kgateway.dev/refs/heads/{{< reuse "docs/versions/github-branch.md" >}}/assets/docs/examples/petstore.yaml
kubectl delete httproute petstore-cors -n default
```
{{% /tab %}}
{{% tab  %}}
```sh
kubectl delete -f https://raw.githubusercontent.com/kgateway-dev/kgateway.dev/refs/heads/{{< reuse "docs/versions/github-branch.md" >}}/assets/docs/examples/petstore.yaml
kubectl delete httproute petstore-cors -n default
kubectl delete trafficpolicy petstore-cors -n default
```
{{% /tab %}}
{{< /tabs >}}
