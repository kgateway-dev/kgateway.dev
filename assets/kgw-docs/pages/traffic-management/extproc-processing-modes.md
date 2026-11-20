Use processing modes to control which parts of a request and response the gateway sends to your ExtProc server, such as headers, bodies, and trailers.

## About processing modes

By default, the gateway proxy sends only the request headers and the response headers to the ExtProc server. Bodies and trailers pass through the gateway without being sent to the ExtProc server. With a processing mode, you can change this behavior for each of the six parts of an HTTP exchange. For example, you might send the request body so that your ExtProc server can inspect or rewrite the payload, or skip the response headers if your server only works on requests. Each part that you skip saves a round trip to the ExtProc server.

You can set the processing mode in the following places:

* **GatewayExtension**: The `extProc.processingMode` field sets the mode for all routes that use this ExtProc server.
* **{{< reuse "kgw-docs/snippets/trafficpolicy.md" >}}**: The `extProc.processingMode` field sets a different mode for the routes that the policy applies to.
* **ExtProc server**: If you set `extProc.allowProcessingModeOverride` in the GatewayExtension, the ExtProc server can change the mode for a single request. For more information, see [Let the ExtProc server change the mode](#server-override).

### Processing mode fields

The following table describes the fields of a processing mode. If you omit a field, the default value is used.

| Field | Default | Values |
| -- | -- | -- |
| `requestHeaderMode` | `SEND` | `SEND`, `SKIP`, or `DEFAULT` |
| `responseHeaderMode` | `SEND` | `SEND`, `SKIP`, or `DEFAULT` |
| `requestBodyMode` | `NONE` | `NONE`, `STREAMED`, `BUFFERED`, `BUFFERED_PARTIAL`, or `FULL_DUPLEX_STREAMED` |
| `responseBodyMode` | `NONE` | `NONE`, `STREAMED`, `BUFFERED`, `BUFFERED_PARTIAL`, or `FULL_DUPLEX_STREAMED` |
| `requestTrailerMode` | `SKIP` | `SEND`, `SKIP`, or `DEFAULT` |
| `responseTrailerMode` | `SKIP` | `SEND`, `SKIP`, or `DEFAULT` |

For headers and trailers, `SEND` sends that part to the ExtProc server, and `SKIP` does not. `DEFAULT` uses Envoy's default, which sends headers and skips trailers. In a {{< reuse "kgw-docs/snippets/trafficpolicy.md" >}}, `DEFAULT` also means Envoy's default, not the value from the GatewayExtension.

For bodies, choose one of the following modes.

| Body mode | Description |
| -- | -- |
| `NONE` | Do not send the body. |
| `STREAMED` | Send the body to the ExtProc server in chunks as they arrive. |
| `BUFFERED` | Buffer the entire body in the gateway proxy, and send it in one message. If the body is larger than the [buffer limit]({{< link-hextra path="/traffic-management/buffering/" >}}), the gateway proxy returns an error. |
| `BUFFERED_PARTIAL` | Buffer the body up to the buffer limit, and send what was buffered in one message. Larger bodies are not rejected. |
| `FULL_DUPLEX_STREAMED` | Stream the body to the ExtProc server in chunks as they arrive. The ExtProc server can buffer chunks and send its processed chunks back at any time. You must also set the matching trailer mode, such as `requestTrailerMode` for `requestBodyMode`, to `SEND`. Otherwise, the gateway proxy rejects the configuration for the entire listener and keeps its previous configuration, even though the resource status shows `Accepted`. |

For more information, see the [Envoy processing mode reference](https://www.envoyproxy.io/docs/envoy/latest/api-v3/extensions/filters/http/ext_proc/v3/processing_mode.proto).

### Set the mode for all routes {#gatewayextension}

To change the mode for every route that uses an ExtProc server, set `processingMode` in the GatewayExtension. The following example sends the request body to the ExtProc server after the gateway proxy buffers it, and skips the response headers.

```yaml
apiVersion: gateway.kgateway.dev/v1alpha1
kind: GatewayExtension
metadata:
  name: ext-proc-extension
  namespace: {{< reuse "kgw-docs/snippets/namespace.md" >}}
spec:
  type: ExtProc
  extProc:
    grpcService:
      backendRef:
        name: ext-proc-grpc
        port: 4444
    processingMode:
      requestBodyMode: BUFFERED
      responseHeaderMode: SKIP
```

### Override the mode for specific routes {#trafficpolicy}

To use a different mode for some routes, set `extProc.processingMode` in the {{< reuse "kgw-docs/snippets/trafficpolicy.md" >}} that applies the ExtProc server to those routes. The mode in the {{< reuse "kgw-docs/snippets/trafficpolicy.md" >}} applies to these routes, even if `allowProcessingModeOverride` is not set in the GatewayExtension.

> [!IMPORTANT]
> The mode in the {{< reuse "kgw-docs/snippets/trafficpolicy.md" >}} replaces the mode in the GatewayExtension as a whole. Fields are not merged. Any field that you omit in the {{< reuse "kgw-docs/snippets/trafficpolicy.md" >}} gets its default value from the [processing mode fields](#processing-mode-fields) table, not the value from the GatewayExtension. For example, if the GatewayExtension in the previous example skips response headers and a {{< reuse "kgw-docs/snippets/trafficpolicy.md" >}} sets only `requestBodyMode: STREAMED`, the response headers on the routes of that policy are sent to the ExtProc server again. To keep a setting from the GatewayExtension, repeat it in the {{< reuse "kgw-docs/snippets/trafficpolicy.md" >}}.

## Before you begin

{{< reuse "kgw-docs/snippets/prereq.md" >}}

4. Deploy the sample ExtProc server as shown in [Set up an ExtProc server]({{< link-hextra path="/traffic-management/extproc/header-manipulation/#set-up-an-extproc-server" >}}). The sample server reads instructions from an `instructions` header in the request headers and in the response headers, and adds or removes headers as instructed. The sample server does not process bodies, so this guide uses the header modes only.

## Skip the response headers on a route {#walkthrough}

In this example, you apply an ExtProc server to a route and check that the server processes both the request headers and the response headers. Then, you use a {{< reuse "kgw-docs/snippets/trafficpolicy.md" >}} to stop sending the response headers for that route.

1. Create a GatewayExtension for the ExtProc server. The `processingMode` field explicitly sets the default mode, which sends the request headers and the response headers to the ExtProc server.
   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.kgateway.dev/v1alpha1
   kind: GatewayExtension
   metadata:
     name: ext-proc-modes
     namespace: {{< reuse "kgw-docs/snippets/namespace.md" >}}
   spec:
     type: ExtProc
     extProc:
       grpcService:
         backendRef:
           name: ext-proc-grpc
           port: 4444
       processingMode:
         requestHeaderMode: SEND
         responseHeaderMode: SEND
   EOF
   ```

   {{< reuse "kgw-docs/snippets/review-table.md" >}}

   | Setting | Description |
   | -- | -- |
   | `spec.extProc.grpcService.backendRef` | The Service of the sample ExtProc server that you deployed before you began. |
   | `spec.extProc.processingMode.requestHeaderMode` | Set to `SEND` to send the request headers to the ExtProc server. |
   | `spec.extProc.processingMode.responseHeaderMode` | Set to `SEND` to send the response headers to the ExtProc server. |

2. Create an HTTPRoute for the httpbin app on the `extproc-modes.example` domain.
   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.networking.k8s.io/v1
   kind: HTTPRoute
   metadata:
     name: extproc-modes
     namespace: {{< reuse "kgw-docs/snippets/namespace.md" >}}
   spec:
     parentRefs:
       - name: http
         namespace: {{< reuse "kgw-docs/snippets/namespace.md" >}}
     hostnames:
       - "extproc-modes.example"
     rules:
       - backendRefs:
           - name: httpbin
             port: 8000
             namespace: httpbin
   EOF
   ```

3. Create a ReferenceGrant to allow the HTTPRoute to forward traffic to the httpbin app. This resource is required because the HTTPRoute and the httpbin app are in different namespaces. If you already created this ReferenceGrant in the [header manipulation guide]({{< link-hextra path="/traffic-management/extproc/header-manipulation/" >}}), you can skip this step.
   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.networking.k8s.io/v1beta1
   kind: ReferenceGrant
   metadata:
     name: allow-httproute-to-httpbin
     namespace: httpbin
   spec:
     from:
       - group: gateway.networking.k8s.io
         kind: HTTPRoute
         namespace: {{< reuse "kgw-docs/snippets/namespace.md" >}}
     to:
       - group: ""
         kind: Service
   EOF
   ```

4. Create a {{< reuse "kgw-docs/snippets/trafficpolicy.md" >}} that applies the ExtProc server to the HTTPRoute.
   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: {{< reuse "kgw-docs/snippets/trafficpolicy-apiversion.md" >}}
   kind: {{< reuse "kgw-docs/snippets/trafficpolicy.md" >}}
   metadata:
     name: extproc-modes
     namespace: {{< reuse "kgw-docs/snippets/namespace.md" >}}
   spec:
     targetRefs:
       - group: gateway.networking.k8s.io
         kind: HTTPRoute
         name: extproc-modes
     extProc:
       extensionRef:
         name: ext-proc-modes
   EOF
   ```

5. Send a request to the `/response-headers` path of the httpbin app. The httpbin app returns each query parameter as a response header, so the response includes an `instructions` header that tells the ExtProc server to add the `extproc-response: true` header. Verify that the response includes the `extproc-response: true` header. This header shows that the ExtProc server processed the response headers.

   {{< tabs >}}

   {{% tab name="Cloud Provider LoadBalancer" %}}
   ```sh
   curl -i -G http://$INGRESS_GW_ADDRESS:8080/response-headers -H "host: extproc-modes.example" \
     --data-urlencode 'instructions={"addHeaders":{"extproc-response":"true"}}'
   ```
   {{% /tab %}}

   {{% tab name="Port-forward for local testing" %}}
   ```sh
   curl -i -G http://localhost:8080/response-headers -H "host: extproc-modes.example" \
     --data-urlencode 'instructions={"addHeaders":{"extproc-response":"true"}}'
   ```
   {{% /tab %}}

   {{< /tabs >}}

   Example output:
   ```console {hl_lines=[7]}
   HTTP/1.1 200 OK
   access-control-allow-credentials: true
   access-control-allow-origin: *
   content-type: application/json; encoding=utf-8
   instructions: {"addHeaders":{"extproc-response":"true"}}
   ...
   extproc-response: true
   server: envoy
   ...
   ```

6. Update the {{< reuse "kgw-docs/snippets/trafficpolicy.md" >}} to skip the response headers for the route. Because the mode in the {{< reuse "kgw-docs/snippets/trafficpolicy.md" >}} replaces the mode in the GatewayExtension, `requestHeaderMode` gets its default value of `SEND`, and the request headers are still sent to the ExtProc server.
   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: {{< reuse "kgw-docs/snippets/trafficpolicy-apiversion.md" >}}
   kind: {{< reuse "kgw-docs/snippets/trafficpolicy.md" >}}
   metadata:
     name: extproc-modes
     namespace: {{< reuse "kgw-docs/snippets/namespace.md" >}}
   spec:
     targetRefs:
       - group: gateway.networking.k8s.io
         kind: HTTPRoute
         name: extproc-modes
     extProc:
       extensionRef:
         name: ext-proc-modes
       processingMode:
         responseHeaderMode: SKIP
   EOF
   ```

   {{< reuse "kgw-docs/snippets/review-table.md" >}}

   | Setting | Description |
   | -- | -- |
   | `spec.extProc.processingMode.responseHeaderMode` | Set to `SKIP` to stop sending the response headers for this route. The other fields get their default values, not the values from the GatewayExtension. |

7. Repeat the request. Verify that the response still includes the `instructions` header, but no `extproc-response` header, because the response headers are no longer sent to the ExtProc server.

   {{< tabs >}}

   {{% tab name="Cloud Provider LoadBalancer" %}}
   ```sh
   curl -i -G http://$INGRESS_GW_ADDRESS:8080/response-headers -H "host: extproc-modes.example" \
     --data-urlencode 'instructions={"addHeaders":{"extproc-response":"true"}}'
   ```
   {{% /tab %}}

   {{% tab name="Port-forward for local testing" %}}
   ```sh
   curl -i -G http://localhost:8080/response-headers -H "host: extproc-modes.example" \
     --data-urlencode 'instructions={"addHeaders":{"extproc-response":"true"}}'
   ```
   {{% /tab %}}

   {{< /tabs >}}

   Example output:
   ```console
   HTTP/1.1 200 OK
   access-control-allow-credentials: true
   access-control-allow-origin: *
   content-type: application/json; encoding=utf-8
   instructions: {"addHeaders":{"extproc-response":"true"}}
   ...
   server: envoy
   ...
   ```

8. Send a request to the `/headers` path with instructions in the request headers. Verify that the `Extproc-Request` header is in the request headers that the httpbin app received, which shows that the ExtProc server still processes the request headers.

   {{< tabs >}}

   {{% tab name="Cloud Provider LoadBalancer" %}}
   ```sh
   curl -s http://$INGRESS_GW_ADDRESS:8080/headers -H "host: extproc-modes.example" \
     -H 'instructions: {"addHeaders":{"extproc-request":"true"}}'
   ```
   {{% /tab %}}

   {{% tab name="Port-forward for local testing" %}}
   ```sh
   curl -s http://localhost:8080/headers -H "host: extproc-modes.example" \
     -H 'instructions: {"addHeaders":{"extproc-request":"true"}}'
   ```
   {{% /tab %}}

   {{< /tabs >}}

   Example output:
   ```console {hl_lines=[6,7,8]}
   {
     "headers": {
       "Accept": [
         "*/*"
       ],
       "Extproc-Request": [
         "true"
       ],
   ...
   ```

## Let the ExtProc server change the mode {#server-override}

An ExtProc server can decide for each request whether it needs more of the request or response. For example, the server might check the `content-type` request header and request the body only for JSON payloads. To do that, the server sets the `mode_override` field in its response to the request headers or the response headers. The new mode applies to the rest of that request and its response only. To change how the request body is processed, the server must send `mode_override` with its response to the request headers.

The gateway proxy ignores `mode_override` unless you set `allowProcessingModeOverride: true` in the GatewayExtension. To limit the modes that the server can switch to, list them in `allowedProcessingModeOverrides`. The gateway proxy then ignores a `mode_override` that does not match one of the listed modes. If you omit the list, the server can switch to any mode.

Each mode in the list gets the default values from the [processing mode fields](#processing-mode-fields) table for the fields that you omit. The gateway proxy fills the header and trailer fields that the `mode_override` leaves at `DEFAULT` with the values from the `processingMode` of the GatewayExtension, and then compares the result with the list. The result must match one of the listed modes in every field except `requestHeaderMode`. The following example lets the ExtProc server turn on buffered request body processing. Because this GatewayExtension does not set `processingMode`, the fields that the server omits stay at `DEFAULT` and do not match the listed mode. To match, the server must send a `mode_override` that sets `requestBodyMode` to `BUFFERED`, `responseHeaderMode` to `SEND`, and both trailer modes to `SKIP`. If you set `processingMode` in the GatewayExtension, the omitted fields come from that mode instead.

```yaml
apiVersion: gateway.kgateway.dev/v1alpha1
kind: GatewayExtension
metadata:
  name: ext-proc-extension
  namespace: {{< reuse "kgw-docs/snippets/namespace.md" >}}
spec:
  type: ExtProc
  extProc:
    grpcService:
      backendRef:
        name: ext-proc-grpc
        port: 4444
    allowProcessingModeOverride: true
    allowedProcessingModeOverrides:
      - requestBodyMode: BUFFERED
```

> [!NOTE]
> The ExtProc server cannot override the mode if the `processingMode` in the GatewayExtension sets a body mode to `FULL_DUPLEX_STREAMED`. A mode that you set in a {{< reuse "kgw-docs/snippets/trafficpolicy.md" >}} does not depend on these settings.

For more information, see [`allow_mode_override`](https://www.envoyproxy.io/docs/envoy/latest/api-v3/extensions/filters/http/ext_proc/v3/ext_proc.proto#envoy-v3-api-field-extensions-filters-http-ext-proc-v3-externalprocessor-allow-mode-override) and [`allowed_override_modes`](https://www.envoyproxy.io/docs/envoy/latest/api-v3/extensions/filters/http/ext_proc/v3/ext_proc.proto#envoy-v3-api-field-extensions-filters-http-ext-proc-v3-externalprocessor-allowed-override-modes) in the Envoy documentation.

## Cleanup

{{< reuse "kgw-docs/snippets/cleanup.md" >}}

```sh
kubectl delete trafficpolicy extproc-modes -n {{< reuse "kgw-docs/snippets/namespace.md" >}}
kubectl delete httproute extproc-modes -n {{< reuse "kgw-docs/snippets/namespace.md" >}}
kubectl delete gatewayextension ext-proc-modes -n {{< reuse "kgw-docs/snippets/namespace.md" >}}
```
