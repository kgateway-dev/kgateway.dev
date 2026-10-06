Protect a route with the OAuth2 authorization code flow. When a browser request is unauthenticated, the gateway redirects it to Okta. After login, the gateway exchanges the authorization code for tokens and stores them in session cookies. Your upstream service does not need to handle the OAuth2 flow.

## Before you begin

1. Complete the [Okta setup]({{< link-hextra path="/security/oauth/okta/setup/" >}}) page. This flow needs the Okta application, the test user, the [access policy and rule on the default authorization server]({{< link-hextra path="/security/oauth/okta/setup/#configure-default-as" >}}), the `Backend`, and the `BackendConfigPolicy` that it creates.

2. Make sure your gateway has an **HTTPS listener**. Kgateway marks the OAuth2 nonce and code verifier cookies as `Secure`, so browsers do not send them over HTTP. Without those cookies, callback validation fails. To add an HTTPS listener, see [HTTPS listener]({{< link-hextra path="/setup/listeners/https/" >}}). The access token validation flow works over HTTP because it does not use cookies.

## Configure the authorization code flow

Create the Kubernetes Secret that holds the Okta client secret, a `GatewayExtension` that configures the provider, and a `TrafficPolicy` that enforces the flow on a route.

1. Create a Kubernetes Secret with the Okta client secret. Kgateway reads the value from the `client-secret` key specifically, so the key name matters. Replace `YOUR_CLIENT_SECRET` with the value that you copied from the **General** tab of your Okta application during [Okta setup]({{< link-hextra path="/security/oauth/okta/setup/" >}}).

   ```sh
   kubectl create secret generic okta-client-secret \
     --from-literal=client-secret=YOUR_CLIENT_SECRET \
     -n {{< reuse "kgw-docs/snippets/namespace.md" >}}
   ```

2. Create a GatewayExtension that holds everything the gateway needs to talk to Okta. The GatewayExtension is independent of routing, so you can reuse the same extension across multiple {{< reuse "kgw-docs/snippets/trafficpolicy.md" >}} resources.

   > [!NOTE]
   > This guide uses the custom authorization server named `default`, at `/oauth2/default`, not the Org authorization server. A custom authorization server lets you control the audience and token contents that the gateway validates. Use `/oauth2/default` in all issuer and endpoint values below. If you also use the [access token validation]({{< link-hextra path="/security/oauth/okta/access-token/" >}}) flow, use the same issuer and audience in both configurations.
   >
   > The `redirectURI` must match the exact value you register in Okta's **Sign-in redirect URIs**. The gateway still reaches Okta through `backendRef`, so the two do not have to be the same address.

   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.kgateway.dev/v1alpha1
   kind: GatewayExtension
   metadata:
     name: okta-oauth2
     namespace: {{< reuse "kgw-docs/snippets/namespace.md" >}}
   spec:
     oauth2:
       backendRef:
         group: gateway.kgateway.dev
         kind: Backend
         name: okta
         namespace: {{< reuse "kgw-docs/snippets/namespace.md" >}}
       issuerURI: https://YOUR_OKTA_DOMAIN/oauth2/default
       authorizationEndpoint: https://YOUR_OKTA_DOMAIN/oauth2/default/v1/authorize
       tokenEndpoint: https://YOUR_OKTA_DOMAIN/oauth2/default/v1/token
       endSessionEndpoint: https://YOUR_OKTA_DOMAIN/oauth2/default/v1/logout
       redirectURI: https://www.example.com/oauth2/redirect
       scopes:
         - openid
         - email
         - profile
       credentials:
         clientID: YOUR_CLIENT_ID
         clientSecretRef:
           name: okta-client-secret
   EOF
   ```

   | **Field** | **Description** |
   | --- | --- |
   | `backendRef` | Points to the `Backend` from [Okta setup]({{< link-hextra path="/security/oauth/okta/setup/#create-backend" >}}). Kgateway uses it to reach Okta for token exchange and OIDC discovery. |
   | `issuerURI` | Triggers OIDC discovery. Kgateway fetches `/.well-known/openid-configuration` from this URL and fills in the authorization, token, and end-session endpoints. If you also set those explicitly (as in the example), the explicit values win. Setting both is fine if you want the config to be readable without relying on discovery. |
   | `authorizationEndpoint` | The Okta endpoint that the gateway redirects browser users to for login. For the default authorization server, this is `/oauth2/default/v1/authorize`. |
   | `tokenEndpoint` | The Okta endpoint that the gateway calls to exchange the authorization code for tokens. For the default authorization server, this is `/oauth2/default/v1/token`. |
   | `redirectURI` | The callback URL that kgateway sends to Okta as the `redirect_uri` parameter. The gateway also intercepts this path to complete the code exchange. If you omit this field, kgateway derives it from the original request scheme and host. The default is `<request-scheme>://<host>/oauth2/redirect`, which might not match the URI registered in Okta. Set the field explicitly. |
   | `scopes` | Defaults to `user` if not set. For OIDC you need `openid` in the list. Add `email` and `profile` if your app needs those claims. |
   | `endSessionEndpoint` | Handles single logout. When a user hits `/logout`, kgateway clears their session cookies and sends their browser to this URL so Okta ends the session too. This is RP-initiated logout in the OIDC spec. Only set it if `openid` is in your scopes. For the default authorization server, this is `/oauth2/default/v1/logout`. |
   | `clientSecretRef.name` | Must match the Secret name from the previous step. Kgateway reads the `client-secret` key inside that Secret. |

3. Create a {{< reuse "kgw-docs/snippets/trafficpolicy.md" >}} that references the extension by name. This policy tells the gateway to enforce the login flow on a specific route.

   > [!WARNING]
   > The OAuth2 filter does not protect against CSRF attacks on routes with cached authentication cookies. Pair it with a `CSRFPolicy` on the same route, especially for browser-facing apps.

   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: {{< reuse "kgw-docs/snippets/trafficpolicy-apiversion.md" >}}
   kind: {{< reuse "kgw-docs/snippets/trafficpolicy.md" >}}
   metadata:
     name: okta-oauth2-policy
     namespace: httpbin
   spec:
     targetRefs:
       - group: gateway.networking.k8s.io
         kind: HTTPRoute
         name: httpbin
     oauth2:
       extensionRef:
         name: okta-oauth2
         namespace: {{< reuse "kgw-docs/snippets/namespace.md" >}}
   EOF
   ```

   > [!IMPORTANT]
   > `targetRefs` has no `namespace` field. The {{< reuse "kgw-docs/snippets/trafficpolicy.md" >}} can target only resources in its own namespace, so create the policy alongside the resource you want to protect. The HTTPRoute from the [Sample app guide]({{< link-hextra path="/install/sample-app/" >}}) is in the `httpbin` namespace, so create the policy there. By contrast, `extensionRef` includes a `namespace` field, so the GatewayExtension can stay in `{{< reuse "kgw-docs/snippets/namespace.md" >}}`.
   >
   > If the namespaces do not match, the policy is accepted but does not attach. Requests then reach your app unauthenticated. Verify that the policy attached before you rely on it.
   >
   > `targetRefs` can also point to a Gateway, which applies the policy to every route that the Gateway serves. In that case, create the policy in the Gateway's namespace.

4. Verify that the policy attached to the route.

   ```sh
   kubectl get {{< reuse "kgw-docs/snippets/trafficpolicy.md" >}} okta-oauth2-policy -n httpbin -o yaml
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

   If your HTTPRoute uses a `PathPrefix` or `Exact` match, it must also match the OAuth2 callback path that you set in `redirectURI`. Otherwise, the redirect back from Okta returns a 404 error.

   The HTTPRoute from the [Sample app guide]({{< link-hextra path="/install/sample-app/" >}}) has no path matches, so it already serves every path and needs no change.

   > [!NOTE]
   > If your route matches only `/status`, add the callback path as a second match:
   >
   > ```yaml
   > rules:
   >   - matches:
   >       - path:
   >           type: PathPrefix
   >           value: /status
   >       - path:
   >           type: PathPrefix
   >           value: /oauth2/redirect
   > ```

## Verify {#verify}

Send these requests to the HTTPS listener. This flow relies on session cookies with the `Secure` attribute.

1. Send a request without a session cookie. The gateway redirects to Okta.

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

   Example output. The `redirect_uri` parameter matches the value registered on the Okta application. The authorization endpoint is under `/oauth2/default`.

   ```text
   < HTTP/2 302
   < location: https://YOUR_OKTA_DOMAIN/oauth2/default/v1/authorize?client_id=YOUR_CLIENT_ID&...&redirect_uri=https%3A%2F%2Fwww.example.com%2Foauth2%2Fredirect
   < set-cookie: OauthNonce-...;path=/;Max-Age=600;secure;HttpOnly
   ```

2. Open a browser and go to your protected route, such as `https://www.example.com/headers`. The gateway redirects you to the Okta login page.

3. Log in with the test user credentials you created in the [Okta setup]({{< link-hextra path="/security/oauth/okta/setup/#create-test-user" >}}).

4. Verify that Okta returns you to the route and that the response shows the httpbin output. The gateway exchanges the authorization code for tokens and stores them in session cookies.

   If Okta shows the message that the user is not allowed to access the app, the access policy or rule on the default authorization server is missing or does not include `kgateway-app`. See [Configure the default authorization server]({{< link-hextra path="/security/oauth/okta/setup/#configure-default-as" >}}).

   If you get a `401` response with `CSRF token validation failed` in the gateway logs, you sent the request over HTTP. Retry over HTTPS.

   If Okta shows `The 'redirect_uri' parameter must be a Login redirect URI in the client app settings`, the `redirectURI` on the `GatewayExtension` does not match a redirect URI that is registered on the Okta application.

5. Optional: If you added the [`denyRedirect` setting](#deny-redirect) to your GatewayExtension, send the same request with `Accept: application/json`. The gateway matches this header and returns `401` instead of redirecting.

   {{< tabs >}}
   {{% tab name="Cloud Provider LoadBalancer" %}}
   ```sh
   curl -vik "https://${INGRESS_GW_ADDRESS}:8443/headers" \
     -H "host: www.example.com" \
     -H "Accept: application/json"
   ```

   {{% /tab %}}
   {{% tab name="Port-forward for local testing" %}}
   ```sh
   curl -vik "https://localhost:8443/headers" \
     -H "host: www.example.com" \
     -H "Accept: application/json"
   ```

   {{% /tab %}}
   {{< /tabs >}}

   Example output:

   ```text
   < HTTP/2 401
   ```

## Cleanup {#cleanup}

{{< reuse "kgw-docs/snippets/cleanup.md" >}}

```sh
kubectl delete {{< reuse "kgw-docs/snippets/trafficpolicy.md" >}} okta-oauth2-policy -n httpbin
kubectl delete GatewayExtension okta-oauth2 -n {{< reuse "kgw-docs/snippets/namespace.md" >}}
kubectl delete secret okta-client-secret -n {{< reuse "kgw-docs/snippets/namespace.md" >}}
```

To remove Okta and the shared resources, see the Cleanup section of the [Okta setup]({{< link-hextra path="/security/oauth/okta/setup/#cleanup" >}}) page.

## More authorization code examples {#more-examples}

The authorization code flow works without the following settings. Add the ones your app needs, then re-apply the `GatewayExtension`.

### Configure cookie settings {#cookie-config}

Kgateway stores the access and ID tokens in session cookies. The default SameSite policy is `Lax`. Set custom cookie names if downstream services need to read them or your app spans subdomains. Configure the names under `cookies` on the GatewayExtension.

```yaml
spec:
  oauth2:
    # ... rest of the provider config ...
    cookies:
      domain: example.com
      sameSite: Strict
      names:
        accessToken: kgw-access
        idToken: kgw-id
```

| **Field** | **Description** |
| --- | --- |
| `domain` | Sets the cookie domain, which makes the session cookies valid for that domain and all of its subdomains. Set it if your app spans subdomains. If you omit it, the cookies apply only to the host that set them. |
| `sameSite` | `Strict` prevents the browser from sending cookies on cross-site requests, including top-level navigations. Use the default, `Lax`, if users arrive through links from other origins, such as email links. `None` requires HTTPS. Use it only when you need cross-site cookie sharing. |
| `names` | Overrides the generated cookie names, which is useful if a downstream service reads them. |

Add this block to the `GatewayExtension` manifest from the previous step and re-apply it. Because the manifest replaces the resource, keep the other fields that you already set, including `redirectURI`.

### Forward the access token to your app {#forward-access-token}

By default, the gateway keeps tokens in cookies and does not pass them upstream. Set `forwardAccessToken` if your app needs the access token, such as when it calls another API on the user's behalf. The gateway forwards the token in the `Authorization` header and a cookie named `BearerToken`.

```yaml
spec:
  oauth2:
    # ... rest of the provider config ...
    forwardAccessToken: true
```

### Copy token claims into request headers {#claims-to-headers}

Kgateway can verify the token signature and copy individual claims into headers for your app. This saves the app from parsing the token. Set `jwksURI` so the gateway can fetch the signing keys. Then map each claim to a header.

```yaml
spec:
  oauth2:
    # ... rest of the provider config ...
    jwt:
      jwksURI: https://YOUR_OKTA_DOMAIN/oauth2/default/v1/keys
      idToken:
        claimsToHeaders:
          - name: sub
            header: x-user-id
          - name: email
            header: x-user-email
```

Use `accessToken` in place of `idToken` to map claims from the access token instead. Both take the same `claimsToHeaders` list, where `name` is the JWT claim and `header` is the header to copy it to.

### Stop redirecting API clients {#deny-redirect}

This step is optional. By default, an unauthenticated request gets a `302` redirect to the Okta login page. Browsers can follow this redirect. API clients might follow it too, then receive the Okta login page instead of an API response. This can affect curl, mobile apps, and AJAX calls.

The `denyRedirect` field on `OAuth2Provider` lets you match specific requests and return `401` instead of redirecting them. It takes a list of `HTTPHeaderMatch` entries. A request matches only if it satisfies every entry.

Pattern for matching JSON API clients:

```yaml
spec:
  oauth2:
    # ... rest of the provider config ...
    denyRedirect:
      headers:
        - name: Accept
          type: Exact
          value: application/json
```

If requests might send `Accept: application/json; charset=utf-8` or similar values, use `RegularExpression`:

```yaml
denyRedirect:
  headers:
    - name: Accept
      type: RegularExpression
      value: "application/json.*"
```

For AJAX requests from browser JavaScript:

```yaml
denyRedirect:
  headers:
    - name: X-Requested-With
      type: Exact
      value: XMLHttpRequest
```

The full GatewayExtension with `denyRedirect` included:

```yaml
kubectl apply -f- <<EOF
apiVersion: gateway.kgateway.dev/v1alpha1
kind: GatewayExtension
metadata:
  name: okta-oauth2
  namespace: {{< reuse "kgw-docs/snippets/namespace.md" >}}
spec:
  oauth2:
    backendRef:
      group: gateway.kgateway.dev
      kind: Backend
      name: okta
      namespace: {{< reuse "kgw-docs/snippets/namespace.md" >}}
    issuerURI: https://YOUR_OKTA_DOMAIN/oauth2/default
    authorizationEndpoint: https://YOUR_OKTA_DOMAIN/oauth2/default/v1/authorize
    tokenEndpoint: https://YOUR_OKTA_DOMAIN/oauth2/default/v1/token
    endSessionEndpoint: https://YOUR_OKTA_DOMAIN/oauth2/default/v1/logout
    redirectURI: https://www.example.com/oauth2/redirect
    scopes:
      - openid
      - email
      - profile
    credentials:
      clientID: YOUR_CLIENT_ID
      clientSecretRef:
        name: okta-client-secret
    denyRedirect:
      headers:
        - name: Accept
          type: Exact
          value: application/json
EOF
```

> [!IMPORTANT]
> This manifest replaces the `GatewayExtension` that you created earlier. Include every field that you want to keep. If you omit `redirectURI`, kgateway uses the derived default instead. That default might not match the URI registered in Okta, causing login to fail with `The 'redirect_uri' parameter must be a Login redirect URI in the client app settings`.
