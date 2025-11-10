Monitor your {{< reuse "docs/snippets/agentgateway.md" >}} proxies with metrics, logs, and events.

## Overview {#overview}
* **Proxy metrics and logs** - Exposed by {{< reuse "docs/snippets/agentgateway.md" >}} proxy pods on port `15020`. These metrics track request/response data, traffic patterns, and proxy health.
* **Control plane metrics and events** - Exposed by the {{< reuse "/docs/snippets/kgateway.md" >}} control plane on port `9092`. These metrics can be used to track configuration synchronization health, including NACKs (negative acknowledgements) when proxies reject configuration updates.

## Proxy metrics and logs {#proxy}

### View proxy metrics {#proxy-metrics}

You can access the {{< reuse "docs/snippets/agentgateway.md" >}} metrics endpoint to view proxy-specific metrics, such as request counts, latency, and connection statistics.

1. Port-forward the agentgateway proxy on port 15020.
   ```sh
   kubectl port-forward deployment/<gateway-name> -n <namespace> 15020
   ```

2. Open the {{< reuse "docs/snippets/agentgateway.md" >}} [metrics endpoint](http://localhost:15020/metrics).

3. Review the available metrics. For LLM-specific metrics, see [View LLM metrics and logs]({{< link-hextra path="/agentgateway/llm/observability/" >}}).

### View logs {#proxy-logs}

{{< reuse "docs/snippets/agentgateway-capital.md" >}} automatically logs information to stdout. When you run {{< reuse "docs/snippets/agentgateway.md" >}} on your local machine, you can view a log entry for each request to {{< reuse "docs/snippets/agentgateway.md" >}} in your CLI output. 

To view the logs: 
```sh
kubectl logs <agentgateway-pod> -n {{< reuse "docs/snippets/namespace.md" >}}
```

## Monitoring config synchronization between the {{< reuse "/docs/snippets/kgateway.md" >}} control plane and {{< reuse "docs/snippets/agentgateway.md" >}} {#config-sync}

### About xDS NACKs {#nacks}

A NACK (negative acknowledgement) occurs when an {{< reuse "docs/snippets/agentgateway.md" >}} proxy rejects a configuration update from the {{< reuse "/docs/snippets/kgateway.md" >}} control plane. NACKs typically indicate configuration issues that prevent the proxy from applying the desired routing, policy, or backend settings. Typically the {{< reuse "/docs/snippets/kgateway.md" >}} control plane reports errors during translation, but some errors can only be caught at configuration time.

{{< reuse "/docs/snippets/kgateway.md" >}} provides a combination of metrics and events to monitor the health of config synchronization between the {{< reuse "/docs/snippets/kgateway.md" >}} control plane and {{< reuse "docs/snippets/agentgateway.md" >}} proxies. The control plane exposes these metrics and events.

For more general information about {{< reuse "/docs/snippets/kgateway.md" >}} control plane metrics, see [Control plane metrics](../../observability/control-plane-metrics/).

Common causes of NACKs include:

* CEL expressions in policies that pass the control plane validator but the data plane rejects (the control plane uses a Go-based CEL validator, while agentgateway uses a Rust-based validator, which can have different validation behavior)
* Invalid TLS certificates

When a NACK occurs, {{< reuse "/docs/snippets/kgateway.md" >}} provides two observability signals:

* **Prometheus metric**: A counter metric tracks the total number of NACKs across all {{< reuse "docs/snippets/agentgateway.md" >}} proxies which kgateway manages
* **Kubernetes Events**: {{< reuse "/docs/snippets/kgateway.md" >}} creates Warning events on both the `Gateway` and its corresponding `Deployment` with details about the error

### Monitor NACKs with control plane metrics {#nack-metrics}

You can access the {{< reuse "/docs/snippets/kgateway.md" >}} control plane metrics endpoint to view NACK metrics that track configuration rejections from {{< reuse "docs/snippets/agentgateway.md" >}} proxies.

#### View the NACK metric {#view-nack-metric}

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

 For guidance on setting up the observability stack which will allow for easily configurable alerting, see the [OpenTelemetry stack guide](../../observability/otel-stack/).

### Check NACK events {#nack-events}

When a NACK occurs for an {{< reuse "docs/snippets/agentgateway.md" >}} proxy, {{< reuse "/docs/snippets/kgateway.md" >}} also creates Kubernetes Warning events on both the `Gateway` and its corresponding `Deployment`.

#### View NACK events {#view-nack-events}

Use the following commands to view NACK events for your agentgateway deployment.

1. List NACK events in the namespace where your Gateway is deployed.

   ```sh
   kubectl get events -n <namespace> --field-selector=reason=AgentGatewayNackError
   ```

   Example output:

   ```console
   LAST SEEN   TYPE      REASON                  OBJECT                    MESSAGE
   83s         Warning   AgentGatewayNackError   gateway/agentgateway      policy/traffic/default/example-agw-policy-for-body:transformation:default/example-route-for-body: error: parse: ERROR: <input>:1:20: invalid argument has(request.headers['x-priority-level']) ? 'level_' + request.headers['x-priority-level'] : 'level_unknown'
   83s         Warning   AgentGatewayNackError   deployment/agentgateway   policy/traffic/default/example-agw-policy-for-body:transformation:default/example-route-for-body: error: parse: ERROR: <input>:1:20: invalid argument has(request.headers['x-priority-level']) ? 'level_' + request.headers['x-priority-level'] : 'level_unknown'
   ```

   To search across all namespaces if you have multiple `Gateways` across different namespaces , use `--all-namespaces` instead of `-n <namespace>`.

2. View events for a specific `Gateway`.

   ```sh
   kubectl describe gateway <gateway-name> -n <namespace>
   ```

   Look for events in the output:

   ```console
   Events:
     Type     Reason                   Age                From                          Message
     ----     ------                   ----               ----                          -------
     Warning  AgentGatewayNackError    36s                kgateway.dev/agentgateway     policy/traffic/default/example-agw-policy-for-body:transformation:default/example-route-for-body: error: parse: ERROR: <input>:1:20: invalid argument has(request.headers['x-priority-level']) ? 'level_' + request.headers['x-priority-level'] : 'level_unknown'
   ```

3. View events for the associated `Deployment` (same name and namespace as the Gateway).

   ```sh
   kubectl describe deployment <gateway-name> -n <namespace>
   ```