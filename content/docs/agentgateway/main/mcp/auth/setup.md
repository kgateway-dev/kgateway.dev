---
title: Set up MCP auth
weight: 40
---

Secure your Model Context Protocol (MCP) servers with OAuth 2.0 authentication by using agentgateway and an identity provider like Keycloak.

## About this guide

In this guide, you explore how to configure the agentgateway proxy to protect a static MCP server with MCP auth by using Keycloak as an identity provider. To authenticate with the MCP server, MCP clients such as the MCP inspector tool, can dynamically register with the identity provider to obtain a client ID. Then, the MCP client uses the client ID during the OAuth flow to obtain the JWT token. Finally, the MCP client uses the JWT token to authenticate with the MCP server and access its tools. 

## Before you begin

1. Set up an [agentgateway proxy]({{< link-hextra path="/setup/" >}}).
2. Follow the steps to set up an [MCP server with a fetch tool]({{< link-hextra path="/mcp/static-mcp/" >}}).
3. Follow the steps to [set up Keycloak]({{< link-hextra path="/mcp/auth/keycloak/" >}}). 

## Configure MCP auth

With Keycloak deployed and your MCP backend configured, you can now create an {{< reuse "docs/snippets/trafficpolicy.md" >}} that enforces authentication for the MCP backend.

1. Create an {{< reuse "docs/snippets/trafficpolicy.md" >}} with MCP authentication configuration.
   ```yaml
   kubectl apply -f - <<EOF
   apiVersion: {{< reuse "docs/snippets/trafficpolicy-apiversion.md" >}}
   kind: {{< reuse "docs/snippets/trafficpolicy.md" >}}
   metadata:
     name: mcp-echo-authn
   spec:
     # Target the MCP backend to apply this authentication policy
     targetRefs:
     - group: agentgateway.dev
       kind: AgentgatewayBackend
       name: mcp-backend
     # Configure MCP authentication
     backend:
       mcp:
         authentication:
           # Issuer URL - must match the 'iss' claim in JWT tokens
           issuer: "${KEYCLOAK_ISSUER}"
           # JWKS configuration for token validation
           jwks:
             # Reference to the Keycloak service for fetching public keys
             backendRef:
               name: keycloak
               kind: Service
               namespace: keycloak
               port: 8080
             # Path to the JWKS endpoint on the issuer
             jwksPath: "${KEYCLOAK_JWKS_PATH}"
           # Expected audience in JWT tokens
           audiences:
           - http://localhost:8080/mcp
           # Validation mode: Strict requires all claims to be valid
           mode: Strict 
           # Identity provider type
           provider: Keycloak  
           # MCP resource metadata for OAuth discovery
           resourceMetadata:
             resourceMetadata:
               # Resource identifier for this MCP server
               resource: http://localhost:8080/mcp
               # Scopes supported by this MCP server
               scopesSupported:
               - email
               # Methods for providing bearer tokens
               bearerMethodsSupported:
               - header
               - body
               - query
   EOF
   ```

   | Setting | Description | 
   | -- | -- | 
   | `issuer` | The OAuth 2.0 issuer URL from your identity provider. This must exactly match the `iss` claim in JWT tokens. Agentgateway validates this claim to ensure tokens come from the expected identity provider. | 
   | `jwks.backendRef` | The Keycloak service. | 
   | `jwks.jwksPath` | The path to the JWKS endpoint to obtain public keys. | 
   | `audiences` | The purpose of the JWT token. This value must match the `aud` claim in JWT tokens. | 
   | `mode` | The JWT validation mode. In this example, strict validation is enforced. This mode requires all claims to be valid for agentgateway to proceed with the OAth flow. | 
   | `provider` | The identity provider that you use. In this example, Keycloak is used. | 
   | `resourceMetadata.resource` | The identifier for the resource. In this example, the MCP server address is used.  | 
   | `resourceMetadata.scopesSupported` | The scopes that the client can request for accessing the MCP server. | 
   | `resourceMetadat.bearerMethodsSupported` | Methods to provide the bearer token when authenticating with the server. In this example, the bearer token can be provided as a header, query parameter, or as part of the body. |

2. Verify the policy was accepted.
   ```sh
   kubectl get {{< reuse "docs/snippets/trafficpolicy.md" >}} mcp-echo-authn -o yaml
   ```

3. Update the HTTPRoute that routes incoming traffic to the MCP server to include the discovery paths for the MCP resource and authorization server. This way, the agentgateway proxy can retrieve the resource and authorization server metadata during the MCP auth flow. 
   ```yaml
   kubectl apply -f - <<EOF
   apiVersion: gateway.networking.k8s.io/v1
   kind: HTTPRoute
   metadata:
     name: mcp
   spec:
     # Reference the Agentgateway
     parentRefs:
     - group: gateway.networking.k8s.io
       kind: Gateway
       name: agentgateway-proxy
       namespace: agentgateway-system
     rules:
     - filters:
        # Enable CORS for browser-based MCP clients
         - type: CORS
           cors:
             allowCredentials: true
             allowHeaders:
               - Origin
               - Authorization
               - Content-Type
             allowMethods:
               - "*"
             allowOrigins:
               - "*"
             exposeHeaders:
               - Origin
               - X-HTTPRoute-Header
             maxAge: 86400
       # Route to the MCP backend
       backendRefs:
       - group: agentgateway.dev
         kind: AgentgatewayBackend
         name: mcp-backend
       # Match MCP and OAuth discovery paths
       matches:
       # Main MCP endpoint to connect to the MCP server
       - path:
           type: PathPrefix
           value: /mcp
       # Path to access resouce server metadata
       - path:
           type: PathPrefix
           value: /.well-known/oauth-protected-resource/mcp
       # Path to access authorization server metadata
       - path:
           type: PathPrefix
           value: /.well-known/oauth-authorization-server/mcp
       # JWKS endpoint for token validation
       - path:
           type: PathPrefix
           value: /realms/master/protocol/openid-connect/certs
   EOF
   ```

## Verify MCP auth 

1. Open the MCP inspector. 
   ```sh
   npx modelcontextprotocol/inspector#{{% reuse "docs/versions/mcp-inspector.md" %}}
   ```

2. From the MCP Inspector menu, connect to your agentgateway address as follows:
   * **Transport Type**: Select `Streamable HTTP`.
   * **URL**: Enter the agentgateway address, port, and the /mcp path. If your agentgateway proxy is exposed with a LoadBalancer server, use `http://${INGRESS_GW_ADDRESS}/mcp`. In local test setups where you port-forwarded the agentgateway proxy on your local machine, use `http://localhost:8080/mcp`.
   * Click **Connect**.

   Verify that the connection fails, because authentication is required to access the MCP server. 

   {{< reuse-image src="img/mcp-auth-connect-error.png" >}}
   {{< reuse-image-dark srcDark="img/mcp-auth-connect-error-dark.png" >}}

3. Click **Open Auth Settings** to run through the MCP Auth flow that you configured with the agentgateway proxy. 

4. Run through the auth flow. You can decide to manually run through the auth flow or select **Quick OAuth Flow** to automatically run through all the auth steps automatically. This guide assumes that you run through the auth flow manually. 
   1. In the **OAuth Flow Progress** card, click **Continue** to start the **Metadata Discovery** phase. Verify that the step succeeds and that you see the authorization server metadata. The metadata include information about the location of the authorization server, supported scopes, and ways to provide the bearer token. 
      {{< reuse-image src="img/oauth-resource-metadata.png" >}}
      {{< reuse-image-dark srcDark="img/oauth-resource-metadata-dark.png" >}}
   2. Click **Continue** to start the **Client registration** phase. Verify that the MCP inspector tool successfully registered as a client in Keycloak and to assigned a client ID. 
      {{< reuse-image src="img/oauth-client-registration.png" >}}
      {{< reuse-image-dark srcDark="img/oauth-client-registration-dark.png" >}}
   3. Click **Continue** to start the **Preparing Authorization** phase. Verify that you get back a URL to log in to Keycloak with your credentials. Open the link in your browser and log in with the user `user1` and password `password`. 
      {{< reuse-image src="img/oauth-prepare-auth.png" >}}
      {{< reuse-image-dark srcDark="img/oauth-prepare-auth-dark.png" >}}

      After you log in to Keycloak, an authorization code is displayed. Copy the authorization code and continue with the next step. 
   4. Copy the authorization code into the **Authorization Code** field in the MCP inspector. Then, click **Continue** to start the **Request Authorization and acquire authorization code** phase. 
      {{< reuse-image src="img/oauth-auth-code.png" >}}
      {{< reuse-image-dark srcDark="img/oauth-auth-code-dark.png" >}}
   5. Click **Continue** to start the **Token Request** phase. In this phase, the authorization code is exchanged for a token. Verify that the **Authentication Complete** phase succeeds and that you get back a token from Keycloak. 
      {{< reuse-image src="img/oauth-token.png" >}}
      {{< reuse-image-dark srcDark="img/oauth-token-dark.png" >}}
   6. Connect to your MCP server. 
      1. Copy the `access_token` value from the **Authentication Complete** phase. 
      2. Open the **Authentication** section in the MCP inspector. 
      3. In the **Custom Headers** card, click **Add**. 
      4. Add the following values: 
         * header name: `Authorization`
         * header value: `Bearer <value of access_token>
      5. Click **Connect** to connect to your MCP server. 
      {{< reuse-image src="img/oauth-connect-to-server.png" >}}
      {{< reuse-image-dark srcDark="img/oauth-connect-to-server-dark.png" >}}


## Clean up

{{< reuse "docs/snippets/cleanup.md" >}}

```sh
kubectl delete {{< reuse "docs/snippets/trafficpolicy.md" >}} mcp-echo-authn 
kubectl delete httproute mcp 
```

