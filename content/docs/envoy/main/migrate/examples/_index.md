---
title: "Examples"
description: Walk through worked examples that convert common Ingress NGINX configurations to kgateway.
weight: 50
---

This section contains step-by-step examples showing how to migrate common Ingress NGINX configurations to kgateway using the `ingress2gateway` tool.

Each example walks through the following steps:

1. Creating a sample Ingress manifest.
2. Running `ingress2gateway` to convert it.
3. Reviewing the generated Gateway API and kgateway resources.
4. Applying them to your cluster.

Pick the example that matches your use case, or work through them all to get familiar with the migration workflow.

{{< cards >}}
  {{< card link="basic" title="Basic Ingress" subtitle="Convert a simple Ingress resource to a Gateway and HTTPRoute." >}}
  {{< card link="session-affinity" title="Session Affinity" subtitle="Convert Ingress NGINX session affinity annotations to a kgateway BackendConfigPolicy." >}}
  {{< card link="rate-limiting" title="Rate Limiting" subtitle="Convert Ingress NGINX rate limit annotations to a kgateway TrafficPolicy." >}}
  {{< card link="cors" title="CORS" subtitle="Convert Ingress NGINX CORS annotations to a kgateway TrafficPolicy." >}}
  {{< card link="ssl-redirect" title="SSL Redirect" subtitle="Convert Ingress NGINX SSL redirect annotations to an HTTPRoute RequestRedirect filter." >}}
  {{< card link="external-auth" title="External Auth" subtitle="Convert Ingress NGINX auth-url annotations to a kgateway external auth GatewayExtension." >}}
  {{< card link="canary" title="Canary Release" subtitle="Convert Ingress NGINX canary annotations to weighted HTTPRoute backends." >}}
  {{< card link="backend-tls" title="Backend TLS" subtitle="Convert Ingress NGINX backend TLS annotations to a kgateway BackendConfigPolicy." >}}
{{< /cards >}}
