Ensure that traffic from a client is always routed to the same backend instance for the duration of a session.

> [!WARNING]
> Session persistence in the BackendConfigPolicy is experimental and subject to breaking changes.

## About

Session persistence, also known as "strong" session affinity or sticky sessions, ensures that traffic is always routed to the same backend instance for the duration of the session, which can improve request latency and the user experience.

In session persistence, a client directly provides information, such as a header or a cookie, that the gateway proxy uses as a reference to direct traffic to a specific backend instance. The persistent client request bypasses the load balancing algorithm of the proxy and is routed directly to the backend instance that it previously established a session with.

**Cookie**: When you use cookie-based persistence, a client sends a request to your app, and receives a `set-cookie` response header. The client then reuses that value in a cookie request header in subsequent requests. The gateway proxy uses this cookie to maintain a persistent connection to a single backend instance on behalf of the client.

**Header**: When you use header-based persistence, a client sends a request to your app, and receives an HTTP response header. The client then reuses that value in the same header in subsequent HTTP requests. The gateway proxy uses this header to maintain a persistent connection to a single backend instance on behalf of the client.

You configure session persistence in the `sessionPersistence` field of a [BackendConfigPolicy]({{< link-hextra path="/about/policies/backendconfigpolicy/" >}}) that targets a Service or a Backend. The policy applies to the HTTPRoutes and GRPCRoutes that route to the backend. It has no effect on TCPRoutes or TLSRoutes. If a route splits traffic between backends, the policy pins a client only to an instance of the backend that the split selects.

> [!NOTE]
> The Kubernetes Gateway API version 1.7 deprecates the `sessionPersistence` field of an HTTPRoute rule in favor of session persistence on the backend. Use the BackendConfigPolicy instead. If a backend has a BackendConfigPolicy with session persistence, the policy takes precedence over the `sessionPersistence` field of a route rule, and the route reports the `SessionPersistenceOverridden` reason on its `kgateway.dev/Programmed` condition.

### Session persistence versus session affinity

In session persistence, the backend instance is encoded in a cookie or header and affinity can be maintained for as long as the backend instance is available. This makes session persistence more reliable than [session affinity through consistent hashing](../consistent-hashing), or "weak" session affinity, in which affinity might be lost when the set of backend instances changes.

However, note that session persistence and session affinity can functionally work together in your {{< reuse "/kgw-docs/snippets/kgateway.md" >}} setup. If you define both session persistence and session affinity through consistent hashing, the gateway proxy makes the following routing decisions for incoming requests:
- If the request contains a session persistence identity in a cookie or header, route the request directly to the backend instance that it previously established a session with.
- If no session persistence identity is present, load balance the request according to the defined session affinity configuration, along with any [load balancing configuration](../loadbalancing).

For more information about session persistence, see the [Kubernetes Gateway API enhancement doc](https://gateway-api.sigs.k8s.io/geps/gep-1619/).

## Before you begin

{{< reuse "kgw-docs/snippets/prereq.md" >}}

## Configure session persistence

Define session persistence based on either a cookie or a header in the `sessionPersistence` section of a BackendConfigPolicy. The following example defines cookie-based session persistence for the `httpbin` service.

```yaml
apiVersion: gateway.kgateway.dev/v1alpha1
kind: BackendConfigPolicy
metadata:
  name: session-persistence
  namespace: httpbin
spec:
  targetRefs:
    - name: httpbin
      group: ""
      kind: Service
  sessionPersistence:
    type: Cookie
    absoluteTimeout: 30m
    cookie:
      name: Session-A
      lifetimeType: Permanent
```

To use a header instead, set the `type` to `Header` and the name of the header.

```yaml
  sessionPersistence:
    type: Header
    header:
      name: Session-B
```

{{< reuse "/kgw-docs/snippets/review-table.md" >}}

| Setting | Description |
| -- | -- |
| `targetRefs` | The Service or Backend that the policy applies to. |
| `type` | The request property, either `Header` or `Cookie`, to base session persistence on. Defaults to `Cookie`. |
| `cookie.name` | The name of the cookie that the proxy sends in response to the client and that the client reuses in subsequent requests. If you do not set a name, a unique name such as `kgw-sp-1cccccdd2c8865e2` is generated for each backend. To prevent unpredictable behavior or rejection, do not reuse cookie names. Do not use the same name for backends in the same traffic split, because clients lose their session whenever the split switches backends. |
| `cookie.path` | The `Path` attribute of the cookie. Defaults to `/`. |
| `cookie.lifetimeType` | Whether the cookie has a `Permanent` or a `Session`-based lifetime. A permanent cookie persists until its expiry time, while a session cookie is deleted when the current session ends. Defaults to `Session`. When set to `Permanent`, `absoluteTimeout` is required. |
| `header.name` | The name of the header that the proxy sends in response to the client. The client must include this header in subsequent requests to maintain the session. Required if the `type` is `Header`. |
| `absoluteTimeout` | The absolute timeout of the persistent session. Once the duration has elapsed, the session becomes invalid. Only cookies with the `Permanent` lifetime support this field. For session cookies and headers, the field has no effect. |

> [!NOTE]
> If you set an `absoluteTimeout` that has no effect, the BackendConfigPolicy is still accepted, but its `Accepted` condition has the `PartiallyValid` reason and the following message: `spec.sessionPersistence.absoluteTimeout only has an effect for Cookie sessions with spec.sessionPersistence.cookie.lifetimeType Permanent`. Session persistence has no effect on Backends of the dynamic forward proxy type, and the policy reports this in the same way.

## Verify the session persistence configuration {#verify}

To try out session persistence, you can follow these steps to define cookie-based session persistence for the httpbin sample app.

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

3. Create a BackendConfigPolicy for the httpbin service with the following `sessionPersistence` section. These settings instruct the gateway proxy to create a persistent session cookie called `Session-A` for any new client connections to the httpbin app. Each created session has an absolute timeout of 30 minutes, and the cookie persists for that time.
   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.kgateway.dev/v1alpha1
   kind: BackendConfigPolicy
   metadata:
     name: session-persistence
     namespace: httpbin
   spec:
     targetRefs:
       - name: httpbin
         group: ""
         kind: Service
     sessionPersistence:
       type: Cookie
       absoluteTimeout: 30m
       cookie:
         name: Session-A
         lifetimeType: Permanent
   EOF
   ```

4. Send a request to the httpbin app and verify that you see the `Session-A` cookie in the `set-cookie` header of your response. The `-c` option stores the cookie in a local file on your machine so that you can use it in subsequent requests.
   {{< tabs >}}
   {{% tab name="LoadBalancer IP address or hostname" %}}
   ```sh
   curl -i -c cookie-jar -k http://$INGRESS_GW_ADDRESS:8080/headers \
   -H "host: www.example.com:8080"
   ```
   {{% /tab %}}
   {{% tab name="Port-forward for local testing" %}}
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
   date: Tue, 27 Oct 2026 17:20:40 GMT
   content-length: 445
   x-envoy-upstream-service-time: 0
   set-cookie: Session-A="ChAxMC4yNDQuMC44MDo4MDAwENOKhNcG"; Max-Age=1800; Path=/; HttpOnly
   server: envoy
   ...
   ```

5. Repeat the request a few more times. Include the cookie that you stored in the local file by using the `-b` option. Make sure to send these requests within the 30 minute cookie validity period.
   {{< tabs >}}
   {{% tab name="LoadBalancer IP address or hostname" %}}
   ```sh
   for i in {1..10}; do
   curl -i -b cookie-jar -k http://$INGRESS_GW_ADDRESS:8080/headers \
   -H "host: www.example.com:8080"; done
   ```
   {{% /tab %}}
   {{% tab name="Port-forward for local testing" %}}
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
   time="2026-10-27T17:17:09.8479" status=200 method="GET" uri="/headers" size_bytes=440 duration_ms=0.10 user_agent="curl/8.7.1" client_ip=10.244.0.7
   time="2026-10-27T17:20:32.1077" status=200 method="GET" uri="/headers" size_bytes=445 duration_ms=0.04 user_agent="curl/8.7.1" client_ip=10.244.0.7
   time="2026-10-27T17:20:40.7017" status=200 method="GET" uri="/headers" size_bytes=445 duration_ms=0.05 user_agent="curl/8.7.1" client_ip=10.244.0.7
   time="2026-10-27T17:20:49.5744" status=200 method="GET" uri="/headers" size_bytes=515 duration_ms=0.04 user_agent="curl/8.7.1" client_ip=10.244.0.7
   ...
   ```

7. Optional: Verify the permanence of the session cookie by restarting the http gateway. The session cookie persists after the gateway restarts due to the `cookie.lifetimeType: Permanent` setting.
   1. Restart the http gateway proxy.
      ```sh
      kubectl rollout restart deploy/http -n {{< reuse "kgw-docs/snippets/namespace.md" >}}
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
      {{< tabs >}}
      {{% tab name="Cloud Provider LoadBalancer" %}}
   ```sh
   export INGRESS_GW_ADDRESS=$(kubectl get svc -n {{< reuse "kgw-docs/snippets/namespace.md" >}} http -o jsonpath="{.status.loadBalancer.ingress[0]['hostname','ip']}")
   echo $INGRESS_GW_ADDRESS
   ```
      {{% /tab %}}
      {{% tab name="Port-forward for local testing" %}}
   ```sh
   kubectl port-forward deployment/http -n {{< reuse "kgw-docs/snippets/namespace.md" >}} 8080:8080
   ```
      {{% /tab %}}
      {{< /tabs >}}
   4. Repeat the same request with the session cookie. Make sure to send this request within the 30 minute cookie validity period.
      {{< tabs >}}
      {{% tab name="LoadBalancer IP address or hostname" %}}
   ```sh
   for i in {1..10}; do
   curl -i -b cookie-jar -k http://$INGRESS_GW_ADDRESS:8080/headers \
   -H "host: www.example.com:8080"; done
   ```
      {{% /tab %}}
      {{% tab name="Port-forward for local testing" %}}
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
      time="2026-10-27T17:20:40.7017" status=200 method="GET" uri="/headers" size_bytes=445 duration_ms=0.05 user_agent="curl/8.7.1" client_ip=10.244.0.7
      time="2026-10-27T17:20:41.5744" status=200 method="GET" uri="/headers" size_bytes=515 duration_ms=0.04 user_agent="curl/8.7.1" client_ip=10.244.0.7
      time="2026-10-27T17:24:06.5744" status=200 method="GET" uri="/headers" size_bytes=515 duration_ms=0.04 user_agent="curl/8.7.1" client_ip=10.244.0.7
      time="2026-10-27T17:24:06.6013" status=200 method="GET" uri="/headers" size_bytes=515 duration_ms=0.04 user_agent="curl/8.7.1" client_ip=10.244.0.7
      time="2026-10-27T17:24:06.631" status=200 method="GET" uri="/headers" size_bytes=515 duration_ms=0.03 user_agent="curl/8.7.1" client_ip=10.244.0.7
      ...
      ```

## Cleanup

{{< reuse "kgw-docs/snippets/cleanup.md" >}}

1. Scale the httpbin app back down.
   ```sh
   kubectl scale deployment httpbin -n httpbin --replicas=1
   ```

2. Delete the BackendConfigPolicy.
   ```sh
   kubectl delete backendconfigpolicy session-persistence -n httpbin
   ```
