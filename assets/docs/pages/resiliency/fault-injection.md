Test the resilience of your apps by injecting delays and connection failures into a percentage of your requests.

## About fault injection

Fault injection is a chaos engineering technique that lets you deliberately introduce failures and delays into the request path so you can test how your services behave under adverse conditions before those conditions occur in production.

You can configure the following fault injection types with a {{< reuse "docs/snippets/trafficpolicy.md" >}}:

* **Delays**: Simulate timing failures such as network latency or overloaded backends by injecting a fixed delay before forwarding the request upstream.
* **Aborts**: Simulate crash failures by returning an HTTP or gRPC error code to the caller without forwarding the request.
* **Response rate limiting**: Simulate slow or degraded upstream connections by throttling the response body data rate.

Delays and aborts are independent of one another. When both are configured, a given request can be delayed only, delayed and then aborted, or aborted without a delay, depending on each fault's configured percentage.

Fault injection can be applied at the route level (via an HTTPRoute target) or at the gateway level (via a Gateway target). A route-level policy can also use `disable: {}` to opt out of a gateway-level fault injection policy.

For more information, see the [Fault injection API reference]({{< link-hextra path="/reference/api/#faultinjectionpolicy" >}}).

## Before you begin

{{< reuse "docs/snippets/prereq.md" >}}

## Delay requests {#delays}

Inject a fixed latency into requests before they are forwarded upstream.

1. Create a {{< reuse "docs/snippets/trafficpolicy.md" >}} that injects a 5-second delay on 50% of all requests to the httpbin route.
   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: {{< reuse "docs/snippets/trafficpolicy-apiversion.md" >}}
   kind: {{< reuse "docs/snippets/trafficpolicy.md" >}}
   metadata:
     name: httpbin-fault
     namespace: httpbin
   spec:
     targetRefs:
     - group: gateway.networking.k8s.io
       kind: HTTPRoute
       name: httpbin
     faultInjection:
       delay:
         fixedDelay: 5s
         percentage: 50
   EOF
   ```

   | Field | Description |
   |---|---|
   | `faultInjection.delay.fixedDelay` | The duration to delay before forwarding the request. Must be between `1ms` and `1h`. |
   | `faultInjection.delay.percentage` | The percentage of requests to delay. Defaults to `100`. |

2. Send several requests to the httpbin app. Verify that roughly half of the requests are delayed by 5 seconds, while the other half respond immediately.
   {{< tabs items="Cloud Provider LoadBalancer,Port-forward for local testing" tabTotal="2" >}}
   {{% tab tabName="Cloud Provider LoadBalancer" %}}
   ```sh
   for i in {1..6}; do
     time curl -s -o /dev/null http://$INGRESS_GW_ADDRESS:8080/status/200 \
       -H "host: www.example.com:8080"
   done
   ```
   {{% /tab %}}
   {{% tab tabName="Port-forward for local testing" %}}
   ```sh
   for i in {1..6}; do
     time curl -s -o /dev/null localhost:8080/status/200 \
       -H "host: www.example.com"
   done
   ```
   {{% /tab %}}
   {{< /tabs >}}

   Example output: 
   ```
   curl -s -o /dev/null localhost:8080/status/200 -H "host: www.example.com"  0.00s user 0.01s system 0% cpu 5.026 total
   curl -s -o /dev/null localhost:8080/status/200 -H "host: www.example.com"  0.00s user 0.01s system 0% cpu 5.022 total
   curl -s -o /dev/null localhost:8080/status/200 -H "host: www.example.com"  0.01s user 0.01s system 0% cpu 5.026 total
   curl -s -o /dev/null localhost:8080/status/200 -H "host: www.example.com"  0.00s user 0.01s system 0% cpu 5.018 total
   curl -s -o /dev/null localhost:8080/status/200 -H "host: www.example.com"  0.00s user 0.01s system 47% cpu 0.017 total
   curl -s -o /dev/null localhost:8080/status/200 -H "host: www.example.com"  0.00s user 0.00s system 48% cpu 0.011 total
   ```

## Abort requests {#aborts}

Terminate requests early by returning an error code to the caller. You can configure the gateway to return an HTTP or gRPC error code. The example in this guide returns an HTTP response code. 

1. Create or update the {{< reuse "docs/snippets/trafficpolicy.md" >}} to abort 100% of all requests with a 503 HTTP response code.
   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: {{< reuse "docs/snippets/trafficpolicy-apiversion.md" >}}
   kind: {{< reuse "docs/snippets/trafficpolicy.md" >}}
   metadata:
     name: httpbin-fault
     namespace: httpbin
   spec:
     targetRefs:
     - group: gateway.networking.k8s.io
       kind: HTTPRoute
       name: httpbin
     faultInjection:
       abort:
         httpStatus: 503
         percentage: 100
   EOF
   ```

   | Field | Description |
   |---|---|
   | `faultInjection.abort.httpStatus` | The HTTP status code to return. Must be between `200` and `599`. Mutually exclusive with `grpcStatus`. Note that if you want to set `grpcStatus` instead, use a value between `0` and `16`.  |
   | `faultInjection.abort.percentage` | The percentage of requests to abort. Defaults to `100`. |

3. Send a request to the httpbin app. Verify that the request is aborted with a 503 response.
   {{< tabs items="Cloud Provider LoadBalancer,Port-forward for local testing" tabTotal="2" >}}
   {{% tab tabName="Cloud Provider LoadBalancer" %}}
   ```sh
   curl -vi http://$INGRESS_GW_ADDRESS:8080/status/200 -H "host: www.example.com:8080"
   ```
   {{% /tab %}}
   {{% tab tabName="Port-forward for local testing" %}}
   ```sh
   curl -vi localhost:8080/status/200 -H "host: www.example.com"
   ```
   {{% /tab %}}
   {{< /tabs >}}

   Example output:
   ```
   HTTP/1.1 503 Service Unavailable
   ...
   fault filter abort
   ```

## Cleanup

{{< reuse "docs/snippets/cleanup.md" >}}

```sh
kubectl delete {{< reuse "docs/snippets/trafficpolicy.md" >}} httpbin-fault -n httpbin 
```

## Other configurations

Review other common fault injection configurations.

### Response rate limiting {#response-rate-limit}

Throttle the response body data rate to simulate slow or degraded upstream connections.

1. Create a {{< reuse "docs/snippets/trafficpolicy.md" >}} that limits the response rate to 8 kbits/s on all requests.
   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: {{< reuse "docs/snippets/trafficpolicy-apiversion.md" >}}
   kind: {{< reuse "docs/snippets/trafficpolicy.md" >}}
   metadata:
     name: httpbin-fault
     namespace: httpbin
   spec:
     targetRefs:
     - group: gateway.networking.k8s.io
       kind: HTTPRoute
       name: httpbin
     faultInjection:
       responseRateLimit:
         kbitsPerSecond: 8
         percentage: 100
   EOF
   ```

   | Field | Description |
   |---|---|
   | `faultInjection.responseRateLimit.kbitsPerSecond` | The maximum response data rate in kilobits per second. Must be at least `1`. |
   | `faultInjection.responseRateLimit.percentage` | The percentage of responses to rate limit. Defaults to `100`. |

2. Request a 500 KB response from httpbin without the rate limit and record the time as a baseline.
   {{< tabs items="Cloud Provider LoadBalancer,Port-forward for local testing" tabTotal="2" >}}
   {{% tab tabName="Cloud Provider LoadBalancer" %}}
   ```sh
   kubectl delete trafficpolicy httpbin-fault -n httpbin
   time curl -s -o /dev/null http://$INGRESS_GW_ADDRESS:8080/bytes/500000 \
     -H "host: www.example.com:8080"
   ```
   {{% /tab %}}
   {{% tab tabName="Port-forward for local testing" %}}
   ```sh
   kubectl delete trafficpolicy httpbin-fault -n httpbin
   time curl -s -o /dev/null localhost:8080/bytes/500000 \
     -H "host: www.example.com"
   ```
   {{% /tab %}}
   {{< /tabs >}}

   Example output:
   ```
   real    0m0.227s
   ```

3. Re-apply the rate limit and repeat the request. Verify that the download is significantly slower than the baseline.
   {{< tabs items="Cloud Provider LoadBalancer,Port-forward for local testing" tabTotal="2" >}}
   {{% tab tabName="Cloud Provider LoadBalancer" %}}
   ```sh
   kubectl apply -f- <<EOF
   apiVersion: {{< reuse "docs/snippets/trafficpolicy-apiversion.md" >}}
   kind: {{< reuse "docs/snippets/trafficpolicy.md" >}}
   metadata:
     name: httpbin-fault
     namespace: httpbin
   spec:
     targetRefs:
     - group: gateway.networking.k8s.io
       kind: HTTPRoute
       name: httpbin
     faultInjection:
       responseRateLimit:
         kbitsPerSecond: 8
         percentage: 100
   EOF
   time curl -s -o /dev/null http://$INGRESS_GW_ADDRESS:8080/bytes/500000 \
     -H "host: www.example.com:8080"
   ```
   {{% /tab %}}
   {{% tab tabName="Port-forward for local testing" %}}
   ```sh
   kubectl apply -f- <<EOF
   apiVersion: {{< reuse "docs/snippets/trafficpolicy-apiversion.md" >}}
   kind: {{< reuse "docs/snippets/trafficpolicy.md" >}}
   metadata:
     name: httpbin-fault
     namespace: httpbin
   spec:
     targetRefs:
     - group: gateway.networking.k8s.io
       kind: HTTPRoute
       name: httpbin
     faultInjection:
       responseRateLimit:
         kbitsPerSecond: 8
         percentage: 100
   EOF
   time curl -s -o /dev/null localhost:8080/bytes/500000 \
     -H "host: www.example.com"
   ```
   {{% /tab %}}
   {{< /tabs >}}

   Example output:
   ```
   real    0m12.487s
   ```

### Gateway-level fault injection {#gateway-level}

Apply fault injection to all routes that use a particular gateway by targeting the Gateway resource instead of an individual HTTPRoute.

```yaml
kubectl apply -f- <<EOF
apiVersion: {{< reuse "docs/snippets/trafficpolicy-apiversion.md" >}}
kind: {{< reuse "docs/snippets/trafficpolicy.md" >}}
metadata:
  name: fault-gateway
  namespace: {{< reuse "docs/snippets/namespace.md" >}}
spec:
  targetRefs:
  - group: gateway.networking.k8s.io
    kind: Gateway
    name: http
  faultInjection:
    abort:
      httpStatus: 503
      percentage: 100
EOF
```


### Disable fault injection per route {#disable}

When a gateway-level fault injection policy is in place, you can use `disable: {}` on a route-level {{< reuse "docs/snippets/trafficpolicy.md" >}} to exempt specific routes from fault injection.

```yaml
kubectl apply -f- <<EOF
apiVersion: {{< reuse "docs/snippets/trafficpolicy-apiversion.md" >}}
kind: {{< reuse "docs/snippets/trafficpolicy.md" >}}
metadata:
  name: fault-disable
  namespace: httpbin
spec:
  targetRefs:
  - group: gateway.networking.k8s.io
    kind: HTTPRoute
    name: httpbin-fault
  faultInjection:
    disable: {}
EOF
```


