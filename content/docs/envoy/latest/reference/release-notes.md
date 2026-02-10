---
title: Release notes
weight: 100
---

Review the release notes for kgateway. For a detailed list of changes between tags, use the [GitHub Compare changes tool](https://github.com/kgateway-dev/kgateway/compare/).

## v2.2.0 {#v220}

For more details, review the [GitHub release notes](https://github.com/kgateway-dev/kgateway/releases/tag/v2.2.0).

### 🔥 Breaking changes {#v22-breaking-changes}

#### Dedicated agentgateway APIs and installation {#agentgateway-apis}

Version 2.2 introduces major breaking changes for agentgateway implementation. Agentgateway now has:
* New dedicated APIs in the `agentgateway.dev` API group
* New `AgentgatewayPolicy` to replace `TrafficPolicy` for agentgateway configurations
* New `AgentgatewayParameters` API in `agentgateway.dev/v1alpha1`
* Split Helm installation with dedicated charts for Envoy-based kgateway and agentgateway


Key changes include:
* Policies are now configured through `AgentgatewayPolicy` instead of `TrafficPolicy.`
* `DirectResponse` for agentgateway is now only configurable through `AgentgatewayPolicy` instead of the separate `DirectResponse` CRD.
* Agentgateway can no longer be configured with `GatewayParameters`, only with `AgentgatewayParameters`.
* The controller name changed from `kgateway.dev/agentgateway` to `agentgateway.dev/agentgateway`.
* `AgentgatewayParameters` `rawConfig` breaking change to allow configuring `binds` and other settings in `config.yaml` outside of its `config` section.
* The default namespace for agentgateway is now `agentgateway-system` instead of `kgateway-system`.

The documentation for agentgateway has also been moved to the [agentgateway.dev](https://agentgateway.dev/docs/kubernetes/latest/) website.

#### Feature gate for experimental Gateway API features {#experimental-feature-gate}

Kgateway 2.2 introduces the `KGW_ENABLE_EXPERIMENTAL_GATEWAY_API_FEATURES` environment variable to gate experimental Gateway API features and APIs. This setting defaults to `false` and must be explicitly enabled to use experimental features such as TCPRoute and TLSRoute.

To enable these features, set the environment variable in your kgateway controller deployment in your Helm values file.

```yaml
controller:
  extraEnv:
    KGW_ENABLE_EXPERIMENTAL_GATEWAY_API_FEATURES: "true"
```

If you are currently using any experimental Gateway API features, you must enable this setting before upgrading to kgateway 2.2, or those features will stop working.

#### GatewayParameters breaking changes {#gatewayparameters-changes}

Several fields have been removed or changed in the `GatewayParameters` CRD:

* The deprecated `spec.kube.floatingUserId` field was removed. When migrating, use the `spec.kube.omitDefaultSecurityContext` field instead. When set to true, this field prevents the controller from injecting opinionated default security contexts, allowing your platform (for example, OCP) to dynamically provide the appropriate security contexts.
* The `spec.kube.aiExtension` field was removed. To use AI capabilities, migrate to the agentgateway data plane.
* The `agentgateway` fields were deprecated in `GatewayParameters`. Use `AgentgatewayParameters` instead.

#### JWT policy renamed {#jwt-policy-rename}

In the `TrafficPolicy` API:
* The `jwt` field is renamed to `jwtAuth`
* The `apiKeyAuthentication` field is renamed to `apiKeyAuth`

Update your TrafficPolicy resources accordingly when upgrading.

#### JWT missing token behavior {#jwt-missing-token}

An option was added to allow missing JWT tokens. Review your JWT authentication policies to ensure they have the desired behavior for missing tokens.

#### ExtAuth fail closed for agentgateway {#extauth-fail-closed}

Agentgateway ExtAuth policies now fail closed when the `backendRef` to the auth server is invalid. Previously, invalid backend references might have allowed requests through. Update your ExtAuth policies to ensure backend references are valid before upgrading.

#### AI policy removed from TrafficPolicy {#ai-policy-removed}

AI policy configuration was removed from the `TrafficPolicy` API. To use AI capabilities, use an [agentgateway proxy](https://agentgateway.dev/docs/kubernetes/latest/setup/) with the `AgentgatewayPolicy` API instead.

### 🌟 New features {#v22-new-features}

#### Agentgateway enhancements {#v22-agentgateway-features}

Agentgateway received significant enhancements in version 2.2:

**Performance improvements**: The agentgateway control plane was refactored, improving performance by up to 25x.

**Model aliases**: Added `modelAliases` support to `AgentgatewayPolicy` to allow friendly model name aliases for your AI backends.

**Provider support**: 
* Added support for Azure OpenAI backends
* Added support for multiple AI backend route types including OpenAI Responses API, Anthropic token counting, and prompt caching configuration for Bedrock (enabling up to 90% cost reduction)

**Authentication and security**:
* CSRF support
* MCP authentication for agentgateway
* Basic auth, API key auth, and inline JWT auth policies
* ExtAuth with HTTP support and configurable timeout

**Advanced features**:
* Multi-network support for cross-network workload discovery and routing in ambient mode
* Stateful/stateless session routing configuration for MCP backends
* Canadian Social Insurance Number prompt guards
* Tracing support

**Infrastructure**:
* Event reporting for agentgateway gateways that indicates when a gateway has NACKed an update
* Multi-arch controller image support
* `Gateway.spec.addresses` support for configuring load balancer IP addresses
* `PodDisruptionBudget` and `HorizontalPodAutoscaler` options via `AgentgatewayParameters`

#### Gateway API and routing enhancements {#v22-gateway-api}

**Multiple certificate references**: Added support for multiple `certificateRefs` in the listener `tls` section, allowing you to serve multiple certificates from a single listener.

**Gateway infrastructure metadata**: The kgateway `GatewayClass` now supports labels and annotations in the Gateway API infrastructure field. When a Gateway specifies infrastructure labels or annotations, these values propagate to all managed Kubernetes resources including the Deployment, Service, ConfigMap, and ServiceAccount. Infrastructure values take precedence over `GatewayParameters` values when the same key is defined in both locations.

**Custom GatewayClasses**: You can now define GatewayClasses using any controller. For example, create a custom GatewayClass with an arbitrary name that uses `controllerName: kgateway.dev/agentgateway` to duplicate the behavior of the built-in GatewayClass. This enables scenarios like two different teams wanting different `GatewayParameters` for the same class, or clean GitOps with entirely new resources without patching.

**Gateway addresses**: Support for `Gateway.spec.addresses` to configure one IP address that is used in the gateway's Service `loadBalancerIP`.

**Regex path rewrite**: Added regex path rewrite capabilities for more advanced routing scenarios.

**Automatic port detection**: Kgateway now detects the port for listeners without a defined port, selecting 80 for HTTP and 443 for HTTPS. Other protocols do not support automatic port detection.

#### Security and authentication {#v22-security}

**JWT authentication**: 
* Added JWT authentication configuration to `TrafficPolicy` with support for JWT providers via `GatewayExtension`
* Support for remote JWKS (JSON Web Key Set) with configurable TLS options
* Global disable option for JWT policies
* Allow missing JWT token configuration

**API key authentication**: Added support for configuring API key authentication in `TrafficPolicy` with keys defined in secrets. Routes can selectively opt out of gateway-level authentication requirements using the `disable` field.

**Basic authentication**: Added basic auth configuration to `TrafficPolicy`.

**OAuth2**: Added OAuth2 policy to enable OAuth2 and OIDC flows with Envoy as the gateway, with customizable cookie settings and the ability to deny redirects for matching requests.

**Frontend TLS configuration**: Implemented `FrontendTLSConfig` with implementation-specific details:
* Allow multiple `caCertificateRefs`
* Allow `caCertificateRefs` to reference secrets and configmaps
* Added `kgateway.dev/verify-certificate-hash` to listener TLS options for validating client certificates
* Added `kgateway.dev/verify-subject-alt-names` TLS option
* Support for secret reference kind for `caCertificateRefs` in `BackendTLSPolicy`

**Cipher suite and TLS configuration**: Configure cipher suites, ECDH curves, minimum TLS version, and maximum TLS version using TLS options. Configure ALPN protocols using the `kgateway.dev/alpn-protocols` TLS option.

**TLS for TCPRoutes**: Added support for TLS termination for TCPRoutes.

#### Resiliency and traffic management {#v22-resiliency}

**Circuit breakers**: Added support for circuit breakers in `BackendConfigPolicy` to prevent cascading failures.

**Compression**: Added support for gzip response compression and request decompression in `TrafficPolicy`.

**Per-connection buffer limit**: Added `PerConnectionBufferLimit` to `ListenerPolicy`. The annotation on Gateway resources is now deprecated in favor of this field.

**Request header modification**: Added `earlyRequestHeaderModifier` to `HTTPListenerPolicy`, allowing header modifications before a route is selected.

**Retry policy for GatewayExtension**: Added retry policy to configure retries for the gRPC streams associated with `GatewayExtension` services.

**Stats matcher configuration**: Added stats matcher config to `GatewayParameters` for controlling which Envoy statistics are collected.

**HTTP request settings**: Added `preserveExternalRequestId` and `generateRequestId` to `HttpListenerPolicy` and `ListenerPolicy`. You can now disable the generation of request IDs and preserve external request IDs.

**Mirror filters**: Fixed HTTPRoute mirror filters to support multiple mirrors per rule and correct percentage-based mirroring. Previously, percentage values were off by 100x (for example, 50% mirrored only 0.5% of traffic).

**Max request headers**: Added `maxRequestHeadersKb` field in `ListenerPolicy` to control the maximum size of request headers.

#### ListenerPolicy and proxy protocol {#v22-listener-policy}

Added a `ListenerPolicy` CRD with ProxyProtocol configuration. The `HTTPListenerPolicy` is now deprecated in favor of using the `httpSettings` under `ListenerPolicy`.

#### Rustformation transformation engine {#v22-rustformation}

Kgateway 2.2 switches to rustformation as the default transformation engine. Rustformation provides:
* Parsing body as JSON
* All documented Jinja custom functions
* Case-insensitive header lookups
* Improved performance with native Envoy per-route config

Note: Strict validation is currently not supported for transformation policies with multi-arch builds.

#### Gateway customization {#v22-gateway-customization}

**Priority class name**: Added `priorityClassName` to the Pod struct in `GatewayParameters` to set the corresponding `priorityClassName` field in the gateway-proxy pod.

**Custom GatewayParameters**: Added Helm values for setting custom `GatewayParameters` for bundled GatewayClasses.

**Control plane resilience**: `PodDisruptionBudget` is now an option for the agentgateway and Envoy control planes.

#### Observability {#v22-observability}

**Metrics and logs for xDS errors**: Added metrics and logs for Envoy xDS errors to help troubleshoot configuration issues.

**Reference grants enforcement**: Enforced `ReferenceGrants` for cross-namespace Secret references used by XListenerSets, improving security and visibility.

#### Multi-architecture support {#v22-multi-arch}

Added multi-arch support for kgateway with Envoy using upstream Envoy for ARM. Note that strict validation is currently not supported for transformation policies with multi-arch builds.

### 🗑️ Deprecated or removed features {#v22-removed-features}

**HTTPListenerPolicy deprecated**: `HTTPListenerPolicy` is now deprecated. Use the `httpSettings` under `ListenerPolicy` instead.

**AI Gateway and Inference Extension removed**: Support for `InferencePool` and AI backends with the `kgateway` class, which was deprecated in v2.1, was removed. Support is available with the `agentgateway` class.

**Per-connection buffer limit annotation**: The `PerConnectionBufferLimit` annotation on Gateway resources is deprecated in favor of the `ListenerPolicy` field.

**Waypoint integration removed**: The waypoint integration for Envoy-based gateway proxies was removed.
