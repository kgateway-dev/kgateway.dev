Agentgateway is based on the [Kubernetes Gateway API](https://gateway-api.sigs.k8s.io/).
Gateway API is an official Kubernetes project that focuses on managing L4 and L7 traffic routing in Kubernetes environments.
Along with core functionality, Gateway API provides a rich set of extension points for advanced use cases.
Agentgateway uses these extension points to provide functionality beyond what is provided by the core Kubernetes API.

## Conformance

Unlike other implementations of Gateway API, agentgateway is the only data plane designed from the ground up for
Kubernetes.
As a result, agentgateway offers some of the most comprehensive support for the Gateway API.

You can review the confornace test results by version in the [Gateway API docs](https://gateway-api.sigs.k8s.io/implementations/#conformance-levels). For example, as of the time of this writing, agentgateway is the only implementation of Gateway API that passes all conformance tests for Gateway API v1.3. 

In addition to supporting all Core and Extended Gateway API features, Gateway API has a number of "experimental"
features that are in development.
Agentgateway supports many of these experimental features, as shown in the following table.

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

To add functionality that is missing in the core Gateway API, agentgateway provides a number of extensions.
Some of these add completely novel functionality, such as support for the MCP protocol, while others provide more rich
functionality for existing features.

This section describes the extensions that overlap with the core Gateway API.
For a full list of extensions, refer to the rest of the documentation.

When a feature is implemented in both the core Gateway API and an extension, you have the choice to use either API.
- If you value building on the portable standard and do not require the additional functionality, then use the core Gateway API.
- If you require the additional functionality, or want the ability to expand to use additional functionality in the future without requiring a migration, then use the agentgateway extension.

| Feature                     | Gateway API                                                                                          | Agentgateway extension                         | Differences                                                                                                                                              |
|-----------------------------|------------------------------------------------------------------------------------------------------|------------------------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------|
| Originating TLS to backends | [BackendTLSPolicy](https://gateway-api.sigs.k8s.io/api-types/backendtlspolicy/)                      | `AgentgatewayPolicy` `.backend.tls`            | Agentgateway supports mutual TLS (mTLS), automatic SNI and SAN validation, ALPN customization, and the ability to (optionally) disable TLS verification. |
| Header manipulation         | [HTTPRoute header modifier](https://gateway-api.sigs.k8s.io/api-types/httproute/#filters-optional)   | `AgentgatewayPolicy` `.traffic.transformation` | Agentgateway supports setting headers based on CEL expressions, rather than just static values. |
| External Authorization      | [HTTPRoute ExternalAuth filter](https://gateway-api.sigs.k8s.io/geps/gep-1494/)                      | `AgentgatewayPolicy` `.traffic.extAuth`        | Agentgateway supports more advanced configuration, such as automatic redirects (to sign-in pages), and more control over request and response processing. |
| HTTP Filters                | [Filters inline in HTTPRoute](https://gateway-api.sigs.k8s.io/api-types/httproute/#filters-optional) | `AgentgatewayPolicy` `.traffic`                | Agentgateway allows all policies to be either configured as inline HTTPRoute filters, or as standalone policies attached to objects like Gateway and HTTPRoute, allowing more flexibility and re-use. |

## Comparison with other implementations {#implementations}

The Kubernetes Gateway API has more than 40 [implementations](https://gateway-api.sigs.k8s.io/implementations/) at the time of this writing.
If you are in the process of evaluating a Gateway API implementation, consider the following factors:



**Conformance level**: Is the implementation up to date? The Gateway API docs [set three levels of conformance](https://gateway-api.sigs.k8s.io/implementations/#conformance-levels), depending on the level of commitment to the Gateway API by version.
- Prefer conformant implementations that pass tests for the past two releases of the Gateway API, such as kgateway with agentgateway.
- Review the release version-specific conformance reports. If an implementation is not listed, then it might be stale. Many implementations have not been updated for years, making them incompatible with the latest API.
- Confirm that the implementation is generally available. Some implementations might be in beta or alpha, and not yet ready for production use.

**Feature coverage**: Is the implementation correctly implementing the Gateway API specification for features that you use?
- Evaluate each implementation's conformance report for the version that you want to use. Unlike other conformance programs, Gateway API conformance **does not require passing all (or any) tests**, and instead lets implementations skip features.
- Confirm that basic functionality like HTTP Method matching, request timeouts, and so forth are supported by thge implementation. Remember that because implementations can skip features, even a "passing" conformance report does not indicate basic functionality.

**Real-world performance**: Does the implementation behave well in real world scenarios?
- Consider that the conformance reports evaluate the correctness of an implementation in a simple environment. They do not test whether the implementation can scale up to thousands of routes, handle rapidly changing configuration, or gracefully handle changes without downtime.
- Review the unofficial [Gateway API Benchmarks](https://github.com/howardjohn/gateway-api-bench) as a starting point for evaluating the behavior of a Gateway API implementation. Agentgateway is featured in [Part 2](https://github.com/howardjohn/gateway-api-bench/blob/main/README-v2.md)!
