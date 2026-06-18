Inject custom Envoy bootstrap configuration into a managed gateway proxy by overriding the bootstrap ConfigMap that the control plane generates with overlays. 

Use this technique to set bootstrap-level Envoy options that are not exposed as built-in fields on the {{< reuse "docs/snippets/gatewayparameters.md" >}} resource, such as the [`stats_config.histogram_bucket_settings`](https://www.envoyproxy.io/docs/envoy/latest/api-v3/config/metrics/v3/stats.proto#envoy-v3-api-msg-config-metrics-v3-statsconfig) to tune histogram bucket boundaries for your metrics.

{{< callout type="warning" >}}
This is an advanced workaround. Prefer the [built-in customization fields]({{< link-hextra path="/setup/customize/options/#built-in" >}}) whenever they cover your use case, because they are validated at apply time and updated automatically when you upgrade. A custom bootstrap ConfigMap is **not** validated by the control plane and is **not** updated automatically on upgrade. You must keep it in sync with the generated bootstrap format yourself. If you need to change the entire proxy template, use a [self-managed gateway]({{< link-hextra path="/setup/customize/selfmanaged/" >}}) instead.
{{< /callout >}}

## How it works

For a managed gateway proxy, the control plane generates a ConfigMap that is named after the Gateway and holds the Envoy bootstrap as an `envoy.yaml` entry. The proxy pod mounts this ConfigMap on the `/etc/envoy` path by using a volume that is named `envoy-config`. The Envoy container is started from the bootstrap configuration.

To inject your own bootstrap configuration while the control plane continues to manage routing through xDS, you can follow these general steps: 

1. Get the ConfigMap that is automatically generated to extract the default bootstrap configuration.
2. Customize the bootstrap configuration to your needs and store it in your own ConfigMap. 
3. Use a `deploymentOverlay` in the {{< reuse "docs/snippets/gatewayparameters.md" >}} resource to point the `envoy-config` volume at your custom ConfigMap. Volumes merge on the `name` key under [strategic merge patch](https://kubernetes.io/docs/tasks/manage-kubernetes-objects/update-api-object-kubectl-patch/), so the overlay updates the existing volume rather than adding a new one.

Because you start from a copy of the generated bootstrap, the proxy keeps its control-plane–managed configuration, such as the `node` identity, the `xds_cluster`, the xDS token, and `dynamic_resources`, and continues to connect to the control plane.

{{< callout type="warning" >}}
Do not change the control-plane–managed sections of the bootstrap configuration, including the `node`, `dynamic_resources`, `xds_cluster`, and `xds_service_account_token.json` entries. Changing these sections breaks the connection between the gateway proxy and the control plane. Make sure to add or change only the fields that you need, such as `stats_config`.
{{< /callout >}}

## Before you begin

{{< reuse "docs/snippets/prereq.md" >}}

## Override the bootstrap config

1. Deploy a Gateway and a {{< reuse "docs/snippets/gatewayparameters.md" >}} resource so that the control plane generates the bootstrap ConfigMap.

   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: {{< reuse "docs/snippets/trafficpolicy-apiversion.md" >}}
   kind: {{< reuse "docs/snippets/gatewayparameters.md" >}}
   metadata:
     name: gw-params
     namespace: {{< reuse "docs/snippets/namespace.md" >}}
   spec:
     kube:
       deployment:
         replicas: 1
   ---
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

2. Get the generated bootstrap and save the `envoy.yaml` entry to a file. This is the bootstrap you customize in the next step.

   ```sh
   kubectl get configmap custom -n {{< reuse "docs/snippets/namespace.md" >}} \
     -o jsonpath='{.data.envoy\.yaml}' > envoy.yaml
   ```

3. Edit `envoy.yaml` to add your customization. The following example adds a `stats_config` block with custom histogram bucket boundaries (in milliseconds) for cluster stats. Add the block as a new top-level key; leave all the existing keys unchanged.

   ```yaml
   stats_config:
     histogram_bucket_settings:
     - match:
         prefix: "cluster."
       buckets: [1, 5, 10, 25, 50, 100, 250, 500, 1000, 2500, 5000, 10000]
   ```

4. Create your own ConfigMap from the edited bootstrap. Copy the other entries from the generated ConfigMap too, such as `xds_service_account_token.json`, so that the proxy still authenticates to the control plane.

   ```sh
   kubectl get configmap custom -n {{< reuse "docs/snippets/namespace.md" >}} -o yaml > custom-bootstrap.yaml
   # In custom-bootstrap.yaml: rename metadata.name to "custom-bootstrap",
   # remove the owner references and resourceVersion, and replace the
   # data.envoy.yaml value with your edited envoy.yaml from step 3.
   kubectl apply -f custom-bootstrap.yaml
   ```

5. Add a `deploymentOverlay` to the {{< reuse "docs/snippets/gatewayparameters.md" >}} resource to repoint the `envoy-config` volume at your custom ConfigMap.

   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: {{< reuse "docs/snippets/trafficpolicy-apiversion.md" >}}
   kind: {{< reuse "docs/snippets/gatewayparameters.md" >}}
   metadata:
     name: gw-params
     namespace: {{< reuse "docs/snippets/namespace.md" >}}
   spec:
     kube:
       deployment:
         replicas: 1
       deploymentOverlay:
         spec:
           template:
             spec:
               volumes:
               # Merge key is 'name'; this patches the existing envoy-config volume
               - name: envoy-config
                 configMap:
                   name: custom-bootstrap
   EOF
   ```

   The control plane re-renders the Deployment and rolls out a new proxy pod that mounts your custom ConfigMap.

6. Verify that the running proxy uses your custom histogram buckets. Open a port-forward to the Envoy admin port and check the bootstrap in the config dump.

   ```sh
   kubectl port-forward -n {{< reuse "docs/snippets/namespace.md" >}} deploy/custom 19000:19000
   ```

   In a separate terminal, query the config dump:

   ```sh
   curl -s localhost:19000/config_dump | grep -A6 histogram_bucket_settings
   ```

   Example output:

   ```json
   "histogram_bucket_settings": [
    {
     "match": { "prefix": "cluster." },
     "buckets": [1, 5, 10, 25, 50, 100, 250, 500, 1000, 2500, 5000, 10000]
    }
   ]
   ```

## Keep your custom bootstrap up to date

When you upgrade {{< reuse "docs/snippets/kgateway.md" >}}, the generated bootstrap format can change to add new fields, clusters, or listeners. Because your custom ConfigMap is a copy, it does not pick up these changes automatically. After each upgrade, regenerate the bootstrap from a proxy that uses the default configuration, re-apply your customization, and update your custom ConfigMap.

To avoid this maintenance, use the [built-in customization fields]({{< link-hextra path="/setup/customize/options/#built-in" >}}) where possible, and open a [feature request](https://github.com/kgateway-dev/kgateway/issues) if you need a built-in field for your bootstrap setting.

## Cleanup

{{< reuse "docs/snippets/cleanup.md" >}}

```sh
kubectl delete gateway custom -n {{< reuse "docs/snippets/namespace.md" >}}
kubectl delete {{< reuse "docs/snippets/gatewayparameters.md" >}} gw-params -n {{< reuse "docs/snippets/namespace.md" >}}
kubectl delete configmap custom-bootstrap -n {{< reuse "docs/snippets/namespace.md" >}}
```
