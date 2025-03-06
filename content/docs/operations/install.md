---
title: Install
weight: 5
description: Install kgateway and related components.
---

In this installation guide, you install {{< reuse "docs/snippets/product-name.md" >}} in a Kubernetes cluster, set up an API gateway, deploy a sample app, and access that app through the API gateway.

The guide includes steps to install {{< reuse "docs/snippets/product-name.md" >}} in two ways.

{{< tabs items="Helm,Argo CD" >}}
  
  {{% tab %}}[Helm](https://helm.sh/) is a popular package manager for Kubernetes configuration files. This approach is flexible for adopting to your own command line, continuous delivery, or other workflows.{{% /tab %}}
  
  {{% tab %}}[Argo CD](https://argoproj.github.io/cd/) is a declarative continuous delivery tool that is especially popular for large, production-level installations at scale. This approach incorporates Helm configuration files.{{% /tab %}}

{{< /tabs >}}

## Before you begin

{{< callout type="warning" >}}
{{< reuse "docs/snippets/one-install.md" >}} If you already tried out {{< reuse "docs/snippets/product-name.md" >}} by following the [Get started](/docs/quickstart/) guide, first [uninstall your installation](/docs/operations/uninstall/).
{{< /callout >}}

{{< tabs items="Helm,Argo CD" >}}
{{% tab %}}
1. Create or use an existing Kubernetes cluster. 
2. Install the following command-line tools.
   * [`kubectl`](https://kubernetes.io/docs/tasks/tools/#kubectl), the Kubernetes command line tool. Download the `kubectl` version that is within one minor version of the Kubernetes clusters you plan to use.
   * [`helm`](https://helm.sh/docs/intro/install/), the Kubernetes package manager.
{{% /tab %}}
{{% tab %}}
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
4. Update the default Argo CD password for the admin user to `kgateway`.
   ```shell
   # bcrypt(password)=$2a$10$g3bspLL4iTNQHxJpmPS0A.MtyOiVvdRk1Ds5whv.qSdnKUmqYVyxa
   # password: kgateway
   kubectl -n argocd patch secret argocd-secret \
     -p '{"stringData": {
       "admin.password": "$2a$10$g3bspLL4iTNQHxJpmPS0A.MtyOiVvdRk1Ds5whv.qSdnKUmqYVyxa",
       "admin.passwordMtime": "'$(date +%FT%T%Z)'"
     }}'
   ```
{{% /tab %}}
{{< /tabs >}}

## Install kgateway

Install the open source {{< reuse "docs/snippets/product-name.md" >}} project in your Kubernetes cluster.

{{< tabs items="Helm,Argo CD" >}}

{{% tab %}}
1. Install the custom resources of the {{< reuse "docs/snippets/k8s-gateway-api-name.md" >}} version 1.2.0. 
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
   
   {{< callout type="info" >}}
   If you want to use TCPRoutes to set up a TCP listener on your Gateway, you must install the TCPRoute CRD, which is part of the {{< reuse "docs/snippets/k8s-gateway-api-name.md" >}} experimental channel. Use the following command to install the CRDs. 
   ```sh
   kubectl apply -f https://github.com/kubernetes-sigs/gateway-api/releases/download/v{{< reuse "docs/versions/k8s-gw-version.md" >}}/experimental-install.yaml
   ```
   {{< /callout >}}

2. Optional: Pull and inspect the {{< reuse "docs/snippets/product-name.md" >}} Helm chart values before installation. You might want to update the Helm chart values files to customize the installation. For example, you might change the namespace, update the resource limits and requests, or enable extensions such as for AI.
   
   ```sh
   helm pull oci://ghcr.io/kgateway-dev/charts/kgateway --version v{{< reuse "docs/versions/n-patch.md" >}}
   tar -xvf kgateway-v{{< reuse "docs/versions/n-patch.md" >}}.tgz
   cat kgateway/values.yaml
   ```
      
3. Install {{< reuse "docs/snippets/product-name.md" >}}. This command creates the {{< reuse "docs/snippets/ns-system.md" >}} namespace and installs the {{< reuse "docs/snippets/product-name.md" >}} control plane into it.
   
   ```sh
   helm install -n {{< reuse "docs/snippets/ns-system.md" >}} kgateway oci://ghcr.io/kgateway-dev/charts/kgateway \
   --create-namespace \
   --version v{{< reuse "docs/versions/n-patch.md" >}}
   ```
   
   Example output: 
   ```txt
   NAME: kgateway
   LAST DEPLOYED: Thu Feb 13 14:03:51 2025
   NAMESPACE: {{< reuse "docs/snippets/ns-system.md" >}}
   STATUS: deployed
   REVISION: 1
   TEST SUITE: None
   ```

4. Verify that the {{< reuse "docs/snippets/product-name.md" >}} control plane is up and running. 
   
   ```sh
   kubectl get pods -n {{< reuse "docs/snippets/ns-system.md" >}}
   ```

   Example output: 
   ```txt
   NAME                                  READY   STATUS    RESTARTS   AGE
   kgateway-78658959cd-cz6jt             1/1     Running   0          12s
   ```

5. Verify that the `kgateway` GatewayClass is created. You can optionally take a look at how the gateway class is configured by adding the `-o yaml` option to your command. 
   ```sh
   kubectl get gatewayclass kgateway
   ```
{{% /tab %}}
{{% tab %}}
1. Install the custom resources of the {{< reuse "docs/snippets/k8s-gateway-api-name.md" >}} version 1.2.0. 
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
   
   {{< callout type="info" >}}
   If you want to use TCPRoutes to set up a TCP listener on your Gateway, you must install the TCPRoute CRD, which is part of the {{< reuse "docs/snippets/k8s-gateway-api-name.md" >}} experimental channel. Use the following command to install the CRDs. 
   ```sh
   kubectl apply -f https://github.com/kubernetes-sigs/gateway-api/releases/download/v{{< reuse "docs/versions/k8s-gw-version.md" >}}/experimental-install.yaml
   ```
   {{< /callout >}}
   
2. Port-forward the Argo CD server on port 9999.
   
   ```sh
   kubectl port-forward svc/argocd-server -n argocd 9999:443
   ```

3. Open the [Argo CD UI](https://localhost:9999/).

4. Log in with the `admin` username and `kgateway` password.
   
   {{< reuse-image src="img/argocd-welcome.png" >}}

5. Create an Argo CD application to install the {{% reuse "docs/snippets/product-name.md" %}} Helm chart. 
   
   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: argoproj.io/v1alpha1
   kind: Application
   metadata:
     name: kgateway-oss-helm
     namespace: argocd
   spec:
     destination:
       namespace: {{< reuse "docs/snippets/ns-system.md" >}}
       server: https://kubernetes.default.svc
     project: default
     source:
       chart: kgateway
       helm:
         skipCrds: false
       repoURL: oci://ghcr.io/kgateway-dev/charts/kgateway
       targetRevision: {{< reuse "docs/versions/n-patch.md" >}}
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
   
6. Verify that the `kgateway` control plane is up and running.
   
   ```sh
   kubectl get pods -n {{< reuse "docs/snippets/ns-system.md" >}} 
   ```
   
   Example output: 
   ```txt
   NAME                                      READY   STATUS      RESTARTS   AGE
   gateway-certgen-wfz9z                     0/1     Completed   0          35s
   kgateway-78f4cc8fc6-6hmsq                 1/1     Running     0          21s
   kgateway-resource-migration-sx5z4         0/1     Completed   0          48s
   kgateway-resource-rollout-28gj6           0/1     Completed   0          21s
   kgateway-resource-rollout-check-tjdp7     0/1     Completed   0          2s
   kgateway-resource-rollout-cleanup-nj4t8   0/1     Completed   0          39s
   ```

7. Verify that the `kgateway` GatewayClass is created. You can optionally take a look at how the gateway class is configured by adding the `-o yaml` option to your command.
   
   ```sh
   kubectl get gatewayclass kgateway
   ```

8. Open the Argo CD UI and verify that you see the Argo CD application with a `Healthy` and `Synced` status.
   
   {{< reuse-image src="/img/argo-gg-oss.png" >}}

{{% /tab %}}
{{< /tabs >}}

## Next steps

Now that you have {{< reuse "docs/snippets/product-name.md" >}} set up and running, check out the following guides to expand your API gateway capabilities.
- Learn more about [{{< reuse "docs/snippets/product-name.md" >}}, its features and benefits](/docs/about/overview). 
- [Deploy an API gateway and sample app](/docs/operations/sample-app/) to test out routing to an app.
- Add routing capabilities to your httpbin route by using the [Traffic management](/docs/traffic-management) guides. 
- Explore ways to make your routes more resilient by using the [Resiliency](/docs/resiliency) guides. 
- Secure your routes with external authentication and rate limiting policies by using the [Security](/docs/security) guides. 

## Cleanup

{{< reuse "docs/snippets/cleanup.md" >}}

{{< tabs items="Helm,Argo CD" >}}
  
  {{% tab %}}Follow the [Uninstall guide](/docs/operations/uninstall).{{% /tab %}}
  
  {{% tab %}}Follow the [Uninstall with Argo CD guide](/docs/operations/uninstall#argocd).{{% /tab %}}

{{< /tabs >}}
