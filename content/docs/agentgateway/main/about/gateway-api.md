---
title: Gateway API
weight: 20
---

Agentgateway is based on the Kubernetes [Gateway API](https://gateway-api.sigs.k8s.io/).
Gateway API is an official Kubernetes API for defining traffic routing and management.
Along with core functionality, Gateway API provides a rich set of extension points for advanced use cases.
Agentgateway uses these to provide functionality beyond what is provided by the core Kubernetes API.

## Conformance

Unlike other implementations of Gateway API, Agentgateway is the only data plane designed from the ground up for
Kubernetes.
As a result, Agentgateway offers some of the most comprehensive support for the API.

At the time of writing, Agentgateway is the only implementation of Gateway API that passes all conformance tests.

You can learn more about conformance
testing [here](https://gateway-api.sigs.k8s.io/implementations/#conformance-levels).

In addition to supporting all Core and Extended Gateway API features, Gateway API has a number of "experimental"
features that are in development.
Agentgateway has support for many of these:

| Feature                                                                   | GEP                                                       | Status                                  |
|---------------------------------------------------------------------------|-----------------------------------------------------------|-----------------------------------------|
| Client Certificate Validation for TLS terminating at the Gateway Listener | [GEP-91](https://gateway-api.sigs.k8s.io/geps/gep-91)     | ✅ Supported                             |
| HTTP Auth                                                                 | [GEP-1494](https://gateway-api.sigs.k8s.io/geps/gep-1494) | ✅ Supported                             |
| Session Persistence                                                       | [GEP-1619](https://gateway-api.sigs.k8s.io/geps/gep-1619) | ❌ Unsupported                           |
| ListenerSets                                                              | [GEP-1713](https://gateway-api.sigs.k8s.io/geps/gep-1713) | ✅ Supported                             |
| HTTPRoute Retries                                                         | [GEP-1731](https://gateway-api.sigs.k8s.io/geps/gep-1731) | ✅ Supported                             |
| Gateway API Interaction with Multi-Cluster Services                       | [GEP-1748](https://gateway-api.sigs.k8s.io/geps/gep-1748) | ❌ Unsupported                           |
| CORS Filter                                                               | [GEP-1767](https://gateway-api.sigs.k8s.io/geps/gep-1767) | ✅ Supported                             |
| TLS based passthrough Route / TLSRoute                                    | [GEP-2643](https://gateway-api.sigs.k8s.io/geps/gep-2643) | ✅ Supported                             |
| Complete Backend mutual TLS Configuration                                 | [GEP-3155](https://gateway-api.sigs.k8s.io/geps/gep-3155) | ❌ Unsupported (supported via extension) |
| Retry Budgets                                                             | [GEP-3388](https://gateway-api.sigs.k8s.io/geps/gep-3388) | ❌ Unsupported                           |
| Gateway TLS Updates for HTTP/2 Connection Coalescing                      | [GEP-3567](https://gateway-api.sigs.k8s.io/geps/gep-3567) | ✅ Supported                             |

## Extensions

To add functionality that is missing in the core Gateway API, Agentgateway provides a number of extensions.
Some of these add completely novel functionality, such as support for the MCP protocol, while others provide more rich
functionality for existing features.

This section describes the extensions that overlap with the core Gateway API.
For a full list of extensions, reference to the rest of the documentation.

When a feature is implemented in both the core Gateway API and an extension, you'll have the choice to use either API.
If you value the portable/standard core API, and do not require the additional functionality, then using the core API is
suitable.
If you require the additional functionality, or want the ability to expand to use additional functionality in the future
without requiring a migration, using the extensions is recommended.

| Feature                     | Gateway API                                                                                          | Extension                                      | Differences                                                                                                                                              |
|-----------------------------|------------------------------------------------------------------------------------------------------|------------------------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------|
| Originating TLS to backends | [BackendTLSPolicy](https://gateway-api.sigs.k8s.io/api-types/backendtlspolicy/)                      | `AgentgatewayPolicy` `.backend.tls`            | Agentgateway supports Mutual TLS, automatic SNI and SAN validation, ALPN customization, and the ability to (optionally) disable TLS verification         |
| Header manipulation         | [HTTPRoute header modifier](https://gateway-api.sigs.k8s.io/api-types/httproute/#filters-optional)   | `AgentgatewayPolicy` `.traffic.transformation` | Agentgateway supports setting headers based on CEL expressions, rather than just static values                                                           |
| External Authorization      | [HTTPRoute ExternalAuth filter](https://gateway-api.sigs.k8s.io/geps/gep-1494/)                      | `AgentgatewayPolicy` `.traffic.extAuth`        | Agentgateway supports more advanced configuration, such as automatic redirects (to sign-in pages), and more control over request and response processing |
| HTTP Filters                | [Filters inline in HTTPRoute](https://gateway-api.sigs.k8s.io/api-types/httproute/#filters-optional) | `AgentgatewayPolicy` `.traffic`                | Agentgateway allows all policies to be either configured as inline HTTPRoute filters, or as standalone policies attached to objects like Gateway and HTTPRoute, allowing more flexibility and re-use.

## Comparison with other implementations

Gateway API has an overwhelming [number of implementations](https://gateway-api.sigs.k8s.io/implementations/) - over 40 at the time of writing.
If you are in the process of evaluating a Gateway API implementation, we recommend taking into account a few factors:

* Is the implementation up-to-date? The Gateway API website [lists the implementations that are submitting conformance reports for each release](https://gateway-api.sigs.k8s.io/implementations/v1.4/).
  If an implementation isn't listed there, they may be stale; many implementations have not been updated for many years, making them incompatible with the latest API.
* Is the implementation correctly implementing the Gateway API specification for features you use?
  Careful evaluation of each implementation's conformance reports is recommended. Unlike other conformance programs, Gateway API conformance **does not require passing all (or any) tests**, and instead lets implementations skip features.
  This means even basic functionality like HTTP Method matching, request timeouts, etc may not be supported by an implementation, even one submitting "passing" conformance reports.
* Does the implementation behavior well in real world scenarios?
  While conformance reports are useful for evaluating the correctness of an implementation in a simple environment,
  they do not test whether the implementation can scale up to thousands of routes, handle rapidly changing configuration, or gracefully handle changes without downtime.
  We recommend the unofficial [Gateway API Benchmarks](https://github.com/howardjohn/gateway-api-bench) as a starting point for evaluating the behavior of a Gateway API implementation (Agentgateway is featured in [Part 2](https://github.com/howardjohn/gateway-api-bench/blob/main/README-v2.md)!)
