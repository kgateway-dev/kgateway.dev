Set up an Okta account, register kgateway as an OAuth2 client, and give the gateway a network path to reach Okta. Every Okta guide in this section starts here.

When you finish, you choose an authentication flow:

* [Authorization code flow]({{< link-hextra path="/security/oauth/okta/authorization-code/" >}}) for browser traffic.
* [Access token validation]({{< link-hextra path="/security/oauth/okta/access-token/" >}}) for API clients that already hold a token.

## Before you begin

{{< reuse "kgw-docs/snippets/prereq.md" >}}

1. An Okta account with a configured Web Application. At minimum, set the following on the Okta application:

   | Setting | Value |
   |---|---|
   | **Application Type** | Web |
   | **Sign-in redirect URIs** | `https://www.example.com/oauth2/redirect` |
   | **Sign-out redirect URIs** | `https://www.example.com` |
   | **Grant types** | Authorization Code, Client Credentials |

   The redirect URI path is `/oauth2/redirect`, which is the default callback path that kgateway registers. You can override it with `redirectURI` in the `GatewayExtension` if needed.

2. A test user created in your Okta directory.

3. An access policy and rule configured on the default authorization server. Without this policy, the browser login fails with the message that the user is not allowed to access the app. You create this policy later in [Configure the default authorization server](#configure-default-as).

> [!NOTE]
> Client Credentials requires API Access Management, which is not enabled on every Okta org. If you plan to use the access token validation flow with a Client Credentials token, confirm that your org has API Access Management enabled before you begin.

## Configure Okta

Create an Okta application, configure the required settings, and add a test user.

### Access the Okta Admin Console

1. Go to your Okta Admin Console (such as, `https://your-okta-domain-admin.okta.com`).
2. Log in with your administrator credentials.

{{< reuse-image src="img/okta/okta-dashboard.png" >}}

### Create a Web Application

1. Navigate to **Applications** → **Applications**.
2. Click **Create App Integration**.
3. Select **OIDC - OpenID Connect** and **Web Application**.
4. Click **Next**.

{{< reuse-image src="img/okta/okta-create-app.png" >}}

### Configure application settings

In the **General Settings** tab, configure the following:

- **Name**: `kgateway-app`
- **Grant types**: Check **Authorization Code** and **Client Credentials**.
- **Sign-in redirect URIs**: Add `https://www.example.com/oauth2/redirect`.
- **Sign-out redirect URIs**: Add `https://www.example.com`.
- **Assignments**: Choose **"Skip group assignment for now"**.
- Click **Save**.

{{< reuse-image src="img/okta/okta-redirect-uri.png" >}}

> [!NOTE]
> This guide registers `kgateway-app` as a Web application, not a Native application. Kgateway is a server-side confidential client that can hold the client secret and perform the code exchange, so the Web application flow applies. This also means you do not need to enable password-only authentication.

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

### Configure the default authorization server {#configure-default-as}

Okta provides two authorization servers that matter for this guide: the Org authorization server and the default custom authorization server. The Org authorization server issues opaque tokens, which the gateway's JWT policy cannot validate. This guide uses the default authorization server at `/oauth2/default`, which issues JWTs that the gateway can validate.

1. In the Okta Admin Console, navigate to **Security** → **API**.
2. Open the **Authorization Servers** tab.
3. Click **default**.
4. Go to the **Access Policies** tab.
5. Click **Add Policy** and configure the following:
   - **Name**: `kgateway-access-policy`
   - **Assign to**: **The following clients**, then select `kgateway-app`
6. Click **Create Policy**.

{{< reuse-image src="img/okta/okta-access-policy.png" >}}

7. On the new policy, click **Add rule** and configure the following:
   - **Rule Name**: `kgateway-default-rule`
   - **Grant type**: Check **Authorization Code**. Check **Client Credentials** too if you plan to use the access token validation flow.
   - **User is**: **Any user assigned the app**
   - **Scopes requested**: **Any scopes**
8. Click **Create Rule**.

{{< reuse-image src="img/okta/okta-access-rule.png" >}}

After you save the policy and rule, the default authorization server issues tokens for the `kgateway-app` client, and the issuer, audience, and JWKS endpoints all resolve under `/oauth2/default`.

## Connect kgateway to Okta

Both authentication flows need a network path from the gateway to Okta. Create these two resources first, whichever flow you use. All URLs in this section, and in the flow guides that follow, resolve under `/oauth2/default` on your Okta domain.

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

### Configure TLS for the Okta Backend {#configure-tls}

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
{{< card link="../access-token" title="Access token validation" subtitle="Validate a JWT that an API client already holds, and reject requests without one." >}}
{{< /cards >}}

## Cleanup {#cleanup}

{{< reuse "kgw-docs/snippets/cleanup.md" >}}

1. Remove the resources from this page only after you have cleaned up whichever flow you configured.

   ```sh
   kubectl delete BackendConfigPolicy okta-tls -n {{< reuse "kgw-docs/snippets/namespace.md" >}}
   kubectl delete Backend okta -n {{< reuse "kgw-docs/snippets/namespace.md" >}}
   ```

2. To remove Okta, delete the Okta application from your Okta Admin Console.