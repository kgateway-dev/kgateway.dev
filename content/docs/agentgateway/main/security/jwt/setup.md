---
title: JWT auth
weight: 10
---

Secure your applications with JSON Web Token (JWT) authentication by using the agentgateway proxy and an identity provider like Keycloak. To learn more about JWT auth, see [About JWT authenticaiton]({{< link-hextra path="/security/jwt/about/" >}}). 

{{< reuse "docs/snippets/agentgateway/prereq.md" >}}

{{< reuse "docs/snippets/keycloak.md" >}}

## Set up JWT authentication

Configure an {{< reuse "docs/snippets/trafficpolicy.md" >}} to validate JWTs using a remote JWKS endpoint from Keycloak. This approach is recommended for production as it supports automatic key rotation.

1. Create an {{< reuse "docs/snippets/trafficpolicy.md" >}} with JWT authentication configuration.
   ```yaml
   kubectl apply -f - <<EOF
   apiVersion: {{< reuse "docs/snippets/trafficpolicy-apiversion.md" >}}
   kind: {{< reuse "docs/snippets/trafficpolicy.md" >}}
   metadata:
     name: jwt-auth-policy
     namespace: {{< reuse "docs/snippets/namespace.md" >}}
   spec:
     # Target the Gateway to apply JWT authentication to all routes
     targetRefs:
     - group: gateway.networking.k8s.io
       kind: Gateway
       name: agentgateway-proxy   
     # Configure JWT authentication
     traffic:
       jwtAuthentication:
         # Validation mode - determines how strictly JWTs are validated
         mode: Strict   
         # List of JWT providers (identity providers)
         providers:
         - # Issuer URL - must match the 'iss' claim in JWT tokens
           issuer: "${KEYCLOAK_ISSUER}"
           # JWKS configuration for remote key fetching
           jwks:
             remote:
               # Path to the JWKS endpoint, relative to the backend root
               jwksPath: "${KEYCLOAK_JWKS_PATH}"
               # Cache duration for JWKS keys (reduces load on identity provider)
               cacheDuration: "5m"
               # Reference to the Keycloak service
               backendRef:
                 group: ""
                 kind: Service
                 name: keycloak
                 namespace: keycloak
                 port: 8080
   EOF
   ```

   | Field | Description | Example |
   |-------|-------------|---------|
   | `mode` | Validation mode for JWT authentication. `Strict` requires a valid JWT for all requests. `Optional` validates JWTs if present but allows requests without tokens. `Permissive` is the least strict mode. | `Strict` |
   | `issuer` | The issuer URL that must match the `iss` claim in JWT tokens exactly. Agentgateway rejects tokens from other issuers. | `http://keycloak:8080/realms/master` |
   | `audiences` | List of allowed audience values. The JWT's `aud` claim must contain at least one of these values. If not specified, any audience is accepted. | `["my-application"]` |
   | `jwks.remote.jwksPath` | The path to the JWKS endpoint on the identity provider, relative to the backend root. This endpoint returns the public keys used to verify JWT signatures. | `/realms/master/protocol/openid-connect/certs` |
   | `jwks.remote.cacheDuration` | How long to cache the JWKS keys locally. This reduces load on the identity provider and improves performance. Keys are automatically refreshed when the cache expires. | `5m` (5 minutes) |
   | `jwks.remote.backendRef` | Reference to the Kubernetes service that hosts the identity provider. Agentgateway uses this to fetch the JWKS from the identity provider. | Keycloak service |


2. View the details of the policy. Verify that the policy is accepted.
   ```sh
   kubectl get {{< reuse "docs/snippets/trafficpolicy.md" >}} jwt-auth-policy -n {{< reuse "docs/snippets/namespace.md" >}} -o json | jq '.status'
   ```

## Verify JWT authentication

Now that JWT authentication is configured, test the setup by obtaining a token from Keycloak and making authenticated requests.

1. Send a request to the httpbin app without any JWT token. Verify that the request fails with a 401 HTTP response code. 
   {{< tabs tabTotal= "2" items="Cloud Provider LoadBalancer,Port-forward for local testing" >}}
   {{% tab tabName="Cloud Provider LoadBalancer" %}}
   ```sh
   curl -v "${INGRESS_GW_ADDRESS}:80/headers" -H "host: www.example.com"
   ```
   {{% /tab %}}
   {{% tab tabName="Port-forward for local testing" %}}
   ```sh
   curl -i localhost:8080/headers -H "host: www.example.com"
   ```
   {{% /tab %}}
   {{< /tabs >}}

   Example output: 
   ```
   HTTP/1.1 401 Unauthorized
   content-type: text/plain
   response-gateway: response path /headers
   content-length: 45
   date: Mon, 19 Jan 2026 16:07:12 GMT

   authentication failure: no bearer token found%  
   ```      
   
2. Get an access token from Keycloak by using the password grant type.
   ```sh
   ACCESS_TOKEN=$(curl -s -X POST "${KEYCLOAK_URL}/realms/master/protocol/openid-connect/token" \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "grant_type=password" \
     -d "client_id=${KEYCLOAK_CLIENT}" \
     -d "client_secret=${KEYCLOAK_SECRET}" \
     -d "username=user1" \
     -d "password=password" \
     | jq -r '.access_token')
   
   echo $ACCESS_TOKEN
   ```

3. Repeat the request to the httpbin app. This time, include the JWT token that you received in the previous step. Verify that the request succeeds and you get back a 200 HTTP response code. 
   {{< tabs tabTotal= "2" items="Cloud Provider LoadBalancer,Port-forward for local testing" >}}
   {{% tab tabName="Cloud Provider LoadBalancer" %}}
   ```sh
   curl -v "${INGRESS_GW_ADDRESS}:80/headers" -H "host: www.example.com" -H "Authorization: Bearer ${ACCESS_TOKEN}"
   ```
   {{% /tab %}}
   {{% tab tabName="Port-forward for local testing" %}}
   ```sh
   curl -v "http://localhost:8080/headers" -H "host: www.example.com" -H "Authorization: Bearer ${ACCESS_TOKEN}"
   ```
   {{% /tab %}}
   {{< /tabs >}}

   Example output: 
   ```
   ...
   < HTTP/1.1 200 OK
   ...
   {
    "headers": {
      "Accept": [
        "*/*"
      ],
      "Host": [
        "www.example.com"
      ],
      "User-Agent": [
        "curl/8.7.1"
      ]
    }
   }
   ```
  

## Other JWT auth examples

Review other common JWT auth configuration examples that you can add to your {{< reuse "docs/snippets/trafficpolicy.md" >}}.

### Multiple JWT providers

You can configure multiple JWT providers to accept tokens from different identity providers. The following example uses Keycloak and the Auth0 identity providers. 

```yaml
traffic:
  jwtAuthentication:
    mode: Strict
    providers:
    - issuer: "${KEYCLOAK_ISSUER}"
      audiences: ["my-application"]
      jwks:
        remote:
          jwksPath: "${KEYCLOAK_JWKS_PATH}"
          backendRef:
            name: keycloak
            namespace: keycloak
            kind: Service
            port: 8080
    - issuer: "https://auth0.example.com/"
      audiences: ["my-other-application"]
      jwks:
        remote:
          jwksPath: "/.well-known/jwks.json"
          backendRef:
            name: auth0-proxy
            namespace: auth-system
            kind: Service
            port: 443
```

### Inline JWKS

For testing purposes, you can use inline JWKS instead of a remote JWKS endpoint. Note that this setup is not recommended for production as it requires manual key updates.

```yaml
traffic:
  jwtAuthentication:
    mode: Strict
    providers:
    - issuer: "${KEYCLOAK_ISSUER}"
      audiences: ["my-application"]
      jwks:
        inline: '{"keys":[{"kty":"RSA","kid":"key-id-123","use":"sig","n":"0vx7agoebG...","e":"AQAB"}]}'
```

### Allow missing

By default, the JWT validation mode is set to `Strict` and allows connections to a backend destination only if a valid JWT was provided as part of the request. 

To allow requests, even if no JWT was provided or if the JWT cannot be validated, use the `Permissive` or `Optional` modes. 

**Optional**

The JWT is optional. If a JWT is provided during the request, the agentgateway proxy validates it. In the case that the JWT validation fails, the request is denied. However, keep in mind that if no JWT is provided during the request, the request is explicitly allowed. 

```yaml
traffic:
  jwtAuthentication:
    mode: Optional
    providers:
    - issuer: "${KEYCLOAK_ISSUER}"
      audiences: ["my-application"]
      jwks:
        remote:
          jwksPath: "${KEYCLOAK_JWKS_PATH}"
          backendRef:
            name: keycloak
            namespace: keycloak
            kind: Service
            port: 8080
```

**Permissive** 

Requests are never rejected, even if no or invalid JWTs are provided during the request. 

```yaml
traffic:
  jwtAuthentication:
    mode: Permissive
    providers:
    - issuer: "${KEYCLOAK_ISSUER}"
      audiences: ["my-application"]
      jwks:
        remote:
          jwksPath: "${KEYCLOAK_JWKS_PATH}"
          backendRef:
            name: keycloak
            namespace: keycloak
            kind: Service
            port: 8080
```


## Cleanup

{{< reuse "docs/snippets/cleanup.md" >}}

```sh
kubectl delete {{< reuse "docs/snippets/trafficpolicy.md" >}} jwt-auth-policy -n {{< reuse "docs/snippets/namespace.md" >}}
kubectl delete ns keycloak
```
