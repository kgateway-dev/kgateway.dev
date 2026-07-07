Secure your services by delegating authentication to an external Identity Provider (IdP) using OpenID Connect (OIDC) or OAuth 2.0.

## About OAuth2 and OIDC in kgateway

When you configure OAuth2/OIDC in kgateway, the gateway proxy acts as the OAuth2 client. It intercepts incoming client requests, determines if they are authenticated, and handles the handshake with the authorization server:

1. **Redirect**: If the request does not contain valid session cookies, the gateway redirects the client's browser to the IdP's authorization endpoint.
2. **Callback**: After the user successfully authenticates with the IdP, they are redirected back to the gateway's redirect URI with an authorization code.
3. **Token Exchange**: The gateway proxy intercepts the redirect callback, contacts the IdP's token endpoint to exchange the authorization code for access, ID, and refresh tokens.
4. **Cookies & Forwarding**: The gateway proxy stores the received tokens in encrypted, secure, HTTP-only session cookies in the user's browser, and then forwards the authenticated request to the upstream backend. Subsequent requests from the client use these cookies to bypass the authorization handshake.

The following sequence diagram illustrates this authorization code flow:

```mermaid
sequenceDiagram
    autonumber
    participant Client as User Browser
    participant Gateway as kgateway proxy
    participant IdP as Identity Provider (such as Keycloak)
    participant Backend as Upstream Service

    Client->>Gateway: 1. Request /api (no session cookies)
    Gateway-->>Client: 2. 302 Redirect to IdP Auth Endpoint
    Client->>IdP: 3. Login with Credentials
    IdP-->>Client: 4. 302 Redirect to Redirect URI with Auth Code
    Client->>Gateway: 5. Callback request with Auth Code
    Gateway->>IdP: 6. POST /token (exchange code for tokens)
    IdP-->>Gateway: 7. ID, Access, & Refresh Tokens
    Gateway-->>Client: 8. 302 Redirect to original path + set session cookies
    Client->>Gateway: 9. Request /api with session cookies
    Gateway->>Backend: 10. Forward request to upstream
    Backend-->>Gateway: 11. Response
    Gateway-->>Client: 12. 200 OK + Response
```

## Before you begin

{{< reuse "kgw-docs/snippets/prereq.md" >}}

This guide requires an OIDC IdP, such as Keycloak, deployed in-cluster and reachable, and an HTTPRoute for your app.

## Set up Keycloak as the identity provider

This guide uses Keycloak as the example IdP. Follow these steps to deploy and configure it.

### 1. Create the Keycloak admin secret

Store the admin credentials in a Kubernetes Secret:

```yaml
kubectl apply -f- <<EOF
apiVersion: v1
kind: Secret
metadata:
  name: keycloak-admin
  namespace: keycloak-system
type: Opaque
stringData:
  admin-user: admin
  admin-password: admin
EOF
```

### 2. Deploy Keycloak

Choose one of the following methods:

**Option A: Using Helm (recommended for production):**

```sh
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo update
helm install keycloak bitnami/keycloak \
  --namespace keycloak-system \
  --create-namespace \
  --set auth.adminUser=admin \
  --set auth.adminPassword=admin \
  --set service.type=ClusterIP \
  --set service.ports.http=8080
```

This deploys Keycloak with the admin credentials `admin/admin`.

**Option B: Using YAML (for testing, no Helm required):**

```yaml
kubectl apply -f- <<EOF
apiVersion: apps/v1
kind: Deployment
metadata:
  name: keycloak
  namespace: keycloak-system
spec:
  replicas: 1
  selector:
    matchLabels:
      app: keycloak
  template:
    metadata:
      labels:
        app: keycloak
    spec:
      containers:
      - name: keycloak
        image: quay.io/keycloak/keycloak:latest
        args: ["start-dev", "--http-port=8080"]
        env:
        - name: KEYCLOAK_ADMIN
          valueFrom:
            secretKeyRef:
              name: keycloak-admin
              key: admin-user
        - name: KEYCLOAK_ADMIN_PASSWORD
          valueFrom:
            secretKeyRef:
              name: keycloak-admin
              key: admin-password
        ports:
        - containerPort: 8080
EOF
```

### 3. Expose Keycloak as a service

If you used the YAML method in step 2, expose Keycloak as a service:

```yaml
kubectl apply -f- <<EOF
apiVersion: v1
kind: Service
metadata:
  name: keycloak
  namespace: keycloak-system
spec:
  selector:
    app: keycloak
  ports:
  - port: 8080
    targetPort: 8080
EOF
```

If you used the Helm method, a service is automatically created. Skip this step.

### 4. Port-forward Keycloak

```sh
kubectl port-forward svc/keycloak -n keycloak-system 8080:8080
```

### 5. Configure Keycloak

1. Access the admin console at `http://localhost:8080`.
2. Log in with:
   - Username: `admin`
   - Password: `admin`
3. Create a new realm (e.g., `kgateway`).
4. Create a confidential client:
   - Set **Valid Redirect URIs** to `https://www.example.com/oauth2/redirect`.
   - Note the client ID and client secret for the next section.

For more details, see the [Keycloak documentation](https://www.keycloak.org/docs/latest/server_admin/).

## Set up OAuth2/OIDC authentication

To configure OIDC/OAuth2, you store the client credentials in a Kubernetes Secret, create a `GatewayExtension` specifying the provider details, and apply the policy using a `TrafficPolicy`.

### 1. Store client secret in a Secret

Create a Kubernetes Secret containing your OAuth2 client secret. The secret must contain the client secret under the `client-secret` key:

```yaml
kubectl apply -f- <<EOF
apiVersion: v1
kind: Secret
metadata:
  name: oauth2-client-secret
  namespace: {{< reuse "kgw-docs/snippets/namespace.md" >}}
type: Opaque
stringData:
  client-secret: my-super-secret-client-secret-key
EOF
```
{{< callout type="info" >}}
Replace `my-super-secret-client-secret-key` with the OAuth/OIDC client secret from your identity provider. For example, in Keycloak, this is the secret generated for your confidential client when you create it in the Keycloak admin console.
{{< /callout >}}

### 2. Create a GatewayExtension for OAuth2

Create a `GatewayExtension` specifying your OIDC provider settings in the `spec.oauth2` block. The following example uses Keycloak as the Identity Provider:

```yaml
kubectl apply -f- <<EOF
apiVersion: {{< reuse "kgw-docs/snippets/trafficpolicy-apiversion.md" >}}
kind: GatewayExtension
metadata:
  name: keycloak-oauth2
  namespace: {{< reuse "kgw-docs/snippets/namespace.md" >}}
spec:
  oauth2:
    backendRef:
      name: keycloak
      namespace: keycloak-system
      port: 8080
    issuerURI: https://keycloak.example.com/realms/master
    redirectURI: https://www.example.com/oauth2/redirect
    credentials:
      clientID: my-client-id
      clientSecretRef:
        name: oauth2-client-secret
    scopes:
      - openid
      - email
      - profile
EOF
```

| Setting | Description |
| ------- | ----------- |
| `backendRef` | Reference to the Kubernetes Service representing your Identity Provider (IdP). This is the internal network path the gateway uses to communicate with the IdP. |
| `issuerURI` | The public issuer URL of the OpenID provider used to discover the auth, token, and JWKS endpoints. Note that while `backendRef` points to the in-cluster location for direct networking, `issuerURI` represents the identity of the issuer as seen by the browser or external clients. |
| `redirectURI` | The callback URI registered with your IdP. The gateway intercepts this endpoint to complete the code exchange. |
| `credentials.clientID` | The client ID registered with your IdP. |
| `credentials.clientSecretRef` | Reference to the Kubernetes Secret containing the client secret. |
| `scopes` | The scopes requested in the authentication flow. Include `openid` to enable OpenID Connect. |

For more details, see the [API reference](https://kgateway.dev/docs/envoy/latest/reference/api/#oauth2jwtconfig).

### 3. Create a TrafficPolicy

Enforce the OAuth2/OIDC authentication policy on your Gateway using the `oauth2` configuration block in a `TrafficPolicy`:

```yaml
kubectl apply -f- <<EOF
apiVersion: {{< reuse "kgw-docs/snippets/trafficpolicy-apiversion.md" >}}
kind: {{< reuse "kgw-docs/snippets/trafficpolicy.md" >}}
metadata:
  name: oauth2-auth-policy
  namespace: {{< reuse "kgw-docs/snippets/namespace.md" >}}
spec:
  targetRefs:
    - group: gateway.networking.k8s.io
      kind: Gateway
      name: http
  oauth2:
    extensionRef:
      name: keycloak-oauth2
EOF
```

| Setting | Description |
| ------- | ----------- |
| `targetRefs` | Selects the resource to apply the authentication policy to (such as a Gateway or HTTPRoute). |
| `oauth2.extensionRef` | References the `GatewayExtension` created in the previous step. |


## Verify the authentication flow

1. Open your browser and navigate to the application URL (e.g., `https://www.example.com/`).

{{< reuse-image src="img/oauth2/application-url.png" >}}
{{< reuse-image-dark srcDark="img/oauth2/application-url.png" >}}

2. Verify that you are redirected to the Keycloak login screen.

{{< reuse-image src="img/oauth2/keycloak-login.png" >}}
{{< reuse-image-dark srcDark="img/oauth2/keycloak-login.png" >}}

3. Authenticate with your credentials.

4. Verify that you are redirected back to your application and the request succeeds.

{{< reuse-image src="img/oauth2/redirected.png" >}}
{{< reuse-image-dark srcDark="img/oauth2/redirected.png" >}}

5. Inspect the cookies in your browser; you should see secure, HTTP-only cookies containing the session tokens.

{{< reuse-image src="img/oauth2/cookies.png" >}}
{{< reuse-image-dark srcDark="img/oauth2/cookies.png" >}}

### Test with curl

The following examples show how to test the OAuth2/OIDC flow using curl. The first request triggers a redirect to the IdP, and the second request uses the session cookie obtained after browser login.

**Send a request without authentication (browser flow):**

{{< tabs tabTotal="2" items="Cloud Provider LoadBalancer,Port-forward for local testing" >}}
{{% tab tabName="Cloud Provider LoadBalancer" %}}

```sh
curl -vik http://$INGRESS_GW_ADDRESS:8080/headers -H "host: www.example.com:8080"
```

{{% /tab %}}
{{% tab tabName="Port-forward for local testing" %}}

```sh
curl -vik localhost:8080/headers -H "host: www.example.com:8080"
```

{{% /tab %}}
{{< /tabs >}}

**Expected output:**

```text
< HTTP/1.1 302 Found
< location: https://keycloak.example.com/realms/master/protocol/openid-connect/auth?...
```

**Send a request with session cookies (after browser login):**

After completing the browser login flow, copy the session cookie from your browser's developer tools (Application → Cookies) and replace `session-cookie=...` with the actual cookie value.

{{< tabs tabTotal="2" items="Cloud Provider LoadBalancer,Port-forward for local testing" >}}
{{% tab tabName="Cloud Provider LoadBalancer" %}}

```sh
curl -vik http://$INGRESS_GW_ADDRESS:8080/headers \
  -H "host: www.example.com:8080" \
  --cookie "session-cookie=..."
```

{{% /tab %}}
{{% tab tabName="Port-forward for local testing" %}}

```sh
curl -vik localhost:8080/headers \
  -H "host: www.example.com:8080" \
  --cookie "session-cookie=..." 
```

{{% /tab %}}
{{< /tabs >}}

**Expected output:**

```text
< HTTP/1.1 200 OK
```

**Optional: Test JWT bearer authentication for API clients**

If you want to test with a bearer token (for API clients), you can use:

{{< tabs tabTotal="2" items="Cloud Provider LoadBalancer,Port-forward for local testing" >}}
{{% tab tabName="Cloud Provider LoadBalancer" %}}

```sh
curl -vik http://$INGRESS_GW_ADDRESS:8080/headers \
  -H "host: www.example.com:8080" \
  --header "Authorization: Bearer $TOKEN"
```

{{% /tab %}}
{{% tab tabName="Port-forward for local testing" %}}

```sh
curl -vik localhost:8080/headers \
  -H "host: www.example.com:8080" \
  --header "Authorization: Bearer $TOKEN"
```

{{% /tab %}}
{{< /tabs >}}

**Expected output:**

```text
< HTTP/1.1 200 OK
```

## Advanced configurations

Review these optional configurations to customize the OAuth2/OIDC behavior. Each of the following examples re-applies the `GatewayExtension` that you created in [step 2](#2-create-a-gatewayextension-for-oauth2) with an additional `spec.oauth2` field. Because the resource name is unchanged, re-applying updates your existing `GatewayExtension`.

### Forward access token to backend

By default, the gateway proxy stores tokens in cookies and does not forward them to backend services. Set `forwardAccessToken: true` in your `GatewayExtension` to forward the access token upstream in the `Authorization: Bearer <token>` header:

```yaml
kubectl apply -f- <<EOF
apiVersion: {{< reuse "kgw-docs/snippets/trafficpolicy-apiversion.md" >}}
kind: GatewayExtension
metadata:
  name: keycloak-oauth2
  namespace: {{< reuse "kgw-docs/snippets/namespace.md" >}}
spec:
  oauth2:
    backendRef:
      name: keycloak
      namespace: keycloak-system
      port: 8080
    issuerURI: https://keycloak.example.com/realms/master
    redirectURI: https://my-app.example.com/oauth2/redirect
    credentials:
      clientID: my-client-id
      clientSecretRef:
        name: oauth2-client-secret
    scopes:
      - openid
      - email
      - profile
    forwardAccessToken: true
EOF
```

### Customize cookie configuration

You can customize the names, domain, and `sameSite` policy of the cookies used to store session tokens:

```yaml
kubectl apply -f- <<EOF
apiVersion: {{< reuse "kgw-docs/snippets/trafficpolicy-apiversion.md" >}}
kind: GatewayExtension
metadata:
  name: keycloak-oauth2
  namespace: {{< reuse "kgw-docs/snippets/namespace.md" >}}
spec:
  oauth2:
    backendRef:
      name: keycloak
      namespace: keycloak-system
      port: 8080
    issuerURI: https://keycloak.example.com/realms/master
    redirectURI: https://my-app.example.com/oauth2/redirect
    credentials:
      clientID: my-client-id
      clientSecretRef:
        name: oauth2-client-secret
    scopes:
      - openid
      - email
      - profile
    cookies:
      domain: example.com
      sameSite: Lax
      names:
        accessToken: my-custom-access-token
        idToken: my-custom-id-token
EOF
```

### Extract JWT claims to custom request headers

If your Identity Provider issues tokens in JWT format, you can configure kgateway to verify the signatures and copy specific claims (such as the user `email`, `sub`, or custom roles) directly into HTTP headers forwarded to the backend:

```yaml
kubectl apply -f- <<EOF
apiVersion: {{< reuse "kgw-docs/snippets/trafficpolicy-apiversion.md" >}}
kind: GatewayExtension
metadata:
  name: keycloak-oauth2
  namespace: {{< reuse "kgw-docs/snippets/namespace.md" >}}
spec:
  oauth2:
    backendRef:
      name: keycloak
      namespace: keycloak-system
      port: 8080
    issuerURI: https://keycloak.example.com/realms/master
    redirectURI: https://my-app.example.com/oauth2/redirect
    credentials:
      clientID: my-client-id
      clientSecretRef:
        name: oauth2-client-secret
    scopes:
      - openid
      - email
      - profile
    jwt:
      jwksURI: https://keycloak.example.com/realms/master/protocol/openid-connect/certs
      idToken:
        claimsToHeaders:
          - name: sub
            header: x-user-id
          - name: email
            header: x-user-email
EOF
```

### Deny redirect for AJAX / API requests

For API calls or AJAX requests (such as `fetch` or `XMLHttpRequest`), a `302 Redirect` back to a login screen is undesirable. Use `denyRedirect` to specify header match rules. When a request matches these rules, the gateway returns a `401 Unauthorized` response instead of redirecting:

```yaml
kubectl apply -f- <<EOF
apiVersion: {{< reuse "kgw-docs/snippets/trafficpolicy-apiversion.md" >}}
kind: GatewayExtension
metadata:
  name: keycloak-oauth2
  namespace: {{< reuse "kgw-docs/snippets/namespace.md" >}}
spec:
  oauth2:
    backendRef:
      name: keycloak
      namespace: keycloak-system
      port: 8080
    issuerURI: https://keycloak.example.com/realms/master
    redirectURI: https://my-app.example.com/oauth2/redirect
    credentials:
      clientID: my-client-id
      clientSecretRef:
        name: oauth2-client-secret
    scopes:
      - openid
      - email
      - profile
    denyRedirect:
      headers:
        - name: X-Requested-With
          value: XMLHttpRequest
EOF
```


## Cleanup

{{< reuse "kgw-docs/snippets/cleanup.md" >}}

```sh
kubectl delete {{< reuse "kgw-docs/snippets/trafficpolicy.md" >}} oauth2-auth-policy -n {{< reuse "kgw-docs/snippets/namespace.md" >}}
kubectl delete gatewayextension keycloak-oauth2 -n {{< reuse "kgw-docs/snippets/namespace.md" >}}
kubectl delete secret oauth2-client-secret -n {{< reuse "kgw-docs/snippets/namespace.md" >}}
```
