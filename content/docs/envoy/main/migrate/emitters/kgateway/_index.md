---
title: "Kgateway"
description: "How ingress-nginx annotations map to Gateway API + kgateway resources"
weight: 30
---

The Kgateway Emitter supports generating **Gateway API** and **kgateway** resources from Ingress manifests using:

- **Provider**: `ingress-nginx`

**Note:** All other providers will be ignored by the emitter.

## Usage

Ingress2gateway reads Ingress resources from a Kubernetes cluster or a file. It will output the equivalent
Gateway API and kgateway-specific resources in a YAML/JSON format to stdout.  The simplest case is to convert
all ingresses from the ingress-nginx provider:

```shell
ingress2gateway print --providers=ingress-nginx --emitter=kgateway
```

The above command will:

1. Read your Kube config file to extract the cluster credentials and the current
   active namespace.
2. Search for ingress-nginx resources in that namespace.
3. Convert them to Gateway-API resources (Currently only Gateways and HTTPRoutes).

## Options

### `print` command

| Flag           | Default Value           | Required | Description                                                  |
| -------------- | ----------------------- | -------- | ------------------------------------------------------------ |
| all-namespaces | False                   | No       | If present, list the requested object(s) across all namespaces. Namespace in the current context is ignored even if specified with --namespace. |
| input-file     |                         | No       | Path to the manifest file. When set, the tool will read ingresses from the file instead of reading from the cluster. Supported files are yaml and json. |
| namespace      |                         | No       | If present, the namespace scope for the invocation.           |
| output         | yaml                    | No       | The output format, either yaml or json.                       |
| providers      |  | Yes       | Comma-separated list of providers (only ingress-nginx is supported in this downstream). |
| emitter      | standard | No       | The emitter to use for generating Gateway API resources (supported values: standard, kgateway). |
| kubeconfig     |                         | No       | The kubeconfig file to use when talking to the cluster. If the flag is not set, a set of standard locations can be searched for an existing kubeconfig file. |

## Conversion of Ingress resources to Gateway API

### Processing Order and Conflicts

Ingress resources will be processed with a defined order to ensure deterministic
generated Gateway API configuration.
This should also determine precedence order of Ingress resources and routes in case
of conflicts.

Ingress resources with the oldest creation timestamp will be sorted first and therefore
given precedence. If creation timestamps are equal, then sorting will be done based
on the namespace/name of the resources. If an Ingress rule conflicts with another
(e.g. same path match but different backends) an error will be reported for the
one that sorted later.

Since the Ingress v1 spec does not itself have a conflict resolution guide, we have
adopted this one. These rules are similar to the [Gateway API conflict resolution
guidelines](https://gateway-api.sigs.k8s.io/concepts/guidelines/#conflicts).

### Ingress resource fields to Gateway API fields

Given a set of Ingress resources, `ingress2gateway` will generate a Gateway with
various HTTP and HTTPS Listeners as well as HTTPRoutes that should represent equivalent
routing rules.

| Ingress Field                   | Gateway API configuration                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         |
| ------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `ingressClassName`              | If configured on an Ingress resource, this value will be translated to `kgateway`.                                                                                                                                                                                                                                                                                                                                                                                                               |
| `defaultBackend`                | If present, this configuration will generate a Gateway Listener with no `hostname` specified as well as a catchall HTTPRoute that references this listener. The backend specified here will be translated to a HTTPRoute `rules[].backendRefs[]` element.                                                                                                                                                                                                                                                                                                                                                         |
| `tls[].hosts`                   | Each host in an IngressTLS will result in a HTTPS Listener on the generated Gateway with the following: `listeners[].hostname` = host as described, `listeners[].port` = `443`, `listeners[].protocol` = `HTTPS`, `listeners[].tls.mode` = `Terminate`                                                                                                                                                                                                                                                                                                                                                            |
| `tls[].secretName`              | The secret specified here will be referenced in the Gateway HTTPS Listeners mentioned above with the field `listeners[].tls.certificateRefs`. Each Listener for each host in an IngressTLS will get this secret.                                                                                                                                                                                                                                                                                                                                                                                                  |
| `rules[].host`                  | If non-empty, each distinct value for this field in the provided Ingress resources will result in a separate Gateway HTTP Listener with matching `listeners[].hostname`. `listeners[].port` will be set to `80` and `listeners[].protocol` set to `HTTPS`. In addition, Ingress rules with the same hostname will generate HTTPRoute rules in a HTTPRoute with `hostnames` containing it as the single element. If empty, similar to the `defaultBackend`, a Gateway Listener with no hostname configuration will be generated (if it doesn't exist) and routing rules will be generated in a catchall HTTPRoute. |
| `rules[].http.paths[].path`     | This field translates to a HTTPRoute `rules[].matches[].path.value` configuration.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                |
| `rules[].http.paths[].pathType` | This field translates to a HTTPRoute `rules[].matches[].path.type` configuration. Ingress `Exact` = HTTPRoute `Exact` match. Ingress `Prefix` = HTTPRoute `PathPrefix` match.                                                                                                                                                                                                                                                                                                                                                                                                                                     |
| `rules[].http.paths[].backend`  | The backend specified here will be translated to a HTTPRoute `rules[].backendRefs[]` element.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     |

## Supported Annotations

### Traffic Behavior

- `nginx.ingress.kubernetes.io/client-body-buffer-size`
- `nginx.ingress.kubernetes.io/proxy-body-size`
- `nginx.ingress.kubernetes.io/enable-cors`
- `nginx.ingress.kubernetes.io/cors-allow-origin`
- `nginx.ingress.kubernetes.io/cors-allow-credentials`
- `nginx.ingress.kubernetes.io/cors-allow-headers`
- `nginx.ingress.kubernetes.io/cors-expose-headers`
- `nginx.ingress.kubernetes.io/cors-allow-methods`
- `nginx.ingress.kubernetes.io/cors-max-age`
- `nginx.ingress.kubernetes.io/limit-rps`
- `nginx.ingress.kubernetes.io/limit-rpm`
- `nginx.ingress.kubernetes.io/limit-burst-multiplier`
- `nginx.ingress.kubernetes.io/proxy-send-timeout`
- `nginx.ingress.kubernetes.io/proxy-read-timeout`
- `nginx.ingress.kubernetes.io/ssl-redirect`: When set to `"true"`, adds a `RequestRedirect` filter to HTTPRoute rules that redirects HTTP to HTTPS with a 301 status code. Note that ingress-nginx redirects with code 308, but that isn't supported by gateway API.
- `nginx.ingress.kubernetes.io/force-ssl-redirect`: When set to `"true"`, adds a `RequestRedirect` filter to HTTPRoute rules that redirects HTTP to HTTPS with a 301 status code. Treated identically to `ssl-redirect`. Note that ingress-nginx redirects with code 308, but that isn't supported by gateway API.
- `nginx.ingress.kubernetes.io/ssl-passthrough`: When set to `"true"`, enables TLS passthrough mode. Converts the Ingress to a `TLSRoute` with a Gateway listener using `protocol: TLS` and `tls.mode: Passthrough`. The HTTPRoute that would normally be created is removed.
- `nginx.ingress.kubernetes.io/use-regex`: When set to `"true"`, indicates that the paths defined on an Ingress should be treated as regular expressions.
  Uses host-group semantics: if any Ingress contributing rules for a given host has `use-regex: "true"`, regex-style path matching is enforced on **all**
  paths for that host (across all contributing Ingresses).
- `nginx.ingress.kubernetes.io/rewrite-target`: Rewrites the request path using regex rewrite semantics.
  Uses host-group semantics: if any Ingress contributing rules for a given host sets `rewrite-target`, regex-style path matching is enforced on **all**
  paths for that host (across all contributing Ingresses), consistent with ingress-nginx behavior.

### Backend Behavior

- `nginx.ingress.kubernetes.io/proxy-connect-timeout`: Sets the timeout for establishing a connection with a proxied server. It should be noted that this timeout
  cannot usually exceed 75 seconds.
- `nginx.ingress.kubernetes.io/load-balance`: Sets the algorithm to use for load balancing to a proxied server. The only supported value is `round_robin`.
- `nginx.ingress.kubernetes.io/affinity`: Enables session affinity (only "cookie" type is supported). Maps to `BackendConfigPolicy.spec.loadBalancer.ringHash.hashPolicies`.
- `nginx.ingress.kubernetes.io/session-cookie-name`: Specifies the name of the cookie used for session affinity. Maps to `BackendConfigPolicy.spec.loadBalancer.ringHash.hashPolicies[].cookie.name`.
- `nginx.ingress.kubernetes.io/session-cookie-path`: Defines the path that will be set on the cookie. Maps to `BackendConfigPolicy.spec.loadBalancer.ringHash.hashPolicies[].cookie.path`.
- **Note (regex-mode constraint):** Ingress NGINX session cookie paths do not support regex. If regex-mode is enabled for a host (via `use-regex: "true"` or
  `rewrite-target`) and cookie affinity is used, `session-cookie-path` must be set; the provider validates this and emits an error if it is missing.
- `nginx.ingress.kubernetes.io/session-cookie-domain`: Sets the Domain attribute of the sticky cookie. **Note:** This annotation is parsed but not currently mapped to kgateway as the Cookie type doesn't support domain.
- `nginx.ingress.kubernetes.io/session-cookie-samesite`: Applies a SameSite attribute to the sticky cookie. Browser accepted values are None, Lax, and Strict. Maps to `BackendConfigPolicy.spec.loadBalancer.ringHash.hashPolicies[].cookie.sameSite`.
- `nginx.ingress.kubernetes.io/session-cookie-expires`: Sets the TTL/expiration time for the cookie. Maps to `BackendConfigPolicy.spec.loadBalancer.ringHash.hashPolicies[].cookie.ttl`.
- `nginx.ingress.kubernetes.io/session-cookie-max-age`: Sets the TTL/expiration time for the cookie (takes precedence over `session-cookie-expires`). Maps to `BackendConfigPolicy.spec.loadBalancer.ringHash.hashPolicies[].cookie.ttl`.
- `nginx.ingress.kubernetes.io/session-cookie-secure`: Sets the Secure flag on the cookie. Maps to `BackendConfigPolicy.spec.loadBalancer.ringHash.hashPolicies[].cookie.secure`.
- `nginx.ingress.kubernetes.io/service-upstream`: When set to `"true"`, configures Kgateway to route to the Service’s cluster IP (or equivalent static host) instead of individual Pod IPs. For each covered Service, the emitter creates a `Backend` resource with `spec.type: Static` and rewrites the corresponding `HTTPRoute.spec.rules[].backendRefs[]` to reference that `Backend` (group `gateway.kgateway.dev`, kind `Backend`).
- `nginx.ingress.kubernetes.io/backend-protocol`: Indicates the L7 protocol that is used to communicate with the proxied backend.
  - **Supported values (mapped):** `GRPC`, `GRPCS`
    - If `service-upstream: "true"` is also set for the same Service backend, the emitter sets `spec.static.appProtocol: grpc` on the generated `Backend`.
    - Otherwise, the emitter does **not** create or modify Kubernetes `Service` resources. Instead, it emits an **INFO** notification with a `kubectl patch`
      command to update the existing Service port with `appProtocol: grpc`.
  - **Values treated as default HTTP/1.x (no-op):** `HTTP`, `HTTPS`, `AUTO_HTTP`
  - **Unsupported values (rejected by provider):** `FCGI` (and others)
  - **Safety note:** Because emitting Service manifests could overwrite user-managed Service configuration, ingress2gateway intentionally avoids generating
    Service resources for this annotation.

### External Auth

- `nginx.ingress.kubernetes.io/auth-url`: Specifies the URL of an external authentication service.
- `nginx.ingress.kubernetes.io/auth-response-headers`: Comma-separated list of headers to pass to backend once authentication request completes.

### Basic Auth

- `nginx.ingress.kubernetes.io/auth-type`: Must be set to `"basic"` to enable basic authentication. Maps to `TrafficPolicy.spec.basicAuth`.
- `nginx.ingress.kubernetes.io/auth-secret`: Specifies the secret containing basic auth credentials in `namespace/name` format (or just `name` if in the same namespace). Maps to `TrafficPolicy.spec.basicAuth.secretRef.name`.
- `nginx.ingress.kubernetes.io/auth-secret-type`: **Only `"auth-file"` is supported** (default). The secret must contain an htpasswd file in the key `"auth"`. Only SHA hashed passwords are supported. Maps to `TrafficPolicy.spec.basicAuth.secretRef.key` set to `"auth"`.

### Backend TLS

- `nginx.ingress.kubernetes.io/proxy-ssl-secret`: Maps to `BackendConfigPolicy.spec.tls.secretRef`
- `nginx.ingress.kubernetes.io/proxy-ssl-verify`: Maps to `BackendConfigPolicy.spec.tls.insecureSkipVerify` (inverted: `"on"` = `false`, `"off"` = `true`)
- `nginx.ingress.kubernetes.io/proxy-ssl-name`: Maps to `BackendConfigPolicy.spec.tls.sni` (automatically enables SNI)

### Access Logging

- `nginx.ingress.kubernetes.io/enable-access-log`: If enabled, will create an HTTPListenerPolicy that will configure a basic policy for envoy access logging. Maps to `HTTPListenerPolicy.spec.accessLog[].fileSink`. This can be further customized as needed, see [docs](https://kgateway.dev/docs/envoy/2.0.x/security/access-logging/).

### Regex Path Matching and Rewrites

- `use-regex` and `rewrite-target` may **mutate HTTPRoute path matching** for a host:
  - When regex-mode is enabled for a host, the emitter converts **all** `PathPrefix`/`Exact` matches under that host to `RegularExpression` matches.
  - For Ingresses that set `use-regex: "true"`, their contributed path strings are treated as **regex** (not escaped as literals).
  - For other Ingresses under the same host (that did not set `use-regex: "true"`), their contributed path strings are treated as **literals** within a regex
    match (escaped), to preserve the original non-regex intent.

- `rewrite-target` generates `TrafficPolicy` URL rewrite:
  - For each rule covered by an Ingress that sets `rewrite-target`, the emitter creates a **per-rule TrafficPolicy** named:
    - `<ingress-name>-rewrite-<rule-index>`
  - That policy sets:

    ```yaml
    spec:
      urlRewrite:
        pathRegex:
          pattern: <regex pattern derived from the HTTPRoute rule match>
          substitution: <rewrite-target value>
    ```

  - The policy is attached via `ExtensionRef` filters to only the covered backendRefs (partial coverage), rather than using `targetRefs`.

## TrafficPolicy Projection

Annotations in the **Traffic Behavior** category are converted into
`TrafficPolicy` resources.

These policies are attached using:

- `targetRefs` when the policy applies to all backends, or
- `extensionRef` backend filters for partial coverage.

Examples:

- Body size annotations control `spec.buffer.maxRequestSize`
- Rate limit annotations control `spec.rateLimit.local.tokenBucket`
- Timeout annotations control `spec.timeouts.request` or `streamIdle`
- SSL redirect annotations add `RequestRedirect` filters to HTTPRoute rules
- SSL passthrough annotation converts HTTPRoute to TLSRoute with TLS passthrough Gateway listener

## BackendConfigPolicy Projection

Annotations in the **Backend Behavior** category are converted into
`BackendConfigPolicy` resources.

Currently supported:

- `proxy-connect-timeout`: Maps to `BackendConfigPolicy.spec.connectTimeout`
- Session affinity annotations: Maps to `BackendConfigPolicy.spec.loadBalancer.ringHash.hashPolicies` with cookie-based hash policy

If multiple Ingresses target the same Service with conflicting `proxy-connect-timeout` values,
the lowest timeout wins and a warning is emitted.

## TLSRoute Projection

Annotations that require TLS passthrough mode are converted into `TLSRoute` resources instead of `HTTPRoute` resources.

Currently supported:

- `nginx.ingress.kubernetes.io/ssl-passthrough`:
  - When enabled, the Ingress is converted to a `TLSRoute` resource
  - A Gateway listener is created with `protocol: TLS` and `tls.mode: Passthrough`
  - The listener uses port 443 (when hostname is specified) or 8443 (default)
  - The HTTPRoute that would normally be created is removed
  - Backend services must handle TLS termination themselves

## Backend Projection

Annotations that change how upstreams are represented (rather than how they are load balanced or configured)
can be projected into Kgateway `Backend` resources.

Currently supported:

- `nginx.ingress.kubernetes.io/service-upstream`:
  - For each Service backend covered by an Ingress with `service-upstream: "true"`, the emitter creates a `Backend` with:
    - `spec.type: Static`
    - `spec.static.hosts` containing a single `{host, port}` entry derived from the Service (e.g. `myservice.default.svc.cluster.local:80`).
  - Matching `HTTPRoute.spec.rules[].backendRefs[]` are rewritten to reference this `Backend` instead of the core Service.
- `nginx.ingress.kubernetes.io/backend-protocol`:
  - When set to `GRPC` or `GRPCS` **and** `service-upstream: "true"` is set for the same backend, the emitter stamps `spec.static.appProtocol: grpc` on the generated `Backend`.
  - When set to `GRPC` or `GRPCS` **without** `service-upstream: "true"`, the emitter emits an **INFO** notification that includes a `kubectl patch service ...`
    command to set `spec.ports[].appProtocol` on the existing Service.
  - `HTTP`, `HTTPS`, and `AUTO_HTTP` are treated as default HTTP/1.x behavior and do not emit additional config.

### Summary of Policy Types

| Annotation Type                    | Kgateway Resource     |
|------------------------------------|-----------------------|
| Request/response behavior          | `TrafficPolicy`       |
| Upstream connection behavior       | `BackendConfigPolicy` |
| Upstream representation.           | `Backend`             |
| TLS passthrough                    | `TLSRoute`            |

## Limitations

- Only the **ingress-nginx provider** is currently supported by the Kgateway emitter.
- Some NGINX behaviors cannot be reproduced exactly due to Envoy/Kgateway differences.
- Regex-mode is implemented by converting HTTPRoute path matches to `RegularExpression`. Some ingress-nginx details (such as case-insensitive `~*` behavior)
  may not be reproduced exactly depending on the underlying Gateway API/Envoy behavior and the patterns provided.

## Supported but not tranlated Annotations

The following annotations have equivalents in kgateway but are not (as of yet) translated by this tool.

`nginx.ingress.kubernetes.io/auth-proxy-set-headers`

Supported in TrafficPolicy

```yaml
spec:
  extAuth:
    httpService:
      authorizationRequest:
        headersToAdd:
        - key: x-forwarded-host
          value: "%DOWNSTREAM_REMOTE_ADDRESS%"
```
