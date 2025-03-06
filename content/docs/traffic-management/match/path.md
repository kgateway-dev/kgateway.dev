---
title: Path 
weight: 421
description: Match the targeted path of an incoming request against specific path criteria. 
---

Match the targeted path of an incoming request against specific path criteria. 

For more information, see the [{{< reuse "docs/snippets/k8s-gateway-api-name.md" >}} documentation](https://gateway-api.sigs.k8s.io/api-types/httproute/#matches).

## Before you begin

{{< reuse "docs/snippets/prereq.md" >}}

## Set up URI path matching

1. Create an HTTPRoute resource for the `match.example` domain that matches incoming requests on the `/status/200` path. 
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
         - path:
             type: Exact
             value: /status/200
         backendRefs:
           - name: httpbin
             port: 8000
   EOF 
   ```
   
2. Send a request to the `/status/200` path of the httpbin app on the `match.example` domain. Verify that you get back a 200 HTTP response code.  
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

3. Send another request to the httpbin app. This time, use the `/headers` path. Because this path is not specified in the HTTPRoute, the request fails and a 404 HTTP response code is returned. 
   {{< tabs items="Cloud Provider LoadBalancer,Port-forward for local testing" >}}
   {{% tab %}}
   ```sh
   curl -vik http://$INGRESS_GW_ADDRESS:8080/headers -H "host: match.example:8080"
   ```
   {{% /tab %}}
   {{% tab %}}
   ```sh
   curl -vik localhost:8080/headers -H "host: match.example"
   ```
   {{% /tab %}}
   {{< /tabs >}}
   
   Example output: 
   ```
   * Mark bundle as not supporting multiuse
   < HTTP/1.1 404 Not Found
   HTTP/1.1 404 Not Found
   < date: Tue, 23 Apr 2024 18:52:01 GMT
   date: Tue, 23 Apr 2024 18:52:01 GMT
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

