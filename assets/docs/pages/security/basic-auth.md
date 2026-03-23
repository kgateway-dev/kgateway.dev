
[Basic authentication](https://en.wikipedia.org/wiki/Basic_access_authentication) sends encoded user credentials in a standard header within the request. The kgateway proxy authenticates the request against a dictionary of usernames and passwords that is stored in an {{< reuse "docs/snippets/trafficpolicy.md" >}} resource. If the credentials in the `Authorization` request header match the credentials in the {{< reuse "docs/snippets/trafficpolicy.md" >}} resource, the request is authenticated and forwarded to the destination. If not, the proxy returns a 401 response.

The following diagram illustrates the flow:

```mermaid
sequenceDiagram
    participant C as Client / Agent
    participant AGW as Kgateway Proxy
    participant Backend as Backend

    C->>AGW: POST /api<br/>(no credentials)

    AGW->>AGW: Basic auth check:<br/>No Authorization header found

    AGW-->>C: 401 Unauthorized<br/>"no basic authentication credentials found"

    Note over C,Backend: Retry with credentials

    C->>AGW: POST /api<br/>Authorization: Basic dXNlcjpwYXNzd29yZA==

    AGW->>AGW: Decode base64 → user:password
    AGW->>AGW: Lookup user in policy config
    AGW->>AGW: Verify SHA-1 hash

    alt Credentials valid
        AGW->>Backend: Forward request
        Backend-->>AGW: Response
        AGW-->>C: 200 OK + Response
    else Credentials invalid or missing
        AGW-->>C: 401 Unauthorized
    end
```

The kgateway proxy requires passwords to be hashed using [SHA-1](https://en.wikipedia.org/wiki/SHA-1). Passwords in this format follow the pattern: `{SHA}BASE64_ENCODED_HASH`. You can use `htpasswd` to generate a hashed password.

## Before you begin 

{{< reuse "docs/snippets/prereq.md" >}}

3. Make sure that you have the following CLI tools, or something comparable:
   * `htpasswd` to generate hashed, salted passwords.
   * `base64` to encode strings.
 

## Set up basic auth {#basic-policy-config}

1. Generate a hashed password for your user credentials. The following example uses the `htpasswd` tool for a user named `user`.
   ```shell
   htpasswd -nbs user password
   ```
   Example output:
   ```
   user:{SHA}W6ph5Mm5Pz8GgiULbPgzG37mj9g=
   ```

2. Create an {{< reuse "docs/snippets/trafficpolicy.md" >}} resource with your basic auth policy. For other common configuration examples, see [Other configuration examples](#other-configuration-examples).
   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: {{< reuse "docs/snippets/trafficpolicy-apiversion.md" >}}
   kind: {{< reuse "docs/snippets/trafficpolicy.md" >}}
   metadata:
     name: basic-auth
     namespace: {{< reuse "docs/snippets/namespace.md" >}}
   spec:
     targetRefs:
       - group: gateway.networking.k8s.io
         kind: Gateway
         name: http
     basicAuth:
       users:
         - "user:{SHA}W6ph5Mm5Pz8GgiULbPgzG37mj9g="
   EOF
   ```

3. Send a request to the httpbin app without any credentials. Verify that the request fails with a 401 HTTP response code. 
   
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

   User authentication failed. Missing username and password. 
   ...
   ```

4. Encode the expected user credentials in base64 format.
   ```sh
   echo -n "user:password" | base64
   ```

   Example output: 
   ```
   dXNlcjpwYXNzd29yZA==
   ```

5. Repeat the request. This time, you include the base64 user credentials in an `Authorization` header. Verify that the request now succeeds and returns.
   {{< tabs tabTotal= "2" items="Cloud Provider LoadBalancer,Port-forward for local testing" >}}
   {{% tab tabName="Cloud Provider LoadBalancer" %}}
   ```sh
   curl -vi "${INGRESS_GW_ADDRESS}:8080/headers" \
   -H "host: www.example.com" \
   -H "Authorization: Basic dXNlcjpwYXNzd29yZA=="
   ```
   {{% /tab %}}
   {{% tab tabName="Port-forward for local testing" %}}
   ```sh
   curl -vi "localhost:8080/headers" \
   -H "host: www.example.com" \
   -H "Authorization: Basic dXNlcjpwYXNzd29yZA=="
   ```
   {{% /tab %}}
   {{< /tabs >}}

   Example output: 
   ```
   ...
   * Request completely sent off
   < HTTP/1.1 200 OK
   HTTP/1.1 200 OK
   < access-control-allow-credentials: true
   access-control-allow-credentials: true
   < access-control-allow-origin: *
   access-control-allow-origin: *
   < content-type: application/json; encoding=utf-8
   content-type: application/json; encoding=utf-8
   < content-length: 148
   content-length: 148
   < x-envoy-upstream-service-time: 0
   x-envoy-upstream-service-time: 0
   < server: envoy
   server: envoy

   < 
   
   {
    "headers": {
      "Accept": [
        "*/*"
      ],
      "Authorization": [
        "Basic dXNlcjpwYXNzd29yZA=="
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
        "4f3af980-3eff-41c1-82fa-8a8ff4df883a"
      ]
    }
   }
   ...
    
   ```

## Cleanup 

{{< reuse "docs/snippets/cleanup.md" >}}

```sh
kubectl delete {{< reuse "docs/snippets/trafficpolicy.md" >}} basic-auth -n {{< reuse "docs/snippets/namespace.md" >}}
```

## Other configuration examples

Review other common configuration examples.

### Multiple users

Add multiple users by including additional entries in the `users` array. Generate each password hash with `htpasswd -nbs <username> <password>`.

```yaml
kubectl apply -f- <<EOF
apiVersion: {{< reuse "docs/snippets/trafficpolicy-apiversion.md" >}}
kind: {{< reuse "docs/snippets/trafficpolicy.md" >}}
metadata:
  name: basic-auth
  namespace: {{< reuse "docs/snippets/namespace.md" >}}
spec:
  targetRefs:
    - group: gateway.networking.k8s.io
      kind: Gateway
      name: http
  basicAuth:
    users:
      - "admin:{SHA}W6ph5Mm5Pz8GgiULbPgzG37mj9g="
      - "developer:{SHA}QL0AFWMIX8NRZTKeof9cXsvbvu8="
EOF
```

### Secret reference

Instead of listing users inline, store the htpasswd data in a Kubernetes secret and reference it. The secret key defaults to `.htpasswd`.

1. Create a secret with your htpasswd data.
   ```sh
   kubectl create secret generic basic-auth-users \
     --from-literal=.htpasswd="admin:{SHA}W6ph5Mm5Pz8GgiULbPgzG37mj9g=" \ 
     -n {{< reuse "docs/snippets/namespace.md" >}}
   ```

2. Reference the secret in an {{< reuse "docs/snippets/trafficpolicy.md" >}} resource.
   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: {{< reuse "docs/snippets/trafficpolicy-apiversion.md" >}}
   kind: {{< reuse "docs/snippets/trafficpolicy.md" >}}
   metadata:
     name: basic-auth
     namespace: {{< reuse "docs/snippets/namespace.md" >}}
   spec:
     targetRefs:
       - group: gateway.networking.k8s.io
         kind: Gateway
         name: http
     basicAuth:
       secretRef:
         name: basic-auth-users
   EOF
   ```

### Custom secret key

If your htpasswd data is stored under a key other than `.htpasswd`, specify it with `secretRef.key`.

```yaml
kubectl apply -f- <<EOF
apiVersion: {{< reuse "docs/snippets/trafficpolicy-apiversion.md" >}}
kind: {{< reuse "docs/snippets/trafficpolicy.md" >}}
metadata:
  name: basic-auth
  namespace: {{< reuse "docs/snippets/namespace.md" >}}
spec:
  targetRefs:
    - group: gateway.networking.k8s.io
      kind: Gateway
      name: http
  basicAuth:
    secretRef:
      name: basic-auth-users
      key: passwords.htpasswd
EOF
```

### Disable basic auth

Use `disable` to override a basic auth policy applied at a higher level in the hierarchy, such as a gateway-level policy, for a specific route.

```yaml
kubectl apply -f- <<EOF
apiVersion: {{< reuse "docs/snippets/trafficpolicy-apiversion.md" >}}
kind: {{< reuse "docs/snippets/trafficpolicy.md" >}}
metadata:
  name: basic-auth-disable
  namespace: {{< reuse "docs/snippets/namespace.md" >}}
spec:
  targetRefs:
    - group: gateway.networking.k8s.io
      kind: HTTPRoute
      name: httpbin
  basicAuth:
    disable: {}
EOF
```