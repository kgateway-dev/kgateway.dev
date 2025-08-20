---
title: Gateway health checks
weight: 10
---

Enable a health check plugin on your gateway proxy to respond with common HTTP codes.

{{< reuse "/docs/snippets/kgateway-capital.md" >}} includes an HTTP health checking plug-in that you can enable for a gateway proxy listener. This plug-in responds to health check requests directly with either a `200 OK` or `503 Service Unavailable` message, depending on the current draining state of Envoy.

{{< callout >}}
{{< reuse "docs/snippets/proxy-kgateway.md" >}}
{{< /callout >}}

## Before you begin

{{< reuse "docs/snippets/prereq.md" >}}
 
## Configure a health check on a gateway

1. Create an HTTPListenerPolicy resource to configure a health check path for the HTTP or HTTPS listener on the gateway. You can define any path, such as `/check/healthz`.
   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.kgateway.dev/v1alpha1
   kind: HTTPListenerPolicy
   metadata:
     name: healthcheck
     namespace: {{< reuse "/docs/snippets/namespace.md" >}}
   spec:
     targetRefs:
     - group: gateway.networking.k8s.io
       kind: Gateway
       name: http
     healthCheck:
       path: <path>
   EOF
   ```

2. To test the health check, drain the Envoy connections by sending an `HTTP POST` request to the `/healthcheck/fail` endpoint of the Envoy admin port.
   1. Port-forward the `http` deployment on port 19000.
      ```shell
      kubectl port-forward deploy/http -n {{< reuse "/docs/snippets/namespace.md" >}} 19000 &
      ```
   2. Send an `HTTP POST` request to the `/healthcheck/fail` endpoint. This causes Envoy connections to begin draining.
      ```sh
      curl -X POST 127.0.0.1:19000/healthcheck/fail
      ```

3. Send a request to the health check path. Because Envoy is in a draining state, the `503 Service Unavailable` message is returned.
   {{< tabs items="Cloud Provider LoadBalancer,Port-forward for local testing" tabTotal="2" >}}
   {{% tab tabName="Cloud Provider LoadBalancer" %}}
   ```sh
   curl -i $INGRESS_GW_ADDRESS:8080/<path>
   ```
   {{% /tab %}}
   {{% tab tabName="Port-forward for local testing" %}}
   ```sh
   curl -i localhost:8080/<path>
   ```
   {{% /tab %}}
   {{< /tabs >}}

   Example output:
   ```console
   HTTP/1.1 503 Service Unavailable
   x-envoy-upstream-healthchecked-cluster: http.{{< reuse "/docs/snippets/namespace.md" >}}
   x-envoy-immediate-health-check-fail: true
   date: Wed, 16 Jul 2025 16:35:12 GMT
   server: envoy
   connection: close
   content-length: 0
   ```

4. After you finish testing, resume Envoy connections by sending an `HTTP POST` request to the `/healthcheck/ok` endpoint of the Envoy admin port.
   ```sh
   curl -X POST 127.0.0.1:19000/healthcheck/ok
   ```

5. Send another request to the health check path. Because Envoy is operating normally, the `200 OK` message is returned.
   {{< tabs items="Cloud Provider LoadBalancer,Port-forward for local testing" tabTotal="2" >}}
   {{% tab tabName="Cloud Provider LoadBalancer" %}}
   ```sh
   curl -i $INGRESS_GW_ADDRESS:8080/<path>
   ```
   {{% /tab %}}
   {{% tab tabName="Port-forward for local testing" %}}
   ```sh
   curl -i localhost:8080/<path>
   ```
   {{% /tab %}}
   {{< /tabs >}}

   Example output:
   ```console
   HTTP/1.1 200 OK
   x-envoy-upstream-healthchecked-cluster: http.{{< reuse "/docs/snippets/namespace.md" >}}
   date: Wed, 16 Jul 2025 16:37:13 GMT
   server: envoy
   content-length: 0
   ```

6. Stop port-forwarding the `http` deployment.
   ```sh
   lsof -ti:19000 | xargs kill -9
   ```

## Cleanup

{{< reuse "docs/snippets/cleanup.md" >}}

```sh
kubectl delete HTTPListenerPolicy healthcheck -n {{< reuse "/docs/snippets/namespace.md" >}}
```