---
title: MCP
weight: 30
---

Route to Model Context Protocol (MCP) servers through agentgateway.

## About MCP {#about}

[Model Context Protocol (MCP)](https://modelcontextprotocol.io/introduction) is an open protocol that standardizes how Large Language Model (LLM) applications connect to various external data sources and tools. Without MCP, you need to implement custom integrations for each tool that your LLM application needs to access. However, this approach is hard to maintain and can cause issues when you want to scale your environment. With MCP, you can significantly speed up, simplify, and standardize these types of integrations.

An MCP server exposes external data sources and tools so that LLM applications can access them. Typically, you want to deploy these servers remotely and have authorization mechanisms in place so that LLM applications can safely access the data.

With agentgateway, you can connect to one or multiple MCP servers in any environment. The agentgateway proxies requests to the MCP tool that is exposed on the server. You can also use the agentgateway to federate tools from multiple MCP servers.

## Guides

{{< cards >}}
  {{< card link="static-mcp" title="Static MCP" >}}
  {{< card link="dynamic-mcp" title="Dynamic MCP" >}}
{{< /cards >}}