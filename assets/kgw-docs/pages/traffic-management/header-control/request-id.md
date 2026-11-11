Control how the gateway proxy generates and forwards the `x-request-id` header.

## About request IDs {#about}

The gateway proxy adds an `x-request-id` header with a UUID to each request before it forwards the request to the backend. You can use the request ID to correlate the logs of a single request across your gateway proxy and backend services, such as with the `%REQ(X-REQUEST-ID)%` command in [access logs]({{< link-hextra path="/security/access-logging/" >}}). If you set up [tracing]({{< link-hextra path="/observability/tracing/" >}}), the gateway proxy also uses the request ID to make trace sampling decisions.

By default, the gateway proxy generates a new request ID for every request from a downstream client. If the client already sends an `x-request-id` header, the gateway proxy replaces it with a new value.

You can use the following settings in the `spec.default.httpSettings` section of a ListenerPolicy to change this behavior.

| Setting | Description |
| -- | -- |
| `preserveExternalRequestId` | Set to `true` to keep the `x-request-id` header that a client sends. The gateway proxy still generates a request ID for requests without an `x-request-id` header. Defaults to `false`. |
| `generateRequestId` | Set to `false` to stop generating request IDs, such as to save the cost of generating a UUID for each request in high-throughput setups. Requests without an `x-request-id` header are forwarded without one, and an `x-request-id` header that a client sends is forwarded unchanged. Defaults to `true`. |
| `uuidRequestIdConfig.packTraceReason` | When tracing is set up, the gateway proxy can change one character of the request ID to record the trace sampling decision in the UUID. Set to `false` to forward request IDs unchanged, such as to keep the exact UUIDs that an external system sets. Note that without the sampling decision in the request ID, stable sampling of traces and access logs no longer works, and only random sampling is possible. Defaults to `true`. |
| `uuidRequestIdConfig.useRequestIdForTraceSampling` | Whether the gateway proxy uses the request ID to make trace sampling decisions. When `true`, the sampling decision is consistent for all requests with the same request ID. Defaults to `true`. |

> [!NOTE]
> If you set `useRemoteAddress` to `false` in your ListenerPolicy, the gateway proxy keeps the `x-request-id` header that a client sends, even if you do not set `preserveExternalRequestId`. The gateway proxy replaces request IDs only for requests that it treats as coming from external clients, which requires `useRemoteAddress` to be `true`, the default setting.

## Before you begin

{{< reuse "kgw-docs/snippets/prereq.md" >}}

## Default behavior {#default}

Send a request to the httpbin app with the `x-request-id: my-request-123` header. Verify that the `X-Request-Id` header that the httpbin app receives has a new UUID instead of the value that you sent.

{{< tabs >}}
{{% tab name="Cloud Provider LoadBalancer" %}}
```sh
curl http://$INGRESS_GW_ADDRESS:8080/headers -H "host: www.example.com" \
  -H "x-request-id: my-request-123"
```
{{% /tab %}}
{{% tab name="Port-forward for local testing" %}}
```sh
curl localhost:8080/headers -H "host: www.example.com" \
  -H "x-request-id: my-request-123"
```
{{% /tab %}}
{{< /tabs >}}

Example output:

```console {hl_lines=[24,25]}
{
  "headers": {
    "Accept": [
      "*/*"
    ],
    "Host": [
      "www.example.com"
    ],
    "User-Agent": [
      "curl/8.7.1"
    ],
    "X-Envoy-Expected-Rq-Timeout-Ms": [
      "15000"
    ],
    "X-Envoy-External-Address": [
      "127.0.0.1"
    ],
    "X-Forwarded-For": [
      "10.244.0.7"
    ],
    "X-Forwarded-Proto": [
      "http"
    ],
    "X-Request-Id": [
      "6e2e78c8-17bd-4340-846b-525ae7dc6c9b"
    ]
  }
}
```

## Keep request IDs from clients {#preserve}

If a client or a proxy in front of the gateway proxy already sets request IDs, keep them so that you can correlate the request across all systems.

1. Create a ListenerPolicy that sets `preserveExternalRequestId` to `true`.

   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.kgateway.dev/v1alpha1
   kind: ListenerPolicy
   metadata:
     name: request-id
     namespace: {{< reuse "kgw-docs/snippets/namespace.md" >}}
   spec:
     targetRefs:
     - group: gateway.networking.k8s.io
       kind: Gateway
       name: http
     default:
       httpSettings:
         preserveExternalRequestId: true
   EOF
   ```

   {{< reuse "kgw-docs/snippets/review-table.md" >}} For more information about the available fields, see the [API reference]({{< link-hextra path="/reference/api/#httpsettings" >}}).

   | Setting | Description |
   | -- | -- |
   | `spec.targetRefs` | The Gateway that this policy applies to. The policy applies to all HTTP and HTTPS listeners on the Gateway. |
   | `spec.default.httpSettings.preserveExternalRequestId` | Set to `true` to keep the `x-request-id` header that a client sends instead of replacing it with a new value. |

2. Repeat the request with the `x-request-id: my-request-123` header. Verify that the httpbin app receives the request ID that you sent.

   {{< tabs >}}
   {{% tab name="Cloud Provider LoadBalancer" %}}
   ```sh
   curl http://$INGRESS_GW_ADDRESS:8080/headers -H "host: www.example.com" \
     -H "x-request-id: my-request-123"
   ```
   {{% /tab %}}
   {{% tab name="Port-forward for local testing" %}}
   ```sh
   curl localhost:8080/headers -H "host: www.example.com" \
     -H "x-request-id: my-request-123"
   ```
   {{% /tab %}}
   {{< /tabs >}}

   Example output:

   ```console {hl_lines=[2,3]}
   ...
       "X-Request-Id": [
         "my-request-123"
       ]
   ...
   ```

3. Send a request without an `x-request-id` header. Verify that the gateway proxy still generates a request ID.

   {{< tabs >}}
   {{% tab name="Cloud Provider LoadBalancer" %}}
   ```sh
   curl http://$INGRESS_GW_ADDRESS:8080/headers -H "host: www.example.com"
   ```
   {{% /tab %}}
   {{% tab name="Port-forward for local testing" %}}
   ```sh
   curl localhost:8080/headers -H "host: www.example.com"
   ```
   {{% /tab %}}
   {{< /tabs >}}

   Example output:

   ```console {hl_lines=[2,3]}
   ...
       "X-Request-Id": [
         "fc7f8d46-069c-4575-94ea-6ca69c01c7a1"
       ]
   ...
   ```

## Stop generating request IDs {#disable}

1. Update the ListenerPolicy to set `generateRequestId` to `false`.

   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.kgateway.dev/v1alpha1
   kind: ListenerPolicy
   metadata:
     name: request-id
     namespace: {{< reuse "kgw-docs/snippets/namespace.md" >}}
   spec:
     targetRefs:
     - group: gateway.networking.k8s.io
       kind: Gateway
       name: http
     default:
       httpSettings:
         generateRequestId: false
   EOF
   ```

2. Send a request without an `x-request-id` header. Verify that the httpbin app does not receive an `X-Request-Id` header.

   {{< tabs >}}
   {{% tab name="Cloud Provider LoadBalancer" %}}
   ```sh
   curl http://$INGRESS_GW_ADDRESS:8080/headers -H "host: www.example.com"
   ```
   {{% /tab %}}
   {{% tab name="Port-forward for local testing" %}}
   ```sh
   curl localhost:8080/headers -H "host: www.example.com"
   ```
   {{% /tab %}}
   {{< /tabs >}}

   Example output:

   ```console
   {
     "headers": {
       "Accept": [
         "*/*"
       ],
       "Host": [
         "www.example.com"
       ],
       "User-Agent": [
         "curl/8.7.1"
       ],
       "X-Envoy-Expected-Rq-Timeout-Ms": [
         "15000"
       ],
       "X-Envoy-External-Address": [
         "127.0.0.1"
       ],
       "X-Forwarded-For": [
         "10.244.0.7"
       ],
       "X-Forwarded-Proto": [
         "http"
       ]
     }
   }
   ```

## Keep request IDs unchanged with tracing {#pack-trace-reason}

When you set up [tracing]({{< link-hextra path="/observability/tracing/" >}}), the gateway proxy records its trace sampling decision in the request ID by changing the version character of the UUID. For example, if you keep request IDs from clients, a sampled request with the `1b4e28ba-2fa1-41d2-883f-0016d3cca427` request ID is forwarded with the `1b4e28ba-2fa1-91d2-883f-0016d3cca427` request ID. If your systems require the exact UUID that a client sends, set `packTraceReason` to `false`.

1. Update the ListenerPolicy to keep request IDs from clients and to not change them.

   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.kgateway.dev/v1alpha1
   kind: ListenerPolicy
   metadata:
     name: request-id
     namespace: {{< reuse "kgw-docs/snippets/namespace.md" >}}
   spec:
     targetRefs:
     - group: gateway.networking.k8s.io
       kind: Gateway
       name: http
     default:
       httpSettings:
         preserveExternalRequestId: true
         uuidRequestIdConfig:
           packTraceReason: false
   EOF
   ```

   {{< reuse "kgw-docs/snippets/review-table.md" >}}

   | Setting | Description |
   | -- | -- |
   | `spec.default.httpSettings.preserveExternalRequestId` | Keep the `x-request-id` header that a client sends. |
   | `spec.default.httpSettings.uuidRequestIdConfig.packTraceReason` | Set to `false` to forward request IDs without recording the trace sampling decision in them. |
   | `spec.default.httpSettings.uuidRequestIdConfig.useRequestIdForTraceSampling` | Not set in this example, so it defaults to `true`. |

2. Port-forward the gateway proxy on port 19000 to open the Envoy admin interface.

   ```sh
   kubectl port-forward deploy/http -n {{< reuse "kgw-docs/snippets/namespace.md" >}} 19000
   ```

3. In the Envoy configuration, verify that the request ID extension is configured. Alternatively, you can open the [Envoy admin interface](http://localhost:19000/config_dump) and look for the `request_id_extension` setting in the config dump.

   ```sh
   curl -s localhost:19000/config_dump | jq '[.. | objects | select(has("request_id_extension")) | {preserve_external_request_id, request_id_extension}]'
   ```

   Example output:

   ```console
   [
     {
       "preserve_external_request_id": true,
       "request_id_extension": {
         "typed_config": {
           "@type": "type.googleapis.com/envoy.extensions.request_id.uuid.v3.UuidRequestIdConfig",
           "pack_trace_reason": false,
           "use_request_id_for_trace_sampling": true
         }
       }
     }
   ]
   ```

## Cleanup

{{< reuse "kgw-docs/snippets/cleanup.md" >}}

```sh
kubectl delete listenerpolicy request-id -n {{< reuse "kgw-docs/snippets/namespace.md" >}} --ignore-not-found
```
