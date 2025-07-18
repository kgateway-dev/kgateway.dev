---
title: Observability
weight: 700
description: Gain insight into the health and performance of your gateways.
next: /docs/operations
prev: /docs/integrations
---

Gain insight into the health and performance of your gateway environment.

## Observability data types {#data-types}

Observability is built on three core pillars as described in the following table. By combining these three data types, you get a complete picture of your system's health and performance.

| Pillar | Description |
| -- | -- |
| Logs | Discrete events that happen at a specific time with detailed context. |
| Metrics | Numerical measurements aggregated over time intervals. |
| Traces | Records of requests as they flow through distributed systems. |

## Guides

{{< cards >}}
  {{< card link="otel-stack" title="Set up the OpenTelemetry stack" >}}
  {{< card link="control-plane-metrics" title="Review control plane metrics" >}}
  {{< card link="gateway-metrics" title="Review gateway proxy metrics" >}}
  {{< card link="../ai/observability/" title="AI Gateway observability" >}}
{{< /cards >}}
