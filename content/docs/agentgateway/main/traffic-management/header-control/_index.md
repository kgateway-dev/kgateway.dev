---
title: Header control
weight: 20
---

Modify the headers of HTTP requests and responses.

## Configuration options {#options}

You can configure the header modifier filter at the HTTPRoute level:

* **HTTPRoute**: For the native way in Kubernetes Gateway API, configure a header modifier filter in the HTTPRoute. You can choose to apply the header modifier filter to all the routes that are defined in the HTTPRoute, or to a selection of `backendRefs`. For more information, see the [Kubernetes Gateway API docs](https://gateway-api.sigs.k8s.io/guides/http-header-modifier/).

## Guides

{{< cards >}}
  {{< card link="request-header" title="Request headers" >}}
  {{< card link="response-header" title="Response headers" >}}
{{< /cards >}}
