You can use this guide to upgrade the {{< reuse "/kgw-docs/snippets/kgateway.md" >}} control plane and data plane components, or to apply changes to the components' configuration settings.

## Considerations

Consider the following rules before you plan your kgateway upgrade.

### Testing upgrades

During the upgrade, pods that run the new version of the control plane and proxies are created. Then, the old pods are terminated. Because zero downtime is not guaranteed, try testing the upgrade in a staging environment before upgrading your production environment.

### Patch and minor versions

**Patch version upgrades**: <br>
- You can skip patch versions within the same minor release. For example, you can upgrade from version {{< reuse "kgw-docs/versions/short.md" >}}.0 to {{< reuse "kgw-docs/versions/n-patch.md" >}} directly, and skip the patch versions in between.

**Minor version upgrades**: <br>
- Before you upgrade the minor version, always upgrade your _current_ minor version to the latest patch. This ensures that your current environment is up-to-date with any bug fixes or security patches before you begin the minor version upgrade process.
- Always upgrade to the latest patch version of the target minor release. Do not upgrade to a lower patch version, such as {{< reuse "kgw-docs/versions/short.md" >}}.0, {{< reuse "kgw-docs/versions/short.md" >}}.1, and so on.
- Do not skip minor versions during your upgrade. Upgrade minor release versions one at a time. 

## Prepare to upgrade {#prepare}

Before you upgrade {{< reuse "/kgw-docs/snippets/kgateway.md" >}}, review the following information.

1. Review the [kgateway release notes](https://github.com/kgateway-dev/kgateway/releases) for any breaking changes or new features that you need to be aware of.

2. Check the [supported version compatibility matrix](../../reference/versions/#released-versions). If the version of {{< reuse "/kgw-docs/snippets/kgateway.md" >}} that you are upgrading to requires a different version of Kubernetes, the {{< reuse "kgw-docs/snippets/k8s-gateway-api-name.md" >}}, or Istio, upgrade those technologies accordingly.

{{< conditional-text include-if="envoy" >}}

   {{< tabs >}}
{{% tab name="Kubernetes Gateway API" %}}
1. Decide on the {{< reuse "kgw-docs/snippets/k8s-gateway-api-name.md" >}} version that you want to use. 

   * For help, review the [Upgrade Notes in the {{< reuse "kgw-docs/snippets/k8s-gateway-api-name.md" >}} docs for each version](https://gateway-api.sigs.k8s.io/guides/getting-started/#v12-upgrade-notes).
{{< version exclude-if="2.0.x,2.1.x" >}}   * Check if you need to install the [experimental channel for the features that you want to use](../../reference/feature-maturity/#experimental-features).{{< /version >}}

2. Install the custom resources of the {{< reuse "kgw-docs/snippets/k8s-gateway-api-name.md" >}} version that you want to upgrade to, such as the standard {{< reuse "kgw-docs/versions/k8s-gw-version.md" >}} version.
   
   * Standard channel:
     
     ```sh
     kubectl apply -f https://github.com/kubernetes-sigs/gateway-api/releases/download/v{{< reuse "kgw-docs/versions/k8s-gw-version.md" >}}/standard-install.yaml
     ```
   
   * Experimental channel: Note that some CRDs are prefixed with `X` to indicate that the entire CRD is experimental and subject to change.
     
     ```sh
     kubectl apply -f https://github.com/kubernetes-sigs/gateway-api/releases/download/v{{< reuse "kgw-docs/versions/k8s-gw-version.md" >}}/experimental-install.yaml
     ```   

   Example output: 
   
   ```txt
   customresourcedefinition.apiextensions.k8s.io/gatewayclasses.gateway.networking.k8s.io created
   customresourcedefinition.apiextensions.k8s.io/gateways.gateway.networking.k8s.io created
   customresourcedefinition.apiextensions.k8s.io/httproutes.gateway.networking.k8s.io created
   customresourcedefinition.apiextensions.k8s.io/referencegrants.gateway.networking.k8s.io created
   customresourcedefinition.apiextensions.k8s.io/grpcroutes.gateway.networking.k8s.io created
   ```

3. Check the {{< reuse "kgw-docs/snippets/k8s-gateway-api-name.md" >}} CRDs. Remove any outdated CRDs.

   ```sh
   kubectl get crds -o jsonpath='{range .items[*]}{.metadata.name}{"\t"}{.spec.versions[*].name}{"\t"}{.metadata.annotations.gateway\.networking\.k8s\.io/bundle-version}{"\t"}{.metadata.annotations.gateway\.networking\.k8s\.io/channel}{"\n"}{end}' | grep gateway.networking.k8s.io
   ```

   Example output:
   
   ```txt
   gatewayclasses.gateway.networking.k8s.io  v1 v1beta1  v1.2.0	experimental
   gateways.gateway.networking.k8s.io        v1 v1beta1  v1.2.0	experimental
   grpcroutes.gateway.networking.k8s.io      v1          v1.2.0	experimental
   httproutes.gateway.networking.k8s.io      v1 v1beta1  v1.2.0	experimental
   ```
{{% /tab %}}
{{% tab name="Kubernetes" %}}
For Kubernetes upgrades, consult your cloud infrastructure provider.
{{% /tab %}}
{{% tab name="Istio" %}}
For Istio upgrades, consult the docs based on the way that you installed Istio. Example providers:

* [Upstream Istio](https://istio.io/latest/docs/setup/upgrade/)
* [Gloo Operator](https://docs.solo.io/gloo-mesh-enterprise/latest/istio/operator/upgrade/)
* [Gloo Mesh Helm](https://docs.solo.io/gloo-mesh-enterprise/latest/istio/manual/upgrade/)

{{% /tab %}}
   {{< /tabs >}}

{{< /conditional-text >}}




## Upgrade {#upgrade-steps}

1. Set the version you want to upgrade to in an environment variable, such as the latest patch version (`{{< reuse "kgw-docs/versions/n-patch.md" >}}`) .
   
   ```sh
   export NEW_VERSION={{< reuse "kgw-docs/versions/n-patch.md" >}}
   ```

2. Apply the new CRDs for the control and data plane by using Helm.

   1. **Optional**: To check the CRDs locally, download the CRDs to a `helm` directory.

      ```sh
      helm template --version {{< reuse "kgw-docs/versions/helm-version-upgrade.md" >}} {{< reuse "/kgw-docs/snippets/helm-kgateway-crds.md" >}} oci://{{< reuse "/kgw-docs/snippets/helm-path.md" >}}/charts/{{< reuse "/kgw-docs/snippets/helm-kgateway-crds.md" >}} --output-dir ./helm
      ```

   2. Upgrade the CRDs in your cluster:

      ```sh
      helm upgrade -i --namespace {{< reuse "kgw-docs/snippets/namespace.md" >}} --version {{< reuse "kgw-docs/versions/helm-version-upgrade.md" >}} {{< reuse "/kgw-docs/snippets/helm-kgateway-crds.md" >}} oci://{{< reuse "/kgw-docs/snippets/helm-path.md" >}}/charts/{{< reuse "/kgw-docs/snippets/helm-kgateway-crds.md" >}}
      ```

3. Make any changes to your Helm values.
   
   1. Get the Helm values file for your current version.
      
      ```sh
      helm get values {{< reuse "/kgw-docs/snippets/helm-kgateway.md" >}} -n {{< reuse "kgw-docs/snippets/namespace.md" >}} -o yaml > values.yaml
      open values.yaml
      ```

   2. Compare your current Helm chart values with the version that you want to upgrade to. 
   
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

   3. Make any changes that you want by editing your `values.yaml` Helm values file or preparing the `--set` flags. For development v{{< reuse "kgw-docs/versions/patch-dev.md" >}} builds, include the `controller.image.pullPolicy=Always` setting or refer to the exact image digest to avoid using cached images.

4. Upgrade the {{< reuse "kgw-docs/snippets/kgateway.md" >}} control plane Helm installation.
   * Make sure to include your Helm values when you upgrade either as a configuration file or with `--set` flags. Otherwise, any previous custom values that you set might be overwritten.
   * When using the development build v{{< reuse "kgw-docs/versions/patch-dev.md" >}}, add the `--set controller.image.pullPolicy=Always` option to ensure you get the latest image. Alternatively, you can specify the exact image digest.
   
   ```sh
   helm upgrade -i -n {{< reuse "kgw-docs/snippets/namespace.md" >}} {{< reuse "/kgw-docs/snippets/helm-kgateway.md" >}} oci://{{< reuse "/kgw-docs/snippets/helm-path.md" >}}/charts/{{< reuse "/kgw-docs/snippets/helm-kgateway.md" >}} \
     -f values.yaml \
     --version {{< reuse "kgw-docs/versions/helm-version-upgrade.md" >}} 
   ```
   
5. Verify that the control plane runs the upgraded version.
   
   ```sh
   kubectl -n {{< reuse "kgw-docs/snippets/namespace.md" >}} get pod -l app.kubernetes.io/name={{< reuse "/kgw-docs/snippets/helm-kgateway.md" >}} -o jsonpath='{.items[0].spec.containers[0].image}'
   ```
   
   Example output:
   ```
   cr.{{< reuse "kgw-docs/snippets/kgateway.md" >}}.dev/controller:{{< reuse "kgw-docs/versions/n-patch.md" >}}
   ```

6. Confirm that the control plane is up and running. 
   
   ```sh
   kubectl get pods -n {{< reuse "kgw-docs/snippets/namespace.md" >}}
   ```

