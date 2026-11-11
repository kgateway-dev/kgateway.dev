Control the value of the `server` header in responses from the gateway proxy.

## About the server header {#about}

By default, the gateway proxy sets the `server` header to `envoy` in every response and overwrites any `server` header that the backend sends. You might want to change this behavior, such as to keep the `server` header that your backend sets, or to not reveal which proxy software your gateway runs.

To change how the gateway proxy handles the `server` header, set the `serverHeaderTransformation` field in the `spec.default.httpSettings` section of a ListenerPolicy to one of the following values.

| Value | Description |
| -- | -- |
| `Overwrite` | The default behavior. The gateway proxy sets the `server` header to `envoy`{{< version exclude-if="2.3.x" >}}, or to the value of the `serverName` field if set,{{< /version >}} and overwrites any `server` header from the backend. |
| `AppendIfAbsent` | The gateway proxy keeps the `server` header from the backend. If the backend does not send a `server` header, the gateway proxy sets it to `envoy`{{< version exclude-if="2.3.x" >}}, or to the value of the `serverName` field if set{{< /version >}}. |
| `PassThrough` | The gateway proxy keeps the `server` header from the backend unchanged. If the backend does not send a `server` header, the response does not include one. |

{{< version exclude-if="2.3.x" >}}
To change the value that the gateway proxy sets, use the `serverName` field in the same section. The `serverName` field applies to the `Overwrite` and `AppendIfAbsent` modes. In the `PassThrough` mode, the gateway proxy never sets the `server` header, so the `serverName` field has no effect.
{{< /version >}}

## Before you begin

{{< reuse "kgw-docs/snippets/prereq.md" >}}

## Default behavior {#default}

Send a request to the httpbin app that asks httpbin to return a `server: my-backend` response header. The `/response-headers` endpoint of the httpbin app sets response headers from the query parameters in the request.

{{< tabs >}}
{{% tab name="Cloud Provider LoadBalancer" %}}
```sh
curl -i "http://$INGRESS_GW_ADDRESS:8080/response-headers?Server=my-backend" -H "host: www.example.com"
```
{{% /tab %}}
{{% tab name="Port-forward for local testing" %}}
```sh
curl -i "localhost:8080/response-headers?Server=my-backend" -H "host: www.example.com"
```
{{% /tab %}}
{{< /tabs >}}

Example output: The gateway proxy overwrites the `server` header that the httpbin app sets with the `envoy` value. The response body shows the `server` header value that the httpbin app sent.

```console {hl_lines=[5,11,12,13]}
HTTP/1.1 200 OK
access-control-allow-credentials: true
access-control-allow-origin: *
content-type: application/json; encoding=utf-8
server: envoy
date: Wed, 11 Nov 2026 16:08:48 GMT
content-length: 39
x-envoy-upstream-service-time: 1

{
  "Server": [
    "my-backend"
  ]
}
```

## Pass through the backend server header {#pass-through}

1. Create a ListenerPolicy that sets the `serverHeaderTransformation` field to `PassThrough`.

   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.kgateway.dev/v1alpha1
   kind: ListenerPolicy
   metadata:
     name: server-header
     namespace: {{< reuse "kgw-docs/snippets/namespace.md" >}}
   spec:
     targetRefs:
     - group: gateway.networking.k8s.io
       kind: Gateway
       name: http
     default:
       httpSettings:
         serverHeaderTransformation: PassThrough
   EOF
   ```

   {{< reuse "kgw-docs/snippets/review-table.md" >}} For more information about the available fields, see the [API reference]({{< link-hextra path="/reference/api/#httpsettings" >}}).

   | Setting | Description |
   | -- | -- |
   | `spec.targetRefs` | The Gateway that this policy applies to. The policy applies to all HTTP and HTTPS listeners on the Gateway. |
   | `spec.default.httpSettings.serverHeaderTransformation` | Set to `PassThrough` to forward the `server` header from the backend unchanged, and to not add a `server` header if the backend does not send one. |

2. Repeat the request to the `/response-headers` endpoint. Verify that the response now includes the `server: my-backend` header from the httpbin app.

   {{< tabs >}}
   {{% tab name="Cloud Provider LoadBalancer" %}}
   ```sh
   curl -i "http://$INGRESS_GW_ADDRESS:8080/response-headers?Server=my-backend" -H "host: www.example.com"
   ```
   {{% /tab %}}
   {{% tab name="Port-forward for local testing" %}}
   ```sh
   curl -i "localhost:8080/response-headers?Server=my-backend" -H "host: www.example.com"
   ```
   {{% /tab %}}
   {{< /tabs >}}

   Example output:

   ```console {hl_lines=[5]}
   HTTP/1.1 200 OK
   access-control-allow-credentials: true
   access-control-allow-origin: *
   content-type: application/json; encoding=utf-8
   server: my-backend
   date: Wed, 11 Nov 2026 16:08:48 GMT
   content-length: 39
   x-envoy-upstream-service-time: 1
   ...
   ```

3. Send a request to the `/status/200` endpoint of the httpbin app, which does not set a `server` header. Verify that the response does not include a `server` header.

   {{< tabs >}}
   {{% tab name="Cloud Provider LoadBalancer" %}}
   ```sh
   curl -i http://$INGRESS_GW_ADDRESS:8080/status/200 -H "host: www.example.com"
   ```
   {{% /tab %}}
   {{% tab name="Port-forward for local testing" %}}
   ```sh
   curl -i localhost:8080/status/200 -H "host: www.example.com"
   ```
   {{% /tab %}}
   {{< /tabs >}}

   Example output:

   ```console
   HTTP/1.1 200 OK
   access-control-allow-credentials: true
   access-control-allow-origin: *
   date: Wed, 11 Nov 2026 16:08:48 GMT
   content-length: 0
   x-envoy-upstream-service-time: 1
   ```

## Set the server header only if the backend does not {#append-if-absent}

1. Update the ListenerPolicy to set the `serverHeaderTransformation` field to `AppendIfAbsent`.{{< version exclude-if="2.3.x" >}} The `serverName` field sets the value that the gateway proxy uses when the backend does not send a `server` header.{{< /version >}}

   {{< version include-if="2.3.x" >}}
   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.kgateway.dev/v1alpha1
   kind: ListenerPolicy
   metadata:
     name: server-header
     namespace: {{< reuse "kgw-docs/snippets/namespace.md" >}}
   spec:
     targetRefs:
     - group: gateway.networking.k8s.io
       kind: Gateway
       name: http
     default:
       httpSettings:
         serverHeaderTransformation: AppendIfAbsent
   EOF
   ```
   {{< /version >}}
   {{< version exclude-if="2.3.x" >}}
   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.kgateway.dev/v1alpha1
   kind: ListenerPolicy
   metadata:
     name: server-header
     namespace: {{< reuse "kgw-docs/snippets/namespace.md" >}}
   spec:
     targetRefs:
     - group: gateway.networking.k8s.io
       kind: Gateway
       name: http
     default:
       httpSettings:
         serverHeaderTransformation: AppendIfAbsent
         serverName: my-gateway
   EOF
   ```
   {{< /version >}}

2. Repeat the request to the `/response-headers` endpoint. Verify that the response includes the `server: my-backend` header from the httpbin app.

   {{< tabs >}}
   {{% tab name="Cloud Provider LoadBalancer" %}}
   ```sh
   curl -i "http://$INGRESS_GW_ADDRESS:8080/response-headers?Server=my-backend" -H "host: www.example.com"
   ```
   {{% /tab %}}
   {{% tab name="Port-forward for local testing" %}}
   ```sh
   curl -i "localhost:8080/response-headers?Server=my-backend" -H "host: www.example.com"
   ```
   {{% /tab %}}
   {{< /tabs >}}

   Example output:

   ```console {hl_lines=[5]}
   HTTP/1.1 200 OK
   access-control-allow-credentials: true
   access-control-allow-origin: *
   content-type: application/json; encoding=utf-8
   server: my-backend
   date: Wed, 11 Nov 2026 16:08:48 GMT
   content-length: 39
   x-envoy-upstream-service-time: 1
   ...
   ```

3. Repeat the request to the `/status/200` endpoint. Verify that the gateway proxy adds a `server` header with the {{< version include-if="2.3.x" >}}`envoy`{{< /version >}}{{< version exclude-if="2.3.x" >}}`my-gateway`{{< /version >}} value, because the httpbin app does not send one.

   {{< tabs >}}
   {{% tab name="Cloud Provider LoadBalancer" %}}
   ```sh
   curl -i http://$INGRESS_GW_ADDRESS:8080/status/200 -H "host: www.example.com"
   ```
   {{% /tab %}}
   {{% tab name="Port-forward for local testing" %}}
   ```sh
   curl -i localhost:8080/status/200 -H "host: www.example.com"
   ```
   {{% /tab %}}
   {{< /tabs >}}

   Example output:

   {{< version include-if="2.3.x" >}}
   ```console {hl_lines=[7]}
   HTTP/1.1 200 OK
   access-control-allow-credentials: true
   access-control-allow-origin: *
   date: Wed, 11 Nov 2026 16:08:48 GMT
   content-length: 0
   x-envoy-upstream-service-time: 1
   server: envoy
   ```
   {{< /version >}}
   {{< version exclude-if="2.3.x" >}}
   ```console {hl_lines=[7]}
   HTTP/1.1 200 OK
   access-control-allow-credentials: true
   access-control-allow-origin: *
   date: Wed, 11 Nov 2026 16:08:48 GMT
   content-length: 0
   x-envoy-upstream-service-time: 1
   server: my-gateway
   ```
   {{< /version >}}

{{< version exclude-if="2.3.x" >}}
## Replace the server header with a custom value {#server-name}

1. Update the ListenerPolicy to set only the `serverName` field. Because the `serverHeaderTransformation` field is not set, the gateway proxy uses the default `Overwrite` mode.

   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.kgateway.dev/v1alpha1
   kind: ListenerPolicy
   metadata:
     name: server-header
     namespace: {{< reuse "kgw-docs/snippets/namespace.md" >}}
   spec:
     targetRefs:
     - group: gateway.networking.k8s.io
       kind: Gateway
       name: http
     default:
       httpSettings:
         serverName: my-gateway
   EOF
   ```

2. Repeat the request to the `/response-headers` endpoint. Verify that the gateway proxy replaces the `server: my-backend` header from the httpbin app with the `my-gateway` value.

   {{< tabs >}}
   {{% tab name="Cloud Provider LoadBalancer" %}}
   ```sh
   curl -i "http://$INGRESS_GW_ADDRESS:8080/response-headers?Server=my-backend" -H "host: www.example.com"
   ```
   {{% /tab %}}
   {{% tab name="Port-forward for local testing" %}}
   ```sh
   curl -i "localhost:8080/response-headers?Server=my-backend" -H "host: www.example.com"
   ```
   {{% /tab %}}
   {{< /tabs >}}

   Example output:

   ```console {hl_lines=[5]}
   HTTP/1.1 200 OK
   access-control-allow-credentials: true
   access-control-allow-origin: *
   content-type: application/json; encoding=utf-8
   server: my-gateway
   date: Wed, 11 Nov 2026 16:08:48 GMT
   content-length: 39
   x-envoy-upstream-service-time: 1
   ...
   ```
{{< /version >}}

## Cleanup

{{< reuse "kgw-docs/snippets/cleanup.md" >}}

```sh
kubectl delete listenerpolicy server-header -n {{< reuse "kgw-docs/snippets/namespace.md" >}} --ignore-not-found
```
