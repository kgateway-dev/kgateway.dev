Set up a Keycloak instance, register kgateway as an OAuth2 client, and give the gateway a network path to reach Keycloak. Every Keycloak guide in this section starts here.

When you finish, you choose an authentication flow:

* [Authorization code flow]({{< link-hextra path="/security/oauth/keycloak/authorization-code/" >}}) for browser traffic.
* [Access token validation]({{< link-hextra path="/security/oauth/keycloak/access-token/" >}}) for API clients that already hold a token.

## Before you begin

{{< reuse "kgw-docs/snippets/prereq.md" >}}

The authorization code flow additionally requires an **HTTPS listener** on your gateway. Kgateway sets the OAuth2 nonce and code verifier cookies with the `Secure` attribute, so browsers do not return them over plain HTTP and the callback fails CSRF validation. To add an HTTPS listener, see [HTTPS listener]({{< link-hextra path="/setup/listeners/https/" >}}). The access token validation flow works over HTTP, because it does not use cookies.

## Install Keycloak

Deploy a Keycloak instance to test this guide against. The following steps create one from a single manifest, with the admin credentials `admin/admin` and a self-signed certificate for HTTPS.

> [!IMPORTANT]
> These steps are for testing this guide only. Running Keycloak in production involves decisions that are outside the scope of kgateway's documentation, such as an external database, clustering, and certificates from a CA that your gateway trusts. For that, use the [Keycloak Operator](https://www.keycloak.org/operator/installation) and follow [Configuring Keycloak for production](https://www.keycloak.org/server/configuration-production). The steps below are not a production install.

1. Create the `keycloak` namespace.

   ```sh
   kubectl create namespace keycloak
   ```

2. Generate a self-signed certificate for Keycloak and store it in a Secret.

   ```sh
   openssl req -x509 -newkey rsa:4096 -keyout tls.key -out tls.crt -days 365 -nodes -subj "/CN=keycloak.keycloak.svc.cluster.local"
   kubectl create secret tls keycloak-tls -n keycloak --cert=tls.crt --key=tls.key
   ```

3. Deploy Keycloak.

   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: v1
   kind: Service
   metadata:
     name: keycloak
     namespace: keycloak
   spec:
     selector:
       app: keycloak
     ports:
       - name: https
         port: 8443
         targetPort: 8443
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
             args: ["start-dev", "--https-port=8443"]
             env:
               - name: KEYCLOAK_ADMIN
                 value: "admin"
               - name: KEYCLOAK_ADMIN_PASSWORD
                 value: "admin"
               - name: KC_HTTPS_CERTIFICATE_FILE
                 value: /opt/keycloak/conf/tls.crt
               - name: KC_HTTPS_CERTIFICATE_KEY_FILE
                 value: /opt/keycloak/conf/tls.key
             ports:
               - name: https
                 containerPort: 8443
             volumeMounts:
               - name: keycloak-tls
                 mountPath: /opt/keycloak/conf
         volumes:
           - name: keycloak-tls
             secret:
               secretName: keycloak-tls
   EOF
   ```

4. Wait for Keycloak to be ready.

   ```sh
   kubectl rollout status deployment/keycloak -n keycloak
   ```

## Configure Keycloak

Create a realm, register kgateway as a confidential client, and add a test user. You return to the admin console values that you collect here, such as the client secret, when you create the kgateway resources.

### Access the Keycloak admin console

1. Port-forward to the Keycloak service.

   ```sh
   kubectl port-forward svc/keycloak -n keycloak 8443:8443
   ```

2. Open `https://localhost:8443` in your browser. Because Keycloak uses a self-signed certificate, accept the browser warning.

3. Log in with username `admin` and password `admin`.

{{< reuse-image src="img/keycloak/keycloak-login.png" >}}
{{< reuse-image-dark srcDark="img/keycloak/keycloak-login.png" >}}

### Create a new realm

1. Open the realm dropdown in the upper-left corner and click **Create realm**.
2. Enter a realm name, such as `myrealm`.
3. Click **Create**.

{{< reuse-image src="img/keycloak/realm-creation.png" >}}
{{< reuse-image-dark srcDark="img/keycloak/realm-creation.png" >}}

### Create a client

1. Click **Clients** in the left sidebar.
2. Click **Create client**.
3. Set **Client ID** (such as, `kgateway-client`).
4. Enable **Client authentication**.

{{< reuse-image src="img/keycloak/client-creation.png" >}}
{{< reuse-image-dark srcDark="img/keycloak/client-creation.png" >}}

5. Click **Next**.
6. On the **Capability config** page, verify that the authentication flows that you need are enabled. Both are enabled by default.
   * **Standard flow** issues authorization codes, which the authorization code flow requires.
   * **Direct access grants** enables the `password` grant, which the access token validation steps use to fetch a token for testing.
7. Click **Next**.

### Configure redirect URIs

Keycloak rejects the login request with `Invalid parameter: redirect_uri` unless the value that kgateway sends is registered on the client. You set that value explicitly in the `redirectURI` field of the `GatewayExtension` in the [authorization code flow]({{< link-hextra path="/security/oauth/keycloak/authorization-code/" >}}) guide, so register the identical string here.

1. In **Valid redirect URIs**, add the callback URL for your gateway, where the host is the hostname that the browser uses to reach your route.

   ```text
   https://www.example.com/oauth2/redirect
   ```

   {{< reuse-image src="img/keycloak/client-redirect-uri.png" >}}
   {{< reuse-image-dark srcDark="img/keycloak/client-redirect-uri.png" >}}

2. Click **Save**.

> [!WARNING]
> Do not register a wildcard redirect URI such as `https://www.example.com/*`. A wildcard lets an attacker who can influence the `redirect_uri` parameter send the authorization code to a path that you do not control. Register the exact callback path instead.

### Note the client secret

1. Go to the **Credentials** tab of your client.
2. Copy the **Client secret** — you need it for the `oauth2-client-secret` in the next section.

{{< reuse-image src="img/keycloak/client-secret.png" >}}
{{< reuse-image-dark srcDark="img/keycloak/client-secret.png" >}}

### Create a test user

1. Click **Users** in the left sidebar.
2. Click **Add user**.
3. Set **Username** (such as, `testuser`).
4. Click **Create**.

{{< reuse-image src="img/keycloak/user-created.png" >}}
{{< reuse-image-dark srcDark="img/keycloak/user-created.png" >}}

### Set a password for the test user

1. Go to the **Credentials** tab.
2. Set a password (such as, `password`).
3. Turn **Temporary** off.
4. Click **Set Password**.

{{< reuse-image src="img/keycloak/user-password.png" >}}
{{< reuse-image-dark srcDark="img/keycloak/user-password.png" >}}

### Add an audience mapper {#audience-mapper}

Complete this step only if you plan to use the access token validation flow.

By default, Keycloak does not put your client ID in the `aud` claim of an access token. A token that is issued to `kgateway-client` carries `"aud": "account"`, which is the realm's built-in account client. Passing an `audience` parameter to the token endpoint does not change this, because Keycloak derives the audience from the client's protocol mappers rather than from the request.

Add an audience mapper so that tokens carry your client ID, which lets the JWT policy restrict access to this client.

1. Open your client and go to the **Client scopes** tab.
2. Click the dedicated scope for your client, which is named `kgateway-client-dedicated`.
3. Click **Add mapper** > **By configuration** > **Audience**.
4. Set **Name** to `kgateway-audience`.
5. Set **Included Client Audience** to `kgateway-client`.
6. Verify that **Add to access token** is on.
7. Click **Save**.

Tokens for this client now include `"aud": ["kgateway-client", "account"]`.

> [!NOTE]
> The steps above create the `myrealm` realm for testing only. For production, use a dedicated Keycloak instance with a certificate from a CA that the gateway trusts, and a realm that your organization manages.

## Connect kgateway to Keycloak

Both authentication flows need a network path from the gateway to Keycloak. Create these two resources first, whichever flow you use.

### Create a Backend for Keycloak {#create-backend}

Create a `Backend` resource that defines how kgateway reaches your Keycloak instance. This Backend uses the `Static` type with the host and port configured for Keycloak.

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
    - host: keycloak.keycloak.svc.cluster.local
      port: 8443
EOF
```

Set `host` and `port` to the address and port that kgateway uses to reach Keycloak from inside the cluster. The example values match the Service that you created in [Install Keycloak](#install-keycloak), which listens on port `8443`. If you deployed Keycloak another way, check the port on its Service.

```sh
kubectl get svc keycloak -n keycloak
```

> [!NOTE]
> This address is separate from the public Keycloak URL that you configure on the `GatewayExtension` in the next steps. The `Backend` is the network path that the gateway uses for token exchange and OIDC discovery, and it does not have to be reachable from the browser.

### Configure TLS for the Keycloak Backend {#configure-tls}

The Keycloak instance in this guide serves HTTPS with a self-signed certificate, which the gateway does not trust. Create a `BackendConfigPolicy` that skips TLS verification for the Keycloak `Backend`.

> [!WARNING]
> `insecureSkipVerify` disables certificate verification for traffic to Keycloak, which means the gateway cannot detect a man-in-the-middle on that connection. Use it only with the self-signed test instance. For production, give Keycloak a certificate from a CA that the gateway trusts.

```yaml
kubectl apply -f- <<EOF
apiVersion: gateway.kgateway.dev/v1alpha1
kind: BackendConfigPolicy
metadata:
  name: keycloak-tls
  namespace: {{< reuse "kgw-docs/snippets/namespace.md" >}}
spec:
  targetRefs:
    - group: gateway.kgateway.dev
      kind: Backend
      name: keycloak
  tls:
    insecureSkipVerify: true
EOF
```

## Next steps

Keycloak is configured and the gateway can reach it. Now protect a route with the flow that matches how your clients arrive.

{{< cards >}}
  {{< card link="../authorization-code" title="Authorization code flow" subtitle="Redirect browser users to Keycloak to log in, and store their tokens in session cookies." >}}
  {{< card link="../access-token" title="Access token validation" subtitle="Validate a token that an API client already holds, and reject requests without one." >}}
{{< /cards >}}

## Cleanup {#cleanup}

{{< reuse "kgw-docs/snippets/cleanup.md" >}}

1. Remove the resources from this page only after you have cleaned up whichever flow you configured.

   ```sh
   kubectl delete BackendConfigPolicy keycloak-tls -n {{< reuse "kgw-docs/snippets/namespace.md" >}}
   kubectl delete Backend keycloak -n {{< reuse "kgw-docs/snippets/namespace.md" >}}
   ```

2. To remove Keycloak, delete its namespace.

   ```sh
   kubectl delete namespace keycloak
   ```
