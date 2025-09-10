---
title: Session affinity
weight: 20
description: 
---

Manage how the gateway proxy selects backend services for incoming client requests, including routing requests for a particular session to the same backend service instance.

{{< callout >}}
{{< reuse "docs/snippets/proxy-kgateway.md" >}}
{{< /callout >}}

{{< cards >}}
  {{< card link="loadbalancing" title="Simple load balancing" >}}
  {{< card link="consistent-hashing" title="Consistent hashing" >}}
  {{< card link="session-persistence" title="Session persistence" >}}
{{< /cards >}}