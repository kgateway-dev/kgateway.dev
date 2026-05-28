---
title: Request matching
description: Match requests by path, method, header, query parameter, or regular expression.
weight: 20
---

Specify how you want to match requests that arrive at your gateway, such as with regular expressions (regex).

{{< cards >}}
  {{< card link="header" title="Header" subtitle="Specify a set of headers which incoming requests must match in entirety, such as with regular expressions (regex)." >}}
  {{< card link="host" title="Host" subtitle="Expose a route on multiple hosts." >}}
  {{< card link="method" title="HTTP method" subtitle="Specify an HTTP method, such as POST, GET, PUT, PATCH, or DELETE, to match requests against." >}}
  {{< card link="path" title="Path" subtitle="Match the targeted path of an incoming request against specific path criteria." >}}
  {{< card link="query" title="Query parameter" subtitle="Specify a set of URL query parameters which requests must match in entirety." >}}
{{< /cards >}}