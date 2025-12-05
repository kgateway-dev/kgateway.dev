---
title: Query parameter
weight: 10
description: Specify a set of URL query parameters which requests must match in entirety.
---

Specify a set of URL query parameters which requests must match in entirety.

For more information, see the [{{< reuse "docs/snippets/k8s-gateway-api-name.md" >}} documentation](https://gateway-api.sigs.k8s.io/api-types/httproute/#matches).

## Before you begin

{{< reuse "docs/snippets/prereq.md" >}}

## Set up query parameter matching

1. Create an HTTPRoute resource for the `match.example` domain that matches incoming requests with a `user=me` query parameter. 
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
         - queryParams: 
             - type: Exact
               value: me
               name: user
         backendRefs:
           - name: httpbin
             port: 8000
   EOF
   ```

2. Send a request to the `/status/200` path of the httpbin app on the `match.example` domain without any query parameters. Verify that your request is not forwarded to the httpbin app because no matching query parameter is found. 
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
   < date: Sat, 04 Nov 2023 03:45:39 GMT
   date: Sat, 04 Nov 2023 03:45:39 GMT
   < server: envoy
   server: envoy
   < content-length: 0
   content-length: 0
   ```

3. Send a request to the `/status/200` path of the httpbin app on the `match.example` domain. This time, you provide the `user=me` query parameter. Verify that your request now succeeds and that you get back a 200 HTTP response code. 
   {{< tabs items="Cloud Provider LoadBalancer,Port-forward for local testing" tabTotal="2" >}}
   {{% tab tabName="Cloud Provider LoadBalancer" %}}
   ```sh
   curl -vi "http://$INGRESS_GW_ADDRESS:8080/status/200?user=me" -H "host: match.example:8080"
   ```
   {{% /tab %}}
   {{% tab tabName="Port-forward for local testing" %}}
   ```sh
   curl -vi "localhost:8080/status/200?user=me" -H "host: match.example"
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
   < date: Sat, 04 Nov 2023 03:49:17 GMT
   date: Sat, 04 Nov 2023 03:49:17 GMT
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

