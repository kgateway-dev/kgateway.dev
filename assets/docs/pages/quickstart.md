Get started with {{< reuse "/docs/snippets/kgateway.md" >}}, a cloud-native Layer 7 proxy that is based on the [Envoy](https://www.envoyproxy.io/) and [{{< reuse "docs/snippets/k8s-gateway-api-name.md" >}}](https://gateway-api.sigs.k8s.io/) projects.

## Before you begin

These quick start steps assume that you have a Kubernetes cluster, `kubectl`, and `helm` already set up. For quick testing, you can use [Kind](https://kind.sigs.k8s.io/).

```sh
kind create cluster
```

## Install

The following steps get you started with a basic installation. For detailed instructions, see the [installation guides]({{< link-hextra path="/install">}}).

{{< reuse "docs/snippets/get-started.md" >}}

Good job! You now have the {{< reuse "/docs/snippets/kgateway.md" >}} control plane running in your cluster.

## Next steps

Set up the data plane by choosing a gateway proxy depending on your use case.

{{< icon "kgateway" >}} [Set up an API gateway with an httpbin sample app]({{< link-hextra path="/install/sample-app/" >}}). This guide uses the Envoy-based {{< reuse "/docs/snippets/kgateway.md" >}} proxy to set up an API gateway. Then, deploy a sample httpbin app, configure a basic HTTP listener on the API gateway, and route traffic to httpbin by using an HTTPRoute resource.

{{% version include-if="2.2.x,2.1.x" %}}

{{< icon "agentgateway" >}} [Set up an AI gateway with an MCP sample tool server](../agentgateway/). This guide uses the agentgateway proxy to set up an AI gateway that you can use for Model Context Protocol (MCP), agent-to-agent (A2A), large language model (LLM), and more AI-related use cases. The example deploys a sample MCP server with a `fetch` tool, exposes the tool with agentgateway, and tests the tool with the MCP Inspector UI.

{{% /version%}}

## Cleanup

No longer need {{< reuse "/docs/snippets/kgateway.md" >}}? Uninstall with the following command:

```sh
helm uninstall {{< reuse "/docs/snippets/helm-kgateway.md" >}} -n {{< reuse "docs/snippets/namespace.md" >}}
```
