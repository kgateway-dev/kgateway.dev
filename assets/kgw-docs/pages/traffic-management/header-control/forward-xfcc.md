The `x-forwarded-client-cert` (XFCC) header carries information about the client certificate that is used to establish a connection to the gateway proxy. Upstream backends can read this header to identify the original caller without terminating mTLS themselves.

By default, Envoy removes the XFCC header from every request before forwarding it upstream, regardless of whether the connection uses mTLS or plain HTTP. You can change this behavior and instead forward this information to the backend by configuring the `forwardClientCertDetails` field in the ListenerPolicy resource. 

## Supported modes {#about}

The following modes are supported to configure the XFCC header. Note that most modes only apply to an mTLS gateway listener and have no effect on other listener types. 

| Mode | Description |
|---|---|
| `Sanitize` | Remove the XFCC header unconditionally. This setting is the default in Envoy. |
| `ForwardOnly` | Forward the XFCC header unchanged. Applies only to mTLS gateway listeners. |
| `AppendForward` | Append the current client certificate details to the existing XFCC header. Applies only to mTLS gateway listeners. |
| `SanitizeSet` | Remove the current XFCC header and replace it with the details of the certificate that was used during the TLS handshake. Applies only to mTLS gateway listeners.  |
| `AlwaysForwardOnly` | Forward the XFCC header unchanged, even on non-mTLS connections. |

When you set the mode to `AppendForward` or `SanitizeSet`, you can use the `details` field to select what fields from the downstream client certificate you want to include into the XFCC header. 

| Detail field | Description |
|---|---|
| `subject` | The certificate Subject. |
| `cert` | The entire client certificate in URL-encoded PEM format. |
| `chain` | The entire client certificate chain in URL-encoded PEM format. |
| `dns` | DNS-type Subject Alternative Names from the certificate. |
| `uri` | The URI-type Subject Alternative Name from the certificate. |

## Before you begin

{{< reuse "kgw-docs/snippets/prereq.md" >}}

## Forward the XFCC headers {#always-forward}

Use `AlwaysForwardOnly` to forward an existing XFCC header to the upstream backend on any connection type, including plain HTTP. This is useful when the header was set by a trusted component in the request chain, such as a Load Balancer or another proxy, and you want to preserve it for your backend services.

1. Send a request to the httpbin app with an XFCC header. Verify that you do not see the XFCC header in your response. 

   {{< tabs >}}
   {{% tab name="Cloud Provider LoadBalancer" %}}
   ```sh
   curl -s http://$INGRESS_GW_ADDRESS:8080/headers \
     -H "host: www.example.com:8080" \
     -H "x-forwarded-client-cert: By=spiffe://cluster.local/ns/default/sa/backend;Hash=abc123"
   ```
   {{% /tab %}}
   {{% tab name="Port-forward for local testing" %}}
   ```sh
   curl -s localhost:8080/headers \
     -H "host: www.example.com" \
     -H "x-forwarded-client-cert: By=spiffe://cluster.local/ns/default/sa/backend;Hash=abc123"
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
       ],
       "X-Request-Id": [
         "00f85e6a-eb80-4b84-81e7-1b6ffd1eda4b"
       ]
     }
   }
   ```

2. Create a ListenerPolicy resource that sets `forwardClientCertDetails.mode: AlwaysForwardOnly`. This mode forwards the XFCC header for all requests.

   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.kgateway.dev/v1alpha1
   kind: ListenerPolicy
   metadata:
     name: forward-xfcc
     namespace: {{< reuse "kgw-docs/snippets/namespace.md" >}}
   spec:
     targetRefs:
     - group: gateway.networking.k8s.io
       kind: Gateway
       name: http
     default:
       httpSettings:
         forwardClientCertDetails:
           mode: AlwaysForwardOnly
   EOF
   ```

   {{< reuse "kgw-docs/snippets/review-table.md" >}} For more information about the available fields, see the [API reference]({{< link-hextra path="/reference/api/#forwardclientcertdetails" >}}).

   | Setting | Description |
   |---|---|
   | `spec.targetRefs` | The Gateway this policy applies to. |
   | `spec.default.httpSettings.forwardClientCertDetails.mode` | How Envoy handles the XFCC header. `AlwaysForwardOnly` forwards the header as-is on all connection types. |

3. Send the same request again. Verify that the upstream now receives the XFCC header.

   {{< tabs >}}
   {{% tab name="Cloud Provider LoadBalancer" %}}
   ```sh
   curl -s http://$INGRESS_GW_ADDRESS:8080/headers \
     -H "host: www.example.com:8080" \
     -H "x-forwarded-client-cert: By=spiffe://cluster.local/ns/default/sa/backend;Hash=abc123"
   ```
   {{% /tab %}}
   {{% tab name="Port-forward for local testing" %}}
   ```sh
   curl -s localhost:8080/headers \
     -H "host: www.example.com" \
     -H "x-forwarded-client-cert: By=spiffe://cluster.local/ns/default/sa/backend;Hash=abc123"
   ```
   {{% /tab %}}
   {{< /tabs >}}

   Example output: The `X-Forwarded-Client-Cert` header is now present and forwarded to the upstream backend.

   ```console {hl_lines=[18,19]}
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
       "X-Forwarded-Client-Cert": [
         "By=spiffe://cluster.local/ns/default/sa/backend;Hash=abc123"
       ],
       "X-Forwarded-For": [
         "10.244.0.7"
       ],
       "X-Forwarded-Proto": [
         "http"
       ],
       "X-Request-Id": [
         "2d032a53-940a-4de8-a3a5-9510afede31d"
       ]
     }
   }
   ```

## Other configurations {#other}

Review other common configuration examples. 

### Forward XFCC on mTLS connections {#forward-only}

Use `ForwardOnly` to pass the existing XFCC header from the client to the upstream without modification. 

> [!NOTE]
> This configuration can only be applied to an mTLS gateway listener. On a plain HTTP listener, this mode has no effect and the header is stripped.

```yaml
kubectl apply -f- <<EOF
apiVersion: gateway.kgateway.dev/v1alpha1
kind: ListenerPolicy
metadata:
  name: forward-xfcc
  namespace: {{< reuse "kgw-docs/snippets/namespace.md" >}}
spec:
  targetRefs:
  - group: gateway.networking.k8s.io
    kind: Gateway
    name: http
  default:
    httpSettings:
      forwardClientCertDetails:
        mode: ForwardOnly
EOF
```

### Append client certificate details {#append-forward}

Use `AppendForward` to keep any XFCC header that is already present in the request and append a new entry with details from the current downstream client certificate. This is useful in multi-hop proxy chains where you want each hop to add its own identity without discarding previous entries. 

> [!NOTE]
> This configuration can only be applied to an mTLS gateway listener. On a plain HTTP listener, this mode has no effect and the header is stripped.

```yaml
kubectl apply -f- <<EOF
apiVersion: gateway.kgateway.dev/v1alpha1
kind: ListenerPolicy
metadata:
  name: forward-xfcc
  namespace: {{< reuse "kgw-docs/snippets/namespace.md" >}}
spec:
  targetRefs:
  - group: gateway.networking.k8s.io
    kind: Gateway
    name: http
  default:
    httpSettings:
      forwardClientCertDetails:
        mode: AppendForward
        details:
          subject: true
          uri: true
EOF
```

### Sanitize the XFCC header {#sanitize-set}

Use `SanitizeSet` to remove any XFCC header that the client sent and replace it with a new one that the gateway proxy builds from the actual client certificate that is used in the mTLS handshake. The upstream receives a trustworthy header that the proxy generated, and not a header that the client might have forged. Use the `details` field to control the information that you want to include in the header. 

> [!NOTE]
> This configuration can only be applied to an mTLS gateway listener. On a plain HTTP listener, this mode has no effect and the header is stripped.

In the following example, you include the subject, DNS, and URI fields from the certificate.

```yaml
kubectl apply -f- <<EOF
apiVersion: gateway.kgateway.dev/v1alpha1
kind: ListenerPolicy
metadata:
  name: forward-xfcc
  namespace: {{< reuse "kgw-docs/snippets/namespace.md" >}}
spec:
  targetRefs:
  - group: gateway.networking.k8s.io
    kind: Gateway
    name: http
  default:
    httpSettings:
      forwardClientCertDetails:
        mode: SanitizeSet
        details:
          subject: true
          dns: true
          uri: true
EOF
```

## Cleanup

{{< reuse "kgw-docs/snippets/cleanup.md" >}}

```sh
kubectl delete listenerpolicy forward-xfcc -n {{< reuse "kgw-docs/snippets/namespace.md" >}}
```

