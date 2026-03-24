Use {{< reuse "docs/snippets/gatewayparameters.md" >}} overlays to apply advanced customizations to the Kubernetes resources that {{< reuse "docs/snippets/kgateway.md" >}} generates for your gateway proxies, such as Deployments, Services, and ServiceAccounts. Overlays use [Kubernetes strategic merge patch (SMP)](https://github.com/kubernetes/community/blob/master/contributors/devel/sig-api-machinery/strategic-merge-patch.md) semantics, and can also be used to create HorizontalPodAutoscalers (HPA), VerticalPodAutoscalers (VPA), and PodDisruptionBudgets (PDB) that automatically target the gateway proxy Deployment.

## Before you begin

{{< reuse "docs/snippets/prereq.md" >}}

## Overlay fields

The following overlay fields are available in `spec.kube` of the {{< reuse "docs/snippets/gatewayparameters.md" >}} resource.

| Field | Resource type | Description |
|-------|--------------|-------------|
| `deploymentOverlay` | Deployment | Apply a strategic merge patch to the generated proxy Deployment. Common use cases include adding initContainers or sidecars, configuring node selectors and affinities, adding custom labels and annotations, or removing default security contexts for OpenShift. |
| `serviceOverlay` | Service | Apply a strategic merge patch to the generated proxy Service. A common use case is adding cloud provider-specific annotations. |
| `serviceAccountOverlay` | ServiceAccount | Apply a strategic merge patch to the generated proxy ServiceAccount. |
| `horizontalPodAutoscaler` | HorizontalPodAutoscaler (HPA) | Create an HPA that automatically targets the proxy Deployment. The HPA is created **only** when this field is specified. |
| `verticalPodAutoscaler` | VerticalPodAutoscaler (VPA) | Create a VPA that automatically targets the proxy Deployment. The VPA is created **only** when this field is specified. Requires the [VPA controller](https://github.com/kubernetes/autoscaler/tree/master/vertical-pod-autoscaler) to be installed. |
| `podDisruptionBudget` | PodDisruptionBudget (PDB) | Create a PDB that automatically targets the proxy Deployment. The PDB is created **only** when this field is specified. |

{{< callout type="warning" >}}
Unlike built-in configuration options such as `kube.deployment` and `kube.service`, overlays are **not validated** by the {{< reuse "docs/snippets/kgateway.md" >}} control plane when you apply the {{< reuse "docs/snippets/gatewayparameters.md" >}} resource. The resulting resources, such as the Deployment, are validated by Kubernetes when they are created or updated.

Keep in mind that the overlay API reflects the underlying Kubernetes resource schema and is **not stable** between Kubernetes versions, which can lead to breaking changes after cluster upgrades. Use built-in configuration options where possible, and apply overlays only for customizations that are not covered by the built-in options.
{{< /callout >}}

## How overlays work

Overlays are applied **after** the control plane renders the base Kubernetes resources. The control plane processes resources in the following order:

1. **Built-in configuration in the GatewayClass** – Settings such as `kube.deployment`, `kube.service`, and `kube.podTemplate` are applied first.
2. **Built-in configuration in the Gateway** – If the Gateway references its own {{< reuse "docs/snippets/gatewayparameters.md" >}}, its built-in settings override any conflicting GatewayClass settings.
3. **Overlay configuration in the GatewayClass** – After all built-in configuration is processed, overlay fields defined on the GatewayClass {{< reuse "docs/snippets/gatewayparameters.md" >}} are applied.
4. **Overlay configuration in the Gateway** – If the Gateway specifies its own overlays, they are applied last using strategic merge patch semantics, overriding conflicting GatewayClass overlay values.

## Set up an overlay

The following example uses `deploymentOverlay` to add a custom label and an annotation to the gateway proxy Deployment.

1. Create a {{< reuse "docs/snippets/gatewayparameters.md" >}} resource with a `deploymentOverlay`.

   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: {{< reuse "docs/snippets/trafficpolicy-apiversion.md" >}}
   kind: {{< reuse "docs/snippets/gatewayparameters.md" >}}
   metadata:
     name: gw-params
     namespace: {{< reuse "docs/snippets/namespace.md" >}}
   spec:
     kube:
       deploymentOverlay:
         metadata:
           labels:
             environment: production
             team: platform
           annotations:
             prometheus.io/scrape: "true"
             prometheus.io/port: "9091"
   EOF
   ```

2. Create a Gateway that references your {{< reuse "docs/snippets/gatewayparameters.md" >}}.

   ```yaml
   kubectl apply -f- <<EOF
   kind: Gateway
   apiVersion: gateway.networking.k8s.io/v1
   metadata:
     name: custom
     namespace: {{< reuse "docs/snippets/namespace.md" >}}
   spec:
     gatewayClassName: {{< reuse "docs/snippets/gatewayclass.md" >}}
     infrastructure:
       parametersRef:
         name: gw-params
         group: {{< reuse "docs/snippets/trafficpolicy-group.md" >}}
         kind: {{< reuse "docs/snippets/gatewayparameters.md" >}}
     listeners:
     - protocol: HTTP
       port: 80
       name: http
       allowedRoutes:
         namespaces:
           from: All
   EOF
   ```

3. Verify that the Deployment for the gateway proxy has the labels and annotations that you specified.

   ```sh
   kubectl get deployment custom -n {{< reuse "docs/snippets/namespace.md" >}} -o jsonpath='{.metadata.labels}' | jq
   kubectl get deployment custom -n {{< reuse "docs/snippets/namespace.md" >}} -o jsonpath='{.metadata.annotations}' | jq
   ```

## Remove or replace configuration

Overlays can also remove configuration from the generated resources. This is useful for platforms such as OpenShift where the default security context must be removed.

### Set field value to null

Set a field to `null` to remove it. Use `kubectl apply --server-side` to ensure that `null` values are sent to the API server and not silently dropped.

The following example removes the container-level security context from the proxy Deployment:

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

### Remove a field entirely

Use `$patch: delete` to remove a field entirely, including in environments where `null` cannot be applied.

The following example removes the pod-level security context:

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

To replace a list instead of merging with it, add `$patch: replace` as a separate list item:

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

{{< callout type="warning" >}}
Place `$patch: replace` as a separate list item **before** your actual items. If you include it in the same item as your configuration, you might end up with an empty list.
{{< /callout >}}

## Next

[Explore common overlay configurations]({{< link-hextra path="/setup/customize/configs/" >}}) such as HPA, VPA, PDB, and extension overlays.

## Cleanup

{{< reuse "docs/snippets/cleanup.md" >}}

```sh
kubectl delete gateway custom -n {{< reuse "docs/snippets/namespace.md" >}}
kubectl delete {{< reuse "docs/snippets/gatewayparameters.md" >}} gw-params -n {{< reuse "docs/snippets/namespace.md" >}}
```
