Configure your gateway proxy to accept older HTTP protocols.

## About HTTP/1.0 and HTTP/0.9

By default, Envoy-based gateway proxies return a 426 Upgrade Required HTTP response code for HTTP/1.0 and HTTP/0.9 requests. HTTP/0.9 was a simple, rudimentary protocol that was introduced in 1991 and supported only the `GET` HTTP method. Other methods, such as `POST`, `PUT`, and `DELETE` were later introduced in HTTP/1.0.

Both protocol versions are rarely used nowadays. However, some applications might still require support for these versions for backwards compatibility. To allow the gateway proxy to accept these types of requests, you can create a ListenerPolicy and attach it to your Gateway.

## Before you begin

{{< reuse "kgw-docs/snippets/prereq-listeners.md" >}}

## Set up HTTP 1.0 support


1. Create a ListenerPolicy with the `acceptHttp10` field. In the `targetRefs`, attach the policy to the Gateway that you want to support the HTTP/1.0 protocol.

   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.kgateway.dev/v1alpha1
   kind: ListenerPolicy
   metadata:
     name: accept-http10
     namespace: {{< reuse "kgw-docs/snippets/namespace.md" >}}
   spec:
     targetRefs:
     - group: gateway.networking.k8s.io
       kind: Gateway
       name: http
     default:
       httpSettings:
         acceptHttp10: true
   EOF
   ```

2. Port-forward the gateway proxy on port 19000 to open the Envoy admin interface.
   ```sh
   kubectl port-forward deploy/http -n {{< reuse "kgw-docs/snippets/namespace.md" >}} 19000
   ```

3. Extract the `http_protocol_options` filter in your Envoy filter chain and verify that the `accept_http_10` field is set to `true`. Alternatively, you can open the [Envoy admin interface](http://localhost:19000/config_dump) and look for this setting in the config dump. 
   ```sh
   curl -s localhost:19000/config_dump | jq '[.. | objects | select(has("http_protocol_options")) | {http_protocol_options}]'
   ```

   Example output:
   ```console
   "http_protocol_options": {
             "accept_http_10": true
      }
   ```

{{< version exclude-if="2.3.x,2.2.x,2.1.x" >}}
## Preserve request paths

By default, Envoy normalizes request paths and merges adjacent slashes before it routes a request. These defaults preserve earlier {{< reuse "kgw-docs/snippets/kgateway.md" >}} behavior. Some backends, such as S3-compatible object stores, need the original path because object keys can contain repeated slashes.

Create a ListenerPolicy that disables path normalization, slash merging, or both. In `targetRefs`, attach the policy to the Gateway. The policy applies to the Gateway's HTTP and HTTPS listeners.

```yaml
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
```

{{< reuse "kgw-docs/snippets/review-table.md" >}}

| Setting | Description |
| --- | --- |
| `spec.default.httpSettings.normalizePath` | Set to `false` to keep Envoy from normalizing paths before routing, such as collapsing `.` and `..` segments or decoding percent-encoded characters. Defaults to `true`. |
| `spec.default.httpSettings.mergeSlashes` | Set to `false` to keep Envoy from merging adjacent `/` characters in request paths. Defaults to `true`. |

{{< /version >}}

## Cleanup

{{< reuse "kgw-docs/snippets/cleanup.md" >}}

```sh
kubectl delete listenerpolicy accept-http10 -n {{< reuse "kgw-docs/snippets/namespace.md" >}}
```
