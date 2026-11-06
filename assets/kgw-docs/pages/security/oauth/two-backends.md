By default, the OAuth2 provider uses the same `backendRef` for both the OAuth2 token endpoint and the JWKS endpoint. However, some identity providers such as Amazon Cognito host these endpoints on different domains.

The `jwksBackendRef` field in `OAuth2JWTConfig` lets you specify a separate backend for fetching JWKS, enabling more flexible network routing and certificate management.


## When to use a separate JWKS backend

- When the JWKS endpoint is on a different domain than the token endpoint.
- When you need different network policies or TLS settings for JWKS fetching.
- When the JWKS endpoint requires different authentication or authorization.

## Before you begin

1. {{< reuse "kgw-docs/snippets/prereq.md" >}}
2. Complete the [OAuth2/OIDC guide for Keycloak]({{< link-hextra path="/security/oauth/keycloak/authorization-code/" >}}).

## Configure separate backends

To configure separate backends for the token endpoint and JWKS fetching, update your existing OAuth2 `GatewayExtension` with a `jwksBackendRef` field.

### Step 0: Save your existing GatewayExtension

Before making changes, save the current GatewayExtension YAML to a file:

```sh
kubectl get gatewayextension keycloak-oauth2 -n {{< reuse "kgw-docs/snippets/namespace.md" >}} -o yaml > gatewayextension-oauth2.yaml
```
This ensures you have a backup and can modify the saved file directly.

### Step 1: Verify your primary backend

Your existing `GatewayExtension` already has a `backendRef` that points to your OAuth2 provider's token endpoint. This remains unchanged. The primary backend is used for:

- Token endpoint
- Authorization endpoint
- End session endpoint

### Step 2: Add a JWKS backend

Add the `jwksBackendRef` field to your `GatewayExtension` to specify a dedicated backend for JWKS fetching:

```yaml
jwksBackendRef:
  kind: {{< reuse "kgw-docs/snippets/backend.md" >}}
  group: {{< reuse "kgw-docs/snippets/gatewayparam-group.md" >}}
  name: cognito-jwks
```

> [!NOTE]
> If you don't set jwksBackendRef, the gateway uses the primary backendRef for JWKS requests, maintaining backward compatibility.

### Step 3: Define the JWKS Backend resource

Create a Backend resource that points to your JWKS endpoint:

```yaml
apiVersion: {{< reuse "kgw-docs/snippets/gatewayparam-apiversion.md" >}}
kind: {{< reuse "kgw-docs/snippets/backend.md" >}}
metadata:
  name: cognito-jwks
  namespace: {{< reuse "kgw-docs/snippets/namespace.md" >}}
spec:
  type: Static
  static:
    hosts:
    - host: cognito-idp.us-east-1.amazonaws.com
      port: 443
```

### Step 4: Apply the updated configuration

Apply the GatewayExtension and Backend resources:

```sh
kubectl apply -f gatewayextension-oauth2.yaml
kubectl apply -f cognito-jwks-backend.yaml
```

## Example: Amazon Cognito

The following example shows how to configure `jwksBackendRef` for Amazon Cognito. For more information on setting up Cognito as an OIDC provider, see the [Amazon Cognito documentation](https://docs.aws.amazon.com/cognito/).

The fields in the example come from your Cognito user pool configuration:
- **jwksURI**: `https://cognito-idp.<region>.amazonaws.com/<user-pool-id>/.well-known/jwks.json`
- **tokenEndpoint**: `https://cognito-idp.<region>.amazonaws.com/oauth2/token`
- **authorizationEndpoint**: `https://cognito-idp.<region>.amazonaws.com/oauth2/authorize`

```yaml
apiVersion: gateway.kgateway.dev/v1alpha1
kind: GatewayExtension
metadata:
  name: oauth-two-backends
  namespace: {{< reuse "kgw-docs/snippets/namespace.md" >}}
spec:
  oauth2:
    backendRef:
      kind: Backend
      group: gateway.kgateway.dev
      name: cognito-token
    tokenEndpoint: https://cognito-idp.us-east-1.amazonaws.com/token
    authorizationEndpoint: https://cognito-idp.us-east-1.amazonaws.com/authorize
    credentials:
      clientID: your-client-id
      clientSecretRef:
        name: oauth-client-secret
    redirectURI: https://example.com/oauth2/redirect
    scopes: ["openid", "email"]
    jwt:
      jwksURI: https://cognito-idp.us-east-1.amazonaws.com/us-east-1_abc123/.well-known/jwks.json
      jwksBackendRef:
        kind: Backend
        group: gateway.kgateway.dev
        name: cognito-jwks
      accessToken:
        audiences:
          - your-client-id
```

### Backend Definitions

```yaml
apiVersion: gateway.kgateway.dev/v1alpha1
kind: Backend
metadata:
  name: cognito-token
  namespace: {{< reuse "kgw-docs/snippets/namespace.md" >}}
spec:
  type: Static
  static:
    hosts:
    - host: cognito-idp.us-east-1.amazonaws.com
      port: 443
---
apiVersion: gateway.kgateway.dev/v1alpha1
kind: Backend
metadata:
  name: cognito-jwks
  namespace: {{< reuse "kgw-docs/snippets/namespace.md" >}}
spec:
  type: Static
  static:
    hosts:
    - host: cognito-idp.us-east-1.amazonaws.com
      port: 443
```

## Verify the configuration

Log in through the gateway to verify that the gateway fetches the JWKS from the correct backend. After the login, the gateway validates the access token against that JWKS. Send these requests to the HTTPS listener, because the session cookies of the login flow use the `Secure` attribute.

> [!NOTE]
> The OAuth2 policy reads tokens only from the session cookies that the gateway sets after a login. A request that carries only an `Authorization: Bearer` header has no session. The gateway redirects that request to the login page, or returns `401` if the request matches the [`denyRedirect` setting]({{< link-hextra path="/security/oauth/keycloak/authorization-code/#deny-redirect" >}}). So you cannot verify this configuration with a bearer token. To validate bearer tokens from API clients, use [access token validation]({{< link-hextra path="/security/oauth/keycloak/access-token/" >}}).

1. Send a request without a session cookie. The gateway redirects you to Keycloak.

   {{< tabs >}}
   {{% tab name="Cloud Provider LoadBalancer" %}}
   ```sh
   curl -vik "https://${INGRESS_GW_ADDRESS}:8443/headers" -H "host: www.example.com"
   ```
   {{% /tab %}}
   {{% tab name="Port-forward for local testing" %}}
   ```sh
   curl -vik "https://localhost:8443/headers" -H "host: www.example.com"
   ```
   {{% /tab %}}
   {{< /tabs >}}

   Example output:

   ```text
   < HTTP/2 302
   < location: https://keycloak.example.com/realms/myrealm/protocol/openid-connect/auth?client_id=kgateway-client&...
   ```

2. Open a browser and go to your protected route, such as `https://www.example.com/headers`. Log in with the test user credentials, `testuser` and `password`.

3. Verify that the response shows the httpbin output. The gateway validated the access token against the JWKS that it fetched through the `jwksBackendRef` backend. If the gateway cannot fetch the JWKS, the request after the login fails and does not return the httpbin output.

### Backward Compatibility

The `jwksBackendRef` field is **optional**. If not specified, the gateway uses the parent `backendRef` for JWKS fetching, maintaining compatibility with existing configurations.

## Cleanup

{{< reuse "kgw-docs/snippets/cleanup.md" >}}

Delete the GatewayExtension and Backend resources that you created in this guide.

```sh
kubectl delete gatewayextension oauth-two-backends -n {{< reuse "kgw-docs/snippets/namespace.md" >}}
kubectl delete backend cognito-token -n {{< reuse "kgw-docs/snippets/namespace.md" >}}
kubectl delete backend cognito-jwks -n {{< reuse "kgw-docs/snippets/namespace.md" >}}
```
