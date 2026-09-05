Protect a route with the OAuth2 authorization code flow. Unauthenticated browser requests are redirected to Okta to log in, the gateway exchanges the returned authorization code for tokens, and it stores those tokens in session cookies. Your upstream service does not need to know that any of this happened.

## Before you begin

1. Complete the [Okta setup]({{< link-hextra path="/security/oauth/okta/setup/" >}}) page. This flow needs the Okta application, the test user, the `Backend`, and the `BackendConfigPolicy` that it creates.

2. Make sure your gateway has an **HTTPS listener**. Kgateway sets the OAuth2 nonce and code verifier cookies with the `Secure` attribute, so browsers do not return them over plain HTTP and the callback fails CSRF validation. To add one, see [HTTPS listener]({{< link-hextra path="/setup/listeners/https/" >}}). The access token validation flow works over HTTP, because it does not use cookies.

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
> Okta's `iss` claim is derived from your Okta domain. Use the same domain consistently across `issuerURI` and the endpoint fields. The `redirectURI` must match the exact value you register in Okta's **Sign-in redirect URIs**. The gateway still reaches Okta through `backendRef`, so the two do not have to be the same address.

```yaml
kubectl apply -f- <<EOF
apiVersion: {{< reuse "kgw-docs/snippets/trafficpolicy-apiversion.md" >}}
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
    authorizationEndpoint: https://YOUR_OKTA_DOMAIN/oauth2/v1/authorize
    tokenEndpoint: https://YOUR_OKTA_DOMAIN/oauth2/v1/token
    endSessionEndpoint: https://YOUR_OKTA_DOMAIN/oauth2/v1/logout
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
| `redirectURI` | The callback URL that kgateway sends to Okta as the `redirect_uri` parameter, and the path that the gateway intercepts to complete the code exchange. If you omit this field, it defaults to `<request-scheme>://<host>/oauth2/redirect` derived from the original request, which is easy to mismatch with the value registered in Okta. Set it explicitly. |
| `scopes` | Defaults to `user` if not set. For OIDC you need `openid` in the list. Add `email` and `profile` if your app needs those claims. |
| `endSessionEndpoint` | Handles single logout. When a user hits `/logout`, kgateway clears their session cookies and sends their browser to this URL so Okta ends the session too. This is RP-initiated logout in the OIDC spec. Only set it if `openid` is in your scopes. |
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
   > `targetRefs` has no `namespace` field, so the {{< reuse "kgw-docs/snippets/trafficpolicy.md" >}} can target only resources in its own namespace. Create the policy in the same namespace as the resource that you want to protect. The HTTPRoute from the [Sample app guide]({{< link-hextra path="/install/sample-app/" >}}) is in the `httpbin` namespace, so this policy is created there too. `extensionRef` does take a `namespace`, so the GatewayExtension can stay in `{{< reuse "kgw-docs/snippets/namespace.md" >}}`.
   >
   > If the namespaces do not match, the policy is still accepted but never attaches, and requests reach your app unauthenticated. Verify that the policy attached before you rely on it.
   >
   > `targetRefs` can also point to a Gateway, which applies the policy to every route that the Gateway serves. In that case, create the policy in the Gateway's namespace.

4. Verify that the policy attached to the route.

```sh
kubectl get {{< reuse "kgw-docs/snippets/trafficpolicy.md" >}} okta-oauth2-policy -n httpbin -o yaml
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

Use the verification steps below to confirm that the Authorization Code flow works. Send these requests to the HTTPS listener, because the session cookies that this flow relies on are set with the `Secure` attribute.

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

Example output. Note that the `redirect_uri` parameter matches the value that you registered on the Okta application.

```text
< HTTP/2 302
< location: https://YOUR_OKTA_DOMAIN/oauth2/v1/authorize?client_id=YOUR_CLIENT_ID&...&redirect_uri=https%3A%2F%2Fwww.example.com%2Foauth2%2Fredirect
< set-cookie: OauthNonce-...;path=/;Max-Age=600;secure;HttpOnly
```

2. Open a browser and go to your protected route, such as `https://www.example.com/headers`. The gateway redirects you to the Okta login page.

3. Log in with the test user credentials you created in the [Okta setup]({{< link-hextra path="/security/oauth/okta/setup/#create-test-user" >}}).

4. Verify that Okta returns you to the route and that the response shows the httpbin output. The gateway exchanged the authorization code for tokens and stored them in session cookies.

If you get a `401` response with `CSRF token validation failed` in the gateway logs, you sent the request over HTTP. Retry over HTTPS.

If Okta shows `Invalid parameter: redirect_uri`, the `redirectURI` on the `GatewayExtension` does not match a redirect URI that is registered on the Okta application.

5. Optional: If you added the [`denyRedirect` setting](#deny-redirect) to your GatewayExtension, send the same request with `Accept: application/json`. Because `denyRedirect` matches on this header, the gateway returns `401` directly instead of redirecting.

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

Kgateway stores the access and ID tokens in session cookies. The default SameSite policy is `Lax`. If you need custom cookie names (for example, to read them in downstream services or share across subdomains), set them explicitly under `cookies` on the GatewayExtension.

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
| `sameSite` | `Strict` means the browser does not send cookies on any cross-site request, including top-level navigations. Use `Lax`, the default, if users arrive at your app through links from other origins, such as an email link. `None` requires HTTPS and should only be used when you explicitly need cross-site cookie sharing. |
| `names` | Overrides the generated cookie names, which is useful if a downstream service reads them. |

Add this block to the `GatewayExtension` manifest from the previous step and re-apply it. Because the manifest replaces the resource, keep the other fields that you already set, including `redirectURI`.

### Forward the access token to your app {#forward-access-token}

By default the gateway keeps the tokens in cookies and does not pass them upstream. Set `forwardAccessToken` if your app needs the access token itself, for example to call another API on the user's behalf. The token is forwarded in the `Authorization` header and in a cookie named `BearerToken`.

```yaml
spec:
  oauth2:
    # ... rest of the provider config ...
    forwardAccessToken: true
```

### Copy token claims into request headers {#claims-to-headers}

Kgateway can verify the token signature and copy individual claims into headers that your app reads, which saves the app from parsing the token. Set `jwksURI` so the gateway can fetch the signing keys, then map each claim to a header.

```yaml
spec:
  oauth2:
    # ... rest of the provider config ...
    jwt:
      jwksURI: https://YOUR_OKTA_DOMAIN/oauth2/v1/keys
      idToken:
        claimsToHeaders:
          - name: sub
            header: x-user-id
          - name: email
            header: x-user-email
```

Use `accessToken` in place of `idToken` to map claims from the access token instead. Both take the same `claimsToHeaders` list, where `name` is the JWT claim and `header` is the header to copy it to.

### Stop redirecting API clients {#deny-redirect}

This step is optional. By default, any unauthenticated request gets a `302` redirect to the Okta login page. That response works for a browser, but not for API clients. curl, mobile apps, and AJAX calls that hit an unauthenticated route silently follow the redirect, land on the Okta login HTML, and fail.

The `denyRedirect` field on `OAuth2Provider` lets you match specific requests and return 401 instead of redirecting them. It takes a list of `HTTPHeaderMatch` entries, and a request matches if it satisfies all of them.

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

For requests that might send `Accept: application/json; charset=utf-8` or similar variations, use `RegularExpression`:

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
apiVersion: {{< reuse "kgw-docs/snippets/trafficpolicy-apiversion.md" >}}
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
    authorizationEndpoint: https://YOUR_OKTA_DOMAIN/oauth2/v1/authorize
    tokenEndpoint: https://YOUR_OKTA_DOMAIN/oauth2/v1/token
    endSessionEndpoint: https://YOUR_OKTA_DOMAIN/oauth2/v1/logout
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
> This manifest replaces the `GatewayExtension` that you created earlier, so it must repeat every field that you want to keep. Omitting `redirectURI` here reverts it to the derived default, which no longer matches the redirect URI registered in Okta, and the login fails with `Invalid parameter: redirect_uri`.