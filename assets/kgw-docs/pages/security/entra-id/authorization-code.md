Protect a route with the OAuth2 authorization code flow. When a browser request is unauthenticated, the gateway redirects it to Microsoft Entra ID. After login, the gateway exchanges the authorization code for tokens and stores them in session cookies. Your upstream service does not need to handle the OAuth2 flow.

## Before you begin

1. Complete the [Microsoft Entra ID setup]({{< link-hextra path="/security/oauth/entra-id/setup/" >}}) page. This flow needs the Entra ID App Registration, the test user, the API scope, the `Backend`, and the `BackendConfigPolicy` that it creates.

2. Make sure your gateway has an **HTTPS listener**. Kgateway marks the OAuth2 nonce and code verifier cookies as `Secure`, so browsers do not send them over HTTP. Without those cookies, callback validation fails. To add an HTTPS listener, see [HTTPS listener]({{< link-hextra path="/setup/listeners/https/" >}}). The access token validation flow works over HTTP because it does not use cookies.

## Configure the authorization code flow

Create the Kubernetes Secret that holds the Entra ID client secret, a `GatewayExtension` that configures the provider, and a `TrafficPolicy` that enforces the flow on a route.

1. Create a Kubernetes Secret with the Entra ID client secret. Replace `YOUR_CLIENT_SECRET` with the value that you copied from the **Certificates & secrets** section of your App Registration during [Entra ID setup]({{< link-hextra path="/security/oauth/entra-id/setup/" >}}).

   ```sh
   kubectl create secret generic entra-id-client-secret \
     --from-literal=client-secret=YOUR_CLIENT_SECRET \
     -n {{< reuse "kgw-docs/snippets/namespace.md" >}}
   ```

2. Create a GatewayExtension that holds everything the gateway needs to talk to Entra ID.

   > [!IMPORTANT]
   > **Entra ID uses v1.0 endpoints:** Because we configured a custom API scope, Entra ID issues v1.0 tokens. The `issuerURI` must point to the v1.0 endpoint (`sts.windows.net`), not the standard `/v2.0` path. If you use the v2.0 paths, token validation will fail.

   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.kgateway.dev/v1alpha1
   kind: GatewayExtension
   metadata:
     name: entra-id-oauth2
     namespace: {{< reuse "kgw-docs/snippets/namespace.md" >}}
   spec:
     oauth2:
       backendRef:
         group: gateway.kgateway.dev
         kind: Backend
         name: entra-id
         namespace: {{< reuse "kgw-docs/snippets/namespace.md" >}}
       issuerURI: https://sts.windows.net/YOUR_TENANT_ID/
       authorizationEndpoint: https://login.microsoftonline.com/YOUR_TENANT_ID/oauth2/authorize
       tokenEndpoint: https://login.microsoftonline.com/YOUR_TENANT_ID/oauth2/token
       endSessionEndpoint: https://login.microsoftonline.com/YOUR_TENANT_ID/oauth2/logout
       redirectURI: https://www.example.com/oauth2/redirect
       scopes:
         - openid
         - email
         - profile
         - api://YOUR_CLIENT_ID/access_as_user
       credentials:
         clientID: YOUR_CLIENT_ID
         clientSecretRef:
           name: entra-id-client-secret
   EOF
   ```

   | **Field** | **Description** |
| :--- | :--- |
| `backendRef` | Points to the `Backend` from [Entra ID setup]({{< link-hextra path="/security/oauth/entra-id/setup/#create-backend" >}}). Kgateway uses it to reach Entra ID for token exchange and OIDC discovery. |
| `issuerURI` | For v1.0 tokens, this must be `https://sts.windows.net/{tenant-id}/`. |
| `authorizationEndpoint` | The Entra ID endpoint that the gateway redirects browser users to for login. |
| `tokenEndpoint` | The Entra ID endpoint that the gateway calls to exchange the authorization code for tokens. |
| `redirectURI` | The callback URL that kgateway sends to Entra ID as the `redirect_uri` parameter. This must match the URI registered in your App Registration exactly. |
| `scopes` | Must include `openid` for OIDC. If you are using the access token validation flow, include your custom scope (such as,`api://{client-id}/access_as_user`). |
| `endSessionEndpoint` | Handles single logout. |
| `clientSecretRef.name` | Must match the Secret name from the previous step. |


3. Create a {{< reuse "kgw-docs/snippets/trafficpolicy.md" >}} that references the extension by name.

   > [!WARNING]
   > The OAuth2 filter does not protect against CSRF attacks on routes with cached authentication cookies. Pair it with a `CSRFPolicy` on the same route.


```yaml
kubectl apply -f- <<EOF
apiVersion: {{< reuse "kgw-docs/snippets/trafficpolicy-apiversion.md" >}}
kind: {{< reuse "kgw-docs/snippets/trafficpolicy.md" >}}
metadata:
  name: entra-id-oauth2-policy
  namespace: httpbin
spec:
  targetRefs:
    - group: gateway.networking.k8s.io
      kind: HTTPRoute
      name: httpbin
  oauth2:
    extensionRef:
      name: entra-id-oauth2
      namespace: {{< reuse "kgw-docs/snippets/namespace.md" >}}
EOF
```


4. Verify that the policy is attached to the route.

   ```sh
   kubectl get {{< reuse "kgw-docs/snippets/trafficpolicy.md" >}} entra-id-oauth2-policy -n httpbin -o yaml
   ```

   In the `status.ancestors` section, confirm that both the `Accepted` and `Attached` conditions are `True`.

## Verify {#verify}

1. Send a request without a session cookie. The gateway redirects to Entra ID.

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

   Example output. The `redirect_uri` parameter matches the value registered on the Entra ID App Registration.

   ```text
   < HTTP/2 302
   < location: https://login.microsoftonline.com/YOUR_TENANT_ID/oauth2/authorize?client_id=YOUR_CLIENT_ID&...&redirect_uri=https%3A%2F%2Fwww.example.com%2Foauth2%2Fredirect
   < set-cookie: OauthNonce-...;path=/;Max-Age=600;secure;HttpOnly
   ```

2. Open a browser and go to your protected route, such as `https://www.example.com/headers`. The gateway redirects you to the Microsoft login page.

3. Log in with the test user credentials you created in the [Entra ID setup]({{< link-hextra path="/security/oauth/entra-id/setup/#create-test-user" >}}).

4. Verify that Entra ID returns you to the route and that the response shows the httpbin output.

   If you get a `401` response with `CSRF token validation failed` in the gateway logs, you sent the request over HTTP. Retry over HTTPS.

   If Entra ID shows `AADSTS50011: The redirect URI ... specified in the request does not match the redirect URIs configured for the application`, the `redirectURI` on the `GatewayExtension` does not match what is registered in your App Registration.


## Cleanup {#cleanup}

{{< reuse "kgw-docs/snippets/cleanup.md" >}}

```sh
kubectl delete {{< reuse "kgw-docs/snippets/trafficpolicy.md" >}} entra-id-oauth2-policy -n httpbin
kubectl delete GatewayExtension entra-id-oauth2 -n {{< reuse "kgw-docs/snippets/namespace.md" >}}
kubectl delete secret entra-id-client-secret -n {{< reuse "kgw-docs/snippets/namespace.md" >}}
```

To remove Entra ID and the shared resources, see the Cleanup section of the [Entra ID setup]({{< link-hextra path="/security/oauth/entra-id/setup/#cleanup" >}}) page.

