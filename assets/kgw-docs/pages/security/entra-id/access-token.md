Protect a route by validating an access token that the client already holds. Kgateway checks the token signature against Microsoft Entra ID's signing keys. It rejects requests without a valid token instead of redirecting them to a login page. Use this flow for API clients that cannot follow browser redirects.

## Before you begin

Complete the [Microsoft Entra ID setup]({{< link-hextra path="/security/oauth/entra-id/setup/" >}}) page. This flow needs the Entra ID App Registration, the test user, the API scope, the `Backend`, and the `BackendConfigPolicy` created during setup.

This flow does not need the client secret in a Kubernetes Secret. The gateway does not exchange an authorization code. The flow also works over HTTP because it does not use cookies.

> [!IMPORTANT]
> By default, Entra ID issues **v1.0 access tokens** for an API that you expose on your App Registration. A v1.0 token has the `iss` claim `https://sts.windows.net/{tenant-id}/` and an `aud` claim of your Application ID URI, such as `api://{client-id}`. Its signing keys are at `https://login.microsoftonline.com/{tenant-id}/discovery/keys`. These values differ from the v2.0 values (`/v2.0` and `/discovery/v2.0/keys`), so use the v1.0 values in the access token validation flow. To get v2.0 tokens instead, set `requestedAccessTokenVersion` to `2` in the App Registration manifest.

## Configure access token validation

Create a `GatewayExtension` to configure token validation. Then create a `TrafficPolicy` to enforce validation on a route.

1. Create a GatewayExtension for JWT validation. The `issuer` must match the token's `iss` claim from Entra ID. The `audiences` list must include the token's `aud` claim (which is your custom API scope).

   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.kgateway.dev/v1alpha1
   kind: GatewayExtension
   metadata:
     name: entra-id-jwt
     namespace: {{< reuse "kgw-docs/snippets/namespace.md" >}}
   spec:
     jwt:
       validationMode: Strict
       providers:
         - name: entra-id
           issuer: https://sts.windows.net/YOUR_TENANT_ID/
           jwks:
             remote:
               backendRef:
                 group: gateway.kgateway.dev
                 kind: Backend
                 name: entra-id
                 namespace: {{< reuse "kgw-docs/snippets/namespace.md" >}}
               url: https://login.microsoftonline.com/YOUR_TENANT_ID/discovery/keys
           audiences:
             - api://YOUR_CLIENT_ID
   EOF
   ```
   
   | **Field** | **Description** |
   | :--- | :--- |
   | `name` | A required, unique name for the provider. |
   | `issuer` | Must exactly match the `iss` claim in your tokens. For v1.0 tokens, use `https://sts.windows.net/{tenant-id}/`. |
   | `jwks.remote.backendRef` | The `Backend` that the gateway uses to fetch the signing keys. |
   | `jwks.remote.url` | The JWKS URL. For v1.0 tokens, use `https://login.microsoftonline.com/{tenant-id}/discovery/keys`. |
   | `audiences` | Accepted values for the `aud` claim. Use your Application ID URI, such as `api://YOUR_CLIENT_ID`. |

   > [!NOTE]
   > The `validationMode` field is optional and defaults to `Strict`. This mode requires a valid JWT on every request. Set it to `AllowMissing` only if you want requests without a token to pass through. Pair that mode with an authorization policy that restricts those requests.


2. Create a {{< reuse "kgw-docs/snippets/trafficpolicy.md" >}} that references the JWT GatewayExtension. Make sure that the {{< reuse "kgw-docs/snippets/trafficpolicy.md" >}} is in the same namespace as the HTTPRoute that it targets.

   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: {{< reuse "kgw-docs/snippets/trafficpolicy-apiversion.md" >}}
   kind: {{< reuse "kgw-docs/snippets/trafficpolicy.md" >}}
   metadata:
     name: entra-id-jwt-policy
     namespace: httpbin
   spec:
     targetRefs:
       - group: gateway.networking.k8s.io
         kind: HTTPRoute
         name: httpbin
     jwtAuth:
       extensionRef:
         name: entra-id-jwt
         namespace: {{< reuse "kgw-docs/snippets/namespace.md" >}}
   EOF
   ```

3. Confirm that the {{< reuse "kgw-docs/snippets/trafficpolicy.md" >}} is attached.

   ```sh
   kubectl get {{< reuse "kgw-docs/snippets/trafficpolicy.md" >}} entra-id-jwt-policy -n httpbin -o yaml
   ```

   In the `status.ancestors` section, confirm that both the `Accepted` and `Attached` conditions are `True`.

   > [!IMPORTANT]
   > If the [authorization code flow]({{< link-hextra path="/security/oauth/entra-id/authorization-code/" >}}) also targets this route, the OAuth2 policy runs first. API requests without a session cookie are redirected to Entra ID before JWT validation runs. To test JWT validation alone, temporarily remove the OAuth2 policy or target a different route with the JWT policy.


## Verify {#verify}

Verify the access token validation flow with these steps.

1. Verify that a request without a token is rejected.

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

2. Obtain an access token from the Entra ID authorization server.

   The JWT policy validates the signature, issuer, and audience of the token that you present. Complete the [authorization code flow]({{< link-hextra path="/security/oauth/entra-id/authorization-code/" >}}) in a browser. Then copy the value of the `AccessToken-<suffix>` cookie that the gateway sets, such as `AccessToken-a1b2c3d4`.

   ```sh
   export TOKEN=<access-token-cookie-value>
   ```

3. Confirm that the token's `iss` and `aud` claims match your `GatewayExtension`.

   ```sh
   echo $TOKEN | jq -rR 'split(".")[1] | gsub("-"; "+") | gsub("_"; "/") | @base64d | fromjson | {iss, aud, ver}'
   ```

   Example output for a v1.0 token:

   ```json
   {
     "iss": "https://sts.windows.net/YOUR_TENANT_ID/",
     "aud": "api://YOUR_CLIENT_ID",
     "ver": "1.0"
   }
   ```
                        
4. Send a request with the token in the `Authorization` header.

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

   | **Message** | **Meaning** |
   | :--- | :--- |
   | `Jwt is missing` | No `Authorization: Bearer` header was sent. |
   | `Jwt verification fails` | The signature does not match a JWKS key, or the issuer or audience does not match the JWT policy. Double-check that you used the v1.0 `issuer` and `jwks` endpoints. |


## Cleanup {#cleanup}

{{< reuse "kgw-docs/snippets/cleanup.md" >}}

```sh
kubectl delete {{< reuse "kgw-docs/snippets/trafficpolicy.md" >}} entra-id-jwt-policy -n httpbin
kubectl delete GatewayExtension entra-id-jwt -n {{< reuse "kgw-docs/snippets/namespace.md" >}}
```

To remove Entra ID and the shared resources, see the Cleanup section of the [Entra ID setup]({{< link-hextra path="/security/oauth/entra-id/setup/#cleanup" >}}) page.