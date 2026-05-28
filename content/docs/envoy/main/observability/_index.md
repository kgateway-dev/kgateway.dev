---
title: Observability
icon: monitoring
weight: 700
description: Gain insight into the health and performance of your gateways.
next: /docs/operations
prev: /docs/integrations
---
Gain insight into the health and performance of your gateway environment.

## Guides

{{< cards >}}
  {{< card link="otel-stack" title="Set up the OpenTelemetry stack" subtitle="Deploy an OpenTelemetry collector stack to collect logs, metrics, and traces from your gateway." >}}
  {{< card link="tracing" title="Configure tracing" subtitle="Capture distributed traces of requests as they pass through your gateway." >}}
  {{< card link="control-plane-metrics" title="Review control plane metrics" subtitle="Monitor the kgateway control plane with Prometheus metrics." >}}
  {{< card link="gateway-metrics" title="Review gateway proxy metrics" subtitle="Scrape Envoy proxy metrics from gateway pods to track request rates, latency, and connection health." >}}
{{< /cards >}}
