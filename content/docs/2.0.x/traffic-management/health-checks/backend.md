---
title: Backend health checks
weight: 20
---

Automatically monitor the status of backends by configuring health checks.

Health checks periodically and automatically assess the readiness of the Backend to receive requests. You can configure several settings, such as health thresholds and check intervals, that {{< reuse "/docs/snippets/kgateway.md" >}} uses to determine whether a service is marked as healthy or unhealthy. For more information, see the Envoy [health checking](https://www.envoyproxy.io/docs/envoy/latest/intro/arch_overview/upstream/health_checking#arch-overview-health-checking) documentation.

{{< callout >}}
{{< reuse "docs/snippets/proxy-kgateway.md" >}}
{{< /callout >}}

## Before you begin

{{< reuse "docs/snippets/prereq.md" >}}
 
## Configure a health check for a Backend {#backend}

In the `healthCheck` section of a BackendConfigPolicy resource, specify settings for how you want the health check to perform for a Backend or Kubernetes service. The following example configures a simple set of HTTP health check settings for a service to get you started.

```yaml
apiVersion: gateway.kgateway.dev/v1alpha1
kind: BackendConfigPolicy
metadata:
  name: healthcheck-policy
  namespace: {{< reuse "/docs/snippets/namespace.md" >}}
spec:
  targetRefs:
    - name: my-backend
      group: ""
      kind: Service
  healthCheck:
    healthyThreshold: 1
    http:
      path: /status/200
    interval: 30s
    timeout: 10s
    unhealthyThreshold: 1
```

{{< reuse "/docs/snippets/review-table.md" >}}

| Setting | Description |
| ------- | ----------- |
| `healthyThreshold` | The number of successful health checks required before a Backend is marked as healthy. Note that during startup, only a single successful health check is required to mark a Backend healthy. |
| `http` | Configuration for an HTTP health check. |
| `http.host` | The host header in the HTTP health check request. If unset, defaults to the name of the Backend that this health check is associated with. |
| `http.path` | The path on your app that you want {{< reuse "/docs/snippets/kgateway.md" >}} to send the health check request to. |
| `http.method` | The HTTP method for the health check to use. If unset, defaults to GET. |
| `interval` | The amount of time between sending health checks to the Backend. You can increase this value to ensure that you don't overload your Backend service. |
| `timeout` | The time to wait for a health check response. If the timeout is reached, the health check is considered unsuccessful. |
| `unhealthyThreshold` | The number of unsuccessful health checks required before a Backend is marked unhealthy. Note that for HTTP health checking, if a Backend responds with `503 Service Unavailable`, this threshold is ignored and the Backend is immediately considered unhealthy. |
| `grpc` | Optional configuration for a gRPC health check. The example omits this field because the Backend is not a gRPC service. |
| `grpc.authority` | The authority header in the gRPC health check request. If unset, defaults to the name of the Backend that this health check is associated with. |
| `grpc.serviceName` | Optional: Name of the gRPC service to check. The example omits this field because the Backend is not a gRPC service. |

## Verify the health check configuration {#verify}

To try out an active health check policy, you can follow these steps to create a BackendConfigPolicy for the httpbin sample app and check the endpoint status in the Envoy service directory.

1. Create a BackendConfigPolicy resource that configures a health check on the httpbin path `/status/503`. This path always returns a `503 Service Unavailable` HTTP response code, which {{< reuse "/docs/snippets/kgateway.md" >}} interprets as a failing request.
   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.kgateway.dev/v1alpha1
   kind: BackendConfigPolicy
   metadata:
     name: httpbin-healthcheck
     namespace: httpbin
   spec:
     targetRefs:
       - name: httpbin
         group: ""
         kind: Service
     healthCheck:
       healthyThreshold: 1
       http:
         path: /status/503
       interval: 2s
       timeout: 1s
       unhealthyThreshold: 1
   EOF
   ```

2. Check the endpoint in the Envoy service directory.
   1. Port-forward the `http` gateway deployment on port 19000.
      ```shell
      kubectl port-forward deploy/http -n {{< reuse "/docs/snippets/namespace.md" >}} 19000 &
      ```
   2. Send an `HTTP GET` request to the `/clusters` endpoint.
      ```sh
      curl -X GET 127.0.0.1:19000/clusters
      ```
   3. In the output, search for `/failed_active_hc`, which indicates that the Backend failed its active health check. For example, you might see a line such as the following.
      ```
      httpbin_httpbin::10.XX.X.XX:8080::health_flags::/failed_active_hc
      ```
   4. Stop port-forwarding the `http` deployment.
      ```sh
      lsof -ti:19000 | xargs kill -9
      ```

## Cleanup

{{< reuse "docs/snippets/cleanup.md" >}}

```sh
kubectl delete BackendConfigPolicy httpbin-healthcheck -n httpbin
```