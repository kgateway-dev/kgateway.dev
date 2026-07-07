---
title: Gateway health checks
description: Expose a health endpoint on the gateway listener for load balancer probes.
weight: 10
---

{{< callout type="tip" >}}
If your load balancer prepends PROXY protocol headers to health check connections, such as an AWS NLB with proxy protocol v2 enabled, the Envoy readiness listener on port 8082 drops these connections by default. You can enable the PROXY protocol filter on the readiness listener so that health checks succeed. For more information, see [Readiness listener PROXY protocol]({{< link-hextra path="/traffic-management/proxy-protocol/#readiness" >}}).
{{< /callout >}}


{{< reuse "kgw-docs/pages/traffic-management/health-checks/gateway.md" >}}
