Choose between the following options to customize the configuration of gateway proxies in {{< reuse "docs/snippets/kgateway.md" >}}.

| Option | Description |
| -- | -- |
| [Built-in configuration (recommended)](#built-in) | Use the built-in fields in the {{< reuse "docs/snippets/gatewayparameters.md" >}} resource. These fields are validated when you apply the resource.  |
| [Overlays](#overlays) | Use the strategic merge patch options in the {{< reuse "docs/snippets/gatewayparameters.md" >}} resource to modify the raw Kubernetes resources that the control plane generates, or to create additional resources such as Horizontal Pod Autoscalers, Vertical Pod Autoscalers, and Pod Disruption Budgets. Use this option for advanced customizations that are not covered by the built-in fields. |{{< conditional-text include-if="envoy" >}}
| [Self-managed gateways]({{< link-hextra path="/setup/customize/selfmanaged/" >}}) | If you want to change the [default gateway proxy template]({{< link-hextra path="/setup/default/#gateway-proxy-template" >}}) and provide your own Envoy configuration to bootstrap the proxy with, you must create a self-managed gateway. For more information, see [Self-managed gateways (BYO)]({{< link-hextra path="/setup/customize/selfmanaged/" >}}). |
{{< /conditional-text >}}

## Built-in customization (recommended) {#built-in}

The {{< reuse "docs/snippets/gatewayparameters.md" >}} resource comes with built-in customization options that you can use to change certain aspects of your gateway proxy, such as the container image, log level, resource requests and limits, or service type. These built-in config options are automatically validated when you apply the {{< reuse "docs/snippets/gatewayparameters.md" >}} resource.

Review the built-in configurations that are provided via the [{{< reuse "docs/snippets/gatewayparameters.md" >}}]({{< link-hextra path="/reference/api/#kubernetesproxyconfig" >}}) resource.

| Field | Description |
| -- | -- |
| `deployment` | Set the number of replicas and the update strategy for the proxy Deployment. If you use an HPA, do not set `replicas` here. |
| `envoyContainer` | Configure the Envoy container, including the image, application log format, bootstrap log level, component log levels, environment variables, resource requests and limits, and security context. |
| `sdsContainer` | Configure the Secret Discovery Service (SDS) sidecar container. |
| `podTemplate` | Configure pod-level settings, including image pull secrets, labels, annotations, node selector, affinity, tolerations, topology spread constraints, and the pod security context. |
| `service` | Configure the Kubernetes Service that exposes the proxy, including the type, ports, labels, annotations, and external traffic policy. |
| `serviceAccount` | Configure the ServiceAccount for the proxy pods. |
| `istio` | Configure the Istio integration for the proxy. |
| `stats` | Configure the stats server that exposes Prometheus metrics. |

{{< callout type="info" >}}
Use the built-in fields where possible. Built-in fields are validated at apply time, are considered stable, and are updated automatically when you upgrade your gateway proxies.
{{< /callout >}}

## Overlays {#overlays}

For advanced customization that is not covered by the built-in fields, the {{< reuse "docs/snippets/gatewayparameters.md" >}} resource supports overlays. Overlays use [Kubernetes strategic merge patch (SMP)](https://github.com/kubernetes/community/blob/master/contributors/devel/sig-api-machinery/strategic-merge-patch.md) semantics to modify the raw Kubernetes resources after the control plane renders them. You can also use overlays to create HorizontalPodAutoscaler (HPA), VerticalPodAutoscaler (VPA), and PodDisruptionBudget (PDB) resources that automatically target the proxy Deployment.

Review the following table for the resource types that you can overlay in the `spec.kube` field of your {{< reuse "docs/snippets/gatewayparameters.md" >}} resource.

| Field | Resource type | Description |
| -- | -- | -- |
| `deploymentOverlay` | Deployment | Modify the proxy Deployment after it is rendered. Common use cases include adding init containers or sidecars, configuring node scheduling settings, adding custom labels and annotations, and removing default security contexts. |
| `serviceOverlay` | Service | Modify the proxy Service. A common use case is adding cloud provider-specific annotations. |
| `serviceAccountOverlay` | ServiceAccount | Modify the proxy ServiceAccount. |
| `horizontalPodAutoscaler` | HorizontalPodAutoscaler | Create an HPA targeting the proxy Deployment. The HPA is created **only** when this field is present. |
| `verticalPodAutoscaler` | VerticalPodAutoscaler | Create a VPA targeting the proxy Deployment. The VPA is created **only** when this field is present. Requires the [VPA controller](https://github.com/kubernetes/autoscaler/tree/master/vertical-pod-autoscaler). |
| `podDisruptionBudget` | PodDisruptionBudget | Create a PDB targeting the proxy Deployment. The PDB is created **only** when this field is present. |

{{< callout type="warning" >}}
Overlays are **not validated** by the {{< reuse "docs/snippets/kgateway.md" >}} control plane at apply time. Configuration errors surface only when Kubernetes processes the resulting resource. The overlay schema reflects the underlying Kubernetes resource schema and is **not stable** between Kubernetes versions. Test overlay configurations after each cluster upgrade.
{{< /callout >}}

### How overlays work

Overlays are applied **after** the control plane renders the base Kubernetes resources. The control plane runs through the following steps:

1. The control plane reads built-in configuration from the {{< reuse "docs/snippets/gatewayparameters.md" >}} resource, such as `kube.deployment`, `kube.service`, and `kube.podTemplate`.
2. The control plane generates the base resources for the gateway proxy, including the Deployment, Service, and ServiceAccount.
3. The control plane applies any overlays that you specified in the {{< reuse "docs/snippets/gatewayparameters.md" >}} resource.
4. The control plane creates or updates the resources in the cluster.

### Remove or replace config

You can use overlays to remove configuration from the generated resources, such as the pod security context when working in OpenShift environments. The strategic merge patch supports the following methods:

**Set field value to null**

Set a field to a `null` value to remove it. You must use `kubectl apply --server-side` to apply the change. Without `--server-side`, the `null` value is silently dropped.

The following example removes the container-level `securityContext`:

```yaml

spec:
  kube:
    deploymentOverlay:
      spec:
        template:
          spec:
            containers:
              - name: kgateway
                # Removes the container-level securityContext
                securityContext: null
```

**Remove an entire field**

To remove an entire field, use `$patch: delete` instead.

The following example removes the pod-level `securityContext`:

```yaml

spec:
  kube:
    deploymentOverlay:
      spec:
        template:
          spec:
            # Removes the pod-level securityContext
            securityContext:
              $patch: delete
```

To replace a list rather than merging with it, add `$patch: replace` as a separate list item before your actual items:

```yaml

spec:
  kube:
    deploymentOverlay:
      spec:
        template:
          spec:
            volumes:
              - $patch: replace
              - name: custom-config
                configMap:
                  name: my-custom-config
```

For a step-by-step guide, see [Change proxy config]({{< link-hextra path="/setup/customize/gateway/" >}}).

## Configuration priority and precedence

You can attach a {{< reuse "docs/snippets/gatewayparameters.md" >}} resource to a GatewayClass that is shared by all Gateways that use that class or to an individual Gateway. When resources are attached at both levels, they are processed in the following order:

1. **Built-in configuration on the GatewayClass is applied first** – Built-in fields such as `kube.deployment`, `kube.service`, and `kube.podTemplate` from the GatewayClass {{< reuse "docs/snippets/gatewayparameters.md" >}} are applied first.
2. **Built-in configuration on the Gateway overrides the GatewayClass** – If the same built-in field is set on both the Gateway and the GatewayClass, the Gateway value takes precedence.
3. **Overlay configuration on the GatewayClass is applied** – After all built-in configuration is processed, the GatewayClass overlay fields are applied to the rendered resources.
4. **Overlay configuration on the Gateway overrides the GatewayClass** – If conflicting overlay configuration is specified on the Gateway, the configuration in the GatewayClass is overridden by using strategic merge patch semantics. Consider the following examples:
   - For scalar values, such as replicas, the Gateway configuration takes precedence.
   - For maps, such as labels, the label keys are merged. If both the Gateway and GatewayClass specify the same label key, the label key on the Gateway takes precedence.

**Example**

Consider the following GatewayClass configuration:

```yaml

spec:
  kube:
    deploymentOverlay:
      metadata:
        labels:
          level: gc
          gc-only-label: from-gc
```

Consider the following Gateway configuration:

```yaml

spec:
  kube:
    deploymentOverlay:
      metadata:
        labels:
          level: gw
          gw-only-label: from-gw
```

The resulting configuration merges both configurations as follows:

```yaml

metadata:
  labels:
    level: gw          # Gateway wins on conflicting key
    gc-only-label: from-gc   # GatewayClass key preserved
    gw-only-label: from-gw   # Gateway key added
```
