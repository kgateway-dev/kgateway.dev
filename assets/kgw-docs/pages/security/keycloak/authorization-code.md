Protect a route with the OAuth2 authorization code flow. Unauthenticated browser requests are redirected to Keycloak to log in, the gateway exchanges the returned authorization code for tokens, and it stores those tokens in session cookies. Your upstream service does not need to know that any of this happened.

## Before you begin

1. Complete the [Keycloak setup]({{< link-hextra path="/security/oauth/keycloak/setup/" >}}) page. This flow needs the realm, the confidential client, the test user, the `Backend`, and the `BackendConfigPolicy` that it creates.

2. Make sure your gateway has an **HTTPS listener**. Kgateway sets the OAuth2 nonce and code verifier cookies with the `Secure` attribute, so browsers do not return them over plain HTTP and the callback fails CSRF validation. To add one, see [HTTPS listener]({{< link-hextra path="/setup/listeners/https/" >}}).

## Configure the authorization code flow

Create the Kubernetes Secret that holds the Keycloak client secret, a `GatewayExtension` that configures the provider, and a `TrafficPolicy` that enforces the flow on a route.

### Store the client secret {#store-credentials}

Create a Kubernetes Secret with the Keycloak client secret. Kgateway reads the value from the `client-secret` key specifically, so the key name matters.

```sh
kubectl create secret generic keycloak-client-secret \
  --from-literal=client-secret=YOUR_CLIENT_SECRET \
  -n {{< reuse "kgw-docs/snippets/namespace.md" >}}
```

Replace `YOUR_CLIENT_SECRET` with the value that you copied from the **Credentials** tab of your Keycloak client during [Keycloak setup]({{< link-hextra path="/security/oauth/keycloak/setup/" >}}).

### Create the OAuth2 GatewayExtension {#create-oauth2-extension}

The `GatewayExtension` holds everything the gateway needs to talk to Keycloak. The GatewayExtension is independent of routing, so you can reuse the same extension across multiple `TrafficPolicy` resources.

```yaml
kubectl apply -f- <<EOF
apiVersion: {{< reuse "kgw-docs/snippets/trafficpolicy-apiversion.md" >}}
kind: GatewayExtension
metadata:
  name: keycloak-oauth2
  namespace: {{< reuse "kgw-docs/snippets/namespace.md" >}}
spec:
  oauth2:
    backendRef:
      group: gateway.kgateway.dev
      kind: Backend
      name: keycloak
      namespace: {{< reuse "kgw-docs/snippets/namespace.md" >}}
    issuerURI: https://keycloak.example.com/realms/myrealm
    authorizationEndpoint: https://keycloak.example.com/realms/myrealm/protocol/openid-connect/auth
    tokenEndpoint: https://keycloak.example.com/realms/myrealm/protocol/openid-connect/token
    endSessionEndpoint: https://keycloak.example.com/realms/myrealm/protocol/openid-connect/logout
    redirectURI: https://www.example.com/oauth2/redirect
    scopes:
      - openid
      - email
      - profile
    credentials:
      clientID: kgateway-client
      clientSecretRef:
        name: keycloak-client-secret
EOF
```

Replace the following values:

- `keycloak.example.com` with the Keycloak hostname that the **browser** uses. The browser is redirected to `authorizationEndpoint`, so this hostname must be resolvable outside the cluster. It cannot be the in-cluster Service address that you used for the `Backend`.

- `www.example.com` in `redirectURI` with the hostname that the browser uses to reach your route. This value must exactly match the redirect URI that you registered on the Keycloak client.

- `myrealm` with the realm name you created.

- `kgateway-client` with your Client ID, if you used a different name.

> [!NOTE]
> Keycloak derives the `iss` claim from the URL that the request arrives on, so the same realm reports a different issuer depending on how it is reached. Use one browser-facing Keycloak URL consistently across `issuerURI` and the endpoint fields. For local testing against a cluster-only Keycloak, port-forward Keycloak and use that address, such as `https://localhost:9443/realms/myrealm`. The gateway still reaches Keycloak through `backendRef`, so the two do not have to be the same address.

**Field notes:**

| Field | Description |
|-------|-------------|
| `backendRef` | Points to the `Backend` from [Keycloak setup]({{< link-hextra path="/security/oauth/keycloak/setup/#create-backend" >}}). Kgateway uses it to reach Keycloak for token exchange and OIDC discovery. |
| `issuerURI` | Triggers OIDC discovery. Kgateway fetches `/.well-known/openid-configuration` from this URL and fills in the authorization, token, and end-session endpoints. If you also set those explicitly (as in the example), the explicit values win. Setting both is fine if you want the config to be readable without relying on discovery. |
| `redirectURI` | The callback URL that kgateway sends to Keycloak as the `redirect_uri` parameter, and the path that the gateway intercepts to complete the code exchange. If you omit this field, it defaults to `<request-scheme>://<host>/oauth2/redirect` derived from the original request, which is easy to mismatch with the value registered in Keycloak. Set it explicitly. |
| `scopes` | Defaults to `user` if not set. For OIDC you need `openid` in the list. Add `email` and `profile` if your app needs those claims. |
| `endSessionEndpoint` | Handles single logout. When a user hits `/logout`, kgateway clears their session cookies and sends their browser to this URL so Keycloak ends the session too. This is RP-initiated logout in the OIDC spec. Only set it if your realm has that feature enabled and `openid` is in your scopes. |
| `clientSecretRef.name` | Must match the Secret name from the previous step. Kgateway reads the `client-secret` key inside that Secret. |

### Attach the OAuth2 policy {#attach-oauth2-policy}

Create a `TrafficPolicy` that references the extension by name. This policy tells the gateway to enforce the login flow on a specific route.

> [!WARNING]
> The OAuth2 filter does not protect against CSRF attacks on routes with cached authentication cookies. Pair it with a `CSRFPolicy` on the same route, especially for browser-facing apps.

```yaml
kubectl apply -f- <<EOF
apiVersion: {{< reuse "kgw-docs/snippets/trafficpolicy-apiversion.md" >}}
kind: {{< reuse "kgw-docs/snippets/trafficpolicy.md" >}}
metadata:
  name: keycloak-oauth2
  namespace: httpbin
spec:
  targetRefs:
    - group: gateway.networking.k8s.io
      kind: HTTPRoute
      name: httpbin
  oauth2:
    extensionRef:
      name: keycloak-oauth2
      namespace: {{< reuse "kgw-docs/snippets/namespace.md" >}}
EOF
```

> [!IMPORTANT]
> `targetRefs` has no `namespace` field, so a `TrafficPolicy` can target only resources in its own namespace. Create the policy in the same namespace as the resource that you want to protect. The HTTPRoute from the [Sample app guide]({{< link-hextra path="/install/sample-app/" >}}) is in the `httpbin` namespace, so this policy is created there too. `extensionRef` does take a `namespace`, so the `GatewayExtension` can stay in `{{< reuse "kgw-docs/snippets/namespace.md" >}}`.
>
> If the namespaces do not match, the policy is still accepted but never attaches, and requests reach your app unauthenticated. Verify that the policy attached before you rely on it.

Verify that the policy attached to the route.

```sh
kubectl get {{< reuse "kgw-docs/snippets/trafficpolicy.md" >}} keycloak-oauth2 -n httpbin -o yaml
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

`targetRefs` can also point to a Gateway, which applies the policy to every route that the Gateway serves. In that case, create the policy in the Gateway's namespace.

If your HTTPRoute restricts traffic with path matches, it must also match the OAuth2 callback path that you set in `redirectURI`. Otherwise, the redirect back from Keycloak returns a 404 error. The HTTPRoute from the Sample app guide has no path matches, so it already serves every path and needs no change.

For example, if your route matches only `/status`, add the callback path as a second match:

```yaml
rules:
  - matches:
      - path:
          type: PathPrefix
          value: /status
      - path:
          type: PathPrefix
          value: /oauth2/redirect
```


## Optional configurations

The authorization code flow works without the following settings. Add either one if your app needs it, then re-apply the `GatewayExtension`.

### Configure cookie settings {#cookie-config}

Kgateway stores the access and ID tokens in session cookies. The default SameSite policy is `Lax`. If you need custom cookie names (for example, to read them in downstream services or share across subdomains), set them explicitly under `cookies` on the GatewayExtension.

```yaml
spec:
  oauth2:
    # ... rest of the provider config ...
    cookies:
      sameSite: Strict
      names:
        accessToken: kgw-access
        idToken: kgw-id
```

`Strict` means the browser does not send cookies on any cross-site request, including top-level navigations. Use `Lax`, which is the default, if users arrive at your app through links from other origins, like an email link. `None` requires HTTPS and should only be used when you explicitly need cross-site cookie sharing.

Add this block to the `GatewayExtension` manifest from the previous step and re-apply it. Because the manifest replaces the resource, keep the other fields that you already set, including `redirectURI`.

### Stop redirecting API clients {#deny-redirect}

This step is optional. By default, any unauthenticated request gets a `302` redirect to the Keycloak login page. That response works for a browser, but not for API clients. curl, mobile apps, and AJAX calls that hit an unauthenticated route silently follow the redirect, land on the Keycloak login HTML, and fail.

The `denyRedirect` field on `OAuth2Provider` lets you match specific requests and return `401` instead of redirecting them. It takes a list of `HTTPHeaderMatch` entries, and a request matches if it satisfies all of them.

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
  name: keycloak-oauth2
  namespace: {{< reuse "kgw-docs/snippets/namespace.md" >}}
spec:
  oauth2:
    backendRef:
      group: gateway.kgateway.dev
      kind: Backend
      name: keycloak
      namespace: {{< reuse "kgw-docs/snippets/namespace.md" >}}
    issuerURI: https://keycloak.example.com/realms/myrealm
    authorizationEndpoint: https://keycloak.example.com/realms/myrealm/protocol/openid-connect/auth
    tokenEndpoint: https://keycloak.example.com/realms/myrealm/protocol/openid-connect/token
    endSessionEndpoint: https://keycloak.example.com/realms/myrealm/protocol/openid-connect/logout
    redirectURI: https://www.example.com/oauth2/redirect
    scopes:
      - openid
      - email
      - profile
    credentials:
      clientID: kgateway-client
      clientSecretRef:
        name: keycloak-client-secret
    denyRedirect:
      headers:
        - name: Accept
          type: Exact
          value: application/json
EOF
```

> [!IMPORTANT]
> This manifest replaces the `GatewayExtension` that you created earlier, so it must repeat every field that you want to keep. Omitting `redirectURI` here reverts it to the derived default, which no longer matches the redirect URI registered in Keycloak, and the login fails with `Invalid parameter: redirect_uri`.

## Verify {#verify}

Use the verification steps below to confirm that the Authorization Code flow works. Send these requests to the HTTPS listener, because the session cookies that this flow relies on are set with the `Secure` attribute.

1. Send a request without a session cookie. The gateway redirects to Keycloak.

   {{< tabs tabTotal="2" items="Cloud Provider LoadBalancer,Port-forward for local testing" >}}
{{% tab tabName="Cloud Provider LoadBalancer" %}}

```sh
curl -vik "https://${INGRESS_GW_ADDRESS}:8443/headers" -H "host: www.example.com"
```

{{% /tab %}}
{{% tab tabName="Port-forward for local testing" %}}

```sh
curl -vik "https://localhost:8443/headers" -H "host: www.example.com"
```

{{% /tab %}}
{{< /tabs >}}

   Example output. Note that the `redirect_uri` parameter matches the value that you registered on the Keycloak client.

   ```text
   < HTTP/2 302
   < location: https://keycloak.example.com/realms/myrealm/protocol/openid-connect/auth?client_id=kgateway-client&...&redirect_uri=https%3A%2F%2Fwww.example.com%2Foauth2%2Fredirect
   < set-cookie: OauthNonce-...;path=/;Max-Age=600;secure;HttpOnly
   ```

2. Open a browser and go to your protected route, such as `https://www.example.com/headers`. The gateway redirects you to the Keycloak login page.

3. Log in with the test user credentials, `testuser` and `password`.

4. Verify that Keycloak returns you to the route and that the response shows the httpbin output. The gateway exchanged the authorization code for tokens and stored them in session cookies.

   If you get a `401` response with `CSRF token validation failed` in the gateway logs, you sent the request over HTTP. Retry over HTTPS.

   If Keycloak shows `Invalid parameter: redirect_uri`, the `redirectURI` on the `GatewayExtension` does not match a redirect URI that is registered on the Keycloak client.

5. If you configured `denyRedirect`, send the same request with `Accept: application/json`. Because `denyRedirect` matches on this header, the gateway returns `401` directly instead of redirecting.

   {{< tabs tabTotal="2" items="Cloud Provider LoadBalancer,Port-forward for local testing" >}}
{{% tab tabName="Cloud Provider LoadBalancer" %}}

```sh
curl -vik "https://${INGRESS_GW_ADDRESS}:8443/headers" \
  -H "host: www.example.com" \
  -H "Accept: application/json"
```

{{% /tab %}}
{{% tab tabName="Port-forward for local testing" %}}

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
kubectl delete {{< reuse "kgw-docs/snippets/trafficpolicy.md" >}} keycloak-oauth2 -n httpbin
kubectl delete GatewayExtension keycloak-oauth2 -n {{< reuse "kgw-docs/snippets/namespace.md" >}}
kubectl delete secret keycloak-client-secret -n {{< reuse "kgw-docs/snippets/namespace.md" >}}
```

To remove Keycloak and the shared resources, see the Cleanup section of the [Keycloak setup]({{< link-hextra path="/security/oauth/keycloak/setup/#cleanup" >}}) page.
