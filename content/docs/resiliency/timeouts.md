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
Timeouts can be configured for a route by using a RouteOption resource. Configuring gateway-level timeouts with a VirtualHostOption resource is not supported.
{{% /callout %}}

## Before you begin

{{< reuse "docs/snippets/prereq.md" >}}

## Set up timeouts {#timeouts}
   
Use a RouteOption resource to specify timeouts for a specific route. 

1. Create a RouteOption custom resource to specify your timeout rules. In the following example, the request must be completed within 20 seconds.  
   ```yaml
   kubectl apply -n httpbin -f- <<EOF
   apiVersion: gateway.kgateway.dev/v1alpha1
   kind: RouteOption
   metadata:
     name: timeout
     namespace: httpbin
   spec:
     options:
       timeout: '20s'
   EOF
   ```

2. Create an HTTPRoute resource for the httpbin app that references the RouteOption resource that you created. 
   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.networking.k8s.io/v1
   kind: HTTPRoute
   metadata:
     name: httpbin-timeout
     namespace: httpbin
   spec:
     parentRefs:
     - name: http
       namespace: {{< reuse "docs/snippets/ns-system.md" >}}
     hostnames:
       - timeout.example
     rules:
       - filters:
           - type: ExtensionRef
             extensionRef:
               group: gateway.solo.io
               kind: RouteOption
               name: timeout
         backendRefs:
           - name: httpbin
             port: 8000
   EOF
   ```

3. Send a request to the httpbin app on the `timout.example` domain. Verify that the request succeeds and that you see a `X-Envoy-Expected-Rq-Timeout-Ms` header. If the header is present, {{< reuse "docs/snippets/product-name.md" >}} expects requests to the httpbin app to succeed within the set timeout. 
   {{< tabs items="LoadBalancer IP address or hostname,Port-forward for local testing" >}}
   {{% tab  %}}
   ```sh
   curl -vik http://$INGRESS_GW_ADDRESS:8080/headers -H "host: timeout.example:8080"
   ```
   {{% /tab %}}
   {{% tab %}}
   ```sh
   curl -vik localhost:8080/headers -H "host: timeout.example"
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
        "timeout.example:8080"
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

4. Optional: Remove the resources that you created. 
   ```sh
   kubectl delete httproute httpbin-timeout -n httpbin
   kubectl delete routeoption timeout -n httpbin
   ```

