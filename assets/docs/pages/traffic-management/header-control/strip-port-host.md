When a downstream client includes a port number in the `Host` or `authority` header, such as `www.example.com:9999`, the port is forwarded to the upstream backend by default. Some upstream services do not accept ports in the `Host` header and might reject or mishandle such requests. Use the `stripHostPortMode` field in a ListenerPolicy to configure your gateway proxy to strip the port from the `Host` header before forwarding the request.

Note that the `stripHostPortMode` field only affects requests where the client explicitly sends a port in the `Host` header. If the client does not include a port, the header is forwarded unchanged regardless of this setting.

## Supported modes {#about}

You can configure the following port stripping behaviors.

| Mode | Description |
|---|---|
| `AnyPort` | Strips the port from the `Host` header unconditionally, regardless of what port the client sent. For example, a `Host` header of `www.example.com:9999` becomes `www.example.com`. |
| `MatchingPort` | Strips the port only when it matches the listener's own port. For example, if the listener is exposed on port 8080 and the client sends the `www.example.com:8080` header, the port is stripped. If the client sends `www.example.com:9999`, the port is preserved. |

## Before you begin

{{< reuse "docs/snippets/prereq.md" >}}

## Strip any port {#strip-any-port}

Use the `AnyPort` setting to strip any port from the `Host` header, regardless of its value. For example, a `Host` header of `www.example.com:443` becomes `www.example.com`.

1. Send a request to the httpbin app and include a port number in the `Host` header. Verify that you see the port included in the `Host` header of your response. 

   {{< tabs items="Cloud Provider LoadBalancer,Port-forward for local testing" tabTotal="2" >}}
   {{% tab tabName="Cloud Provider LoadBalancer" %}}
   ```sh
   curl -v http://$INGRESS_GW_ADDRESS:8080/headers -H "host: www.example.com:9999"
   ```
   {{% /tab %}}
   {{% tab tabName="Port-forward for local testing" %}}
   ```sh
   curl -v localhost:8080/headers -H "host: www.example.com:9999"
   ```
   {{% /tab %}}
   {{< /tabs >}}

   Example output: 

   ```console {hl_lines=[7]}
   {
     "headers": {
       "Accept": [
         "*/*"
       ],
       "Host": [
         "www.example.com:9999"
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
         "03f7152b-0546-4080-b7cb-43a4c64b0d2a"
       ]
     }
   }
   ```

2. Create a ListenerPolicy with the `stripHostPortMode: AnyPort` setting.

   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.kgateway.dev/v1alpha1
   kind: ListenerPolicy
   metadata:
     name: strip-host-port
     namespace: {{< reuse "docs/snippets/namespace.md" >}}
   spec:
     targetRefs:
     - group: gateway.networking.k8s.io
       kind: Gateway
       name: http
     default:
       httpSettings:
         stripHostPortMode: AnyPort
   EOF
   ```

   {{< reuse "docs/snippets/review-table.md" >}} For more information about the available fields, see the [API reference]({{< link-hextra path="/reference/api/#httplistenerpolicyspec" >}}).

   | Setting | Description |
   |---|---|
   | `spec.targetRefs` | The Gateway this policy applies to. |
   | `spec.default.httpSettings.stripHostPortMode` | How Envoy strips the port from the `Host`/`authority` header. In this example, the `AnyPort` setting is used that removes any port that the client sends as part of the request. |

3. Send another request to the httpbin app. Verify that this time, port 9999 is not returned in the `Host` header. 
   {{< tabs items="Cloud Provider LoadBalancer,Port-forward for local testing" tabTotal="2" >}}
   {{% tab tabName="Cloud Provider LoadBalancer" %}}
   ```sh
   curl -v http://$INGRESS_GW_ADDRESS:8080/headers -H "host: www.example.com:9999"
   ```
   {{% /tab %}}
   {{% tab tabName="Port-forward for local testing" %}}
   ```sh
   curl -v localhost:8080/headers -H "host: www.example.com:9999"
   ```
   {{% /tab %}}
   {{< /tabs >}}

   Example output: 

   ```console {hl_lines=[7]}
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
         "03f7152b-0546-4080-b7cb-43a4c64b0d2a"
       ]
     }
   }
   ```

## Strip listener ports only {#strip-matching-port}

Use the `MatchingPort` setting to strip the port only when it matches the listener's own port. Ports that do not match the listener port are preserved in the header and forwarded to the upstream backend.

1. Review the port settings on your Gateway. The Gateway in this example has a listener on port 8080. 
   ```sh
   kubectl get gateway http -n {{< reuse "docs/snippets/namespace.md" >}} -o yaml
   ```

   Example output: 
   ```console {hl_lines=[16]}
   apiVersion: gateway.networking.k8s.io/v1
   kind: Gateway
   metadata:
     generation: 1
     name: http
     namespace: kgateway-system
     resourceVersion: "768"
     uid: 6dba42be-3e96-4616-a56a-267f0f01a207
   spec:
    gatewayClassName: kgateway
     listeners:
     - allowedRoutes:
         namespaces:
           from: All
       name: http
       port: 8080
       protocol: HTTP
   ...
   ```

2. Create or update the ListenerPolicy to enable port stripping when a client sends a port in the `Host` header that matches the listener's port. 
   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.kgateway.dev/v1alpha1
   kind: ListenerPolicy
   metadata:
     name: strip-host-port
     namespace: {{< reuse "docs/snippets/namespace.md" >}}
   spec:
     targetRefs:
     - group: gateway.networking.k8s.io
       kind: Gateway
       name: http
     default:
       httpSettings:
         stripHostPortMode: MatchingPort
   EOF
   ```

   {{< reuse "docs/snippets/review-table.md" >}} For more information about the available fields, see the [API reference]({{< link-hextra path="/reference/api/#httplistenerpolicyspec" >}}).

   | Setting | Description |
   |---|---|
   | `spec.targetRefs` | The Gateway this policy applies to. |
   | `spec.default.httpSettings.stripHostPortMode` | How Envoy strips the port from the `Host`/`authority` header. In this example, the `MatchingPort` setting is used that removes a port only if it matches the listener's own port.  |

3. Send a request to the httpbin app and include the listener port in the `Host` header. Verify that the port is removed from the `Host` header. 

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

   ```console {hl_lines=[7]}
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
   ...
   ```

4. Send another request to the httpbin app. This time, you include a port in the `Host` header that does not match the listener port, such as `9999`. Verify that the port is not removed from the `Host` header.
   {{< tabs items="Cloud Provider LoadBalancer,Port-forward for local testing" tabTotal="2" >}}
   {{% tab tabName="Cloud Provider LoadBalancer" %}}
   ```sh
   curl -v http://$INGRESS_GW_ADDRESS:8080/headers -H "host: www.example.com:9999"
   ```
   {{% /tab %}}
   {{% tab tabName="Port-forward for local testing" %}}
   ```sh
   curl -v localhost:8080/headers -H "host: www.example.com:9999"
   ```
   {{% /tab %}}
   {{< /tabs >}}

   Example output: 

   ```console {hl_lines=[7]}
   {
     "headers": {
       "Accept": [
         "*/*"
       ],
       "Host": [
         "www.example.com:9999"
       ],
       "User-Agent": [
         "curl/8.7.1"
       ],
   ...
   ```

## Cleanup

{{< reuse "docs/snippets/cleanup.md" >}}

```sh
kubectl delete listenerpolicy strip-host-port -n {{< reuse "docs/snippets/namespace.md" >}}
```

