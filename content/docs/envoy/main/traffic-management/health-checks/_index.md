---
title: Health checks
description: Probe backend and gateway health to remove unhealthy endpoints from rotation.
weight: 20
---

Enable health checks on the gateway proxy or your backends to automatically monitor their availability.

{{< cards >}}
  {{< card link="gateway" title="Gateway health checks" subtitle="Expose a health endpoint on the gateway listener for load balancer probes." >}}
  {{< card link="backend" title="Backend health checks" subtitle="Configure active health checks against backend endpoints to detect failures." >}}
{{< /cards >}}
