
Set up an Auth0 account, register kgateway as an OAuth2 client, and give the gateway a network path to reach Auth0. Every Auth0 guide in this section starts here.

When you finish, you choose an authentication flow:

* [Authorization code flow]({{< link-hextra path="/security/oauth/auth0/authorization-code/" >}}) for browser traffic.
* [Access token validation]({{< link-hextra path="/security/oauth/auth0/access-token/" >}}) for API clients that already hold a token.

## Before you begin

{{< reuse "kgw-docs/snippets/prereq.md" >}}

1. An Auth0 account with a configured Regular Web Application. At minimum, set the following on the Auth0 application:

   | Setting | Value |
   |---|---|
   | **Application Type** | Regular Web Application |
   | **Allowed Callback URLs** | `http://localhost:8080/oauth2/redirect` |
   | **Allowed Logout URLs** | `http://localhost:8080` |
   | **Allowed Web Origins** | `http://localhost:8080` |
   | **JWT Signature Algorithm** | RS256 |
   | **OIDC Conformant** | Enabled |

   The redirect URI path is `/oauth2/redirect`, which is the default callback path that kgateway registers. You can override it with `redirectURI` in the `GatewayExtension` if needed.

2. A test user created in your Auth0 database connection.

The authorization code flow additionally requires an **HTTPS listener** on your gateway. Kgateway sets the OAuth2 nonce and code verifier cookies with the `Secure` attribute, so browsers do not return them over plain HTTP and the callback fails CSRF validation. To add an HTTPS listener, see [HTTPS listener]({{< link-hextra path="/setup/listeners/https/" >}}). The access token validation flow works over HTTP, because it does not use cookies.

## Configure Auth0

Create an Auth0 application, configure the required settings, and add a test user.

### Access the Auth0 Dashboard

1. Go to [Auth0 Dashboard](https://manage.auth0.com/).

{{< reuse-image src="img/auth0/auth0-dashboard.png" >}}

2. Navigate to **Applications** → **Applications**.
3. Click on your Regular Web Application.

{{< reuse-image src="img/auth0/create-application.png" >}}

### Configure application settings

In the **Settings** tab, configure the following:

- **Allowed Callback URLs**: Add `http://localhost:8080/oauth2/redirect`
- **Allowed Logout URLs**: Add `http://localhost:8080`
- **Allowed Web Origins**: Add `http://localhost:8080`

{{< reuse-image src="img/auth0/redirect-uri.png" >}}

### Configure Advanced Settings

1. Scroll to **Advanced Settings** → **OAuth**:
   - **JsonWebToken Signature Algorithm**: Set to `RS256`
   - **OIDC Conformant**: Enable

2. In **Advanced Settings** → **Grant Types**:
   - Ensure **Authorization Code** is enabled

{{< callout type="note" >}}
If you plan to use the **Access Token Validation (JWT)** flow, you must enable the **Password** grant in **Advanced Settings → Grant Types**. This allows the `password` grant type for obtaining tokens programmatically.
{{< /callout >}}

{{< reuse-image src="img/auth0/advanced-settings-grant-types.png" >}}

3. Click **Save Changes**.

### Create a test user {#create-test-user}

1. In the Auth0 Dashboard, navigate to **User Management** → **Users**.
2. Click **Create User**.

{{< reuse-image src="img/auth0/users-list.png" >}}

3. Enter user details:
   - **Email**: `testuser@example.com`
   - **Password**: `your-password`
   - **Connection**: `Username-Password-Authentication`
4. Click **Create**.

5. Verify the user is created.

{{< reuse-image src="img/auth0/user-created.png" >}}

{{< callout type="note" >}}
The steps above create a test user for this guide. For production, use a dedicated Auth0 tenant and follow Auth0's [production best practices](https://auth0.com/docs/best-practices).
{{< /callout >}}


## Connect kgateway to Auth0

Both authentication flows need a network path from the gateway to Auth0. Create these two resources first, whichever flow you use.

### Create a Backend for Auth0 {#create-backend}

Create a `Backend` resource that defines how kgateway reaches your Auth0 instance. This Backend uses the `Static` type with the host and port configured for Auth0.

```yaml
kubectl apply -f- <<EOF
apiVersion: gateway.kgateway.dev/v1alpha1
kind: Backend
metadata:
  name: auth0
  namespace: {{< reuse "kgw-docs/snippets/namespace.md" >}}
spec:
  type: Static
  static:
    hosts:
    - host: YOUR_AUTH0_DOMAIN
      port: 443
EOF
```

Replace `YOUR_AUTH0_DOMAIN` with your Auth0 domain (such as, `dev-xxx.us.auth0.com`). The port must be `443` because kgateway communicates with Auth0 over HTTPS.

{{< callout type="note" >}}
This address is separate from the public Auth0 URL that you configure on the `GatewayExtension` in the next steps. The `Backend` is the network path that the gateway uses for token exchange and OIDC discovery, and it does not have to be reachable from the browser.
{{< /callout >}}


## Configure TLS for the Auth0 Backend {#configure-tls}

Since Auth0 uses a public, trusted certificate, you can use the system's trusted CA certificates. Create a `BackendConfigPolicy` to configure TLS.

```yaml
kubectl apply -f- <<EOF
apiVersion: gateway.kgateway.dev/v1alpha1
kind: BackendConfigPolicy
metadata:
  name: auth0-tls
  namespace: {{< reuse "kgw-docs/snippets/namespace.md" >}}
spec:
  targetRefs:
    - group: gateway.kgateway.dev
      kind: Backend
      name: auth0
  tls:
    sni: YOUR_AUTH0_DOMAIN
    wellKnownCACertificates: System
EOF
```

Replace `YOUR_AUTH0_DOMAIN` with your Auth0 domain (such as, `dev-xxx.us.auth0.com`). The `wellKnownCACertificates: System` setting tells Envoy to use the system's trusted CA certificates, which include the Certificate Authorities that signed
Auth0's certificate.

## Next steps

Auth0 is configured and the gateway can reach it. Now protect a route with the flow that matches how your clients arrive.

{{< cards >}}
{{< card link="../authorization-code" title="Authorization code flow" subtitle="Redirect browser users to Auth0 to log in, and store their tokens in session cookies." >}}
{{< card link="../access-token" title="Access token validation" subtitle="Validate a token that an API client already holds, and reject requests without one." >}}
{{< /cards >}}

## Cleanup {#cleanup}

{{< reuse "kgw-docs/snippets/cleanup.md" >}}

1. Remove the resources from this page only after you have cleaned up whichever flow you configured.

   ```sh
   kubectl delete BackendConfigPolicy auth0-tls -n {{< reuse "kgw-docs/snippets/namespace.md" >}}
   kubectl delete Backend auth0 -n {{< reuse "kgw-docs/snippets/namespace.md" >}}
   ```

2. To remove Auth0, delete the Auth0 application from your Auth0 Dashboard.
