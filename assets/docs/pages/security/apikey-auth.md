[API keys](https://en.wikipedia.org/wiki/Application_programming_interface_key) are secure, long-lived UUIDs that clients provide when they send a request to your service. You might use API keys in the following scenarios:
* You know the set of users that need access to your service. These users do not change often, or you have automation that easily generates or deletes the API key when the users do change. 
* You want direct control over how the credentials are generated and expire.

{{< callout type="warning" >}}
When you use API keys, your services are only as secure as the API keys. Storing and rotating the API key securely is up to the user.
{{< /callout >}}

## API key auth in kgateway

The kgateway proxy comes with built-in API key auth support via the {{< reuse "docs/snippets/trafficpolicy.md" >}} resource. To secure your services with API keys, first provide your kgateway proxy with your API keys in the form of Kubernetes secrets. Then in the {{< reuse "docs/snippets/trafficpolicy.md" >}} resource, you refer to the secrets in one of two ways.

* Specify a **label selector** that matches the label of one or more API key secrets. Labels are the more flexible, scalable approach.
* Refer to the **name and namespace** of each secret.

The proxy matches a request to a route that is secured by the external auth policy. The request must have a valid API key in the `api-key` header to be accepted. You can configure the name of the expected header. If the header is missing, or the API key is invalid, the proxy denies the request and returns a `401` response. 

The following diagram illustrates the flow: 

```mermaid
sequenceDiagram
    participant C as Client / Agent
    participant AGW as Kgateway Proxy
    participant K8s as K8s Secrets<br/>(API Keys)
    participant Backend as Backend

    C->>AGW: POST /api<br/>(no api-key header)

    AGW->>AGW: API key auth check:<br/>No API key found

    AGW-->>C: 401 Unauthorized<br/>"no API Key found"

    Note over C,Backend: Retry with API key

    C->>AGW: POST /api<br/>api-key: Bearer N2YwMDIx...

    AGW->>K8s: Lookup referenced secret<br/>(by name or label selector)
    K8s-->>AGW: Secret found

    AGW->>AGW: Compare API key from<br/>request header vs secret

    alt mode: Strict — Key valid
        AGW->>Backend: Forward request
        Backend-->>AGW: Response
        AGW-->>C: 200 OK + Response
    else Key invalid or missing
        AGW-->>C: 401 Unauthorized
    end
```

## Before you begin

{{< reuse "docs/snippets/prereq.md" >}}

## Set up API key auth

Store your API keys in a Kubernetes secret so that you can reference it in an {{< reuse "docs/snippets/trafficpolicy.md" >}} resource. 

1. From your API management tool, generate an API key. The examples in this guide use `N2YwMDIxZTEtNGUzNS1jNzgzLTRkYjAtYjE2YzRkZGVmNjcy`.

2. Create a Kubernetes secret to store your API key. 

   ```yaml 
   kubectl apply -f - <<EOF
   apiVersion: v1
   kind: Secret
   metadata:
     name: apikey
     namespace: {{< reuse "docs/snippets/namespace.md" >}}
     labels:
       app: httpbin
   type: extauth.solo.io/apikey
   stringData:
     api-key: N2YwMDIxZTEtNGUzNS1jNzgzLTRkYjAtYjE2YzRkZGVmNjcy
   EOF
   ```

3. Verify that the secret is created. Note that the `data.api-key` value is base64 encoded. 
   
   ```sh
   kubectl get secret apikey -n {{< reuse "docs/snippets/namespace.md" >}} -o yaml
   ```

4. Create an {{< reuse "docs/snippets/trafficpolicy.md" >}} resource that configures API key authentication for all routes that the Gateway serves and reference the `apikey` secret that you created earlier. The following example uses the `Strict` validation mode, which requires requests to include a valid `Authorization` header to be authenticated successfully. For other common configuration examples, see [Other configuration examples](#other-configuration-examples).  
   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: {{< reuse "docs/snippets/trafficpolicy-apiversion.md" >}}
   kind: {{< reuse "docs/snippets/trafficpolicy.md" >}}
   metadata:
     name: apikey-auth
     namespace: {{< reuse "docs/snippets/namespace.md" >}}
   spec:
     targetRefs:
       - group: gateway.networking.k8s.io
         kind: Gateway
         name: http
     apiKeyAuth:
       secretRef:
         name: apikey
   EOF
   ```

5. Send a request to the httpbin app without an API key. Verify that the request fails with a 401 HTTP response code. 
   
   {{< tabs tabTotal= "2" items="Cloud Provider LoadBalancer,Port-forward for local testing" >}}
   {{% tab tabName="Cloud Provider LoadBalancer" %}}
   ```sh
   curl -vi "${INGRESS_GW_ADDRESS}:8080/headers" -H "host: www.example.com"                                  
   ```
   {{% /tab %}}
   {{% tab tabName="Port-forward for local testing" %}}
   ```sh
   curl -vi "localhost:8080/headers" -H "host: www.example.com" 
   ```
   {{% /tab %}}
   {{< /tabs >}}

   Example output: 
   ```
   ...
   < HTTP/1.1 401 Unauthorized
   HTTP/1.1 401 Unauthorized

   Client authentication failed   
   ...
   ```

6. Repeat the request. This time, you provide a valid API key in the `Authorization` header. Verify that the request now succeeds. 
   {{< tabs tabTotal= "2" items="Cloud Provider LoadBalancer,Port-forward for local testing" >}}
   {{% tab tabName="Cloud Provider LoadBalancer" %}}
   ```sh
   curl -vi "${INGRESS_GW_ADDRESS}:8080/headers" \
   -H "host: www.example.com" \
   -H "api-key: Bearer N2YwMDIxZTEtNGUzNS1jNzgzLTRkYjAtYjE2YzRkZGVmNjcy"                                 
   ```
   {{% /tab %}}
   {{% tab tabName="Port-forward for local testing" %}}
   ```sh
   curl -vi "localhost:8080/headers" \
   -H "host: www.example.com" \
   -H "api-key: Bearer N2YwMDIxZTEtNGUzNS1jNzgzLTRkYjAtYjE2YzRkZGVmNjcy"  
   ```
   {{% /tab %}}
   {{< /tabs >}}

   Example output: 
   ```console
   ...
   HTTP/1.1 200 OK
   < access-control-allow-credentials: true
   access-control-allow-credentials: true
   < access-control-allow-origin: *
   access-control-allow-origin: *
   < content-type: application/json; encoding=utf-8
   content-type: application/json; encoding=utf-8
   < content-length: 441
   content-length: 441
   < x-envoy-upstream-service-time: 13
   x-envoy-upstream-service-time: 13
   < server: envoy
   server: envoy
   
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
        "10.244.0.18"
      ],
      "X-Forwarded-Proto": [
        "http"
      ],
      "X-Request-Id": [
        "f64f1efa-1288-47d8-921f-4cb8f8deb96c"
      ]
    }
   }
   ...
   ```

## Cleanup 

{{< reuse "docs/snippets/cleanup.md" >}}

```sh
kubectl delete {{< reuse "docs/snippets/trafficpolicy.md" >}} apikey-auth -n {{< reuse "docs/snippets/namespace.md" >}}
kubectl delete secret apikey -n {{< reuse "docs/snippets/namespace.md" >}}
```

## Other configuration examples

Review other common configuration examples.

### Label selectors

Refer to your API key secrets by using label selectors. 

```yaml
kubectl apply -f- <<EOF
apiVersion: {{< reuse "docs/snippets/trafficpolicy-apiversion.md" >}}
kind: {{< reuse "docs/snippets/trafficpolicy.md" >}}
metadata:
  name: apikey-auth
  namespace: {{< reuse "docs/snippets/namespace.md" >}}
spec:
  targetRefs:
    - group: gateway.networking.k8s.io
      kind: Gateway
      name: http
  apiKeyAuth:
    secretSelector:
      matchLabels:
        app: httpbin
EOF
```

### Custom header name

By default, kgateway reads the API key from the `api-key` header. Use `keySources` to specify a different header name.

```yaml
kubectl apply -f- <<EOF
apiVersion: {{< reuse "docs/snippets/trafficpolicy-apiversion.md" >}}
kind: {{< reuse "docs/snippets/trafficpolicy.md" >}}
metadata:
  name: apikey-auth
  namespace: {{< reuse "docs/snippets/namespace.md" >}}
spec:
  targetRefs:
    - group: gateway.networking.k8s.io
      kind: Gateway
      name: http
  apiKeyAuth:
    secretRef:
      name: apikey
    keySources:
      - header: X-API-KEY
EOF
```

### Multiple key sources

Configure multiple key sources. The gateway proxy checks them in order. If you define different types of key sources, the precedence is determined as follows: 
* Header key sources take precedence over query parameter
* Query parameter key sources take precedence over cookie key sources

```yaml
kubectl apply -f- <<EOF
apiVersion: {{< reuse "docs/snippets/trafficpolicy-apiversion.md" >}}
kind: {{< reuse "docs/snippets/trafficpolicy.md" >}}
metadata:
  name: apikey-auth
  namespace: {{< reuse "docs/snippets/namespace.md" >}}
spec:
  targetRefs:
    - group: gateway.networking.k8s.io
      kind: Gateway
      name: http
  apiKeyAuth:
    secretRef:
      name: apikey
    keySources:
      - header: X-API-KEY
      - query: api_key
      - cookie: auth_token
EOF
```

### Forward client ID header

Use `clientIdHeader` to forward the authenticated client identifier to the upstream service in a request header. This setup is useful for passing caller identity to backend services.

```yaml
kubectl apply -f- <<EOF
apiVersion: {{< reuse "docs/snippets/trafficpolicy-apiversion.md" >}}
kind: {{< reuse "docs/snippets/trafficpolicy.md" >}}
metadata:
  name: apikey-auth
  namespace: {{< reuse "docs/snippets/namespace.md" >}}
spec:
  targetRefs:
    - group: gateway.networking.k8s.io
      kind: Gateway
      name: http
  apiKeyAuth:
    secretRef:
      name: apikey
    clientIdHeader: x-client-id
EOF
```

### Forward credential to upstream

By default, the API key is stripped from the request before it is forwarded to the upstream. Set `forwardCredential: true` to preserve the API key in the upstream request.

```yaml
kubectl apply -f- <<EOF
apiVersion: {{< reuse "docs/snippets/trafficpolicy-apiversion.md" >}}
kind: {{< reuse "docs/snippets/trafficpolicy.md" >}}
metadata:
  name: apikey-auth
  namespace: {{< reuse "docs/snippets/namespace.md" >}}
spec:
  targetRefs:
    - group: gateway.networking.k8s.io
      kind: Gateway
      name: http
  apiKeyAuth:
    secretRef:
      name: apikey
    forwardCredential: true
EOF
```

### Disable API key auth

Use `disable` to override an API key auth policy that is applied at a higher level in the hierarchy, such as a gateway-level policy, for a specific route.

```yaml
kubectl apply -f- <<EOF
apiVersion: {{< reuse "docs/snippets/trafficpolicy-apiversion.md" >}}
kind: {{< reuse "docs/snippets/trafficpolicy.md" >}}
metadata:
  name: apikey-auth-disable
  namespace: {{< reuse "docs/snippets/namespace.md" >}}
spec:
  targetRefs:
    - group: gateway.networking.k8s.io
      kind: HTTPRoute
      name: httpbin
  apiKeyAuth:
    disable: {}
EOF
```
