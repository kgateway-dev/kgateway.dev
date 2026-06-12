
Use this guide to protect an HTTPRoute with Keycloak as an OIDC provider. kgateway handles the OAuth2 authorization code flow: unauthenticated browser requests get redirected to Keycloak, the code is exchanged for tokens, and those tokens are stored in session cookies. Your upstream service doesn't need to know any of this happened.

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

   The redirect URI path is `/oauth2/redirect`, which is the default callback path that kgateway registers. You can override it with `redirectURI` in the `GatewayExtension` if needed.

## Store the client secret {#store-credentials}

Create a Kubernetes Secret with the Keycloak client secret. kgateway reads the value from the `client-secret` key specifically, so the key name matters.

```shell
kubectl create secret generic keycloak-client-secret \
  --from-literal=client-secret=YOUR_CLIENT_SECRET \
  -n {{< reuse "docs/snippets/namespace.md" >}}
```

Grab `YOUR_CLIENT_SECRET` from the **Credentials** tab of your Keycloak client.

## Create the GatewayExtension {#create-extension}

The `GatewayExtension` holds everything the gateway needs to talk to Keycloak. The `GatewayExtension` is independent of routing, so you can reuse the same extension across multiple `TrafficPolicy` resources.

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

- `issuerURI` triggers OIDC discovery. kgateway fetches `/.well-known/openid-configuration` from this URL and fills in the authorization, token, and end-session endpoints. If you also set those explicitly (as in the example), the explicit values win. Setting both is fine if you want the config to be readable without relying on discovery.
- `scopes` defaults to `user` if not set. For OIDC you need `openid` in the list. Add `email` and `profile` if your app needs those claims.
- `endSessionEndpoint` enables single logout across both kgateway and Keycloak. When a user hits `/logout`, kgateway clears their session cookies and redirects their browser to this URL, which tells Keycloak to end the session on its side too (this is called RP-initiated logout in the OIDC spec). Only set this if your Keycloak realm has that feature enabled and `openid` is in your scopes.
- `clientSecretRef.name` must match the Secret name from the previous step. kgateway reads the `client-secret` key inside that Secret.

## Attach the policy {#attach-policy}

Create a `TrafficPolicy` that references the extension by name. This policy tells the gateway to enforce the login flow on a specific route.

> **Note:** The OAuth2 filter does not protect against CSRF attacks on routes with cached authentication cookies. Pair the OAuth2 filter with a `CSRFPolicy` on the same route, especially for browser-facing apps.

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

`targetRefs` can point to a specific `HTTPRoute` or all routes in a `Gateway`. This example locks down a single route named `httpbin`.

## Configure cookie settings {#cookie-config}

kgateway stores the access and ID tokens in session cookies. The default `SameSite` policy is `Lax`. If you need custom cookie names (for example, to read them in downstream services or share across subdomains), set them explicitly under `cookies` on the `GatewayExtension`.

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

`Strict` means the browser won't send cookies on any cross-site request, including top-level navigations. Use `Lax`, which is the default, if users arrive at your app through links from other origins, like an email link. `None` requires HTTPS and should only be used when you explicitly need cross-site cookie sharing.

Add this block to the `GatewayExtension` manifest from the previous step and re-apply.

## Stop redirecting API clients {#deny-redirect}

By default, any unauthenticated request gets a `302` redirect to the Keycloak login page. That response is what you want for a browser, but not for API clients. `curl`, mobile apps, and AJAX calls that hit an unauthenticated route will silently follow the redirect, land on the Keycloak login HTML, and fail.

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

The full `GatewayExtension` with `denyRedirect` included:

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

1. Send a request without a session cookie. The gateway should redirect to Keycloak.

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

   Example output:
   ```
   < HTTP/1.1 302 Found
   < location: https://keycloak.example.com/realms/myrealm/protocol/openid-connect/auth?client_id=kgateway-client&...
   ```

2. Send the same request with `Accept: application/json`. Because `denyRedirect` matches on this header, the gateway returns `401` directly instead of redirecting.

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

   Example output:
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
