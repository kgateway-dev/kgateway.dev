---
title: Transformations
weight: 120
---

Mutate and transform requests and responses before forwarding them to the destination.

{{< callout type="warning" >}}
To apply transformations to all the routes, you must use kgateway version 2.1.0-main or later. Then, you can select the Gateway in the `targetRefs` field of the TrafficPolicy. Remember that you can configure route-specific transformations by creating another TrafficPolicy with the `targetRefs` field set to the specific HTTPRoute. The HTTPRoute-level policy takes precedence over the Gateway-level policy.
{{< /callout >}}

{{< cards >}}
  {{< card link="inject-response-headers" title="Inject response headers" >}}
  {{< card link="decode-base64-headers" title="Decode base64 headers" >}}
  {{< card link="update-request-path" title="Update request paths and methods" >}}
{{< /cards >}}