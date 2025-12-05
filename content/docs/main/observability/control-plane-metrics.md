---
title: Control plane metrics
weight: 20
---

By default, the {{< reuse "/docs/snippets/kgateway.md" >}} control plane exposes metrics in Prometheus format. You can use these metrics to monitor the health and performance of your gateway environment. For more information about how metrics are implemented, refer to the [kgateway project developer docs](https://github.com/kgateway-dev/kgateway/tree/main/devel/metrics).

## View control plane metrics {#control-plane-metrics}

The following steps show you how to quickly view the metrics endpoint of the control plane deployment. To integrate the metrics into your observability stack, see the [OpenTelemetry guide](/docs/observability/otel-stack/).

1. Port-forward the control plane deployment on port 9092.

   ```sh
   kubectl -n {{< reuse "docs/snippets/namespace.md" >}} port-forward deployment/{{< reuse "/docs/snippets/helm-kgateway.md" >}} 9092
   ```

2. Open your browser to the metrics endpoint: [http://localhost:9092/metrics](http://localhost:9092/metrics).

   Example output:

   ```console
   # HELP kgateway_controller_reconciliations_total Total controller reconciliations
   # TYPE kgateway_controller_reconciliations_total counter
   kgateway_controller_reconciliations_total{controller="gateway",result="success"} 1
   kgateway_controller_reconciliations_total{controller="gatewayclass",result="success"} 2
   kgateway_controller_reconciliations_total{controller="gatewayclass-provisioner",result="success"} 2
   ```

## Control plane metrics reference {#reference}

Review the following table to understand more about each metric.

Helpful terms:

* Controller: A Kubernetes controller that reconciles resources as part of the {{< reuse "/docs/snippets/kgateway.md" >}} control plane deployment.

* Resource: A Kubernetes object that is managed by a controller of the control plane.

* Snapshot: A complete, point-in-time representation of the current state of resources that the controller builds and serves to a gateway proxy via the Envoy extensible Discovery Service (XDS) API.

* Sync: The metrics refer to two kinds of syncs:
  
  * Status sync metrics represent the time it takes for you as a user to view the status that is reported on the resource.
  * Snapshot sync metrics roughly represent the time it takes for a resource change to become effective in the gateway proxies.

* Transform: The process of the control plane converting high-level resources or intermediate representations (IR) into lower-level representations into the structure that the XDS API expects for a snapshot.

{{< reuse "docs/snippets/main/metrics-control-plane.md" >}}
