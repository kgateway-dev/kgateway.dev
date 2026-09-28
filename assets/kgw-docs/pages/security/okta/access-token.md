Protect a route by validating an access token that the client already holds. Kgateway checks the token signature against the Okta signing keys and rejects requests that do not carry a valid token, instead of redirecting them to a login page. Use this flow for API clients, which cannot follow a browser redirect.

## Before you begin

Complete the [Okta setup]({{< link-hextra path="/security/oauth/okta/setup/" >}}) page. This flow needs the Okta application, the test user, the [access policy and rule on the default authorization server]({{< link-hextra path="/security/oauth/okta/setup/#configure-default-as" >}}), the `Backend`, and the `BackendConfigPolicy` that it creates.

Unlike the authorization code flow, this flow does not need the client secret in a Kubernetes Secret, because the gateway never exchanges an authorization code. It also works over plain HTTP, because it does not use cookies.

> [!NOTE]
> This guide validates tokens issued by the default custom authorization server at `/oauth2/default`. The Org authorization server issues opaque tokens, which are not JWTs and cannot be validated. If your tokens do not contain the expected `iss` and `aud` claims, confirm that your Okta application requests tokens from the default authorization server, not the Org server.

## Configure access token validation

Create a `GatewayExtension` that tells the gateway how to validate tokens, and a `TrafficPolicy` that enforces it on a route.

1. Create a GatewayExtension for JWT validation. The `issuer` must match the token's `iss` claim from Okta, and the `audiences` list must include the token's `aud` claim.

```yaml
kubectl apply -f- <<EOF
apiVersion: {{< reuse "kgw-docs/snippets/trafficpolicy-apiversion.md" >}}
kind: GatewayExtension
metadata:
  name: okta-jwt
  namespace: {{< reuse "kgw-docs/snippets/namespace.md" >}}
spec:
  jwt:
    validationMode: Strict
    providers:
      - name: okta
        issuer: https://YOUR_OKTA_DOMAIN/oauth2/default
        jwks:
          remote:
            backendRef:
              group: gateway.kgateway.dev
              kind: Backend
              name: okta
              namespace: {{< reuse "kgw-docs/snippets/namespace.md" >}}
            url: https://YOUR_OKTA_DOMAIN/oauth2/default/v1/keys
        audiences:
          - api://default
EOF
```

| **Field** | **Description** |
| --- | --- |
| `name` | A required, unique name for the provider. The resource is rejected without it. |
| `issuer` | Must match the `iss` claim in your tokens exactly. Okta's `iss` claim for the default authorization server is `https://YOUR_OKTA_DOMAIN/oauth2/default`. Decode a real token and read its `iss` claim rather than assuming. |
| `jwks.remote.backendRef` | The network path that the gateway uses to fetch the signing keys. This is the `Backend` for Okta, so the JWKS endpoint does not have to be reachable from outside the cluster. |
| `jwks.remote.url` | The JWKS URL. For the default authorization server, this is `/oauth2/default/v1/keys`. Kgateway connects through `backendRef`, and uses this value for the request path and `Host` header. |
| `audiences` | The accepted values of the `aud` claim. A token is rejected with a `403` response if none of its audiences match. For the default authorization server, the audience is `api://default`. You can create your own authorization server and use its Identifier. You can decode a token and check its `aud` claim at [jwt.io](https://jwt.io). |

> [!NOTE]
> The `validationMode` field is optional. When set to `Strict`, the JWT policy rejects requests that do not carry a valid token. If you omit it, the default behavior may allow unauthenticated requests to pass through, which is not what you want for a protection policy.

2. Create a {{< reuse "kgw-docs/snippets/trafficpolicy.md" >}} that references the JWT GatewayExtension. Make sure that the {{< reuse "kgw-docs/snippets/trafficpolicy.md" >}} is in the same namespace as the HTTPRoute that it targets.

```yaml
kubectl apply -f- <<EOF
apiVersion: {{< reuse "kgw-docs/snippets/trafficpolicy-apiversion.md" >}}
kind: {{< reuse "kgw-docs/snippets/trafficpolicy.md" >}}
metadata:
  name: okta-jwt-policy
  namespace: httpbin
spec:
  targetRefs:
    - group: gateway.networking.k8s.io
      kind: HTTPRoute
      name: httpbin
  jwtAuth:
    extensionRef:
      name: okta-jwt
      namespace: {{< reuse "kgw-docs/snippets/namespace.md" >}}
EOF
```

3. Confirm that the {{< reuse "kgw-docs/snippets/trafficpolicy.md" >}} is attached.

```sh
kubectl get {{< reuse "kgw-docs/snippets/trafficpolicy.md" >}} okta-jwt-policy -n httpbin -o yaml
```

In the `status.ancestors` section of the output, confirm that the `Accepted` and `Attached` conditions are both `True`. An empty status means that the policy did not attach to anything.

```yaml
    - message: Policy accepted
      reason: Valid
      status: "True"
      type: Accepted
    - message: Attached to all targets
      reason: Attached
      status: "True"
      type: Attached
```

> [!IMPORTANT]
> If the [authorization code flow]({{< link-hextra path="/security/oauth/okta/authorization-code/" >}}) is also attached to the same route, the OAuth2 policy runs first. Requests from API clients that do not carry a session cookie are redirected to Okta before JWT validation runs. To test JWT validation in isolation, remove the OAuth2 policy temporarily, or point the JWT policy at a route that the OAuth2 policy does not target.

## Verify {#verify}

Use the verification steps below to confirm that the Access Token Validation flow works.

1. Get the JWKS URI from Okta:
   - The JWKS endpoint for the default authorization server is `https://YOUR_OKTA_DOMAIN/oauth2/default/v1/keys`.
   - Confirm that the value matches the `jwks.remote.url` field that you set on the `GatewayExtension`.

2. Verify that a request without a token is rejected.

{{< tabs >}}
{{% tab name="Cloud Provider LoadBalancer" %}}
```sh
curl -vi "http://$INGRESS_GW_ADDRESS:8080/headers" -H "host: www.example.com"
```

{{% /tab %}}
{{% tab name="Port-forward for local testing" %}}
```sh
curl -vi "http://localhost:8080/headers" -H "host: www.example.com"
```

{{% /tab %}}
{{< /tabs >}}

Example output:

```text
< HTTP/1.1 401 Unauthorized
```

If you instead get a `200 OK` response, the JWT policy is not attached to the route you are testing. Check the policy attachment step above, and confirm that the HTTPRoute name matches.

3. Obtain a token from Okta with the `client_credentials` grant.

Request the token from the same Okta address that you set as the `issuer` on the `GatewayExtension`. The token endpoint for the default authorization server is `/oauth2/default/v1/token`.

```bash
export TOKEN=$(curl -s -X POST "https://YOUR_OKTA_DOMAIN/oauth2/default/v1/token" \
  -d "client_id=YOUR_CLIENT_ID" \
  -d "client_secret=YOUR_CLIENT_SECRET" \
  -d "grant_type=client_credentials" \
  -d "scope=openid email profile" \
  | jq -r .access_token)
```

> [!NOTE]
> When obtaining a token from Okta:
> - The `audience` parameter is optional for the client credentials grant. If your authorization server requires an audience, add `-d "audience=api://default"`.
> - The default authorization server has audience `api://default`.
> - Client credentials requires API Access Management, which is not enabled on every Okta org. If your org does not support this grant, you can request a token through the [authorization code flow]({{< link-hextra path="/security/oauth/okta/authorization-code/" >}}) instead and use that token for the verification steps below.

4. Confirm that the token's `iss` and `aud` claims match your `GatewayExtension`. Decode the payload.

```sh
echo $TOKEN | jq -rR 'split(".")[1] | @base64d' | jq '{iss, aud}'
```

Example output. If `aud` does not include your expected audience, update the `audiences` list in your `GatewayExtension`.

```json
{
  "iss": "https://YOUR_OKTA_DOMAIN/oauth2/default",
  "aud": ["api://default"]
}
```

5. Send a request with the token in the `Authorization` header.

{{< tabs >}}
{{% tab name="Cloud Provider LoadBalancer" %}}
```bash
curl -vi "http://$INGRESS_GW_ADDRESS:8080/headers" \
  -H "host: www.example.com" \
  -H "Authorization: Bearer $TOKEN"
```

{{% /tab %}}
{{% tab name="Port-forward for local testing" %}}
```bash
curl -vi "http://localhost:8080/headers" \
  -H "host: www.example.com" \
  -H "Authorization: Bearer $TOKEN"
```

{{% /tab %}}
{{< /tabs >}}

A successful response shows the headers from the httpbin app.

```text
< HTTP/1.1 200 OK
```

If you get a `403` response, the token is valid but its `aud` claim does not match the `audiences` list. Update the `audiences` field in your `GatewayExtension`.

If you get a `401` response, the token is missing, expired, or signed by an issuer that does not match `issuer`. The error message in the response body tells you which one:

| Message | Meaning |
| --- | --- |
| `Jwt is missing` | No `Authorization: Bearer` header was sent. |
| `Jwt is not in the form of Header.Payload.Signature with two dots and 3 sections` | The token is not a JWT. This usually means it was issued by the Org authorization server as an opaque token, or the header value was truncated. |
| `Jwt verification fails` | The signature does not match any of the JWKS keys, or the issuer or audience does not match the JWT policy. |

## Cleanup {#cleanup}

{{< reuse "kgw-docs/snippets/cleanup.md" >}}

```sh
kubectl delete {{< reuse "kgw-docs/snippets/trafficpolicy.md" >}} okta-jwt-policy -n httpbin
kubectl delete GatewayExtension okta-jwt -n {{< reuse "kgw-docs/snippets/namespace.md" >}}
```

To remove Okta and the shared resources, see the Cleanup section of the [Okta setup]({{< link-hextra path="/security/oauth/okta/setup/#cleanup" >}}) page.