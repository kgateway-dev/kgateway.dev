---
title: Upgrade
weight: 20
description: Upgrade the control plane and any gateway proxies that run in your cluster. 
---

You can use this guide to upgrade the version of your kgateway components, or to apply changes to the components’ configuration settings.

<!-- TODO upgrade guide when we have a minor version
## Considerations
Consider the following rules before you plan your kgateway upgrade.

### Testing upgrades

During the upgrade, pods that run the new version of the control plane and proxies are created. Then, the old pods are terminated. Because zero downtime is not guaranteed, try testing the upgrade in a staging environment before upgrading your production environment.

### Patch and minor versions

**Patch version upgrades**: </br>
- You can skip patch versions within the same minor release. For example, you can upgrade from version {{< reuse "docs/versions/short.md" >}}.0 to {{< reuse "docs/versions/n-patch.md" >}} directly, and skip the patch versions in between.

**Minor version upgrades**: </br>
- Before you upgrade the minor version, always upgrade your _current_ minor version to the latest patch. This ensures that your current environment is up-to-date with any bug fixes or security patches before you begin the minor version upgrade process.
- Always upgrade to the latest patch version of the target minor release. Do not upgrade to a lower patch version, such as {{< reuse "docs/versions/short.md" >}}.0, {{< reuse "docs/versions/short.md" >}}.1, and so on.
- Do not skip minor versions during your upgrade. Upgrade minor release versions one at a time. 

## Step 1: Prepare to upgrade

1. **Minor version upgrades**: Before you upgrade to a new minor version, first upgrade your _current_ minor version to the latest patch.
   1. Find the latest patch of your minor version by checking the [release changelog](https://github.com/kgateway-dev/kgateway/releases).
   2. Follow this upgrade guide to upgrade to the latest patch for your current minor version.
   3. Then, you can repeat the steps in this guide to upgrade to the latest patch of the next minor version.

2. Check that your underlying infrastructure platform, such as Kubernetes, and other dependencies run supported versions for the kgateway version that you want to upgrade to.
   1. Review the [supported versions](/docs/reference/versions/) for dependencies such as Kubernetes, Istio, Helm, and more.
   2. Compare the supported version against the versions that you currently use. 
   3. If necessary, upgrade your dependencies, such as consulting your cluster infrastructure provider to upgrade the version of Kubernetes that your cluster runs.

3. Set the version to upgrade kgateway to in an environment variable, such as the latest patch version (`{{< reuse "docs/versions/n-patch.md" >}}`) .
   ```sh
   export NEW_VERSION={{< reuse "docs/versions/n-patch.md" >}}
   ```

## Step 2: Upgrade the CLI

1. Upgrade `{{< reuse "docs/snippets/cli-name.md" >}}` to the new version. Note that this command only updates the CLI binary version, and does not upgrade your kgateway installation.
   ```shell
   {{< reuse "docs/snippets/cli-name.md" >}} upgrade --release v${NEW_VERSION}
   ```

2. Verify that the **client** version matches the version you installed.
   ```shell
   {{< reuse "docs/snippets/cli-name.md" >}} version
   ```

   Example output:
   ```json
   {
   "client": {
     "version": "{{< reuse "docs/versions/n-patch.md" >}}"
   },
   ```

## Step 3: Upgrade kgateway

-->

## Prepare to upgrade {#prepare}

Before you upgrade kgateway, review the following information.

1. Review the [release notes](https://github.com/kgateway-dev/kgateway/releases) for any breaking changes or new features that you need to be aware of.

2. Check the [supported version compatibility matrix](/docs/reference/versions/#supported-versions). If the version of kgateway that you are upgrading to requires a different version of Kubernetes, the {{< reuse "docs/snippets/k8s-gateway-api-name.md" >}}, or Istio, upgrade those technologies accordingly.

   {{< tabs items="Kubernetes Gateway API, Kubernetes, Istio" >}}
{{% tab %}}
1. Decide on the {{< reuse "docs/snippets/k8s-gateway-api-name.md" >}} version that you want to use. For help, review the [Upgrade Notes in the {{< reuse "docs/snippets/k8s-gateway-api-name.md" >}} docs](https://gateway-api.sigs.k8s.io/guides/#v12-upgrade-notes). In particular, check if you need to install the experimental channel, which is required for the following features.
   
   * BackendTLSPolicy to configure TLS settings for the connection between a gateway and a backend workload.
   * CORS policies for HTTPRoutes.
   * ListenerSets to configure listeners separately from the Gateway.
   * TCPRoutes to set up a TCP listener on your Gateway.

2. Install the custom resources of the {{< reuse "docs/snippets/k8s-gateway-api-name.md" >}} version that you want to upgrade to, such as the standard {{< reuse "docs/versions/k8s-gw-version.md" >}} version.
   
   * Standard channel:
     
     ```sh
     kubectl apply -f https://github.com/kubernetes-sigs/gateway-api/releases/download/v{{< reuse "docs/versions/k8s-gw-version.md" >}}/standard-install.yaml
     ```
   
   * Experimental channel:
     
     ```sh
     kubectl apply -f https://github.com/kubernetes-sigs/gateway-api/releases/download/v{{< reuse "docs/versions/k8s-gw-version.md" >}}/experimental-install.yaml
     ```   

   Example output: 
   
   ```txt
   customresourcedefinition.apiextensions.k8s.io/gatewayclasses.gateway.networking.k8s.io created
   customresourcedefinition.apiextensions.k8s.io/gateways.gateway.networking.k8s.io created
   customresourcedefinition.apiextensions.k8s.io/httproutes.gateway.networking.k8s.io created
   customresourcedefinition.apiextensions.k8s.io/referencegrants.gateway.networking.k8s.io created
   customresourcedefinition.apiextensions.k8s.io/grpcroutes.gateway.networking.k8s.io created
   ```

3. Check the {{< reuse "docs/snippets/k8s-gateway-api-name.md" >}} CRDs. Remove any outdated CRDs.

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
{{% tab %}}
For Kubernetes upgrades, consult your cloud infrastructure provider.
{{% /tab %}}
{{% tab %}}
For Istio upgrades, consult the docs based on the way that you installed Istio. Example providers:

* [Upstream Istio](https://istio.io/latest/docs/setup/upgrade/)
* [Gloo Mesh Enterprise](https://docs.solo.io/gloo-mesh-enterprise/latest/istio/upgrade/)

{{% /tab %}}
   {{< /tabs >}}

## Upgrade kgateway {#kgateway}

1. Set the version to upgrade kgateway in an environment variable, such as the latest patch version (`{{< reuse "docs/versions/n-patch.md" >}}`) .
   
   ```sh
   export NEW_VERSION={{< reuse "docs/versions/n-patch.md" >}}
   ```

2. Apply the kgateway CRDs for the upgrade version by using Helm.

   ```sh
   helm upgrade -i --namespace kgateway-system --version v$NEW_VERSION kgateway-crds oci://cr.kgateway.dev/kgateway-dev/charts/kgateway-crds
   ```

3. Make any changes to your Helm values.
   
   1. Get the Helm values file for your current version.
      
      ```sh
      helm get values kgateway -n kgateway-system -o yaml > kgateway.yaml
      open kgateway.yaml
      ```

   2. Compare your current Helm chart values with the version that you want to upgrade to. You can get a values file for the upgrade version by pulling and inspecting the Helm chart locally.
      
      ```sh
      helm pull oci://cr.kgateway.dev/kgateway-dev/charts/kgateway --version v$NEW_VERSION
      tar -xvf kgateway-v$NEW_VERSION.tgz
      open kgateway/values.yaml
      ```

   3. Make any changes that you want by editing your `kgateway.yaml` Helm values file or preparing the `--set` flags.

4. Upgrade the kgateway Helm installation.
   {{< callout type="warning" >}}
   Make sure to include your Helm values when you upgrade either as a configuration file or with <code>--set</code> flags. Otherwise, any previous custom values that you set might be overwritten.
   {{< /callout >}}
   
   ```sh
   helm upgrade -i -n kgateway-system kgateway oci://cr.kgateway.dev/kgateway-dev/charts/kgateway \
     -f kgateway.yaml \
     --version v$NEW_VERSION
   ```
   
5. Verify that kgateway runs the upgraded version.
   
   ```sh
   kubectl -n kgateway-system get pod -l kgateway=kgateway -ojsonpath='{.items[0].spec.containers[0].image}'
   ```
   
   Example output:
   ```
   cr.kgateway.dev/kgateway-dev/kgateway:{{< reuse "docs/versions/n-patch.md" >}}
   ```

6. Confirm that the kgateway control plane is up and running. 
   
   ```sh
   kubectl get pods -n kgateway-system
   ```
