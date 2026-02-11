---
title: kgateway v2.2 release blog
toc: false
publishDate: 2026-02-11T10:00:00-00:00
author: Nadine Spies, Nina Polshakova, Andy Fong, Lawrence Gadban, Daneyon Hansen 
excludeSearch: true
---

Kgateway v2.2 is packed with exciting new features and improvements. Here are a few select updates the kgateway team would like to highlight!

There have been major breaking changes regarding the agentgateway implementation! We have a new installation UX and new dedicated APIs. If you are currently running agentgateway with kgateway please refer to our [migration guide](https://github.com/kgateway-dev/kgateway/blob/main/docs/guides/agentgateway-migration.md). 

## 🔥Breaking changes

### Agentgateway-specific resources and Helm charts

This release separated kgateway and agentgateway controllers and introduced several agentgateway-specific resources, Helm charts, and controllers. Kgateway-specific resources were not changed. 

Note: If you used agentgateway with kgateway,  you must update and migrate your agentgateway-specific configuration to the new resources. Agentgateway-specific fields in kgateway resources, such as TrafficPolicy or GatewayParameters were deprecated. You cannot upgrade your environment without migrating your resources first!

The following table includes the new agentgateway-specific resources that were introduced in this release and compares them to kgateway. Make sure to migrate your agentgateway configuration to these new resources. 

| Resource | Agentgateway vs kgateway | Description of change
| -- | -- | -- | 
| GatewayClass | <b>agentgateway</b>: <ul><li>agentgateway</li></ul></br><b>kgateway</b>: <ul><li>kgateway</li></ul> | Adds agentgateway-specific GatewayClass. | 
| Controller name | <b>agentgateway</b>: <ul><li>agentgateway.dev/agentgateway</li></ul></br><b>kgateway</b>: <ul><li>kgateway.dev/kgateway</li></ul> | Adds agentgateway-specific controller. </br></br><b>Related PRs:</br><ul><li><a href="https://github.com/kgateway-dev/kgateway/pull/13088">13088</a></li></ul> | 
| Control plane deployment name | <b>agentgateway</b>: <ul><li>agentgateway</li></ul></br><b>kgateway</b>: <ul><li>kgateway</li></ul> | Adds agentgateway-specific control plane name. |
| Default namespace | <b>agentgateway</b>: <ul><li>agentgateway-system</li></ul></br><b>kgateway</b>: <ul><li>kgateway-system</li></ul> | Updates docs to use agentgateway-specific namespace. | 
| CRD Helm chart location | <b>agentgateway</b>: <ul><li>oci://cr.agentgateway.dev/charts/agentgateway-crds</li></ul></br><b>kgateway</b>: <ul><li>oci://cr.kgateway.dev/kgateway-dev/charts/kgateway-crds</li></ul> | Adds agentgateway-specific CRD Helm charts. </br></br><b>Related PRs:</br><ul><li><a href="https://github.com/kgateway-dev/kgateway/pull/13062">13062</a></li><li><a href="https://github.com/kgateway-dev/kgateway/pull/12960">12960</a></li></ul> |
| Controller Helm chart location | <b>agentgateway</b>: <ul><li>oci://cr.agentgateway.dev/charts/agentgateway</li></ul></br><b>kgateway</b>: <ul><li>oci://cr.kgateway.dev/kgateway-dev/charts/kgateway</li></ul> | Adds agentgateway-specific controller Helm charts. </br></br><b>Related PRs:</br><ul><li><a href="https://github.com/kgateway-dev/kgateway/pull/13062">13062</a></li><li><a href="https://github.com/kgateway-dev/kgateway/pull/12960">12960</a></li></ul> | 
| CRDs | <b>agentgateway</b>: <ul><li>AgentgatewayPolicy</li><li>AgentgatewayBackend</li><li>AgentgatewayParameters</li></ul></br><b>kgateway</b>: <ul><li>TrafficPolicy</li><li>Backend</li><li>GatewayParameters</li></ul> | Introduces agentgateway-specific custom resource. </br> Removes AI policy from TrafficPolicy. </br> Adds DirectResponse support to AgentgatewayPolicy. </br> Allows agentgateway proxy-specific parameters via AgentgatewayParameters resource only.</br></br><b>Related PRs:</br><ul><li><a href="https://github.com/kgateway-dev/kgateway/pull/12901">12901</a></li><li><a href="https://github.com/kgateway-dev/kgateway/pull/12723">12723</a></li><li><a href="https://github.com/kgateway-dev/kgateway/pull/13054">13054</a></li><li><a href="https://github.com/kgateway-dev/kgateway/pull/13018">13018</a></li><li><a href="https://github.com/kgateway-dev/kgateway/pull/13101">13101</a></li></ul> | 
| API version in CRDs | <b>agentgateway</b>: <ul><li>agentgateway.dev/v1alpha1</li></ul></br><b>kgateway</b>: <ul><li>kgateway.dev/v1alpha1</li></ul> | Updates agentgateway resources to use the new `agentgateway.dev` group. </br></br><b>Related PRs:</br><ul><li><a href="https://github.com/kgateway-dev/kgateway/pull/13013">13013</a></li></ul> | 
| Group in CRDs | <b>agentgateway</b>: <ul><li>agentgateway.dev</li></ul></br><b>kgateway</b>: <ul><li>gateway.kgateway.dev</li></ul> | Updates agentgateway resources to use the new `agentgateway.dev` group. | 


### Agentgateway-specific documentation moved

With the introduction of agentgateway-specific resources and Helm charts, the agentgateway documentation moved to the [agentgateway.dev](https://agentgateway.dev/docs/kubernetes) org. 

Kgateway-specific documentation for Envoy gateways did not move and continues to be accessible via the [kgateway.dev org](https://kgateway.dev/docs/envoy). 


### `KGW_ENABLE_EXPERIMENTAL_GATEWAY_API_FEATURES` to gate experimental Gateway API features and APIs

Use the `--set controller.extraEnv.KGW_ENABLE_GATEWAY_API_EXPERIMENTAL_FEATURES=true` setting in your Helm installation to enable experimental Kubernetes Gateway API features and APIs, such as the following: 

* XListenerSet
* Route SessionPersistence
* HTTPCORSFilter
* HTTPRouteRetry

By default, the `KGW_ENABLE_EXPERIMENTAL_GATEWAY_API_FEATURES` is set to `false`. For more information, see the related [kgateway PR](https://github.com/kgateway-dev/kgateway/pull/12695).

For setup steps, see the get started guide in the [kgateway](https://kgateway.dev/docs/envoy/latest/quickstart/) or [agentgateway](https://agentgateway.dev/docs/kubernetes/latest/quickstart/) docs.

### Agentgateway ExtAuth policies fail closed

Agentgateway external auth policies now fail closed when the auth server that is referenced in the backendRef is invalid. Previously, external auth policies failed open. 

See this [PR](https://github.com/kgateway-dev/kgateway/pull/13273) for more information. 

### AI prompt guard API alignment

The AI prompt guard API is updated to align with other enums. The values change from `MASK` to `Mask` and `REJECT` to `Reject` as shown in the following example. These changes are enforced by CEL validation in the API.

```yaml
kubectl apply -f - <<EOF
apiVersion: agentgateway.dev/v1alpha1
kind: AgentgatewayPolicy
metadata:
  name: openai-prompt-guard
  namespace: agentgateway-system
  labels:
    app: agentgateway
spec:
  targetRefs:
  - group: gateway.networking.k8s.io
    kind: HTTPRoute
    name: openai
  backend:
    ai:
      promptGuard:
        request:
        - response:
            message: "Rejected due to inappropriate content"
          regex:
            action: Reject
            matches:
            - "credit card"
EOF
```

For steps to set up prompt guards, see the [docs](https://agentgateway.dev/docs/kubernetes/latest/llm/prompt-guards/). 


##  🗑️ Deprecated or removed features

### HTTPListenerPolicy is deprecated

The HTTPListenerPolicy is now deprecated and is planned to be removed in future releases. If you currently use policies in the HTTPListenerPolicy resource, migrate them to the httpSettings under the ListenerPolicy. 

See this [PR](https://github.com/kgateway-dev/kgateway/pull/13066) for more information.

To learn more about the ListenerPolicy, see the [docs](https://kgateway.dev/docs/envoy/latest/about/policies/listenerpolicy/). 

### PerConnectionBufferLimit annotation deprecated 

The  PerConnectionBufferLimit annotation on Gateway resources is deprecated. Configure PerConnectionBufferLimit  on the ListenerPolicy instead. For an example, see the [docs](https://kgateway.dev/docs/envoy/latest/traffic-management/buffering/). 

See this [PR](https://github.com/kgateway-dev/kgateway/pull/13016) for more information.

### `spec.kube.floatingUserId` field removed from GatewayParameters CRD

This field was previously used to unset runAsUser values in security contexts. When migrating, users should use the supported `spec.kube.omitDefaultSecurityContext` field instead. When set to true, this field prevents the controller from injecting opinionated default security contexts, allowing your platform (e.g., OCP) to dynamically provide the appropriate security contexts. 

See this [PR](https://github.com/kgateway-dev/kgateway/pull/12747) for more information.


## 🌟New features

### Highlighted agentgateway features

#### MCP authentication

MCP authentication enables OAuth 2.0 protection for MCP servers, helping to implement the MCP Authorization specification. Agentgateway can act as a resource server, validating JWT tokens and exposing protected resource metadata.

The MCP authentication policy can be attached to an MCP backend using the AgentgatewayPolicy or inlined on the AgentgatewayBackend:

```yaml
apiVersion: agentgateway.dev/v1alpha1
kind: AgentgatewayPolicy
metadata:
 name: keycloak-mcp-authn-policy
 namespace: default
spec:
 targetRefs:
   - name: mcp-backend-static
     kind: AgentgatewayBackend
     group: agentgateway.dev
 backend:
   mcp:
     authentication:
       issuer: http://keycloak:7080/realms/mcp
       jwks:
         jwksPath: realms/mcp/protocol/openid-connect/certs
         backendRef:
           group: ""
           kind: Service
           name: keycloak
           port: 7080
       audiences:
         - "account"
       provider: Keycloak
       resourceMetadata:
         resource: http://mcp-website-fetcher.default.svc.cluster.local/mcp
         scopesSupported: '["tools/call/fetch"]'
         bearerMethodsSupported: '["header"]'
         resourceDocumentation: http://mcp-website-fetcher.default.svc.cluster.local/docs
         resourcePolicyUri: http://mcp-website-fetcher.default.svc.cluster.local/policies
```

See the following PRs for more information:
* [12966](https://github.com/kgateway-dev/kgateway/pull/12966)
* [13111](https://github.com/kgateway-dev/kgateway/pull/13111)

For setup steps, see the [docs](https://agentgateway.dev/docs/kubernetes/latest/mcp/auth/). 

##### Inline and remote JWKS support

You can now define both inline and remote JWKS endpoints to automatically fetch and rotate keys from your identity provider on the AgentgatewayPolicy. See this [PR](https://github.com/kgateway-dev/kgateway/pull/12850) for more information. 

```yaml
kubectl apply -f - <<EOF
apiVersion: agentgateway.dev/v1alpha1
kind: AgentgatewayPolicy
metadata:
  name: jwt-auth-policy
  namespace: agentgateway-system
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

You can also set TLS options when connecting to a remote JWKS source. See this [PR](https://github.com/kgateway-dev/kgateway/pull/13014) for more information. 

To see an example in agentgateway, see the [docs](https://agentgateway.dev/docs/kubernetes/latest/security/jwt/setup/). 

#### Azure OpenAI backends

Agentgateway now natively supports Azure OpenAI backends:

```yaml
apiVersion: agentgateway.dev/v1alpha1
kind: AgentgatewayBackend
metadata:
 name: ai-providers
spec:
 ai:
   groups:
   - providers:
     - name: azure
       azureopenai:
         endpoint: test
```

See this [PR](https://github.com/kgateway-dev/kgateway/pull/12836) for more information. 

For setup steps, see the [docs](https://agentgateway.dev/docs/kubernetes/latest/llm/providers/azureopenai/). 

#### Model aliasing

The modelAliases field in the AgentgatewayPolicy now allows users to define friendly model name aliases that map to actual provider model names (e.g., "fast" can map to "gpt-3.5-turbo").

```yaml
apiVersion: agentgateway.dev/v1alpha1
kind: AgentgatewayPolicy
metadata:
 name: backend-ai-prompt
spec:
 targetRefs:
   - group: "agentgateway.dev"
     kind: AgentgatewayBackend
     name: test
 backend:
   ai:
     modelAliases:
       fast: gpt-3.5-turbo
       smart: gpt-4-turbo
```

See this [PR](https://github.com/kgateway-dev/kgateway/pull/12479) for more information.

#### CSRF

Cross-Site Request Forgery (CSRF) is an attack that tricks an authenticated user into unknowingly executing actions chosen by an attacker. While application frameworks commonly provide CSRF protections, agentgateway allows enforcing these defenses at a centralized access point, reducing the burden on individual application teams.

You can now configure CSRF policies using the traffic field in the AgentgatewayPolicy:

```yaml
apiVersion: agentgateway.dev/v1alpha1
kind: AgentgatewayPolicy
metadata:
 name: csrf-gw-policy
 namespace: agentgateway-base
spec:
 targetRefs:
 - group: gateway.networking.k8s.io
   kind: Gateway
   name: gw
 traffic:
   csrf:
     additionalOrigins:
     - example.org
```

See this [PR](https://github.com/kgateway-dev/kgateway/pull/12516) for more information.

For setup steps, see the [docs](https://agentgateway.dev/docs/kubernetes/latest/security/csrf/). 

#### Path-based API format routing (completions, messages, models, passthrough) 

Agentgateway now supports explicit route typing and path-based routing to agentgateway backends, enabling a single backend to support multiple LLM API formats (OpenAI, Anthropic, models, and passthrough) based on request URL. It introduces a RouteType enum, path-to-type mappings, and supporting translation logic and tests to enable flexible multi-format API handling.

```yaml
apiVersion: agentgateway.dev/v1alpha1
kind: AgentgatewayPolicy
metadata:
 name: agw
 namespace: default
spec:
 targetRefs:
   - kind: HTTPRoute
     name: my-route
     group: gateway.networking.k8s.io
 backend:
   ai:
     routes:
       "/v1/chat/completions": Completions
       "/v1/embeddings": Passthrough
       "/v1/models": Passthrough
       "*": Passthrough
```

See this [PR](https://github.com/kgateway-dev/kgateway/pull/12590) for more information.

For setup steps, see the [docs](https://agentgateway.dev/docs/kubernetes/latest/llm/providers/multiple-endpoints/). 

#### OpenAI Responses API, Anthropic token counting, and Bedrock prompt caching
You can now route traffic for the OpenAI Responses API and Anthropic token-counting endpoints, and configure prompt caching for Amazon Bedrock to improve performance and reduce costs. These enhancements enable significantly faster response times and can reduce LLM-related costs by up to 90% by avoiding repeated prompt processing.

```yaml
apiVersion: agentgateway.dev/v1alpha1
kind: AgentgatewayPolicy
metadata:
 name: bedrock-caching-policy
spec:
 targetRefs:
   - group: gateway.networking.k8s.io
     kind: HTTPRoute
     name: bedrock-route
 backend:
   ai:
     promptCaching:
       cacheSystem: true
       cacheMessages: true
       cacheTools: false
       minTokens: 1024
     modelAliases:
       "fast": "amazon.nova-micro-v1:0"
       "smart": "anthropic.claude-3-5-sonnet-20241022-v2:0"
```
See this [PR](https://github.com/kgateway-dev/kgateway/pull/12855) for more information.

####  Stateful/stateless session routing for MCP backends

You can now configure the MCP session behavior for requests to be `Stateful` or `Stateless` on the AgentgatewayBackend. Behavior defaults to `Stateful` if not set.

```yaml
apiVersion: agentgateway.dev/v1alpha1
kind: AgentgatewayBackend
metadata:
 namespace: default
 name: mcp-static-no-protocol
spec:
 mcp:
   targets:
   - name: default-target
     static:
       host: mcp-server.example.com
       port: 8080
   sessionRouting: Stateless
```

See this [PR](https://github.com/kgateway-dev/kgateway/pull/13201) for more information. 

#### Tracing support

You can now dynamically configure tracing for agentgateway using the AgentgatewayPolicy frontend field:

```yaml
apiVersion: agentgateway.dev/v1alpha1
kind: AgentgatewayPolicy
metadata:
 name: agw
 namespace: default
spec:
 targetRefs:
   - kind: Gateway
     name: gw
     group: gateway.networking.k8s.io
 frontend:
   tracing:
     backendRef:
       name: opentelemetry-collector
       namespace: default
       port: 4317
     protocol: GRPC
     clientSampling: "true"
     randomSampling: "true"
     resources:
       - name: deployment.environment.name
         expression: '"production"'
       - name: service.version
         expression: '"test"'
     attributes:
       add:
         - expression: '"literal"'
           name: custom
         - expression: 'request.headers["x-header-tag"]'
           name: request
```

See this [PR](https://github.com/kgateway-dev/kgateway/pull/13226) for more information on the new changes.

For setup steps, see the [docs](https://agentgateway.dev/docs/kubernetes/latest/observability/tracing/). 

####  CipherSuite configuration via frontend TLS policy

You can now configure the cipher-suites and min and max TLS version on the agentgateway proxy by using the spec.frontend.tls fields in the AgentgatewayPolicy frontend field:

```yaml
apiVersion: agentgateway.dev/v1alpha1
kind: AgentgatewayPolicy
metadata:
 name: tls-policy
 namespace: default
spec:
 targetRefs:
 - kind: Gateway
   name: test
   group: gateway.networking.k8s.io
 frontend:
   tls:
     alpnProtocols:
     - h2
     - http/1.1
     handshakeTimeout: 15s
     minProtocolVersion: "1.2"
     maxProtocolVersion: "1.3"
     cipherSuites:
     - TLS13_AES_256_GCM_SHA384
     - TLS_ECDHE_ECDSA_WITH_AES_256_GCM_SHA384
```

See this [PR](https://github.com/kgateway-dev/kgateway/pull/13219) for more information.


#### Basic auth, api-key auth, and JWT auth

Agentgateway proxies now support basic auth, API key auth and JWT auth. 
See this [PR]](https://github.com/kgateway-dev/kgateway/pull/12886) for more information.

For a JWT setup example, see the [docs](https://agentgateway.dev/docs/kubernetes/latest/security/jwt/setup/). 

### Highlighted Envoy features 

#### API Gateway feature gaps

{{< reuse-image src="img/feature-gap-epic.png"  >}}
{{< reuse-image-dark srcDark="img/feature-gap-epic.png"  >}}

Issue: https://github.com/kgateway-dev/kgateway/issues/12910

One of the most common themes of feedback we received from the v2.1 release is that there were several missing features which can be considered “tablestakes” for API gateways. This feedback was completely valid and we took it to heart, so we gathered the most requested features and made sure to deliver them for the v2.2 release! Huge thanks goes to all that gave us this important feedback on Slack, GitHub, or anywhere else!

##### API key authentication

API key authentication is a common security mechanism for API gateways, allowing clients to authenticate using API keys provided in HTTP headers. API key authentication support has now been added to TrafficPolicies, allowing API keys to be provided via HTTP headers, query parameters, or cookies.

```yaml
apiVersion: gateway.kgateway.dev/v1alpha1
kind: TrafficPolicy
metadata:
 name: api-key-auth-gateway
 namespace: default
spec:
 targetRefs:
   - group: gateway.networking.k8s.io
     kind: Gateway
     name: gw
 apiKeyAuth:
   keySources:
   - header: "api-key"
   forwardCredential: false
   secretRef:
     name: api-keys-secret

```

See the following PRs for more information:
* [12962](https://github.com/kgateway-dev/kgateway/pull/12962)
* [13217](https://github.com/kgateway-dev/kgateway/pull/13217)

##### Basic auth 

TrafficPolicy now provides configuration for HTTP Basic authentication. Basic authentication checks if an incoming request has a valid username and password before routing the request to a backend service.

```yaml
apiVersion: gateway.kgateway.dev/v1alpha1
kind: TrafficPolicy
metadata:
 name: route-basicauth
spec:
 targetRefs:
 - group: gateway.networking.k8s.io
   kind: HTTPRoute
   name: route-secure
 basicAuth:
   users:
     - alice:{SHA}W6ph5Mm5Pz8GgiULbPgzG37mj9g=
     - bob:{SHA}W6ph5Mm5Pz8GgiULbPgzG37mj9g=

```

See this [PR](https://github.com/kgateway-dev/kgateway/pull/12983) for more information.

##### JWT Authentication

You can now configure JWT policies in the TrafficPolicy. To setup your JWT providers, use the GatewayExtension resource. 

See this [PR](https://github.com/kgateway-dev/kgateway/pull/12811) for more information.


##### OAuth2 and OIDC flows

Added capability to protect traffic using OAuth2/OIDC policy when using Envoy as the Gateway proxy.

You can configure kgateway with your OIDC provider's details by creating a GatewayExtension resource to hold the OIDC configuration, a Backend and BackendTLSPolicy to allow kgateway to communicate with the OIDC endpoints, and a Secret for your client secret.

```yaml
apiVersion: gateway.kgateway.dev/v1alpha1
kind: GatewayExtension
metadata:
 name: google-oauth
spec:
 oauth2:
   backendRef:
     kind: Backend
     group: gateway.kgateway.dev
     name: google-oauth
   issuerURI: https://accounts.google.com
   # tokenEndpoint and authorizationEndpoint can be omitted to use OpenID provider config discovery using the issuerURI
   #tokenEndpoint: https://oauth2.googleapis.com/token
   #authorizationEndpoint: https://accounts.google.com/o/oauth2/v2/auth
   credentials:
     # FIXME: replace with your OAuth2 client ID
     clientID: your-client-id
     clientSecretRef:
       name: google-oauth-client-secret
   redirectURI: https://example.com:8443/oauth2/redirect
   logoutPath: /logout
   forwardAccessToken: true
   scopes: ["openid", "email"]
---
apiVersion: gateway.kgateway.dev/v1alpha1
kind: Backend
metadata:
 name: google-oauth
spec:
 type: Static
 static:
   hosts:
   - host: oauth2.googleapis.com
     port: 443
---
apiVersion: gateway.networking.k8s.io/v1
kind: BackendTLSPolicy
metadata:
 name: google-oauth-tls
spec:
 targetRefs:
 - group: gateway.kgateway.dev
   kind: Backend
   name: google-oauth
 validation:
   hostname: oauth2.googleapis.com
   wellKnownCACertificates: System
---
apiVersion: v1
kind: Secret
metadata:
 name: google-oauth-client-secret
data:
 # FIXME: replace with your base64 encoded OAuth2 client secret
 client-secret: Y2xpZW50LXNlY3JldA==
```

See the following PRs for more information:
* [13051](https://github.com/kgateway-dev/kgateway/pull/13051)
* [13099](https://github.com/kgateway-dev/kgateway/pull/13099)


#### ListenerPolicy CRD and ProxyProtocol

Kgateway now exposes config to accept incoming network traffic with Proxy Protocol via the ListenerPolicy resource.

The new ListenerPolicy also supports `preserveExternalRequestId`, `generateRequestId ', so users can now disable the generation of Request ID and preserve the external request ID.

Example fields on the new ListenerPolicy:
```yaml
apiVersion: gateway.kgateway.dev/v1alpha1
kind: ListenerPolicy
metadata:
 name: http-listener-policy-all-fields
 namespace: default
spec:
 targetRefs:
 - group: gateway.networking.k8s.io
   kind: Gateway
   name: gw
 default:
   httpSettings:
     useRemoteAddress: true
     xffNumTrustedHops: 2
     serverHeaderTransformation: AppendIfAbsent
     streamIdleTimeout: 30s
     acceptHttp10: true
     preserveExternalRequestId: true
     generateRequestId: false
     maxRequestHeadersKb: 64
     healthCheck:
       path: "/health_check"

```

See the following PRs for more information:
* [12979](https://github.com/kgateway-dev/kgateway/pull/12979)
* [13250](https://github.com/kgateway-dev/kgateway/pull/13250)
* [13224](https://github.com/kgateway-dev/kgateway/pull/13224)

To learn more about the ListenerPolicy, see the [docs](https://kgateway.dev/docs/envoy/latest/about/policies/listenerpolicy/). To set up Proxy Protocol with a ListenerPolicy, check out this [guide](https://kgateway.dev/docs/envoy/latest/traffic-management/proxy-protocol/). 


#### earlyRequestHeaderModifier to perform header modifications before route selection 

Kgateway now supports sanitizing HTTP headers from an incoming request. This is especially useful for gateways that are handling untrusted downstream traffic.
Before, there were ways to do this with kgateway using a transformation policy or the header modifier feature, but these occur as "standard" filters in an already executing filter chain, they will not guarantee that the headers are removed before any routing or processing decisions are made. Now we support earlyRequestHeaderModifier on the ListenerPolicy:

```yaml
apiVersion: gateway.kgateway.dev/v1alpha1
kind: ListenerPolicy
metadata:
 name: early-header-mutation
spec:
 targetRefs:
 - group: gateway.networking.k8s.io
   kind: Gateway
   name: example-gateway
 default:
   httpSettings:
     earlyRequestHeaderModifier:
       add:
         - name: "x-added-one"
           value: "v1"
         - name: "x-added-two"
           value: "v2"
       set:
         - name: "x-set"
           value: "s1"
       remove:
         - "x-remove"
```


See this [PR](https://github.com/kgateway-dev/kgateway/pull/12992) for more information.

For setup steps, see the [docs](https://kgateway.dev/docs/envoy/latest/traffic-management/header-control/early-request-header-modifier/). 


#### Metrics and logs for Envoy xDS errors 

Kgateway now has a warning log and metric when envoy NACKs. 2 metrics are added. One metric is a total counter, and the other is a gauge for the current state. Both are labeled by (gwname, gw-ns, envoy-resource).

```sh
# TYPE kgateway_envoy_xds_rejects_active gauge
kgateway_envoy_xds_rejects_active{gateway_name="gw",gateway_namespace="default",type_url="envoy.config.route.v3.RouteConfiguration"} 0
# HELP kgateway_envoy_xds_rejects_total Total number of xDS responses rejected by envoy proxy
# TYPE kgateway_envoy_xds_rejects_total counter
kgateway_envoy_xds_rejects_total{gateway_name="gw",gateway_namespace="default",type_url="envoy.config.route.v3.RouteConfiguration"} 1
```

See this [PR](https://github.com/kgateway-dev/kgateway/pull/13003) for more information.


#### Multi-arch image support using upstream Envoy for ARM

{{< reuse-image src="img/arm-builds.png" >}}
{{< reuse-image-dark srcDark="img/arm-builds.png" >}}

After years of waiting, we have finally delivered multi-arch Envoy builds! Thank you for the extreme patience shown by our community users as we navigated several technical challenges to get to this point.

Some historical context is needed to explain how we got to this point. The 1.x version of kgateway, Gloo Edge, had a custom Envoy build which included Gloo-specific filters, notably the filter which enables [our powerful transformation feature](https://kgateway.dev/docs/envoy/latest/traffic-management/transformations/). The build process for this custom Envoy predated the widespread adoption of multi-arch builds in upstream Envoy. It would have taken a very big investment to rework our entire pipeline to modernize the process.

However, thanks to the new Envoy feature [dynamic modules](https://www.envoyproxy.io/docs/envoy/latest/intro/arch_overview/advanced/dynamic_modules), we are able to extract our custom functionality out of the full Envoy build process, enabling us to move away from our legacy Envoy build pipeline. A massive thanks goes to all the upstream Envoy dynamic module contributors! 

Starting in v2.2, kgateway will use a Rust-based dynamic module (rustformation) for the transformation functionality. With that, we were able to use the vanilla Envoy upstream arm64 image and bundle our Rust dynamic module with that in our envoy-wrapper image to support arm64 build. While rustformation will now be used by default, with this being the first version to use the dynamic module, we want to give current users a way to go back to the old C++ base transformation filter, which is possible as the x86 build is still using the envoy-gloo binary.

Please refer to the release note and this [guide](https://github.com/kgateway-dev/kgateway/blob/v2.2.x/docs/guides/transformation.md) to see the major differences. The C++ base transformation is being deprecated and will be completely removed in the next release. The dynamic module development in Envoy is very active, including C++ and Go SDK in the current main development branch. It’s a great way to build and iterate on custom features for Envoy. 

Note: Strict validation is currently not supported for transformation policies with multi-arch builds. ([#13356](https://github.com/kgateway-dev/kgateway/pull/13356))

See the following PRs for more information:
* [13356](https://github.com/kgateway-dev/kgateway/pull/13356)
* [13194](https://github.com/kgateway-dev/kgateway/pull/13194)
* [13319](https://github.com/kgateway-dev/kgateway/pull/13319)


### TLS Listener Improvements 

#### FrontendTLSConfig support

Kgateway and agentgateway now implement the [FrontendTLSConfig](https://gateway-api.sigs.k8s.io/reference/1.4/spec/#frontendtlsconfig). This config allows you to set up a mutual TLS listener on the gateway. 

```yaml
kubectl apply -f- <<EOF
apiVersion: gateway.networking.k8s.io/v1
kind: Gateway
metadata:
  name: mtls
  namespace: kgateway-system
spec:
  gatewayClassName: kgateway
  tls:
    frontend:
      default:
        validation:
          mode: AllowValidOnly
          caCertificateRefs:
            - name: ca-cert
              kind: ConfigMap
              group: ""
  listeners:
  - name: https-8443
    protocol: HTTPS
    port: 8443
    tls:
      mode: Terminate
      certificateRefs:
        - name: https-cert
          kind: Secret
    allowedRoutes:
      namespaces:
        from: All
  - name: https-8444
    protocol: HTTPS
    port: 8444
    tls:
      mode: Terminate
      certificateRefs:
        - name: https-cert
          kind: Secret
    allowedRoutes:
      namespaces:
        from: All
EOF
```

FrontendTLS supports the following configurations:
* **Default (required)**: Create the default client certificate validation configuration for all Gateway listeners that handle HTTPS traffic. For an example, see the [Default configuration for all listeners guide](https://kgateway.dev/docs/envoy/latest/setup/listeners/mtls/#default).
* **perPort (optional)**: Override the default configuration with port-specific configuration. The configuration is applied only to matching ports that handle HTTPS traffic. For all other ports that handle HTTPS traffic, the default configuration continues to apply. For an example, see the [Per port configuration guide](https://kgateway.dev/docs/envoy/latest/setup/listeners/mtls/#perport).

In addition, you can choose between the following validation modes:
* **AllowValidOnly**: A connection between a client and the gateway proxy can only be established if the gateway can validate the client’s TLS certificate successfully. For an example, see the [Default configuration for all listeners guide](https://kgateway.dev/docs/envoy/latest/setup/listeners/mtls/#default).
* **AllowInsecureFallback**: The gateway proxy can establish a TLS connection, even if the client TLS certificate could not be validated successfully. For an example, see the [Per port configuration guide](https://kgateway.dev/docs/envoy/latest/setup/listeners/mtls/#perport).

To support FrontendTLSConfig, the following changes were introduced: 
* Allow multiple `caCertificateRefs`. You can use secrets or configmaps to reference your TLS credentials. See this [PR](https://github.com/kgateway-dev/kgateway/pull/12895) for more information.
* Allow configuring cipher suites, ecdh curves, minimum TLS version, and maximum TLS version using the TLS options map. See this [PR](https://github.com/kgateway-dev/kgateway/pull/12917) for more information.
* Added the `kgateway.dev/verify-certificate-hash` to listener TLS options to allow configuration of validating client certificates. See this [PR](https://github.com/kgateway-dev/kgateway/pull/13064) for more details.
* Added `kgateway.dev/verify-certificate-hash` and `kgateway.dev/verify-subject-alt-names` annotations to limit connections to clients that present certificates with a specific Subject Alt Name and certificate hash. See this [PR](https://github.com/kgateway-dev/kgateway/pull/13064 and https://github.com/kgateway-dev/kgateway/pull/13097) for more details.

For more information, see the following doc guides: 
* [mTLS (Frontend TLS)](https://kgateway.dev/docs/envoy/latest/setup/listeners/mtls/)
* [Additional TLS settings](https://kgateway.dev/docs/envoy/latest/setup/listeners/tls-settings/)


#### TLS termination for TCPRoutes 

You can now terminate TLS connections for TCPRoutes. 

See this [PR](https://github.com/kgateway-dev/kgateway/pull/12906) for more information.

### Ingress Migration

If you’re currently running [Ingress Nginx](https://kubernetes.github.io/ingress-nginx/) to support the Kubernetes Ingress API, [ingress2gateway](https://github.com/kgateway-dev/ingress2gateway) can help you migrate to Gateway API by translating your existing Ingress manifests into Gateway, HTTPRoute, and implementation-specific policy resources. The tool provides coverage for common Ingress Nginx annotations (auth, rate limiting, CORS, session affinity, backend TLS, SSL redirect, and more) and can emit resources tailored for either kgateway (Envoy) or agentgateway. Choose your migration guide to learn more:

* [Kgateway (Envoy) migration guide](https://kgateway.dev/docs/envoy/latest/migrate/)
* [Agentgateway migration guide](https://agentgateway.dev/docs/kubernetes/latest/migrate/)

## Release notes
Check out the full details of the kgateway v2.2 release in our [release notes](https://kgateway.dev/docs/envoy/main/reference/release-notes/).


## Availability
kgateway v2.2  is available for download on [GitHub](https://github.com/kgateway-dev/kgateway).

To get started with kgateway, check out our getting started guides for [kgateway](https://kgateway.dev/docs/envoy/latest/quickstart/) or [agentgateway](https://agentgateway.dev/docs/kubernetes/latest/quickstart/).

## Get Involved
The simplest way to get involved with kgateway is by joining our [Slack](https://kgateway.dev/slack/) and [community meetings](https://github.com/kgateway-dev/community?tab=readme-ov-file#community-meetings).

## Contributors

Thanks to the 40+ contributors who made this release possible:

{{< reuse-image src="img/contributors.png" >}}
{{< reuse-image-dark srcDark="img/contributors.png" >}}


