By default, the OAuth2 provider uses the same `backendRef` for both the OAuth2 token endpoint and the JWKS endpoint. However, some identity providers such as Amazon Cognito host these endpoints on different domains.

The `jwksBackendRef` field in `OAuth2JWTConfig` lets you specify a separate backend for fetching JWKS, enabling more flexible network routing and certificate management.


## When to use a separate JWKS backend

- When the JWKS endpoint is on a different domain than the token endpoint.
- When you need different network policies or TLS settings for JWKS fetching.
- When the JWKS endpoint requires different authentication or authorization.

## Before you begin

1. {{< reuse "kgw-docs/snippets/prereq.md" >}}
2. Complete the [OAuth2/OIDC guide]({{< link-hextra path="/security/extauth/oauth2/" >}}).

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

{{< callout type="info" >}}
If you don't set jwksBackendRef, the gateway uses the primary backendRef for JWKS requests, maintaining backward compatibility.
{{< /callout >}}

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

After deploying the GatewayExtension, verify that the JWKS is fetched from the correct backend.

**Send a request with a valid token**:

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

**Expected output**:

```text
< HTTP/1.1 200 OK
```

If the JWKS is fetched correctly, you should see a 200 OK response.

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