Review additional configuration options for using {{< reuse "/kgw-docs/snippets/kgateway.md" >}} as the ingress gateway in an Istio ambient mesh.

## Cluster draining weights {#cluster-draining}

{{< reuse "/kgw-docs/snippets/kgateway.md" >}} honors the `solo.io/draining-weight` annotation on east-west and remote peering gateways when routing ingress traffic to a multicluster ambient mesh. Previously, the draining weight was respected by ztunnel and waypoints for east-west traffic, but {{< reuse "/kgw-docs/snippets/kgateway.md" >}} continued to send ingress traffic to a draining cluster, resulting in connection errors.

When a remote cluster's east-west gateway is annotated with `solo.io/draining-weight`, {{< reuse "/kgw-docs/snippets/kgateway.md" >}} adjusts the Envoy load balancing weights for that cluster's endpoints on the ingress path:

| Draining mode | Annotation value | Traffic to remote cluster |
|---|---|---|
| Off (default) | `solo.io/draining-weight: "0"` or absent | 100% |
| Partial | `solo.io/draining-weight: "40"` | 60% (100% minus the draining weight) |
| Full | `solo.io/draining-weight: "100"` | 0% (cluster excluded from Envoy endpoint set) |

## Exclude ServiceEntries from discovery {#exclude-serviceentries}

You can exclude specific Istio ServiceEntry resources from the gateway's backend and endpoint discovery by using Kubernetes label selectors. To enable this feature, set the `serviceEntriesExclusionLabelSelectors` Helm value to a list of selectors. Any ServiceEntry that matches a selector is ignored during the backend and endpoint discovery phase.

A ServiceEntry is excluded if it matches any entry in the list (`OR` condition). Within each entry, all `matchLabels` and `matchExpressions` conditions must hold for the ServiceEntry to be excluded (`AND` condition). Empty entries are rejected to prevent excluding all ServiceEntries.

The following example shows multiple `matchLabel` entries. ServiceEntries are excluded if they have both `example.io/source: generated` and `example.io/source-kind: ExternalService` labels (`AND` condition), or the `env: staging` label (`OR` condition).

```yaml
serviceEntriesExclusionLabelSelectors:
  # Exclude entries that have both labels (AND within an entry)
  - matchLabels:
      example.io/source: generated
      example.io/source-kind: ExternalService
  # Also exclude entries in staging (OR across entries)
  - matchLabels:
      env: staging
```

## Exclude WorkloadEntries from discovery {#exclude-workloadentries}

When a ServiceEntry has a `workloadSelector`, {{< reuse "kgw-docs/snippets/kgateway.md" >}} adds every WorkloadEntry with matching labels as an endpoint of that ServiceEntry, so that the gateway can route traffic to it.

Sometimes a WorkloadEntry that matches the selector is not a real backend. For example, it might represent the address of another gateway or proxy. To stop the gateway from sending traffic to it, exclude the WorkloadEntry from endpoint discovery.

To exclude WorkloadEntries, set the `KGW_WORKLOAD_ENTRIES_EXCLUSION_LABELS` environment variable on the {{< reuse "kgw-docs/snippets/kgateway.md" >}} control plane to a comma-separated list of label keys. By default, no WorkloadEntries are excluded. This setting applies only if the [Istio integration]({{< link-hextra path="/integrations/istio/ambient/ambient-ingress/#step-1-enable-the-istio-integration" >}}) is enabled.

```yaml
controller:
  extraEnv:
    KGW_WORKLOAD_ENTRIES_EXCLUSION_LABELS: "example.io/source-kind,example.io/infrastructure"
```

Note the following behavior:

* A WorkloadEntry is excluded if it has any of the label keys that you list, regardless of the value of the label. For example, if you list the `example.io/infrastructure` key, a WorkloadEntry with the label `example.io/infrastructure: "false"` is also excluded.
* The label keys are checked in both the `metadata.labels` and the `spec.labels` fields of the WorkloadEntry.
* An excluded WorkloadEntry is not used as an endpoint for any ServiceEntry that the gateway discovers. The WorkloadEntry itself is not changed or deleted, so other components, such as Istio, can still use it.

To exclude entire ServiceEntry resources, or to match label values, use the [`serviceEntriesExclusionLabelSelectors` Helm value](#exclude-serviceentries) instead.
