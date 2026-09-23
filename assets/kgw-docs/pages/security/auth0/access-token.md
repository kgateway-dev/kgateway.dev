Protect a route by validating an access token that the client already holds. Kgateway checks the token signature against the Auth0 signing keys and rejects requests that do not carry a valid token, instead of redirecting them to a login page. Use this flow for API clients, which cannot follow a browser redirect.

## Before you begin

Complete the [Auth0 setup]({{< link-hextra path="/security/oauth/auth0/setup/" >}}) page. This flow needs the Auth0 application, the test user, the `Backend`, and the `BackendConfigPolicy` that it creates, and it needs the [Auth0 API]({{< link-hextra path="/security/oauth/auth0/setup/#create-api" >}}) whose Identifier the tokens carry in the `aud` claim.

Unlike the authorization code flow, this flow does not need the client secret in a Kubernetes Secret, because the gateway never exchanges an authorization code. It also works over plain HTTP, because it does not use cookies.

## Configure access token validation

Create a `GatewayExtension` that tells the gateway how to validate tokens, and a {{< reuse "kgw-docs/snippets/trafficpolicy.md" >}} that enforces it on a route.

1. Create a GatewayExtension for JWT validation. The `issuer` must match the token's `iss` claim from Auth0.

   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.kgateway.dev/v1alpha1
   kind: GatewayExtension
   metadata:
     name: auth0-jwt
     namespace: {{< reuse "kgw-docs/snippets/namespace.md" >}}
   spec:
     jwt:
       providers:
         - name: auth0
           issuer: https://YOUR_AUTH0_DOMAIN/
           jwks:
             remote:
               backendRef:
                 group: gateway.kgateway.dev
                 kind: Backend
                 name: auth0
                 namespace: {{< reuse "kgw-docs/snippets/namespace.md" >}}
               url: https://YOUR_AUTH0_DOMAIN/.well-known/jwks.json
           audiences:
             - YOUR_API_AUDIENCE
   EOF
   ```

   | Field | Description |
   |-------|-------------|
   | `name` | A required, unique name for the provider. The resource is rejected without it. |
   | `issuer` | Must match the `iss` claim in your tokens exactly. Auth0 derives `iss` from your Auth0 domain and includes the trailing slash. Decode a real token and read its `iss` claim rather than assuming. |
   | `jwks.remote.backendRef` | The network path that the gateway uses to fetch the signing keys. This is the `Backend` for Auth0, so the JWKS endpoint does not have to be reachable from outside the cluster. |
   | `jwks.remote.url` | The JWKS URL. Kgateway connects through `backendRef`, and uses this value for the request path and `Host` header. |
   | `audiences` | The accepted values of the `aud` claim. A token is rejected with a `403` response if none of its audiences match. Use the **Identifier** of the Auth0 API that you created in [Auth0 setup]({{< link-hextra path="/security/oauth/auth0/setup/#create-api" >}}), not the Management API. Auth0 puts the `audience` value from the token request into this claim, so the two must agree. You can decode a token and check its `aud` claim at [jwt.io](https://www.jwt.io/). |

2. Create a {{< reuse "kgw-docs/snippets/trafficpolicy.md" >}} that references the JWT GatewayExtension. Make sure that the {{< reuse "kgw-docs/snippets/trafficpolicy.md" >}} is in the same namespace as the HTTPRoute that it targets.

   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: {{< reuse "kgw-docs/snippets/trafficpolicy-apiversion.md" >}}
   kind: {{< reuse "kgw-docs/snippets/trafficpolicy.md" >}}
   metadata:
     name: auth0-jwt-policy
     namespace: httpbin
   spec:
     targetRefs:
       - group: gateway.networking.k8s.io
         kind: HTTPRoute
         name: httpbin
     jwtAuth:
       extensionRef:
         name: auth0-jwt
         namespace: {{< reuse "kgw-docs/snippets/namespace.md" >}}
   EOF
   ```

3. Confirm that the {{< reuse "kgw-docs/snippets/trafficpolicy.md" >}} is attached.

   ```sh
   kubectl get {{< reuse "kgw-docs/snippets/trafficpolicy.md" >}} auth0-jwt-policy -n httpbin -o yaml
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

## Verify {#verify}

Use the verification steps below to confirm that the access token validation flow works.

1. Confirm the JWKS URI. Auth0 always serves it at `/.well-known/jwks.json` on your Auth0 domain, and it must match the `jwks.remote.url` field that you set on the `GatewayExtension`.

   ```text
   https://YOUR_AUTH0_DOMAIN/.well-known/jwks.json
   ```

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

3. Obtain a token from Auth0 with the `password` grant. Request the token from the same Auth0 address that you set as the `issuer` on the `GatewayExtension`, and pass the API Identifier as the `audience` so that the token carries it in the `aud` claim.

   ```sh
   export TOKEN=$(curl -s -X POST "https://YOUR_AUTH0_DOMAIN/oauth/token" \
     -d "client_id=YOUR_CLIENT_ID" \
     -d "client_secret=YOUR_CLIENT_SECRET" \
     -d "username=testuser@example.com" \
     -d "password=YOUR_PASSWORD" \
     -d "grant_type=password" \
     -d "audience=YOUR_API_AUDIENCE" \
     | jq -r .access_token)
   ```

   > [!NOTE]
   > If your tenant has more than one database connection, add `-d "connection=YOUR_CONNECTION_NAME"` to the token request, or set the **Default Directory** on the application as described in [Auth0 setup]({{< link-hextra path="/security/oauth/auth0/setup/" >}}).

4. Confirm that the token's `iss` and `aud` claims match your `GatewayExtension`. Decode the payload.

   ```sh
   echo $TOKEN | jq -rR 'split(".")[1] | @base64d' | jq '{iss, aud}'
   ```

   Example output. If `aud` does not include your API Identifier, check the `audience` value that you passed to the token endpoint.

   ```json
   {
     "iss": "https://YOUR_AUTH0_DOMAIN/",
     "aud": ["https://my-api.example.com"]
   }
   ```

5. Send a request with the token in the `Authorization` header.

   {{< tabs >}}
   {{% tab name="Cloud Provider LoadBalancer" %}}
   ```sh
   curl -vi "http://$INGRESS_GW_ADDRESS:8080/headers" \
     -H "host: www.example.com" \
     -H "Authorization: Bearer $TOKEN"
   ```
   {{% /tab %}}
   {{% tab name="Port-forward for local testing" %}}
   ```sh
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

   A `403` response means that the token is valid but its `aud` claim does not match the `audiences` list. A `401` response means that the token is missing, expired, or signed by an issuer that does not match `issuer`.

## Cleanup {#cleanup}

{{< reuse "kgw-docs/snippets/cleanup.md" >}}

```sh
kubectl delete {{< reuse "kgw-docs/snippets/trafficpolicy.md" >}} auth0-jwt-policy -n httpbin
kubectl delete GatewayExtension auth0-jwt -n {{< reuse "kgw-docs/snippets/namespace.md" >}}
```

To remove Auth0 and the shared resources, see the Cleanup section of the [Auth0 setup]({{< link-hextra path="/security/oauth/auth0/setup/#cleanup" >}}) page.
