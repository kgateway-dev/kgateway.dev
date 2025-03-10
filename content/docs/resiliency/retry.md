---
title: Retries
weight: 10
description: Specify the number of times and duration you want kgateway to try a connection to an unresponsive backend service.
---

Specify the number of times and duration you want {{< reuse "docs/snippets/product-name.md" >}} to try a connection to an unresponsive backend service.

## About retries

A retry specifies the maximum number of times {{< reuse "docs/snippets/product-name.md" >}} attempts to connect to an backend service if the initial call fails. Retries can enhance service availability and application performance by making sure that calls don’t fail permanently because of transient problems such as a temporarily overloaded service or network.

To configure retries, you can use the following settings in the RouteOption resource: 
- `options.retries.retryOn` : The condition under which to retry forwarding the request to the backend service. This setting exposes the [`x-envoy-retry-on` Envoy header](https://www.envoyproxy.io/docs/envoy/latest/configuration/http/http_filters/router_filter#x-envoy-retry-on). 
- `options.retries.numRetries`: The number of allowed retries. The default value is 1.  
- `options.retries.perTryTimeout`: The timeout [duration](https://protobuf.dev/reference/protobuf/google.protobuf/#duration) for each retry attempt. This setting exposes the [x-envoy-expected-rq-timeout-ms](https://www.envoyproxy.io/docs/envoy/latest/configuration/http/http_filters/router_filter#x-envoy-expected-rq-timeout-ms) header.

## Before you begin

{{< reuse "docs/snippets/prereq.md" >}}

## Set up retries {#retries}
   
Use a RouteOption resource to specify retries for a specific route. 

1. Create a RouteOption custom resource to specify your retry rules. In the following example, the request is retried up to 3 times when a connection failure is detected. For each retry a timeout of 5 seconds is set. 
   ```yaml
   kubectl apply -n httpbin -f- <<EOF
   apiVersion: gateway.kgateway.dev/v1alpha1
   kind: RouteOption
   metadata:
     name: retry
     namespace: httpbin
   spec:
     options:
       retries:
         retryOn: 'connect-failure'
         numRetries: 3
         perTryTimeout: '5s'
   EOF
   ```

2. Create an HTTPRoute resource for the httpbin app that references the RouteOption resource that you created. 
   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.networking.k8s.io/v1
   kind: HTTPRoute
   metadata:
     name: httpbin-retry
     namespace: httpbin
   spec:
     parentRefs:
     - name: http
       namespace: {{< reuse "docs/snippets/ns-system.md" >}}
     hostnames:
       - retry.example
     rules:
       - filters:
           - type: ExtensionRef
             extensionRef:
               group: gateway.solo.io
               kind: RouteOption
               name: retry
         backendRefs:
           - name: httpbin
             port: 8000
   EOF
   ```

3. Send a request to the httpbin app on the `retry.example` domain. Verify that the request succeeds and that you see a `X-Envoy-Expected-Rq-Timeout-Ms` header. If the header is present, {{< reuse "docs/snippets/product-name.md" >}} expects requests to the httpbin app to succeed within the set timeout. 
   {{< tabs items="LoadBalancer IP address or hostname,Port-forward for local testing" >}}
   {{% tab  %}}
   ```sh
   curl -vik http://$INGRESS_GW_ADDRESS:8080/headers -H "host: retry.example:8080"
   ```
   {{% /tab %}}
   {{% tab %}}
   ```sh
   curl -vik localhost:8080/headers -H "host: retry.example"
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
        "5000"
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
   kubectl delete httproute httpbin-retry -n httpbin
   kubectl delete routeoption retry -n httpbin
   ```



