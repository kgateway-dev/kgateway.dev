You can update several installation settings in your Helm values file. For example, you can update the namespace, set resource limits and requests, or enable extensions such as for AI. 

Set the version you want to configure in an environment variable, such as the latest patch version (`{{< reuse "kgw-docs/versions/n-patch.md" >}}`).
   ```sh
   export NEW_VERSION={{< reuse "kgw-docs/versions/n-patch.md" >}}
   ```
* **Show all values**: 
      
  ```sh
  helm show values oci://{{< reuse "/kgw-docs/snippets/helm-path.md" >}}/charts/{{< reuse "/kgw-docs/snippets/helm-kgateway.md" >}} --version {{< reuse "kgw-docs/versions/helm-version-upgrade.md" >}}
  ```

* **Get a file with all values**: You can get a `{{< reuse "/kgw-docs/snippets/helm-kgateway.md" >}}/values.yaml` file for the upgrade version by pulling and inspecting the Helm chart locally.
      
  ```sh
  helm pull oci://{{< reuse "/kgw-docs/snippets/helm-path.md" >}}/charts/{{< reuse "/kgw-docs/snippets/helm-kgateway.md" >}} --version {{< reuse "kgw-docs/versions/helm-version-upgrade.md" >}}
  tar -xvf {{< reuse "/kgw-docs/snippets/helm-kgateway.md" >}}-{{< reuse "kgw-docs/versions/helm-version-upgrade.md" >}}.tgz
  open {{< reuse "/kgw-docs/snippets/helm-kgateway.md" >}}/values.yaml
  ```

For more information, see the [Helm reference docs]({{< link-hextra path="/reference/helm/" >}}).

## Development builds

When using the development build {{< reuse "kgw-docs/versions/patch-dev.md" >}}, add `--set controller.image.pullPolicy=Always` to ensure you get the latest image. For production environments, this setting is not recommended as it might impact performance.

### Experimental Gateway API features {#experimental-gateway-api-features}

{{< version include-if="2.1.x,2.2.x,2.3.x,2.4.x" >}}
The `KGW_ENABLE_EXPERIMENTAL_GATEWAY_API_FEATURES` feature gate controls support for experimental Gateway API features such as the following:

- TCPRoutes
- TLSRoutes
- ListenerSets
- CORS policies
- Retries
- Session persistence
{{< /version >}}
{{< version exclude-if="2.1.x,2.2.x,2.3.x,2.4.x" >}}
The `KGW_ENABLE_EXPERIMENTAL_GATEWAY_API_FEATURES` feature gate controls support for experimental Gateway API features and API versions, such as the following:

- Session persistence in HTTPRoutes, which is deprecated in favor of session persistence in a BackendConfigPolicy
- The legacy `XListenerSet` resource in the `gateway.networking.x-k8s.io` API group
- Support for the pre-v1 API versions of TCPRoutes and TLSRoutes, such as `v1alpha2`, in clusters where the Gateway API CRDs do not serve `v1`

Features that are in the standard channel of the Gateway API, such as ListenerSets, TCPRoutes, CORS policies, and retries, work when the gate is disabled. Retries are in the standard channel in Gateway API version 1.7 and later.
{{< /version >}}

{{< version include-if="2.1.x" >}}This setting defaults to `false` and must be explicitly enabled. To enable these features, set the environment variable in your kgateway controller deployment in your Helm values file.

```yaml
controller:
  extraEnv:
    KGW_ENABLE_EXPERIMENTAL_GATEWAY_API_FEATURES: "true"
```{{< /version >}}{{< version exclude-if="2.1.x" >}}In kgateway version 2.2 and later, this setting defaults to `true`, so experimental features are enabled by default and no additional configuration is required. To disable these features, set the environment variable to `false` in your kgateway controller deployment in your Helm values file.

```yaml
controller:
  extraEnv:
    KGW_ENABLE_EXPERIMENTAL_GATEWAY_API_FEATURES: "false"
```{{< /version >}}

## Leader election

Leader election is enabled by default to ensure that you can run {{< reuse "kgw-docs/snippets/kgateway.md" >}} in a multi-control plane replica setup for high availability. 

You can disable leader election by setting the `KGW_DISABLE_LEADER_ELECTION` environment variable to `"true"` through the `controller.extraEnv` Helm value.

```yaml
controller:
  extraEnv:
    KGW_DISABLE_LEADER_ELECTION: "true"
```

{{< version exclude-if="2.1.x,2.2.x,2.3.x,2.4.x" >}}
### Leader election timings {#leader-election-timings}

On clusters with a slow or temporarily unavailable Kubernetes API server, the controller can fail to renew its lease in time. The controller then repeatedly loses and re-acquires leadership. To make the controller more tolerant of a slow API server, increase the leader election timings through the `controller.leaderElection` Helm values.

```yaml
controller:
  leaderElection:
    leaseDuration: 30s
    renewDeadline: 20s
    retryPeriod: 5s
```

| Helm value | Environment variable | Description | Default |
| -- | -- | -- | -- |
| `controller.leaderElection.leaseDuration` | `KGW_LEADER_ELECTION_LEASE_DURATION` | The time that controller replicas that are not the leader wait before they try to take over a lease that the leader has not renewed. This value must be greater than `renewDeadline`. | `15s` |
| `controller.leaderElection.renewDeadline` | `KGW_LEADER_ELECTION_RENEW_DEADLINE` | The time that the leader keeps trying to renew its lease before it stops leading. This value must be greater than `retryPeriod` and less than `leaseDuration`. | `10s` |
| `controller.leaderElection.retryPeriod` | `KGW_LEADER_ELECTION_RETRY_PERIOD` | The time between attempts to acquire or renew the lease. | `2s` |


{{< /version >}}


## Namespace discovery {#namespace-discovery}

You can limit the namespaces that {{< reuse "/kgw-docs/snippets/kgateway.md" >}} watches for gateway configuration. For example, you might have a multi-tenant cluster with different namespaces for different tenants. You can limit {{< reuse "/kgw-docs/snippets/kgateway.md" >}} to only watch a specific namespace for gateway configuration.

Namespace selectors are a list of matched expressions or labels.

* `matchExpressions`: Use this field for more complex selectors where you want to specify an operator such as `In` or `NotIn`.
* `matchLabels`: Use this field for simple selectors where you want to specify a label key-value pair.

Each entry in the list is disjunctive (OR semantics). This means that a namespace is selected if it matches any selector.

You can also use matched expressions and labels together in the same entry, which is conjunctive (AND semantics).

The following example selects namespaces for discovery that meet either of the following conditions:

* The namespace has the label `environment=prod` and the label `version=v2`, or
* The namespace has the label `version=v3`

```yaml

discoveryNamespaceSelectors:
- matchExpressions:
  - key: environment
    operator: In
    values:
    - prod
  matchLabels:
    version: v2
- matchLabels:
    version: v3
```

{{< conditional-text include-if="envoy" >}}
{{< version exclude-if="2.1.x,2.2.x,2.3.x,2.4.x" >}}
## Scope xDS configuration per gateway {#xds-scoping}

> [!WARNING]
> The `REFERENCED` scoping mode is experimental and might change in future releases.

The control plane sends configuration to the gateway proxies over xDS. By default, every gateway proxy receives a cluster for every backend that the control plane discovers, even if no route of that Gateway uses it. In a cluster with many Services and few routed ones, each proxy carries a large config dump and reports stats for many clusters that it never uses.

### Enable xDS scoping

You can scope the xDS configuration so that each gateway's proxies receive only the clusters that the gateway's configuration references by using the `controller.xds.scoping` Helm values. These clusters include the backends that your routes send traffic to, and the backends that your policies call while the proxy processes a request. Examples are an external auth, external processing, or rate limit service, a server that hosts the JWKS for JWT validation, and a gRPC access log service. The proxies also receive the endpoints, listeners, and secrets that these backends need, such as the internal listener of an HTTP CONNECT tunnel. Scoping does not change the listeners and secrets that you configure on the Gateway, such as an HTTPS listener and its TLS certificate. The proxies always receive them.

1. Set the scoping mode in your Helm values file. The control plane supports the following scoping modes:
   * `ALL` (default): Every gateway proxy receives a cluster for every discovered backend, whether or not a route uses it.
   * `REFERENCED`: Each gateway's proxies receive only the clusters that the gateway's configuration references. A gateway whose routes select the destination at request time is not scoped and receives all clusters.

   The following example enables the `REFERENCED` mode.
   ```yaml
   controller:
     xds:
       scoping:
         mode: REFERENCED
   ```

   The Helm value sets the `KGW_XDS_SCOPING_MODE` environment variable on the control plane.

2. Upgrade your {{< reuse "kgw-docs/snippets/kgateway.md" >}} installation with the updated values file.
   ```sh
   helm upgrade -i -n {{< reuse "kgw-docs/snippets/namespace.md" >}} {{< reuse "/kgw-docs/snippets/helm-kgateway.md" >}} \
     oci://{{< reuse "/kgw-docs/snippets/helm-path.md" >}}/charts/{{< reuse "/kgw-docs/snippets/helm-kgateway.md" >}} \
     --version {{< reuse "kgw-docs/versions/helm-version-flag.md" >}} \
     -f values.yaml
   ```

### Monitor xDS scoping

The control plane reports the following metrics, each with the `gateway` and `namespace` labels, so that you can see how scoping affects each gateway. Note that scoping metrics are emitted only in `REFERENCED` mode. 

{{< table >}}
| Metric | Description |
| -- | -- |
| `kgateway_xds_snapshot_resources` (Gauge) | The number of resources that the control plane publishes to the gateway proxy. Filter for `resource="Cluster"` to see how many clusters the proxies receive after scoping. |
| `kgateway_xds_scoping_dropped_clusters` (Gauge) | The number of clusters that the control plane withholds from the gateway proxy, because the gateway's configuration references none of them. If a gateway has several groups of proxies, such as in different zones, the metric reports the most that any group withholds. |
| `kgateway_xds_scoping_disabled_gateways` (Gauge) | `1` if the gateway is not scoped and receives all clusters, because its routes select the destination at request time, such as through a header. The control plane cannot determine in advance which clusters the gateway needs. If a gateway has several groups of proxies, such as in different zones, `1` means that at least one group is not scoped. </br></br> The proxies of a gateway that is not scoped still receive all clusters, so scoping does not reduce their configuration or stats. Because the gateway keeps working, consider alerting on a value of `1` to find out when scoping stops applying to a gateway. If all gateways are scoped, the value is `0`.  |
| `kgateway_xds_scoping_transitions_total` (Counter) | The number of cluster transitions that the control plane delayed, such as when you add a route to a new backend or remove the last route to a backend. The `transition` label shows the kind of transition. For the label values, see [Tune cluster transitions](#xds-scoping-transitions). |
{{< /table >}}


You can access scoping metrics by querying the controller's metrics endpoint. 
```sh
kubectl get --raw \
  "/api/v1/namespaces/{{< reuse "kgw-docs/snippets/namespace.md" >}}/services/{{< reuse "/kgw-docs/snippets/helm-kgateway.md" >}}:9092/proxy/metrics" \
  | grep -E 'kgateway_xds_scoping|kgateway_xds_snapshot_resources.*Cluster'
```

Example output: 
```console
kgateway_xds_scoping_disabled_gateways{gateway="http",namespace="kgateway-system"} 0
kgateway_xds_scoping_dropped_clusters{gateway="http",namespace="kgateway-system"} 12
kgateway_xds_snapshot_resources{gateway="http",namespace="kgateway-system",resource="Cluster"} 2
```

In this example, the gateway proxies receive 2 clusters, and the control plane withholds 12 clusters. The `kgateway_xds_scoping_transitions_total` metric appears after you add or remove a route to a backend.

### Tune cluster transitions {#xds-scoping-transitions}

A transition is a change to the clusters that a gateway proxy receives. It happens when you add a route to a backend that is new to the gateway, or when you remove the last route to a backend. Envoy does not necessarily apply cluster updates before route updates, so the control plane delays one half of the change to reduce brief 503 errors.

* **Adding a route to a new backend**: The control plane sends the cluster first, and holds the route until the cluster had time to reach the proxy.
* **Removing the last route to a backend**: The control plane sends the route update first, and keeps the cluster for a while before it removes the cluster.

You can tune how long the control plane delays each half of a transition with the following settings. Set them in the `controller.xds.scoping` section of your Helm values file, or as environment variables on the control plane. The control plane counts transitions in the `kgateway_xds_scoping_transitions_total` metric, by the `transition` label.

| Helm value | Environment variable | Description | Default |
| -- | -- | -- | -- |
| `referenceAhead` | `KGW_XDS_SCOPING_REFERENCE_AHEAD` | How long the control plane holds routes, listeners, and secrets that name a cluster that is new to a proxy, so that the cluster reaches the proxy first. The metric counts each hold as `reference_ahead_held`. A hold also ends when the `KGW_PER_CLIENT_PUBLISH_BUDGET` time expires. For more information, see [Limit xDS publication delays](#xds-publication). | `2s` |
| `dereferenceGrace` | `KGW_XDS_SCOPING_DEREFERENCE_GRACE` | How long a cluster stays published after the control plane sends the route update that stops naming it, so that the update reaches the proxy first. The cluster of a deleted backend is removed at once. The metric counts a kept cluster as `dereference_graced`, and the removal of the cluster afterward as `dereference_pruned`. | `5s` |

Watch the rate of the `reference_ahead_held` transition. A high rate means that your route changes often add clusters that are new to the gateway, and each change waits for the `referenceAhead` time. If these waits delay your route changes more than you can accept, consider setting a lower `referenceAhead` time. A lower time increases the risk of brief 503 errors.

The `referenceAhead` hold is one of several delays that the control plane applies before it publishes configuration to a proxy. A separate time limit ends any delay that lasts too long. For more information, see [Limit xDS publication delays](#xds-publication).

## Limit xDS publication delays {#xds-publication}

The settings in this section apply whether or not you enable [xDS scoping](#xds-scoping). The control plane can delay sending configuration to a gateway proxy until the clusters that the configuration references are ready. A cluster is ready when the control plane has translated the cluster and its endpoints. The delay matters because the control plane can translate a route before it translates the cluster that the route points to. If the proxy received the route first, requests on that route would fail with a `503` response until the cluster arrived.

The control plane delays configuration in the following cases:

* **First configuration**: A gateway proxy connects to the control plane and requests its configuration for the first time, such as when a new gateway pod starts. The control plane waits so that the proxy starts with routes that work.
* **Route change**: You change a route so that it references a cluster that is not ready yet. The proxy keeps its current routes until the cluster is ready, while the new cluster and its endpoints still reach the proxy.

A cluster might never become ready, for example if a route references a Service that does not exist. To keep that cluster from blocking the proxy, the control plane limits how long each delay lasts. When the time limit expires, the control plane publishes the latest configuration. Requests on routes to the missing cluster return a `503` response until the cluster becomes ready.

### Tune the time limits {#xds-publication-settings}

You can tune the time limits with environment variables on the control plane. The control plane reads the variables at startup.

1. Set the environment variables in the `controller.extraEnv` section of your Helm values file. The following example sets a longer time limit for the first configuration of a proxy.
   ```yaml
   controller:
     extraEnv:
       KGW_PER_CLIENT_PUBLISH_BUDGET: "20s"
   ```

   | Environment variable | Description | Default |
   | -- | -- | -- |
   | `KGW_PER_CLIENT_PUBLISH_BUDGET` | How long the control plane delays the first configuration of a proxy, or a route change, while referenced clusters are not ready. Keep this value well below the startup probe time of the gateway proxy, which is 60 seconds by default. You can change the probe in the `spec.kube.podTemplate.startupProbe` field of the GatewayParameters resource. This value is not the total time until the proxy is ready. The total time also includes translation, the first connection delay that the `KGW_XDS_FIRST_CONNECT_DELAY` variable sets, and delivery to the proxy. If the first configuration arrives after the probe time, the proxy restarts. Set `0` to remove the time limit, so that the control plane delays the configuration until all referenced clusters are ready. With `0`, a new proxy that references a cluster that never becomes ready never receives configuration and never becomes ready. | `15s` |
   | `KGW_PER_CLIENT_WARM_WITHHOLD_BOUND` | How long the control plane continues to delay the configuration of a proxy that reconnects with configuration that it already has, such as after the control plane restarts, while referenced clusters are missing. This time starts after the `KGW_PER_CLIENT_PUBLISH_BUDGET` time expires. While the control plane delays the configuration, the proxy receives no updates at all, including certificate rotations. The value also limits how long the control plane keeps sending the last configuration of a cluster that is missing. Keep this value well above the time that the control plane needs to translate all resources after a restart. If the value is too low, routes fail each time the control plane restarts. Set `0` to remove the time limit. This setting has no effect if `KGW_PER_CLIENT_PUBLISH_BUDGET` is `0`. | `10m` |

2. Upgrade your {{< reuse "kgw-docs/snippets/kgateway.md" >}} installation with the updated values file. The `--reuse-values` setting re-applies any Helm values that you previously set.
   ```sh
   helm upgrade -i -n {{< reuse "kgw-docs/snippets/namespace.md" >}} {{< reuse "/kgw-docs/snippets/helm-kgateway.md" >}} \
     oci://{{< reuse "/kgw-docs/snippets/helm-path.md" >}}/charts/{{< reuse "/kgw-docs/snippets/helm-kgateway.md" >}} \
     --version {{< reuse "kgw-docs/versions/helm-version-flag.md" >}} \
     --reuse-values \
     -f values.yaml
   ```

3. Verify that the control plane runs with the new value. The upgrade restarts the control plane, so wait for the rollout to finish first. The command prints the value of the variable that you set, such as `20s`.
   ```sh
   kubectl -n {{< reuse "kgw-docs/snippets/namespace.md" >}} rollout status deployment/{{< reuse "/kgw-docs/snippets/helm-kgateway.md" >}}
   kubectl -n {{< reuse "kgw-docs/snippets/namespace.md" >}} get deployment {{< reuse "/kgw-docs/snippets/helm-kgateway.md" >}} \
     -o jsonpath='{.spec.template.spec.containers[*].env[?(@.name=="KGW_PER_CLIENT_PUBLISH_BUDGET")].value}'
   ```

### Monitor xDS publication {#xds-publication-metrics}

The control plane reports the following metrics so that you can monitor xDS publication in your cluster.

| Metric | Description |
| -- | -- |
| `kgateway_xds_snapshot_perclient_defers_total` (Counter) | The number of times that the control plane built configuration for a proxy while a referenced cluster was not ready. The `reason` label is `missing_clusters` or `missing_endpoints`. |
| `kgateway_xds_snapshot_perclient_withheld_clients` (Gauge) | The number of proxy groups where the first configuration is delayed. The `state` label is `within_budget` while the `KGW_PER_CLIENT_PUBLISH_BUDGET` time runs, and `warm_withheld` while the `KGW_PER_CLIENT_WARM_WITHHOLD_BOUND` time runs. The control plane reports no value for a state that has no delayed proxy groups, so the metric is missing when no configuration is delayed. |
| `kgateway_xds_snapshot_perclient_bounded_publishes_total` (Counter) | The number of times that the control plane published configuration because a time limit expired before all referenced clusters were ready. The `mode` label shows which delay ended: <ul><li>`first_publish`: The first configuration of a proxy.</li><li>`warm_truth`: The first configuration of a proxy that reconnected, when only the endpoints of referenced clusters were missing.</li><li>`warm_release`: The configuration of a proxy that reconnected, after the `KGW_PER_CLIENT_WARM_WITHHOLD_BOUND` time expired. Routes to the missing clusters fail until the clusters appear.</li><li>`flip_release`: A route change to a cluster that is not ready.</li><li>`carry_expired`: The control plane stopped sending the last configuration of a missing cluster after the `KGW_PER_CLIENT_WARM_WITHHOLD_BOUND` time expired. Routes to the cluster fail until the cluster appears.</li><li>`reference_ahead`: A hold for a cluster that is new to the proxy, in the `REFERENCED` scoping mode. For more information, see [Tune cluster transitions](#xds-scoping-transitions).</li></ul> |

A rising `kgateway_xds_snapshot_perclient_bounded_publishes_total` value means that routes reference clusters that do not become ready in time. To find these clusters, check the control plane logs for warnings such as `first-publish budget expired`. The warnings list the missing clusters.

To check the metrics, query the metrics endpoint of the control plane.

```sh
kubectl get --raw \
  "/api/v1/namespaces/{{< reuse "kgw-docs/snippets/namespace.md" >}}/services/{{< reuse "/kgw-docs/snippets/helm-kgateway.md" >}}:9092/proxy/metrics" \
  | grep kgateway_xds_snapshot_perclient
```

Example output after the control plane restarts:
```console
kgateway_xds_snapshot_perclient_defers_total{gateway="http",namespace="demo",reason="missing_endpoints"} 1
```

In this example, the control plane delayed the configuration of the `http` gateway once after the restart, until the control plane translated the endpoints of a referenced cluster. The control plane reports each metric only after the event that the metric counts happens for the first time. If the command returns no output, the control plane did not delay any configuration.

{{< /version >}}

## TLS encryption {#tls-encryption}

You can enable TLS encryption for the xDS gRPC server in the {{< reuse "kgw-docs/snippets/kgateway.md" >}} control plane. For more information, see the [TLS encryption]({{< link-hextra path="/install/tls" >}}) docs.
{{< /conditional-text >}}

## Resource validation

{{< reuse "kgw-docs/snippets/kgateway-capital.md" >}} supports two validation modes for routes and policies in the control plane: `standard` and `strict`. The validation mode controls how the control plane handles invalid configuration before it is sent to Envoy.

### Validation modes

{{< reuse "kgw-docs/snippets/kgateway-capital.md" >}} supports the following validation modes. The mode is set globally on the controller through a single Helm value.

| Mode | Behavior |
| --- | --- |
| `standard` (default) | The control plane translates all valid resources and replaces invalid routes with a direct response (typically `HTTP 500`). Valid routes that are unrelated to the invalid resource are unaffected. </br></br>The control plane does not run Envoy in this mode, so configuration that only Envoy can detect as invalid, such as an invalid RE2 regular expression in a route matcher, is still sent to the proxies. Envoy rejects (NACKs) that update and keeps serving the last route configuration that it accepted, so later route changes on the same listener are not applied until you fix the error. The routes keep reporting that they are accepted and programmed, so the resource statuses do not show the problem. To find out when Envoy rejects an update, [monitor NACKs]({{< link-hextra path="/observability/control-plane-metrics/#monitor-nacks" >}}). |
| `strict` | In addition to the `standard` checks, the control plane validates the generated configuration with Envoy before it sends the configuration to the proxies. Instead of sending invalid configuration, the control plane removes or replaces only the invalid parts, so that Envoy does not NACK the update and valid changes continue to be applied. For more information, see [How strict mode handles invalid configuration](#strict-invalid-configuration). |

> [!NOTE]
> The `standard` mode is the default resource validation mode and is appropriate for most production environments. Use `strict` mode when you cannot tolerate that a NACKed xDS update reaches the data plane. For example, use `strict` mode when one team's invalid route must not block configuration updates for other routes on the same listener. In exchange, the invalid route itself returns errors until you fix it, instead of continuing to serve its previous configuration. For more information, see [Invalid configuration handling in strict mode](#strict-invalid-configuration).

### Invalid configuration handling in strict mode {#strict-invalid-configuration}

Strict mode does not keep a previous version of a route when an update to the route is invalid. The control plane translates the current state of your resources, and handles invalid configuration as follows.

| Invalid configuration | Result | Status |
| --- | --- | --- |
| A route matcher, such as an invalid RE2 regular expression in a path, header, or query parameter match | The control plane removes the route rule. Requests that the rule matched are handled by the remaining routes, or receive an `HTTP 404` response if no other route matches. | {{< version exclude-if="2.1.x,2.2.x,2.3.x" >}}`kgateway.dev/Programmed=False`{{< /version >}}{{< version include-if="2.1.x,2.2.x,2.3.x" >}}`Accepted=False`{{< /version >}} with reason `RouteRuleDropped` on the route |
| Any other part of a route rule, such as a filter or policy setting that Envoy rejects | The control plane replaces the route rule with a direct `HTTP 500` response. | {{< version exclude-if="2.1.x,2.2.x,2.3.x" >}}`kgateway.dev/Programmed=False`{{< /version >}}{{< version include-if="2.1.x,2.2.x,2.3.x" >}}`Accepted=False`{{< /version >}} with reason `RouteRuleReplaced` on the route. If a policy setting fails validation, the policy resource also reports `Accepted=False` with reason `Invalid` and a message that describes the error. |{{< version exclude-if="2.1.x,2.2.x,2.3.x" >}}
| A virtual host that is still invalid after the control plane removes or replaces its invalid route rules | The control plane replaces all routes for the virtual host's domains with a direct `HTTP 500` response. | `Accepted=False` with reason `ListenerReplaced` on the listener |{{< /version >}}

For example, suppose that `route-a` and `route-b` are attached to the same listener, and you update `route-b` with an invalid regular expression in a path match. In `strict` mode, `route-a` continues to serve traffic, the invalid rule of `route-b` is removed so that its requests receive an `HTTP 404` response, and `route-b` reports the `RouteRuleDropped` reason. In `standard` mode, the invalid regular expression is sent to Envoy, which rejects the update. Both routes keep their previous configuration on the proxies that already accepted it, but no further route changes on that listener take effect until you fix `route-b`.

### Enable strict validation {#strict-validation}

Set the `validation.level` Helm value to `strict` when you install or upgrade kgateway. Restart the control plane to apply the change.

```yaml
validation:
  level: strict
```

Internally, the Helm chart passes the value to the control plane through the `KGW_VALIDATION_MODE` environment variable. If you manage the control plane deployment manually, set `KGW_VALIDATION_MODE=STRICT` on the kgateway container.

The accepted values for `validation.level` are `standard` and `strict` (case-insensitive). Any other value causes the Helm install to fail.

### Verify the validation mode

To check which mode is active, inspect the `KGW_VALIDATION_MODE` environment variable on the kgateway controller deployment. The expected output is `standard` or `strict`.

```sh
kubectl -n {{< reuse "kgw-docs/snippets/namespace.md" >}} get deployment {{< reuse "/kgw-docs/snippets/helm-kgateway.md" >}} \
  -o jsonpath='{.spec.template.spec.containers[*].env[?(@.name=="KGW_VALIDATION_MODE")].value}'
```

### Transformation policies and strict validation

Strict validation runs the preflight against an Envoy binary that is bundled in the kgateway control plane image. The control plane image is built from the envoy-wrapper image, which bundles the rustformation dynamic module, and the validator sets `ENVOY_DYNAMIC_MODULES_SEARCH_PATH=/usr/local/lib` before invoking the preflight. As a result, the preflight understands rustformation per-route config and can validate TrafficPolicies that use `transformation`.

For more information about transformation engines, see [Transformation engines]({{< link-hextra path="/traffic-management/transformations/engines/" >}}).

{{< version exclude-if="2.1.x,2.2.x,2.3.x,2.4.x" >}}
## Tune the controller Go memory limit {#controller-memory-limit}

By default, the Go runtime that the kgateway controller runs on does not know how much memory Kubernetes allows its container to use. The controller's garbage collector just runs on its own schedule, so the controller can keep allocating memory right up to the container's limit. When it crosses that limit, the Linux kernel kills the container immediately, with no warning and no chance for the controller to free memory first. This event appears as a Kubernetes pod restart, often labeled `OOMKilled`.

The `GOMEMLIMIT` environment variable fixes this issue by giving the Go runtime a soft memory ceiling. As the pod's memory usage approaches that ceiling, the garbage collector starts freeing up memory, so the controller can stay under the container's limit instead of being killed when it goes over.

By default, `controller.goMemLimitPercent` is set to `0`, which disables the Go memory limit feature. The Helm chart sets the `GOMEMLIMIT` environment variable when the controller pod starts by reading the `resources.limits.memory` on the associated Deployment. This limit is fixed throughout the pod's lifecycle. If the container's memory limit changes later, such as when a Kubernetes LimitRange resource is applied or a Vertical Pod Autoscaler (VPA) resizes the pod in place, `GOMEMLIMIT` does not follow that change until the pod restarts.

To adjust the `GOMEMLIMIT` variable dynamically, set the `controller.goMemLimitPercent` field to a value between `1` and `100`. This way, the `GOMEMLIMIT` environment variable is kept in sync with the container's memory limit as it changes. Instead of reading the memory limit once at startup, the controller reads the container's live memory limit directly from its cgroup every 30 seconds, and sets `GOMEMLIMIT` to the percentage you configure of that current value. A value of `90` is the recommended starting point. The controller targets 90% of the container's memory limit, leaving 10% as headroom for memory that the Go runtime does not track, such as memory that is used by Envoy subprocesses.

```yaml
controller:
  goMemLimitPercent: 90
```

| Field | Description |
| -- | -- |
| `controller.goMemLimitPercent` | Sets the percentage of the controller container's live memory limit that the Go runtime targets for `GOMEMLIMIT`. Valid values are `0`-`100`. The default value, `0`, sets `GOMEMLIMIT` once at pod startup from the container's memory limit and does not update it afterward. A value between `1` and `100` re-reads the container's live memory limit every 30 seconds and sets `GOMEMLIMIT` to that percentage of it. |

If you enable [strict validation](#strict-validation), use a lower value such as `80` because Envoy subprocess memory is not covered by `GOMEMLIMIT`. Do not set `controller.extraEnv.GOMEMLIMIT` or `controller.extraEnv.AUTOMEMLIMIT` with `controller.goMemLimitPercent`. If the controller container has no finite cgroup memory limit, `GOMEMLIMIT` remains unconstrained and the controller logs a warning.
{{< /version >}}

{{< version exclude-if="2.1.x,2.2.x">}}

## ReferenceGrant enforcement modes

In multi-tenant clusters, different teams typically own separate namespaces and share a gateway. The Gateway API [ReferenceGrant](https://gateway-api.sigs.k8s.io/reference/api-types/referencegrant/) mechanism controls which cross-namespace references are permitted, ensuring that one team cannot silently access another team's resources. Without a ReferenceGrant in the target namespace, the reference is denied.

In {{< reuse "kgw-docs/snippets/kgateway.md" >}}, you can configure how strictly you want ReferenceGrant requirements to be enforced by using the `KGW_REFERENCE_GRANT_MODE` environment variable on the control plane. You can choose between the following modes: 

- **`STRICT`**: Enforce ReferenceGrants for every cross-namespace reference in the [following table](#referencegrant-modes), including cross-namespace `ExtensionRef` references. This mode provides the strongest namespace isolation and is recommended for new clusters.
- **`PERMISSIVE`** (default): Enforce ReferenceGrants for every cross-namespace reference in the [following table](#referencegrant-modes) except cross-namespace `ExtensionRef` references. Before reference grant modes were introduced, {{< reuse "kgw-docs/snippets/trafficpolicy.md" >}} resources were able to reference and access a GatewayExtension resource in another namespace without a ReferenceGrant. `PERMISSIVE` mode allows these setups to function as before. Over time, you can add the missing ReferenceGrant resources in the required namespaces and migrate your cluster to `STRICT` ReferenceGrant validation. 
- **`OFF`**: Disable all ReferenceGrant validation. Not recommended for multi-tenant or production environments.
  > [!CAUTION]
  > Do not use `OFF` in multi-tenant or production environments. It breaks Gateway API compliance, bypasses namespace isolation, and lets any namespace access backends, secrets, and GatewayExtensions in other namespaces without restriction.

### Reference validation by mode {#referencegrant-modes}

The following table shows which cross-namespace references are checked in each mode. Same-namespace references always pass, regardless of the mode. 

| Source resource | Field | Referenced resource | `STRICT` | `PERMISSIVE` (default) | `OFF` |
|---|---|---|---|---|---|
| HTTPRoute / <br>GRPCRoute / <br>TCPRoute / <br>TLSRoute | `spec.rules[].backendRefs` | Service / Backend | checked | checked | allowed |
| HTTPRoute / <br>GRPCRoute | `spec.rules[].filters[].requestMirror.backendRef` | Service / Backend | checked | checked | allowed |
| Gateway / <br>ListenerSet | `spec.listeners[].tls.certificateRefs` | Secret | checked | checked | allowed |
| Gateway / <br>ListenerSet | `spec.listeners[].tls.frontendValidation.caCertificateRefs`, or `spec.default.clientCertificateValidation.caCertificateRefs` on a ListenerPolicy that targets the listener | Secret / ConfigMap | checked | checked | allowed |
| Gateway | `spec.backendTLS.clientCertificateRef` | Secret | checked | checked | allowed |
| GatewayExtension (ExtAuth, ExtProc, RateLimit) | `spec.<type>.grpcService.backendRef` | Service / Backend | checked | checked | allowed |
| GatewayExtension | `spec.extAuth.httpService.backendRef` | Service / Backend | checked | checked | allowed |
| GatewayExtension | `spec.oauth2.backendRef`{{< version exclude-if="2.1.x,2.2.x,2.3.x" >}} / <br>`spec.oauth2.jwt.jwksBackendRef`{{< /version >}} | Service / Backend | checked | checked | allowed |
| GatewayExtension | `spec.jwt.providers[].jwks.remote.backendRef` | Service / Backend | checked | checked | allowed |
| ListenerPolicy | `spec.default.httpSettings.accessLog[].grpcService.backendRef` / <br>`spec.default.httpSettings.accessLog[].openTelemetry.grpcService.backendRef` | Service / Backend | checked | checked | allowed |
| ListenerPolicy | `spec.default.httpSettings.tracing.provider.openTelemetry.grpcService.backendRef` | Service / Backend | checked | checked | allowed |{{% version exclude-if="2.1.x,2.2.x,2.3.x" %}}
| ListenerPolicy | `spec.default.httpSettings.localReplies.mappers[].headers.set[].secretRef` / <br>`spec.default.httpSettings.localReplies.mappers[].headers.add[].secretRef` | Secret | checked | checked | allowed |
| {{< reuse "kgw-docs/snippets/referencegrant-from-kind.md" >}}{{% downstream %}}*{{% /downstream %}} | `spec.headerModifiers.request.set[].secretRef` / <br>`spec.headerModifiers.request.add[].secretRef` / <br>`spec.headerModifiers.response.set[].secretRef` / <br>`spec.headerModifiers.response.add[].secretRef` | Secret | checked | checked | allowed |{{% /version %}}
| {{< reuse "kgw-docs/snippets/referencegrant-from-kind.md" >}}{{% downstream %}}*{{% /downstream %}} | `spec.basicAuth.secretRef` / <br>`spec.apiKeyAuth.secretRef` / <br>`spec.apiKeyAuth.secretSelector` | Secret | checked | checked | allowed |
| {{< reuse "kgw-docs/snippets/referencegrant-from-kind.md" >}}{{% downstream %}}*{{% /downstream %}} | `spec.<plugin>.extensionRef` | GatewayExtension (same namespace) | allowed | allowed | allowed |
| {{< reuse "kgw-docs/snippets/referencegrant-from-kind.md" >}}{{% downstream %}}*{{% /downstream %}} | `spec.<plugin>.extensionRef` | GatewayExtension (different namespace) | checked | allowed | allowed |
{{% downstream %}}| {{< reuse "kgw-docs/snippets/trafficpolicy.md" >}}† | `spec.entJWT.<stage>.providers.<name>.jwks.remote.backendRef` | Service / Backend | checked | checked | allowed |
| {{< reuse "kgw-docs/snippets/trafficpolicy.md" >}}† | `spec.entWAF.wafServerRef` | Service / Backend | checked | checked | allowed |
| {{< reuse "kgw-docs/snippets/trafficpolicy.md" >}}† | `spec.entGrpcJsonTranscoder.protoDescriptorConfigMap` | ConfigMap | checked | checked | allowed |
{{% /downstream %}}

{{% downstream %}}
\* Fields that the {{< reuse "kgw-docs/snippets/trafficpolicy.md" >}} inherits from the upstream TrafficPolicy API.

† Fields that are available only in the {{< reuse "kgw-docs/snippets/trafficpolicy.md" >}}.
{{% /downstream %}}

> [!IMPORTANT]
> In most cases, the **Source resource** column is the resource that you name in the `from` section of your ReferenceGrant. If you configure a CA certificate reference on a ListenerPolicy by using the `spec.default.clientCertificateValidation.caCertificateRefs` field, you must use the Gateway or ListenerSet that owns that listener in the `from` section of your ReferenceGrant and not the ListenerPolicy.
> {{< reuse "kgw-docs/snippets/referencegrant-policy-kind-note.md" >}}

### ReferenceGrant example {#referencegrant-example}

To reference resources across namespaces, create a ReferenceGrant in the namespace of the resource that you want to access, not in the namespace of the resource that makes the reference. The `from` section describes the resource that makes the reference, and the `to` section describes the resource it is allowed to reach. For more information about which resource to reference in each field, see [Reference validation by mode](#referencegrant-modes). 

The following example allows a policy in the `httpbin` namespace to read Secrets in the `team-secrets` namespace.

```yaml
kubectl apply -f- <<EOF
apiVersion: gateway.networking.k8s.io/v1beta1
kind: ReferenceGrant
metadata:
  name: allow-apikey-secrets
  # The namespace that holds the Secrets.
  namespace: team-secrets
spec:
  from:
  - group: {{< reuse "kgw-docs/snippets/referencegrant-from-group.md" >}}
    kind: {{< reuse "kgw-docs/snippets/referencegrant-from-kind.md" >}}
    # The namespace that holds the policy.
    namespace: httpbin
  to:
  - group: ""
    kind: Secret
EOF
```

To restrict the grant to a single Secret, add `name` to the `to` entry. When you omit `name`, every Secret in the namespace is allowed.

If a policy reports `missing reference grant`, check the following settings of your ReferenceGrant.

* The ReferenceGrant is in the namespace of the resource that you want to access, such as the namespace of the Secret.
* The `from` section matches the group, kind, and namespace of the resource that makes the reference. The API server accepts a ReferenceGrant with a group or kind that does not match, but that grant never matches the reference.
* The `to` section matches the group and kind of the resource that you want to access, and the `name`, if you set one.

### Enable STRICT mode {#set-referencegrant-mode}

1. Check which mode is currently active by inspecting the `KGW_REFERENCE_GRANT_MODE` environment variable on the controller deployment. If the variable is not set, the active mode is `PERMISSIVE`.
   ```sh
   kubectl -n {{< reuse "kgw-docs/snippets/namespace.md" >}} get deployment {{< reuse "kgw-docs/snippets/pod-name.md" >}} \
     -o jsonpath='{.spec.template.spec.containers[*].env[?(@.name=="KGW_REFERENCE_GRANT_MODE")].value}'
   ```

2. Make sure that any existing cross-namespace {{< reuse "kgw-docs/snippets/trafficpolicy.md" >}} → GatewayExtension references have a corresponding ReferenceGrant. 

3. Get the current Helm values for your {{< reuse "kgw-docs/snippets/kgateway.md" >}} release and save them to a file.

   ```sh
   helm get values {{< reuse "/kgw-docs/snippets/helm-kgateway.md" >}} -n {{< reuse "kgw-docs/snippets/namespace.md" >}} -o yaml > values.yaml
   open values.yaml
   ```

4. Add the following values to enable `STRICT` ReferenceGrant validation. 

   ```yaml
   controller:
     extraEnv:
       KGW_REFERENCE_GRANT_MODE: "STRICT"
   ```

5. Apply the change by upgrading the Helm release.

   ```sh
   helm upgrade -i -n {{< reuse "kgw-docs/snippets/namespace.md" >}} {{< reuse "/kgw-docs/snippets/helm-kgateway.md" >}} \
     oci://{{< reuse "/kgw-docs/snippets/helm-path.md" >}}/charts/{{< reuse "/kgw-docs/snippets/helm-kgateway.md" >}} \
     --version {{< reuse "kgw-docs/versions/helm-version-flag.md" >}} \
     -f values.yaml
   ```

6. Confirm that the {{< reuse "kgw-docs/snippets/kgateway.md" >}} control plane restarted and is running.

   ```sh
   kubectl get pods -n {{< reuse "kgw-docs/snippets/namespace.md" >}}
   ```

7. Verify the active mode.

   ```sh
   kubectl -n {{< reuse "kgw-docs/snippets/namespace.md" >}} get deployment {{< reuse "kgw-docs/snippets/pod-name.md" >}} \
     -o jsonpath='{.spec.template.spec.containers[*].env[?(@.name=="KGW_REFERENCE_GRANT_MODE")].value}'
   ```

{{< /version >}}

{{< version exclude-if="2.1.x,2.2.x,2.3.x" >}}

## Disable automatic RBAC creation {#disable-rbac}

By default, the {{< reuse "kgw-docs/snippets/kgateway.md" >}} Helm chart creates a `ClusterRole` and `ClusterRoleBinding` that grant the controller's service account the permissions it needs to watch and manage Kubernetes resources. In environments where RBAC resources are managed externally, such as by a platform or security team that controls all cluster-scoped permissions, you can disable the creation of these resources by setting `rbac.create: false`.

The `rbac.create` setting does not affect the ServiceAccount of the controller. The chart still creates the ServiceAccount, so that you can bind your own permissions to it. To skip the ServiceAccount too, set `serviceAccount.create: false`.

> [!CAUTION]
> If you disable the creation of ClusterRole and ClusterRoleBinding resources, you must create equivalent resources yourself before or alongside the {{< reuse "kgw-docs/snippets/kgateway.md" >}} installation. Without these resources, the controller cannot watch and manage Gateways, HTTPRoutes, Secrets, or other resources. 

To disable automatic RBAC creation, create the permissions yourself, and then turn off the chart's RBAC resources.

1. Render the ClusterRole and ClusterRoleBinding that the Helm chart creates by default. Use the output as the starting point for your own resources. The ClusterRole is in the `role.yaml` template, and the ClusterRoleBinding is in the `serviceaccount.yaml` template. The output also includes the ServiceAccount of the controller.

   ```sh
   helm template {{< reuse "/kgw-docs/snippets/helm-kgateway.md" >}} \
     oci://{{< reuse "/kgw-docs/snippets/helm-path.md" >}}/charts/{{< reuse "/kgw-docs/snippets/helm-kgateway.md" >}} \
     --version {{< reuse "kgw-docs/versions/n-patch.md" >}} \
     -n {{< reuse "kgw-docs/snippets/namespace.md" >}} {{< reuse "kgw-docs/snippets/helm-template-license-flag.md" >}} \
     --show-only templates/role.yaml \
     --show-only templates/serviceaccount.yaml {{< reuse "kgw-docs/snippets/helm-template-extra-templates.md" >}} > rbac.yaml
   ```

2. Open the `rbac.yaml` file and review the rules of the ClusterRole. Then remove the ServiceAccount resource from the file. This is the YAML document with `apiVersion: v1` and `kind: ServiceAccount`. The chart still creates the ServiceAccount, and a ServiceAccount that you create yourself with the same name conflicts with it. Keep the `serviceaccounts` rule in the ClusterRole and the ServiceAccount in the `subjects` of the ClusterRoleBinding.

3. If you upgrade an existing installation, change the names of the ClusterRole and ClusterRoleBinding resources in the file, and update the `roleRef` of each ClusterRoleBinding to use the new ClusterRole name. The upgrade in step 6 removes the ClusterRole and ClusterRoleBinding resources that the chart created earlier. It also removes any resource that has the same name as one of them.

4. Create the resources in your cluster.

   ```sh
   kubectl apply -f rbac.yaml
   ```

5. Add the `rbac.create` setting to your Helm values file.

   ```yaml
   rbac:
     create: false
   ```

6. Install or upgrade the Helm release with the values file.

   ```sh
   helm upgrade -i -n {{< reuse "kgw-docs/snippets/namespace.md" >}} {{< reuse "/kgw-docs/snippets/helm-kgateway.md" >}} \
     oci://{{< reuse "/kgw-docs/snippets/helm-path.md" >}}/charts/{{< reuse "/kgw-docs/snippets/helm-kgateway.md" >}} \
     --version {{< reuse "kgw-docs/versions/n-patch.md" >}} \
     -f values.yaml
   ```

7. Verify that the Helm release no longer includes a ClusterRole or ClusterRoleBinding. The command returns no output.

   ```sh
   helm get manifest {{< reuse "/kgw-docs/snippets/helm-kgateway.md" >}} -n {{< reuse "kgw-docs/snippets/namespace.md" >}} | grep -E "^kind: (ClusterRole|ClusterRoleBinding)$"
   ```

8. Verify that the control plane is running.

   ```sh
   kubectl get pods -n {{< reuse "kgw-docs/snippets/namespace.md" >}}
   ```

{{< reuse "kgw-docs/snippets/rbac-additional-components.md" >}}

{{< /version >}}
