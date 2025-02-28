---
title: HTTP
weight: 20
description: Limit the number of requests that are allowed to enter the cluster before global rate limiting and external auth policies are applied.  
---

To learn more about what local rate limiting is and the differences between local and global rate limiting, see [About local rate limiting](/docs/security/ratelimit/local/).

## Before you begin

{{< reuse "docs/snippets/prereq.md" >}}

## Apply local rate limit settings to Layer 4 traffic {#layer4}

1. Create an HTTPListenerPolicy resource with your local rate limit settings.  
   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.kgateway.dev/v1alpha1
   kind: HTTPListenerPolicy
   metadata:
     name: local-ratelimit
     namespace: {{< reuse "docs/snippets/ns-system.md" >}}
   spec:
     targetRefs: 
     - group: gateway.networking.k8s.io
       kind: Gateway
       name: http
     options: 
       networkLocalRatelimit: 
         maxTokens: 1
         tokensPerFill: 1
         fillInterval: 100s  
   EOF
   ```

2. Send a request to the httpbin app. Verify that your request succeeds and a 200 HTTP response code is returned. 
   {{< tabs items="LoadBalancer IP address or hostname,Port-forward for local testing" >}}
   {{% tab  %}}
   ```sh
   curl -vik http://$INGRESS_GW_ADDRESS:8080/status/200 -H "host: www.example.com:8080"
   ```
   {{% /tab %}}
   {{% tab %}}
   ```sh
   curl -vik localhost:8080/status/200 -H "host: www.example.com"
   ```
   {{% /tab %}}
   {{< /tabs >}}
   
   Example output: 
   ```
   ...
   * Mark bundle as not supporting multiuse
   < HTTP/1.1 200 OK
   HTTP/1.1 200 OK
   < content-type: application/xml
   content-type: application/xml
   ...
   ```

3. Send another request to the httpbin app. Note that this time the request is denied immediately. Because the gateway is configured with only 1 token that is refilled every 100 seconds, the token was assigned to the connection of the first request. No tokens were available to be assigned to the second request. Because the request is rejected on Layer 4, no HTTP response code or message is returned. 
   {{< tabs items="LoadBalancer IP address or hostname,Port-forward for local testing" >}}
   {{% tab  %}}
   ```sh
   curl -vik http://$INGRESS_GW_ADDRESS:8080/status/200 -H "host: www.example.com:8080"
   ```
   {{% /tab %}}
   {{% tab  %}}
   ```sh
   curl -vik localhost:8080/status/200 -H "host: www.example.com"
   ```
   {{% /tab %}}
   {{< /tabs >}}

   Example output: 
   ```
   * Recv failure: Connection reset by peer
   * Closing connection 0
   curl: (56) Recv failure: Connection reset by peer
   ```

## Apply local rate limit settings to Layer 7 traffic {#layer7}

1. Change the local rate limiting settings in the HTTPListenerPolicy resource to apply to Layer 7 traffic instead of Layer 4 traffic by using the `httpLocalRatelimit` option. The following example configures the gateway with a token bucket with a maximum of 1 token that is refilled every 100 seconds. To verify that your rate limiting settings are working as expected and to simplify troubleshooting, set `enableXRatelimitHeaders: true`. This option adds rate limiting headers to your response that indicate the local rate limiting settings that are applied, the number of tokens that are left in the bucket, and the number of seconds until the token bucket is refilled. For more information, see the [Envoy documentation](https://www.envoyproxy.io/docs/envoy/latest/api-v3/extensions/common/ratelimit/v3/ratelimit.proto#envoy-v3-api-enum-extensions-common-ratelimit-v3-xratelimitheadersrfcversion).
   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.kgateway.dev/v1alpha1
   kind: HTTPListenerPolicy
   metadata:
     name: local-ratelimit
     namespace: {{< reuse "docs/snippets/ns-system.md" >}}
   spec: 
     targetRefs: 
     - group: gateway.networking.k8s.io
       kind: Gateway
       name: http
     options: 
       httpLocalRatelimit: 
         defaultLimit:
           maxTokens: 1
           tokensPerFill: 1
           fillInterval: 100s
         enableXRatelimitHeaders: true
   EOF
   ```

2. Send a request to the httpbin app. Verify that your request succeeds and a 200 HTTP response code is returned. In addition, review the `x-ratelimit-*` headers that are returned. The `x-ratelimit-limit` header represents the token limit that is set on the gateway. To check how many tokens are available for subsequent requests, review the `x-ratelimit-remaining` header. Use the `x-ratelimit-reset` header to view how many seconds are left until the token bucket is refilled.
   {{< tabs items="LoadBalancer IP address or hostname,Port-forward for local testing" >}}
   {{% tab  %}}
   ```sh
   curl -vik http://$INGRESS_GW_ADDRESS:8080/status/200 -H "host: www.example.com:8080"
   ```
   {{% /tab %}}
   {{% tab  %}}
   ```sh
   curl -vik localhost:8080/status/200 -H "host: www.example.com"
   ```
   {{% /tab %}}
   {{< /tabs >}}

   Example output: 
   ```
   ...
   * Mark bundle as not supporting multiuse
   < HTTP/1.1 200 OK
   HTTP/1.1 200 OK
   < x-ratelimit-limit: 1
   x-ratelimit-limit: 1
   < x-ratelimit-remaining: 0
   x-ratelimit-remaining: 0
   < x-ratelimit-reset: 95
   x-ratelimit-reset: 95
   ...
   ```

3. Send another request to the httpbin app. Note that this time the request is denied with a 429 HTTP response code and a `local_rate_limited` message in your CLI output. Because the gateway is configured with only 1 token that is refilled every 100 seconds, the token was assigned to the connection of the first request. No tokens were available to be assigned to the second request. If you wait for 100 seconds, the token bucket is refilled and a new connection can be accepted by the gateway. 
   {{< tabs items="LoadBalancer IP address or hostname,Port-forward for local testing" >}}
   {{% tab  %}}
   ```sh
   curl -vik http://$INGRESS_GW_ADDRESS:8080/status/200 -H "host: www.example.com:8080"
   ```
   {{% /tab %}}
   {{% tab %}}
   ```sh
   curl -vik localhost:8080/status/200 -H "host: www.example.com"
   ```
   {{% /tab %}}
   {{< /tabs >}}

   Example output:
   ```
   ...
   * Mark bundle as not supporting multiuse
   < HTTP/1.1 429 Too Many Requests
   HTTP/1.1 429 Too Many Requests
   < x-ratelimit-limit: 1
   x-ratelimit-limit: 1
   < x-ratelimit-remaining: 0
   x-ratelimit-remaining: 0
   < x-ratelimit-reset: 79
   x-ratelimit-reset: 79
   ...
   Connection #0 to host 34.XXX.XX.XXX left intact
   local_rate_limited      
   ```
   

## Cleanup

{{< reuse "docs/snippets/cleanup.md" >}}

```sh
kubectl delete HTTPListenerPolicy local-ratelimit -n {{< reuse "docs/snippets/ns-system.md" >}}
```
