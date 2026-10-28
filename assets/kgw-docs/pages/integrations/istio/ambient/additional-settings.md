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

{{% version exclude-if="2.0.x,2.1.x,2.2.x,2.3.x,2.4.x" %}}
## Migrate from kgateway waypoints {#migrate-from-kgateway-waypoints}

Support for running {{< reuse "/kgw-docs/snippets/kgateway.md" >}} as an Istio ambient waypoint is removed. Move each kgateway waypoint to an Istio waypoint before you upgrade.

After the upgrade, the {{< reuse "/kgw-docs/snippets/kgateway.md" >}} control plane does not reconcile the `kgateway-waypoint` GatewayClass, any GatewayClass with the `ambient.istio.io/waypoint-inbound-binding` annotation, or the Gateways that use these GatewayClasses. These resources are not migrated or deleted:

* The GatewayClass and its Gateways stay in the cluster, but their status is no longer updated. A stale `Accepted=True` or `Programmed=True` condition does not mean that the waypoint works.
* The Deployments and Services of the waypoints stay in the cluster and keep the previous proxy image.
* A running waypoint proxy keeps the configuration that it last received. A waypoint pod that restarts, such as after an eviction or a node drain, gets no configuration, and traffic through it fails.

The control plane ClusterRole keeps the `get`, `list`, and `watch` permissions on `authorizationpolicies.security.istio.io` for one more release, so that pods of the previous version keep their access during the upgrade. If you maintain a custom ClusterRole, you can remove this rule in the next minor release.

Repeat the following steps for each kgateway waypoint. The ztunnel moves a workload to the new waypoint as soon as its `istio.io/use-waypoint` label changes. You can move one namespace or Service at a time.

1. Create an Istio waypoint next to the kgateway waypoint, with a different name. The following example creates an Istio waypoint in the `httpbin` namespace. Wait until the Gateway has the `Programmed=True` condition.
   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.networking.k8s.io/v1
   kind: Gateway
   metadata:
     name: httpbin-istio-waypoint
     namespace: httpbin
   spec:
     gatewayClassName: istio-waypoint
     listeners:
     - name: mesh
       port: 15008
       protocol: HBONE
   EOF
   ```

2. Change every resource that refers to the kgateway waypoint so that it refers to the Istio waypoint.
   * **HTTPRoutes and GRPCRoutes** that have the kgateway waypoint Gateway as a `parentRef`. Routes with a Service or ServiceEntry as the `parentRef` do not need a change.
   * **AuthorizationPolicies** with `targetRefs` that refer to the kgateway waypoint Gateway. Change AuthorizationPolicies that target the `kgateway-waypoint` GatewayClass to target the `istio-waypoint` GatewayClass in the mesh root namespace. Istio waypoints enforce AuthorizationPolicies with their own implementation, so test policies with `CUSTOM` actions or uncommon match fields in step 4.
   * **{{< reuse "/kgw-docs/snippets/kgateway.md" >}} policies**, such as TrafficPolicies, that target the kgateway waypoint or its routes. Istio waypoints do not apply {{< reuse "/kgw-docs/snippets/kgateway.md" >}} policies. Configure the same behavior with Istio APIs instead, or remove the policies.

3. Change the `istio.io/use-waypoint` label on each namespace, Service, or ServiceEntry that used the kgateway waypoint to the name of the Istio waypoint.
   ```sh
   kubectl label namespace httpbin istio.io/use-waypoint=httpbin-istio-waypoint --overwrite
   ```

4. Verify the Istio waypoint before you delete anything.
   * Send requests to the moved Services. Check that the requests succeed and go through the Istio waypoint, such as in the access logs of the waypoint or with the `istioctl ztunnel-config workloads` command.
   * Check that your AuthorizationPolicies allow and deny the same requests as before.
   * Check that no resource still refers to the kgateway waypoint Gateway.

5. Delete the kgateway waypoint Gateway. When no Gateway uses the `kgateway-waypoint` GatewayClass, delete the GatewayClass too. The control plane does not create it again.

## Send ingress traffic through Istio waypoints {#ingress-use-waypoint}

You can send the ingress traffic for a Service through the Istio waypoint of that Service. The policies and telemetry of the waypoint then apply to the ingress traffic too. With this integration enabled, the gateway proxy sends the traffic for a backend to the cluster IP of its Service, not to its pods. Then, the ztunnel passes the traffic through the waypoint.

The gateway proxy uses the waypoint only when the following conditions are true:

* The pods of the gateway proxy are in the ambient mesh. A gateway proxy outside the mesh keeps sending traffic straight to the pods.
* The backend has an Istio waypoint, attached with the `istio.io/use-waypoint` label.
* The Service or ServiceEntry, or its namespace, has the `istio.io/ingress-use-waypoint=true` label.
* The Service has a cluster IP. A headless Service (`clusterIP: None`) has no cluster IP, so requests to it fail with a `503` response and the `UH` response flag. Do not add the label to a headless Service.
* For a ServiceEntry, the [Istio integration]({{< link-hextra path="/integrations/istio/ambient/ambient-ingress/#step-1-enable-the-istio-integration" >}}) is enabled with `KGW_ENABLE_ISTIO_INTEGRATION=true`. Without it, ServiceEntries are not used as backends.

1. Enable the integration in the Helm values of your {{< reuse "/kgw-docs/snippets/kgateway.md" >}} installation, and upgrade the release.
   ```yaml
   waypoint:
     enabled: true
   ```

   | Setting | Description |
   | -- | -- |
   | `waypoint.enabled` | Sends ingress traffic through the Istio waypoint of each labeled backend. The default value is `false`. If you do not use Helm, set the `KGW_INGRESS_USE_WAYPOINTS=true` environment variable on the control plane instead. A `KGW_INGRESS_USE_WAYPOINTS` value in `controller.extraEnv` overrides `waypoint.enabled`. The deprecated `KGW_ENABLE_WAYPOINT=true` setting still enables the integration when `KGW_INGRESS_USE_WAYPOINTS` is not set. |

2. Add the namespace of the gateway proxy to the ambient mesh.
   ```sh
   kubectl label ns {{< reuse "kgw-docs/snippets/namespace.md" >}} istio.io/dataplane-mode=ambient --overwrite
   ```

3. Attach an Istio waypoint to the namespace, Service, or ServiceEntry of the backend. The following example attaches the `httpbin-istio-waypoint` waypoint to the `httpbin` namespace.
   ```sh
   kubectl label namespace httpbin istio.io/use-waypoint=httpbin-istio-waypoint --overwrite
   ```

4. Label the backend so that the gateway proxy sends its ingress traffic through the waypoint. Do not label a headless Service.
   ```sh
   kubectl label service httpbin -n httpbin istio.io/ingress-use-waypoint=true --overwrite
   ```

To stop sending the ingress traffic of a backend through its waypoint, remove the label.

```sh
kubectl label service httpbin -n httpbin istio.io/ingress-use-waypoint-
```
{{% /version %}}
