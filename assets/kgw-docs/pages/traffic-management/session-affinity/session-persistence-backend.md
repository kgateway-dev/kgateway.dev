Ensure that traffic from a client is always routed to the same backend instance for the duration of a session.

> [!WARNING]
> Session persistence is experimental.
>
> * **BackendConfigPolicy**: The `sessionPersistence` field is an experimental {{< reuse "/kgw-docs/snippets/kgateway.md" >}} API and is subject to breaking changes. The field does not require the experimental channel of the Kubernetes Gateway API.
> * **HTTPRoute**: The `sessionPersistence` field is part of the experimental channel of the Kubernetes Gateway API, which deprecates the field in version 1.7.

## About

Session persistence, also known as "strong" session affinity or sticky sessions, ensures that traffic is always routed to the same backend instance for the duration of the session, which can improve request latency and the user experience.

In session persistence, a client directly provides information, such as a header or a cookie, that the gateway proxy uses as a reference to direct traffic to a specific backend instance. The persistent client request bypasses the load balancing algorithm of the proxy and is routed directly to the backend instance that it previously established a session with.

**Cookie**: When you use cookie-based persistence, a client sends a request to your app, and receives a `set-cookie` response header. The client then reuses that value in a cookie request header in subsequent requests. The gateway proxy uses this cookie to maintain a persistent connection to a single backend instance on behalf of the client.

**Header**: When you use header-based persistence, a client sends a request to your app, and receives an HTTP response header. The client then reuses that value in the same header in subsequent HTTP requests. The gateway proxy uses this header to maintain a persistent connection to a single backend instance on behalf of the client.

You can configure session persistence in one of the following ways.

* **HTTPRoute**: Set the `sessionPersistence` field of an HTTPRoute rule. The settings apply to the requests that the rule matches.
* **BackendConfigPolicy**: Set the `sessionPersistence` field of a [BackendConfigPolicy]({{< link-hextra path="/about/policies/backendconfigpolicy/" >}}) that targets a Service or a Backend. The policy applies to the HTTPRoutes and GRPCRoutes that route to the backend. It has no effect on TCPRoutes or TLSRoutes. If a route splits traffic between backends, the policy pins a client only to an instance of the backend that the split selects.

> [!NOTE]
> The Kubernetes Gateway API version 1.7 deprecates the `sessionPersistence` field of an HTTPRoute rule in favor of session persistence on the backend. The field still works in this version. If a backend has a BackendConfigPolicy with session persistence, the policy takes precedence over the `sessionPersistence` field of a route rule, and the route reports the `SessionPersistenceOverridden` reason on its `kgateway.dev/Programmed` condition.

### Session persistence versus session affinity

In session persistence, the backend instance is encoded in a cookie or header and affinity can be maintained for as long as the backend instance is available. This makes session persistence more reliable than [session affinity through consistent hashing](../consistent-hashing), or "weak" session affinity, in which affinity might be lost when the set of backend instances changes.

However, note that session persistence and session affinity can functionally work together in your {{< reuse "/kgw-docs/snippets/kgateway.md" >}} setup. If you define both session persistence and session affinity through consistent hashing, the gateway proxy makes the following routing decisions for incoming requests:
- If the request contains a session persistence identity in a cookie or header, route the request directly to the backend instance that it previously established a session with.
- If no session persistence identity is present, load balance the request according to the defined session affinity configuration, along with any [load balancing configuration](../loadbalancing).

For more information about session persistence, see the [Kubernetes Gateway API enhancement doc](https://gateway-api.sigs.k8s.io/geps/gep-1619/).

## Before you begin

{{< reuse "kgw-docs/snippets/prereq.md" >}}

The requirements depend on the option that you use.

* **HTTPRoute**: Install the experimental channel of the Kubernetes Gateway API, because the `sessionPersistence` field of an HTTPRoute is not part of the standard channel. {{< reuse "/kgw-docs/snippets/kgateway.md" >}} ignores the field if you disable experimental Gateway API features. For more information, see [Experimental Gateway API features]({{< link-hextra path="/install/advanced/#experimental-gateway-api-features" >}}).

  ```sh
  kubectl apply --server-side -f https://github.com/kubernetes-sigs/gateway-api/releases/download/v{{< reuse "kgw-docs/versions/k8s-gw-version.md" >}}/experimental-install.yaml
  ```

* **BackendConfigPolicy**: You do not need the experimental channel of the Kubernetes Gateway API. The option also works if you disable experimental Gateway API features.

## Configure session persistence

{{< tabs >}}
{{% tab name="BackendConfigPolicy" %}}

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

{{% /tab %}}
{{% tab name="HTTPRoute" %}}

Define session persistence based on either a cookie or a header in the `sessionPersistence` section of an HTTPRoute rule. The following example defines cookie-based session persistence for requests to `/path-A`, and header-based session persistence for requests to `/path-B`.

```yaml
apiVersion: gateway.networking.k8s.io/v1
kind: HTTPRoute
metadata:
  name: example-route
  namespace: default
spec:
  parentRefs:
    - name: example-gateway
      namespace: {{< reuse "kgw-docs/snippets/namespace.md" >}}
  rules:
    - matches:
        - path:
            type: PathPrefix
            value: /path-A
      backendRefs:
        - name: backend
          port: 3000
      sessionPersistence:
        type: Cookie
        absoluteTimeout: 10s
        cookie:
          name: Session-A
          lifetimeType: Permanent
    - matches:
        - path:
            type: PathPrefix
            value: /path-B
      backendRefs:
        - name: backend
          port: 3000
      sessionPersistence:
        type: Header
        header:
          name: Session-B
```

{{< reuse "/kgw-docs/snippets/review-table.md" >}}

| Setting | Description |
| -- | -- |
| `type` | The request property, either `Header` or `Cookie`, to base session persistence on. Defaults to `Cookie`. |
| `cookie.name` | The name of the cookie that the proxy sends in response to the client and that the client reuses in subsequent requests. If you do not set a name, the cookie is named `sessionPersistence`. To prevent unpredictable behavior or rejection, do not reuse cookie names. |
| `cookie.path` | The `Path` attribute of the cookie. Defaults to `/`. |
| `cookie.lifetimeType` | Whether the cookie has a `Permanent` or a `Session`-based lifetime. A permanent cookie persists until its expiry time, while a session cookie is deleted when the current session ends. Defaults to `Session`. When set to `Permanent`, `absoluteTimeout` is required. |
| `header.name` | The name of the header that the proxy sends in response to the client. The client must include this header in subsequent requests to maintain the session. Required if the `type` is `Header`. |
| `absoluteTimeout` | The absolute timeout of the persistent session. Once the duration has elapsed, the session becomes invalid. Only cookies with the `Permanent` lifetime support this field. For session cookies and headers, the field has no effect. |

> [!NOTE]
> You must set the `cookie` field if the `type` is `Cookie`, and the `header` field if the `type` is `Header`. The `sessionName`, `cookieConfig`, and `idleTimeout` fields are not available in the Kubernetes Gateway API version 1.7.

{{% /tab %}}
{{< /tabs >}}

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

3. Configure session persistence for the httpbin app. These settings instruct the gateway proxy to create a persistent session cookie called `Session-A` for any new client connections to the httpbin app. Each created session has an absolute timeout of 30 minutes, and the cookie persists for that time.
   {{< tabs >}}
   {{% tab name="BackendConfigPolicy" %}}
   Create a BackendConfigPolicy for the httpbin service with the `sessionPersistence` section.
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
   {{% /tab %}}
   {{% tab name="HTTPRoute" %}}
   Modify the sample HTTPRoute resource for the httpbin app to add the `sessionPersistence` section.
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
         namespace: {{< reuse "kgw-docs/snippets/namespace.md" >}}
     hostnames:
       - "www.example.com"
     rules:
       - backendRefs:
           - name: httpbin
             port: 8000
         sessionPersistence:
           type: Cookie
           absoluteTimeout: 30m
           cookie:
             name: Session-A
             lifetimeType: Permanent
   EOF
   ```
   {{% /tab %}}
   {{< /tabs >}}

4. Send a request to the httpbin app and verify that you see the `Session-A` cookie in the `set-cookie` header of your response. The `-c` option stores the cookie in a local file on your machine so that you can use it in subsequent requests.
   {{< tabs >}}
   {{% tab name="Cloud Provider LoadBalancer" %}}
   ```sh
   curl -i -c cookie-jar http://$INGRESS_GW_ADDRESS:8080/headers \
   -H "host: www.example.com:8080"
   ```
   {{% /tab %}}
   {{% tab name="Port-forward for local testing" %}}
   ```sh
   curl -i -c cookie-jar localhost:8080/headers \
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
   date: Wed, 28 Oct 2026 02:21:26 GMT
   content-length: 446
   x-envoy-upstream-service-time: 0
   set-cookie: Session-A="Cg8xMC4yNDQuMC4zOjgwODAQrsaF1wY="; Max-Age=1800; Path=/; HttpOnly
   server: envoy
   ...
   ```

5. Repeat the request a few more times. Include the cookie that you stored in the local file by using the `-b` option. Make sure to send these requests within the 30 minute cookie validity period.
   {{< tabs >}}
   {{% tab name="Cloud Provider LoadBalancer" %}}
   ```sh
   for i in {1..10}; do
   curl -i -b cookie-jar http://$INGRESS_GW_ADDRESS:8080/headers \
   -H "host: www.example.com:8080"; done
   ```
   {{% /tab %}}
   {{% tab name="Port-forward for local testing" %}}
   ```sh
   for i in {1..10}; do
   curl -i -b cookie-jar localhost:8080/headers \
   -H "host: www.example.com:8080"; done
   ```
   {{% /tab %}}
   {{< /tabs >}}

6. Check the logs of each httpbin instance. Verify that only one of the instances served all 10 of the subsequent requests that you made.
   ```sh
   kubectl logs -n httpbin <httpbin-pod>
   ```

   Example output for one pod, in which the first request (timestamp at `02:21:26`) and all 10 subsequent requests (timestamps at `02:21:27`) are served by the same instance:
   ```
   ...
   time="2026-10-28T02:21:26.3729" status=200 method="GET" uri="/headers" size_bytes=446 duration_ms=0.03 user_agent="curl/8.7.1" client_ip=10.244.0.87
   time="2026-10-28T02:21:27.4003" status=200 method="GET" uri="/headers" size_bytes=528 duration_ms=0.04 user_agent="curl/8.7.1" client_ip=10.244.0.87
   time="2026-10-28T02:21:27.4155" status=200 method="GET" uri="/headers" size_bytes=528 duration_ms=0.02 user_agent="curl/8.7.1" client_ip=10.244.0.87
   time="2026-10-28T02:21:27.428" status=200 method="GET" uri="/headers" size_bytes=528 duration_ms=0.01 user_agent="curl/8.7.1" client_ip=10.244.0.87
   ...
   ```

7. Optional: Verify the permanence of the session cookie by restarting the http gateway. The session cookie persists after the gateway restarts due to the `cookie.lifetimeType: Permanent` setting.
   1. Restart the http gateway proxy.
      ```sh
      kubectl rollout restart deploy/http -n {{< reuse "kgw-docs/snippets/namespace.md" >}}
      ```
   2. Verify that the gateway proxy pod is running.
      ```sh
      kubectl get po -n {{< reuse "kgw-docs/snippets/namespace.md" >}} -l gateway.networking.k8s.io/gateway-name=http
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
      {{% tab name="Cloud Provider LoadBalancer" %}}
   ```sh
   for i in {1..10}; do
   curl -i -b cookie-jar http://$INGRESS_GW_ADDRESS:8080/headers \
   -H "host: www.example.com:8080"; done
   ```
      {{% /tab %}}
      {{% tab name="Port-forward for local testing" %}}
   ```sh
   for i in {1..10}; do
   curl -i -b cookie-jar localhost:8080/headers \
   -H "host: www.example.com:8080"; done
   ```
      {{% /tab %}}
      {{< /tabs >}}
   5. Check the logs again of the httpbin instance that served the previous requests. Verify that your most recent request continued to be served by the same instance, even after the http gateway restarted.
      ```sh
      kubectl logs -n httpbin <httpbin-pod>
      ```

      Example output for one pod, in which all 10 new requests (timestamps at `02:22:54`) are served after the previous requests (timestamps at `02:21:27`):
      ```
      ...
      time="2026-10-28T02:21:27.5063" status=200 method="GET" uri="/headers" size_bytes=528 duration_ms=0.01 user_agent="curl/8.7.1" client_ip=10.244.0.87
      time="2026-10-28T02:22:54.33" status=200 method="GET" uri="/headers" size_bytes=529 duration_ms=0.12 user_agent="curl/8.7.1" client_ip=10.244.0.87
      time="2026-10-28T02:22:54.3502" status=200 method="GET" uri="/headers" size_bytes=529 duration_ms=0.04 user_agent="curl/8.7.1" client_ip=10.244.0.87
      time="2026-10-28T02:22:54.3639" status=200 method="GET" uri="/headers" size_bytes=529 duration_ms=0.04 user_agent="curl/8.7.1" client_ip=10.244.0.87
      ...
      ```

## Cleanup

{{< reuse "kgw-docs/snippets/cleanup.md" >}}

1. Scale the httpbin app back down.
   ```sh
   kubectl scale deployment httpbin -n httpbin --replicas=1
   ```

2. Remove the session persistence configuration.
   {{< tabs >}}
   {{% tab name="BackendConfigPolicy" %}}
   Delete the BackendConfigPolicy.
   ```sh
   kubectl delete backendconfigpolicy session-persistence -n httpbin
   ```
   {{% /tab %}}
   {{% tab name="HTTPRoute" %}}
   Remove the session persistence settings from the httpbin HTTPRoute.
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
         namespace: {{< reuse "kgw-docs/snippets/namespace.md" >}}
     hostnames:
       - "www.example.com"
     rules:
       - backendRefs:
           - name: httpbin
             port: 8000
   EOF
   ```
   {{% /tab %}}
   {{< /tabs >}}
