---
title: "Ingress NGINX"
description: "How ingress-nginx annotations map to Gateway API + kgateway resources"
weight: 30
---

The `ingress-nginx` provider defines the source resources to be translated, e.g. an Ingress resource with Ingress NGINX-specific annotations.

**Note:** Some annotations may be translated into kgateway resources or user-facing notifications.

## Supported Annotations

The `ingress-nginx` provider currently supports an Ingress with the following annotations.

### Canary / Traffic Shaping

- `nginx.ingress.kubernetes.io/canary`: If set to `true`, enables weighted backends.

- `nginx.ingress.kubernetes.io/canary-by-header`: Specifies the header name used to generate an HTTPHeaderMatch.

- `nginx.ingress.kubernetes.io/canary-by-header-value`: Specifies the exact header value to match.

- `nginx.ingress.kubernetes.io/canary-by-header-pattern`: Specifies a regex pattern used in the header match.

- `nginx.ingress.kubernetes.io/canary-weight`: Specifies the backend weight for traffic shifting.

- `nginx.ingress.kubernetes.io/canary-weight-total`: Defines the total weight used when calculating backend percentages.

---

### Request / Body Size

- `nginx.ingress.kubernetes.io/client-body-buffer-size`: Sets the maximum request body size when `proxy-body-size` is not present. For kgateway, this maps to `TrafficPolicy.spec.buffer.maxRequestSize`.

- **Note (regex-mode constraint):** Ingress NGINX session cookie paths do not support regex. If regex-mode is enabled for a host (via `use-regex: "true"` or
  `rewrite-target`) and cookie affinity is used, `session-cookie-path` must be set; the provider validates this and emits an error if it is missing.

- `nginx.ingress.kubernetes.io/proxy-body-size`: Sets the maximum allowed request body size. Takes precedence over `client-body-buffer-size`. For kgateway, this maps to `TrafficPolicy.spec.buffer.maxRequestSize`.

---

### CORS

- `nginx.ingress.kubernetes.io/enable-cors`: Enables CORS policy generation. When set to "true", enables CORS handling for the Ingress.
  Maps to creation of a TrafficPolicy with `spec.cors` populated.
- `nginx.ingress.kubernetes.io/cors-allow-origin`: Comma-separated list of origins (e.g. "https://example.com, https://another.com").
  For kgateway, this maps to `TrafficPolicy.spec.cors.allowOrigins`.
- `nginx.ingress.kubernetes.io/cors-allow-credentials`: Controls whether credentials are allowed in cross-origin requests ("true" / "false").
  For kgateway, this maps to `TrafficPolicy.spec.cors.allowCredentials`.
- `nginx.ingress.kubernetes.io/cors-allow-headers`: A comma-separated list of allowed request headers. For kgateway,
  this maps to `TrafficPolicy.spec.cors.allowHeaders`.
- `nginx.ingress.kubernetes.io/cors-expose-headers`: A comma-separated list of HTTP response headers that can be exposed to client-side
  scripts in response to a cross-origin request. For kgateway, this maps to `TrafficPolicy.spec.cors.exposeHeaders`.
- `nginx.ingress.kubernetes.io/cors-allow-methods`: A comma-separated list of allowed HTTP methods (e.g. "GET, POST, OPTIONS").
  For kgateway, this maps to `TrafficPolicy.spec.cors.allowMethods`.
- `nginx.ingress.kubernetes.io/cors-max-age`: Controls how long preflight responses may be cached (in seconds). For the kgateway
  implementation, this maps to `TrafficPolicy.spec.cors.maxAge`.

### Rate Limiting

- `nginx.ingress.kubernetes.io/limit-rps`: Requests per second limit.  For kgateway, this maps to `TrafficPolicy.spec.rateLimit.local.tokenBucket`.

- `nginx.ingress.kubernetes.io/limit-rpm`: Requests per minute limit. For kgateway, this maps to `TrafficPolicy.spec.rateLimit.local.tokenBucket`.

- `nginx.ingress.kubernetes.io/limit-burst-multiplier`: Burst multiplier for rate limiting. Used to compute `maxTokens`.

---

### Timeouts

- `nginx.ingress.kubernetes.io/proxy-send-timeout`: Controls the request timeout. For kgateway, this maps to `TrafficPolicy.spec.timeouts.request`.

- `nginx.ingress.kubernetes.io/proxy-read-timeout`: Controls stream idle timeout. For kgateway, this maps to `TrafficPolicy.spec.timeouts.streamIdle`.

---

### External Auth

- `nginx.ingress.kubernetes.io/auth-url`: Specifies the URL of an external authentication service. For kgateway, this maps to `GatewayExtension.spec.extAuth.httpService`.
- `nginx.ingress.kubernetes.io/auth-response-headers`: Comma-separated list of headers to pass to backend once authentication request completes. For kgateway, this maps to `GatewayExtension.spec.extAuth.httpService.authorizationResponse.headersToBackend`.

### Basic Auth

- `nginx.ingress.kubernetes.io/auth-type`: Must be set to `"basic"` to enable basic authentication. For kgateway, this maps to `TrafficPolicy.spec.basicAuth`.
- `nginx.ingress.kubernetes.io/auth-secret`: Specifies the secret containing basic auth credentials in `namespace/name` format (or just `name` if in the same namespace). For kgateway, this maps to `TrafficPolicy.spec.basicAuth.secretRef.name`.
- `nginx.ingress.kubernetes.io/auth-secret-type`: **Only `"auth-file"` is supported** (default). The secret must contain an htpasswd file in the key `"auth"`. Only SHA hashed passwords are supported. For kgateway, this maps to `TrafficPolicy.spec.basicAuth.secretRef.key` set to `"auth"`.

---

### Backend Protocol

- `nginx.ingress.kubernetes.io/backend-protocol`: Indicates the L7 protocol that is used to communicate with the proxied backend.
  - **Supported values (recorded):** `GRPC`, `GRPCS`
    - The provider records protocol intent as policy metadata (used by implementation emitters).
    - For kgateway:
      - If `service-upstream: "true"` is also enabled for the same Service backend, the kgateway emitter stamps `spec.static.appProtocol: grpc`
        on the generated `Backend`.
      - Otherwise, the kgateway emitter does **not** generate Kubernetes `Service` resources. Instead, it emits an **INFO** notification with a `kubectl patch`
        command to set `spec.ports[].appProtocol` on the existing Service.
  - **Values treated as default HTTP/1.x (no-op):** `HTTP`, `HTTPS`, `AUTO_HTTP`
  - **Unsupported values (rejected):** `FCGI` (and others)
  - **Safety note:** The provider does not attempt to create or mutate Kubernetes Services; implementation emitters decide how to safely project this intent.

---

### Backend (Upstream) Configuration

- `nginx.ingress.kubernetes.io/proxy-connect-timeout`: Controls the upstream connection timeout. For kgateway,
  this maps to `BackendConfigPolicy.spec.connectTimeout`.
- `nginx.ingress.kubernetes.io/load-balance`: Sets the algorithm to use for load balancing. The only supported value is `round_robin`.
  For kgateway, this maps to `BackendConfigPolicy.spec.loadBalancer`.

**Note:** For kgateway, if multiple Ingress resources reference the same Service with different `proxy-connect-timeout` values, ingress2gateway emits warnings because Kgateway cannot safely apply multiple conflicting `BackendConfigPolicy` resources to the same Service.

---

### Backend TLS

- `nginx.ingress.kubernetes.io/proxy-ssl-secret`: Specifies a Secret containing client certificate (`tls.crt`), client key (`tls.key`), and optionally CA certificate (`ca.crt`) in PEM format. The secret name can be specified as `secretName` (same namespace) or `namespace/secretName`. For kgateway, this maps to `BackendConfigPolicy.spec.tls.secretRef`. **Note:** The secret must be in the same namespace as the BackendConfigPolicy.

- `nginx.ingress.kubernetes.io/proxy-ssl-verify`: Enables or disables verification of the proxied HTTPS server certificate. Values: `"on"` or `"off"` (default: `"off"`). For kgateway, this maps to `BackendConfigPolicy.spec.tls.insecureSkipVerify` (inverted: `"on"` = `false`, `"off"` = `true`).

- `nginx.ingress.kubernetes.io/proxy-ssl-name`: Overrides the server name used to verify the certificate of the proxied HTTPS server. This value is also passed through SNI (Server Name Indication) when establishing a connection. For kgateway, this maps to `BackendConfigPolicy.spec.tls.sni`. Setting this value automatically enables SNI.

- `nginx.ingress.kubernetes.io/proxy-ssl-server-name`: **Note:** This annotation is not handled separately. In Kgateway, SNI is automatically enabled when `proxy-ssl-name` is set.

**Note:** For kgateway, backend TLS configuration is applied via `BackendConfigPolicy` resources. If multiple Ingress resources reference the same Service with different backend TLS settings, ingress2gateway creates a single `BackendConfigPolicy` per Service, and conflicting settings may result in warnings.

---

### Session Affinity

- `nginx.ingress.kubernetes.io/affinity`: Enables and sets the affinity type in all Upstreams of an Ingress. The only affinity type available for NGINX is "cookie". For kgateway, this maps to `BackendConfigPolicy.spec.loadBalancer.ringHash.hashPolicies` with cookie-based hash policy.

- `nginx.ingress.kubernetes.io/session-cookie-name`: Defines the name of the cookie used for session affinity. For kgateway, this maps to `BackendConfigPolicy.spec.loadBalancer.ringHash.hashPolicies[].cookie.name`.

- `nginx.ingress.kubernetes.io/session-cookie-path`: Defines the path that is set on the cookie. For kgateway, this maps to `BackendConfigPolicy.spec.loadBalancer.ringHash.hashPolicies[].cookie.path`.

- `nginx.ingress.kubernetes.io/session-cookie-domain`: Sets the Domain attribute of the sticky cookie. **Note:** This annotation is parsed but not currently mapped to kgateway as the Cookie type doesn't support domain.

- `nginx.ingress.kubernetes.io/session-cookie-samesite`: Applies a SameSite attribute to the sticky cookie. Browser accepted values are None, Lax, and Strict. For kgateway, this maps to `BackendConfigPolicy.spec.loadBalancer.ringHash.hashPolicies[].cookie.sameSite`.

- `nginx.ingress.kubernetes.io/session-cookie-expires`: Sets the TTL/expiration time for the cookie. For kgateway, this maps to `BackendConfigPolicy.spec.loadBalancer.ringHash.hashPolicies[].cookie.ttl`.

- `nginx.ingress.kubernetes.io/session-cookie-max-age`: Sets the TTL/expiration time for the cookie. Takes precedence over `session-cookie-expires` if both are specified. For kgateway, this maps to `BackendConfigPolicy.spec.loadBalancer.ringHash.hashPolicies[].cookie.ttl`.

- `nginx.ingress.kubernetes.io/session-cookie-secure`: Sets the Secure flag on the cookie. For kgateway, this maps to `BackendConfigPolicy.spec.loadBalancer.ringHash.hashPolicies[].cookie.secure`.

---

### SSL Redirect

- `nginx.ingress.kubernetes.io/ssl-redirect`: When set to `"true"`, enables SSL redirect for HTTP requests. For kgateway, this maps to a `RequestRedirect` filter on HTTPRoute rules that redirects HTTP to HTTPS with a 301 status code. Note that ingress-nginx redirects with code 308, but that isn't supported by gateway API. 

- `nginx.ingress.kubernetes.io/force-ssl-redirect`: When set to `"true"`, enables SSL redirect for HTTP requests. This annotation is treated exactly the same as `ssl-redirect`. For kgateway, this maps to a `RequestRedirect` filter on HTTPRoute rules that redirects HTTP to HTTPS with a 301 status code. Note that ingress-nginx redirects with code 308, but that isn't supported by gateway API. 

**Note:** Both annotations are supported and treated identically. If either annotation is set to `"true"` (case-insensitive), SSL redirect is enabled. The redirect filter is added at the rule level in the HTTPRoute, redirecting all HTTP traffic to HTTPS.

---

### Regex Path Matching and Rewrites

- `nginx.ingress.kubernetes.io/use-regex`: When set to `"true"`, indicates that the paths defined on that Ingress should be treated as regular expressions.
  Uses host-group semantics: if any Ingress contributing rules for a given host has `use-regex: "true"`, regex-style path matching is enforced on **all**
  paths for that host (across all contributing Ingresses).

- `nginx.ingress.kubernetes.io/rewrite-target`: Rewrites the request path using regex rewrite semantics.
  Uses host-group semantics: if any Ingress contributing rules for a given host sets `rewrite-target`, regex-style path matching is enforced on **all**
  paths for that host (across all contributing Ingresses), consistent with ingress-nginx behavior.

For kgateway:

- When regex-mode is enabled for a host (via `use-regex: "true"` or `rewrite-target`), the emitter converts `PathPrefix` / `Exact` matches under that host
  to `RegularExpression` matches.
- For Ingresses that set `use-regex: "true"`, their contributed path strings are treated as **regex** (not escaped as literals).
- For other Ingresses under the same host (that did not set `use-regex: "true"`), their contributed path strings are treated as **literals** within a regex
  match (escaped), to preserve the original non-regex intent.
- `rewrite-target` generates `TrafficPolicy` URL rewrites using `spec.urlRewrite.pathRegex` and is attached via `ExtensionRef` filters (partial coverage).

---

## Provider Limitations

- Currently, kgateway is the only supported emitter.
- Some NGINX behaviors cannot be reproduced exactly due to differences between NGINX and semantics of other proxy implementations.
- Regex-mode is implemented by converting HTTPRoute path matches to `RegularExpression`. Some ingress-nginx details (such as case-insensitive `~*` behavior)
  may not be reproduced exactly depending on the underlying Gateway API / Envoy behavior and the patterns provided.

If you rely on annotations not listed above, please open an [issue](https://github.com/kgateway-dev/ingress2gateway/issues) or be prepared to apply
post-migration manual adjustments.
