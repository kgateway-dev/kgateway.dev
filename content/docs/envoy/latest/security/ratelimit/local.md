---
title: Local rate limiting
weight: 5
description: Limit the number of requests that are allowed to enter the cluster before global rate limiting and external auth policies are applied.  
---

{{< reuse "docs/pages/security/ratelimit/local.md" >}}

## Gradual rollout and shadow mode {#gradual-rollout}

The `percentEnabled` and `percentEnforced` fields let you control how aggressively the rate limit filter acts on incoming traffic. This is useful for two common scenarios:

- **Gradual rollout**: Increase `percentEnabled` (and optionally `percentEnforced`) incrementally to roll out rate limiting to a growing percentage of traffic without affecting all requests at once.
- **Shadow mode**: Set `percentEnabled: 100` and `percentEnforced: 0`. The filter runs for all requests and records statistics, such as the number of requests that would have been rate limited, but does not actually block any traffic. This setup lets you validate your token bucket configuration before enforcing it in production.

The following steps walk through a shadow mode setup where rate limiting is observed but not enforced. You switch to full rate limit enforcement in subsequent steps. 

1. Create a rate limit config in your {{< reuse "docs/snippets/trafficpolicy.md" >}}. In this example, the rate limit filter is enabled for all requests (`percentEnabled: 100`), but no requests are blocked (`percentEnforced: 0`).
   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: {{< reuse "docs/snippets/trafficpolicy-apiversion.md" >}}
   kind: {{< reuse "docs/snippets/trafficpolicy.md" >}}
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
         percentEnabled: 100
         percentEnforced: 0
   EOF
   ```

   | Setting | Description |
   | ------- | ----------- |
   | `maxTokens` | The maximum number of tokens that are available to use. |
   | `tokensPerFill` | The number of tokens that are added during a refill. |
   | `fillInterval` | The number of seconds after which the token bucket is refilled. |
   | `percentEnabled` | The percentage of requests for which the rate limit filter is enabled. Set to `100` so that the filter runs on all requests and collects statistics. |
   | `percentEnforced` | The percentage of requests for which the rate limit is enforced. Set to `0` so that no requests are blocked, even when the token bucket is exhausted. |

2. Create an HTTPRoute that applies the {{< reuse "docs/snippets/trafficpolicy.md" >}} to the httpbin app along the `ratelimit.example` domain.
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
       namespace: {{< reuse "docs/snippets/namespace.md" >}}
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
           group: {{< reuse "docs/snippets/trafficpolicy-group.md" >}}
           kind: {{< reuse "docs/snippets/trafficpolicy.md" >}}
       backendRefs:
       - name: httpbin
         port: 8000
   EOF
   ```

3. Send two requests to the httpbin app. Verify that both succeed with a 200 HTTP response code, even though the token bucket is configured with only 1 token. Because `percentEnforced` is set to `0`, the rate limit filter is running in shadow mode and is not blocking any requests.
   {{< tabs tabTotal="2" items="Cloud Provider LoadBalancer,Port-forward for local testing" >}}
   {{% tab tabName="Cloud Provider LoadBalancer" %}}
   ```sh
   for i in {1..2}; do curl -vi http://$INGRESS_GW_ADDRESS:8080/status/200 -H "host: ratelimit.example:8080"; done
   ```
   {{% /tab %}}
   {{% tab tabName="Port-forward for local testing" %}}
   ```sh
   for i in {1..2}; do curl -vi localhost:8080/status/200 -H "host: ratelimit.example"; done
   ```
   {{% /tab %}}
   {{< /tabs >}}

   Example output: Both requests succeed.
   ```
   < HTTP/1.1 200 OK
   HTTP/1.1 200 OK
   ...
   < HTTP/1.1 200 OK
   HTTP/1.1 200 OK
   ...
   ```

4. Check the Envoy statistics to observe how many requests would have been rate limited. The local rate limit filter exposes stats through the Envoy admin API under the `http_local_rate_limiter.http_local_rate_limit.*` prefix.

   Port-forward to the Envoy admin endpoint on the gateway proxy pod and query the local rate limit stats:
   ```sh
   kubectl port-forward deploy/http -n {{< reuse "docs/snippets/namespace.md" >}} 19000:19000 & sleep 1 && curl -s localhost:19000/stats | grep local_rate_limit; kill %1
   ```

   Example output:
   ```
   http_local_rate_limiter.http_local_rate_limit.enabled: 2
   http_local_rate_limiter.http_local_rate_limit.enforced: 0
   http_local_rate_limiter.http_local_rate_limit.ok: 1
   http_local_rate_limiter.http_local_rate_limit.rate_limited: 1
   ```

   | Stat | Description |
   | ---- | ----------- |
   | `enabled` | Total number of requests for which the rate limit filter ran. |
   | `ok` | Number of requests that had a token available and were allowed through. |
   | `rate_limited` | Number of requests that exceeded the token bucket and would have been blocked. |
   | `enforced` | Number of requests that were actually blocked with a 429 response. In shadow mode this is `0`. |

   In this example, 2 requests were processed by the filter, 1 was within the token limit (`ok: 1`), and 1 would have been rate limited (`rate_limited: 1`), but nothing was actually blocked (`enforced: 0`). Use the `rate_limited` counter to assess whether your token bucket settings reflect realistic traffic patterns before moving to enforcement.

5. When you are satisfied with your token bucket configuration, update the {{< reuse "docs/snippets/trafficpolicy.md" >}} to enforce rate limiting for all requests by setting `percentEnforced` to `100`.
   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: {{< reuse "docs/snippets/trafficpolicy-apiversion.md" >}}
   kind: {{< reuse "docs/snippets/trafficpolicy.md" >}}
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
         percentEnabled: 100
         percentEnforced: 100
   EOF
   ```

6. Send two requests again. Verify that this time, only the first request succeeds. The second request is denied with a 429 HTTP response code and a `local_rate_limited` message.
   {{< tabs tabTotal="2" items="Cloud Provider LoadBalancer,Port-forward for local testing" >}}
   {{% tab tabName="Cloud Provider LoadBalancer" %}}
   ```sh
   for i in {1..2}; do curl -vi http://$INGRESS_GW_ADDRESS:8080/status/200 -H "host: ratelimit.example:8080"; done
   ```
   {{% /tab %}}
   {{% tab tabName="Port-forward for local testing" %}}
   ```sh
   for i in {1..2}; do curl -vi localhost:8080/status/200 -H "host: ratelimit.example"; done
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
kubectl delete {{< reuse "docs/snippets/trafficpolicy.md" >}} local-ratelimit -n httpbin
kubectl delete {{< reuse "docs/snippets/trafficpolicy.md" >}} local-ratelimit -n {{< reuse "docs/snippets/namespace.md" >}}
kubectl delete {{< reuse "docs/snippets/trafficpolicy.md" >}} disable-ratelimit -n httpbin
kubectl delete httproute httpbin-ratelimit -n httpbin
kubectl delete httproute httpbin-anything -n httpbin
```
