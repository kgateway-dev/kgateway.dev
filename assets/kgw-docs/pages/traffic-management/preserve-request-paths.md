## About path normalization and slash merging {#about}

By default, Envoy applies two transformations to a request path before it forwards the request to the backend.

* **Path normalization**: Envoy resolves the path per [RFC 3986](https://www.rfc-editor.org/rfc/rfc3986.html), for example by collapsing `.` and `..` segments and decoding percent-encoded characters.
* **Slash merging**: Envoy collapses sequences of adjacent `/` characters into a single `/`.

These defaults match Envoy's historical behavior and help guard against common path-based bypass techniques. However, some backends depend on the original, unmodified path. For example, S3-compatible object stores can use object keys that contain repeated slashes, such as `my-bucket//nested//key`. If Envoy merges these slashes before routing, the request no longer matches the intended object key.

Use a ListenerPolicy to disable path normalization, slash merging, or both, for the listeners on a Gateway.

## Before you begin {#prereqs}

{{< reuse "kgw-docs/snippets/prereq.md" >}}

## Disable path normalization and slash merging {#disable}

1. Create a ListenerPolicy that sets `normalizePath` and `mergeSlashes` to `false`. In `targetRefs`, attach the policy to the Gateway. The policy applies to all HTTP and HTTPS listeners on that Gateway.

   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.kgateway.dev/v1alpha1
   kind: ListenerPolicy
   metadata:
     name: preserve-path-handling
     namespace: {{< reuse "kgw-docs/snippets/namespace.md" >}}
   spec:
     targetRefs:
     - group: gateway.networking.k8s.io
       kind: Gateway
       name: http
     default:
       httpSettings:
         normalizePath: false
         mergeSlashes: false
   EOF
   ```

   {{< reuse "kgw-docs/snippets/review-table.md" >}}

   | Setting | Description |
   | --- | --- |
   | `spec.default.httpSettings.normalizePath` | Set to `false` to keep Envoy from normalizing paths before routing, such as collapsing `.` and `..` segments or decoding percent-encoded characters. Defaults to `true`. |
   | `spec.default.httpSettings.mergeSlashes` | Set to `false` to keep Envoy from merging adjacent `/` characters in request paths. Defaults to `true`. |

2. Port-forward the gateway proxy on port 19000 to open the Envoy admin interface, and verify that the HTTP connection manager config for the gateway listener no longer normalizes paths or merges slashes.
   ```sh
   kubectl port-forward deploy/http -n {{< reuse "kgw-docs/snippets/namespace.md" >}} 19000 &
   PF_PID=$!

   sleep 2

   curl -s localhost:19000/config_dump | jq '
     .configs[]
     | select(.["@type"] == "type.googleapis.com/envoy.admin.v3.ListenersConfigDump")
     | .dynamic_listeners[]
     | .active_state.listener.filter_chains[].filters[]
     | select(.name == "envoy.filters.network.http_connection_manager")
     | .typed_config
     | {normalize_path, merge_slashes}
   '

   kill $PF_PID
   ```

   Example output:
   ```console
   {
     "normalize_path": false,
     "merge_slashes": null
   }
   ```

   > [!NOTE]
   > `merge_slashes` shows as `null` rather than `false`. Envoy omits this field from the config dump entirely when it is set to its default value of `false`, so the `{normalize_path, merge_slashes}` object construction in the command above fills in `null` for the missing key. A `null` value confirms that slash merging is disabled. `normalize_path` always appears explicitly, including when it is `false`, because Envoy represents it as a wrapper type rather than a plain boolean.
   >
   > `.dynamic_listeners` contains only the Gateway-managed listener, so you don't need to filter by name or port. Use `.active_state`, not `.draining_state`, to see the current configuration instead of a previous version of the listener that Envoy is still closing out connections for after an update.

3. Send a request with a repeated slash in the path.

   {{< tabs >}}
   {{% tab name="Cloud Provider LoadBalancer" %}}
   ```sh
   curl -i http://$INGRESS_GW_ADDRESS:8080/anything/foo//bar -H "host: www.example.com:8080"
   ```
   {{% /tab %}}
   {{% tab name="Port-forward for local testing" %}}
   ```sh
   curl -i localhost:8080/anything/foo//bar -H "host: www.example.com"
   ```
   {{% /tab %}}
   {{< /tabs >}}

   Example output:
   ```console
   HTTP/1.1 301 Moved Permanently
   content-type: text/html; charset=utf-8
   location: /anything/foo/bar

   <a href="/anything/foo/bar">Moved Permanently</a>.
   ```

   > [!NOTE]
   > The 301 response comes from httpbin's underlying Werkzeug framework, which has its own, independent path normalization. Httpbin redirects any request with a repeated slash to the canonical single-slash path. This behavior only triggers if httpbin receives the raw, unmerged path with repeated slashes. If Envoy had merged the slashes before proxying the request, httpbin would receive the already-canonical path and return a normal 200 response with no redirect.

{{< version exclude-if="2.0.x,2.1.x,2.2.x,2.3.x,2.4.x" >}}
## Handle escaped slashes {#escaped-slashes}

Path normalization and slash merging do not change an escaped slash (`%2F`), because RFC 3986 treats `%2F` as data and not as a path separator. As a result, a request for `/anything/a%2Fb` reaches the backend unchanged. This can bypass your rules if the backend decodes `%2F` itself. For example, a route or policy that applies only to the path prefix `/internal/` does not match a request for `/internal%2Fsecret`, but a backend that decodes the path treats this request as `/internal/secret`.

To control how the proxy handles escaped slashes, set the `pathWithEscapedSlashesAction` field in the `httpSettings` of a ListenerPolicy. The field supports the following values.

| Value | Description |
| --- | --- |
| `KeepUnchanged` | Forward the request with the escaped slashes unchanged. |
| `RejectRequest` | Reject the request with a 400 response. |
| `UnescapeAndRedirect` | Replace each escaped slash with a slash, and send the client a 307 redirect to the new path. |
| `UnescapeAndForward` | Replace each escaped slash with a slash, and forward the request to the backend with the new path. The routing decision is made on the new path. |

If you do not set the field, Envoy keeps the escaped slashes unchanged, which is the same as `KeepUnchanged`. This default might change in a future version of Envoy.

1. Create a ListenerPolicy that rejects requests with escaped slashes in the path. In `targetRefs`, attach the policy to the Gateway. To use a different action, change the value of `pathWithEscapedSlashesAction`.

   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.kgateway.dev/v1alpha1
   kind: ListenerPolicy
   metadata:
     name: escaped-slashes
     namespace: {{< reuse "kgw-docs/snippets/namespace.md" >}}
   spec:
     targetRefs:
     - group: gateway.networking.k8s.io
       kind: Gateway
       name: http
     default:
       httpSettings:
         pathWithEscapedSlashesAction: RejectRequest
   EOF
   ```

   > [!NOTE]
   > To combine this setting with `normalizePath` or `mergeSlashes` from the previous section, add the field to the same ListenerPolicy.

2. Send a request with an escaped slash in the path.

   {{< tabs >}}
   {{% tab name="Cloud Provider LoadBalancer" %}}
   ```sh
   curl -i http://$INGRESS_GW_ADDRESS:8080/anything/a%2Fb -H "host: www.example.com:8080"
   ```
   {{% /tab %}}
   {{% tab name="Port-forward for local testing" %}}
   ```sh
   curl -i localhost:8080/anything/a%2Fb -H "host: www.example.com"
   ```
   {{% /tab %}}
   {{< /tabs >}}

   Example output:
   ```console
   HTTP/1.1 400 Bad Request
   ```

3. Change the action to `UnescapeAndRedirect`.

   ```sh
   kubectl patch listenerpolicy escaped-slashes -n {{< reuse "kgw-docs/snippets/namespace.md" >}} --type=merge \
     -p '{"spec":{"default":{"httpSettings":{"pathWithEscapedSlashesAction":"UnescapeAndRedirect"}}}}'
   ```

4. Send the request with the escaped slash again. The proxy responds with a redirect to the path that has the escaped slash replaced.

   {{< tabs >}}
   {{% tab name="Cloud Provider LoadBalancer" %}}
   ```sh
   curl -i http://$INGRESS_GW_ADDRESS:8080/anything/a%2Fb -H "host: www.example.com:8080"
   ```
   {{% /tab %}}
   {{% tab name="Port-forward for local testing" %}}
   ```sh
   curl -i localhost:8080/anything/a%2Fb -H "host: www.example.com"
   ```
   {{% /tab %}}
   {{< /tabs >}}

   Example output:
   ```console
   HTTP/1.1 307 Temporary Redirect
   location: /anything/a/b
   ```
{{< /version >}}

## Cleanup {#cleanup}

{{< reuse "kgw-docs/snippets/cleanup.md" >}}

```sh
kubectl delete listenerpolicy preserve-path-handling -n {{< reuse "kgw-docs/snippets/namespace.md" >}} --ignore-not-found
{{< version exclude-if="2.0.x,2.1.x,2.2.x,2.3.x,2.4.x" >}}kubectl delete listenerpolicy escaped-slashes -n {{< reuse "kgw-docs/snippets/namespace.md" >}} --ignore-not-found{{< /version >}}
```
