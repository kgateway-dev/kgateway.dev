---
title: CORS
weight: 10
description: Enforce client-site access controls with cross-origin resource sharing (CORS).
---

Enforce client-site access controls with cross-origin resource sharing (CORS).

## About CORS

Cross-Origin Resource Sharing (CORS) is a security feature that is implemented by web browsers and that controls how web pages in one domain can request and interact with resources that are hosted on a different domain. By default, web browsers only allow requests to resources that are hosted on the same domain as the web page that served the original request. Access to web pages or resources that are hosted on a different domain is restricted to prevent potential security vulnerabilities, such as cross-site request forgery (CRSF).

When CORS is enabled in a web browser and a request for a different domain comes in, the web browser checks whether this request is allowed or not. To do that, it typically sends a preflight request (HTTP `OPTIONS` method) to the server or service that serves the requested resource. The service returns the methods that are permitted to send the actual cross-origin request, such as GET, POST, etc. If the request to the different domain is allowed, the response includes CORS-specific headers that instruct the web browser how to make the cross-origin request. For example, the CORS headers typically include the origin that is allowed to access the resource, and the credentials or headers that must be included in the cross-origin request.

Note that the preflight request is optional. Web browsers can also be configured to send the cross-origin directly. However, access to the request resource is granted only if CORS headers were returned in the response. If no headers are returned during the preflight request, the web browser denies access to the resource in the other domain.

CORS policies are typically implemented to limit access to server resources for JavaScripts that are embedded in a web page, such as:

* A JavaScript on a web page at `example.com` tries to access a different domain, such as `api.com`.
* A JavaScript on a web page at `example.com` tries to access a different subdomain, such as `api.example.com`.
* A JavaScript on a web page at `example.com` tries to access a different port, such as `example.com:3001`.
* A JavaScript on a web page at `https://example.com` tries to access the resources by using a different protocol, such as `http://example.com`.

For more information, see the [CORS API](/docs/reference/api/cors/).

### Configuration options

You can configure the CORS policy at two levels:

* VirtualHostOption: Configure a CORS policy in the VirtualHostOption that is applied to a gateway proxy. The policy is automatically attached to all the listeners that are defined for one or multiple hosts on the gateway. 
* RouteOption: Configure a CORS policy in the RouteOption. Then, you can apply the policy to one or multiple routes by using the `targetRefs` field on the RouteOption or the `ExtensionRef` filter on the HTTPRoute. For more information, see [Policy attachment](/docs/about/policies/routeoption/#policy-attachment-routeoption}). 

By default, the configuration of the RouteOption takes precedence over the VirtualHostOption. However, you can change this behavior for the `exposeHeaders` CORS option by using the `corsPolicyMergeSettings` field in the VirtualHostOption. Currently, only `exposeHeaders` is configurable. You cannot merge other CORS options such as `allowHeaders` or `allowOrigin`. 

For example, you might want to expose the CORS `origin` header for traffic that reaches any of the gateway listeners with the VirtualHostOption. Additionally, each team or product might have their own headers on a per route basis that you want to expose also, such as `product-a`. By setting the `corsPolicyMergeSettings` to `UNION`, the exposed headers are merged together. This way, both the VirtualHostOption and RouteOption `exposeHeaders` CORS policies are applied. When the routes are called, the exposed headers from the VirtualHostOption and RouteOption are both returned, such as `origin` and `product-a`.

For more information about the supported merge strategies, see the [API docs](/docs/reference/api/cors/#corspolicymergesettings).

{{% callout type="info" %}} 
Some apps, such as `httpbin`, have built-in CORS policies that allow all origins. These policies take precedence over CORS policies that you might configure in {{< reuse "docs/snippets/product-name.md" >}}. 
{{% /callout %}}

## Before you begin

{{< reuse "docs/snippets/prereq.md" >}}

## Set up CORS policies

{{% callout type="info" %}}
This example uses the Petstore app to demonstrate CORS policies. You cannot use the httpbin app, because httpbin has built-in CORS policies that allow all origins. These policies take precedence over CORS policies that you configure in {{< reuse "docs/snippets/product-name.md" >}}.
{{% /callout %}}

1. Deploy the Petstore app. 
   ```sh
   kubectl apply -f https://raw.githubusercontent.com/solo-io/gloo/v1.16.x/example/petstore/petstore.yaml
   ```
   
   Example output: 
   ```console
   deployment.apps/petstore created
   service/petstore created
   ```

2. Verify that the Petstore app is up and running. 
   ```sh
   kubectl get pods   
   ```
   
   Example output: 
   ```console                                                                              
   NAME                        READY   STATUS    RESTARTS   AGE
   petstore-66cddd5bb4-x7vdd   1/1     Running   0          26s
   ```

3. Create the CORS policy at either the virtual host level or the route level. Policies at the virtual host level apply to all routes that are attached to the gateway that the virtual host targets. If you have a CORS policy at both virtual host and route levels, the route policy takes precedence by default.

   {{< tabs items="Virtual host, Route" >}}
   {{% tab %}}
   Create a VirtualHostOption resource to define your CORS rules. The following example allows requests from the `example.com/` and `*.example.com` origins. The example also sets the `corsPolicyMergeSettings` to configure how conflicting CORS policies at the virtual host and route levels are handled. In the example, you configure a `UNION` merge strategy for the `exposeHeaders` field. Now, the CORS policy applies to requests so that all the `exposeHeaders` values from both the virtual host and route are included. Currently, only `exposeHeaders` is configurable. You cannot merge other CORS options such as `allowHeaders` or `allowOrigin`.
   ```yaml
   kubectl apply -n {{< reuse "docs/snippets/ns-system.md" >}} -f- <<EOF
   apiVersion: gateway.kgateway.dev/v1alpha1
   kind: VirtualHostOption
   metadata:
     name: cors
     namespace: {{< reuse "docs/snippets/ns-system.md" >}}
   spec:
     options:
       corsPolicyMergeSettings:
         exposeHeaders: UNION
       cors:
         allowCredentials: true
         allowHeaders:
         - origin
         allowMethods:
         - GET
         - POST
         - OPTIONS
         allowOrigin:
         - https://example.com/
         allowOriginRegex:
         - https://\[a-zA-Z0-9\]\*.example
         exposeHeaders:
         - origin
         - vh-header
         maxAge: 1d
     targetRefs:
     - group: gateway.networking.k8s.io
       kind: Gateway
       name: http
       namespace: {{< reuse "docs/snippets/ns-system.md" >}}
   EOF
   ```
   {{% /tab %}}
   {{% tab  %}}
   1. Create a RouteOption resource to define your CORS rules. The following example allows requests from the `example.com/` and `*.example.com` origins. 
      ```yaml
      kubectl apply -f- <<EOF
      apiVersion: gateway.kgateway.dev/v1alpha1
      kind: RouteOption
      metadata:
        name: cors
        namespace: default
      spec:
        options:
          cors:
            allowCredentials: true
            allowHeaders:
            - origin
            allowMethods:
            - GET
            - POST
            - OPTIONS
            allowOrigin:
            - https://example.com/
            allowOriginRegex:
            - https://\[a-zA-Z0-9\]\*.example
            exposeHeaders:
            - origin
            - route-header
            maxAge: 1d
      EOF
      ```

2. Create an HTTPRoute resource for the Petstore app that applies the RouteOption resources that you created. 
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
       namespace: {{< reuse "docs/snippets/ns-system.md" >}}
     hostnames:
       - cors.example
     rules:
       - filters:
           - type: ExtensionRef
             extensionRef:
               group: gateway.solo.io
               kind: RouteOption
               name: cors
         backendRefs:
           - name: petstore
             port: 8080
   EOF
   ```
   {{% /tab %}}
   {{< /tabs >}}   

1. Send a request to the Petstore app on the `cors.example` domain and use `https://example.com/` as the origin. Verify that your request succeeds and that you get back CORS headers, such as `access-control-allow-origin`, `access-control-allow-credentials`, and `access-control-expose-headers`. 
   {{< tabs items="LoadBalancer IP address or hostname,Port-forward for local testing" >}}
   {{% tab  %}}
   ```sh
   curl -v -X GET http://$INGRESS_GW_ADDRESS:8080/api/pets -H "host: cors.example:8080" \
    -H "Origin: https://example.com/" -H "Access-Control-Request-Method: GET"
   ```
   {{% /tab %}}
   {{% tab  %}}
   ```sh
   curl -v -X GET localhost:8080/api/pets -H "host: cors.example:8080" \
    -H "Origin: https://example.com/" -H "Access-Control-Request-Method: GET"
   ```
   {{% /tab %}}
   {{< /tabs >}}
   
   Example output: Notice that the `access-control-expose-headers` value changes depending on the resources that you created.
   * If you created only a VirtualHostOption, you see the `origin` and `vh-header` headers.
   * If you created only a RouteOption or both a RouteOption and VirtualHostOption, you see the `origin` and `route-header` headers, because the RouteOption takes precedence. 
   * If you created both options and also configured the `corsPolicyMergeSettings` on the VirtualHostOptions with a `UNION` merge strategy, then you see all the `origin`, `vh-header`, and `route-header` headers.
   ```console {hl_lines=[7,8,9]}
   * Mark bundle as not supporting multiuse
   < HTTP/1.1 200 OK
   < content-type: text/xml
   < date: Mon, 03 Jun 2024 17:05:31 GMT
   < content-length: 86
   < x-envoy-upstream-service-time: 7
   < access-control-allow-origin: https://example.com/
   < access-control-allow-credentials: true
   < access-control-expose-headers: origin, vh-header, route-header
   < server: envoy
   < 
   [{"id":1,"name":"Dog","status":"available"},{"id":2,"name":"Cat","status":"pending"}]
   ```
   
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

```sh
kubectl delete -f https://raw.githubusercontent.com/solo-io/gloo/v1.16.x/example/petstore/petstore.yaml
kubectl delete virtualhostoption cors -n {{< reuse "docs/snippets/ns-system.md" >}}
kubectl delete routeoption cors -n default
kubectl delete httproute petstore-cors -n default
```
   