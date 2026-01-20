---
title: Header control
weight: 20
---

Modify the headers of HTTP requests and responses.

## Configuration options {#options}

You can modify headers in kgateway using **three options**:

1. **HTTPRoute** — Modify request/response headers after route selection.
2. **TrafficPolicy** — Apply policies to headers after route selection.
3. **HTTPListenerPolicy** — New in v2.2, allows early request header modification before route selection. This ensures headers cannot influence routing or downstream policy evaluation. See the [Early request header modification guide](early-request-header-modifier.md) for full details.

{{< reuse "docs/snippets/header-control-options.md" >}}

## Guides

{{< cards >}}
  {{< card link="request-header" title="Request headers" >}}
  {{< card link="response-header" title="Response headers" >}}
  {{< card link="early-request-header-modifier" title="Early request header modification" >}}
{{< /cards >}}
