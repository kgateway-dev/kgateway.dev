Set a maximum number of headers that Envoy accepts on incoming requests. Requests that exceed the limit are rejected before they reach your upstream services. This way, you can protect your backends from oversized or malformed requests and limit certain header-based attack vectors.

By default, Envoy allows up to 100 headers per request. When the limit is exceeded, Envoy returns a `431 Request Header Fields Too Large` response for HTTP/1.x connections and resets the stream for HTTP/2 connections.

> [!NOTE]
> Keep in mind that HTTP clients, such as curl, automatically include additional headers beyond the ones you explicitly set. For example, a basic curl request always sends `Host`, `User-Agent`, and `Accept`, which already counts as 3 headers before any custom headers are added. Set `maxHeadersCount` to a value that accounts for headers that clients send automatically.

## Before you begin

{{< reuse "kgw-docs/snippets/prereq.md" >}}

## Set a maximum header count {#set-max-headers-count}

1. Create a ListenerPolicy with the `maxHeadersCount` setting.

   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.kgateway.dev/v1alpha1
   kind: ListenerPolicy
   metadata:
     name: max-headers-count
     namespace: {{< reuse "kgw-docs/snippets/namespace.md" >}}
   spec:
     targetRefs:
     - group: gateway.networking.k8s.io
       kind: Gateway
       name: http
     default:
       httpSettings:
         maxHeadersCount: 5
   EOF
   ```

   {{< reuse "kgw-docs/snippets/review-table.md" >}} For more information about the available fields, see the [API reference]({{< link-hextra path="/reference/api/#httpsettings" >}}).

   | Setting | Description |
   |---|---|
   | `spec.targetRefs` | The Gateway this policy applies to. |
   | `spec.default.httpSettings.maxHeadersCount` | The maximum number of headers that are allowed in a request. Requests that exceed this limit receive a `431` response for HTTP/1.x and a stream reset for HTTP/2 connections. Must be at least `1`. If unset, Envoy's default of `100` is used. |

2. Send a request to the httpbin app without extra headers. The curl automatically sends `Host`, `User-Agent`, and `Accept` (3 headers), which is under the limit of 5. Verify that you get back a 200 HTTP response code.

   {{< tabs items="Cloud Provider LoadBalancer,Port-forward for local testing" tabTotal="2" >}}
   {{% tab tabName="Cloud Provider LoadBalancer" %}}
   ```sh
   curl -v http://$INGRESS_GW_ADDRESS:8080/headers -H "host: www.example.com:8080"
   ```
   {{% /tab %}}
   {{% tab tabName="Port-forward for local testing" %}}
   ```sh
   curl -v localhost:8080/headers -H "host: www.example.com:8080"
   ```
   {{% /tab %}}
   {{< /tabs >}}

   Example output:
   ```console
   < HTTP/1.1 200 OK
   ```

3. Send another request with 3 extra custom headers so that the total number of headers exceeds the limit of 5. Verify that Envoy rejects the request with a 431 Request Header Fields Too Large response.

   {{< tabs items="Cloud Provider LoadBalancer,Port-forward for local testing" tabTotal="2" >}}
   {{% tab tabName="Cloud Provider LoadBalancer" %}}
   ```sh
   curl -v http://$INGRESS_GW_ADDRESS:8080/headers \
     -H "host: www.example.com:8080" \
     -H "x-custom-1: a" -H "x-custom-2: b" -H "x-custom-3: c"
   ```
   {{% /tab %}}
   {{% tab tabName="Port-forward for local testing" %}}
   ```sh
   curl -v localhost:8080/headers \
     -H "host: www.example.com:8080" \
     -H "x-custom-1: a" -H "x-custom-2: b" -H "x-custom-3: c"
   ```
   {{% /tab %}}
   {{< /tabs >}}

   Example output:
   ```console
   < HTTP/1.1 431 Request Header Fields Too Large
   ```

## Cleanup

{{< reuse "kgw-docs/snippets/cleanup.md" >}}

```sh
kubectl delete listenerpolicy max-headers-count -n {{< reuse "kgw-docs/snippets/namespace.md" >}}
```
