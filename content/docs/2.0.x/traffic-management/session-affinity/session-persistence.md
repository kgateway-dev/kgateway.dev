---
title: Session persistence
weight: 30
---

Ensure that traffic from a client is always routed to the same backend instance for the duration of a session.

{{< callout type="warning" >}} 
{{< reuse "docs/versions/warn-1-3-only-experimental.md" >}}
{{< /callout >}}

## About

HTTPRoutes support `sessionPersistence`, also known as "strong" session affinity or sticky sessions. Session persistence ensures that traffic is always routed to the same backend instance for the duration of the session, which can improve request latency and the user experience.

In session persistence, a client directly provides information, such as a header or a cookie, that the gateway proxy uses as a reference to direct traffic to a specific backend server. The persistent client request bypasses the proxy's load balancing algorithm and is routed directly to the backend that it previously established a session with.

**Cookie**: When you use cookie-based persistence, a client sends a request to your app, and receives a `set-cookie` response header. The client then reuses that value in a cookie request header in subsequent requests. The gateway proxy uses this cookie to maintain a persistent connection to a single backend server on behalf of the client.

**Header**: When you use cookie-based persistence, a client sends a request to your app, and receives an HTTP response header. The client then reuses that value in the same header in subsequent HTTP requests. The gateway proxy uses this header to maintain a persistent connection to a single backend server on behalf of the client.

### Session persistence versus session affinity

In session persistence, the backend service is encoded in a cookie or header and affinity can be maintained for as long as the backend service is available. This makes session persistence more reliable than [session affinity through consistent hashing](../consistent-hashing), or "weak" session affinity, in which affinity might be lost when a backend service is added or removed, or if the gateway proxy restarts.

However, note that session persistence and session affinity can functionally work together in your {{< reuse "/docs/snippets/kgateway.md" >}} setup. If you define both session persistence and session affinity through consistent hashing, the gateway proxy makes the following routing decisions for incoming requests:
- If the request contains a session persistence identity in a cookie or header, route the request directly to the backend that it previously established a session with.
- If no session persistence identity is present, load balance the request according to the defined session affinity configuration, along with any [load balancing configuration](../loadbalancing).

For more information about session peristence, see the [Kubernetes Gateway API enhancement doc](https://gateway-api.sigs.k8s.io/geps/gep-1619/).

## Before you begin 

{{< reuse "docs/snippets/prereq-1-3-channel-experimental.md" >}}

## Configure session persistence

Define session persistence based on either a request cookie or header in the `sessionPersistence` section of an HTTPRoute. This example defines session persistence for requests to `/path-A` by using cookies, and session persistence for requests to `/path-B` by using headers.

```yaml
apiVersion: gateway.networking.k8s.io/v1
kind: HTTPRoute
metadata:
  name: example-route
  namespace: default
spec:
  parentRefs:
    - name: example-gateway
      namespace: {{< reuse "docs/snippets/namespace.md" >}}
  rules:
    - matches:
        - path:
            type: PathPrefix
            value: /path-A
      backendRefs:
        - name: backend
          port: 3000
      sessionPersistence:
        sessionName: Session-A
        type: Cookie
        absoluteTimeout: 10s
        cookieConfig:
          lifetimeType: Permanent
    - matches:
        - path:
            type: PathPrefix
            value: /path-B
      backendRefs:
        - name: backend
          port: 3000
      sessionPersistence:
        sessionName: Session-B
        type: Header
        idleTimeout: 10s
```

{{< reuse "/docs/snippets/review-table.md" >}}

| Setting | Description | 
| -- | -- | 
| `sessionName` | The name of the persistent session, which is reflected in the cookie or the header that the proxy sends in response to the client and the client reuses in subsequent requests. To prevent unpredictable behavior or rejection, do not reuse session names. |
| `type` | The request property, either `Header` or `Cookie`, to base session persistence on. Defaults to `Cookie`. |
| `idleTimeout` | The idle timeout of the persistent session. Once the session has been idle for more than the specified duration, the session becomes invalid. |
| `absoluteTimeout` | The absolute timeout of the persistent session. Once the duration has elapsed, the session becomes invalid. |
| `cookieConfig.lifetimeType` | If the `type` is `Cookie`, the `lifetimeType` determines whether the session cookie has a `Permanent` or `Session`-based lifetime. A permanent cookie persists until its specified expiry time, while a session cookie is deleted when the current session ends. When set to `Permanent`, `absoluteTimeout` indicates the cookie's lifetime as defined by either the `Expires` or `Max-Age` cookie attributes, and is required. When set to `Session`, `absoluteTimeout` indicates the absolute lifetime of the cookie that is tracked by the gateway, and is optional. **Note**: To maintain affinity even when the gateway proxy restarts, you must set this field to `Permanent`. Defaults to `Session`. |

## Verify the session persistence configuration {#verify}

To try out session persistence, you can follow these steps to define cookie-based session persistence in the HTTPRoute for the httpbin sample app.

1. Scale the httpbin app up to two instances.
   ```sh 
   kubectl scale deployment httpbin -n httpbin --replicas=2
   ```
   
2. Verify that another instance of the httpbin app is created.
   ```sh
   kubectl get pods -n httpbin
   ```
   
   Example output:
   ```
   NAME                      READY   STATUS        RESTARTS   AGE
   httpbin-8d557795f-86hzg   3/3     Running       0          54s
   httpbin-8d557795f-h8ks9   3/3     Running       0          26m
   ```

3. Modify the sample HTTPRoute resource for the httpbin app to add the following `sessionPersistence` section. These settings instruct the gateway proxy to create a persistent session cookie called `Session-A` for any new client connections to the httpbin app. Each created session has an absolute timeout of 30 minutes, and the cookie for each session is deleted only when that timeout ends.
   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.networking.k8s.io/v1
   kind: HTTPRoute
   metadata:
     name: httpbin
     namespace: httpbin
   spec:
     parentRefs:
       - name: http
         namespace: {{< reuse "docs/snippets/namespace.md" >}}
     hostnames:
       - "www.example.com"
     rules:
       - backendRefs:
           - name: httpbin
             port: 8000
         sessionPersistence:
           sessionName: Session-A
           type: Cookie
           absoluteTimeout: 30m
           cookieConfig:
             lifetimeType: Permanent
   EOF
   ```

4. Send a request to the httpbin app and verify that you see the `Session-A` cookie in the `set-cookie` header of your response. The `-c` option stores the cookie in a local file on your machine so that you can use it in subsequent requests.
   {{< tabs tabTotal="2" items="LoadBalancer IP address or hostname,Port-forward for local testing" >}}
   {{% tab tabName="LoadBalancer IP address or hostname" %}}
   ```sh
   curl -i -c cookie-jar -k http://$INGRESS_GW_ADDRESS:8080/headers \
   -H "host: www.example.com:8080"
   ```
   {{% /tab %}}
   {{% tab tabName="Port-forward for local testing" %}}
   ```sh
   curl -i -c cookie-jar -k localhost:8080/headers \
   -H "host: www.example.com:8080"
   ```
   {{% /tab %}}
   {{< /tabs >}} 
   
   Example output: 
   ```console {hl_lines=[8]}
   HTTP/1.1 200 OK
   access-control-allow-credentials: true
   access-control-allow-origin: *
   content-type: application/json; encoding=utf-8
   date: Wed, 16 Jul 2025 17:20:40 GMT
   content-length: 445
   x-envoy-upstream-service-time: 0
   set-cookie: Session-A="Cg8xMC4yNDQuMC42OjgwODA="; HttpOnly
   server: envoy
   ...
   ```

5. Repeat the request a few more times. Include the cookie that you stored in the local file by using the `-b` option. Make sure to send these requests within the 30 minute cookie validity period.
   {{< tabs tabTotal="2" items="LoadBalancer IP address or hostname,Port-forward for local testing" >}}
   {{% tab tabName="LoadBalancer IP address or hostname" %}}
   ```sh
   for i in {1..10}; do
   curl -i -b cookie-jar -k http://$INGRESS_GW_ADDRESS:8080/headers \
   -H "host: www.example.com:8080"; done
   ```
   {{% /tab %}}
   {{% tab tabName="Port-forward for local testing" %}}
   ```sh
   for i in {1..10}; do
   curl -i -b cookie-jar -k localhost:8080/headers \
   -H "host: www.example.com:8080"; done
   ```
   {{% /tab %}}
   {{< /tabs >}}

6. Check the logs of each httpbin instance. Verify that only one of the instances served all 10 of the subsequent requests that you made.
   ```sh
   kubectl logs -n httpbin <httpbin-pod>
   ```

   Example output for one pod, in which all 10 subsequent requests (timestamps at `17:20`) are served after the previous 1 request (timestamp at `17:17`):
   ```
   Defaulted container "httpbin" out of: httpbin, curl
   go-httpbin listening on http://0.0.0.0:8080
   time="2025-07-16T17:17:09.8479" status=200 method="GET" uri="/headers" size_bytes=440 duration_ms=0.10 user_agent="curl/8.7.1" client_ip=10.244.0.7
   time="2025-07-16T17:20:32.1077" status=200 method="GET" uri="/headers" size_bytes=445 duration_ms=0.04 user_agent="curl/8.7.1" client_ip=10.244.0.7
   time="2025-07-16T17:20:40.7017" status=200 method="GET" uri="/headers" size_bytes=445 duration_ms=0.05 user_agent="curl/8.7.1" client_ip=10.244.0.7
   time="2025-07-16T17:20:49.5744" status=200 method="GET" uri="/headers" size_bytes=515 duration_ms=0.04 user_agent="curl/8.7.1" client_ip=10.244.0.7
   ...
   ```

7. Optional: Verify the permanence of the session cookie by restarting the http gateway. The session cookie persists after the gateway restarts due to the `cookieConfig.lifetimeType: Permanent` setting.
   1. Restart the http gateway proxy.
      ```sh
      kubectl rollout restart deploy/http -n {{< reuse "docs/snippets/namespace.md" >}}
      ```
   2. Verify that the gateway proxy pod is running.
      ```sh
      kubectl get po -n kgateway-system -l gateway.networking.k8s.io/gateway-name=http
      ```
      Example output:
      ```
      NAME                  READY   STATUS    RESTARTS   AGE
      http-7dd94b74-k26j6   3/3     Running   0          8s
      ```
   3. Get the new external address that is assigned to the gateway, or restart local port forwarding.
      {{< tabs items="Cloud Provider LoadBalancer,Port-forward for local testing" tabTotal="2"  >}}
      {{% tab tabName="Cloud Provider LoadBalancer" %}}
   ```sh
   export INGRESS_GW_ADDRESS=$(kubectl get svc -n {{< reuse "docs/snippets/namespace.md" >}} http -o jsonpath="{.status.loadBalancer.ingress[0]['hostname','ip']}")
   echo $INGRESS_GW_ADDRESS  
   ```
      {{% /tab %}}
      {{% tab tabName="Port-forward for local testing"  %}}
   ```sh
   kubectl port-forward deployment/http -n {{< reuse "docs/snippets/namespace.md" >}} 8080:8080
   ```
      {{% /tab %}}
      {{< /tabs >}}
   4. Repeat the same request with the session cookie. Make sure to send this request within the 30 minute cookie validity period.
      {{< tabs tabTotal="2" items="LoadBalancer IP address or hostname,Port-forward for local testing" >}}
      {{% tab tabName="LoadBalancer IP address or hostname" %}}
   ```sh
   for i in {1..10}; do
   curl -i -b cookie-jar -k http://$INGRESS_GW_ADDRESS:8080/headers \
   -H "host: www.example.com:8080"; done
   ```
      {{% /tab %}}
      {{% tab tabName="Port-forward for local testing" %}}
   ```sh
   for i in {1..10}; do
   curl -i -b cookie-jar -k localhost:8080/headers \
   -H "host: www.example.com:8080"; done
   ```
      {{% /tab %}}
      {{< /tabs >}}
   5. Check the logs again of the httpbin instance that served the previous requests. Verify that your most recent request continued to be served by the same instance, even after the http gateway restarted.
      ```sh
      kubectl logs -n httpbin <httpbin-pod>
      ```

      Example output for one pod, in which all 10 new requests (timestamps at `17:24`) are served after the previous 10 requests (timestamps at `17:20`):
      ```
      ...
      time="2025-07-16T17:20:40.7017" status=200 method="GET" uri="/headers" size_bytes=445 duration_ms=0.05 user_agent="curl/8.7.1" client_ip=10.244.0.7
      time="2025-07-16T17:20:41.5744" status=200 method="GET" uri="/headers" size_bytes=515 duration_ms=0.04 user_agent="curl/8.7.1" client_ip=10.244.0.7
      time="2025-07-16T17:24:06.5744" status=200 method="GET" uri="/headers" size_bytes=515 duration_ms=0.04 user_agent="curl/8.7.1" client_ip=10.244.0.7
      time="2025-07-16T17:24:06.6013" status=200 method="GET" uri="/headers" size_bytes=515 duration_ms=0.04 user_agent="curl/8.7.1" client_ip=10.244.0.7
      time="2025-07-16T17:24:06.631" status=200 method="GET" uri="/headers" size_bytes=515 duration_ms=0.03 user_agent="curl/8.7.1" client_ip=10.244.0.7
      ...
      ```

## Cleanup

{{< reuse "docs/snippets/cleanup.md" >}}

1. Scale the httpbin app back down.
   ```sh 
   kubectl scale deployment httpbin -n httpbin --replicas=1
   ```

2. Remove the session persistence settings from the httpbin HTTPRoute.
   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.networking.k8s.io/v1
   kind: HTTPRoute
   metadata:
     name: httpbin
     namespace: httpbin
   spec:
     parentRefs:
       - name: http
         namespace: kgateway-system
     hostnames:
       - "www.example.com"
     rules:
       - backendRefs:
           - name: httpbin
             port: 8000
   EOF
   ```