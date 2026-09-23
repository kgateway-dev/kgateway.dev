---
title: Buffering
description: Buffer request and response bodies so that filters can inspect and transform them safely.
weight: 20
next: /docs/traffic-management/header-control
prev: /docs/traffic-management/route-delegation
---

{{< reuse "kgw-docs/pages/traffic-management/buffering2.2-body.md" >}}

## Move the buffer filter before body-reading filters

By default, the buffer filter runs at a fixed position after authentication, authorization, and rate limiting, but before routing. This default position is not one of the values that you can set in the `buffer.filterStage.stage` and `buffer.filterStage.predicate` fields. 

The following stages and predicates are supported to determine the position of the buffering filter in the Envoy filter chain.

> [!NOTE]
> To keep the buffering filter at the default position, omit the `buffer.filterStage` block entirely.


| `buffer.filterStage.stage` | `buffer.filterStage.predicate`  |
| --- | --- |
| <ul><li>`Fault`: Earliest stage. The buffer filter runs before fault injection.</li><li>`AuthN`: Authentication stage.</li><li>`AuthZ`: Authorization stage.</li><li>`RateLimit`: Rate limiting stage.</li><li>`Route`: Final processing stage before the request leaves the gateway proxy. </li></ul> | <ul><li>`Before`: Runs the buffer filter before the selected stage. </li><li>`During`: Runs the buffer filter during the selected stage. This setting is the default when the `predicate` field is not set. </li><li>`After`: Runs the buffer filter after the selected stage. </li></ul> |

Some filters in the filter chain read or hold the request body before the buffer filter ever sees it, such as external auth with request body checks, ExtProc, or a request transformation. When one of these filters reads the body, the `maxRequestSize` setting on the {{< reuse "/kgw-docs/snippets/kgateway.md" >}} resource cannot be enforced, because the buffer filter never receives the body to measure it. You can set the `buffer.filterStage` field to move the buffer filter to an earlier position in the filter chain to place it ahead of the filter that reads the body. This way, you can reject oversized messages before they reach the extauth service. 

Because {{< reuse "/kgw-docs/snippets/kgateway.md" >}} installs one buffer filter per filter chain, this placement applies to every route on the listener that the {{< reuse "/kgw-docs/snippets/trafficpolicy.md" >}} targets, not only the route that is named in the `targetRefs` block. If {{< reuse "/kgw-docs/snippets/trafficpolicy.md" >}} resources on the same filter chain ask for different stages, the earliest requested stage wins for the whole chain. 

The following example uses a separate route and hostname so that the buffer and transformation policies from the earlier sections do not interfere with it.

1. Deploy an external authorization service, a Service, and a GatewayExtension in the `httpbin` namespace, so that no cross-namespace [ReferenceGrant](https://gateway-api.sigs.k8s.io/reference/api-types/referencegrant/) is required. This example reuses the sample service from [Bring your own external authorization service]({{< link-hextra path="/security/external-auth/" >}}#byo-ext-auth), which allows any request that carries the `x-ext-authz: allow` header.
   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: apps/v1
   kind: Deployment
   metadata:
     name: ext-authz
     namespace: httpbin
     labels:
       app: ext-authz
   spec:
     replicas: 1
     selector:
       matchLabels:
         app: ext-authz
     template:
       metadata:
         labels:
           app: ext-authz
       spec:
         containers:
         - image: gcr.io/istio-testing/ext-authz:1.25-dev
           name: ext-authz
           ports:
           - containerPort: 9000
   ---
   apiVersion: v1
   kind: Service
   metadata:
     name: ext-authz
     namespace: httpbin
     labels:
       app: ext-authz
   spec:
     ports:
     - port: 4444
       targetPort: 9000
       protocol: TCP
       appProtocol: kubernetes.io/h2c
     selector:
       app: ext-authz
   ---
   apiVersion: gateway.kgateway.dev/v1alpha1
   kind: GatewayExtension
   metadata:
     name: basic-ext-auth-buffer
     namespace: httpbin
   spec:
     type: ExtAuth
     extAuth:
       grpcService:
         backendRef:
           name: ext-authz
           port: 4444
   EOF
   ```

2. Create an HTTPRoute with its own hostname, and a {{< reuse "/kgw-docs/snippets/trafficpolicy.md" >}} that pairs `extAuth.withRequestBody` with `buffer.maxRequestSize`. Do not set `buffer.filterStage` yet.
   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.networking.k8s.io/v1
   kind: HTTPRoute
   metadata:
     name: bufferedroute
     namespace: httpbin
   spec:
     parentRefs:
     - name: http
       namespace: {{< reuse "/kgw-docs/snippets/namespace.md" >}}
     hostnames:
     - "bufferedroute.com"
     rules:
     - backendRefs:
       - name: httpbin
         port: 8000
   ---
   apiVersion: {{< reuse "/kgw-docs/snippets/trafficpolicy-apiversion.md" >}}
   kind: {{< reuse "/kgw-docs/snippets/trafficpolicy.md" >}}
   metadata:
     name: bufferedroute-policy
     namespace: httpbin
   spec:
     targetRefs:
     - group: gateway.networking.k8s.io
       kind: HTTPRoute
       name: bufferedroute
     extAuth:
       extensionRef:
         name: basic-ext-auth-buffer
       withRequestBody:
         maxRequestBytes: 8192
     buffer:
       maxRequestSize: "1024"
   EOF
   ```

3. Send an oversized request. The external authorization service allows any request that carries the `x-ext-authz: allow` header, so a rejection can only come from the buffer filter. Verify that the request succeeds even though the body is larger than the configured `maxRequestSize`. The external authorization service buffers the body ahead of the buffer filter's default placement in the filter chain, so the configured `maxRequestSize` never gets a chance to reject it.

   {{< tabs >}}
   {{% tab name="Cloud Provider LoadBalancer" %}}
   ```sh
   curl -sik -X POST http://$INGRESS_GW_ADDRESS:8080/anything \
   -H "host: bufferedroute.com:8080" \
   -H "x-ext-authz: allow" \
   --data-binary @/tmp/large_payload_2k.txt
   ```
   {{% /tab %}}
   {{% tab name="Port-forward for local testing" %}}
   ```sh
   curl -sik -X POST http://localhost:8080/anything \
   -H "host: bufferedroute.com:8080" \
   -H "x-ext-authz: allow" \
   --data-binary @/tmp/large_payload_2k.txt
   ```
   {{% /tab %}}
   {{< /tabs >}}

   Example output:
   ```console
   HTTP/1.1 200 OK
   access-control-allow-credentials: true
   access-control-allow-origin: *
   content-type: application/json; encoding=utf-8
   ```

4. Add the `buffer.filterStage` field to the same {{< reuse "/kgw-docs/snippets/trafficpolicy.md" >}} to move the buffer filter before the `AuthN` stage, ahead of external auth.
   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: {{< reuse "/kgw-docs/snippets/trafficpolicy-apiversion.md" >}}
   kind: {{< reuse "/kgw-docs/snippets/trafficpolicy.md" >}}
   metadata:
     name: bufferedroute-policy
     namespace: httpbin
   spec:
     targetRefs:
     - group: gateway.networking.k8s.io
       kind: HTTPRoute
       name: bufferedroute
     extAuth:
       extensionRef:
         name: basic-ext-auth-buffer
       withRequestBody:
         maxRequestBytes: 8192
     buffer:
       maxRequestSize: "1024"
       filterStage:
         stage: AuthN
         predicate: Before
   EOF
   ```

5. Send the same oversized request again. The buffer filter now runs before external auth, so it sees the body first and rejects it.
   {{< tabs >}}
   {{% tab name="Cloud Provider LoadBalancer" %}}
   ```sh
   curl -sik -X POST http://$INGRESS_GW_ADDRESS:8080/anything \
   -H "host: bufferedroute.com:8080" \
   -H "x-ext-authz: allow" \
   --data-binary @/tmp/large_payload_2k.txt
   ```
   {{% /tab %}}
   {{% tab name="Port-forward for local testing" %}}
   ```sh
   curl -sik -X POST http://localhost:8080/anything \
   -H "host: bufferedroute.com:8080" \
   -H "x-ext-authz: allow" \
   --data-binary @/tmp/large_payload_2k.txt
   ```
   {{% /tab %}}
   {{< /tabs >}}

   Example output:
   ```
   HTTP/1.1 413 Payload Too Large
   content-length: 17
   content-type: text/plain
   ```

6. Send a small request, `"hello world"`, to confirm that the route still accepts requests within the limit.
   {{< tabs >}}
   {{% tab name="Cloud Provider LoadBalancer" %}}
   ```sh
   curl -sik -X POST http://$INGRESS_GW_ADDRESS:8080/anything \
      -H "host: bufferedroute.com:8080" \
      -H "x-ext-authz: allow" \
      -d "{\"payload\": \"hello world\"}"
   ```
   {{% /tab %}}
   {{% tab name="Port-forward for local testing" %}}
   ```sh
   curl -sik -X POST http://localhost:8080/anything \
      -H "host: bufferedroute.com:8080" \
      -H "x-ext-authz: allow" \
      -d "{\"payload\": \"hello world\"}"
   ```
   {{% /tab %}}
   {{< /tabs >}}

   Example output:
   ```console
   HTTP/1.1 200 OK
   ...
     "json": {
       "payload": "hello world"
     }
   ```



> [!NOTE]
> This placement applies to every route on the listener that the policy targets. If routes on the same listener need different buffer-filter placements, serve them from separate listeners.
>
> Do not set `buffer.filterStage` together with `buffer.disable`. The API rejects a buffer policy that sets both fields.
>
> Do not set `buffer.filterStage.weight` to a nonzero value. The field defaults to `0`. A filter chain has only one buffer filter. If you have multiple {{< reuse "/kgw-docs/snippets/trafficpolicy.md" >}} resources that request different stages, the earliest stage is configured in the buffer filter. All other stages are ignored. Because the `weight` field cannot break a tie in such cases, tthe API rejects a nonzero value.

## Cleanup

{{< reuse "kgw-docs/snippets/cleanup.md" >}}

```sh
kubectl delete {{< reuse "/kgw-docs/snippets/trafficpolicy.md" >}} transformation-buffer-body -n httpbin --ignore-not-found
kubectl delete {{< reuse "/kgw-docs/snippets/trafficpolicy.md" >}} transformation-buffer-limit -n httpbin --ignore-not-found
kubectl delete {{< reuse "/kgw-docs/snippets/trafficpolicy.md" >}} bufferedroute-policy -n httpbin --ignore-not-found
kubectl delete httproute/bufferedroute gatewayextension/basic-ext-auth-buffer deployment/ext-authz service/ext-authz -n httpbin --ignore-not-found
kubectl delete listenerpolicy bufferlimits -n {{< reuse "/kgw-docs/snippets/namespace.md" >}} --ignore-not-found
```
