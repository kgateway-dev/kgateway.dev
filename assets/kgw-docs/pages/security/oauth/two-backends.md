By default, the OAuth2 provider uses the same `backendRef` for both the OAuth2 token endpoint and the JWKS endpoint. However, some identity providers (e.g., Amazon Cognito) host these endpoints on different domains.

The `jwksBackendRef` field in `OAuth2JWTConfig` lets you specify a separate backend for fetching JWKS, enabling more flexible network routing and certificate management.

## When to use a separate JWKS backend

- When the JWKS endpoint is on a different domain than the token endpoint
- When you need different network policies or TLS settings for JWKS fetching
- When the JWKS endpoint requires different authentication or authorization

## Before you begin

{{< reuse "kgw-docs/snippets/prereq.md" >}}

## Configuration

### BackendRef (primary)

The `backendRef` field specifies the primary backend for the OAuth2 provider. This is used for:
- Token endpoint
- Authorization endpoint
- End session endpoint

### JWKSBackendRef (optional)

The `jwksBackendRef` field specifies a dedicated backend for fetching JWKS. When set, the gateway uses this backend instead of `backendRef` for JWKS requests.

If not set, the gateway falls back to using `backendRef` for all requests.

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

Delete the GatewayExtension, TrafficPolicy, and Backend resources that you created in this guide.

```sh
kubectl delete gatewayextension oauth-two-backends -n {{< reuse "kgw-docs/snippets/namespace.md" >}}
kubectl delete backend cognito-token -n {{< reuse "kgw-docs/snippets/namespace.md" >}}
kubectl delete backend cognito-jwks -n {{< reuse "kgw-docs/snippets/namespace.md" >}}
```