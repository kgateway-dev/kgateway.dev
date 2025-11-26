Use the kgateway control plane to deploy and manage the lifecycle of {{< reuse "/docs/snippets/agentgateway.md" >}} proxies on Kubernetes. </br></br>

{{< reuse "docs/snippets/agentgateway/about.md" >}}

## Before you begin

These quickstart steps assume that you have a Kubernetes cluster, `kubectl`, and `helm` already set up. For quick testing, you can use [Kind](https://kind.sigs.k8s.io/).

```sh
kind create cluster
```

## Install

The following steps get you started with a basic installation.

{{< reuse "docs/snippets/agentgateway/get-started.md" >}}

Good job! You now have the {{< reuse "/docs/snippets/kgateway.md" >}} control plane running in your cluster.

## Next steps

{{< icon "agentgateway" >}} [Create an agentgateway proxy]({{< link-hextra path="/setup/" >}}) that you can use for Model Context Protocol (MCP), agent-to-agent (A2A), large language model (LLM), and more AI-related use cases. For example, you can follow the [guide]({{< link-hextra path="/mcp/static-mcp/" >}}) to use agentgateway to proxy traffic to a sample MCP tool server. The example deploys a sample MCP server with a `fetch` tool, exposes the tool with agentgateway, and tests the tool with the MCP Inspector UI.

For other examples, see the [LLM consumption]({{< link-hextra path="/llm/" >}}), [inference routing]({{< link-hextra path="/inference/" >}}), [MCP]({{< link-hextra path="/mcp/" >}}), or [agent connectivity]({{< link-hextra path="/agent/" >}}) guides. 

## Cleanup

No longer need {{< reuse "/docs/snippets/kgateway.md" >}}? Uninstall with the following command:

```sh
helm uninstall {{< reuse "/docs/snippets/helm-kgateway.md" >}} -n {{< reuse "docs/snippets/namespace.md" >}}
```
