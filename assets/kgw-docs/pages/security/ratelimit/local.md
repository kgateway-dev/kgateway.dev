Limit the number of requests that are allowed to enter the cluster before global rate limiting and external auth policies are applied.  

## About {#about}

Local {{< gloss "Rate Limiting" >}}rate limiting{{< /gloss >}} is a coarse-grained rate limiting capability that is primarily used as a first line of defense mechanism to limit the number of requests that are forwarded to your rate limit servers. 

Without local rate limiting, all requests are directly forwarded to a rate limit server that you set up where the request is either denied or allowed based on the global rate limiting settings that you configured. However, during an attack, too many requests might be forwarded to your rate limit servers and can cause overload or even failure.

To protect your rate limit servers from being overloaded and to optimize their resource utilization, you can set up local rate limiting in conjunction with global rate limiting. Because local rate limiting is enforced in each Envoy instance that makes up your gateway, no rate limit server is required in this setup. For example, if you have 5 Envoy instances that together represent your gateway, each instance is configured with the limit that you set. 

For more information about local rate limiting, see the [Envoy documentation](https://www.envoyproxy.io/docs/envoy/latest/configuration/http/http_filters/local_rate_limit_filter). 

### Architecture

The following image shows how local rate limiting works in {{< reuse "/kgw-docs/snippets/kgateway.md" >}}. As clients send requests to a backend destination, they first reach the Envoy instance that represents your gateway. Local rate limiting settings are applied to an Envoy pod or process. By default, limits are applied to each pod or process. For example, if you have 5 Envoy instances that are configured with a local rate limit of 10 requests per second, the total number of allowed requests per second is 50 (5 x 10). In a global rate limiting setup, this limit is shared between all Envoy instances, so the total number of allowed requests per second is 10. {{< version exclude-if="2.1.x,2.2.x,2.3.x,2.4.x" >}}To apply a single limit across all replicas of a gateway without running a rate limit server, see [Share a limit across gateway replicas](#share-across-gateway).{{< /version >}}

Depending on your setup, each Envoy instance or pod is configured with a number of tokens in a token bucket. To allow a request, a token must be available in the bucket so that it can be assigned to a downstream connection. Token buckets are refilled occasionally as defined in the refill setting of the local rate limiting configuration. If no token is available, the connection is closed immediately, and a 429 HTTP response code is returned to the client. 

When a token is available in the token bucket it can be assigned to an incoming connection. The request is then forwarded to your rate limit server to enforce any global rate limiting settings. For example, the request might be further rate limited based on headers or query parameters. Only requests that are within the local and global rate limits are forwarded to the backend destination in the cluster. 

{{< reuse-image src="/img/local-rate-limiting.svg" caption="Local rate limiting" width="600px" >}}
{{< reuse-image-dark srcDark="/img/local-rate-limiting.svg" caption="Local rate limiting" width="600px" >}}

### Local rate limiting

In {{< reuse "kgw-docs/snippets/kgateway.md" >}}, you use a [{{< reuse "kgw-docs/snippets/trafficpolicy.md" >}}]({{< link-hextra path="/about/policies/trafficpolicy/" >}}) to set up local rate limiting for your routes. You can choose between the following attachment options: 
* **A particular route in an HTTPRoute resource**: Use the `extensionRef` filter in the HTTPRoute to attach the {{< reuse "kgw-docs/snippets/trafficpolicy.md" >}} to the route you want to rate limit. For an example, see [Route configuration](#route). 
* **All routes in an HTTPRoute**: Use the `targetRefs` section in the {{< reuse "kgw-docs/snippets/trafficpolicy.md" >}} to attach the policy to a particular HTTPRoute resource. 
* **All routes that the Gateway serves**: Use the `targetRefs` section in the {{< reuse "kgw-docs/snippets/trafficpolicy.md" >}} to attach the policy to a Gateway. For an example, see [Gateway configuration](#gateway). 

Note that if you apply a policy to an HTTPRoute and to a Gateway at the same time, the HTTPRoute policy takes precedence. For more information, see [{{< reuse "kgw-docs/snippets/trafficpolicy.md" >}}]({{< link-hextra path="/about/policies/trafficpolicy/#policy-priority-and-merging-rules" >}}). 

## Before you begin

{{< reuse "kgw-docs/snippets/prereq.md" >}}

## Route configuration {#route}

Set up local rate limiting for a particular route. 

1. Create a {{< reuse "kgw-docs/snippets/trafficpolicy.md" >}} with your local rate limiting settings. 
   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: {{< reuse "kgw-docs/snippets/trafficpolicy-apiversion.md" >}}
   kind: {{< reuse "kgw-docs/snippets/trafficpolicy.md" >}}
   metadata:
     name: local-ratelimit
     namespace: httpbin
   spec:
     rateLimit:
       local:
         tokenBucket:
           maxTokens: 1
           tokensPerFill: 1
           fillInterval: 100s
   EOF
   ```

   | Setting | Description |
   | ------- | ----------- |
   | `maxTokens` | The maximum number of tokens that are available to use.   |
   | `tokensPerFill` | The number of tokens that are added during a refill.  |
   | `fillIntervall` | The number of seconds, after which the token bucket is refilled. |

2. Create an HTTPRoute that limits requests to the httpbin app along the `ratelimit.example` domain. To apply the {{< reuse "kgw-docs/snippets/trafficpolicy.md" >}} that created earlier, you use the `extensionRef` filter. 
   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.networking.k8s.io/v1
   kind: HTTPRoute
   metadata:
     name: httpbin-ratelimit
     namespace: httpbin
   spec:
     parentRefs:
     - name: http
       namespace: {{< reuse "kgw-docs/snippets/namespace.md" >}}
     hostnames:
     - ratelimit.example
     rules:
     - matches:
       - path:
           type: PathPrefix
           value: /
       filters:
       - type: ExtensionRef
         extensionRef:
           name: local-ratelimit
           group: {{< reuse "kgw-docs/snippets/trafficpolicy-group.md" >}}
           kind: {{< reuse "kgw-docs/snippets/trafficpolicy.md" >}}
       backendRefs:
       - name: httpbin
         port: 8000
   EOF
   ```

3. Send a request to the httpbin app. Verify that you get back a 200 HTTP response code. 
   {{< tabs >}}
   {{% tab name="Cloud Provider LoadBalancer" %}}
   ```sh
   curl -vi http://$INGRESS_GW_ADDRESS:8080/status/200 -H "host: ratelimit.example:8080"
   ```
   {{% /tab %}}
   {{% tab name="Port-forward for local testing" %}}
   ```sh
   curl -vi localhost:8080/status/200 -H "host: ratelimit.example"
   ```
   {{% /tab %}}
   {{< /tabs >}}
   
   Example output: 
   ```
   * Request completely sent off
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
   
4. Send another request to the httpbin app. Note that this time the request is denied with a 429 HTTP response code and a `local_rate_limited` message in your CLI output. Because the route is configured with only 1 token that is refilled every 100 seconds, the token was assigned to the connection of the first request. No tokens were available to be assigned to the second request. If you wait for 100 seconds, the token bucket is refilled and a new connection can be accepted by the route. 
   {{< tabs >}}
   {{% tab name="Cloud Provider LoadBalancer" %}}
   ```sh
   curl -vi http://$INGRESS_GW_ADDRESS:8080/status/200 -H "host: ratelimit.example:8080"
   ```
   {{% /tab %}}
   {{% tab name="Port-forward for local testing" %}}
   ```sh
   curl -vi localhost:8080/status/200 -H "host: ratelimit.example"
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
   
## Gateway configuration {#gateway}

Instead of applying local rate limiting to a particular route, you can also apply it to an entire gateway. This way, the local rate limiting settings are applied to all the routes that the gateway serves. 

1. Create a {{< reuse "kgw-docs/snippets/trafficpolicy.md" >}} with your local rate limiting settings. Use the `targetRefs` section to apply the policy to a specific Gateway. The policy automatically applies to all the routes that the Gateway serves. 
   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: {{< reuse "kgw-docs/snippets/trafficpolicy-apiversion.md" >}}
   kind: {{< reuse "kgw-docs/snippets/trafficpolicy.md" >}}
   metadata:
     name: local-ratelimit
     namespace: {{< reuse "kgw-docs/snippets/namespace.md" >}}
   spec:
     targetRefs: 
     - group: gateway.networking.k8s.io
       kind: Gateway
       name: http
     rateLimit:
       local:
         tokenBucket:
           maxTokens: 1
           tokensPerFill: 1
           fillInterval: 100s
   EOF
   ```

   | Setting | Description |
   | ------- | ----------- |
   | `targetRefs`| Select the Gateway that you want to apply your local rate limiting configuration to. In this example, the policy is applied to all the routes that the `http` gateway serves.  |
   | `maxTokens` | The maximum number of tokens that are available to use.   |
   | `tokensPerFill` | The number of tokens that are added during a refill.  |
   | `fillIntervall` | The number of seconds, after which the token bucket is refilled. |
   
3. Send a request to the httpbin app alongside the `www.example.com` domain that you set up as part of the getting started tutorial. Verify that the request succeeds.
   {{< tabs >}}
   {{% tab name="Cloud Provider LoadBalancer" %}}
   ```sh
   curl -vi http://$INGRESS_GW_ADDRESS:8080/status/200 -H "host: www.example.com:8080"
   ```
   {{% /tab %}}
   {{% tab name="Port-forward for local testing" %}}
   ```sh
   curl -vi localhost:8080/status/200 -H "host: www.example.com"
   ```
   {{% /tab %}}
   {{< /tabs >}}
   
   Example output: 
   ```
   * Request completely sent off
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

4. Send another request to the httpbin app. Note that this time the request is denied with a 429 HTTP response code and a `local_rate_limited` message in your CLI output. Because the gateway is configured with only 1 token that is refilled every 100 seconds, the token was assigned to the connection of the first request. No tokens were available to be assigned to the second request. If you wait for 100 seconds, the token bucket is refilled and a new connection can be accepted by the gateway. 
   {{< tabs >}}
   {{% tab name="Cloud Provider LoadBalancer" %}}
   ```sh
   curl -vi http://$INGRESS_GW_ADDRESS:8080/status/200 -H "host: www.example.com:8080"
   ```
   {{% /tab %}}
   {{% tab name="Port-forward for local testing" %}}
   ```sh
   curl -vi localhost:8080/status/200 -H "host: www.example.com"
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

## Disable rate limiting for a route {#disable-route}

Sometimes, you might want to disable {{< gloss "Rate Limiting" >}}rate limiting{{< /gloss >}}  for a route. For example, you might have system critical routes that should be accessible even under high traffic conditions, such as a health check or admin endpoints. You can exclude a route from rate limiting by setting `rateLimit.local` to `{}` in the {{< reuse "kgw-docs/snippets/trafficpolicy.md" >}}. 

1. Create a Gateway-level {{< reuse "kgw-docs/snippets/trafficpolicy.md" >}} to enforce local rate limiting on all routes. For more information, refer to the [Gateway configuration](#gateway).

   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: {{< reuse "kgw-docs/snippets/trafficpolicy-apiversion.md" >}}
   kind: {{< reuse "kgw-docs/snippets/trafficpolicy.md" >}}
   metadata:
     name: local-ratelimit
     namespace: {{< reuse "kgw-docs/snippets/namespace.md" >}}
   spec:
     targetRefs: 
     - group: gateway.networking.k8s.io
       kind: Gateway
       name: http
     rateLimit:
       local:
         tokenBucket:
           maxTokens: 1
           tokensPerFill: 1
           fillInterval: 100s
   EOF
   ```

2. Create an HTTPRoute for the route that you want to exclude from rate limiting, such as `/anything` on the `httpbin` app. Note that because no {{< reuse "kgw-docs/snippets/trafficpolicy.md" >}} applies to this HTTPRoute yet, the Gateway-level rate limit policy is enforced for the `/anything` route.

   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.networking.k8s.io/v1
   kind: HTTPRoute
   metadata:
     name: httpbin-anything
     namespace: httpbin
   spec:
     parentRefs:
     - name: http
       namespace: {{< reuse "kgw-docs/snippets/namespace.md" >}}
     hostnames:
     - www.example.com
     rules:
     - matches:
       - path:
           type: PathPrefix
           value: /anything
       backendRefs:
       - name: httpbin
         port: 8000
   EOF
   ```

3. Send two requests to verify that the route is rate limited due to the Gateway-level {{< reuse "kgw-docs/snippets/trafficpolicy.md" >}} that allows only 1 request per 100 seconds.

   {{< tabs >}}
   {{% tab name="Cloud Provider LoadBalancer" %}}
   ```sh
   for i in {1..2}; do curl -vi http://$INGRESS_GW_ADDRESS:8080/anything -H "host: www.example.com:8080"; done
   ```
   {{% /tab %}}
   {{% tab name="Port-forward for local testing" %}}
   ```sh
   for i in {1..2}; do curl -vi localhost:8080/anything -H "host: www.example.com"; done
   ```
   {{% /tab %}}
   {{< /tabs >}}

   Example output: Verify that the first request succeeds and the second request is rate limited.
   
   Request 1:
   ```
   < HTTP/1.1 200 OK
   HTTP/1.1 200 OK   
   ...
   ```

   Request 2:
   ```
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

4. Create a {{< reuse "kgw-docs/snippets/trafficpolicy.md" >}} to disable rate limiting for the HTTPRoute.

   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: {{< reuse "kgw-docs/snippets/trafficpolicy-apiversion.md" >}}
   kind: {{< reuse "kgw-docs/snippets/trafficpolicy.md" >}}
   metadata:
     name: disable-ratelimit
     namespace: httpbin
   spec:
     targetRefs:
     - group: gateway.networking.k8s.io
       kind: HTTPRoute
       name: httpbin-anything
     rateLimit:
       local: {}
   EOF
   ```

5. Repeat the requests. This time, the requests succeed because the HTTPRoute is excluded from rate limiting.

   {{< tabs >}}
   {{% tab name="Cloud Provider LoadBalancer" %}}
   ```sh
   for i in {1..2}; do curl -vi http://$INGRESS_GW_ADDRESS:8080/anything -H "host: www.example.com:8080"; done
   ```
   {{% /tab %}}
   {{% tab name="Port-forward for local testing" %}}
   ```sh
   for i in {1..2}; do curl -vi localhost:8080/anything -H "host: www.example.com"; done
   ```
   {{% /tab %}}
   {{< /tabs >}}

   Example output:
   
   Request 1:
   ```
   < HTTP/1.1 200 OK
   HTTP/1.1 200 OK   
   ...
   ```

   Request 2:
   ```
   < HTTP/1.1 200 OK
   HTTP/1.1 200 OK   
   ...
   ```

{{< version exclude-if="2.1.x,2.2.x,2.3.x,2.4.x" >}}

## Share a limit across gateway replicas {#share-across-gateway}

By default, every replica of a gateway enforces the token bucket independently, so the effective limit scales with the number of replicas. A bucket of 100 requests per second across 4 replicas admits up to 400 requests per second. That behavior is fine as a safety valve, but it makes the real limit depend on how many replicas happen to be running, which changes whenever the gateway scales.

Set `shareAcrossGateway: true` to treat the token bucket as the limit for the gateway as a whole. Each replica receives an even share of the bucket based on the current replica count, so the configured rate becomes the total rate that all replicas admit together. With `tokensPerFill: 100` and `fillInterval: 1s`, a gateway with 4 replicas admits 100 requests per second in total rather than 100 per replica.

This setting gives you a gateway-wide limit without deploying a rate limit server. Unlike [global rate limiting]({{< link-hextra path="/security/ratelimit/global/" >}}), the replicas do not coordinate with each other or share a counter. Each one simply enforces its own fraction of the bucket, so a client whose requests are unevenly distributed across replicas can still be limited earlier than the total suggests.

Keep the following in mind when you use this setting:

* `shareAcrossGateway` requires `tokenBucket` to be set. The gateway rejects the policy otherwise.
* Set `maxTokens` to at least the number of replicas. Because the bucket is divided, a `maxTokens` value lower than the replica count leaves some replicas with no tokens at all, and requests that reach those replicas are rate limited immediately.

1. Create a {{< reuse "kgw-docs/snippets/trafficpolicy.md" >}} that applies a gateway-wide limit. This example allows 4 requests per 300 seconds across the entire gateway.
   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: {{< reuse "kgw-docs/snippets/trafficpolicy-apiversion.md" >}}
   kind: {{< reuse "kgw-docs/snippets/trafficpolicy.md" >}}
   metadata:
     name: local-ratelimit
     namespace: {{< reuse "kgw-docs/snippets/namespace.md" >}}
   spec:
     targetRefs:
     - group: gateway.networking.k8s.io
       kind: Gateway
       name: http
     rateLimit:
       local:
         shareAcrossGateway: true
         tokenBucket:
           maxTokens: 4
           tokensPerFill: 4
           fillInterval: 300s
   EOF
   ```

   | Setting | Description |
   | ------- | ----------- |
   | `shareAcrossGateway` | Applies the token bucket to the gateway as a whole instead of to each replica. Defaults to `false`. |
   | `maxTokens` | The maximum number of tokens that are available to use, across all replicas of the gateway. |
   | `tokensPerFill` | The number of tokens that are added during a refill, across all replicas of the gateway. |
   | `fillInterval` | The number of seconds, after which the token bucket is refilled. |

2. Scale the gateway proxy to 4 replicas so that the bucket is divided.
   ```sh
   kubectl scale deployment/http -n {{< reuse "kgw-docs/snippets/namespace.md" >}} --replicas=4
   ```

3. Verify that the gateway proxy is configured to divide the bucket. Port-forward the gateway proxy on port 19000 and check the rate limit filter configuration.
   ```sh
   kubectl port-forward deployment/http -n {{< reuse "kgw-docs/snippets/namespace.md" >}} 19000
   ```

   ```sh
   curl -s 127.0.0.1:19000/config_dump | jq '.. | objects
     | select(."@type"? == "type.googleapis.com/envoy.extensions.filters.http.local_ratelimit.v3.LocalRateLimit")
     | {token_bucket, local_cluster_rate_limit}'
   ```

   Example output: Note that the token bucket still reports the values that you configured. The `local_cluster_rate_limit` field is what instructs each proxy to enforce only its own share of that bucket at runtime, so you do not see pre-divided numbers in the config dump.
   ```console
   {
     "token_bucket": {
       "max_tokens": 4,
       "tokens_per_fill": 4,
       "fill_interval": "300s"
     },
     "local_cluster_rate_limit": {}
   }
   ```

4. Port-forward a single gateway proxy pod so that all of your requests reach the same replica.
   ```sh
   kubectl port-forward $(kubectl get pods -n {{< reuse "kgw-docs/snippets/namespace.md" >}} -l app.kubernetes.io/name=http -o jsonpath='{.items[0].metadata.name}') -n {{< reuse "kgw-docs/snippets/namespace.md" >}} 8080:8080
   ```

5. Send 6 requests to that replica. Verify that only the first request succeeds. The 4-token bucket is divided across the 4 replicas, so this replica holds a single token.
   ```sh
   for i in {1..6}; do curl -s -o /dev/null -w '%{http_code}\n' localhost:8080/status/200 -H "host: www.example.com"; done
   ```

   Example output:
   ```console
   200
   429
   429
   429
   429
   429
   ```

6. To see the difference, set `shareAcrossGateway` to `false` and repeat the requests.
   ```sh
   kubectl patch {{< reuse "kgw-docs/snippets/trafficpolicy.md" >}} local-ratelimit -n {{< reuse "kgw-docs/snippets/namespace.md" >}} \
     --type=merge -p '{"spec":{"rateLimit":{"local":{"shareAcrossGateway":false}}}}'
   ```

   Example output: This time, 4 requests succeed, because the replica holds the full bucket rather than a quarter of it.
   ```console
   200
   200
   200
   200
   429
   429
   ```

7. Scale the gateway proxy back down.
   ```sh
   kubectl scale deployment/http -n {{< reuse "kgw-docs/snippets/namespace.md" >}} --replicas=1
   ```

{{< /version >}}

{{< version exclude-if="2.3.x,2.4.x,2.5.x" >}}

## Cleanup

{{< reuse "kgw-docs/snippets/cleanup.md" >}}

```sh
kubectl delete {{< reuse "kgw-docs/snippets/trafficpolicy.md" >}} local-ratelimit -n httpbin
kubectl delete {{< reuse "kgw-docs/snippets/trafficpolicy.md" >}} local-ratelimit -n {{< reuse "kgw-docs/snippets/namespace.md" >}}
kubectl delete {{< reuse "kgw-docs/snippets/trafficpolicy.md" >}} disable-ratelimit -n httpbin
kubectl delete httproute httpbin-ratelimit -n httpbin
kubectl delete httproute httpbin-anything -n httpbin
```

{{< /version >}}


