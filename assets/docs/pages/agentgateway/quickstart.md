Get started with {{< reuse "/docs/snippets/agentgateway.md" >}}. {{< reuse "docs/snippets/agentgateway/about.md" >}}

## Before you begin

These quick start steps assume that you have a Kubernetes cluster, `kubectl`, and `helm` already set up. For quick testing, you can use [Kind](https://kind.sigs.k8s.io/).

```sh
kind create cluster
```

## Install

The following steps get you started with a basic installation.

{{< reuse "docs/snippets/agentgateway/get-started.md" >}}

Good job! You now have the {{< reuse "/docs/snippets/kgateway.md" >}} control plane running in your cluster.

## Next steps

{{< icon "agentgateway" >}} [Set up an AI gateway with an MCP sample tool server]({{< link-hextra path="/setup/" >}}). This guide uses the agentgateway proxy to set up an AI gateway that you can use for Model Context Protocol (MCP), agent-to-agent (A2A), large language model (LLM), and more AI-related use cases. The example deploys a sample MCP server with a `fetch` tool, exposes the tool with agentgateway, and tests the tool with the MCP Inspector UI.

## Cleanup

No longer need {{< reuse "/docs/snippets/kgateway.md" >}}? Uninstall with the following command:

```sh
helm uninstall {{< reuse "/docs/snippets/helm-kgateway.md" >}} -n {{< reuse "docs/snippets/namespace.md" >}}
```
