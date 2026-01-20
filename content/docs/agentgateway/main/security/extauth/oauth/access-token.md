---
title: Access token validation
description: Validate access tokens from an external identity provider.
weight: 10
---

For more information or other OAuth options, see the [OAuth about page]({{< link path="/security/extauth/oauth/about/" >}}).

## Before you begin {#before}

{{< reuse "conrefs/snippets/agentgateway/prereqs.md" >}}

## Step 1: Set up your Identity Provider {#identity-provider}

Set up an OpenID Connect (OIDC) compatible identity provider (IdP).

For example, you can use [Keycloak as an IdP]({{< link path="/security/extauth/oauth/keycloak/" >}}).

## Step 2: Enforce access token validation {#authconfig}

Use AuthConfig and {{< reuse "docs/snippets/trafficpolicy.md" >}} resources to apply the auth rules to the routes that you want to secure with access token validation.

1. Create an AuthConfig resource with your access token validation rules. The following example uses JWT validation and an inline JWKS server to provide the JWT. For more access token validation options, see the [Gloo Edge API docs](https://docs.solo.io/gloo-edge/main/reference/api/github.com/solo-io/gloo/projects/gloo/api/v1/enterprise/options/extauth/v1/extauth.proto.sk/#accesstokenvalidation). For more information about JWTs, see the [JWT guide]({{< link path="/security/jwt/" >}}).
   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: extauth.solo.io/v1
   kind: AuthConfig
   metadata:
     name: oauth-jwt-validation
     namespace: {{< reuse "docs/snippets/namespace.md" >}}
   spec:
     configs:
     - oauth2:
         accessTokenValidation:
           jwt:
             localJwks:
               inlineString: >-
                 $KEYCLOAK_CERT_KEYS
   EOF
   ```
   
   {{% reuse "conrefs/snippets/field-desc/review-table.md" %}}

   | Field | Description |
   | ----- | ----------- |
   | `oauth2.accessTokenValidation.jwt` | Set up the OAuth policy to validate access tokens that conform to the [JSON Web Token (JWT) specification](https://datatracker.ietf.org/doc/rfc7662/). |
   | `localJwks.inlineString` | Embed a local JWKS as a string, based on the value that you retrieved when you set up your IdP. |

2. Verify that the AuthConfig is in an **Accepted** state.

   ```sh
   kubectl get authconfig oauth-jwt-validation -n {{< reuse "docs/snippets/namespace.md" >}} -o yaml
   ```

   If you see a `REJECTED` error similar to `invalid character 'k' looking for beginning of object key string`, try copying the `$KEYCLOAK_CERT_KEYS` value manually again.

3. Create an {{< reuse "docs/snippets/trafficpolicy.md" >}} resource that refers to the AuthConfig that you earlier. The following policy applies external auth to all routes that the Gateway serves.

   ```yaml
   kubectl apply -f - <<EOF
   apiVersion: {{< reuse "docs/snippets/trafficpolicy-apiversion.md" >}}
   kind: {{< reuse "docs/snippets/trafficpolicy.md" >}}
   metadata:
     name: oauth-jwt-validation
     namespace: {{< reuse "docs/snippets/namespace.md" >}}
   spec:
     targetRefs:
       - group: gateway.networking.k8s.io
         kind: Gateway
         name: agentgateway-proxy
     traffic:
       entExtAuth:
         authConfigRef:
           name: oauth-jwt-validation
           namespace: {{< reuse "docs/snippets/namespace.md" >}}
         backendRef:
           name: ext-auth-service-enterprise-agentgateway
           namespace: {{< reuse "docs/snippets/namespace.md" >}}
           port: 8083
   EOF
   ```

## Step 3: Verify access token validation {#verify}

Send various requests to verify that OAuth is enforced for your routes.

1. Send a request to the OpenAI API without any token. Verify that the request fails with a 403 HTTP response code. 
   
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
   ...
   * upload completely sent off: 358 bytes
   < HTTP/1.1 403 Forbidden
   < content-type: text/plain
   < content-length: 29
   < 
   * Connection #0 to host localhost left intact
   external authorization failed%   
   ...
   ```

2. Generate an access token from your IdP, such as with the following command for Keycloak. If you get a `404` response, verify that the Keycloak URL and client credentials are correct. Common errors include using a different realm.

   ```sh
   export USER1_TOKEN=$(curl -Ssm 10 --fail-with-body \
   -d "client_id=${KEYCLOAK_CLIENT}" \
   -d "client_secret=${KEYCLOAK_SECRET}" \
   -d "username=user1" \
   -d "password=password" \
   -d "grant_type=password" \
   "$KEYCLOAK_URL/realms/master/protocol/openid-connect/token" |
   jq -r .access_token)
   ```

   ```sh
   echo $USER1_TOKEN
   ```

   Example output:
   
   ```console
   eyJhbGc...
   ```

3. Repeat the request with a valid token. Verify that the request now succeeds and returns a response from your LLM provider. 
   {{< tabs tabTotal= "2" >}}
   {{% tab tabName="Cloud Provider LoadBalancer" %}}
   ```sh
   curl -v "${INGRESS_GW_ADDRESS}:80/openai" -H content-type:application/
   -H "Authorization: Bearer $USER1_TOKEN"
   json -d '{
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
   -H "Authorization: Bearer $USER1_TOKEN" \
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

   Example output: 
   ```
   ...
   < HTTP/1.1 200 OK
   ...
   ```

## Cleanup

{{< reuse "conrefs/snippets/cleanup.md" >}}

```sh
kubectl delete authconfig oauth-jwt-validation -n {{< reuse "docs/snippets/namespace.md" >}}
kubectl delete {{< reuse "docs/snippets/trafficpolicy.md" >}} oauth-jwt-validation -n {{< reuse "docs/snippets/namespace.md" >}}
```
