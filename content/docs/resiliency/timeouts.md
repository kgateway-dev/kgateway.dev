---
title: Timeouts
weight: 10
description: Set a maximum time for the gateway to handle a request.
---

Set a maximum time for the gateway to handle a request.

The Kubernetes Gateway API provides a way to configure timeouts on your HTTPRoutes. You might commonly use timeouts alongside [Retries](/docs/resiliency/retry/) to ensure that your apps are available even if they are temporarily unavailable.

{{< callout >}}
{{< reuse "docs/snippets/proxy-kgateway.md" >}}
{{< /callout >}}

## About

A timeout is the amount of time ([duration](https://protobuf.dev/reference/protobuf/google.protobuf/#duration)) that the gateway waits for replies from a backend service before the service is considered unavailable. This setting can be useful to avoid your apps from hanging or fail if no response is returned in a specific timeframe. With timeouts, calls either succeed or fail within a predicatble timeframe.

The time an app needs to process a request can vary a lot which is why applying the same timeout across services can cause a variety of issues. For example, a timeout that is too long can result in excessive latency from waiting for replies from failing services. On the other hand, a timeout that is too short can result in calls failing unnecessarily while waiting for an operation that needs responses from multiple services.

## Before you begin

{{< reuse "docs/snippets/prereq.md" >}}

## Set up timeouts {#timeouts}
   
Specify timeouts for a specific route. 

1. Create an HTTPRoute resource to specify your timeout rules. In the following example, the request must be completed within 20 seconds.  
   ```yaml
   kubectl apply -n httpbin -f- <<EOF
   apiVersion: gateway.networking.k8s.io/v1
   kind: HTTPRoute
   metadata:
     name: httpbin-timeout
   spec:
     hostnames:
     - timeout.example
     parentRefs:
     - group: gateway.networking.k8s.io
       kind: Gateway
       name: http
       namespace: {{< reuse "docs/snippets/namespace.md" >}}
     rules:
     - matches: 
       - path:
           type: PathPrefix
           value: /
       backendRefs:
       - group: ""
         kind: Service
         name: httpbin
         port: 8000
       timeouts:
         request: "20s"
   EOF
   ```

2. Send a request to the httpbin app. Verify that the request succeeds and that you see a `X-Envoy-Expected-Rq-Timeout-Ms` header. If the header is present, {{< reuse "/docs/snippets/kgateway.md" >}} expects requests to the httpbin app to succeed within the set timeout. 
   {{< tabs items="Cloud Provider LoadBalancer,Port-forward for local testing" tabTotal="2" >}}
   {{% tab tabName="Cloud Provider LoadBalancer" %}}
   ```sh
   curl -vi http://$INGRESS_GW_ADDRESS:8080/headers -H "host: timeout.example:8080"
   ```
   {{% /tab %}}
   {{% tab tabName="Port-forward for local testing" %}}
   ```sh
   curl -vi localhost:8080/headers -H "host: timeout.example"
   ```
   {{% /tab %}}
   {{< /tabs >}}

   Example output for a successful response: 
   ```console {hl_lines=[12,13]}
   {
    "headers": {
      "Accept": [
        "*/*"
      ],
      "Host": [
        "www.example.com:8080"
      ],
      "User-Agent": [
        "curl/7.77.0"
      ],
      "X-Envoy-Expected-Rq-Timeout-Ms": [
        "20000"
      ],
      "X-Forwarded-Proto": [
        "http"
      ],
      "X-Request-Id": [
        "0ae53bc3-2644-44f2-8603-158d2ccf9f78"
      ]
    }
   }
   ```

## Cleanup

{{< reuse "docs/snippets/cleanup.md" >}}

Delete the HTTPRoute resource.
   
```sh
kubectl delete httproute httpbin-timeout -n httpbin
```
