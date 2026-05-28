---
title: Route delegation
description: Compose routing across teams by delegating subpaths to child HTTPRoute resources.
weight: 20
---

Manage routing rules more effectively by using multiple connected HTTPRoute resources.

{{< callout >}}
{{< reuse "docs/snippets/proxy-kgateway.md" >}}
{{< /callout >}}

{{< cards >}}
  {{< card link="overview" title="Route delegation overview" subtitle="Understand how parent and child HTTPRoutes delegate routing across teams and namespaces." >}}
  {{< card link="basic" title="Basic example" subtitle="Set up basic route delegation between a parent and two child HTTPRoute resources." >}}
  {{< card link="label" title="Delegation via labels" subtitle="Use labels to delegate traffic from a parent HTTPRoute to different child HTTPRoutes." >}}
  {{< card link="multi-parent" title="Multiple parents" subtitle="Set up route delegation for a child HTTPRoute resource that can receive traffic from one or more parent HTTPRoute resources." >}}
  {{< card link="multi-level-delegation" title="Multi-level delegation" subtitle="Create a 3-level route delegation hierarchy with a parent, child, and grandchild HTTPRoute resource." >}}
  {{< card link="header-query" title="Header and query match" subtitle="Use header and query matchers in a route delegation setup." >}}
  {{< card link="inheritance" title="Policy inheritance and overrides" subtitle="Control how policies are inherited and overridden along an HTTPRoute delegation chain." >}}
{{< /cards >}}
