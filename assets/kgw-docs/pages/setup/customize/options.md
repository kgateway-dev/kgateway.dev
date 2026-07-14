Choose between the following options to customize the configuration of gateway proxies in {{< reuse "kgw-docs/snippets/kgateway.md" >}}.

| Option | Description |
| -- | -- |
| [Built-in configuration (recommended)](#built-in) | Use the built-in fields in the {{< reuse "kgw-docs/snippets/gatewayparameters.md" >}} resource. These fields are validated when you apply the resource.  |
| [Overlays](#overlays) | Use the strategic merge patch options in the {{< reuse "kgw-docs/snippets/gatewayparameters.md" >}} resource to modify the raw Kubernetes resources that the control plane generates, or to create additional resources such as Horizontal Pod Autoscalers, Vertical Pod Autoscalers, and Pod Disruption Budgets. Use this option for advanced customizations that are not covered by the built-in fields. |{{< conditional-text include-if="envoy" >}}
| {{< version include-if="2.1.x,2.2.x" >}}[Self-managed gateways]({{< link-hextra path="/setup/selfmanaged/" >}}){{< /version >}}{{< version exclude-if="2.1.x,2.2.x" >}}[Self-managed gateways]({{< link-hextra path="/setup/customize/selfmanaged/" >}}){{< /version >}} | If you want to change the [default gateway proxy template]({{< link-hextra path="/setup/default/#gateway-proxy-template" >}}) and provide your own Envoy configuration to bootstrap the proxy with, you must create a self-managed gateway. For more information, see {{< version include-if="2.1.x,2.2.x" >}}[Self-managed gateways (BYO)]({{< link-hextra path="/setup/selfmanaged/" >}}){{< /version >}}{{< version exclude-if="2.1.x,2.2.x" >}}[Self-managed gateways (BYO)]({{< link-hextra path="/setup/customize/selfmanaged/" >}}){{< /version >}}. |
{{< /conditional-text >}}

## Built-in customization (recommended) {#built-in}

The {{< reuse "kgw-docs/snippets/gatewayparameters.md" >}} resource comes with built-in customization options that you can use to change certain aspects of your gateway proxy, such as the container image, log level, resource requests and limits, or service type. These built-in config options are automatically validated when you apply the {{< reuse "kgw-docs/snippets/gatewayparameters.md" >}} resource.

Review the built-in configurations that are provided via the [{{< reuse "kgw-docs/snippets/gatewayparameters.md" >}}]({{< link-hextra path="/reference/api/#kubernetesproxyconfig" >}}) resource.

| Field | Description |
| -- | -- |
| `deployment` | Set the number of replicas and the update strategy for the proxy Deployment. If you use an HPA, do not set `replicas` here. |
| `envoyContainer` | Configure the Envoy container, including the image, application log format, bootstrap log level, component log levels, environment variables, resource requests and limits, and security context. |
| `sdsContainer` | Configure the Secret Discovery Service (SDS) sidecar container. |
| `podTemplate` | Configure pod-level settings, including image pull secrets, labels, annotations, node selector, affinity, tolerations, topology spread constraints, and the pod security context. |
| `service` | Configure the Kubernetes Service that exposes the proxy, including the type, ports, labels, annotations, and external traffic policy. |
| `serviceAccount` | Configure the ServiceAccount for the proxy pods. |
| `omitDefaultSecurityContext` | Prevent the control plane from adding its default pod and container security contexts. Enable this setting on platforms such as OpenShift that assign security contexts dynamically. |
| `istio` | Configure the Istio integration for the proxy. |
| `stats` | Configure the stats server that exposes Prometheus metrics, including enabling the stats endpoint, rewriting the stats route prefix, and [filtering which stats Envoy emits]({{< link-hextra path="/observability/gateway-metrics/#filter-stats" >}}). |

{{< callout type="info" >}}
Use the built-in fields where possible. Built-in fields are validated at apply time, are considered stable, and are updated automatically when you upgrade your gateway proxies.
{{< /callout >}}

## Overlays {#overlays}

For advanced customization that is not covered by the built-in fields, the {{< reuse "kgw-docs/snippets/gatewayparameters.md" >}} resource supports overlays. Overlays use [Kubernetes strategic merge patch (SMP)](https://github.com/kubernetes/community/blob/main/contributors/devel/sig-api-machinery/strategic-merge-patch.md) semantics to modify the raw Kubernetes resources after the control plane renders them. You can also use overlays to create HorizontalPodAutoscaler (HPA), VerticalPodAutoscaler (VPA), and PodDisruptionBudget (PDB) resources that automatically target the proxy Deployment.

Review the following table for the resource types that you can overlay in the `spec.kube` field of your {{< reuse "kgw-docs/snippets/gatewayparameters.md" >}} resource.

| Field | Resource type | Description |
| -- | -- | -- |
| `deploymentOverlay` | Deployment | Modify Deployment settings that do not have built-in fields, such as adding an init container or a generic sidecar. |
| `serviceOverlay` | Service | Modify Service settings that are not available in the built-in `service` field. |
| `serviceAccountOverlay` | ServiceAccount | Modify ServiceAccount settings that are not available in the built-in `serviceAccount` field. |
| `horizontalPodAutoscaler` | HorizontalPodAutoscaler | Create an HPA targeting the proxy Deployment. The HPA is created **only** when this field is present. |
| `verticalPodAutoscaler` | VerticalPodAutoscaler | Create a VPA targeting the proxy Deployment. The VPA is created **only** when this field is present. Requires the [VPA controller](https://github.com/kubernetes/autoscaler/tree/master/vertical-pod-autoscaler). |
| `podDisruptionBudget` | PodDisruptionBudget | Create a PDB targeting the proxy Deployment. The PDB is created **only** when this field is present. |

{{< callout type="warning" >}}
Overlays are **not validated** by the {{< reuse "kgw-docs/snippets/kgateway.md" >}} control plane at apply time. Configuration errors surface only when Kubernetes processes the resulting resource. The overlay schema reflects the underlying Kubernetes resource schema and is **not stable** between Kubernetes versions. Test overlay configurations after each cluster upgrade.
{{< /callout >}}

### How overlays work

Overlays are applied **after** the control plane renders the base Kubernetes resources. The control plane runs through the following steps:

1. The control plane reads built-in configuration from the {{< reuse "kgw-docs/snippets/gatewayparameters.md" >}} resource, such as `kube.deployment`, `kube.service`, and `kube.podTemplate`.
2. The control plane generates the base resources for the gateway proxy, including the Deployment, Service, and ServiceAccount.
3. The control plane applies any overlays that you specified in the {{< reuse "kgw-docs/snippets/gatewayparameters.md" >}} resource.
4. The control plane creates or updates the resources in the cluster.

### Strategic merge patch behavior

An overlay can replace scalar values, merge maps and lists, or remove generated configuration. Lists with a Kubernetes patch merge key are merged by that key. For example, `containers` and `initContainers` merge on `name`, so an item with a new name is appended and an item with an existing name updates that container. Maps merge by key, and values from an overlay replace conflicting generated values.

You can also explicitly delete or replace values that the control plane generated or an earlier overlay added.

**Delete a value with `null`**

Set a field to `null` to remove it. You must use `kubectl apply --server-side` to preserve the `null` value. With client-side apply, `kubectl` silently drops the value before it reaches the API server. The following overlay removes an advanced Deployment setting that was added by an earlier overlay.

```yaml

spec:
  kube:
    deploymentOverlay:
      spec:
        minReadySeconds: null
```

**Delete a field or list item with `$patch: delete`**

Use `$patch: delete` for consistent behavior with both client-side and server-side apply. The following overlay removes an init container named `wait-for-config` while preserving other init containers.

```yaml

spec:
  kube:
    deploymentOverlay:
      spec:
        template:
          spec:
            initContainers:
              - name: wait-for-config
                $patch: delete
```

**Replace a map with `$patch: replace`**

Add `$patch: replace` within a map to discard all existing keys in that map before adding the specified keys. The following overlay replaces an advanced DNS configuration instead of merging with it.

```yaml

spec:
  kube:
    deploymentOverlay:
      spec:
        template:
          spec:
            dnsConfig:
              $patch: replace
              options:
                - name: ndots
                  value: "1"
```

**Replace a list with `$patch: replace`**

To replace a list rather than merging it, add `$patch: replace` as a separate list item before the actual items. The following overlay replaces all init containers.

```yaml

spec:
  kube:
    deploymentOverlay:
      spec:
        template:
          spec:
            initContainers:
              - $patch: replace
              - name: initialize-gateway
                image: busybox:1.36
                command: ["sh", "-c", "echo initialization complete"]
```

{{< callout type="warning" >}}
Replacing a map or list discards values that the control plane generated. Verify the rendered resource to make sure that you did not remove configuration required by the gateway proxy.
{{< /callout >}}

For a step-by-step guide, see [Change proxy config]({{< link-hextra path="/setup/customize/gateway/" >}}).

## Configuration priority and precedence

You can attach a {{< reuse "kgw-docs/snippets/gatewayparameters.md" >}} resource to a GatewayClass that is shared by all Gateways that use that class or to an individual Gateway. When resources are attached at both levels, they are processed in the following order:

1. **Built-in configuration on the GatewayClass is applied first** – Built-in fields such as `kube.deployment`, `kube.service`, and `kube.podTemplate` from the GatewayClass {{< reuse "kgw-docs/snippets/gatewayparameters.md" >}} are applied first.
2. **Built-in configuration on the Gateway overrides the GatewayClass** – If the same built-in field is set on both the Gateway and the GatewayClass, the Gateway value takes precedence.
3. **Overlay configuration on the GatewayClass is applied** – After all built-in configuration is processed, the GatewayClass overlay fields are applied to the rendered resources.
4. **Overlay configuration on the Gateway overrides the GatewayClass** – If conflicting overlay configuration is specified on the Gateway, the configuration in the GatewayClass is overridden by using strategic merge patch semantics. Consider the following examples:
   - For scalar values, such as `dnsPolicy` in a Deployment overlay, the Gateway configuration takes precedence.
   - For maps, such as `dnsConfig`, keys from both levels are preserved unless the Gateway replaces the entire map.

**Example**

Consider the following GatewayClass configuration:

```yaml

spec:
  kube:
    deploymentOverlay:
      spec:
        template:
          spec:
            dnsPolicy: Default
            dnsConfig:
              nameservers:
                - 1.1.1.1
```

Consider the following Gateway configuration:

```yaml

spec:
  kube:
    deploymentOverlay:
      spec:
        template:
          spec:
            dnsPolicy: None
            dnsConfig:
              searches:
                - gateway.example
```

The resulting configuration merges both configurations as follows:

```yaml

spec:
  template:
    spec:
      dnsPolicy: None # Gateway scalar wins
      dnsConfig:
        nameservers:  # GatewayClass map key is preserved
          - 1.1.1.1
        searches:     # Gateway map key is added
          - gateway.example
```
