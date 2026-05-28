---
title: About
description: Get to know kgateway's architecture, custom resources, deployment patterns, and policy system.
weight: 200
icon: lightbulb
---

{{< reuse "docs/snippets/kgateway-about.md" >}}

To learn more about {{< reuse "docs/snippets/kgateway.md" >}}, review the following topics.

{{< cards >}}
  {{< card link="overview" title="Overview" subtitle="Get a primer on ingress, API gateways, and how kgateway extends the Kubernetes Gateway API." >}}
  {{< card link="architecture" title="Architecture" subtitle="Learn how the kgateway control plane translates Gateway API resources into Envoy configuration." >}}
  {{< card link="deployment-patterns" title="Deployment patterns" subtitle="Compare single-gateway, sharded, and service-mesh deployment patterns." >}}
  {{< card link="custom-resources" title="Custom resources" subtitle="Review the Gateway API and kgateway custom resources for configuring your gateway." >}}
  {{< card link="proxies" title="Gateway proxies" subtitle="Compare kgateway, agentgateway, and other supported gateway proxy types." >}}
  {{< card link="policies" title="Policies" subtitle="Attach traffic management, resiliency, and security policies to HTTPRoutes, Gateways, and listeners." >}}
{{< /cards >}}