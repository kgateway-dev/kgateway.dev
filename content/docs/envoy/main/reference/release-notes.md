---
title: Release notes
weight: 100
---

Review the release notes for kgateway. For a detailed list of changes between tags, use the [GitHub Compare changes tool](https://github.com/kgateway-dev/kgateway/compare/).

## v2.3.0

<!-- TODO release 2.2 
For more details, review the [GitHub release notes](https://github.com/kgateway-dev/kgateway/releases/tag/v2.2.0).-->

### 🔥 Breaking changes {#v22-breaking-changes}


### 🌟 New features {#v22-new-features}

#### Control plane changes

- **Common labels**: Add custom labels to all resources that are created by the Helm charts by using the `commonLabels` field, including the Deployment, Service, and ServiceAccount of the control plane. This allows you to better organize your resources or integrate with external tools. For more information, see [Common labels]({{< link-hextra path="/install/advanced/#common-labels" >}}).
- **PriorityClass support**: Assign a PriorityClassName to control plane pods using the `controller.priorityClassName` Helm field. [Priority](https://kubernetes.io/docs/concepts/scheduling-eviction/pod-priority-preemption/) indicates the importance of a pod relative to other pods and allows higher priority pods to preempt lower priority ones when scheduling.
- **Topology spread constraints**: Distribute kgateway controller pods across failure domains such as zones or nodes by using the `topologySpreadConstraints` Helm field. For more information, see [Topology spread constraints]({{< link-hextra path="/install/advanced/#topology-spread-constraints" >}}).
- The default `app.kubernetes.io/component: controller` label is added to the controller deployment. Similarly, the `app.kubernetes.io/component: proxy` is added to all gateway proxies. 

#### Static IPs for Gateways

Assign a static IP address to the Kubernetes service that exposes your Gateway using the `spec.addresses` field with `type: IPAddress`.

For more information, see [Static IP address]({{< link-hextra path="/setup/gateway/#static-ip-address" >}}). 

#### Local rate limit filter options {#v23-local-rate-limit-filter-options}

The {{< reuse "docs/snippets/trafficpolicy.md" >}} resource now supports the `percentEnabled` and `percentEnforced` optional fields to control the percentage of requests for which the local rate limit filter is enabled or enforced. If not set, both fields default to `100`, which enables and enforces the local rate limiting filter for 100% of all requests.

Use these fields for gradual rollouts or to run the filter in shadow mode (`percentEnabled: 100`, `percentEnforced: 0`), where rate limiting statistics are collected without blocking any requests.

For more information, see [Gradual rollout and shadow mode]({{< link-hextra path="/security/ratelimit/local/#gradual-rollout" >}}).


#### Envoy application log format {#v23-envoy-log-format}

Configure how Envoy formats its application logs by using the `logFormat` field in the GatewayParameters resource. You can choose between structured JSON or text output. This setting controls the Envoy application log format only and does not affect access logs.

For more information, see [Change proxy settings]({{< link-hextra path="/setup/customize/gateway/#built-in" >}}).

#### Gateway proxy customization with overlays {#v23-gateway-customization}

The GatewayParameters resource now supports gateway proxy customization via overlay fields. Overlays use strategic merge patch (SMP) semantics to apply advanced customizations to the Kubernetes resources that are generated for gateway proxies, including the Service, ServiceAccount, and Deployment. 

The following overlays are supported: 

* Use `deploymentOverlay`, `serviceOverlay`, and `serviceAccountOverlay` to patch the generated Deployment, Service, and ServiceAccount.
* Use `horizontalPodAutoscaler`, `verticalPodAutoscaler`, and `podDisruptionBudget` to automatically create and configure these resources targeting the proxy Deployment.

For more information, see [Change proxy settings]({{< link-hextra path="/setup/customize/gateway/" >}}) and [Overlay examples]({{< link-hextra path="/setup/customize/configs/" >}}).

#### Additional Envoy container arguments {#envoy-extra-args}

Use `spec.kube.envoyContainer.extraArgs` to pass additional Envoy CLI arguments to the managed proxy container. User-supplied arguments are appended after the default built-in Envoy arguments.

The following example sets a custom base ID and enables CPU set threading:

```yaml
kubectl apply --server-side -f- <<'EOF'
apiVersion: {{< reuse "docs/snippets/trafficpolicy-apiversion.md" >}}
kind: {{< reuse "docs/snippets/gatewayparameters.md" >}}
metadata:
  name: gw-params
  namespace: {{< reuse "docs/snippets/namespace.md" >}}
spec:
  kube:
    envoyContainer:
      extraArgs:
        - --base-id
        - "7"
        - --cpuset-threads
EOF
```

#### Upstream proxy protocol {#v23-upstream-proxy-protocol}

The `BackendConfigPolicy` resource now supports an `upstreamProxyProtocol` field. When configured, the gateway proxy prepends a PROXY protocol header to outbound TCP connections to the upstream backend, allowing the backend to see the original client IP address and port. Both PROXY protocol `V1` (human-readable) and `V2` (binary) are supported.

For more information, see [Outbound proxy protocol]({{< link-hextra path="/traffic-management/proxy-protocol/#outbound" >}}).

#### Allow requests without proxy protocol {#v23-proxy-protocol-allow-without-header}

The ListenerPolicy proxy protocol configuration now supports an `allowRequestsWithoutProxyProtocol` field. When set to `true`, a single listener accepts connections with or without a PROXY protocol header. By default, the field is set to `false` and the listener strictly requires a PROXY protocol header on all incoming connections.

For more information, see [Allow connections without proxy protocol headers]({{< link-hextra path="/traffic-management/proxy-protocol/#allow-without-proxy-protocol" >}}).

#### Circuit breaker remaining capacity metrics {#v23-circuit-breaker-track-remaining}

The `BackendConfigPolicy` circuit breakers configuration now supports a `trackRemaining` field. When set to `true`, Envoy emits gauge metrics for the remaining capacity of each circuit breaker threshold group: `remaining_cx`, `remaining_pending`, `remaining_rq`, and `remaining_retries`. Note that enabling this field has a small performance overhead.

For more information, see [Track remaining capacity]({{< link-hextra path="/resiliency/circuit-breakers/#track-remaining" >}}).

#### IP-based access control (ACL) {#v23-acl}

The {{< reuse "docs/snippets/trafficpolicy.md" >}} resource now supports an `acl` field for IP-based access control. You can define allow and deny rules by using CIDR blocks or bare IP addresses, set a `defaultAction` for unmatched requests, and customize denial responses with a custom HTTP status code and headers. 

For more information, see [IP-based access control (ACL)]({{< link-hextra path="/security/acl/" >}}).

#### Fault injection {#v23-fault-injection}

The {{< reuse "docs/snippets/trafficpolicy.md" >}} resource now supports a `faultInjection` field for chaos engineering and resiliency testing. You can inject the following fault types into a percentage of requests:

- **Delays**: Inject a fixed latency before forwarding the request upstream to simulate slow networks or overloaded backends.
- **Aborts**: Return an HTTP or gRPC error code without forwarding the request to simulate upstream failures.
- **Response rate limiting**: Throttle the response body data rate to simulate degraded upstream connections.

Fault injection can be applied at the route level by targeting an HTTPRoute, or at the gateway level by targeting a Gateway. A route-level policy can use `disable: {}` to opt out of a gateway-level fault injection policy.

For more information, see [Fault injection]({{< link-hextra path="/resiliency/fault-injection/" >}}).

#### OpenTelemetry tracing {#v23-otel-tracing}

Configure distributed tracing for your gateway by using the ListenerPolicy resource, and override tracing settings per route with a `TrafficPolicy` resource.

The following tracing improvements are included in this release:

- **Listener-level tracing**: Configure the OTel provider, sampling rates (`clientSampling`, `randomSampling`, `overallSampling`), and custom span attributes in a ListenerPolicy that targets your Gateway.
- **Per-route tracing overrides**: Use a TrafficPolicy that targets an HTTPRoute or GRPCRoute to override sampling rates, add route-specific span attributes, or disable tracing for specific routes.
- **Auto-populated resource attributes**: [OTel semantic convention](https://opentelemetry.io/docs/specs/semconv/resource/) resource attributes are automatically added to all spans, including `service.name`, `service.namespace`, `service.instance.id`, `service.version`, and Kubernetes identity attributes such as `k8s.pod.name`, `k8s.node.name`, and `k8s.deployment.name`.

For more information, see [Tracing]({{< link-hextra path="/observability/tracing/" >}}).

#### Dynamic direct response bodies {#v23-direct-response-body-format}

The DirectResponse resource now supports a `bodyFormat` field for returning dynamic response bodies by using [Envoy format strings](https://www.envoyproxy.io/docs/envoy/latest/api-v3/config/core/v3/substitution_format_string.proto). Format strings use `%VARIABLE%` placeholders that Envoy substitutes at request time, such as request headers or dynamic metadata. You can choose between returning a text or JSON body. Both formats are mutually exclusive. 

For more information, see [Dynamic text body]({{< link-hextra path="/traffic-management/direct-response/#dynamic-text-body" >}}) and [Dynamic JSON body]({{< link-hextra path="/traffic-management/direct-response/#dynamic-json-body" >}}).

#### GRPCRoute support {#v23-grpcroute}

Route traffic to gRPC services by using the GRPCRoute resource for protocol-aware routing. Unlike the HTTPRoute, which requires matching on HTTP paths and methods, the GRPCRoute allows you to define routing rules by using gRPC-native concepts, such as service and method names.

For more information, see [gRPC routing]({{< link-hextra path="/traffic-management/grpc/" >}}).

#### TLS termination for TLSRoutes and TCPRoutes {#v23-tls-terminate}

Terminate TLS traffic at the gateway by using a TLS listener in `Terminate` mode with either a TLSRoute or a TCPRoute. The gateway decrypts incoming TLS traffic using a server-side certificate and forwards the plain traffic to the backend service via TCP proxy.

- **TLSRoute**: Supports SNI-based hostname matching. Use this when you need to route traffic to different backends based on the requested hostname.
- **TCPRoute**: Routes traffic based on listener port only, without SNI hostname matching. Use this listener for simpler port-based routing.

For more information, see [TLS termination for TLSRoutes]({{< link-hextra path="/setup/listeners/tls-termination/" >}}) and [TLS termination for TCPRoutes]({{< link-hextra path="/setup/listeners/tls-termination-tcproute/" >}}).

<!-- TODO release 2.2

### ⚒️ Installation changes {#v2.2-installation-changes}

### 🔄 Feature changes {#v2.2-feature-changes}

### 🗑️ Deprecated or removed features {#v2.2-removed-features}

### 🚧 Known issues {#v2.2-known-issues}
-->
