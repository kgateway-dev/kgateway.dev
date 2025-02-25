---
title: Upstream health checks
weight: 20
---

Automatically monitor the status of upstreams by configuring health checks.

## About

When you configure a {{< reuse "docs/snippets/product-name.md" >}} [Upstream](/docs/traffic-management/destination-types/upstreams/) resource, you can add both health checks and outlier detection, which are important elements of building resilient apps.

### Health checks

Health checks periodically and automatically assess the readiness of the Upstream to receive requests. You can configure several settings, such as health thresholds and check intervals, that {{< reuse "docs/snippets/product-name.md" >}} uses to determine whether a service is marked as healthy or unhealthy. For more information, see the Envoy [health checking](https://www.envoyproxy.io/docs/envoy/latest/intro/arch_overview/upstream/health_checking#arch-overview-health-checking) documentation.

In the `healthChecks` section of an Upstream resource, specify settings for how you want the health check to perform. For more information about all of the settings that you can configure, see the [reference documentation](/docs/reference/api/health_check).

| Setting | Description |
| ------- | ----------- |
| `alwaysLogHealthCheckFailures` and `eventLogPath` | Enables logging of any health check failures to a specific log path. |
| `healthyThreshold` | The number of successful health checks required before an Upstream is marked as healthy. Note that during startup, only a single successful health check is required to mark an Upstream healthy. |
| `httpHealthCheck.path` | The path on your app that you want {{< reuse "docs/snippets/product-name.md" >}} to send the health check request to. |
| `interval` | The amount of time between sending health checks to the Upstream. You can increase this value to ensure that you don't overload your Upstream service. |
| `timeout` | The time to wait for a health check response. If the timeout is reached, the health check is considered unsuccessful. |
| `unhealthyThreshold` | The number of unsuccessful health checks required before an Upstream is marked unhealthy. Note that for HTTP health checking, if an Upstream responds with `503 Service Unavailable`, this threshold is ignored and the Upstream is immediately considered unhealthy. |

### Outlier detection

Outlier detection defines how {{< reuse "docs/snippets/product-name.md" >}} removes (ejects) any unhealthy services from the pool of healthy destinations to send traffic to. Your apps then have time to recover before they are added back to the load-balancing pool and checked again for consecutive errors. For more information, see the Envoy [outlier detection](https://www.envoyproxy.io/docs/envoy/latest/intro/arch_overview/upstream/outlier) documentation.

In the `outlierDetection` section of an Upstream resource, specify settings for how you want {{< reuse "docs/snippets/product-name.md" >}} to handle Upstreams that fail healthchecks. For more information about all of the settings that you can configure, see the [reference documentation](/docs/reference/api/outlier_detection/).

| Setting | Description |
| ------- | ----------- |
| `consecutive5xx` | The number of consecutive 500-level responses that can occur before {{< reuse "docs/snippets/product-name.md" >}} ejects the Upstream and no longer serves new connections to it while it is ejected. |
| `baseEjectionTime` | The base time that an Upstream is ejected for. The real time is equal to the base time multiplied by the number of times the Upstream has been ejected. |
| `maxEjectionPercent` | The maximum percentage of an Upstream that can be ejected when the `consecutive5xx` value is met. Must be set to `100` to eject the entire Upstream in case of failing health checks.  |
| `interval` | The time interval between ejection analysis sweeps. This can result in both new ejections as well as Upstreams being returned to service. |

### Other settings

You can add the following additional settings to adjust the health check configuration.
* `ignoreHealthOnHostRemoval`: Upstreams with working health checks are not removed from Envoy's service directory, even due to configuration changes. To allow them to be removed, set `spec.ignoreHealthOnHostRemoval` to `true`.

## Before you begin

{{< reuse "docs/snippets/prereq.md" >}}
 
## Configure a health check and outlier detection for an Upstream

In an Upstream resource, add the following configuration sections to configure health checks and outlier detection. The following example configures a simple set of health check and outlier detection settings to get you started.

```yaml
apiVersion: gloo.solo.io/v1
kind: Upstream
metadata:
  name: my-upstream
  namespace: {{< reuse "docs/snippets/ns-system.md" >}}
spec:
  kube:
    ...
  healthChecks:
    - alwaysLogHealthCheckFailures: true
      eventLogPath: /dev/stdout
      healthyThreshold: 1
      httpHealthCheck:
        path: /status/200
      interval: 30s
      timeout: 10s
      unhealthyThreshold: 1
  outlierDetection:
    consecutive5xx: 3
    baseEjectionTime: 20s
    maxEjectionPercent: 100
    interval: 10s
  ignoreHealthOnHostRemoval: true
```

## Example configuration and verification

To try out an active health check and outlier detection policy, you can follow these steps to create an Upstream for the httpbin sample app and check the endpoint status in the Envoy service directory.

1. Create an Upstream resource that configures a health check on the httpbin path `/status/503`. This path always returns a `503 Service Unavailable` HTTP response code, which {{< reuse "docs/snippets/product-name.md" >}} interprets as a failing request. Additionally, the outlier detection settings allow {{< reuse "docs/snippets/product-name.md" >}} to remove the Upstream from its pool of healthy destinations that it can send traffic to.
   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gloo.solo.io/v1
   kind: Upstream
   metadata:
     name: httpbin
     namespace: httpbin
   spec:
     kube:
       serviceName: httpbin
       serviceNamespace: httpbin
       servicePort: 8000
     healthChecks:
       - httpHealthCheck:
           path: /status/503
         interval: 2s
         timeout: 1s
         unhealthyThreshold: 1
     outlierDetection:
       consecutive5xx: 3
       baseEjectionTime: 30s
       maxEjectionPercent: 100
       interval: 10s
     ignoreHealthOnHostRemoval: true
   EOF
   ```

2. Create an HTTPRoute resource that references the Upstream.
   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.networking.k8s.io/v1
   kind: HTTPRoute
   metadata:
     name: healthcheck-test
     namespace: httpbin
     labels:
       example: httpbin-route
   spec:
     hostnames:
     - www.httpbin.com
     parentRefs:
     - group: gateway.networking.k8s.io
       kind: Gateway
       name: http
       namespace: {{< reuse "docs/snippets/ns-system.md" >}}
     rules:
     - backendRefs:
       - group: gloo.solo.io
         kind: Upstream
         name: httpbin
   EOF
   ```

3. Check the endpoint in the Envoy service directory.
   1. Port-forward the `gloo-gateway-http` deployment on port 19000.
      ```shell
      kubectl port-forward deploy/http -n {{< reuse "docs/snippets/ns-system.md" >}} 19000 &
      ```
   2. Send an `HTTP GET` request to the `/clusters` endpoint.
      ```sh
      curl -X GET 127.0.0.1:19000/clusters
      ```
   3. In the output, search for `/failed_active_hc/failed_outlier_check`. For example, you might see a line such as the following. This indicates that the Upstream failed its active health check, and that the outlier policy detected the unhealthy state.
      ```
      httpbin_httpbin::10.XX.X.XX:8080::health_flags::/failed_active_hc/failed_outlier_check
      ```

4. You can also check the Envoy logs for health check failures and ejection events. 
   1. Get the logs for the `gloo-gateway-http` deployment.
      ```shell
      kubectl logs -f deploy/http -n {{< reuse "docs/snippets/ns-system.md" >}} > gateway-proxy.log
      ```
   2. In the output `gateway-proxy.log` file, search for events such as `health_check_failure_event` or `ejection` as shown in the following example log lines.
      ```json
      {"health_checker_type":"HTTP","host":{"socket_address":{"protocol":"TCP","address":"10.XX.X.XX","port_value":8080,"resolver_name":"","ipv4_compat":false}},"cluster_name":"httpbin_httpbin","timestamp":"2024-08-20T18:13:47.577Z","health_check_failure_event":{"failure_type":"ACTIVE","first_check":false},"metadata":{"filter_metadata":{"envoy.lb":{"version":"v1","app":"httpbin","pod-template-hash":"f46cc8b9b"}},"typed_filter_metadata":{}},"locality":{"region":"","zone":"","sub_zone":""}}
      {"time": "2024-08-20T18:15:47.112Z", "secs_since_last_action": "-1", "cluster": "httpbin_httpbin", "upstream_url": "0.0.0.0:0", "action": "eject", "type": "5xx", "num_ejections": "1", "enforced": "true"}
      ```

## Cleanup

{{< reuse "docs/snippets/cleanup.md" >}}

```sh
kubectl delete HTTPRoute healthcheck-test -n httpbin
kubectl delete Upstream httpbin -n httpbin
```