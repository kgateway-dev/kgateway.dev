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
* Controller: The controller is the {{< reuse "/docs/snippets/kgateway.md" >}} control plane deployment.
* Resource: A resource is a Kubernetes object that is managed by the controller.
* Snapshot: A complete, point-in-time representation of the current state of resources that the controller builds and serves to a gateway proxy via the Envoy extensible Discovery Service (XDS) API.
* Sync: The syncer synchronizes the status of resources between the control plane and the underlying Kubernetes resources, so that their state is accurately reflected.
* Transform: The process of the control plane converting high-level resources or intermediate representations (IR) into lower-level representations into the structure that the XDS API expects for a snapshot.

{{< reuse "docs/snippets/metrics-control-plane.md" >}}
