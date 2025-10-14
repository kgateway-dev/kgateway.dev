---
title: ArgoCD
weight: 10
description: Install kgateway and related components.
---

In this installation guide, you install {{< reuse "/docs/snippets/kgateway.md" >}} in a Kubernetes cluster by using [Argo CD](https://argoproj.github.io/cd/). Argo CD is a declarative continuous delivery tool that is especially popular for large, production-level installations at scale. This approach incorporates Helm configuration files.

## Before you begin

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

## Install

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



## Next steps

Now that you have {{< reuse "/docs/snippets/kgateway.md" >}} set up and running, check out the following guides to expand your API gateway capabilities.
- Learn more about [{{< reuse "/docs/snippets/kgateway.md" >}}, its features and benefits](../../about/overview). 
- [Deploy an API gateway and sample app](../sample-app/) to test out routing to an app.
- Add routing capabilities to your httpbin route by using the [Traffic management](../../traffic-management) guides. 
- Explore ways to make your routes more resilient by using the [Resiliency](../../resiliency) guides. 
- Secure your routes with external authentication and rate limiting policies by using the [Security](../../security) guides. 

## Cleanup

{{< reuse "docs/snippets/cleanup.md" >}}

Follow the [Uninstall with Argo CD guide](../../operations/uninstall#argocd).
