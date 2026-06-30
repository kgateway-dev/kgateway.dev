By default, the {{< reuse "/docs/snippets/kgateway.md" >}} control plane exposes metrics in Prometheus format. You can use these metrics to monitor the health and performance of your gateway environment. For more information about how metrics are implemented, refer to the [kgateway project developer docs](https://github.com/kgateway-dev/kgateway/blob/main/devel/architecture/metrics.md).

## View control plane metrics {#control-plane-metrics}

The following steps show you how to quickly view the metrics endpoint of the control plane deployment. To integrate the metrics into your observability stack, see the [OpenTelemetry guide]({{< link-hextra path="/observability/otel-stack/" >}}).

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

{{< reuse "docs/snippets/control-plane-metrics.md" >}}

## Monitor NACKs

Monitor and troubleshoot Envoy proxy configuration rejections with control plane metrics.

### About NACKs {#nacks}

A NACK (negative acknowledgement) occurs when an Envoy proxy rejects a configuration update from the {{< reuse "/docs/snippets/kgateway.md" >}} control plane. NACKs typically indicate configuration issues that prevent the proxy from applying the desired routing, policy, or listener settings.

Typically, the {{< reuse "/docs/snippets/kgateway.md" >}} control plane reports errors during translation, in which the control plane immediately rejects invalid configuration in custom resources and records errors in custom resource statuses. However, some errors can only be caught at configuration time, in which the control plane cannot determine the configuration failure until an Envoy proxy in the data plane rejects the configuration.

To track these NACKs, the {{< reuse "/docs/snippets/kgateway.md" >}} control plane exposes Prometheus metrics that monitor the health of config synchronization between the control plane and Envoy proxies.

For more general information about {{< reuse "/docs/snippets/kgateway.md" >}} control plane metrics, see [Control plane metrics]({{< link-hextra path="/observability/control-plane-metrics/" >}}).

Common causes of NACKs include:

* Invalid Envoy configuration that passes control plane validation but is rejected by the Envoy proxy at runtime.
* Invalid TLS certificates.

You can access the {{< reuse "/docs/snippets/kgateway.md" >}} control plane metrics endpoint to view NACK metrics that track configuration rejections from Envoy proxies.

### View the NACK metrics {#view-nack-metrics}

1. Port-forward the control plane deployment on port 9092.

   ```sh
   kubectl -n {{< reuse "docs/snippets/namespace.md" >}} port-forward deployment/{{< reuse "docs/snippets/pod-name.md" >}} 9092
   ```

2. Open the {{< reuse "/docs/snippets/kgateway.md" >}} control plane [metrics endpoint](http://localhost:9092/metrics).

3. Search for the `kgateway_envoy_xds_rejects_total` and `kgateway_envoy_xds_rejects_active` metrics.

   {{< callout type="info" >}}
   The metrics only appear after at least one NACK has been reported. If no NACKs have occurred, these metrics are not present in the metrics output.
   {{< /callout >}}

   Example output:

   ```console
   # HELP kgateway_envoy_xds_rejects_total Total number of xDS responses rejected by envoy proxy
   # TYPE kgateway_envoy_xds_rejects_total counter
   kgateway_envoy_xds_rejects_total{gateway_namespace="default",gateway_name="gw",type_url="envoy.config.route.v3.RouteConfiguration"} 1
   # HELP kgateway_envoy_xds_rejects_active Number of xDS responses currently rejected by envoy proxy
   # TYPE kgateway_envoy_xds_rejects_active gauge
   kgateway_envoy_xds_rejects_active{gateway_namespace="default",gateway_name="gw",type_url="envoy.config.route.v3.RouteConfiguration"} 0
   ```

Both metrics are labeled by `gateway_namespace`, `gateway_name`, and `type_url`. The `type_url` label identifies the Envoy resource type that was rejected, such as `envoy.config.route.v3.RouteConfiguration`.

| Metric | Type | Description |
|--------|------|-------------|
| `kgateway_envoy_xds_rejects_total` | Counter | The cumulative total number of xDS responses rejected by Envoy proxies. This value only increases over time. |
| `kgateway_envoy_xds_rejects_active` | Gauge | The current number of active xDS rejections. This value increases when a new NACK occurs and decreases when the proxy successfully applies a subsequent configuration update (ACK). A value of `0` indicates no active rejections. |

You can use these metrics to configure alerts to notify you when NACKs occur so you can quickly investigate and resolve configuration issues.

For more information about how to set up the observability stack, see the [OpenTelemetry stack guide]({{< link-hextra path="/observability/otel-stack/" >}}).