---
title: Timeouts
weight: 10
description: Set a maximum time for the gateway to handle a request, including error retries.
---

Set a maximum time for the gateway to handle a request, including error retries.

## About
A timeout is the amount of time ([duration](https://protobuf.dev/reference/protobuf/google.protobuf/#duration)) that {{< reuse "docs/snippets/product-name.md" >}} waits for replies from a backend service before the service is considered unavailable. This setting can be useful to avoid your apps from hanging or fail if no response is returned in a specific timeframe. With timeouts, calls either succeed or fail within a predicatble timeframe.

The time an app needs to process a request can vary a lot which is why applying the same timeout across services can cause a variety of issues. For example, a timeout that is too long can result in excessive latency from waiting for replies from failing services. On the other hand, a timeout that is too short can result in calls failing unnecessarily while waiting for an operation that needs responses from multiple services.

{{% callout type="info" %}}
Timeouts can be configured for a route by using a RoutePolicy resource. 
{{% /callout %}}

## Before you begin

{{< reuse "docs/snippets/prereq.md" >}}

## Set up timeouts {#timeouts}
   
Use a RoutePolicy resource to specify timeouts for a specific route. 

1. Create a RoutePolicy resource to specify your timeout rules. In the following example, the request must be completed within 20 seconds.  
   ```yaml
   kubectl apply -n httpbin -f- <<EOF
   apiVersion: gateway.kgateway.dev/v1alpha1
   kind: RoutePolicy
   metadata:
     name: timeout
     namespace: httpbin
   spec:
     timeout: 20
     targetRef: 
       group: gateway.networking.k8s.io
       kind: HTTPRoute
       name: httpbin
   EOF
   ```

2. Send a request to the httpbin app. Verify that the request succeeds and that you see a `X-Envoy-Expected-Rq-Timeout-Ms` header. If the header is present, {{< reuse "docs/snippets/product-name.md" >}} expects requests to the httpbin app to succeed within the set timeout. 
   {{< tabs items="LoadBalancer IP address or hostname,Port-forward for local testing" >}}
   {{% tab  %}}
   ```sh
   curl -vik http://$INGRESS_GW_ADDRESS:8080/headers -H "host: www.example.com:8080"
   ```
   {{% /tab %}}
   {{% tab %}}
   ```sh
   curl -vik localhost:8080/headers -H "host: www.example.com"
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

3. Optional: Remove the RoutePolicy that you created. 
   ```sh
   kubectl delete routepolicy timeout -n httpbin
   ```

