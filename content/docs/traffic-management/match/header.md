---
title: Header 
weight: 422
description: Specify a set of headers which incoming requests must match in entirety.
---

Specify a set of headers which incoming requests must match in entirety.

For more information, see the [{{< reuse "docs/snippets/k8s-gateway-api-name.md" >}} documentation](https://gateway-api.sigs.k8s.io/api-types/httproute/#matches).

## Before you begin

{{< reuse "docs/snippets/prereq.md" >}}

## Set up header matching

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
         namespace: {{< reuse "docs/snippets/ns-system.md" >}}
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
   {{< tabs items="Cloud Provider LoadBalancer,Port-forward for local testing" >}}
   {{% tab %}}
   ```sh
   curl -vik http://$INGRESS_GW_ADDRESS:8080/status/200 -H "host: match.example:8080"
   ```
   {{% /tab %}}
   {{% tab %}}
   ```sh
   curl -vik localhost:8080/status/200 -H "host: match.example"
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
   {{< tabs items="Cloud Provider LoadBalancer,Port-forward for local testing" >}}
   {{% tab %}}
   ```sh
   curl -vik http://$INGRESS_GW_ADDRESS:8080/status/200 -H "host: match.example:8080" -H "version: v2"
   ```
   {{% /tab %}}
   {{% tab %}}
   ```sh
   curl -vik localhost:8080/status/200 -H "host: match.example" -H "version: v2"
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

## Cleanup

{{< reuse "docs/snippets/cleanup.md" >}}

```sh
kubectl delete httproute httpbin-match -n httpbin
```

