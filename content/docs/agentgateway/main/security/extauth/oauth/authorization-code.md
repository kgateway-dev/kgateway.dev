---
title: Authorization code
description: Use authorization codes to authenticate requests with an external identity provider.
weight: 15
---

For more information or other OAuth options, see the [OAuth about page]({{< link path="/security/extauth/oauth/about/" >}}).

## Before you begin {#before}

{{< reuse "conrefs/snippets/agentgateway/prereqs.md" >}}

## Step 1: Set up your Identity Provider {#identity-provider}

Set up an OpenID Connect (OIDC) compatible identity provider (IdP).

For example, you can use [Keycloak as an IdP]({{< link path="/security/extauth/oauth/keycloak/" >}}).

## Step 2: Enforce authorization code {#authconfig}

Use AuthConfig and {{< reuse "docs/snippets/trafficpolicy.md" >}} resources to apply the auth rules to the routes that you want to secure with authorization code OAuth.

1. Create a Kubernetes secret to store your Keycloak client credentials. 

   ```yaml 
   kubectl apply -f - <<EOF
   apiVersion: v1
   kind: Secret
   metadata:
     name: oauth-keycloak
     namespace: {{< reuse "docs/snippets/namespace.md" >}}
   type: extauth.solo.io/oauth
   stringData:
     client-secret: ${KEYCLOAK_SECRET}
   EOF
   ```

2. Create an AuthConfig resource with your authorization code OAuth rules.

   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: extauth.solo.io/v1
   kind: AuthConfig
   metadata:
     name: oauth-authorization-code
     namespace: {{< reuse "docs/snippets/namespace.md" >}}
   spec:
     configs:
     - oauth2:
         oidcAuthorizationCode:
           appUrl: "http://${INGRESS_GW_ADDRESS}:80"
           callbackPath: /openai
           clientId: ${KEYCLOAK_CLIENT}
           clientSecretRef:
             name: oauth-keycloak
             namespace: {{< reuse "docs/snippets/namespace.md" >}}
           issuerUrl: "${KEYCLOAK_URL}/realms/master/"
           scopes:
           - email
           session:
             failOnFetchFailure: true
             redis:
               cookieName: keycloak-session
               options:
                 host: {{< reuse "conrefs/snippets/gateway/redis-name.md" >}}:6379
           headers:
             idTokenHeader: jwt
   EOF
   ```
   
   {{% reuse "conrefs/snippets/field-desc/review-table.md" %}} For more authorization code options, see the [Gloo Edge API docs](https://docs.solo.io/gloo-edge/main/reference/api/github.com/solo-io/gloo/projects/gloo/api/v1/enterprise/options/extauth/v1/extauth.proto.sk/#oidcauthorizationcode).

   | Field | Description |
   | ----- | ----------- |
   | `oauth2.oidcAuthorizationCode` | Set up the OAuth policy to authenticate requests with an authorization code. |
   | `appUrl` | The public URL of the app that you want to set up external auth for. This setting is used in combination with the `callbackPath` attribute. |
   | `callbackPath` | The callback path, relative to the `appUrl` setting. After a user authenticates, the IdP redirects the user to this callback URL. {{< reuse "conrefs/snippets/product-names.md" >}} intercepts requests with this path, exchanges the authorization code received from the IdP for an ID token, places the ID token in a cookie on the request, and forwards the request to its original destination. **Note**: The callback path must have a matching route that the {{< reuse "docs/snippets/trafficpolicy.md" >}} applies to. For example, you could simply have a `/` path-prefix route which would match any callback path. The important part of this callback “catch all” route is that the request goes through the routing filters, including external auth. |
   | `clientId` | The client ID token that you got when you registered your app with the IdP. In this example, you set the client ID when you set up Keycloak. |
   | `clientSecretRef` | The Kubernetes secret that has the client secret that you got when you registered your app with the identity provider. The secret must exist on the same cluster as the external auth service that enforces this policy. In this example, you created the secret in an earlier step. |
   | `issuerUrl` | The URL of the OpenID Connect IdP. {{< reuse "conrefs/snippets/product-names.md" >}} automatically discovers OIDC configuration by querying the `.well-known/openid-configuration` endpoint on the `issuer_url`. In this example, {{< reuse "conrefs/snippets/product-names.md" >}} expects to find OIDC discovery information at `"${KEYCLOAK_URL}/realms/master/"`. |
   | `scopes` | Scopes to request in addition to the `openid` scope, such as `email` in this example. |
   | `session` | Details on how to store the user session details. In this example, the cookie is stored as by the name `keycloak-session` in a Redis instance that is set up for the external auth service by default. {{< reuse "conrefs/snippets/gateway/redis-name-note.md" >}} |
   | `headers` | Forward the ID token to the destination after successful authentication. In this example, the ID token is sent as a JWT. |

3. Create an {{< reuse "docs/snippets/trafficpolicy.md" >}} resource that refers to the AuthConfig that you created. The following policy applies external auth to all routes that the Gateway serves.

   ```yaml
   kubectl apply -f - <<EOF
   apiVersion: {{< reuse "docs/snippets/trafficpolicy-apiversion.md" >}}
   kind: {{< reuse "docs/snippets/trafficpolicy.md" >}}
   metadata:
     name: oauth-authorization-code
     namespace: {{< reuse "docs/snippets/namespace.md" >}}
   spec:
     targetRefs:
       - group: gateway.networking.k8s.io
         kind: Gateway
         name: agentgateway-proxy
     traffic:
       entExtAuth:
         authConfigRef:
           name: oauth-authorization-code
           namespace: {{< reuse "docs/snippets/namespace.md" >}}
         backendRef:
           name: ext-auth-service-enterprise-agentgateway
           namespace: {{< reuse "docs/snippets/namespace.md" >}}
           port: 8083
   EOF
   ```

4. Verify that the AuthConfig is `ACCEPTED`.

   ```sh
   kubectl get authconfig oauth-authorization-code -n {{< reuse "docs/snippets/namespace.md" >}} -o yaml
   ```

   If you see a `REJECTED` error similar to `invalid character 'k' looking for beginning of object key string`, try copying the values of your environment variables manually into the AuthConfig resource.

## Step 3: Verify access token validation {#verify}

1. Send a request to your LLM. Verify that the request is not forwarded to the LLM. Instead, a 302 HTTP response code is returned with the Keycloak URL that you use to authenticate with Keycloak. 
   {{< tabs tabTotal= "2" >}}
   {{% tab tabName="Cloud Provider LoadBalancer" %}}
   ```sh
   curl -v "${INGRESS_GW_ADDRESS}:80/openai" -H content-type:application/json -d '{
    "model": "gpt-3.5-turbo",
    "messages": [
      {
        "role": "system",
        "content": "You are a poetic assistant, skilled in explaining complex programming concepts with creative flair."
      },
      {
        "role": "user",
        "content": "In the style of Shakespeare, write a series of sonnets that explain the concept of recursion in programming."
      }
    ]
   }'
   ```
   {{% /tab %}}
   {{% tab tabName="Port-forward for local testing" %}}
   ```sh
   curl -v "localhost:8080/openai" -H content-type:application/json -d '{
    "model": "gpt-3.5-turbo",
    "messages": [
      {
        "role": "system",
        "content": "You are a poetic assistant, skilled in explaining complex programming concepts with creative flair."
      },
      {
        "role": "user",
        "content": "In the style of Shakespeare, write a series of sonnets that explain the concept of recursion in programming."
      }
    ]
   }'
   ```
   {{% /tab %}}
   {{< /tabs >}}

   Example output: 
   ```
   HTTP/1.1 302 Found
   < location: http://172.18.0.16:8080/realms/master/protocol/openid-connect/auth?client_id=a3417aca-4214-4296-8664-482f159b2fac&redirect_uri=http%3A%2F%2F172.18.0.4%3A80%2Fopenai&response_type=code&scope=email+openid&state=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3Njg1MDYyNzMsImlhdCI6MTc2ODUwNDQ3MywibmJmIjoxNzY4NTA0NDczLCJzdGF0ZSI6Imh0dHA6Ly9sb2NhbGhvc3Qvb3BlbmFpIn0.768Q4wgQr3QxVtSC646tY1uLZZXLH3-QZG8kpyUgaC0
   ```

2. Open the redirect URL in your browser and verify that you see the Keycloak log in screen. Enter the user credentials from the IdP, such as the following values from the Keycloak setup to log in to Keycloak. 

   * Username: `user1`
   * Password: `password`

   {{< reuse-image src="img/keycloak-login.png" width="600px" >}}
   {{< reuse-image-dark srcDark="img/keycloak-login.png" width="600px">}}

   After the successful login, you are redirected to the callback URL. 

3. Inspect your browser, go to the **Network** tab and retrieve the **Cookie** that was issued from Keycloak from the `Set-Cookie` header. 
   
   Example cookie: 
   ```
   keycloak-session=ZLYHZ4XOGE6XDHY6YT256O45PB3KTPNCDHJRZOY6QGZUHPTM3TO5JTEYB7EUPMG7X7TRI34ZKY2EA3ZBZV7XZLMOKLRYWXPBDD3BRHI=
   ```

4. Store the cookie in an environment variable. 
   ```sh
   export COOKIE="<keycloak-session-id>"
   ```

5. Use the cookie to send a request to the Open AI provider. Verify that the request now succeeds. If you continue to see a 302 HTTP response code, the cookie might be expired. 
   {{< tabs tabTotal= "2" >}}
   {{% tab tabName="Cloud Provider LoadBalancer" %}}
   ```sh
   curl -v "${INGRESS_GW_ADDRESS}:80/openai" -H content-type:application/json -d '{
    "model": "gpt-3.5-turbo",
    "messages": [
      {
        "role": "system",
        "content": "You are a poetic assistant, skilled in explaining complex programming concepts with creative flair."
      },
      {
        "role": "user",
        "content": "In the style of Shakespeare, write a series of sonnets that explain the concept of recursion in programming."
      }
    ]
   }'
   ```
   {{% /tab %}}
   {{% tab tabName="Port-forward for local testing" %}}
   ```sh
   curl -v "localhost:8080/openai" -H content-type:application/json \
   -H "Cookie: $COOKIE" \
   -d '{
    "model": "gpt-3.5-turbo",
    "messages": [
      {
        "role": "system",
        "content": "You are a poetic assistant, skilled in explaining complex programming concepts with creative flair."
      },
      {
        "role": "user",
        "content": "In the style of Shakespeare, write a series of sonnets that explain the concept of recursion in programming."
      }
    ]
   }'
   ```
   {{% /tab %}}
   {{< /tabs >}}


## Cleanup

{{< reuse "conrefs/snippets/cleanup.md" >}}

```sh
kubectl delete authconfig oauth-authorization-code -n {{< reuse "docs/snippets/namespace.md" >}} 
kubectl delete {{< reuse "docs/snippets/trafficpolicy.md" >}} oauth-authorization-code -n {{< reuse "docs/snippets/namespace.md" >}}
kubectl delete secret oauth-keycloak -n {{< reuse "docs/snippets/namespace.md" >}}
```
