---
title: Session persistence
weight: 30
---

Ensure that traffic from a client is always routed to the same backend instance for the duration of a session.

## About

HTTPRoutes support `sessionPersistence`, also known as "strong" session affinity or sticky sessions. Session persistence ensures that traffic is always routed to the same backend instance for the duration of the session, which can improve request latency and the user experience.

In session persistence, a client directly provides information, such as a header or a cookie, that the gateway proxy uses as a reference to direct traffic to a specific backend server. The persistent client request bypasses the proxy's load balancing algorithm and is routed directly to the backend that it previously established a session with.

**Cookie**: A client sends a request to your app, and receives a `set-cookie` response header. The client then reuses that value in a cookie request header in subsequent requests. The gateway proxy uses this cookie to maintain a persistent connection to a single backend server on behalf of the client.

**Header**: A client sends a request to your app, and receives an HTTP response header. The client then reuses that value in the same header in subsequent HTTP requests. The gateway proxy uses this header to maintain a persistent connection to a single backend server on behalf of the client.

### Session persistence versus session affinity

In session persistence, the backend service is encoded in a cookie or header and affinity can be maintained for as long as the backend service is available. This makes session persistence more reliable than [session affinity through consistent hashing](../consistent-hashing), or "weak" session affinity, in which affinity might be lost when a backend service is added or removed, or if the gateway proxy restarts.

However, note that session persistence and session affinity can functionally work together in your kgateway setup. If you define both session persistence and session affinity through consistent hashing, the gateway proxy makes the following routing decisions for incoming requests:
- If the request contains a session persistence identity in a cookie or header, route the request directly to the backend that it previously established a session with.
- If no session persistence identity is present, load balance the request according to the defined session affinity configuration, along with any [load balancing configuration](../loadbalancing).

For more information about session peristence, see the [Kubernetes Gateway API enhancement doc](https://gateway-api.sigs.k8s.io/geps/gep-1619/).

## Before you begin 

{{< reuse "docs/snippets/prereq.md" >}}

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
| `cookieConfig.lifetimeType` | If the `type` is `Cookie`, the `lifetimeType` determines whether the session cookie has a `Permanent` or `Session`-based lifetime. A permanent cookie persists until its specified expiry time, while a session cookie is deleted when the current session ends. When set to `Permanent`, `absoluteTimeout` indicates the cookie's lifetime as defined by either the `Expires` or `Max-Age` cookie attributes, and is required. When set to `Session`, `absoluteTimeout` indicates the absolute lifetime of the cookie that is tracked by the gateway, and is optional. Defaults to `Session`. |

## Verify the session persistence configuration {#verify}

To try out session persistence, you can follow these steps to define cookie-based session persistence in the HTTPRoute for the httpbin sample app.

1. Scale the httpbin app up to 2 instances.
   ```sh 
   kubectl scale deployment httpbin -n httpbin --replicas=2
   ```
   
2. Verify that another instance of the httpbin app is created and note the IP addresses of both httpbin instances. In the following example, you have an httpbin instance available at the `10.0.43.175` and `10.0.38.52` IP addresses.
   ```sh
   kubectl get pods -n httpbin -o wide
   ```
   
   Example output
   ```
   NAME                      READY   STATUS        RESTARTS   AGE    IP            NODE                          NOMINATED NODE   READINESS GATES
   httpbin-8d557795f-86hzg   3/3     Running       0          54m    10.0.43.175   ip-10-0-34-108.ec2.internal   <none>           <none>
   httpbin-8d557795f-h8ks9   3/3     Running       0          126m   10.0.38.52    ip-10-0-39-74.ec2.internal    <none>           <none>
   ```

3. Modify the sample HTTPRoute resource for the httpbin app to add the following `sessionPersistence` section. These settings instruct the gateway proxy to create a persistent session cookie called `Session-A` for any new client connections to the httpbin app. Each created session has an idle timeout of 30 minutes, and the cookie for each session is deleted when the session ends.
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
           idleTimeout: 30m
           cookieConfig:
             lifetimeType: Session
   EOF
   ```

4. Send a request to the httpbin app and verify that you see the `Session-A` cookie in the `set-cookie` header of your response. The `-c` option stores the cookie in a local file on your machine so that you can use it in subsequent requests.
   {{< tabs tabTotal="2" items="LoadBalancer IP address or hostname,Port-forward for local testing" >}}
   {{% tab tabName="LoadBalancer IP address or hostname" %}}
   ```sh
   curl -i -c cookie-jar -k http://$INGRESS_GW_ADDRESS:8080/headers \
   -H "host: httpbin.example:8080"
   ```
   {{% /tab %}}
   {{% tab tabName="Port-forward for local testing" %}}
   ```sh
   curl -i -c cookie-jar -k localhost:8080/headers \
   -H "host: httpbin.example:8080"
   ```
   {{% /tab %}}
   {{< /tabs >}} 
   
   Example output: 
   ```
   < set-cookie: Session-A="298b1ac340fdea97"; Max-Age=60; Path=/; HttpOnly
   set-cookie: Session-A="298b1ac340fdea97"; Max-Age=60; Path=/; HttpOnly
   < server: envoy
   server: envoy
   < 

   {
     "headers": {
       "Accept": [
        "*/*"
       ],
       "Host": [
         "httpbin.example:8080"
       ],
       "User-Agent": [
         "curl/8.7.1"
       ],
       "X-Envoy-Expected-Rq-Timeout-Ms": [
         "15000"
       ],
       "X-Forwarded-Proto": [
         "http"
       ],
       "X-Request-Id": [
         "fe080d74-2b6e-4954-8bde-54bed3e71dde"
       ]
     }
   }
   ```

5. Repeat the request a few more times. Include the cookie that you stored in the local file by using the `-b` option. Make sure to send these requests within the 30 minute cookie validity period.
   {{< tabs tabTotal= "2" >}}
   {{% tab tabName="LoadBalancer IP address or hostname" %}}
   ```sh
   for i in {1..10}; do
   curl -i -b cookie-jar -k http://$INGRESS_GW_ADDRESS:8080/headers \
   -H "host: httpbin.example:8080"; done
   ```
   {{% /tab %}}
   {{% tab tabName="Port-forward for local testing" %}}
   ```sh
   for i in {1..10}; do
   curl -i -b cookie-jar -k localhost:8080/headers \
   -H "host: htttpbin.example:8080"; done
   ```
   {{% /tab %}}
   {{< /tabs >}}

6. Get the logs of the httpbin instance that served the initial request. Verify that all subsequent requests were also served by the same instance.
   ```sh
   kubectl logs <httpbin-pod> -n httpbin
   ```

7. Optional: Verify the permanence of the session cookie by restarting the http gateway.
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
   3. Repeat the same request with the session cookie. Make sure to send this request within the 30 minute cookie validity period.
      {{< tabs tabTotal= "2" >}}
      {{% tab tabName="LoadBalancer IP address or hostname" %}}
      ```sh
      for i in {1..10}; do
      curl -i -b cookie-jar -k http://$INGRESS_GW_ADDRESS:8080/headers \
      -H "host: httpbin.example:8080"; done
      ```
      {{% /tab %}}
      {{% tab tabName="Port-forward for local testing" %}}
      ```sh
      for i in {1..10}; do
      curl -i -b cookie-jar -k localhost:8080/headers \
      -H "host: htttpbin.example:8080"; done
      ```
      {{% /tab %}}
      {{< /tabs >}}
   4. Check the logs again of the httpbin instance that served the previous requests. Verify that your most recent request continued to be served by the same instance, even after the http gateway restarted.
      ```sh
      kubectl logs <httpbin-pod> -n httpbin
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
     labels:
       example: httpbin-route
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