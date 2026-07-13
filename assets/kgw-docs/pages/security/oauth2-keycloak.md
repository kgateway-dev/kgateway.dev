Use this guide to protect an HTTPRoute with Keycloak as an OIDC provider. kgateway handles the OAuth2 authorization code flow: unauthenticated browser requests get redirected to Keycloak, the code is exchanged for tokens, and those tokens are stored in session cookies. Your upstream service doesn't need to know any of this happened.

You need three resources: a `Backend` pointing at your Keycloak host, a `GatewayExtension` to configure the OAuth2 provider, and a `TrafficPolicy` to attach it to a route.

## Before you begin

{{< reuse "kgw-docs/snippets/prereq.md" >}}

## Install Keycloak

Deploy Keycloak in your cluster. The following example creates a Keycloak instance with admin credentials `admin/admin` for testing.

### Option A: Using YAML (recommended for testing)

This option deploys Keycloak using a single Kubernetes manifest that creates a Namespace, Service, and Deployment. It is ideal for testing and development because it's quick to apply and doesn't require Helm. However, it's not recommended for production because it uses the `start-dev` mode, which is not secure for production environments.

```yaml
kubectl apply -f- <<EOF
apiVersion: v1
kind: Namespace
metadata:
  name: keycloak
---
apiVersion: v1
kind: Service
metadata:
  name: keycloak
  namespace: keycloak
spec:
  selector:
    app: keycloak
  ports:
    - name: http
      port: 8080
      targetPort: 8080
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: keycloak
  namespace: keycloak
spec:
  replicas: 1
  selector:
    matchLabels:
      app: keycloak
  template:
    metadata:
      labels:
        app: keycloak
    spec:
      containers:
        - name: keycloak
          image: quay.io/keycloak/keycloak:22.0
          args: ["start-dev"]
          env:
            - name: KEYCLOAK_ADMIN
              value: "admin"
            - name: KEYCLOAK_ADMIN_PASSWORD
              value: "admin"
          ports:
            - name: http
              containerPort: 8080
EOF
```

### Option B: Using Helm (recommended for production)

This option deploys Keycloak using the Bitnami Helm chart, which provides better configuration management, easier upgrades, and production-ready defaults. It is recommended for production environments because it supports advanced settings like persistent storage, TLS, and custom resource limits.

```sh
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo update
helm install keycloak bitnami/keycloak \
  --namespace keycloak \
  --create-namespace \
  --set auth.adminUser=admin \
  --set auth.adminPassword=admin \
  --set service.type=ClusterIP \
  --set service.ports.http=8080
```

Wait for Keycloak to be ready:

```sh
kubectl rollout status deployment/keycloak -n keycloak
```

## Configure Keycloak

Access the Keycloak admin console:

```sh
kubectl port-forward svc/keycloak -n keycloak 8080:8080
```

1. Open `http://localhost:8080` in your browser

2. Log in with username `admin` and password `admin`

{{< reuse-image src="img/keycloak/keycloak-login.png" >}}
{{< reuse-image-dark srcDark="img/keycloak/keycloak-login.png" >}}

3. Create a new realm:
   - Click **Add realm** from the realm dropdown (top-left)
   - Enter a realm name (e.g., `myrealm`)
   - Click **Create**

{{< reuse-image src="img/keycloak/realm-creation.png" >}}
{{< reuse-image-dark srcDark="img/keycloak/realm-creation.png" >}}

4. Create a client:
   - Click **Clients** in the left sidebar
   - Click **Create client**
   - Set **Client ID** (e.g., `kgateway-client`)

{{< reuse-image src="img/keycloak/client-creation.png" >}}
{{< reuse-image-dark srcDark="img/keycloak/client-creation.png" >}}

   - Enable **Client authentication**
   - Click **Next**
   - In **Valid redirect URIs**, add `https://GATEWAY_HOST/oauth2/redirect`

{{< reuse-image src="img/keycloak/client-redirect-uri.png" >}}
{{< reuse-image-dark srcDark="img/keycloak/client-redirect-uri.png" >}}

   - Click **Save**

5. Note the client secret:
   - Go to the **Credentials** tab of your client
   - Copy the **Client secret** — you will need it for the `oauth2-client-secret` in the next section

{{< reuse-image src="img/keycloak/client-secret.png" >}}
{{< reuse-image-dark srcDark="img/keycloak/client-secret.png" >}}

6. Create a test user:
   - Click **Users** in the left sidebar
   - Click **Add user**
   - Set **Username** (e.g., `testuser`)
   - Click **Create**
   - Go to the **Credentials** tab
   - Set a password (e.g., `password`)
   - Turn **Temporary** off
   - Click **Set Password**

{{< reuse-image src="img/keycloak/user-password.png" >}}
{{< reuse-image-dark srcDark="img/keycloak/user-password.png" >}}

{{< reuse-image src="img/keycloak/user-created.png" >}}
{{< reuse-image-dark srcDark="img/keycloak/user-created.png" >}}

{{< callout type="info" >}}
For production, use a dedicated Keycloak instance with proper TLS and a real realm. The steps above use the default `master` realm for testing only.
{{< /callout >}}

## Store the client secret {#store-credentials}

Create a Kubernetes Secret with the Keycloak client secret. kgateway reads the value from the `client-secret` key specifically, so the key name matters.

```shell
kubectl create secret generic keycloak-client-secret \
  --from-literal=client-secret=YOUR_CLIENT_SECRET \
  -n {{< reuse "kgw-docs/snippets/namespace.md" >}}
```

Grab `YOUR_CLIENT_SECRET` from the **Credentials** tab of your Keycloak client.

## Create a Backend for Keycloak {#create-backend}

The following Backend resources defines how kgateway reaches the Cognito endpoints. The first Backend points to the token endpoint, and the second points to the JWKS endpoint. Both use the `Static` type with the host and port configured for Amazon Cognito.


```yaml
kubectl apply -f- <<EOF
apiVersion: gateway.kgateway.dev/v1alpha1
kind: Backend
metadata:
  name: keycloak
  namespace: {{< reuse "kgw-docs/snippets/namespace.md" >}}
spec:
  type: Static
  static:
    hosts:
    - host: keycloak.example.com
      port: 443
EOF
```

Replace `keycloak.example.com` with your Keycloak hostname. The port must be `443` because kgateway communicates with Keycloak over HTTPS.

## Create the GatewayExtension {#create-extension}

The `GatewayExtension` holds everything the gateway needs to talk to Keycloak. The `GatewayExtension` is independent of routing, so you can reuse the same extension across multiple `TrafficPolicy` resources.

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
      name: keycloak
      namespace: {{< reuse "kgw-docs/snippets/namespace.md" >}}
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

Field notes:

- `backendRef` points to the `Backend` created in the previous step. kgateway uses it to reach Keycloak for token exchange and OIDC discovery.
- `issuerURI` triggers OIDC discovery. kgateway fetches `/.well-known/openid-configuration` from this URL and fills in the authorization, token, and end-session endpoints. If you also set those explicitly (as in the example), the explicit values win. Setting both is fine if you want the config to be readable without relying on discovery.
- `scopes` defaults to `user` if not set. For OIDC you need `openid` in the list. Add `email` and `profile` if your app needs those claims.
- `endSessionEndpoint` handles single logout. When a user hits `/logout`, kgateway clears their session cookies and sends their browser to this URL so Keycloak ends the session too. This is RP-initiated logout in the OIDC spec. Only set it if your realm has that feature enabled and `openid` is in your scopes.
- `clientSecretRef.name` must match the Secret name from the previous step. kgateway reads the `client-secret` key inside that Secret.

## Attach the policy {#attach-policy}

Create a `TrafficPolicy` that references the extension by name. This policy tells the gateway to enforce the login flow on a specific route.

{{< callout type="warning" >}}
The OAuth2 filter does not protect against CSRF attacks on routes with cached authentication cookies. Pair the OAuth2 filter with a `CSRFPolicy` on the same route, especially for browser-facing apps.
{{< /callout >}}

```yaml
kubectl apply -f- <<EOF
apiVersion: {{< reuse "kgw-docs/snippets/trafficpolicy-apiversion.md" >}}
kind: {{< reuse "kgw-docs/snippets/trafficpolicy.md" >}}
metadata:
  name: keycloak-oauth2
  namespace: {{< reuse "kgw-docs/snippets/namespace.md" >}}
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
apiVersion: {{< reuse "kgw-docs/snippets/trafficpolicy-apiversion.md" >}}
kind: GatewayExtension
metadata:
  name: keycloak-oauth2
  namespace: {{< reuse "kgw-docs/snippets/namespace.md" >}}
spec:
  oauth2:
    backendRef:
      name: keycloak
      namespace: {{< reuse "kgw-docs/snippets/namespace.md" >}}
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

{{< reuse "kgw-docs/snippets/cleanup.md" >}}

```sh
kubectl delete {{< reuse "kgw-docs/snippets/trafficpolicy.md" >}} keycloak-oauth2 -n {{< reuse "kgw-docs/snippets/namespace.md" >}}
kubectl delete GatewayExtension keycloak-oauth2 -n {{< reuse "kgw-docs/snippets/namespace.md" >}}
kubectl delete Backend keycloak -n {{< reuse "kgw-docs/snippets/namespace.md" >}}
kubectl delete secret keycloak-client-secret -n {{< reuse "kgw-docs/snippets/namespace.md" >}}
```
