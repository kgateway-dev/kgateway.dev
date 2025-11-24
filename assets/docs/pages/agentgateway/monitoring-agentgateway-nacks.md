## About NACKs {#nacks}

A NACK (negative acknowledgement) occurs when an {{< reuse "docs/snippets/agentgateway.md" >}} proxy rejects a configuration update from the {{< reuse "/docs/snippets/kgateway.md" >}} control plane. NACKs typically indicate configuration issues that prevent the proxy from applying the desired routing, policy, or backend settings.

Typically, the {{< reuse "/docs/snippets/kgateway.md" >}} control plane reports errors during translation, in which the control plane immediately rejects invalid configuration in custom resources and records errors in custom resource statuses. However, some errors can only be caught at configuration time, in which the control plane cannot determine the configuration failure until a proxy in the data plane rejects the configuration.

To track these NACKs at configuration time, the {{< reuse "/docs/snippets/kgateway.md" >}} control plane exposes a combination of metrics and events that monitor the health of config synchronization between the {{< reuse "/docs/snippets/kgateway.md" >}} control plane and {{< reuse "docs/snippets/agentgateway.md" >}} proxies.

For more general information about {{< reuse "/docs/snippets/kgateway.md" >}} control plane metrics, see [Control plane metrics](../../observability/control-plane-metrics/).

Common causes of NACKs include:

* CEL expressions in policies that the control plane validator allows, but the data plane rejects. The control plane uses a Go-based CEL validator, while agentgateway uses a Rust-based validator, which can have different validation behavior.
* Invalid TLS certificates.

When a NACK occurs, {{< reuse "/docs/snippets/kgateway.md" >}} provides two observability signals:

* **Prometheus metric**: A counter metric tracks the total number of NACKs across all {{< reuse "docs/snippets/agentgateway.md" >}} proxies that {{< reuse "/docs/snippets/kgateway.md" >}} manages.
* **Kubernetes events**: {{< reuse "/docs/snippets/kgateway.md" >}} creates Warning events on both the `Gateway` and its corresponding `Deployment` with details about the error.

## Monitor NACKs with control plane metrics {#nack-metrics}

You can access the {{< reuse "/docs/snippets/kgateway.md" >}} control plane metrics endpoint to view NACK metrics that track configuration rejections from {{< reuse "docs/snippets/agentgateway.md" >}} proxies.

### View the NACK metric {#view-nack-metric}

1. Port-forward the control plane deployment on port 9092.
   ```sh
   kubectl -n {{< reuse "docs/snippets/namespace.md" >}} port-forward deployment/{{< reuse "/docs/snippets/helm-kgateway.md" >}} 9092
   ```

2. Open the {{< reuse "/docs/snippets/kgateway.md" >}} control plane [metrics endpoint](http://localhost:9092/metrics).

3. Search for the `kgateway_agentgateway_xds_rejects_total` metric.

   {{< callout type="info" >}}
   The metric will only appear after at least one NACK has been reported. If no NACKs have occurred, the metric will not be present in the metrics output.
   {{< /callout >}}

   Example output:

   ```console
   # HELP kgateway_agentgateway_xds_rejects_total Total number of xDS responses rejected by agentgateway proxy
   # TYPE kgateway_agentgateway_xds_rejects_total counter
   kgateway_agentgateway_xds_rejects_total 3
   ```

You can use this metric to configure alerts to notify you when NACKs occur so you can quickly investigate and resolve configuration issues.

For guidance on setting up the observability stack, which allows for configurable alerting, see the [OpenTelemetry stack guide](../../observability/otel-stack/).

## Monitor NACKs with Kubernetes events {#nack-events}

When a NACK occurs for an {{< reuse "docs/snippets/agentgateway.md" >}} proxy, {{< reuse "/docs/snippets/kgateway.md" >}} also creates Kubernetes Warning events on both the `Gateway` and its corresponding `Deployment`.

### View NACK events {#view-nack-events}

Use the following commands to view NACK events for your agentgateway deployment.

1. List NACK events in the namespace where your Gateway is deployed.  If you have multiple Gateways across different namespaces, you can search across all namespaces with `--all-namespaces` instead of `-n <namespace>`.

   ```sh
   kubectl get events -n <namespace> --field-selector=reason=AgentGatewayNackError
   ```

   Example output:

   ```console
   LAST SEEN   TYPE      REASON                  OBJECT                    MESSAGE
   83s         Warning   AgentGatewayNackError   gateway/agentgateway      policy/traffic/default/example-agw-policy-for-body:transformation:default/example-route-for-body: error: parse: ERROR: <input>:1:20: invalid argument has(request.headers['x-priority-level']) ? 'level_' + request.headers['x-priority-level'] : 'level_unknown'
   83s         Warning   AgentGatewayNackError   deployment/agentgateway   policy/traffic/default/example-agw-policy-for-body:transformation:default/example-route-for-body: error: parse: ERROR: <input>:1:20: invalid argument has(request.headers['x-priority-level']) ? 'level_' + request.headers['x-priority-level'] : 'level_unknown'
   ```

2. View events for a specific Gateway.

   ```sh
   kubectl describe gateway <gateway-name> -n <namespace>
   ```

   Look for events in the output similar to the following.

   ```console
   Events:
     Type     Reason                   Age                From                          Message
     ----     ------                   ----               ----                          -------
     Warning  AgentGatewayNackError    36s                kgateway.dev/agentgateway     policy/traffic/default/example-agw-policy-for-body:transformation:default/example-route-for-body: error: parse: ERROR: <input>:1:20: invalid argument has(request.headers['x-priority-level']) ? 'level_' + request.headers['x-priority-level'] : 'level_unknown'
   ```

3. View events for the associated Deployment in the same name and namespace as the Gateway.

   ```sh
   kubectl describe deployment <gateway-name> -n <namespace>
   ```