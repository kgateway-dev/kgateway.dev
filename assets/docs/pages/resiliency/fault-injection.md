Test the resilience of your apps by injecting delays and connection failures into a percentage of your requests.

## About fault injection

Fault injection lets you deliberately introduce failures into your request path for chaos engineering and resiliency testing. {{< reuse "/docs/snippets/kgateway-capital.md" >}} maps fault injection configuration directly to the Envoy [HTTP fault filter](https://www.envoyproxy.io/docs/envoy/latest/configuration/http/http_filters/fault_filter), and supports the following fault types:

* **Abort**: Terminates requests early with a specified HTTP or gRPC status code, simulating crash failures such as backend errors.
* **Delay**: Injects artificial latency before forwarding a request upstream, simulating timing failures such as network latency or overloaded backends.
* **Response rate limit**: Throttles the response body data rate to simulate slow or degraded upstream connections.

Faults are configured by creating a {{< reuse "docs/snippets/trafficpolicy.md" >}} resource and attaching it to a Gateway or HTTPRoute via `targetRefs`. When attached to a Gateway, the fault applies to all routes on that gateway. When attached to an HTTPRoute, the fault applies only to that specific route.

You can also use a route-level `disable` override to opt specific routes out of a gateway-level fault policy.

## Before you begin

{{< reuse "docs/snippets/prereq.md" >}}

## Abort {#abort}

Abort incoming requests with a specific HTTP status code.

1. Configure the {{< reuse "docs/snippets/trafficpolicy.md" >}} to abort requests with a 503 HTTP status code. You can attach the policy to an HTTPRoute to affect a specific route, or to a Gateway to affect all routes.
   {{< tabs items="HTTPRoute,Gateway" tabTotal="2" >}}
   {{% tab tabName="HTTPRoute" %}}
   The following example aborts 50% of requests to the httpbin app. Other routes on the same gateway are not affected.
   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: {{< reuse "docs/snippets/trafficpolicy-apiversion.md" >}}
   kind: {{< reuse "docs/snippets/trafficpolicy.md" >}}
   metadata:
     name: fault-abort
     namespace: httpbin
   spec:
     targetRefs:
     - group: gateway.networking.k8s.io
       kind: HTTPRoute
       name: httpbin
     faultInjection:
       abort:
         httpStatus: 503
         percentage: 50
   EOF
   ```
   {{% /tab %}}
   {{% tab tabName="Gateway" %}}
   The following example aborts 100% of requests on the gateway. All routes on this gateway are affected.
   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: {{< reuse "docs/snippets/trafficpolicy-apiversion.md" >}}
   kind: {{< reuse "docs/snippets/trafficpolicy.md" >}}
   metadata:
     name: fault-abort
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
   {{% /tab %}}
   {{< /tabs >}}

   | Field | Description |
   |-------|-------------|
   | `targetRefs` | The HTTPRoute or Gateway to apply the fault injection to. |
   | `faultInjection.abort.httpStatus` | The HTTP status code to return for aborted requests. Must be between 200-599. |
   | `faultInjection.abort.percentage` | The percentage of requests to abort (0-100). Defaults to 100 if not set. |

2. Send a few requests to the httpbin app. Verify that requests are rejected with a 503 HTTP response code at the percentage that matches what you set in the {{< reuse "docs/snippets/trafficpolicy.md" >}}.
   {{< tabs items="Cloud Provider LoadBalancer,Port-forward for local testing" tabTotal="2" >}}
   {{% tab tabName="Cloud Provider LoadBalancer" %}}
   ```sh
   curl -i http://$INGRESS_GW_ADDRESS:8080/status/200 -H "host: www.example.com:8080"
   ```
   {{% /tab %}}
   {{% tab tabName="Port-forward for local testing" %}}
   ```sh
   curl -i localhost:8080/status/200 -H "host: www.example.com"
   ```
   {{% /tab %}}
   {{< /tabs >}}

   Example output for a successful response:
   ```
   HTTP/1.1 200 OK
   access-control-allow-credentials: true
   access-control-allow-origin: *
   date: Tue, 23 Apr 2024 17:12:13 GMT
   x-envoy-upstream-service-time: 0
   server: envoy
   transfer-encoding: chunked
   ```

   Example output for an aborted request:
   ```
   HTTP/1.1 503 Service Unavailable
   content-length: 18
   content-type: text/plain
   date: Tue, 23 Apr 2024 17:12:08 GMT
   server: envoy
   ```

3. When you are done, remove the {{< reuse "docs/snippets/trafficpolicy.md" >}}.
   {{< tabs items="HTTPRoute,Gateway" tabTotal="2" >}}
   {{% tab tabName="HTTPRoute" %}}
   ```sh
   kubectl delete trafficpolicy fault-abort -n httpbin
   ```
   {{% /tab %}}
   {{% tab tabName="Gateway" %}}
   ```sh
   kubectl delete trafficpolicy fault-abort -n {{< reuse "docs/snippets/namespace.md" >}}
   ```
   {{% /tab %}}
   {{< /tabs >}}

## Delay {#delay}

Delay, or inject latency into, incoming requests for a certain amount of time. 

1. Create a {{< reuse "docs/snippets/trafficpolicy.md" >}} that delays requests. You can attach the policy to an HTTPRoute to affect a specific route, or to a Gateway to affect all routes.
   {{< tabs items="HTTPRoute,Gateway" tabTotal="2" >}}
   {{% tab tabName="HTTPRoute" %}}
   The following example delays 50% of requests to the httpbin app by 500 milliseconds. Other routes on the same gateway are not affected.
   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: {{< reuse "docs/snippets/trafficpolicy-apiversion.md" >}}
   kind: {{< reuse "docs/snippets/trafficpolicy.md" >}}
   metadata:
     name: fault-delay
     namespace: httpbin
   spec:
     targetRefs:
     - group: gateway.networking.k8s.io
       kind: HTTPRoute
       name: httpbin
     faultInjection:
       delay:
         fixedDelay: "500ms"
         percentage: 50
   EOF
   ```
   {{% /tab %}}
   {{% tab tabName="Gateway" %}}
   The following example delays 100% of requests by 500 milliseconds on the gateway. All routes on this gateway are affected.
   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: {{< reuse "docs/snippets/trafficpolicy-apiversion.md" >}}
   kind: {{< reuse "docs/snippets/trafficpolicy.md" >}}
   metadata:
     name: fault-delay
     namespace: {{< reuse "docs/snippets/namespace.md" >}}
   spec:
     targetRefs:
     - group: gateway.networking.k8s.io
       kind: Gateway
       name: http
     faultInjection:
       delay:
         fixedDelay: "500ms"
         percentage: 100
   EOF
   ```
   {{% /tab %}}
   {{< /tabs >}}

   | Field | Description |
   |-------|-------------|
   | `targetRefs` | The HTTPRoute or Gateway to apply the fault injection to. |
   | `faultInjection.delay.fixedDelay` | The duration to delay requests. Must be between 1ms and 1h. Supported units: `h`, `m`, `s`, `ms`. |
   | `faultInjection.delay.percentage` | The percentage of requests to delay (0-100). Defaults to 100 if not set. |

2. Send a few requests to the httpbin app. Verify that some requests are delayed by approximately 500 milliseconds.
   {{< tabs items="Cloud Provider LoadBalancer,Port-forward for local testing" tabTotal="2" >}}
   {{% tab tabName="Cloud Provider LoadBalancer" %}}
   ```sh
   curl -i http://$INGRESS_GW_ADDRESS:8080/status/200 -H "host: www.example.com:8080" -w "\nTotal time: %{time_total}s\n"
   ```
   {{% /tab %}}
   {{% tab tabName="Port-forward for local testing" %}}
   ```sh
   curl -i localhost:8080/status/200 -H "host: www.example.com" -w "\nTotal time: %{time_total}s\n"
   ```
   {{% /tab %}}
   {{< /tabs >}}

   Example output for a delayed request:
   ```
   HTTP/1.1 200 OK
   access-control-allow-credentials: true
   access-control-allow-origin: *
   date: Tue, 23 Apr 2024 17:18:51 GMT
   x-envoy-upstream-service-time: 0
   server: envoy
   transfer-encoding: chunked

   Total time: 0.512s
   ```

3. When you are done, remove the {{< reuse "docs/snippets/trafficpolicy.md" >}}.
   {{< tabs items="HTTPRoute,Gateway" tabTotal="2" >}}
   {{% tab tabName="HTTPRoute" %}}
   ```sh
   kubectl delete trafficpolicy fault-delay -n httpbin
   ```
   {{% /tab %}}
   {{% tab tabName="Gateway" %}}
   ```sh
   kubectl delete trafficpolicy fault-delay -n {{< reuse "docs/snippets/namespace.md" >}}
   ```
   {{% /tab %}}
   {{< /tabs >}}

## Response rate limit {#response-rate-limit}

Use a {{< reuse "docs/snippets/trafficpolicy.md" >}} resource to limit the rate at which response data is sent back to the client. This is useful for simulating slow or degraded upstream connections.

1. Create a {{< reuse "docs/snippets/trafficpolicy.md" >}} that limits the response rate to 1 kbit/s for 100% of requests.
   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: {{< reuse "docs/snippets/trafficpolicy-apiversion.md" >}}
   kind: {{< reuse "docs/snippets/trafficpolicy.md" >}}
   metadata:
     name: fault-rate-limit
     namespace: httpbin
   spec:
     targetRefs:
     - group: gateway.networking.k8s.io
       kind: HTTPRoute
       name: httpbin
     faultInjection:
       responseRateLimit:
         kbitsPerSecond: 1
         percentage: 100
   EOF
   ```

   | Field | Description |
   |-------|-------------|
   | `faultInjection.responseRateLimit.kbitsPerSecond` | The maximum response rate in kilobits per second. Must be at least 1. |
   | `faultInjection.responseRateLimit.percentage` | The percentage of requests to apply the rate limit to (0-100). Defaults to 100 if not set. |

2. Send a request that returns a large response body. Verify that the response is noticeably slower.
   {{< tabs items="Cloud Provider LoadBalancer,Port-forward for local testing" tabTotal="2" >}}
   {{% tab tabName="Cloud Provider LoadBalancer" %}}
   ```sh
   curl http://$INGRESS_GW_ADDRESS:8080/bytes/10000 -H "host: www.example.com:8080" -w "\nTotal time: %{time_total}s\n" -o /dev/null -s
   ```
   {{% /tab %}}
   {{% tab tabName="Port-forward for local testing" %}}
   ```sh
   curl localhost:8080/bytes/10000 -H "host: www.example.com" -w "\nTotal time: %{time_total}s\n" -o /dev/null -s
   ```
   {{% /tab %}}
   {{< /tabs >}}

   With a 1 kbit/s rate limit, a 10 KB response takes approximately 80 seconds.

3. When you are done, remove the {{< reuse "docs/snippets/trafficpolicy.md" >}}.
   ```sh
   kubectl delete trafficpolicy fault-rate-limit -n httpbin
   ```

## Abort with gRPC status code {#grpc-abort}

Instead of an HTTP status code, you can abort requests with a gRPC status code. This is useful when the upstream service is a gRPC service.

1. Create a {{< reuse "docs/snippets/trafficpolicy.md" >}} that aborts 100% of requests with gRPC status code 14 (UNAVAILABLE).
   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: {{< reuse "docs/snippets/trafficpolicy-apiversion.md" >}}
   kind: {{< reuse "docs/snippets/trafficpolicy.md" >}}
   metadata:
     name: fault-grpc-abort
     namespace: httpbin
   spec:
     targetRefs:
     - group: gateway.networking.k8s.io
       kind: HTTPRoute
       name: httpbin
     faultInjection:
       abort:
         grpcStatus: 14
         percentage: 100
   EOF
   ```

   | Field | Description |
   |-------|-------------|
   | `faultInjection.abort.grpcStatus` | The gRPC status code to return for aborted requests. Must be between 0-16. Only one of `httpStatus` or `grpcStatus` can be set. |

2. When you are done, remove the {{< reuse "docs/snippets/trafficpolicy.md" >}}.
   ```sh
   kubectl delete trafficpolicy fault-grpc-abort -n httpbin
   ```

## Combined delay and abort {#combined}

You can combine delay and abort faults in a single {{< reuse "docs/snippets/trafficpolicy.md" >}}. When both are set, the delay is applied first, then the request is aborted. You can also set `maxActiveFaults` to limit the number of concurrent active faults.

1. Create a {{< reuse "docs/snippets/trafficpolicy.md" >}} that delays 50% of requests by 100 milliseconds and aborts 25% of requests with a 503 HTTP status code, with a maximum of 5 concurrent active faults.
   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: {{< reuse "docs/snippets/trafficpolicy-apiversion.md" >}}
   kind: {{< reuse "docs/snippets/trafficpolicy.md" >}}
   metadata:
     name: fault-combined
     namespace: httpbin
   spec:
     targetRefs:
     - group: gateway.networking.k8s.io
       kind: HTTPRoute
       name: httpbin
     faultInjection:
       delay:
         fixedDelay: "100ms"
         percentage: 50
       abort:
         httpStatus: 503
         percentage: 25
       maxActiveFaults: 5
   EOF
   ```

   | Field | Description |
   |-------|-------------|
   | `faultInjection.delay` | The delay to inject. Applied before the abort. |
   | `faultInjection.abort` | The abort to inject. Applied after the delay. |
   | `faultInjection.maxActiveFaults` | The maximum number of concurrent active faults. Once reached, new requests pass through without faults. |

2. Send a few requests to the httpbin app. Depending on the configured percentages, requests are either delayed only, delayed and aborted, aborted only, or passed through normally.
   {{< tabs items="Cloud Provider LoadBalancer,Port-forward for local testing" tabTotal="2" >}}
   {{% tab tabName="Cloud Provider LoadBalancer" %}}
   ```sh
   curl -i http://$INGRESS_GW_ADDRESS:8080/status/200 -H "host: www.example.com:8080" -w "\nTotal time: %{time_total}s\n"
   ```
   {{% /tab %}}
   {{% tab tabName="Port-forward for local testing" %}}
   ```sh
   curl -i localhost:8080/status/200 -H "host: www.example.com" -w "\nTotal time: %{time_total}s\n"
   ```
   {{% /tab %}}
   {{< /tabs >}}

3. When you are done, remove the {{< reuse "docs/snippets/trafficpolicy.md" >}}.
   ```sh
   kubectl delete trafficpolicy fault-combined -n httpbin
   ```

## Disable override {#disable}

If you have a gateway-level fault injection policy, you can opt specific routes out by applying a route-level {{< reuse "docs/snippets/trafficpolicy.md" >}} with `faultInjection.disable`.

1. Create a gateway-level {{< reuse "docs/snippets/trafficpolicy.md" >}} that aborts all requests with a 503 HTTP status code.
   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: {{< reuse "docs/snippets/trafficpolicy-apiversion.md" >}}
   kind: {{< reuse "docs/snippets/trafficpolicy.md" >}}
   metadata:
     name: fault-abort-gateway
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

2. Create a route-level {{< reuse "docs/snippets/trafficpolicy.md" >}} that disables fault injection for the httpbin route.
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
       name: httpbin
     faultInjection:
       disable: {}
   EOF
   ```

3. Send a request to the httpbin app. Verify that the request succeeds with a 200 HTTP response code, even though the gateway-level policy aborts all requests.
   {{< tabs items="Cloud Provider LoadBalancer,Port-forward for local testing" tabTotal="2" >}}
   {{% tab tabName="Cloud Provider LoadBalancer" %}}
   ```sh
   curl -i http://$INGRESS_GW_ADDRESS:8080/status/200 -H "host: www.example.com:8080"
   ```
   {{% /tab %}}
   {{% tab tabName="Port-forward for local testing" %}}
   ```sh
   curl -i localhost:8080/status/200 -H "host: www.example.com"
   ```
   {{% /tab %}}
   {{< /tabs >}}

   Example output:
   ```
   HTTP/1.1 200 OK
   access-control-allow-credentials: true
   access-control-allow-origin: *
   date: Tue, 23 Apr 2024 17:12:13 GMT
   x-envoy-upstream-service-time: 0
   server: envoy
   transfer-encoding: chunked
   ```

4. When you are done, remove the resources that you created.
   ```sh
   kubectl delete trafficpolicy fault-abort-gateway -n {{< reuse "docs/snippets/namespace.md" >}}
   kubectl delete trafficpolicy fault-disable -n httpbin
   ```

## Cleanup

{{< reuse "docs/snippets/cleanup.md" >}}

Remove the {{< reuse "docs/snippets/trafficpolicy.md" >}} resources if you haven't already.

```sh
kubectl delete trafficpolicy -n httpbin --all
kubectl delete trafficpolicy -n {{< reuse "docs/snippets/namespace.md" >}} --all
```
