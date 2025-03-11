---
title: Direct responses
weight: 20
prev: /docs/traffic-management/destination-types
next: /docs/traffic-management/match
---

Directly respond to incoming requests without forwarding them to services by returning a pre-defined body and HTTP status to the client.

## About direct responses

When you configure a direct response, the gateway proxy intercepts requests to specific routes and directly sends back a predefined response. Common use cases include: 

* **Static responses**: You might have endpoints for which sending back static responses is sufficient.
* **Health checks**: You might use direct responses when configuring health checks for the gateway. 
* **Redirects**: You can use direct responses to redirect users to new locations, such as when an endpoint is now available at a different address. 
* **Test responses**: You can use direct responses to simulate responses from backend services without forwarding the request to the actual service. 

### Limitations

Consider the following limitations before creating DirectResponse resources in your cluster: 
* You cannot configure multiple DirectResponse resources on the same route. If multiple DirectResponse resources are defined on the same route, the route is replaced with a 500 HTTP response code and an error message is shown on the HTTPRoute. 
* You cannot combine a DirectResponse with other route actions on the same route. For example, you cannot configure a DirectResponse and a `RequestRedirect` filter or `backendRefs` rule at the same time. If multiple route actions are defined, the route is replaced with a 500 HTTP response code and an error message is shown on the HTTPRoute. 
* DirectResponse resources can be referenced by using an `ExtensionRef` filter only. If specified in a `backendRef` filter, the DirectResponse configuration is ignored. 
* No status information is currently populated to the DirectResponse resource.
* The DirectResponse CRD currently does not show a description when you run `kubectl explain directresponse`. 

### Schema validation
The following rules are applied during schema validation: 
* The `spec.body` field can have a size of up to 4KB. 
* The `spec.status` field can define a valid HTTP status code in the 200-599 range. 

## Before you begin

{{< reuse "docs/snippets/prereq.md" >}}

## Set up direct responses 

1. Create a DirectResponse resource that sends back a 510 HTTP response code and a custom message to incoming requests. 
   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.kgateway.dev/v1alpha1
   kind: DirectResponse
   metadata:
     name: direct-response
     namespace: httpbin
   spec:
     status: 510
     body: "User-agent: *\nDisallow: /direct-response\n"
   EOF
   ```
   
2. Create an HTTPRoute resource. All traffic on the `/` path is routed to the httpbin app. However, traffic along the `/direct-response` path is not forwarded. Instead, the direct response that you configured earlier is returned to the user.
   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.networking.k8s.io/v1
   kind: HTTPRoute
   metadata:
     name: httpbin-direct-resonse
     namespace: httpbin
   spec:
     hostnames:
     - direct-response.com
     parentRefs:
     - name: http
       namespace: {{< reuse "docs/snippets/ns-system.md" >}}
     rules:
     - matches:
       - path:
           type: PathPrefix
           value: /
       backendRefs:
       - name: httpbin
         port: 8000
     - matches:
       - path:
           type: Exact
           value: /direct-response
       filters:
       - type: ExtensionRef
         extensionRef:
          name: direct-response
          group: gateway.gateway.kgateway.dev
          kind: DirectResponse
   EOF
   ```
   
3. Send a request to the httpbin app along the `/status/200` path on the `direct-response.com` domain. Verify that your request succeeds and that you get back a 200 HTTP response code.  
   {{< tabs items="LoadBalancer IP address or hostname,Port-forward for local testing" >}}
   {{% tab %}}
   ```sh
   curl -vik http://$INGRESS_GW_ADDRESS:8080/status/200 \
   -H "host: direct-response.com:8080"
   ```
   {{% /tab %}}
   {{% tab %}}
   ```sh
   curl -vik localhost:8080/status/200 \
   -H "host: direct-response.com:8080"
   ```
   {{% /tab %}}
   {{< /tabs >}}
   
   Example output: 
   ```
   * Mark bundle as not supporting multiuse
   < HTTP/1.1 200 OK
   HTTP/1.1 200 OK
   < access-control-allow-credentials: true
   access-control-allow-credentials: true
   < access-control-allow-origin: *
   access-control-allow-origin: *
   < date: Mon, 23 Sep 2024 17:47:37 GMT
   date: Mon, 23 Sep 2024 17:47:37 GMT
   < content-length: 0
   content-length: 0
   < x-envoy-upstream-service-time: 3
   x-envoy-upstream-service-time: 3
   < server: envoy
   server: envoy
   ```
   
4. Send another request along the `/direct-response` path. Verify that you get back the direct response message that you defined in the DirectResponse resource. 
   {{< tabs items="LoadBalancer IP address or hostname,Port-forward for local testing" >}}
   {{% tab %}}
   ```sh
   curl -vik http://$INGRESS_GW_ADDRESS:8080/direct-response \
   -H "host: direct-response.com:8080"
   ```
   {{% /tab %}}
   {{% tab %}}
   ```sh
   curl -vik localhost:8080/direct-response \
   -H "host: direct-response.com:8080"
   ```
   {{% /tab %}}
   {{< /tabs >}}
   
   Example output: 
   ```
   * Mark bundle as not supporting multiuse
   < HTTP/1.1 510 Not Extended
   HTTP/1.1 510 Not Extended
   < content-length: 41
   content-length: 41
   < content-type: text/plain
   content-type: text/plain
   < date: Mon, 23 Sep 2024 17:48:37 GMT
   date: Mon, 23 Sep 2024 17:48:37 GMT
   < server: envoy
   server: envoy
   
   < 
   User-agent: *
   Disallow: /direct-response
   ```
   
## Cleanup

{{< reuse "docs/snippets/cleanup.md" >}}

```sh
kubectl delete directresponse direct-response -n httpbin
kubectl delete httproute httpbin-direct-resonse -n httpbin
```
