Protect a route by validating an access token that the client already holds. Kgateway checks the token signature against Okta's signing keys. It rejects requests without a valid token instead of redirecting them to a login page. Use this flow for API clients that cannot follow browser redirects.

## Before you begin

Complete the [Okta setup]({{< link-hextra path="/security/oauth/okta/setup/" >}}) page. This flow needs the Okta application and test user, the [access policy and rule on the default authorization server]({{< link-hextra path="/security/oauth/okta/setup/#configure-default-as" >}}), and the `Backend` and `BackendConfigPolicy` created during setup.

This flow does not need the client secret in a Kubernetes Secret. The gateway does not exchange an authorization code. The flow also works over HTTP because it does not use cookies.

> [!NOTE]
> This guide validates tokens issued by the custom authorization server named `default`, at `/oauth2/default`. Do not validate tokens from the Org authorization server. Okta says that those tokens "aren't intended for validation or use by your own apps or resource servers." Their contents are also "subject to change at any time without notice." If your tokens do not carry the expected `iss` and `aud` claims, confirm that your application requests them from the `default` authorization server.

## Configure access token validation

Create a `GatewayExtension` to configure token validation. Then create a `TrafficPolicy` to enforce validation on a route.

1. Create a GatewayExtension for JWT validation. The `issuer` must match the token's `iss` claim from Okta. The `audiences` list must include the token's `aud` claim.

   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.kgateway.dev/v1alpha1
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
   | `issuer` | Must match the `iss` claim in your tokens exactly. For the default authorization server, Okta uses `https://YOUR_OKTA_DOMAIN/oauth2/default`. Decode a real token and check its `iss` claim. |
   | `jwks.remote.backendRef` | The `Backend` that the gateway uses to fetch the signing keys. The JWKS endpoint does not need to be reachable from outside the cluster. |
   | `jwks.remote.url` | The JWKS URL. For the default authorization server, use `/oauth2/default/v1/keys`. Kgateway connects through `backendRef` and uses this URL for the request path and `Host` header. |
   | `audiences` | Accepted values for the `aud` claim. The gateway rejects a token if none of its audiences match. The default authorization server uses `api://default`. You can use the Identifier from your own authorization server instead. Decode a token and check its `aud` claim at [jwt.io](https://jwt.io). |

   > [!NOTE]
   > The `validationMode` field is optional and defaults to `Strict`. This mode requires a valid JWT on every request. The guide sets it explicitly to make the intent clear. Set it to `AllowMissing` only if you want requests without a token to pass through. Pair that mode with an authorization policy that restricts those requests.

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

   In the `status.ancestors` section, confirm that both the `Accepted` and `Attached` conditions are `True`. An empty status means that the policy did not attach to anything.

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
   > If the [authorization code flow]({{< link-hextra path="/security/oauth/okta/authorization-code/" >}}) also targets this route, the OAuth2 policy runs first. API requests without a session cookie are redirected to Okta before JWT validation runs. To test JWT validation alone, temporarily remove the OAuth2 policy or target a different route with the JWT policy.

## Verify {#verify}

Verify the access token validation flow with these steps.

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

   If you get `200 OK`, the JWT policy is not attached to the route. Check the policy attachment step and confirm that the HTTPRoute name matches.

3. Obtain an access token from the `default` authorization server.

   The JWT policy validates the signature, issuer, and audience of the token you present. It does not depend on which grant produced the token. Use an option supported by your Okta org, and request the token from the same Okta address that you set as the `issuer` on the `GatewayExtension`.

   * **Authorization code flow**: Complete the [authorization code flow]({{< link-hextra path="/security/oauth/okta/authorization-code/" >}}) in a browser. Then copy the value of the `AccessToken` cookie set by the gateway.

   ```sh
   export TOKEN=<access-token-cookie-value>
   ```

   * **Client credentials grant**: Request the token from `/oauth2/default/v1/token`. This grant has no user context, so Okta does not accept reserved OIDC scopes such as `openid`, `email`, and `profile`. [Add a custom scope](https://developer.okta.com/docs/guides/implement-grant-type/clientcreds/main/) to the `default` authorization server, then request that scope.

   ```bash
   export TOKEN=$(curl -s -X POST "https://YOUR_OKTA_DOMAIN/oauth2/default/v1/token" \
     -d "client_id=YOUR_CLIENT_ID" \
     -d "client_secret=YOUR_CLIENT_SECRET" \
     -d "grant_type=client_credentials" \
     -d "scope=YOUR_CUSTOM_SCOPE" \
     | jq -r .access_token)
   ```

   > [!NOTE]
   > The client credentials grant requires API Access Management. Not every Okta org has this feature. If yours does not, use the authorization code flow to obtain a token.

4. Confirm that the token's `iss` and `aud` claims match your `GatewayExtension`. Decode the payload.

   ```sh
   echo $TOKEN | jq -rR 'split(".")[1] | @base64d' | jq '{iss, aud}'
   ```

   Example output. If `aud` does not include the expected audience, update the `audiences` list in your `GatewayExtension`.

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

   If the request is rejected, check the response body for the reason:

   | Message | Meaning |
   | --- | --- |
   | `Jwt is missing` | No `Authorization: Bearer` header was sent. |
   | `Jwt is not in the form of Header.Payload.Signature with two dots and 3 sections` | The `Authorization` header value is not a JWT. Check that the token came from the `/oauth2/default` authorization server. Also check that it was not truncated when copied. |
   | `Jwt verification fails` | The signature does not match a JWKS key, or the issuer or audience does not match the JWT policy. |

## Cleanup {#cleanup}

{{< reuse "kgw-docs/snippets/cleanup.md" >}}

```sh
kubectl delete {{< reuse "kgw-docs/snippets/trafficpolicy.md" >}} okta-jwt-policy -n httpbin
kubectl delete GatewayExtension okta-jwt -n {{< reuse "kgw-docs/snippets/namespace.md" >}}
```

To remove Okta and the shared resources, see the Cleanup section of the [Okta setup]({{< link-hextra path="/security/oauth/okta/setup/#cleanup" >}}) page.
