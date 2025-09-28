---
title: Install
weight: 5
description: Install kgateway and related components.
---

In this installation guide, you install {{< reuse "/docs/snippets/kgateway.md" >}} in a Kubernetes cluster, set up an API gateway, deploy a sample app, and access that app through the API gateway.

The guide includes steps to install {{< reuse "/docs/snippets/kgateway.md" >}} in two ways.

{{< tabs tabTotal="2" items="Helm,Argo CD" >}}
  
  {{% tab tabName="Helm" %}}
  [Helm](https://helm.sh/) is a popular package manager for Kubernetes configuration files. This approach is flexible for adopting to your own command line, continuous delivery, or other workflows.
  {{% /tab %}}
  
  {{% tab tabName="Argo CD" %}}
  [Argo CD](https://argoproj.github.io/cd/) is a declarative continuous delivery tool that is especially popular for large, production-level installations at scale. This approach incorporates Helm configuration files.
  {{% /tab %}}

{{< /tabs >}}

## Before you begin

{{< callout type="warning" >}}
{{< reuse "docs/snippets/one-install.md" >}} If you already tried out {{< reuse "/docs/snippets/kgateway.md" >}} by following the [Get started](../../quickstart/) guide, first [uninstall your installation](../uninstall/).
{{< /callout >}}

{{< tabs tabTotal="2" items="Helm,Argo CD" >}}
{{% tab tabName="Helm" %}}
1. Create or use an existing Kubernetes cluster. 
2. Install the following command-line tools.
   * [`kubectl`](https://kubernetes.io/docs/tasks/tools/#kubectl), the Kubernetes command line tool. Download the `kubectl` version that is within one minor version of the Kubernetes clusters you plan to use.
   * [`helm`](https://helm.sh/docs/intro/install/), the Kubernetes package manager.
{{% /tab %}}
{{% tab tabName="Argo CD" %}}
1. Create or use an existing Kubernetes cluster. 
2. Install the following command-line tools.
   * [`kubectl`](https://kubernetes.io/docs/tasks/tools/#kubectl), the Kubernetes command line tool. Download the `kubectl` version that is within one minor version of the Kubernetes clusters you plan to use.
   * [`argo`](https://argo-cd.readthedocs.io/en/stable/cli_installation/), the Argo CD command line tool.
3. Install Argo CD in your cluster.
   ```shell
   kubectl create namespace argocd
   until kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/v2.12.3/manifests/install.yaml > /dev/null 2>&1; do sleep 2; done
   # wait for deployment to complete
   kubectl -n argocd rollout status deploy/argocd-applicationset-controller
   kubectl -n argocd rollout status deploy/argocd-dex-server
   kubectl -n argocd rollout status deploy/argocd-notifications-controller
   kubectl -n argocd rollout status deploy/argocd-redis
   kubectl -n argocd rollout status deploy/argocd-repo-server
   kubectl -n argocd rollout status deploy/argocd-server   
   ```
4. Update the default Argo CD password for the admin user to `{{< reuse "/docs/snippets/helm-kgateway.md" >}}`.
   ```shell
   # bcrypt(password)=$2a$10$g3bspLL4iTNQHxJpmPS0A.MtyOiVvdRk1Ds5whv.qSdnKUmqYVyxa
   # password: {{< reuse "/docs/snippets/helm-kgateway.md" >}}
   kubectl -n argocd patch secret argocd-secret \
     -p '{"stringData": {
       "admin.password": "$2a$10$g3bspLL4iTNQHxJpmPS0A.MtyOiVvdRk1Ds5whv.qSdnKUmqYVyxa",
       "admin.passwordMtime": "'$(date +%FT%T%Z)'"
     }}'
   ```
{{% /tab %}}
{{< /tabs >}}

## Install

Install {{< reuse "/docs/snippets/kgateway.md" >}} in your Kubernetes cluster. Choose from the following installation options:

* [Helm](#helm)
* [Argo CD](#argo-cd)

### Helm

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
   
      {{< callout type="info" >}}For common values that you might want to update, see [Installation settings](#installation-settings).{{< /callout >}}

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
     --set agentGateway.enabled=true \
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

### Argo CD

Install {{< reuse "/docs/snippets/kgateway.md" >}} by using Argo CD.

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
   
2. Port-forward the Argo CD server on port 9999.
   
   ```sh
   kubectl port-forward svc/argocd-server -n argocd 9999:443
   ```

3. Open the [Argo CD UI](https://localhost:9999/).

4. Log in with the `admin` username and `{{< reuse "/docs/snippets/helm-kgateway.md" >}}` password.
   
   {{< reuse-image src="img/argocd-welcome.png" >}}
   {{< reuse-image-dark srcDark="img/argocd-welcome.png" >}}

5. Create an Argo CD application to deploy the {{< reuse "/docs/snippets/kgateway.md" >}} CRD Helm chart. 
   
   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: argoproj.io/v1alpha1
   kind: Application
   metadata:
     name: {{< reuse "/docs/snippets/helm-kgateway-crds.md" >}}-helm
     namespace: argocd
   spec:
     destination:
       namespace: {{< reuse "docs/snippets/namespace.md" >}}
       server: https://kubernetes.default.svc
     project: default
     source:
       chart: {{< reuse "/docs/snippets/helm-kgateway-crds.md" >}}
       helm:
         skipCrds: false
       repoURL: {{< reuse "/docs/snippets/helm-path.md" >}}/charts
       targetRevision: {{< reuse "docs/versions/helm-version-flag.md" >}}
     syncPolicy:
       automated:
         # Prune resources during auto-syncing (default is false)
         prune: true 
         # Sync the app in part when resources are changed only in the target Kubernetes cluster
         # but not in the git source (default is false).
         selfHeal: true 
       syncOptions:
       - CreateNamespace=true 
   EOF
   ```

6. Create an Argo CD application to install the {{< reuse "/docs/snippets/kgateway.md" >}} Helm chart. 
 {{< callout type="warning" >}}
   When using the development build {{< reuse "docs/versions/patch-dev.md" >}} , add the `controller.image.pullPolicy=Always` parameter to ensure you get the latest image.
   {{< /callout >}}
   
   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: argoproj.io/v1alpha1
   kind: Application
   metadata:
     name: {{< reuse "/docs/snippets/helm-kgateway.md" >}}-helm
     namespace: argocd
   spec:
     destination:
       namespace: {{< reuse "docs/snippets/namespace.md" >}}
       server: https://kubernetes.default.svc
     project: default
     source:
       chart: {{< reuse "/docs/snippets/helm-kgateway.md" >}}
       helm:
         skipCrds: false
         parameters:
         - name: controller.image.pullPolicy
           value: "Always"
       repoURL: {{< reuse "/docs/snippets/helm-path.md" >}}/charts
       targetRevision: {{< reuse "docs/versions/helm-version-flag.md" >}}
     syncPolicy:
       automated:
         # Prune resources during auto-syncing (default is false)
         prune: true 
         # Sync the app in part when resources are changed only in the target Kubernetes cluster
         # but not in the git source (default is false).
         selfHeal: true 
       syncOptions:
       - CreateNamespace=true 
   EOF
   ```
   
7. Verify that the control plane is up and running.
   
   ```sh
   kubectl get pods -n {{< reuse "docs/snippets/namespace.md" >}} 
   ```
   
   Example output: 
   ```txt
   NAME                                      READY   STATUS      RESTARTS   AGE
   gateway-certgen-wfz9z                     0/1     Completed   0          35s
   {{< reuse "/docs/snippets/helm-kgateway.md" >}}-78f4cc8fc6-6hmsq                 1/1     Running     0          21s
   {{< reuse "/docs/snippets/helm-kgateway.md" >}}-resource-migration-sx5z4         0/1     Completed   0          48s
   {{< reuse "/docs/snippets/helm-kgateway.md" >}}-resource-rollout-28gj6           0/1     Completed   0          21s
   {{< reuse "/docs/snippets/helm-kgateway.md" >}}-resource-rollout-check-tjdp7     0/1     Completed   0          2s
   {{< reuse "/docs/snippets/helm-kgateway.md" >}}-resource-rollout-cleanup-nj4t8   0/1     Completed   0          39s
   ```

8. Verify that the `{{< reuse "/docs/snippets/gatewayclass.md" >}}` GatewayClass is created. You can optionally take a look at how the gateway class is configured by adding the `-o yaml` option to your command.
   
   ```sh
   kubectl get gatewayclass {{< reuse "/docs/snippets/gatewayclass.md" >}}
   ```

9. Open the Argo CD UI and verify that you see the Argo CD application with a `Healthy` and `Synced` status.
   
   {{< reuse-image src="img/argo-app.png" >}}
   {{< reuse-image-dark srcDark="img/argo-app.png" >}}

## Installation settings {#installation-settings}

You can update several installation settings in your Helm values file. For example, you can update the namespace, set resource limits and requests, or enable extensions such as for AI.

### Agentgateway and AI extensions {#agentgateway-ai-extensions}

To enable the [Agentgateway](../../agentgateway/) and [AI extensions](../../ai/), set the following values in your Helm values file.

```yaml
agentgateway:
  enabled: true
gateway:
  aiExtension:
    enabled: true
```

### Development builds

When using the development build {{< reuse "docs/versions/patch-dev.md" >}}, add `--set controller.image.pullPolicy=Always` to ensure you get the latest image. For production environments, this setting is not recommended as it might impact performance.

### Helm reference docs {#helm-docs}

For more information, see the Helm reference docs.

{{< cards >}}
  {{< card link="/docs/reference/helm/helm/" title="Helm reference docs" >}}
{{< /cards >}}

### Namespace discovery {#namespace-discovery}

You can limit the namespaces that {{< reuse "/docs/snippets/kgateway.md" >}} watches for gateway configuration. For example, you might have a multi-tenant cluster with different namespaces for different tenants. You can limit {{< reuse "/docs/snippets/kgateway.md" >}} to only watch a specific namespace for gateway configuration.

Namespace selectors are a list of matched expressions or labels.

* `matchExpressions`: Use this field for more complex selectors where you want to specify an operator such as `In` or `NotIn`.
* `matchLabels`: Use this field for simple selectors where you want to specify a label key-value pair.

Each entry in the list is disjunctive (OR semantics). This means that a namespace is selected if it matches any selector.

You can also use matched expressions and labels together in the same entry, which is conjunctive (AND semantics).

The following example selects namespaces for discovery that meet either of the following conditions:

* The namespace has the label `environment=prod` and the label `version=v2`, or
* The namespace has the label `version=v3`

```yaml
discoveryNamespaceSelectors:
- matchExpressions:
  - key: environment
    operator: In
    values:
    - prod
  matchLabels:
    version: v2
- matchLabels:
    version: v3
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

{{< tabs tabTotal="2" items="Helm,Argo CD" >}}
  
  {{% tab tabName="Helm" %}}Follow the [Uninstall guide](../uninstall).{{% /tab %}}
  
  {{% tab tabName="Argo CD" %}}Follow the [Uninstall with Argo CD guide](../uninstall#argocd).{{% /tab %}}

{{< /tabs >}}
