Set up a Microsoft Entra ID app registration, register kgateway as an OAuth2 client, and give the gateway a network path to reach Entra ID. Every Entra ID guide in this section starts here.

When you finish, you choose an authentication flow:

* [Authorization code flow]({{< link-hextra path="/security/oauth/entra-id/authorization-code/" >}}) for browser traffic.
* [Access token validation]({{< link-hextra path="/security/oauth/entra-id/access-token/" >}}) for API clients that already hold a token.

## Before you begin

{{< reuse "kgw-docs/snippets/prereq.md" >}}

1. A Microsoft Entra ID tenant with an App Registration. At minimum, set the following on the App Registration:

   | Setting | Value |
   |---|---|
   | **Supported account types** | Accounts in this organizational directory only |
   | **Platform** | Web |
   | **Redirect URI** | `https://www.example.com/oauth2/redirect` |
   | **Front-channel logout URL** | `https://www.example.com` |

   The redirect URI path is `/oauth2/redirect`, which is the default callback path that kgateway registers. You can override it with `redirectURI` in the `GatewayExtension` if needed.

2. A test user created in your Entra ID directory and assigned to the App Registration.

> [!IMPORTANT]
> **Entra ID token version finding:** When you configure custom API scopes (as required for access token validation), Entra ID issues **v1.0 tokens**, even if you configure the manifest for v2.0. This means the `iss` claim will be `https://sts.windows.net/{tenant-id}/` and the JWKS endpoint will be `https://login.microsoftonline.com/{tenant-id}/discovery/keys`. This is different from the standard v2.0 endpoints (`/v2.0` and `/discovery/v2.0/keys`). You must use the v1.0 endpoints in your `GatewayExtension`.

## Configure Microsoft Entra ID

Create an App Registration, configure the required settings, and add a test user.

### Create an App Registration

Kgateway is a server-side confidential client. It holds the client secret and performs the code exchange itself, so register it as a Web application rather than a Single-page application.

1. Log in to the [Microsoft Entra admin center](https://entra.microsoft.com) with your administrator credentials.
2. Go to **Applications** > **App registrations**, and click **New registration**.
3. Configure the application:
   * **Name**: `kgateway-app`
   * **Supported account types**: **Accounts in this organizational directory only**
   * **Redirect URI**: Select **Web** and enter `https://www.example.com/oauth2/redirect`
4. Click **Register**.

   {{< reuse-image src="img/entra-id/entra-create-app.png" >}}

### Configure Authentication and Logout

1. On the App Registration page, go to **Authentication**.
2. Under **Front-channel logout URL**, enter `https://www.example.com`.
3. Under **Implicit grant and hybrid flows**, leave both checkboxes unchecked (we use the Authorization Code flow).
4. Click **Save**.

### Expose an API Scope

To use the access token validation flow, you must define a custom scope.

1. Go to **Expose an API**.
2. Click **Set** next to Application ID URI. Accept the default `api://{client-id}` and click **Save**.
3. Click **Add a scope**:
   * **Scope name**: `access_as_user`
   * **Who can consent**: Admins and users
   * **Admin consent display name**: Access kgateway as the user
   * **Admin consent description**: Allows the app to access kgateway on behalf of the signed-in user
   * **State**: Enabled
4. Click **Add scope**.

   {{< reuse-image src="img/entra-id/entra-expose-scope.png" >}}

### Copy the Client ID and Client Secret

1. Go to **Overview** and copy the **Application (client) ID**.
2. Go to **Certificates & secrets** > **Client secrets**, and click **New client secret**.
3. Add a description (e.g., `kgateway-secret`) and select an expiry period. Click **Add**.
4. **Copy the secret value immediately.** It will not be shown again.

   {{< reuse-image src="img/entra-id/entra-client-credentials.png" >}}

   > [!NOTE]
   > The Client Secret is shown only once after creation. If you lose it, you can generate a new one, but generating a new one invalidates any existing tokens.

### Create a test user {#create-test-user}

1. Go to the Microsoft Entra admin center > **Identity** > **Users** > **All users**.
2. Click **New user** > **Create new user**.
3. Configure the user:
   * **User principal name**: `testuser@yourdomain.onmicrosoft.com`
   * **Display name**: `Test User`
   * **Password**: Enter a password or let it auto-generate
4. Click **Create**.

   {{< reuse-image src="img/entra-id/entra-create-user.png" >}}

5. Go back to your App Registration > **Enterprise applications** > **kgateway-app** > **Users and groups**.
6. Click **Add user/group**, select the test user, and assign them to the app.

   {{< reuse-image src="img/entra-id/entra-assign-user.png" >}}

   
## Connect kgateway to Microsoft Entra ID

Both authentication flows need a network path from the gateway to Entra ID. Create these two resources before configuring either flow.

### Create a Backend for Entra ID {#create-backend}

Create a `Backend` resource to define how kgateway reaches Entra ID.

```yaml
kubectl apply -f- <<EOF
apiVersion: gateway.kgateway.dev/v1alpha1
kind: Backend
metadata:
  name: entra-id
  namespace: {{< reuse "kgw-docs/snippets/namespace.md" >}}
spec:
  type: Static
  static:
    hosts:
    - host: login.microsoftonline.com
      port: 443
EOF
```

The port must be `443` because kgateway communicates with Entra ID over HTTPS.

> [!NOTE]
> This address is separate from the public Entra ID URL that you configure on the `GatewayExtension`. The `Backend` provides the network path for token exchange and OIDC discovery. The browser does not need to reach it.

### Configure TLS for the Entra ID Backend {#configure-tls}

Entra ID uses a certificate from a public, trusted CA, so you can use the system's trusted CA certificates.

```yaml
kubectl apply -f- <<EOF
apiVersion: gateway.kgateway.dev/v1alpha1
kind: BackendConfigPolicy
metadata:
  name: entra-id-tls
  namespace: {{< reuse "kgw-docs/snippets/namespace.md" >}}
spec:
  targetRefs:
    - group: gateway.kgateway.dev
      kind: Backend
      name: entra-id
  tls:
    sni: login.microsoftonline.com
    wellKnownCACertificates: System
EOF
```
## Next steps

Microsoft Entra ID is configured and the gateway can reach it. Now protect a route with the flow that matches how your clients arrive.

{{< cards >}}
{{< card link="../authorization-code" title="Authorization code flow" subtitle="Redirect browser users to Entra ID to log in, and store their tokens in session cookies." >}}
{{< card link="../access-token" title="Access token validation" subtitle="Validate a JWT that an API client already holds, and reject requests without one." >}}
{{< /cards >}}

## Cleanup {#cleanup}

{{< reuse "kgw-docs/snippets/cleanup.md" >}}

1. Remove the resources from this page only after you have cleaned up whichever flow you configured.

   ```sh
   kubectl delete BackendConfigPolicy entra-id-tls -n {{< reuse "kgw-docs/snippets/namespace.md" >}}
   kubectl delete Backend entra-id -n {{< reuse "kgw-docs/snippets/namespace.md" >}}
   ```

2. To remove Entra ID, delete the App Registration from the Microsoft Entra admin center.