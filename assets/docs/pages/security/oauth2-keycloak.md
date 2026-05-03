
Use this guide to protect an HTTPRoute with Keycloak as an OIDC provider. kgateway handles the full OAuth2 authorization code flow at the proxy level — unauthenticated browser requests get redirected to Keycloak, the code is exchanged for tokens, and those tokens are written into session cookies. Your upstream service doesn't need to know any of this happened.

You need two resources: a `GatewayExtension` to configure the provider (endpoints, client credentials, cookie behavior), and a `TrafficPolicy` to wire that extension to a route.

## Before you begin

{{< reuse "docs/snippets/prereq.md" >}}

4. A running Keycloak instance with a configured realm and OIDC client. At minimum, set the following on the Keycloak client:

   | Setting | Value |
   |---|---|
   | **Client ID** | Any name — you'll reference it in the `GatewayExtension` |
   | **Client authentication** | On (this makes it a confidential client with a secret) |
   | **Valid redirect URIs** | `https://<your-gateway-host>/oauth2/redirect` |
   | **Web origins** | `https://<your-gateway-host>` |

   The redirect URI path is `/oauth2/redirect` — that is the default callback path kgateway registers. You can override it with `redirectURI` in the `GatewayExtension` if needed.

## Store the client secret {#store-credentials}

Create a Kubernetes Secret with the Keycloak client secret. kgateway reads the value from the `client-secret` key specifically, so the key name matters.

```shell
kubectl create secret generic keycloak-client-secret \
  --from-literal=client-secret=YOUR_CLIENT_SECRET \
  -n {{< reuse "docs/snippets/namespace.md" >}}
```

Grab `YOUR_CLIENT_SECRET` from the **Credentials** tab of your Keycloak client.

## Create the GatewayExtension {#create-extension}

The `GatewayExtension` holds everything the gateway needs to talk to Keycloak. It's independent of routing, so you can reuse the same extension across multiple `TrafficPolicy` resources.

```yaml
kubectl apply -f- <<EOF
apiVersion: {{< reuse "docs/snippets/trafficpolicy-apiversion.md" >}}
kind: GatewayExtension
metadata:
  name: keycloak-oauth2
  namespace: {{< reuse "docs/snippets/namespace.md" >}}
spec:
  oauth2:
    issuerURI: https://keycloak.example.com/realms/myrealm
    authorizationEndpoint: https://keycloak.example.com/realms/myrealm/protocol/openid-connect/auth
    tokenEndpoint: https://keycloak.example.com/realms/myrealm/protocol/openid-connect/token
    endSessionEndpoint: https://keycloak.example.com/realms/myrealm/protocol/openid-connect/logout
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

Replace `keycloak.example.com` and `myrealm` with your Keycloak host and realm.

A few things worth knowing about these fields:

- `issuerURI` triggers OIDC discovery. kgateway fetches `/.well-known/openid-configuration` from this URL and populates the authorization, token, and end-session endpoints automatically. If you also set those endpoints explicitly (as in the example above), your explicit values take precedence over whatever was discovered. Setting both is fine — it makes the config self-documenting and resilient to discovery failures.
- `openid` must be in `scopes` for OIDC flows. Add `email` and `profile` if your app needs those claims.
- `endSessionEndpoint` enables RP-initiated logout. When a user hits `/logout` (the default logout path), kgateway clears their session cookies and redirects them here to end the Keycloak session too. Only set this if your Keycloak realm has RP-initiated logout configured and you've included `openid` in scopes.
- `clientSecretRef.name` must match the Secret name from the previous step. kgateway reads the `client-secret` key inside that Secret.

## Attach the policy {#attach-policy}

Create a `TrafficPolicy` that references the extension by name. This is what tells the gateway to actually enforce the login flow on a specific route.

> **Note:** The OAuth2 filter does not protect against CSRF attacks on routes with cached authentication cookies. It's worth pairing this with a `CSRFPolicy` on the same route, especially for browser-facing apps.

```yaml
kubectl apply -f- <<EOF
apiVersion: {{< reuse "docs/snippets/trafficpolicy-apiversion.md" >}}
kind: {{< reuse "docs/snippets/trafficpolicy.md" >}}
metadata:
  name: keycloak-oauth2
  namespace: {{< reuse "docs/snippets/namespace.md" >}}
spec:
  targetRefs:
    - group: gateway.networking.k8s.io
      kind: HTTPRoute
      name: httpbin
  oauth2:
    extensionRef:
      name: keycloak-oauth2
      namespace: {{< reuse "docs/snippets/namespace.md" >}}
EOF
```

`targetRefs` can point to an `HTTPRoute` (specific route) or a `Gateway` (all routes on that gateway). This example locks down a single route named `httpbin`.

## Configure cookie settings {#cookie-config}

kgateway stores the access and ID tokens in session cookies. The default cookie names are implementation-defined — if you need predictable names (for example, to read them in downstream JavaScript or share them across subdomains), set them explicitly. The default `SameSite` policy is `Lax`. Both settings live under `cookies` on the `GatewayExtension`.

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

`Strict` means the browser won't send cookies on any cross-site request, including top-level navigations. Use `Lax` (the default) if users arrive at your app through links from other origins, like an email link. `None` requires HTTPS and should only be used when you explicitly need cross-site cookie sharing.

Add this block to the `GatewayExtension` manifest from the previous step and re-apply.

## Stop redirecting API clients {#deny-redirect}

By default, any unauthenticated request gets a `302` redirect to the Keycloak login page. That's what you want for a browser, but it's wrong for API clients. `curl`, mobile apps, and AJAX calls that hit an unauthenticated route will silently follow the redirect, land on the Keycloak login HTML, and fail in confusing ways.

The `denyRedirect` field on `OAuth2Provider` lets you match specific requests and return `401` instead of redirecting them. It takes a list of `HTTPHeaderMatch` entries — a request matches if it satisfies all of them.

Here's the pattern for matching JSON API clients:

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

For requests that might send `Accept: application/json; charset=utf-8` or similar variations, you can use `RegularExpression`:

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

Here's the full `GatewayExtension` with `denyRedirect` included:

```yaml
kubectl apply -f- <<EOF
apiVersion: {{< reuse "docs/snippets/trafficpolicy-apiversion.md" >}}
kind: GatewayExtension
metadata:
  name: keycloak-oauth2
  namespace: {{< reuse "docs/snippets/namespace.md" >}}
spec:
  oauth2:
    issuerURI: https://keycloak.example.com/realms/myrealm
    authorizationEndpoint: https://keycloak.example.com/realms/myrealm/protocol/openid-connect/auth
    tokenEndpoint: https://keycloak.example.com/realms/myrealm/protocol/openid-connect/token
    endSessionEndpoint: https://keycloak.example.com/realms/myrealm/protocol/openid-connect/logout
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

## Verify {#verify}

Send a plain request without a session cookie. The gateway should redirect you to Keycloak.

{{< tabs tabTotal="2" items="Cloud Provider LoadBalancer,Port-forward for local testing" >}}
{{% tab tabName="Cloud Provider LoadBalancer" %}}
```sh
curl -vi "http://${INGRESS_GW_ADDRESS}:8080/headers" -H "host: www.example.com"
```
{{% /tab %}}
{{% tab tabName="Port-forward for local testing" %}}
```sh
curl -vi "http://localhost:8080/headers" -H "host: www.example.com"
```
{{% /tab %}}
{{< /tabs >}}

You should see:

```
< HTTP/1.1 302 Found
< location: https://keycloak.example.com/realms/myrealm/protocol/openid-connect/auth?client_id=kgateway-client&...
```

Now send the same request but with `Accept: application/json`. Because `denyRedirect` matches this header, the gateway returns `401` directly instead of redirecting.

{{< tabs tabTotal="2" items="Cloud Provider LoadBalancer,Port-forward for local testing" >}}
{{% tab tabName="Cloud Provider LoadBalancer" %}}
```sh
curl -vi "http://${INGRESS_GW_ADDRESS}:8080/headers" \
  -H "host: www.example.com" \
  -H "Accept: application/json"
```
{{% /tab %}}
{{% tab tabName="Port-forward for local testing" %}}
```sh
curl -vi "http://localhost:8080/headers" \
  -H "host: www.example.com" \
  -H "Accept: application/json"
```
{{% /tab %}}
{{< /tabs >}}

Expected:

```
< HTTP/1.1 401 Unauthorized
```

## Cleanup {#cleanup}

{{< reuse "docs/snippets/cleanup.md" >}}

```sh
kubectl delete {{< reuse "docs/snippets/trafficpolicy.md" >}} keycloak-oauth2 -n {{< reuse "docs/snippets/namespace.md" >}}
kubectl delete GatewayExtension keycloak-oauth2 -n {{< reuse "docs/snippets/namespace.md" >}}
kubectl delete secret keycloak-client-secret -n {{< reuse "docs/snippets/namespace.md" >}}
```
