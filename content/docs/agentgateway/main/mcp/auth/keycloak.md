---
title: Set up Keycloak
weight: 20
---

Set up Keycloak in your cluster as your OAuth identity provider. Then, configure your agentgateway proxy to connect to your Keycloak IdP. With this guide, you set up a sample realm with two users, as well as configure settings that you might use for future auth scenarios.

{{< reuse "docs/snippets/keycloak.md" >}}

## Next 

[Set up MCP auth]({{< link-hextra path="/mcp/auth/setup/" >}}).
 
## Cleanup

{{< reuse "docs/snippets/cleanup.md" >}}

```
kubectl delete namespace keycloak
```