---
title: Transformations
description: Transform request and response headers and bodies with templated expressions.
weight: 20
---

Mutate and transform requests and responses before forwarding them to the destination.

{{< cards >}}
  {{< card link="engines" title="Transformation engine" subtitle="Learn how the rustformation engine processes TrafficPolicy transformations and migrate templates from the classic transformation filter." >}}
  {{< card link="templating-language" title="Templating language" subtitle="Reference for the MiniJinja-style templating language used in transformations." >}}
  {{< card link="inject-response-headers" title="Inject response headers" subtitle="Extract values from a request header and inject it as a header to your response." >}}
  {{< card link="decode-base64-headers" title="Decode base64 headers" subtitle="Automatically decode base64 values in request headers and add the decoded value as a response header." >}}
  {{< card link="update-request-path" title="Update request paths and methods" subtitle="Change the request path and HTTP method when a request header is present." >}}
  {{< card link="redirect-url" title="Create redirect URLs" subtitle="Use a transformation to generate dynamic redirect URLs from request data." >}}
  {{< card link="change-response-status" title="Change response status" subtitle="Update the response status based on headers being present in a response." >}}
  {{< card link="update-response-body" title="Update response body" subtitle="Learn how to return a customized response body and how replace specific values in the body." >}}
{{< /cards >}}

## Known limitations

**Gateway-level policy in 2.1.x or later**: {{< reuse "docs/versions/warn-2-1-only.md" >}} If you use version 2.1 or later, you can select the Gateway in the `targetRefs` field of the TrafficPolicy. Remember that you can configure route-specific transformations by creating another TrafficPolicy with the `targetRefs` field set to the specific HTTPRoute. The HTTPRoute-level policy takes precedence over the Gateway-level policy.
