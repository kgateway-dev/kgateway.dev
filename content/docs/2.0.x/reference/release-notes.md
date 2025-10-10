---
title: Release notes
weight: 100
---

Review the release notes for kgateway. For a detailed list of changes between tags, use the [GitHub Compare changes tool](https://github.com/kgateway-dev/kgateway/compare/).

## v2.0.0 {#v200}

**Kgateway version 2.0.0** is the first official release of the project following its donation to the [Cloud Native Computing Foundation (CNCF)](https://www.cncf.io/). The donation marks a new chapter for the codebase, which was originally developed as the Gloo project by Solo.io. The 2.0 release introduces foundational changes to the Gloo project that lay the groundwork for a vibrant, open-source ecosystem built around the [Kubernetes Gateway API](https://gateway-api.sigs.k8s.io/).

### Why 2.0 was needed {#why}

The previous open-source Gloo project supported a hybrid model, offering both custom Gloo APIs (such as VirtualServices and Upstreams) as well as Gateway API-based extensions. This dual model created challenges in terms of maintainability, user experience, and community alignment.

The 2.0 release is a clean break from the legacy Gloo API surface:

- **Vendor-neutral APIs:** All `solo.io`-specific API groups have been renamed to `kgateway.dev`.
- **CRD Refactors:** Significant API renaming and refactoring was completed:
  - Upstream backend and policy configuration were decoupled into a new Backend resource. Policy is now configured via Gateway API or policy-specific resources.
  - Policy `*Option` resources such as `HTTPListenerOption` and `RouteOption` were redesigned to follow the Gateway API policy attachment pattern. As such, these resources are now `HTTPListenerPolicy` and `TrafficPolicy`.
  - Removal of fields and behaviors only applicable to the enterprise edition
- **CRD Cleanup:** Removed legacy CRDs such as `Proxy`, `Settings`, and deprecated or enterprise-only field names.

These changes ensure that kgateway is a **standards-first** and **community-owned** project moving forward.

### Key Features {#features}

Besides the versioned API changes, kgateway offers a host of features designed to make it easy to extend and customize your implementation of the Gateway API.

#### 🚀 Kgateway custom resources {#kgateway-crs}

Kgateway introduces powerful, standards-aligned extensions via custom resources that follow the Gateway API’s policy attachment pattern. Key new resources include:

* [Backend](/docs/reference/api/#backend): Define routable backends such as AI providers (OpenAI, Azure, Gemini, and more), AWS Lambda functions, or static server for use by Gateways.
* [DirectResponse](/docs/reference/api/#directresponse): Enable Gateways to directly return immediate HTTP responses, specifying custom status codes and optional response content without contacting backend services.
* [GatewayExtension](/docs/reference/api/#gatewayextension): Add external authorization (ExtAuth) and external request processing (ExtProc) via gRPC services, extending the Gateway's request handling capabilities.
* [GatewayParameter](/docs/reference/api/#gatewayparameter): Provide detailed customization of Gateway deployments, including container images, logging, resource allocations, Istio integrations, sidecar configurations, and AI-related extensions.
* [HTTPListenerPolicy](/docs/reference/api/#httplistenerpolicy): Set policies for HTTP listeners, including advanced access logging.
* [TrafficPolicy](/docs/reference/api/#trafficpolicy): Implement advanced traffic rules such as AI prompt manipulation, local rate limiting, request/response transformations, and external processing control for managing traffic through gateways.

#### 🚦 Traffic management {#traffic}

Kgateway gives you sophisticated traffic-handling policies, including:

* **TrafficPolicy** for request transformation and enforcement of security policy such as external authorization and local rate limiting.
* **External processing (ExtProc)** to modify HTTP requests and responses with an external gRPC processing server.
* **Route delegation** to manage route and policy configuration in multi-tenant environments.

For more information, see the [Traffic management docs](/docs/traffic-management/).

#### 🔐 Secure traffic {#security}

Kgateway provides a comprehensive set of security features, as well as the ability for you to bring your own external authorization service.

* **TLS support** for a variety of use cases including mTLS with Istio, TLS passthrough, and Backend TLS.
* **Local rate limiting** as a first line of defense to control the rate of requests to your Gateway.
* **External authorization** to protect requests that go through your Gateway by using an external service.

For more information, see the [Security docs](/docs/security/).

#### 🤖 AI Gateway (open sourced) {#ai-gateway}

Enterprise-grade **AI gateway functionality** has been open sourced for the first time, including the following highlights:

* Support for multiple LLM providers such as OpenAI, Anthropic, Gemini, and more
* Model failover within an LLM provider
* Function calling
* Prompt enrichment and prompt guarding
* AI-specific metrics
* [Gateway API Inference Extension project](https://gateway-api-inference-extension.sigs.k8s.io/guides/) support for routing to local LLM workloads

For more information, see the [AI Gateway docs](/docs/ai/).

#### 🧠 KRT-based control plane {#control-plane}

Kgateway uses a **brand new control plane** architecture built on the [Kubernetes Declarative Controller Runtime (`krt`)](https://github.com/istio/istio/blob/master/pkg/kube/krt/README.md). Benefits include:

- Improved controller performance and scalability
- Cleaner reconciliation and modular plugin framework
- Scalability to massive clusters with tens of thousands of routes

For more information, see the [Architecture docs](/docs/about/architecture/).

#### 🐬 Ambient waypoint integration {#ambient-waypoint}

Kgateway introduces support for using its Gateway implementation as an **Istio ambient mesh waypoint proxy**:

- Drop-in replacement for the stock `istio` GatewayClass
- Just update your `Gateway` CR to reference `gateway.kgateway.dev` class
- Provides kgateway L7 features inside the mesh

This way, you get full L7 policy control over **east-west traffic** while using Gateway API semantics. For more information, see the [Ambient docs](/docs/integrations/istio/ambient/).

### 🔥 Breaking changes from Gloo v1 {#changes}

Kgateway v2 has extensive API changes from Gloo v1, which include the following.

- **CRD group renames:** All CRDs now use the `kgateway.dev` API group
- **CRD renames and field removals** to ensure clean, vendor-neutral APIs
- **Control plane** updated to `kgateway-system`
- **Default Envoy proxy deployment renamed** to remove the `gloo-proxy-` prefix
- **Gateway ports** default to `80` and `443` to match the Kubernetes Ingress convention, instead of `8080` and `8443`
- **Removed Gloo Edge API mode**
- **Removed Gloo-specific tooling** such as the `glooctl` CLI

### Feedback and next steps {#next}

We’re excited to collaborate with the community to continue shaping the future of API gateways! 

* [Get started](/docs/quickstart/) with kgateway 2.0.
* Check out the [Community repo](https://github.com/kgateway-dev/community) for more about contributing to kgateway.
* Let us know how it goes in the [CNCF `#kgateway` Slack](https://cloud-native.slack.com/archives/C080D3PJMS4)!
