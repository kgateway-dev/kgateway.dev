Set the maximum total size of the headers that Envoy accepts on incoming requests.

By default, Envoy accepts request headers with a total size of up to 60 KiB. When a request exceeds the limit, Envoy rejects the request before it reaches your upstream services. Envoy returns a `431 Request Header Fields Too Large` response for HTTP/1.x connections and resets the stream for HTTP/2 connections.

You might want to change the limit in the following cases:

- **Lower the limit** to protect your backends from oversized requests and to limit header-based attack vectors.
- **Raise the limit** for clients that send large headers, such as large cookies or tokens. Note that your backends might enforce their own header size limits. You can tell where a `431` response comes from by its headers: a `431` response from a backend includes the `x-envoy-upstream-service-time` header, but a `431` response from the gateway proxy does not.

> [!NOTE]
> The limit applies to the total size of all request headers, including the names and values of headers that HTTP clients add automatically. For example, curl always sends the `Host`, `User-Agent`, and `Accept` headers. To limit the number of headers instead of their size, see [Limit request header count]({{< link-hextra path="/traffic-management/header-control/max-headers-count/" >}}).

## Before you begin

{{< reuse "kgw-docs/snippets/prereq.md" >}}

## Set a maximum header size {#set-max-request-headers-kb}

1. Create a ListenerPolicy with the `maxRequestHeadersKb` setting. This example sets a low limit of 1 KiB so that you can test it with a single large header.

   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.kgateway.dev/v1alpha1
   kind: ListenerPolicy
   metadata:
     name: max-request-headers-size
     namespace: {{< reuse "kgw-docs/snippets/namespace.md" >}}
   spec:
     targetRefs:
     - group: gateway.networking.k8s.io
       kind: Gateway
       name: http
     default:
       httpSettings:
         maxRequestHeadersKb: 1
   EOF
   ```

   {{< reuse "kgw-docs/snippets/review-table.md" >}} For more information about the available fields, see the [API reference]({{< link-hextra path="/reference/api/#httpsettings" >}}).

   | Setting | Description |
   |---|---|
   | `spec.targetRefs` | The Gateway that this policy applies to. The policy applies to all HTTP and HTTPS listeners on the Gateway. |
   | `spec.default.httpSettings.maxRequestHeadersKb` | The maximum total size of request headers in KiB. Requests that exceed this limit receive a `431` response for HTTP/1.x and a stream reset for HTTP/2 connections. Must be between `1` and `8192`. If unset, Envoy's default of `60` KiB is used. |

2. Send a request to the httpbin app with a 500-byte header. The total size of the request headers is under the limit of 1 KiB. Verify that you get back a 200 HTTP response code.

   {{< tabs >}}
   {{% tab name="Cloud Provider LoadBalancer" %}}
   ```sh
   curl -i http://$INGRESS_GW_ADDRESS:8080/headers -H "host: www.example.com" \
     -H "x-large-header: $(head -c 500 /dev/zero | tr '\0' a)"
   ```
   {{% /tab %}}
   {{% tab name="Port-forward for local testing" %}}
   ```sh
   curl -i localhost:8080/headers -H "host: www.example.com" \
     -H "x-large-header: $(head -c 500 /dev/zero | tr '\0' a)"
   ```
   {{% /tab %}}
   {{< /tabs >}}

   Example output:
   ```console
   HTTP/1.1 200 OK
   ...
   ```

3. Send another request with a 2,000-byte header so that the total size of the request headers exceeds the limit of 1 KiB. Verify that the gateway proxy rejects the request with a `431 Request Header Fields Too Large` response.

   {{< tabs >}}
   {{% tab name="Cloud Provider LoadBalancer" %}}
   ```sh
   curl -i http://$INGRESS_GW_ADDRESS:8080/headers -H "host: www.example.com" \
     -H "x-large-header: $(head -c 2000 /dev/zero | tr '\0' a)"
   ```
   {{% /tab %}}
   {{% tab name="Port-forward for local testing" %}}
   ```sh
   curl -i localhost:8080/headers -H "host: www.example.com" \
     -H "x-large-header: $(head -c 2000 /dev/zero | tr '\0' a)"
   ```
   {{% /tab %}}
   {{< /tabs >}}

   Example output: The response does not include the `x-envoy-upstream-service-time` header, because the gateway proxy rejects the request before it forwards it to the httpbin app.
   ```console
   HTTP/1.1 431 Request Header Fields Too Large
   content-length: 31
   content-type: text/plain
   date: Wed, 11 Nov 2026 16:19:26 GMT
   server: envoy
   connection: close

   Request Header Fields Too Large
   ```

## Cleanup

{{< reuse "kgw-docs/snippets/cleanup.md" >}}

```sh
kubectl delete listenerpolicy max-request-headers-size -n {{< reuse "kgw-docs/snippets/namespace.md" >}} --ignore-not-found
```
