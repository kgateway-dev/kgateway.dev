---
title: Session affinity
weight: 20
description: Choose how the gateway selects a backend, from load balancing strategies to sticky sessions.
---
Manage how the gateway proxy selects backend services for incoming client requests, including routing requests for a particular session to the same backend service instance.

{{< callout >}}
{{< reuse "docs/snippets/proxy-kgateway.md" >}}
{{< /callout >}}

{{< cards >}}
  {{< card link="loadbalancing" title="Simple load balancing" subtitle="Choose a load balancing algorithm, such as round robin or least request, for a backend." >}}
  {{< card link="consistent-hashing" title="Consistent hashing" subtitle="Pin requests from the same client to the same backend by using consistent hashing." >}}
  {{< card link="session-persistence" title="Session persistence" subtitle="Maintain client-to-backend affinity with cookie or header-based session persistence." >}}
{{< /cards >}}