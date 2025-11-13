---
title: About 
weight: 5
description:
---

Learn more about MCP and common challenges when adopting MCP in enterprise environments. 

## About MCP

[Model Context Protocol (MCP)](https://modelcontextprotocol.io/introduction) is an open protocol that standardizes how Large Language Model (LLM) applications connect to various external data sources and tools. Without MCP, you need to implement custom integrations for each tool that your LLM application needs to access. However, this approach is hard to maintain and can cause issues when you want to scale your environment. With MCP, you can significantly speed up, simplify, and standardize these types of integrations.

An MCP server exposes external data sources and tools so that LLM applications can access them. Typically, you want to deploy these servers remotely and have authorization mechanisms in place so that LLM applications can safely access the data.

With {{< reuse "docs/snippets/agentgateway.md" >}}, you can connect to one or multiple MCP servers in any environment. {{< reuse "docs/snippets/agentgateway-capital.md" >}} proxies requests to the MCP tool that is exposed on the server. <!-- You can also use the agentgateway to federate tools from multiple MCP servers. For more information, see the [MCP multiplexing](/docs/mcp/connect/multiplex/) guide. -->

## MCP vs. A2A

MCP and [Agent-to-Agent (A2A)](https://github.com/a2aproject/A2A) are the leading protocols for enabling communication between agents and tools. MCP helps to retrieve and exchange context with Large Language Models (LLMs) and connect LLMs to tools. On the other hand, A2A solves for long-running tasks and state management across multiple agents. MCP and A2A are both JSON-RPC protocols that define the structure of how an agent describes what it wants to do, how it calls tools, and how it hands off tasks to other agents.

## Challenges with MCP and A2A
While MCP and A2A define the RPC communication protocol for agents and tools, they currently do not address real-world, enterprise-level concerns.

Agents typically do not operate in isolation. Instead, they interact with each other (agent-to-agent), with internal systems (agent-to-tool), and external or foundational models (agent-to-LLM). These interactions are often dynamic, multi-modal, and span organizational and data boundaries. 

Such long-lived interactivity creates new vectors for risk and complexity, including: 
* **Security**: How to handle authentication, authorization, and auditing of agent interactions across tools and services? 
* **Governance**: How to enforce policies across autonomous workflows, such as data residency or access control? 
* **Observability**: How to gain visibility into what agents are doing, when, and why? 
* **Scalability and performance**: How to ensure low latency while securely handling retries, timeouts, and failures? 

{{< reuse "docs/snippets/agentgateway-capital.md" >}} is designed to tackle these challenges at its core with built-in security, governance, and observability for all MCP and A2A communication between agents, tools, and LLMs. 