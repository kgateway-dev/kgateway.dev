Inject custom Envoy bootstrap configuration into a managed gateway proxy by overriding the bootstrap ConfigMap that the control plane generates with overlays. 

Use this technique to set bootstrap-level Envoy options that are not exposed as built-in fields on the {{< reuse "kgw-docs/snippets/gatewayparameters.md" >}} resource, such as the [`stats_config.histogram_bucket_settings`](https://www.envoyproxy.io/docs/envoy/latest/api-v3/config/metrics/v3/stats.proto#envoy-v3-api-msg-config-metrics-v3-statsconfig) to tune histogram bucket boundaries for your metrics.

> [!WARNING]
> This is an advanced workaround. Prefer the [built-in customization fields]({{< link-hextra path="/setup/customize/options/#built-in" >}}) whenever they cover your use case, because they are validated at apply time and updated automatically when you upgrade. A custom bootstrap ConfigMap is **not** validated by the control plane and is **not** updated automatically on upgrade. You must keep it in sync with the generated bootstrap format yourself.

## How it works

For a managed gateway proxy, the control plane generates a ConfigMap that is named after the Gateway and holds the Envoy bootstrap as an `envoy.yaml` entry. The proxy pod mounts this ConfigMap on the `/etc/envoy` path by using a volume that is named `envoy-config`. The Envoy container is started from the bootstrap configuration.

To inject your own bootstrap configuration while the control plane continues to manage routing through xDS, you can follow these general steps: 

1. Get the ConfigMap that is automatically generated to extract the default bootstrap configuration.
2. Customize the bootstrap configuration to your needs and store it in your own ConfigMap. 
3. Use a `deploymentOverlay` in the {{< reuse "kgw-docs/snippets/gatewayparameters.md" >}} resource to point the `envoy-config` volume at your custom ConfigMap. Volumes merge on the `name` key under [strategic merge patch](https://kubernetes.io/docs/tasks/manage-kubernetes-objects/update-api-object-kubectl-patch/), so the overlay updates the existing volume rather than adding a new one.

Because you start from a copy of the generated bootstrap, the proxy keeps its control-plane–managed configuration, such as the `node` identity, `xds_cluster`, xDS token, and `dynamic_resources`, and continues to connect to the control plane.

> [!WARNING]
> Do not change the control-plane–managed sections of the bootstrap configuration, including the `node`, `dynamic_resources`, `xds_cluster`, and `xds_service_account_token.json` entries. Changing these sections breaks the connection between the gateway proxy and the control plane. Make sure to add or change only the fields that you need, such as `stats_config`.

## Before you begin

{{< reuse "kgw-docs/snippets/prereq.md" >}}

## Override the bootstrap config

1. Deploy a Gateway and a {{< reuse "kgw-docs/snippets/gatewayparameters.md" >}} resource so that the control plane generates the bootstrap ConfigMap.

   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: {{< reuse "kgw-docs/snippets/gatewayparam-apiversion.md" >}}
   kind: {{< reuse "kgw-docs/snippets/gatewayparameters.md" >}}
   metadata:
     name: gw-params
     namespace: {{< reuse "kgw-docs/snippets/namespace.md" >}}
   spec:
     kube:
       deployment:
         replicas: 1
   ---
   kind: Gateway
   apiVersion: gateway.networking.k8s.io/v1
   metadata:
     name: custom
     namespace: {{< reuse "kgw-docs/snippets/namespace.md" >}}
   spec:
     gatewayClassName: {{< reuse "kgw-docs/snippets/gatewayclass.md" >}}
     infrastructure:
       parametersRef:
         name: gw-params
         group: {{< reuse "kgw-docs/snippets/gatewayparam-group.md" >}}
         kind: {{< reuse "kgw-docs/snippets/gatewayparameters.md" >}}
     listeners:
     - protocol: HTTP
       port: 80
       name: http
       allowedRoutes:
         namespaces:
           from: All
   EOF
   ```

2. Get the ConfigMap that contains the Envoy bootstrap configuration and save it in a local file. 
   ```sh
   kubectl get configmap custom -n {{< reuse "kgw-docs/snippets/namespace.md" >}} -o yaml > custom-bootstrap.yaml
   ```

3. Make the following changes to your ConfigMap. 
   1. Change the `metadata.name` field to a custom name, such as `custom-bootstrap`. You must create the ConfigMap under a different name to avoid automatic overwrites of the ConfigMap by the managed proxy. 
   2. Find the Envoy bootstrap configuration in the `envoy.yaml` entry and customize it to your needs. The following example adds a `stats_config` block with custom histogram bucket boundaries (in milliseconds) for cluster stats. Add the block as a new top-level key. Make sure to leave all the existing keys of your Envoy bootstrap configuration unchanged.
      ```yaml
      stats_config:
        histogram_bucket_settings:
        - match:
            prefix: "cluster."
          buckets: [1, 5, 10, 25, 50, 100, 250, 500, 1000, 2500, 5000, 10000]
      ```

      > [!TIP]
      > If you prefer to extract only the Envoy bootstrap configuration for easier updating, run the following command. Make sure to apply your customizations to the `envoy.yaml` section of your ConfigMap.
      > ```sh
      > kubectl get configmap custom -n {{< reuse "kgw-docs/snippets/namespace.md" >}} \
      > -o jsonpath='{.data.envoy\.yaml}' > envoy.yaml
      >
      > open envoy.yaml
      > ```
  
   3. Apply the new ConfigMap. 
      ```sh
      kubectl apply -f custom-bootstrap.yaml
      ```
   
4. Add a `deploymentOverlay` to the {{< reuse "kgw-docs/snippets/gatewayparameters.md" >}} resource to point the `envoy-config` volume at your custom ConfigMap.

   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: {{< reuse "kgw-docs/snippets/gatewayparam-apiversion.md" >}}
   kind: {{< reuse "kgw-docs/snippets/gatewayparameters.md" >}}
   metadata:
     name: gw-params
     namespace: {{< reuse "kgw-docs/snippets/namespace.md" >}}
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

5. Verify that the gateway proxy is restarted. 
   ```sh
   kubectl get pods -n {{< reuse "kgw-docs/snippets/namespace.md" >}} | grep custom
   ```

6. Port-forward the gateway proxy on port 19000 to access the admin interface. 

   ```sh
   kubectl port-forward -n {{< reuse "kgw-docs/snippets/namespace.md" >}} deploy/custom 19000:19000
   ```

7. Get the `histogram_bucket_settings` of your proxy config dump to verify that your custom settings are applied. 

   ```sh
   curl -s localhost:19000/config_dump | grep -A25 histogram_bucket_settings
   ```

   Example output:

   ```console
   "histogram_bucket_settings": [
    {
     "match": {
      "prefix": "cluster."
     },
     "buckets": [
      1,
      5,
      10,
      25,
      50,
      100,
      250,
      500,
      1000,
      2500,
      5000,
      10000
     ]
    }
   ]
   ```

## Keep your custom bootstrap up to date

When you upgrade {{< reuse "kgw-docs/snippets/kgateway.md" >}}, the generated bootstrap format can change to add new fields, clusters, or listeners. Because your custom ConfigMap is a copy, it does not pick up these changes automatically. After each upgrade, regenerate the bootstrap from a proxy that uses the default configuration, re-apply your customization, and update your custom ConfigMap.

To avoid this maintenance, use the [built-in customization fields]({{< link-hextra path="/setup/customize/options/#built-in" >}}) where possible, and open a [feature request](https://github.com/kgateway-dev/kgateway/issues) if you need a built-in field for your bootstrap setting. 

## Cleanup

{{< reuse "kgw-docs/snippets/cleanup.md" >}}

```sh
kubectl delete gateway custom -n {{< reuse "kgw-docs/snippets/namespace.md" >}}
kubectl delete {{< reuse "kgw-docs/snippets/gatewayparameters.md" >}} gw-params -n {{< reuse "kgw-docs/snippets/namespace.md" >}}
kubectl delete configmap custom-bootstrap -n {{< reuse "kgw-docs/snippets/namespace.md" >}}
```
