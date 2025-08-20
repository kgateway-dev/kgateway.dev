---
title: User interface
weight: 50
---

Review your agentic networking resources in a user interface (UI). Choose from the [agentgateway UI](#agentgateway) or [MCP Inspector](#mcp-inspector).

## Before you begin

{{< reuse "docs/snippets/prereq-agw.md" >}}
3. Follow one of the guides such as the [static MCP server](../mcp/static-mcp/) to create an agentgateway proxy and set up routing to an MCP server. 

## Launch the agentgateway UI {#agentgateway}

Agentgateway includes a read-only user interface (UI) that you can use to view your agentgateway resources.

{{< callout type="warning" >}}
Note that the agentgateway UI is read-only, because proxy updates must go through the {{< reuse "/docs/snippets/kgateway.md" >}} control plane translation process to generate an xDS snapshot. The playground functionality is also restricted until agentgateway supports more policies in {{< reuse "/docs/snippets/kgateway.md" >}}.
{{< /callout >}}

1. Find the agentgateway proxy that you want to view resources for. 

   ```shell
   kubectl get pods -A -l app.kubernetes.io/name=agentgateway
   ```

2. Enable port forwarding to the agentgateway proxy on port 15000.

   ```shell
   kubectl port-forward -n default $(kubectl get pod -n default -l app.kubernetes.io/name=agentgateway -o jsonpath='{.items[0].metadata.name}') 15000:15000
   ```

3. In your browser, open the UI at [`http://localhost:15000/ui`](http://localhost:15000/ui).

   {{< reuse-image src="img/agw-ui-landing.png" caption="Agentgateway UI landing page" >}}
   {{< reuse-image-dark srcDark="img/agw-ui-landing-dark.png" caption="Agentgateway UI landing page" >}}

Nice job! Now you can use the UI to explore your agentgateway resources. For more information about these resources, see [Agentgateway resource configuration](../about/#resources).

## MCP Inspector {#mcp-inspector}

MCP Inspector is a popular tool for testing and debugging Model Context Protocol (MCP) servers, including agentgateway.

For more information about installing and using the tool, see the [MCP Inspector documentation](https://modelcontextprotocol.io/legacy/tools/inspector).
