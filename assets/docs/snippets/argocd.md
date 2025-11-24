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
   When using the development build {{< reuse "docs/versions/patch-dev.md" >}}, add the `controller.image.pullPolicy=Always` parameter to ensure you get the latest image.
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
   NAME                             READY   STATUS    RESTARTS   AGE
   kgateway-helm-6b5bb4db6b-c2pkq   1/1     Running   0          4m4s
   ```

8. Verify that the `{{< reuse "/docs/snippets/gatewayclass.md" >}}` GatewayClass is created. You can optionally take a look at how the gateway class is configured by adding the `-o yaml` option to your command.
   
   ```sh
   kubectl get gatewayclass {{< reuse "/docs/snippets/gatewayclass.md" >}}
   ```

9. Open the Argo CD UI and verify that you see the Argo CD application with a `Healthy` and `Synced` status.
   
   {{< reuse-image src="img/argo-app.png" >}}
   {{< reuse-image-dark srcDark="img/argo-app.png" >}}