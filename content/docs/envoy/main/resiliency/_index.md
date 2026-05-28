---
title: Resiliency
icon: health_and_safety
description: Apply retries, timeouts, circuit breakers, and fault injection to keep your gateway resilient.
weight: 430
---
Simulate failures, disruptions, and adverse conditions to test that your gateway and apps continue to function.

{{< cards >}}
  {{< card link="circuit-breakers" title="Circuit breakers" subtitle="Trip a circuit breaker when concurrent requests or pending connections exceed a threshold." >}}
  {{< card link="connection" title="HTTP conection settings" subtitle="Configure and manage HTTP connections to an upstream service." >}}
  {{< card link="fault-injection" title="Fault injection" subtitle="Test the resilience of your apps by injecting delays and connection failures into a percentage of your requests." >}}
  {{< card link="mirroring" title="Mirroring" subtitle="Copy live production traffic to a shadow environment or service so that you can try out, analyze, and monitor new software changes before deploying them to production." >}}
  {{< card link="outlier-detection" title="Outlier detection" subtitle="Eject misbehaving upstream hosts from the load balancing pool when consecutive errors occur." >}}
  {{< card link="retry" title="Retries" subtitle="Automatically retry failed requests against backends with configurable conditions and budgets." >}}
  {{< card link="tcp-keepalive" title="TCP keepalive" subtitle="Manage idle and stale connections with TCP keepalive." >}}
  {{< card link="timeouts" title="Timeouts" subtitle="Bound how long requests, streams, and idle connections can run before the gateway gives up." >}}
{{< /cards >}}
