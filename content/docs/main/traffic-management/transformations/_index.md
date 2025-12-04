---
title: Transformations
weight: 20
---

Mutate and transform requests and responses before forwarding them to the destination.

{{< cards >}}
  {{< card link="inject-response-headers" title="Inject response headers" >}}
  {{< card link="decode-base64-headers" title="Decode base64 headers" >}}
  {{< card link="update-request-path" title="Update request paths and methods" >}}
  {{< card link="redirect-url" title="Create redirect URLs" >}}
  {{< card link="change-response-status" title="Change response status" >}}
  {{< card link="update-response-body" title="Update response body" >}}
{{< /cards >}}

## Known limitations

**Gateway-level policy in 2.1.x or later**: {{< reuse "docs/versions/warn-2-1-only.md" >}} If you use version 2.1 or later, you can select the Gateway in the `targetRefs` field of the TrafficPolicy. Remember that you can configure route-specific transformations by creating another TrafficPolicy with the `targetRefs` field set to the specific HTTPRoute. The HTTPRoute-level policy takes precedence over the Gateway-level policy.
