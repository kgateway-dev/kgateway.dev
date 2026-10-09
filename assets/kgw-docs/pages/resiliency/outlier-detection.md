Configure passive health checks and remove unhealthy hosts from the load balancing pool with an outlier detection policy. 

## About outlier detection

Outlier detection is an important part of building resilient apps. An outlier detection policy sets up several conditions, such as retries and ejection percentages, that {{< reuse "kgw-docs/snippets/kgateway.md" >}} uses to determine if a service is unhealthy. In case an unhealthy service is detected, the outlier detection policy defines how the service is removed from the pool of healthy destinations to send traffic to. Your apps then have time to recover before they are added back to the load-balancing pool and checked again for consecutive errors.

## Before you begin

{{< reuse "kgw-docs/snippets/prereq.md" >}}

## Set up outlier detection

1. Scale the httpbin app to 2 replicas. 
   ```sh
   kubectl scale deploy/httpbin -n httpbin --replicas=2
   ```

2. Verify that you see two replicas of the httpbin app. 
   ```sh
   kubectl get pods -n httpbin
   ```
   
   Example output: 
   ```console
   NAME                                   READY   STATUS    RESTARTS   AGE
   httpbin-577649ddb-lsgp8                2/2     Running   0          31d
   httpbin-577649ddb-q9b92                2/2     Running   0          3s
   ```

3. Send a few requests to the httpbin app. Because both httpbin replicas are exposed under the same service, requests are automatically load balanced between all healthy replicas. 
   {{< tabs >}}
   {{% tab name="Cloud Provider Load Balancer" %}}
   ```sh
   for i in {1..5}; do curl -vi http://$INGRESS_GW_ADDRESS:8080/status/200 -H "host: www.example.com:8080" ; done
   ```
   {{% /tab %}}
   {{% tab name="Port forward for local testing" %}}
   ```sh
   for i in {1..5}; do curl -vi localhost:8080/status/200 -H "host: www.example.com:8080"; done
   ```
   {{% /tab %}}
   {{< /tabs >}}
   
   Example output for one request: 
   ```console
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
   < 
   ....
   ```

4. Review the logs for both replicas. Verify that you see log entries for the 5 requests spread across both replicas. For example, one replica might have 2 log entries and the other one 3. 
   ```sh
   kubectl logs -l app=httpbin -n httpbin -f --prefix
   ``` 
   
   Example output for one request: 
   ```console
   time="2025-09-15T21:11:52.8514" status=200 method="GET" uri="/status/200" 
   size_bytes=0 duration_ms=0.03 user_agent="curl/8.7.1" client_ip=10.X.X.XX
   ```

5. Create a BackendConfigPolicy with your outlier detection policy. The following example ejects an unhealthy upstream host for one hour if the host returns one 5XX HTTP response code. Note that the maximum number of ejected hosts is set to 80%. Because of that, only one replica of httpbin can be ejected at any given time. If two replicas were ejected, that would exceed the 80% maximum threshold (because the two replicas equal 100%).
   ```yaml
   kubectl apply -f- <<EOF
   kind: BackendConfigPolicy
   apiVersion: gateway.kgateway.dev/v1alpha1
   metadata:
     name: httpbin-policy
     namespace: httpbin
   spec:
     targetRefs:
       - name: httpbin
         group: ""
         kind: Service
     outlierDetection:
       interval: 2s
       consecutive5xx: 1
       baseEjectionTime: 1h
       maxEjectionPercent: 80
   EOF
   ```
   
   | Setting | Description | 
   | -- | -- | 
   | `interval`| The time interval after which the hosts are evaluated to determine if they are healthy or not. In this example, the hosts are evaluated every 2 seconds. If not set, this field defaults to `10s`.   | 
   | `consecutive5xx` | The number of consecutive server-side error responses, such as 5XX HTTP response codes for HTTP traffic and connection failures for TCP traffic, before a host is ejected from the load balancing pool. In this example, you remove the host when one 5XX HTTP response code is returned. If not set, ejection occurs after 5 consecutive errors by default. If this field is set to 0, passive health checks are disabled. | 
   | `baseEjectionTime` | The duration that a host is removed from the load balancing pool before a new evaluation starts. If not set, this field defaults to `30s`.  |  
   | `maxEjectionPercent` | The maximum percent of hosts that can be ejected from the load balancing pool. In this example, 80% of all hosts can be ejected at a given time. If not set, this field defaults to `10` percent.  |

   
6. Repeat the requests to the httpbin app. In the log output for both httpbin replicas, verify that all requests are still spread across both httpbin instances. 
   {{< tabs >}}
   {{% tab name="Cloud Provider Load Balancer" %}}
   ```sh
   for i in {1..5}; do curl -vi http://$INGRESS_GW_ADDRESS:8080/status/200 -H "host: www.example.com:8080" ; done
   ```
   {{% /tab %}}
   {{% tab name="Port forward for local testing" %}}
   ```sh
   for i in {1..5}; do curl -vi localhost:8080/status/200 -H "host: www.example.com:8080"; done
   ```
   {{% /tab %}}
   {{< /tabs >}}

7. Force one httpbin replica to return a 503 HTTP response code. This response code triggers the outlier detection policy and automatically removes this httpbin replica from the load balancing pool for 1 hour. 
   {{< tabs >}}
   {{% tab name="Cloud Provider Load Balancer" %}}
   ```sh
   curl -vik http://$INGRESS_GW_ADDRESS:8080/status/503 -H "host: www.example.com:8080"
   ```
   {{% /tab %}}
   {{% tab name="Port forward for local testing" %}}
   ```sh
   curl -vi localhost:8080/status/503 -H "host: www.example.com:8080"
   ```
   {{% /tab %}}
   {{< /tabs >}}
   
   Example output: 
   ```console
   * Request completely sent off
   < HTTP/1.1 503 Service Unavailable
   HTTP/1.1 503 Service Unavailable
   < access-control-allow-credentials: true
   access-control-allow-credentials: true
   < access-control-allow-origin: *
   ...
   ```

8. Send a few more requests to the httpbin app. In the logs for both replicas, verify that all requests now only go to the instance that is still considered healthy. 
   {{< tabs >}}
   {{% tab name="Cloud Provider Load Balancer" %}}
   ```sh
   for i in {1..5}; do curl http://$INGRESS_GW_ADDRESS:8080/status/200 -H "host: www.example.com:8080" ; done
   ```
   {{% /tab %}}
   {{% tab name="Port forward for local testing" %}}
   ```sh
   for i in {1..5}; do curl -vi localhost:8080/status/200 -H "host: www.example.com:8080"; done
   ```
   {{% /tab %}}
   {{< /tabs >}}
   
   Example log output of the healthy instance: 
   ```console
   time="2025-09-15T21:19:02.0808" status=200 method="GET" uri="/status/200" size_bytes=0 duration_ms=0.03 user_agent="curl/8.7.1" client_ip=10.X.X.XX
   time="2025-09-15T21:19:02.2452" status=200 method="GET" uri="/status/200" size_bytes=0 duration_ms=0.03 user_agent="curl/8.7.1" client_ip=10.X.X.XX
   time="2025-09-15T21:19:02.4053" status=200 method="GET" uri="/status/200" size_bytes=0 duration_ms=0.04 user_agent="curl/8.7.1" client_ip=10.X.X.XX
   time="2025-09-15T21:19:02.6067" status=200 method="GET" uri="/status/200" size_bytes=0 duration_ms=0.01 user_agent="curl/8.7.1" client_ip=10.X.X.XX
   time="2025-09-15T21:19:02.7604" status=200 method="GET" uri="/status/200" size_bytes=0 duration_ms=0.01 user_agent="curl/8.7.1" client_ip=10.X.X.XX
   ```
   
   Example log output of the unhealthy instance: 
   ```console
   time="2025-09-15T21:17:25.4035" status=503 method="GET" uri="/status/503" size_bytes=0 duration_ms=0.04 user_agent="curl/8.7.1" client_ip=10.X.X.XX
   ```

9. Force the second httpbin replica to return a 503 HTTP response code. Note that the outlier detection only allows 80% of all upstream hosts to be ejected at a given time. Since both replicas would equal 100%, the outlier detection does not remove the host from the load balancing pool. The instance is still considered healthy and can receive requests. In your log output for the healthy instance, verify that you see the log entry for the 503 request. 
   {{< tabs >}}
   {{% tab name="Cloud Provider Load Balancer" %}}
   ```sh
   curl -vik http://$INGRESS_GW_ADDRESS:8080/status/503 -H "host: www.example.com:8080"
   ```
   {{% /tab %}}
   {{% tab name="Port forward for local testing" %}}
   ```sh
   curl -vi localhost:8080/status/503 -H "host: www.example.com:8080"
   ```
   {{% /tab %}}
   {{< /tabs >}}
   
   Example log output of the healthy instance: 
   ```console
   time="2025-09-15T21:20:27.1117" status=503 method="GET" uri="/status/503" size_bytes=0 duration_ms=0.02 user_agent="curl/8.7.1" client_ip=10.X.X.XX
   ```

10. Send a few more requests to the httpbin app. In the logs for both replicas, verify that all requests are still routed to the same instance as the instance was not removed from the load balancing pool.  
   {{< tabs >}}
   {{% tab name="Cloud Provider Load Balancer" %}}
   ```sh
   for i in {1..5}; do curl http://$INGRESS_GW_ADDRESS:8080/status/200 -H "host: www.example.com:8080" ; done
   ```
   {{% /tab %}}
   {{% tab name="Port forward for local testing" %}} 
   ```sh
   for i in {1..5}; do curl -vi localhost:8080/status/200 -H "host: www.example.com:8080"; done
   ```
   {{% /tab %}}
   {{< /tabs >}}
   
    Example log output for the healthy instance: 
    ```console
    # Previous log output
    time="2025-09-15T21:20:27.1117" status=503 method="GET" uri="/status/503" size_bytes=0 duration_ms=0.02 user_agent="curl/8.7.1" client_ip=10.0.9.76
    # New log output
    time="2025-09-15T21:25:11.4236" status=200 method="GET" uri="/status/200" size_bytes=0 duration_ms=0.02 user_agent="curl/8.7.1" client_ip=10.0.15.215
    time="2025-09-15T21:25:11.5833" status=200 method="GET" uri="/status/200" size_bytes=0 duration_ms=0.03 user_agent="curl/8.7.1" client_ip=10.0.9.76
    time="2025-09-15T21:25:11.7473" status=200 method="GET" uri="/status/200" size_bytes=0 duration_ms=0.03 user_agent="curl/8.7.1" client_ip=10.0.9.76
    time="2025-09-15T21:25:11.9098" status=200 method="GET" uri="/status/200" size_bytes=0 duration_ms=0.01 user_agent="curl/8.7.1" client_ip=10.0.15.215
    time="2025-09-15T21:25:12.0824" status=200 method="GET" uri="/status/200" size_bytes=0 duration_ms=0.01 user_agent="curl/8.7.1" client_ip=10.0.9.76

11. Port-forward the Gateway pod on port 19000. 
    ```sh
    kubectl port-forward deploy/http -n {{< reuse "kgw-docs/snippets/namespace.md" >}} 19000
    ```

12. Open the [stats Prometheus](http://localhost:19000/stats/prometheus) endpoint and look for the following metrics. 
    * `envoy_cluster_outlier_detection_ejections_consecutive_5xx`: The number of times a host qualified for ejection. In this example, the number is 2, because both hosts qualified for ejection. 
    * `envoy_cluster_outlier_detection_ejections_enforced_consecutive_5xx`: The number of times an ejection was forced. In this example, the number is 1, because the second host instance could not be ejected as it did not meet the maximum percentage setting in your outlier policy. 
    
    Example output: 
    ```console
    envoy_cluster_outlier_detection_ejections_consecutive_5xx{envoy_cluster_name="kube_httpbin_httpbin_8000"} 2
    envoy_cluster_outlier_detection_ejections_enforced_consecutive_5xx{envoy_cluster_name="kube_httpbin_httpbin_8000"} 1
    ```


{{< version exclude-if="2.4.x,2.3.x,2.2.x,2.1.x" >}}
## Separate local-origin failures from 5xx responses {#local-origin-outlier-detection}

By default, outlier detection counts 5xx responses from the upstream and connection failures toward the same threshold. This behavior is a problem when your upstream returns 5xx responses during normal operation. For example, a gRPC service can return a status such as `UNAVAILABLE`, which outlier detection treats as an HTTP 503 error.

A local-origin failure is a request for which the upstream never sends a response, such as a refused connection, a connection reset, or a timeout. An external 5xx response is a failure that the upstream itself reports. With the default settings, outlier detection counts both toward the `consecutive5xx` threshold. You can instruct the gateway proxy to count these types of failures separately, and eject a host only for local-origin failures. 

1. Update the BackendConfigPolicy to count local-origin failures separately from external 5xx responses. The following policy ejects a host for 1 hour after 10 consecutive local-origin failures. A host is never ejected for 5xx responses from the upstream. Only 80% of all hosts can be ejected at the same time. 
   ```yaml
   kubectl apply -f- <<EOF
   kind: BackendConfigPolicy
   apiVersion: gateway.kgateway.dev/v1alpha1
   metadata:
     name: httpbin-policy
     namespace: httpbin
   spec:
     targetRefs:
       - name: httpbin
         group: ""
         kind: Service
     outlierDetection:
       interval: 2s
       baseEjectionTime: 1h
       maxEjectionPercent: 80
       consecutive5xx: 1
       enforcingConsecutive5xx: 0
       splitExternalLocalOriginErrors: true
       consecutiveLocalOriginFailure: 10
       enforcingConsecutiveLocalOriginFailure: 100
   EOF
   ```

   | Setting | Description |
   | -- | -- |
   | `interval`, `baseEjectionTime`, `maxEjectionPercent` | The same settings as in the previous section. |
   | `consecutive5xx` | The number of consecutive 5xx responses from the upstream before a host qualifies for ejection. In this example, one 5xx response is enough to qualify for ejection. Ejection is only enforced if `enforcingConsecutive5xx` is set to a value greater than 0.  |
   | `enforcingConsecutive5xx` | The percentage chance that a host is ejected after it reaches the `consecutive5xx` threshold. In this example, the value is `0`, so 5xx responses from the upstream never eject a host. If omitted, the field defaults to `100`. The value must be between `0` and `100`. |
   | `splitExternalLocalOriginErrors` | Counts local-origin failures separately from errors that the upstream sends. If omitted, the field defaults to `false`, and the settings for local-origin failures have no effect. |
   | `consecutiveLocalOriginFailure` | The number of consecutive local-origin failures before a host is ejected. In this example, a host is ejected after 10 failures. This field takes effect only when `splitExternalLocalOriginErrors` is `true`. If omitted, the field defaults to `5`. If the value is `0`, ejection for local-origin failures is disabled. |
   | `enforcingConsecutiveLocalOriginFailure` | The percentage chance that a host is ejected after it reaches the `consecutiveLocalOriginFailure` threshold. This field takes effect only when `splitExternalLocalOriginErrors` is `true`. If omitted, the field defaults to `100`. The value must be between `0` and `100`. |

2. Verify that the policy is accepted and attached.
   ```sh
   kubectl get backendconfigpolicy httpbin-policy -n httpbin -o jsonpath='{.status.ancestors[0].conditions[*].message}'
   ```

   Example output:
   ```console
   Policy accepted Attached to all targets
   ```

3. Force a 503 HTTP response code from the httpbin app. This response comes from the upstream, so it does not eject the host. Both httpbin replicas serve the 503 requests. 
   {{< tabs >}}
   {{% tab name="Cloud Provider Load Balancer" %}}
   ```sh
   for i in {1..3}; do curl -vik http://$INGRESS_GW_ADDRESS:8080/status/503 -H "host: www.example.com:8080"; done
   ```
   {{% /tab %}}
   {{% tab name="Port forward for local testing" %}}
   ```sh
   for i in {1..3}; do curl -vi localhost:8080/status/503 -H "host: www.example.com:8080"; done
   ```
   {{% /tab %}}
   {{< /tabs >}}

4. Send a few more requests to the httpbin app along the `/status/200` path. In the logs for both replicas, verify that requests are still spread across both instances.
   {{< tabs >}}
   {{% tab name="Cloud Provider Load Balancer" %}}
   ```sh
   for i in {1..10}; do curl http://$INGRESS_GW_ADDRESS:8080/status/200 -H "host: www.example.com:8080" ; done
   ```
   {{% /tab %}}
   {{% tab name="Port forward for local testing" %}}
   ```sh
   for i in {1..10}; do curl -vi localhost:8080/status/200 -H "host: www.example.com:8080"; done
   ```
   {{% /tab %}}
   {{< /tabs >}}

   ```sh
   kubectl logs -l app=httpbin -n httpbin --prefix
   ```

5. Create an HTTPRoute that sends requests on the `/refused` path to port 9000 of the httpbin service. The httpbin app does not listen on this port, so the gateway proxy cannot connect and records a local-origin failure.
   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.networking.k8s.io/v1
   kind: HTTPRoute
   metadata:
     name: httpbin-refused
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
               value: /refused
         backendRefs:
           - name: httpbin
             port: 9000
   EOF
   ```

6. Send enough requests to the `/refused` path for each replica to reach the threshold of 10 consecutive failures. Every request returns a 503 HTTP response code. The gateway proxy generates this response itself because it cannot connect to the upstream, so the failure counts as a local-origin failure and not as a 5xx response from the upstream.
   {{< tabs >}}
   {{% tab name="Cloud Provider Load Balancer" %}}
   ```sh
   for i in {1..30}; do curl -s -o /dev/null -w "%{http_code}\n" http://$INGRESS_GW_ADDRESS:8080/refused -H "host: www.example.com:8080"; done
   ```
   {{% /tab %}}
   {{% tab name="Port forward for local testing" %}}
   ```sh
   for i in {1..30}; do curl -s -o /dev/null -w "%{http_code}\n" localhost:8080/refused -H "host: www.example.com:8080"; done
   ```
   {{% /tab %}}
   {{< /tabs >}}

7. Port-forward the Gateway pod on port 19000.
   ```sh
   kubectl port-forward deploy/http -n {{< reuse "kgw-docs/snippets/namespace.md" >}} 19000
   ```

8. Open the [stats Prometheus](http://localhost:19000/stats/prometheus) endpoint and look for the following metrics.
   * `envoy_cluster_outlier_detection_ejections_enforced_consecutive_5xx`: The number of ejections for 5xx responses from the upstream. In this example, the number for the `kube_httpbin_httpbin_8000` cluster is 1 from the ejection in the previous section. The number does not increase after the 503 responses in step 3, because `enforcingConsecutive5xx` is `0`.
   * `envoy_cluster_outlier_detection_ejections_enforced_consecutive_local_origin_failure`: The number of ejections for local-origin failures. In this example, the number is 1 for the `kube_httpbin_httpbin_9000` cluster, because one replica reached the failure threshold and was ejected.
   * `envoy_cluster_outlier_detection_ejections_overflow`: The number of times the maximum ejection percentage prevented an ejection. In this example, the number is greater than 0 because the second replica also reached the threshold, but ejecting it would exceed the `maxEjectionPercent` of 80%.

   Example output:
   ```console
   envoy_cluster_outlier_detection_ejections_enforced_consecutive_5xx{envoy_cluster_name="kube_httpbin_httpbin_8000"} 1
   envoy_cluster_outlier_detection_ejections_enforced_consecutive_local_origin_failure{envoy_cluster_name="kube_httpbin_httpbin_9000"} 1
   envoy_cluster_outlier_detection_ejections_overflow{envoy_cluster_name="kube_httpbin_httpbin_9000"} 2
   ```
{{< /version >}}

## Cleanup

1. Scale down the httpbin app to 1 replica. 
   ```sh
   kubectl scale deploy/httpbin -n httpbin --replicas=1
   ```

2. Remove the BackendConfigPolicy. 
   ```sh
   kubectl delete backendconfigpolicy httpbin-policy -n httpbin
   ```

{{< version exclude-if="2.4.x,2.3.x,2.2.x,2.1.x" >}}
3. Remove the HTTPRoute for the `/refused` path that you created in the local-origin section.
   ```sh
   kubectl delete httproute httpbin-refused -n httpbin
   ```
{{< /version >}}
