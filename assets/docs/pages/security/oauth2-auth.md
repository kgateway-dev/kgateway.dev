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
    participant Gateway as Kgateway Proxy
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

{{< reuse "docs/snippets/prereq.md" >}}

This guide requires an OIDC IdP, such as Keycloak, deployed in-cluster and reachable, and an HTTPRoute for your app.

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
  namespace: {{< reuse "docs/snippets/namespace.md" >}}
type: Opaque
stringData:
  client-secret: my-super-secret-client-secret-key
EOF
```

### 2. Create a GatewayExtension for OAuth2

Create a `GatewayExtension` specifying your OIDC provider settings in the `spec.oauth2` block. The following example uses Keycloak as the Identity Provider:

```yaml
kubectl apply -f- <<EOF
apiVersion: {{< reuse "docs/snippets/trafficpolicy-apiversion.md" >}}
kind: GatewayExtension
metadata:
  name: keycloak-oauth2
  namespace: {{< reuse "docs/snippets/namespace.md" >}}
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

### 3. Create a TrafficPolicy

Enforce the OAuth2/OIDC authentication policy on your Gateway using the `oauth2` configuration block in a `TrafficPolicy`:

```yaml
kubectl apply -f- <<EOF
apiVersion: {{< reuse "docs/snippets/trafficpolicy-apiversion.md" >}}
kind: {{< reuse "docs/snippets/trafficpolicy.md" >}}
metadata:
  name: oauth2-auth-policy
  namespace: {{< reuse "docs/snippets/namespace.md" >}}
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

---

## Verify the authentication flow

1. Open your browser and navigate to the application URL (for example, `https://my-app.example.com/`).
2. Verify that you are redirected to the Keycloak login screen.
3. Authenticate with your credentials.
4. Verify that you are redirected back to your application and the request succeeds.
5. Inspect the cookies in your browser; you should see secure, HTTP-only cookies containing the session tokens.

---

## Advanced configurations

Review these optional configurations to customize the OAuth2/OIDC behavior.

### Forward access token to backend

By default, the gateway proxy stores tokens in cookies and does not forward them to backend services. Set `forwardAccessToken: true` in your `GatewayExtension` to forward the access token upstream in the `Authorization: Bearer <token>` header:

```yaml
spec:
  oauth2:
    forwardAccessToken: true
    # ... other settings
```

### Customize cookie configuration

You can customize the names, domain, and `sameSite` policy of the cookies used to store session tokens:

```yaml
spec:
  oauth2:
    cookies:
      domain: example.com
      sameSite: Lax
      names:
        accessToken: my-custom-access-token
        idToken: my-custom-id-token
```

### Extract JWT claims to custom request headers

If your Identity Provider issues tokens in JWT format, you can configure kgateway to verify the signatures and copy specific claims (such as the user `email`, `sub`, or custom roles) directly into HTTP headers forwarded to the backend:

```yaml
spec:
  oauth2:
    jwt:
      jwksURI: https://keycloak.example.com/realms/master/protocol/openid-connect/certs
      idToken:
        claimsToHeaders:
          - name: sub
            header: x-user-id
          - name: email
            header: x-user-email
```

### Deny redirect for AJAX / API requests

For API calls or AJAX requests (such as `fetch` or `XMLHttpRequest`), a `302 Redirect` back to a login screen is undesirable. Use `denyRedirect` to specify header match rules. When a request matches these rules, the gateway returns a `401 Unauthorized` response instead of redirecting:

```yaml
spec:
  oauth2:
    denyRedirect:
      headers:
        - name: X-Requested-With
          value: XMLHttpRequest
```

---

## Cleanup

{{< reuse "docs/snippets/cleanup.md" >}}

```sh
kubectl delete {{< reuse "docs/snippets/trafficpolicy.md" >}} oauth2-auth-policy -n {{< reuse "docs/snippets/namespace.md" >}}
kubectl delete gatewayextension keycloak-oauth2 -n {{< reuse "docs/snippets/namespace.md" >}}
kubectl delete secret oauth2-client-secret -n {{< reuse "docs/snippets/namespace.md" >}}
```
