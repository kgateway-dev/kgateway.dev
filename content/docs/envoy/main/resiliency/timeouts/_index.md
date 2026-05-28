---
title: Timeouts
weight: 10
description: Bound how long requests, streams, and idle connections can run before the gateway gives up.
---
{{< cards >}}
{{< card link="about" title="About timeouts" subtitle="Compare the request, stream, idle, and per-try timeouts that kgateway supports." >}}
{{< card link="request" title="Request timeouts" subtitle="Configure timeouts for all routes in an HTTPRoute." >}}
{{< card link="idle-stream" title="Idle stream timeouts" subtitle="Close HTTP/2 streams that stay idle longer than the configured stream idle timeout." >}}
{{< card link="per-try-timeout" title="Per-try timeouts" subtitle="Per-try timeouts now live under the retry section, where they bound a single retry attempt.">}}
{{< /cards >}}