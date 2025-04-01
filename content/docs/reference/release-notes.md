---
title: Release notes
weight: 10
---

Review the release notes for {{< reuse "docs/snippets/product-name.md" >}}. For a detailed list of changes between tags, use the [GitHub Compare changes tool](https://github.com/kgateway-dev/kgateway/compare/).

## v2.0.0

**{{< reuse "docs/snippets/product-name-caps.md" >}} version 2.0.0** is the first official release of the project following its donation to the [Cloud Native Computing Foundation (CNCF)](https://www.cncf.io/). The donation marks a new chapter for the codebase, which was originally developed as the Gloo project by Solo.io. The 2.0 release introduces foundational changes to the Gloo project that lay the groundwork for a vibrant, open-source ecosystem built around the [Kubernetes Gateway API](https://gateway-api.sigs.k8s.io/).

### Why 2.0 was needed {#why}

The previous open-source Gloo Gateway project supported a hybrid model, offering both custom Gloo APIs (such as VirtualServices and Upstreams)as well as Gateway API-based extensions. This dual model created challenges in terms of maintainability, user experience, and community alignment.

The 2.0 release is a clean break from the legacy Gloo API surface:

- **Vendor-neutral APIs:** All `solo.io`-specific API groups have been renamed to `kgateway.dev`.
- **CRD Refactors:** Significant API renaming and refactoring was completed:
  - Upstream backend and policy configuration were decoupled into a new Backend resource. Policy is now configured via Gateway API or policy-specific resources.
  - Policy `*Option` resources such as `HTTPListenerOption` and `RouteOption` were redesigned to follow the Gateway API policy attachment pattern. As such, these resources are now `HTTPListenerPolicy` and `TrafficPolicy`.
  - Removal of fields and behaviors only applicable to the enterprise edition
- **CRD Cleanup:** Removed legacy CRDs such as `Proxy`, `Settings`, and deprecated or enterprise-only field names.

These changes ensure that kgateway is a **standards-first** and **community-owned** project moving forward.

### Key Features

Besides the versioned API changes, {{< reuse "docs/snippets/product-name.md" >}} offers a host of features designed to make it easy to extend and customize your implementation of the Gateway API.

#### 🚀 Gateway API Extensions

kgateway introduces powerful, standards-aligned extensions via custom resources that follow the Gateway API’s policy attachment pattern. Key new resources include:

- **TrafficPolicy** – advanced request/response transformations, retries, timeouts, and more
- **HTTPListenerPolicy** – fine-grained configuration of L7 behavior at the listener level
- **DirectResponse** – configure routes to return custom HTTP responses
- **RateLimitPolicy** – local rate limiting for Gateway and Route traffic
- **AccessLogPolicy** – customizable access logging format and output

#### Traffic management

* Ext processing
* Route delegation

#### 🔐 Secure traffic

* Rate limiting
* External authorization

#### 🤖 AI Gateway (open sourced)

Enterprise-grade AI gateway functionality has been open sourced for the first time, including the following highlights:

* Support for multiple LLM providers such as OpenAI, Anthropic, Gemini, and more
* Model failover within an LLM provider
* Function calling
* Prompt enrichment and prompt guarding
* AI-specific metrics
* [Gateway API Inference Extension project](https://gateway-api-inference-extension.sigs.k8s.io/guides/) support for routing to local LLM workloads

For more information, see the [AI Gateway docs](/docs/ai/).

#### 🧠 KRT-based control plane

{{< reuse "docs/snippets/product-name-caps.md" >}} uses a brand new control plane architecture built on the [Kubernetes Runtime Toolkit (KRT)](https://github.com/kubernetes-sigs/kubebuilder). Benefits include:

- Improved controller performance and scalability
- Cleaner reconciliation and modular plugin framework
- Scalability to massive clusters with tens of thousands of routes

#### 🕸 Ambient waypoint integration

{{< reuse "docs/snippets/product-name-caps.md" >}} introduces support for using its Gateway implementation as an **Istio ambient mesh waypoint proxy**:

- Drop-in replacement for the stock `istio` GatewayClass
- Just update your `Gateway` CR to reference `gateway.kgateway.dev` class
- Provides all {{< reuse "docs/snippets/product-name.md" >}} L7 features (auth, rate limiting, transformations) inside the mesh

This way, you get full L7 policy control over **east-west traffic** while using Gateway API semantics.

### ⚠️ Breaking changes

Because of the extensive API changes, {{< reuse "docs/snippets/product-name.md" >}} 2.0 requires a fresh installation instead of an upgrade from a previous Gloo v1.x release.

- **CRD group renames:** All CRDs now use the `kgateway.dev` API group
- **CRD renames and field removals** to ensure clean, vendor-neutral APIs
- **Control plane** updated to `{{< reuse "docs/snippets/ns-system.md" >}}`
- **Default Envoy proxy deployment renamed** to remove the `gloo-proxy-` prefix
- **Removed Gloo Edge API mode**
- **Removed Gloo-specific tooling** such as the `glooctl` CLI

### Feedback and next steps {#next}

We’re excited to collaborate with the community to continue shaping the future of API gateways. [Get started](/docs/quickstart/) with {{< reuse "docs/snippets/product-name.md" >}} 2.0 and [let us know how it goes in the CNCF `#kgateway` Slack](https://cloud-native.slack.com/archives/C080D3PJMS4)!

## Earlier v1 releases

Refer to the [Gloo Gateway documentation](https://docs.solo.io/gloo-edge/latest/reference/changelog/open_source/) and [`gloo` project](https://github.com/solo-io/gloo).
