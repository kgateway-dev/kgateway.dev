---
title: Header 
weight: 10
description: Specify a set of headers which incoming requests must match in entirety.
---

Specify a set of headers which incoming requests must match in entirety.

For more information, see the [{{< reuse "docs/snippets/k8s-gateway-api-name.md" >}} documentation](https://gateway-api.sigs.k8s.io/api-types/httproute/#matches).

## Before you begin

{{< reuse "docs/snippets/prereq.md" >}}

## Set up exact header matching

1. Create an HTTPRoute resource. 
   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.networking.k8s.io/v1
   kind: HTTPRoute
   metadata:
     name: httpbin-match
     namespace: httpbin
   spec:
     parentRefs:
       - name: http
         namespace: {{< reuse "docs/snippets/namespace.md" >}}
     hostnames:
       - match.example
     rules:
       - matches:
         - headers:
           - name: version
             value: v2
             type: Exact
         backendRefs:
           - name: httpbin
             port: 8000
   EOF
   ```

2. Send a request to the httpbin app on the `match.example` domain without any headers. Verify that you get back a 404 HTTP response code as no matching request could be found. 
   {{< tabs items="Cloud Provider LoadBalancer,Port-forward for local testing" tabTotal="2" >}}
   {{% tab tabName="Cloud Provider LoadBalancer" %}}
   ```sh
   curl -vi http://$INGRESS_GW_ADDRESS:8080/status/200 -H "host: match.example:8080"
   ```
   {{% /tab %}}
   {{% tab tabName="Port-forward for local testing" %}}
   ```sh
   curl -vi localhost:8080/status/200 -H "host: match.example"
   ```
   {{% /tab %}}
   {{< /tabs >}}

   Example output: 
   ```
   * Mark bundle as not supporting multiuse
   < HTTP/1.1 404 Not Found
   HTTP/1.1 404 Not Found
   < date: Sat, 04 Nov 2023 03:16:43 GMT
   date: Sat, 04 Nov 2023 03:16:43 GMT
   < server: envoy
   server: envoy
   < content-length: 0
   content-length: 0
   ```

3. Send another request to the httpbin app on the `match.example` domain. This time, add the `version: v2` header that you configured in the HTTPRoute. Verify that your request now succeeds and you get back a 200 HTTP response code. 
   {{< tabs items="Cloud Provider LoadBalancer,Port-forward for local testing" tabTotal="2" >}}
   {{% tab tabName="Cloud Provider LoadBalancer" %}}
   ```sh
   curl -vi http://$INGRESS_GW_ADDRESS:8080/status/200 -H "host: match.example:8080" -H "version: v2"
   ```
   {{% /tab %}}
   {{% tab tabName="Port-forward for local testing" %}}
   ```sh
   curl -vi localhost:8080/status/200 -H "host: match.example" -H "version: v2"
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
   < date: Sat, 04 Nov 2023 03:19:26 GMT
   date: Sat, 04 Nov 2023 03:19:26 GMT
   < content-length: 0
   content-length: 0
   < x-envoy-upstream-service-time: 1
   x-envoy-upstream-service-time: 1
   < server: envoy
   server: envoy
   ```
   
## Set up regex header matching

1. Create an HTTPRoute resource to match multiple headers based on a regular expression. Only if all headers are present in the request, the request is accepted and processed by the gateway proxy. The following rules apply: 
   * ` (dogs|cats)`: The value of the `pet` request header must either be `dogs` or `cats`.
   * `\\d[.]\\d.*`: The value of the `version` header must meet the following conditions: 
     * `\\d` matches a single digit.
     * `[.]` matches a literal period.
     * `\\d.*` matches a single digit followed by zero or any character.
     * Allowed pattern: `3.0-game`, not allowed: `30`
   * `Bearer\s.*`: The value of the `Authorization` request header must be `Bearer` followed by a space (`\s`), followed by zero or any characters (`.*`).
     * Allowed pattern: `Bearer 123`, not allowed: `Bearer` 
   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.networking.k8s.io/v1
   kind: HTTPRoute
   metadata:
     name: httpbin-match
     namespace: httpbin
   spec:
     parentRefs:
       - name: http
         namespace: {{< reuse "docs/snippets/namespace.md" >}}
     hostnames:
       - match.example
     rules:
       - matches:
         - headers:
           - name: pet
             value: (dogs|cats)
             type: RegularExpression
           - name: version
             value: \\d[.]\\d.*
             type: RegularExpression
           - name: Authorization
             value: Bearer\s.*
             type: RegularExpression
         backendRefs:
           - name: httpbin
             port: 8000
   EOF
   ```

2. Send a request to the httpbin app on the `match.example` domain and add valid values for each of your headers. Verify that the request succeeds and you get back a 200 HTTP response code. 
   {{< tabs items="Cloud Provider LoadBalancer,Port-forward for local testing" tabTotal="2" >}}
   {{% tab tabName="Cloud Provider LoadBalancer" %}}
   ```sh
   curl -vi http://$INGRESS_GW_ADDRESS:8080/status/200 -H "host: match.example:8080" -H "host: match.example" \
   -H "Authorization: Bearer 123" \
   -H "pet: dogs" \
   -H "version: 3.0" 
   ```
   {{% /tab %}}
   {{% tab tabName="Port-forward for local testing" %}}
   ```sh
   curl -vi localhost:8080/status/200 -H "host: match.example" -H "host: match.example" \
   -H "Authorization: Bearer 123" \
   -H "pet: dogs" \
   -H "version: 3.0"
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
   < content-length: 0
   content-length: 0
   < x-envoy-upstream-service-time: 1
   x-envoy-upstream-service-time: 1
   < server: envoy
   server: envoy
   ```

3. Send another request to the httpbin app on the `match.example` domain. This time, you change the value of the `version` header to an invalid value that does not meet the regular expression that you defined. Verify that the request is denied with a 404 HTTP response code. 
   {{< tabs items="Cloud Provider LoadBalancer,Port-forward for local testing" tabTotal="2" >}}
   {{% tab tabName="Cloud Provider LoadBalancer" %}}
   ```sh
   curl -vi http://$INGRESS_GW_ADDRESS:8080/status/200 -H "host: match.example:8080" -H "host: match.example" \
   -H "Authorization: Bearer 123" \
   -H "pet: dogs" \
   -H "version: 30"
   ```
   {{% /tab %}}
   {{% tab tabName="Port-forward for local testing" %}}
   ```sh
   curl -vi localhost:8080/status/200 -H "host: match.example" -H "host: match.example" \
   -H "Authorization: Bearer 123" \
   -H "pet: dogs" \
   -H "version: 30"
   ```
   {{% /tab %}}
   {{< /tabs >}}

   Example output: 
   ```
   * Request completely sent off
   < HTTP/1.1 404 Not Found
   HTTP/1.1 404 Not Found
   < server: envoy
   server: envoy
   < content-length: 0
   content-length: 0

   ```
## Cleanup

{{< reuse "docs/snippets/cleanup.md" >}}

```sh
kubectl delete httproute httpbin-match -n httpbin
```

