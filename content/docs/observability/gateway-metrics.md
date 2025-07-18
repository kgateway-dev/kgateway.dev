---
title: Gateway proxy metrics
weight: 20
---

By default, {{< reuse "/docs/snippets/kgateway.md" >}} exposes metrics in Prometheus format for the data plane of each gateway proxy. You can use these metrics to monitor the health and performance of your gateway environment.

## View default data plane metrics in Prometheus {#prometheus-metrics}

The following steps show you how to quickly view the metrics endpoint of the gateway proxy deployment. To integrate the Prometheus metrics into your observability stack, see the [OpenTelemetry guide](/docs/observability/otel-stack/).

1. Port-forward the gateway deployment on port 19000.
   
   ```sh
   kubectl -n {{< reuse "docs/snippets/namespace.md" >}} port-forward deployment/http 19000
   ```

2. Access the gateway metrics by reviewing the [Prometheus statistics `/stats/prometheus` endpoint](http://localhost:19000/stats/prometheus).

   Example output:

   ```console
   # TYPE envoy_cluster_external_upstream_rq counter
   envoy_cluster_external_upstream_rq{envoy_response_code="200",envoy_cluster_name="kube_httpbin_httpbin_8000"} 5
   ```

## Gateway proxy metrics reference {#reference}

For more details about the collected metrics, see the [Envoy statistics reference docs](https://www.envoyproxy.io/docs/envoy/latest/operations/stats_overview).
