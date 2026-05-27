# OIDC / OAuth2 concepts for kgateway

## 1. Introduction

This page explains how kgateway uses OAuth2/OIDC at the edge and how those flows map to kgateway resources. It is practical guidance for operators who need to secure browser-based login flows, delegate authentication to an IdP, or map identity into upstream services.

Scope
- How the Authorization Code flow appears when kgateway handles OIDC at the proxy
- When JWT validation is a better fit than a full OIDC session
- How `GatewayExtension` and `TrafficPolicy` are used to enable and apply OIDC behavior

This is an overview — provider-specific steps (for example Keycloak) remain in separate provider guides.

## 2. How authentication works in kgateway

Below is the typical Authorization Code flow as it appears when kgateway implements OIDC at the edge.

1. Client request arrives at kgateway
   - An unauthenticated browser request for a protected route is intercepted by kgateway's OAuth2 policy (configured via a `GatewayExtension` and applied with a `TrafficPolicy`).

2. Redirect to IdP authorization endpoint
   - kgateway constructs an authorization request (issuer / authorization endpoint, client_id, redirect_uri, scope, state, and optionally PKCE) and redirects the user to the IdP's login page.

3. User authenticates at the IdP
   - The user performs interactive authentication at the IdP (username/password, MFA, etc.). On success the IdP issues an authorization code and redirects the browser back to the configured `redirect_uri` on kgateway.

4. Token exchange
   - kgateway receives the authorization code at its redirect endpoint and (if configured) performs a server-to-server token exchange with the IdP's token endpoint using the registered client credentials.
   - The IdP returns tokens (ID token, access token, optional refresh token) and metadata (token type, expiry).

5. Session cookies and token storage
   - If configured, kgateway can store tokens in secure cookies (cookie configuration is available in the OAuth2 settings). Cookies should be HttpOnly, use an appropriate SameSite value, and be sent only over TLS in production.
   - Optionally, kgateway can forward the access token to upstreams (`forwardAccessToken`) or expose parsed token payload as dynamic metadata for downstream checks.

6. Subsequent requests
   - On subsequent requests the presence of a valid session cookie or bearer token indicates an authenticated session. If enabled, kgateway validates stored tokens against the IdP's JWKS or via introspection (per your `GatewayExtension` settings).
   - When validation succeeds, kgateway can forward the original bearer token upstream, inject selected claims as headers, or rely on its session cookie to allow the request — behavior depends on the policy configuration.

7. Request forwarded to backend
   - The backend receives requests with the headers or tokens that your `TrafficPolicy`/`GatewayExtension` are configured to provide. Backends should not assume tokens are forwarded unless the policy explicitly enables it.

Notes
- kgateway's OAuth2/OIDC support depends on correct IdP metadata (issuerURI, `.well-known` discovery, JWKS) and accurate client registration. Validation and session behavior follow the gateway's configured policies.
- For machine-to-machine scenarios (no browser), prefer Client Credentials or JWT validation rather than interactive OIDC flows.

## 3. JWT vs OIDC

| Aspect | JWT validation | OIDC (Authorization Code / session) |
|---|---:|---|
| Primary use case | API-to-API authentication (bearer tokens) | Browser-based user authentication and delegated access
| Statefulness | Stateless (token contains claims) | Session cookies or token storage are common (stateful at gateway)
| Token issuance | Token issued by IdP; gateway validates signature and claims | Token issued via authorization code exchange; gateway may manage cookies and refresh
| Refresh support | No built-in refresh: client must obtain new token | Gateway or client can use refresh tokens (if granted) or re-authenticate
| Best for | APIs, microservices, machine clients | Web apps, SPAs (with PKCE), user login scenarios

Note: OIDC commonly issues ID and access tokens that are JWTs; the difference is not only the token format but the flow and session semantics.

## 4. When to use what

- API-only (machine clients): Use JWT validation configured via `GatewayExtension`/`TrafficPolicy`. It keeps the gateway stateless and scales well.
- Browser-based user sessions: Use OIDC (Authorization Code ± PKCE). This supports interactive login, consent, and session cookies.
- Hybrid cases: Use OIDC at the edge to authenticate the user, then pass a short-lived access token to backends. Avoid forwarding long-lived credentials.

Real-world examples
- Single-page application (SPA): Authorization Code + PKCE; kgateway handles redirects and session cookies; backend receives claims via headers or token.
- Backend API consumed by other services: JWT validation with audience checks and JWKS verification.

Avoid using OIDC flows for non-interactive clients where redirects are not possible.

## 5. How kgateway implements this

- `GatewayExtension` (OAuth2 section): holds the IdP configuration (issuerURI, endpoints, client credentials reference, cookie settings, token processing options). This resource tells kgateway where and how to talk to the IdP.
- `TrafficPolicy`: applies an OAuth2 or JWT policy to a specific `Gateway`, `HTTPRoute`, or other target. Use a `TrafficPolicy` to enable redirects, deny-redirect matchers for AJAX clients, or to attach JWT validation to a route.
- Provider role (IdP): the identity provider is authoritative for issuing tokens and JWKS. kgateway relies on IdP discovery endpoints (issuer URI / .well-known/openid-configuration) and the JWKS URI to verify tokens.

Implementation tips
- Use provider discovery (`issuerURI`) when possible to avoid copying endpoints manually. Verify JWKS reachability from the cluster.
- Prefer short cookie lifetimes and secure cookie attributes. Configure `denyRedirect` for AJAX endpoints to avoid unexpected HTML redirects.
- Map only needed claims to headers (`claimsToHeaders`) and avoid forwarding sensitive claims unless the backend requires them.

## 6. Related guides

- JWT validation: ../jwt-validation
- Keycloak integration (provider-specific): ../oauth2/keycloak

---
