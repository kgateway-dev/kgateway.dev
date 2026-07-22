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
