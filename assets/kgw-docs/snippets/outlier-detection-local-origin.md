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
