---
title: Transformations
description: Transform request and response headers and bodies with templated expressions.
weight: 20
---

Mutate and transform requests and responses before forwarding them to the destination.

## Known limitations

**Gateway-level policy in 2.1.x or later**: {{< reuse "docs/versions/warn-2-1-only.md" >}} If you use version 2.1 or later, you can select the Gateway in the `targetRefs` field of the TrafficPolicy. Remember that you can configure route-specific transformations by creating another TrafficPolicy with the `targetRefs` field set to the specific HTTPRoute. The HTTPRoute-level policy takes precedence over the Gateway-level policy.
