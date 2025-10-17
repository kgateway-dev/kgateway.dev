---
title: Helm
weight: 5
description: Install kgateway and related components.
---

In this installation guide, you install {{< reuse "/docs/snippets/kgateway.md" >}} in a Kubernetes cluster by using [Helm](https://helm.sh/). Helm is a popular package manager for Kubernetes configuration files. This approach is flexible for adopting to your own command line, continuous delivery, or other workflows.

## Before you begin

1. Create or use an existing Kubernetes cluster. 
2. Install the following command-line tools.
   * [`kubectl`](https://kubernetes.io/docs/tasks/tools/#kubectl), the Kubernetes command line tool. Download the `kubectl` version that is within one minor version of the Kubernetes clusters you plan to use.
   * [`helm`](https://helm.sh/docs/intro/install/), the Kubernetes package manager.

## Install

Install {{< reuse "/docs/snippets/kgateway.md" >}} by using Helm.

1. Install the custom resources of the {{< reuse "docs/snippets/k8s-gateway-api-name.md" >}} version {{< reuse "docs/versions/k8s-gw-version.md" >}}.
   
   ```sh
   kubectl apply -f https://github.com/kubernetes-sigs/gateway-api/releases/download/v{{< reuse "docs/versions/k8s-gw-version.md" >}}/standard-install.yaml
   ```
   Example output: 
   ```console
   customresourcedefinition.apiextensions.k8s.io/gatewayclasses.gateway.networking.k8s.io created
   customresourcedefinition.apiextensions.k8s.io/gateways.gateway.networking.k8s.io created
   customresourcedefinition.apiextensions.k8s.io/httproutes.gateway.networking.k8s.io created
   customresourcedefinition.apiextensions.k8s.io/referencegrants.gateway.networking.k8s.io created
   customresourcedefinition.apiextensions.k8s.io/grpcroutes.gateway.networking.k8s.io created
   ```
   
   {{< callout type="info" >}}If you need to use an experimental feature such as TCPRoutes, install the experimental CRDs. For more information, see [Experimental features in Gateway API](../../reference/versions/#experimental-features).{{< /callout >}}

2. Apply the {{< reuse "/docs/snippets/kgateway.md" >}} CRDs for the upgrade version by using Helm.

   1. **Optional**: To check the CRDs locally, download the CRDs to a `helm` directory.

      ```sh
      helm template --version {{< reuse "docs/versions/helm-version-flag.md" >}} {{< reuse "/docs/snippets/helm-kgateway-crds.md" >}} oci://{{< reuse "/docs/snippets/helm-path.md" >}}/charts/{{< reuse "/docs/snippets/helm-kgateway-crds.md" >}} --output-dir ./helm
      ```

   2. Deploy the {{< reuse "/docs/snippets/kgateway.md" >}} CRDs by using Helm. This command creates the {{< reuse "docs/snippets/namespace.md" >}} namespace and creates the {{< reuse "/docs/snippets/kgateway.md" >}} CRDs in the cluster.
      ```sh
      helm upgrade -i --create-namespace --namespace {{< reuse "docs/snippets/namespace.md" >}} --version {{< reuse "docs/versions/helm-version-flag.md" >}} {{< reuse "/docs/snippets/helm-kgateway-crds.md" >}} oci://{{< reuse "/docs/snippets/helm-path.md" >}}/charts/{{< reuse "/docs/snippets/helm-kgateway-crds.md" >}} 
      ```

3. Install the {{< reuse "/docs/snippets/kgateway.md" >}} Helm chart.

   1. **Optional**: Pull and inspect the {{< reuse "/docs/snippets/kgateway.md" >}} Helm chart values before installation. You might want to update the Helm chart values files to customize the installation. For example, you might change the namespace, update the resource limits and requests, or enable extensions such as for AI.
   
      {{< callout type="info" >}}For other values that you might want to update, see [Advanced settings](../advanced).{{< /callout >}}

      ```sh
      helm pull oci://{{< reuse "/docs/snippets/helm-path.md" >}}/charts/{{< reuse "/docs/snippets/helm-kgateway.md" >}} --version {{< reuse "docs/versions/helm-version-flag.md" >}}
      tar -xvf {{< reuse "/docs/snippets/helm-kgateway.md" >}}-v{{< reuse "docs/versions/n-patch.md" >}}.tgz
      open {{< reuse "/docs/snippets/helm-kgateway.md" >}}/values.yaml
      ```
      
   2. Install {{< reuse "/docs/snippets/kgateway.md" >}} by using Helm. This command installs the control plane into it. If you modified the `values.yaml` file with custom installation values, add the `-f {{< reuse "/docs/snippets/helm-kgateway.md" >}}/values.yaml` flag.
      
      {{< tabs tabTotal="4" items="Basic installation,Custom values file,Development,Agentgateway and AI extensions" >}}
{{% tab tabName="Basic installation" %}}
```sh
helm upgrade -i -n {{< reuse "docs/snippets/namespace.md" >}} {{< reuse "/docs/snippets/helm-kgateway.md" >}} oci://{{< reuse "/docs/snippets/helm-path.md" >}}/charts/{{< reuse "/docs/snippets/helm-kgateway.md" >}} \
--version {{< reuse "docs/versions/helm-version-flag.md" >}}
```
{{% /tab %}}
{{% tab tabName="Custom values" %}}
```sh
helm upgrade -i -n {{< reuse "docs/snippets/namespace.md" >}} {{< reuse "/docs/snippets/helm-kgateway.md" >}} oci://{{< reuse "/docs/snippets/helm-path.md" >}}/charts/{{< reuse "/docs/snippets/helm-kgateway.md" >}} \
--version {{< reuse "docs/versions/helm-version-flag.md" >}} \
-f {{< reuse "/docs/snippets/helm-kgateway.md" >}}/values.yaml
```
{{% /tab %}}
{{% tab tabName="Development" %}}
When using the development build v{{< reuse "docs/versions/patch-dev.md" >}}, add the `--set controller.image.pullPolicy=Always` option to ensure you get the latest image. Alternatively, you can specify the exact image digest.

```sh
helm upgrade -i -n {{< reuse "docs/snippets/namespace.md" >}} {{< reuse "/docs/snippets/helm-kgateway.md" >}} oci://{{< reuse "/docs/snippets/helm-path.md" >}}/charts/{{< reuse "/docs/snippets/helm-kgateway.md" >}} \
--version v{{< reuse "docs/versions/patch-dev.md" >}} \
--set controller.image.pullPolicy=Always
```
{{% /tab %}}
{{% tab tabName="Agentgateway and AI extensions" %}}
```sh
helm upgrade -i -n {{< reuse "docs/snippets/namespace.md" >}} {{< reuse "/docs/snippets/helm-kgateway.md" >}} oci://{{< reuse "/docs/snippets/helm-path.md" >}}/charts/{{< reuse "/docs/snippets/helm-kgateway.md" >}} \
     --set gateway.aiExtension.enabled=true \
     --set agentgateway.enabled=true \
     --version {{< reuse "docs/versions/helm-version-upgrade.md" >}}
```
{{% /tab %}}
      {{< /tabs >}}

      Example output: 
      ```txt
      NAME: {{< reuse "/docs/snippets/helm-kgateway.md" >}}
      LAST DEPLOYED: Thu Feb 13 14:03:51 2025
      NAMESPACE: {{< reuse "docs/snippets/namespace.md" >}}
      STATUS: deployed
      REVISION: 1
      TEST SUITE: None
      ```

1. Verify that the control plane is up and running. 
   
   ```sh
   kubectl get pods -n {{< reuse "docs/snippets/namespace.md" >}}
   ```

   Example output: 
   ```txt
   NAME                                  READY   STATUS    RESTARTS   AGE
   {{< reuse "/docs/snippets/helm-kgateway.md" >}}-78658959cd-cz6jt             1/1     Running   0          12s
   ```

2. Verify that the `{{< reuse "/docs/snippets/gatewayclass.md" >}}` GatewayClass is created. You can optionally take a look at how the GatewayClass is configured by adding the `-o yaml` option to your command. 
   ```sh
   kubectl get gatewayclass {{< reuse "/docs/snippets/gatewayclass.md" >}}
   ```



## Next steps

Now that you have {{< reuse "/docs/snippets/kgateway.md" >}} set up and running, check out the following guides to expand your API gateway capabilities.
- Learn more about [{{< reuse "/docs/snippets/kgateway.md" >}}, its features and benefits](../../about/overview). 
- [Deploy an API gateway and sample app](../sample-app/) to test out routing to an app.
- Add routing capabilities to your httpbin route by using the [Traffic management](../../traffic-management) guides. 
- Explore ways to make your routes more resilient by using the [Resiliency](../../resiliency) guides. 
- Secure your routes with external authentication and rate limiting policies by using the [Security](../../security) guides. 

## Cleanup

{{< reuse "docs/snippets/cleanup.md" >}}

Follow the [Uninstall guide](../../operations/uninstall).
