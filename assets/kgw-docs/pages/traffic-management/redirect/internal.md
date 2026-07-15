Configure the gateway proxy to follow upstream HTTP redirect responses (3xx) on behalf of the client. Instead of returning the redirect to the client, the proxy resolves it internally and returns only the final response.

## About internal redirects

By default, when an upstream backend returns a 3xx redirect response, the gateway forwards it to the client and the client must follow the redirect itself. With internal redirects enabled, the gateway proxy reads the `Location` header from the upstream's redirect response and sends a new request to that URL on behalf of the client. The client receives only the final response and never sees the intermediate redirect.

Internal redirects are configured in the {{< reuse "kgw-docs/snippets/trafficpolicy.md" >}} resource. The following configuration options are available. 

| Field | Type | Default | Description |
|---|---|---|---|
| `redirectResponseCodes` | `[]integer` | `[302]` | HTTP response codes that trigger an internal redirect. Valid values: `301`, `302`, `303`, `307`, `308`. Specify 1–5 unique codes. |
| `maxRedirects` | `integer` | `1` | Maximum number of internal redirects to follow for a single downstream request. |
| `allowCrossSchemeRedirect` | `boolean` | `false` | Allow the gateway to follow redirects that change the scheme, for example HTTP to HTTPS. |
| `responseHeadersToCopy` | `[]string` | — | Response headers from the redirect response to copy to the outgoing redirected request. Specify 1–16 unique header names. |

> [!NOTE]
> The redirect target URL in the upstream's `Location` header must be an absolute URL, such as `http://www.example.com/anything/redirected`. Relative location headers, such as `/get` are not followed. The redirect target must also match a route in the gateway's route table.

> [!NOTE]
> Internal redirects apply only to routes that forward traffic to a backend. They have no effect on routes that use a redirect or direct response filter.

## Before you begin

{{< reuse "kgw-docs/snippets/prereq.md" >}}

## Follow upstream redirects

Use a {{< reuse "kgw-docs/snippets/trafficpolicy.md" >}} to configure internal redirect behavior for an HTTPRoute.

1. Send a request to the `/redirect-to` path of the httpbin app. Use the `url` query parameter to specify an absolute redirect target on the same host, and `status_code` to set the redirect response code. Verify that you get back a 302 HTTP response with a `location` header that points to the redirect target.

   {{< tabs >}}
   {{% tab name="Cloud Provider LoadBalancer" %}}
   ```sh
   curl -vi "http://$INGRESS_GW_ADDRESS:8080/redirect-to?url=http://www.example.com/anything/redirected&status_code=302" -H "host: www.example.com"
   ```
   {{% /tab %}}
   {{% tab name="Port-forward for local testing" %}}
   ```sh
   curl -vi "localhost:8080/redirect-to?url=http://www.example.com/anything/redirected&status_code=302" -H "host: www.example.com"
   ```
   {{% /tab %}}
   {{< /tabs >}}

   Example output:
   ```console {hl_lines=[2,3,8,9]}
   * Request completely sent off
   < HTTP/1.1 302 Found
   HTTP/1.1 302 Found
   < access-control-allow-credentials: true
   access-control-allow-credentials: true
   < access-control-allow-origin: *
   access-control-allow-origin: *
   < location: http://www.example.com/anything/redirected
   location: http://www.example.com/anything/redirected
   ...
   ```

2. Create the {{< reuse "kgw-docs/snippets/trafficpolicy.md" >}} that follows 302 redirects from the upstream. The policy targets the `httpbin` HTTPRoute that you set up as part of the prerequisites.

   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: {{< reuse "kgw-docs/snippets/trafficpolicy-apiversion.md" >}}
   kind: {{< reuse "kgw-docs/snippets/trafficpolicy.md" >}}
   metadata:
     name: internal-redirect
     namespace: httpbin
   spec:
     targetRefs:
     - group: gateway.networking.k8s.io
       kind: HTTPRoute
       name: httpbin
     internalRedirect: {}
   EOF
   ```

   {{< reuse "kgw-docs/snippets/review-table.md" >}} For more information, see the [API docs]({{< link-hextra path="/reference/api/#internalredirect" >}}).

   | Field | Description |
   |---|---|
   | `targetRefs` | The policy targets the `httpbin` HTTPRoute resource that you created as part of the prerequisites. |
   | `internalRedirect` | Enables internal redirect with default settings (follow `302` responses, maximum 1 redirect). |

3. Repeat the request. Verify that the gateway now follows the redirect on your behalf and returns a 200 HTTP response with the body from the `/anything/redirected` redirect path. 

   {{< tabs >}}
   {{% tab name="Cloud Provider LoadBalancer" %}}
   ```sh
   curl -vi "http://$INGRESS_GW_ADDRESS:8080/redirect-to?url=http://www.example.com/anything/redirected&status_code=302" -H "host: www.example.com"
   ```
   {{% /tab %}}
   {{% tab name="Port-forward for local testing" %}}
   ```sh
   curl -vi "localhost:8080/redirect-to?url=http://www.example.com/anything/redirected&status_code=302" -H "host: www.example.com"
   ```
   {{% /tab %}}
   {{< /tabs >}}

   Example output:
   ```console
   HTTP/1.1 200 OK
   ...
   {
     "method": "GET",
     "url": "http://www.example.com/anything/redirected",
     ...
   }
   ```

## Configure redirect options

The following example configures the gateway to follow `302` and `303` redirects, copy the `access-control-allow-credentials` header from the redirect response to the follow-up request, and allow a maximum of 3 consecutive redirects.

1. Update the {{< reuse "kgw-docs/snippets/trafficpolicy.md" >}} resource with additional redirect options.

   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: {{< reuse "kgw-docs/snippets/trafficpolicy-apiversion.md" >}}
   kind: {{< reuse "kgw-docs/snippets/trafficpolicy.md" >}}
   metadata:
     name: internal-redirect
     namespace: httpbin
   spec:
     targetRefs:
     - group: gateway.networking.k8s.io
       kind: HTTPRoute
       name: httpbin
     internalRedirect:
       redirectResponseCodes: [302, 303]
       maxRedirects: 3
       responseHeadersToCopy:
       - access-control-allow-credentials
   EOF
   ```

   | Field | Description |
   |---|---|
   | `redirectResponseCodes` | The gateway follows `302` and `303` redirect responses from the upstream. |
   | `maxRedirects` | The gateway follows up to 3 consecutive redirects per downstream request. If the chain exceeds this limit, the last redirect response is returned to the client. |
   | `responseHeadersToCopy` | The `access-control-allow-credentials` header from the redirect response is copied to the follow-up request sent to the redirect target. |

2. Send a request that triggers a `303` redirect. Verify that the gateway follows it and returns a 200 response. Check the `headers` section in the response body and confirm that `Access-Control-Allow-Credentials` is present, which proves it was copied from the redirect response to the follow-up request.

   {{< tabs >}}
   {{% tab name="Cloud Provider LoadBalancer" %}}
   ```sh
   curl -vi "http://$INGRESS_GW_ADDRESS:8080/redirect-to?url=http://www.example.com/anything/redirected&status_code=303" -H "host: www.example.com"
   ```
   {{% /tab %}}
   {{% tab name="Port-forward for local testing" %}}
   ```sh
   curl -vi "localhost:8080/redirect-to?url=http://www.example.com/anything/redirected&status_code=303" -H "host: www.example.com"
   ```
   {{% /tab %}}
   {{< /tabs >}}

   Example output:
   ```console {hl_lines=[5,6,13,17]}
   HTTP/1.1 200 OK
   ...
   {
     "headers": {
       "Access-Control-Allow-Credentials": [
         "true"
       ],
       "Host": [
         "www.example.com"
       ],
       ...
       "X-Envoy-Original-Url": [
         "http://www.example.com/redirect-to?url=http://www.example.com/anything/redirected&status_code=303"
       ],
       ...
     },
     "url": "http://www.example.com/anything/redirected",
     ...
   }
   ```

   
## Cleanup

{{< reuse "kgw-docs/snippets/cleanup.md" >}}

```sh
kubectl delete {{< reuse "kgw-docs/snippets/trafficpolicy.md" >}} internal-redirect -n httpbin
```
