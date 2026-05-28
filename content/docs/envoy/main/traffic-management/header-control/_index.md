---
title: Header control
description: Add, remove, or rewrite request and response headers on routes and listeners.
weight: 20
---

Modify the headers of HTTP requests and responses.

## Configuration options {#options}

{{< reuse "docs/snippets/header-control-options.md" >}}

## Guides

{{< cards >}}
  {{< card link="request-header" title="Request headers" subtitle="Add, set, or remove headers on requests that the gateway forwards to a backend." >}}
  {{< card link="response-header" title="Response headers" subtitle="Add, set, or remove headers on responses that the gateway returns to the client." >}}
  {{< card link="early-request-header-modifier" title="Early request header modification" subtitle="Modify request headers before authentication and policy filters run." >}}
{{< /cards >}}
