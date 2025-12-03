{{< reuse "docs/snippets/agentgateway/about.md" >}}

Agentgateway supports many agent connectivity use cases, including the following:

* Agent-to-agent (A2A)
* Model Context Protocol (MCP)
* REST APIs as agent-native tools
* AI routing to cloud and local large language models (LLMs)
* Support for the Gateway API Inference Extension project

## Architecture

For more information about how kgateway integrates with agentgateway, see the [Architecture](../../about/architecture/) topic.

For more information about agentgateway resources, see the [Agentgateway upstream docs](https://agentgateway.dev/docs/about/).

## Agentgateway resource configuration {#resources}

Review the following table to understand how to configure agentgateway resources in {{< reuse "/docs/snippets/kgateway.md" >}}.

| Agentgateway resource | Description | Configured in {{< reuse "/docs/snippets/kgateway.md" >}} by |
| -- | -- | -- |
| Bind | The set of port bindings that associate gateway listeners with specific network ports. The bind has a unique key in the format `port/namespace/name`, such as `8080/default/my-gateway` with the value being the port number, such as `8080`. | Created automatically based on the Gateway and each unique port across Gateway listeners or ListenerSets. |
| Port | The port to listen on. Each port has a set of listeners that in turn have their own routes with policies and backends. | Ports in a Gateway or ListenerSet. |
| Listener | Listener configuration for how agentgateway accepts and processes incoming requests. <ul><li>Unique key for the listener</li><li>Name that maps to the section name from the Gateway listener</li><li>Bind key of the bind that the listener is part of</li><li>Gateway name</li><li>Hostname that the listener accepts traffic for</li><li>Protocol (HTTP, HTTPS, TCP, TLS)</li><li>TLS configuration details such as certificates and termination modes</li></ul> Listeners can each have their own set of routes with policies and backends. | Listeners in a Gateway or ListenerSet. |
| Route | Routing rules for how agentgateway routes incoming requests to the appropriate backend.<ul><li>Unique key in the format: `namespace.name.rule.match`</li><li>Route name in the format: `namespace/name`</li><li>Listener key of the listener that the route is part of</li><li>Rule name from the source route</li><li>Traffic matching criteria (path, headers, method, query params) that are derived from the Gateway API routing resources</li><li>Filters that transform request and responses, such as header modification, redirects, rewrites, mirroring, and other policies</li><li>Target backend services with load balancing and health checking</li><li>Hostnames that the route serves traffic for</li></ul> | Routing resources such as HTTPRoute, GRPCRoute, TCPRoute, and TLSRoute. |
| Backend | The backing destination where traffic is routed. Unlike other resources, backends are global resources (not per-gateway) that are applied to all Gateways that use agentgateway. Each backend has a unique name in the format: `namespace/name`. Backend types include AI for model-specific LLM provider configuration, static host or IP addresses, and virtual MCP servers, including A2A use cases. | Services and Backends. |
| Target | The details of the backend, such as the tools in an MCP backend. | Services and Backends. |
| Policies | Policies for how agentgateway processes incoming requests.<ul><li>Request Header Modifier: Add, set, or remove HTTP request headers.</li><li>Response Header Modifier: Add, set, or remove HTTP response headers.</li><li>Request Redirect: Redirect incoming requests to a different scheme, authority, path, or status code.</li><li>URL Rewrite: Rewrite the authority or path of requests before forwarding.</li><li>Request Mirror: Mirror a percentage of requests to an additional backend for testing or analysis.</li><li>CORS: Configure Cross-Origin Resource Sharing (CORS) settings for allowed origins, headers, methods, and credentials.</li><li>A2A: Enable agent-to-agent (A2A) communication features.</li><li>Backend Auth: Set up authentication for backend services such as passthrough, key, GCP, AWS, and so on.</li><li>Timeout: Set request and backend timeouts.</li><li>Retry: Configure retry attempts, backoff, and which response codes should trigger retries.</li></ul> | Policies in HTTPRoutes and Backends. |

## Feature enablement

To use agentgateway features, you must enable the agentgateway feature in {{< reuse "docs/snippets/kgateway.md" >}}. Additionally, to route to AI providers, enable the AI Gateway feature alongside AI gateway.

1. Upgrade or install the {{< reuse "/docs/snippets/kgateway.md" >}} control plane to enable the agentgateway data plane. 

   ```shell
   helm upgrade -i -n {{< reuse "docs/snippets/namespace.md" >}} {{< reuse "/docs/snippets/helm-kgateway.md" >}} oci://{{< reuse "/docs/snippets/helm-path.md" >}}/charts/{{< reuse "/docs/snippets/helm-kgateway.md" >}} \
     --set agentgateway.enabled=true \
     --version {{< reuse "docs/versions/helm-version-upgrade.md" >}}
   ```

2. Verify that your Helm installation was updated.
   ```shell
   helm get values {{< reuse "/docs/snippets/helm-kgateway.md" >}} -n {{< reuse "docs/snippets/namespace.md" >}} -o yaml
   ```
   
   Example output: 
   ```
   
   agentgateway:
     enabled: true
   ```

3. Review the guides in the following sections to create an agentgateway proxy that fits your use case:
   * [LLM consumption]({{< link-hextra path="/agentgateway/llm/" >}})
   * [Inference routing]({{< link-hextra path="/agentgateway/inference/" >}})
   * [MCP connectivity]({{< link-hextra path="/agentgateway/mcp/" >}})
   * [Agent connectivity]({{< link-hextra path="/agentgateway/agent/" >}})


<!--
## More considerations

Review the following considerations for using agentgateway.

- Attaching a {{< reuse "docs/snippets/trafficpolicy.md" >}} to a particular route via the `ExtensionRef` filter is not supported. Instead, use the [HTTPRoute rule attachment option]({{< link-hextra path="/about/policies/trafficpolicy/#attach-to-rule" >}}) to apply a policy to an individual route, which requires the Kubernetes Gateway API experimental channel version 1.3.0 or later.
- HTTPListenerPolicy and BackendConfigPolicy resources that configure Envoy-specific filters, such as health checks, TLS, and access logging, cannot be applied to agentgateway proxies. You can use these policies with Envoy-based kgateway proxies only. 
- External processing (extProc) as part of the {{< reuse "docs/snippets/trafficpolicy.md" >}} is not supported.
- Configuring your agentgateway proxy as a Dynamic Forward Proxy (DFP) is currently not supported.
- [Header modifier filters](../../traffic-management/header-control/) in {{< reuse "docs/snippets/trafficpolicy.md" >}} are not supported for agentgateway proxies. You can still use header modifier filters in the Gateway API-native HTTPRoutes.
- Retries and timeouts cannot be configured on an agentgateway proxy.
- In transformation policies, response-based transformations are not supported. Also note that the `parseAs` field is not supported, but you can use the `json()` function directly in CEL expressions instead

-->