Automatically monitor the status of backends by configuring health checks.

Health checks periodically and automatically assess the readiness of the Backend to receive requests. You can configure several settings, such as health thresholds and check intervals, that {{< reuse "/kgw-docs/snippets/kgateway.md" >}} uses to determine whether a service is marked as healthy or unhealthy. For more information, see the Envoy [health checking](https://www.envoyproxy.io/docs/envoy/latest/intro/arch_overview/upstream/health_checking#arch-overview-health-checking) documentation.

## Before you begin

{{< reuse "kgw-docs/snippets/prereq.md" >}}
 
## Configure a health check for a Backend {#backend}

In the `healthCheck` section of a BackendConfigPolicy resource, specify settings for how you want the health check to perform for a Backend or Kubernetes service. The following example configures a simple set of HTTP health check settings for a service to get you started.

```yaml
apiVersion: gateway.kgateway.dev/v1alpha1
kind: BackendConfigPolicy
metadata:
  name: healthcheck-policy
  namespace: {{< reuse "/kgw-docs/snippets/namespace.md" >}}
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

{{< reuse "/kgw-docs/snippets/review-table.md" >}}

| Setting | Description |
| ------- | ----------- |
| `healthyThreshold` | The number of successful health checks required before a Backend is marked as healthy. Note that during startup, only a single successful health check is required to mark a Backend healthy. |
| `http` | Configuration for an HTTP health check. |
| `http.host` | The host header in the HTTP health check request. If unset, defaults to the name of the Backend that this health check is associated with. |
| `http.path` | The path on your app that you want {{< reuse "/kgw-docs/snippets/kgateway.md" >}} to send the health check request to. |
| `http.method` | The HTTP method for the health check to use. If unset, defaults to GET. |
| `interval` | The amount of time between sending health checks to the Backend. You can increase this value to ensure that you don't overload your Backend service. |
| `timeout` | The time to wait for a health check response. If the timeout is reached, the health check is considered unsuccessful. |
| `unhealthyThreshold` | The number of unsuccessful health checks required before a Backend is marked unhealthy. Note that for HTTP health checking, if a Backend responds with `503 Service Unavailable`, this threshold is ignored and the Backend is immediately considered unhealthy. |
| `grpc` | Optional configuration for a gRPC health check. The example omits this field because the Backend is not a gRPC service. |
| `grpc.authority` | The authority header in the gRPC health check request. If unset, defaults to the name of the Backend that this health check is associated with. |
| `grpc.serviceName` | Optional: Name of the gRPC service to check. The example omits this field because the Backend is not a gRPC service. |

## Verify the health check configuration {#verify}

To verify an active health check, use an app that has several endpoints, of which only some fail. In the following example, a single Kubernetes service selects the pods of two Deployments. One Deployment runs 1 replica that always returns an `HTTP 503` response. The other Deployment runs 2 replicas that always succeed. The service therefore has three endpoints, and two of them (about 67%) are always healthy. This share is above the default panic threshold of 50%, so the health check can take effect.

> [!NOTE]
> If most of the endpoints of a Backend fail their health checks, requests can still reach the failing endpoints. When the share of healthy endpoints drops below the panic threshold, which is 50% by default, Envoy enters panic mode. In panic mode, Envoy ignores the health status and sends requests to all endpoints. For example, an active health check does not stop requests to an app that has only one endpoint, even if that endpoint is marked as unhealthy. To change the panic threshold, see [Configure the panic threshold](#panic-threshold). For more information, see the Envoy [panic threshold](https://www.envoyproxy.io/docs/envoy/latest/intro/arch_overview/upstream/load_balancing/panic_threshold) documentation.

1. Deploy the sample app. The app uses the [fake-service](https://github.com/nicholasjackson/fake-service) image, which you can configure to return errors. The `health-check-demo-failing` Deployment has 1 replica and an error rate of `1`, so all requests to its pod fail with a `503` response. The `health-check-demo-ok` Deployment has 2 replicas and no errors.
   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: v1
   kind: Service
   metadata:
     name: health-check-demo
     namespace: httpbin
   spec:
     selector:
       app: health-check-demo
     ports:
     - name: http
       port: 8000
       targetPort: 8000
   ---
   apiVersion: apps/v1
   kind: Deployment
   metadata:
     name: health-check-demo-failing
     namespace: httpbin
   spec:
     replicas: 1 # One pod that always fails
     selector:
       matchLabels:
         app: health-check-demo
         variant: failing
     template:
       metadata:
         labels:
           app: health-check-demo
           variant: failing
       spec:
         containers:
         - name: app
           image: nicholasjackson/fake-service:v0.20.0
           ports:
           - containerPort: 8000
           env:
           - name: LISTEN_ADDR
             value: "0.0.0.0:8000"
           - name: NAME
             value: failing
           - name: ERROR_RATE
             value: "1"
           - name: ERROR_CODE
             value: "503"
   ---
   apiVersion: apps/v1
   kind: Deployment
   metadata:
     name: health-check-demo-ok
     namespace: httpbin
   spec:
     replicas: 2 # Two pods that always succeed
     selector:
       matchLabels:
         app: health-check-demo
         variant: ok
     template:
       metadata:
         labels:
           app: health-check-demo
           variant: ok
       spec:
         containers:
         - name: app
           image: nicholasjackson/fake-service:v0.20.0
           ports:
           - containerPort: 8000
           env:
           - name: LISTEN_ADDR
             value: "0.0.0.0:8000"
           - name: NAME
             value: ok
   EOF
   ```

2. Create an HTTPRoute that routes requests for the `healthcheck.example` domain to the sample app.
   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.networking.k8s.io/v1
   kind: HTTPRoute
   metadata:
     name: health-check-demo
     namespace: httpbin
   spec:
     parentRefs:
     - name: http
       namespace: {{< reuse "/kgw-docs/snippets/namespace.md" >}}
     hostnames:
     - healthcheck.example
     rules:
     - backendRefs:
       - name: health-check-demo
         port: 8000
   EOF
   ```

3. Send 30 requests to the sample app and count the HTTP response codes. Because no health check is configured yet, about one third of the requests reach the failing pod and return a `503` response.
   {{< tabs >}}
   {{% tab name="Cloud Provider LoadBalancer" %}}
   ```sh
   for i in $(seq 1 30); do curl -s -o /dev/null -w "%{http_code}\n" http://$INGRESS_GW_ADDRESS:8080/ -H "host: healthcheck.example"; done | sort | uniq -c
   ```
   {{% /tab %}}
   {{% tab name="Port-forward for local testing" %}}
   ```sh
   for i in $(seq 1 30); do curl -s -o /dev/null -w "%{http_code}\n" localhost:8080/ -H "host: healthcheck.example"; done | sort | uniq -c
   ```
   {{% /tab %}}
   {{< /tabs >}}

   Example output:
   ```console
     20 200
     10 503
   ```

4. Create a BackendConfigPolicy resource that configures an active health check on the root path of the sample app. The failing pod returns a `503` response on this path.
   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.kgateway.dev/v1alpha1
   kind: BackendConfigPolicy
   metadata:
     name: health-check-demo
     namespace: httpbin
   spec:
     targetRefs:
       - name: health-check-demo
         group: ""
         kind: Service
     healthCheck:
       healthyThreshold: 1
       http:
         path: /
       interval: 2s
       timeout: 1s
       unhealthyThreshold: 1
   EOF
   ```

5. Check the endpoints in the Envoy service directory. The following command port-forwards the `http` gateway deployment on port 19000, waits for the health check to run, gets the health status of the endpoints of the sample app, and stops the port-forwarding. Only the pod of the failing Deployment is marked with `/failed_active_hc`.
   ```sh
   kubectl port-forward deploy/http -n {{< reuse "/kgw-docs/snippets/namespace.md" >}} 19000 &
   sleep 5
   curl -s 127.0.0.1:19000/clusters | grep health-check-demo | grep health_flags
   lsof -ti:19000 | xargs kill -9
   ```

   Example output:
   ```console
   kube_httpbin_health-check-demo_8000::10.XX.X.XX:8000::health_flags::healthy
   kube_httpbin_health-check-demo_8000::10.XX.X.XX:8000::health_flags::/failed_active_hc
   kube_httpbin_health-check-demo_8000::10.XX.X.XX:8000::health_flags::healthy
   ```

6. Send the 30 requests again. This time, all requests succeed, because the gateway no longer sends requests to the failing pod.
   {{< tabs >}}
   {{% tab name="Cloud Provider LoadBalancer" %}}
   ```sh
   for i in $(seq 1 30); do curl -s -o /dev/null -w "%{http_code}\n" http://$INGRESS_GW_ADDRESS:8080/ -H "host: healthcheck.example"; done | sort | uniq -c
   ```
   {{% /tab %}}
   {{% tab name="Port-forward for local testing" %}}
   ```sh
   for i in $(seq 1 30); do curl -s -o /dev/null -w "%{http_code}\n" localhost:8080/ -H "host: healthcheck.example"; done | sort | uniq -c
   ```
   {{% /tab %}}
   {{< /tabs >}}

   Example output:
   ```console
     30 200
   ```

## Configure the panic threshold {#panic-threshold}

By default, Envoy enters panic mode when fewer than 50% of the endpoints of a Backend are healthy. To change this threshold, set the `loadBalancer.healthyPanicThreshold` field in the BackendConfigPolicy to a percentage between `0` and `100`. When the share of healthy endpoints drops below this percentage, Envoy enters panic mode. You must set this field together with a load balancing algorithm, such as `roundRobin`. For more information about load balancing settings, see [Simple load balancing]({{< link-hextra path="/traffic-management/session-affinity/loadbalancing/" >}}).

The following steps set the panic threshold to `0` for the sample app. This value disables panic mode, so requests are never sent to endpoints that fail their health check. If all endpoints of the Backend are unhealthy, requests to the Backend fail with a `503` response.

1. Update the BackendConfigPolicy to set the panic threshold to `0`.
   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.kgateway.dev/v1alpha1
   kind: BackendConfigPolicy
   metadata:
     name: health-check-demo
     namespace: httpbin
   spec:
     targetRefs:
       - name: health-check-demo
         group: ""
         kind: Service
     healthCheck:
       healthyThreshold: 1
       http:
         path: /
       interval: 2s
       timeout: 1s
       unhealthyThreshold: 1
     loadBalancer:
       roundRobin: {}
       healthyPanicThreshold: 0
   EOF
   ```

2. Scale the Deployment of the healthy pods down to 0, so that the only remaining endpoint is the failing pod. Wait a few seconds for the health check to mark the endpoint as unhealthy.
   ```sh
   kubectl scale deployment health-check-demo-ok -n httpbin --replicas=0
   sleep 10
   ```

3. Send a request to the sample app. The gateway does not send the request to the failing pod. Instead, the gateway proxy responds with a `503` response and the `no healthy upstream` message. With the default panic threshold, the request reaches the failing pod, and you see the error response of the app instead.
   {{< tabs >}}
   {{% tab name="Cloud Provider LoadBalancer" %}}
   ```sh
   curl -i http://$INGRESS_GW_ADDRESS:8080/ -H "host: healthcheck.example"
   ```
   {{% /tab %}}
   {{% tab name="Port-forward for local testing" %}}
   ```sh
   curl -i localhost:8080/ -H "host: healthcheck.example"
   ```
   {{% /tab %}}
   {{< /tabs >}}

   Example output:
   ```console
   HTTP/1.1 503 Service Unavailable
   ...
   no healthy upstream
   ```

4. Scale the Deployment of the healthy pods back up.
   ```sh
   kubectl scale deployment health-check-demo-ok -n httpbin --replicas=2
   ```

## Cleanup

{{< reuse "kgw-docs/snippets/cleanup.md" >}}

```sh
kubectl delete BackendConfigPolicy health-check-demo -n httpbin
kubectl delete HTTPRoute health-check-demo -n httpbin
kubectl delete Service health-check-demo -n httpbin
kubectl delete Deployment health-check-demo-failing health-check-demo-ok -n httpbin
```


