---
title: "Examples"
weight: 50
---

This section contains step-by-step examples showing how to migrate common Ingress NGINX configurations to agentgateway using the `ingress2gateway` tool.

Each example walks through:
1. Creating a sample Ingress manifest
2. Running `ingress2gateway` to convert it
3. Reviewing the generated Gateway API and agentgateway resources
4. Applying them to your cluster

Pick the example that matches your use case, or work through them all to get familiar with the migration workflow.

  {{< card link="basic" title="Basic Ingress" >}}
  {{< card link="rate-limiting" title="Rate Limiting" >}}
  {{< card link="cors" title="CORS" >}}
  {{< card link="ssl-redirect" title="SSL Redirect" >}}
  {{< card link="external-auth" title="External Auth" >}}
  {{< card link="backend-tls" title="Backend TLS" >}}
