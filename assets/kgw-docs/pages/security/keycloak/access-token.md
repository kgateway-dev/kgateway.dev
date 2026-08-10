Protect a route by validating an access token that the client already holds. Kgateway checks the token signature against the Keycloak signing keys and rejects requests that do not carry a valid token, instead of redirecting them to a login page. Use this flow for API clients, which cannot follow a browser redirect.

## Before you begin

Complete the [Keycloak setup]({{< link-hextra path="/security/oauth2/keycloak/setup/" >}}) page. This flow needs the realm, the client, the test user, the `Backend`, and the `BackendConfigPolicy` that it creates, and it needs the [audience mapper]({{< link-hextra path="/security/oauth2/keycloak/setup/#audience-mapper" >}}) so that tokens carry your client ID in the `aud` claim.

Unlike the authorization code flow, this flow does not need the client secret in a Kubernetes Secret, because the gateway never exchanges an authorization code. It also works over plain HTTP, because it does not use cookies.

## Configure access token validation

Create a `GatewayExtension` that tells the gateway how to validate tokens, and a `TrafficPolicy` that enforces it on a route.

### Create the JWT GatewayExtension {#create-jwt-extension}

Create a GatewayExtension for JWT validation. The `issuer` must match the token's `iss` claim from Keycloak.

```yaml
kubectl apply -f- <<EOF
apiVersion: {{< reuse "kgw-docs/snippets/trafficpolicy-apiversion.md" >}}
kind: GatewayExtension
metadata:
  name: keycloak-jwt
  namespace: {{< reuse "kgw-docs/snippets/namespace.md" >}}
spec:
  jwt:
    providers:
      - name: keycloak
        issuer: https://keycloak.example.com/realms/myrealm
        jwks:
          remote:
            backendRef:
              group: gateway.kgateway.dev
              kind: Backend
              name: keycloak
              namespace: {{< reuse "kgw-docs/snippets/namespace.md" >}}
            url: https://keycloak.example.com/realms/myrealm/protocol/openid-connect/certs
        audiences:
          - kgateway-client
EOF
```

Replace the following values:

- `keycloak.example.com` with your Keycloak hostname.

- `myrealm` with your realm name.

- `kgateway-client` with your Client ID.

| Field | Description |
|-------|-------------|
| `name` | A required, unique name for the provider. The resource is rejected without it. |
| `issuer` | Must match the `iss` claim in your tokens exactly. Keycloak derives `iss` from the URL that the token request arrives on, so a token that you fetch through a port-forward on `https://localhost:9443` carries that address, not the in-cluster Service name. Decode a real token and read its `iss` claim rather than assuming. |
| `jwks.remote.backendRef` | The network path that the gateway uses to fetch the signing keys. This is the `Backend` for Keycloak, so the JWKS endpoint does not have to be reachable from outside the cluster. |
| `jwks.remote.url` | The JWKS URL. Kgateway connects through `backendRef`, and uses this value for the request path and `Host` header. |
| `audiences` | The accepted values of the `aud` claim. A token is rejected with a `403` response if none of its audiences match. |

> [!WARNING]
> Do not add `account` to `audiences` as a way to make token validation pass. `account` is the realm's built-in client, and every token that the realm issues carries it, so accepting it lets a token minted for **any** client in the realm through this policy. If your tokens do not contain your client ID, add the [audience mapper](#audience-mapper) to the Keycloak client instead. You can decode a token and check its `aud` claim at [jwt.io](https://jwt.io).

### Attach the JWT policy {#attach-jwt-policy}

Create a `TrafficPolicy` that references the JWT GatewayExtension.

```yaml
kubectl apply -f- <<EOF
apiVersion: {{< reuse "kgw-docs/snippets/trafficpolicy-apiversion.md" >}}
kind: {{< reuse "kgw-docs/snippets/trafficpolicy.md" >}}
metadata:
  name: keycloak-jwt-policy
  namespace: httpbin
spec:
  targetRefs:
    - group: gateway.networking.k8s.io
      kind: HTTPRoute
      name: httpbin
  jwtAuth:
    extensionRef:
      name: keycloak-jwt
      namespace: {{< reuse "kgw-docs/snippets/namespace.md" >}}
EOF
```

As with the OAuth2 policy, this `TrafficPolicy` must be in the same namespace as the HTTPRoute that it targets. Confirm that it attached.

```sh
kubectl get {{< reuse "kgw-docs/snippets/trafficpolicy.md" >}} keycloak-jwt-policy -n httpbin -o yaml
```

## Verify {#verify}

Use the verification steps below to confirm that the Access Token Validation flow works.

1. Get the JWKS URI from Keycloak:

   * In the Keycloak admin console, go to the **Realm settings** > **General** tab.
   * Scroll down to the **Endpoints** section.
   * Open the **OpenID Endpoint Configuration** link in a new tab.
   * In the OpenID configuration, find the `jwks_uri` field.
   * Confirm that the value matches the `jwks.remote.url` field that you set on the `GatewayExtension`, for example:

     ```text
     https://keycloak.example.com/realms/myrealm/protocol/openid-connect/certs
     ```

2. Verify that a request without a token is rejected.

   ```sh
   curl -vi "http://localhost:8080/headers" -H "host: www.example.com"
   ```

   Example output:

   ```text
   < HTTP/1.1 401 Unauthorized
   ```

3. Obtain a token from Keycloak with the `password` grant. Add `-k` if Keycloak uses a self-signed certificate.

   ```bash
   export TOKEN=$(curl -sk -d "client_id=kgateway-client" \
     -d "client_secret=YOUR_CLIENT_SECRET" \
     -d "username=testuser" \
     -d "password=password" \
     -d "grant_type=password" \
     "https://keycloak.example.com/realms/myrealm/protocol/openid-connect/token" \
     | jq -r .access_token)
   ```

4. Confirm that the token's `iss` and `aud` claims match your `GatewayExtension`. Decode the payload.

   ```sh
   echo $TOKEN | jq -rR 'split(".")[1] | @base64d' | jq '{iss, aud}'
   ```

   Example output. If `aud` does not include your client ID, add the [audience mapper](#audience-mapper) to the Keycloak client.

   ```json
   {
     "iss": "https://keycloak.example.com/realms/myrealm",
     "aud": ["kgateway-client", "account"]
   }
   ```

5. Send a request with the token in the `Authorization` header.

   ```bash
   curl -vi "http://localhost:8080/headers" \
     -H "host: www.example.com" \
     -H "Authorization: Bearer $TOKEN"
   ```

   A successful response shows the headers from the httpbin app.

   ```text
   < HTTP/1.1 200 OK
   ```

   A `403` response means that the token is valid but its `aud` claim does not match the `audiences` list. A `401` response means that the token is missing, expired, or signed by an issuer that does not match `issuer`.

## Cleanup {#cleanup}

{{< reuse "kgw-docs/snippets/cleanup.md" >}}

```sh
kubectl delete {{< reuse "kgw-docs/snippets/trafficpolicy.md" >}} keycloak-jwt-policy -n httpbin
kubectl delete GatewayExtension keycloak-jwt -n {{< reuse "kgw-docs/snippets/namespace.md" >}}
```

To remove Keycloak and the shared resources, see the Cleanup section of the [Keycloak setup]({{< link-hextra path="/security/oauth2/keycloak/setup/#cleanup" >}}) page.
