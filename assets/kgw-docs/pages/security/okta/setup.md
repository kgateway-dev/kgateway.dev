Set up an Okta account, register kgateway as an OAuth2 client, and give the gateway a network path to reach Okta. Every Okta guide in this section starts here.

When you finish, you choose an authentication flow:

* [Authorization code flow]({{< link-hextra path="/security/oauth/okta/authorization-code/" >}}) for browser traffic.
* [Access token validation]({{< link-hextra path="/security/oauth/okta/access-token/" >}}) for API clients that already hold a token.

## Before you begin

{{< reuse "kgw-docs/snippets/prereq.md" >}}

1. An Okta account with a configured Native Application. At minimum, set the following on the Okta application:

   | Setting | Value |
   |---|---|
   | **Application Type** | Native |
   | **Sign-in redirect URIs** | `https://www.example.com/oauth2/redirect` |
   | **Sign-out redirect URIs** | `https://www.example.com` |
   | **Grant types** | Authorization Code, Refresh Token, Resource Owner Password |

   The redirect URI path is `/oauth2/redirect`, which is the default callback path that kgateway registers. You can override it with `redirectURI` in the `GatewayExtension` if needed.

2. A test user created in your Okta directory.

The authorization code flow requires an **HTTPS listener** on your gateway. Kgateway sets the OAuth2 nonce and code verifier cookies with the `Secure` attribute, so browsers do not return them over plain HTTP and the callback fails CSRF validation. To add one, see [HTTPS listener]({{< link-hextra path="/setup/listeners/https/" >}}). The access token validation flow works over HTTP, because it does not use cookies.

## Configure Okta

Create an Okta application, configure the required settings, and add a test user.

### Access the Okta Admin Console

1. Go to your Okta Admin Console (such as, `https://your-okta-domain-admin.okta.com`).
2. Log in with your administrator credentials.

{{< reuse-image src="img/okta/okta-dashboard.png" >}}

### Create a Native Application

1. Navigate to **Applications** → **Applications**.
2. Click **Create App Integration**.
3. Select **OIDC - OpenID Connect** and **Native Application**.
4. Click **Next**.

> [!NOTE]
> Selecting **Native Application** makes the **Resource Owner Password** grant available, which the Access Token flow requires. The sign-in redirect URIs work the same as for a web application.

{{< reuse-image src="img/okta/okta-create-app.png" >}}

### Configure application settings

In the **General Settings** tab, configure the following:

- **Name**: `kgateway-app`
- **Grant types**: Check **Authorization Code**, **Refresh Token**, and **Resource Owner Password**.

{{< reuse-image src="img/okta/okta-grant-types.png" >}}

- **Sign-in redirect URIs**: Add `https://www.example.com/oauth2/redirect`.
- **Sign-out redirect URIs**: Add `https://www.example.com`.
- **Assignments**: Choose **"Skip group assignment for now"**.
- Click **Save**.

{{< reuse-image src="img/okta/okta-redirect-uri.png" >}}

### Copy the Client ID and Client Secret

1. After saving, you'll see the application details page.
2. Copy the **Client ID** and **Client Secret** from the **Client Credentials** section. You'll need these for the kgateway GatewayExtension.

{{< reuse-image src="img/okta/okta-client-credentials.png" >}}


> [!NOTE]
> The Client Secret is only shown once after creation. If you lose it, you can regenerate it, but this will invalidate any existing tokens.

### Create a test user {#create-test-user}

1. In the Okta Admin Console, navigate to **Directory** → **People**.
2. Click **Add person**.
3. Fill in the details:
   - **First name**: `Test`
   - **Last name**: `User`
   - **Username**: `testuser@example.com`
   - **Primary email**: `testuser@example.com`
   - **Activation**: Select **"I will set password"** and enter a password (such as, `password`).
   - **Uncheck** "User must change password at next login".
4. Click **Save**.

{{< reuse-image src="img/okta/okta-users-list.png" >}}

### Configure the Authentication Policy

To use the `password` grant, Okta's sign-on policy must allow password-only authentication. If your default policy enforces MFA, update the rule:

1. In the Okta Admin Console, go to **Security** → **Authentication**.
2. Click the **"App sign-in"** tab.
3. Click the **"Default"** policy.
4. Click **"Edit"** (pencil icon) on the **"Catch-all Rule"**.
5. Under **"User must authenticate with"**, select **"Any 1 factor type"**.
6. Under **"Authentication methods"**, select **"Allow specific authentication methods"** and ensure only **"Password"** is checked.
7. Click **"Update Rule"**.

{{< reuse-image src="img/okta/okta-auth-policy.png" >}}

> [!NOTE]
> This change is only required for testing the Access Token flow. In production, you may want a stricter policy.

## Connect kgateway to Okta

Both authentication flows need a network path from the gateway to Okta. Create these two resources first, whichever flow you use.

### Create a Backend for Okta {#create-backend}

Create a `Backend` resource that defines how kgateway reaches your Okta instance. This Backend uses the `Static` type with the host and port configured for Okta.

```yaml
kubectl apply -f- <<EOF
apiVersion: gateway.kgateway.dev/v1alpha1
kind: Backend
metadata:
  name: okta
  namespace: {{< reuse "kgw-docs/snippets/namespace.md" >}}
spec:
  type: Static
  static:
    hosts:
    - host: YOUR_OKTA_DOMAIN
      port: 443
EOF
```

Replace `YOUR_OKTA_DOMAIN` with your Okta domain (such as `integrator-6003780.okta.com`). The port must be `443` because kgateway communicates with Okta over HTTPS.

> [!NOTE]
> This address is separate from the public Okta URL that you configure on the `GatewayExtension` in the next steps. The `Backend` is the network path that the gateway uses for token exchange and OIDC discovery, and it does not have to be reachable from the browser.

## Configure TLS for the Okta Backend {#configure-tls}

Since Okta uses a public, trusted certificate, you can use the system's trusted CA certificates. Create a `BackendConfigPolicy` to configure TLS.

```yaml
kubectl apply -f- <<EOF
apiVersion: gateway.kgateway.dev/v1alpha1
kind: BackendConfigPolicy
metadata:
  name: okta-tls
  namespace: {{< reuse "kgw-docs/snippets/namespace.md" >}}
spec:
  targetRefs:
    - group: gateway.kgateway.dev
      kind: Backend
      name: okta
  tls:
    sni: YOUR_OKTA_DOMAIN
    wellKnownCACertificates: System
EOF
```

Replace `YOUR_OKTA_DOMAIN` with your Okta domain (such as `integrator-6003780.okta.com`). The `wellKnownCACertificates: System` setting tells Envoy to use the system's trusted CA certificates.

## Next steps

Okta is configured and the gateway can reach it. Now protect a route with the flow that matches how your clients arrive.

{{< cards >}}
{{< card link="../authorization-code" title="Authorization code flow" subtitle="Redirect browser users to Okta to log in, and store their tokens in session cookies." >}}
{{< card link="../access-token" title="Access token validation" subtitle="Validate a token that an API client already holds, and reject requests without one." >}}
{{< /cards >}}

## Cleanup {#cleanup}

{{< reuse "kgw-docs/snippets/cleanup.md" >}}

1. Remove the resources from this page only after you have cleaned up whichever flow you configured.

   ```sh
   kubectl delete BackendConfigPolicy okta-tls -n {{< reuse "kgw-docs/snippets/namespace.md" >}}
   kubectl delete Backend okta -n {{< reuse "kgw-docs/snippets/namespace.md" >}}
   ```

2. To remove Okta, delete the Okta application from your Okta Admin Console.