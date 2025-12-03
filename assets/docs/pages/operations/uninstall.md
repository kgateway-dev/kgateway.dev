If you no longer need your {{< reuse "/docs/snippets/kgateway.md" >}} environment, you can uninstall the control plane and all gateway proxies. You can also optionally remove related components such as Prometheus and sample apps.

## Uninstall

Remove the {{< reuse "/docs/snippets/kgateway.md" >}} control plane and gateway proxies.

{{< callout type="info" >}}
Did you use Argo CD to install {{< reuse "/docs/snippets/kgateway.md" >}}? Skip to the [Argo CD steps](#argocd).
{{< /callout >}}

1. Get all HTTP routes in your environment. 
   
   ```sh
   kubectl get httproutes -A
   ```

2. Remove each HTTP route. 
   
   ```sh
   kubectl delete -n <namespace> httproute <httproute-name>
   ```

3. Get all reference grants in your environment. 
   
   ```sh
   kubectl get referencegrants -A
   ```

4. Remove each reference grant. 
   
   ```sh
   kubectl delete -n <namespace> referencegrant <referencegrant-name>
   ```

5. Get all gateways in your environment that are configured by the `{{< reuse "/docs/snippets/gatewayclass.md" >}}` gateway class. 
   
   ```sh
   kubectl get gateways -A | grep {{< reuse "/docs/snippets/gatewayclass.md" >}}
   ```

6. Remove each gateway. 
   
   ```sh
   kubectl delete -n <namespace> gateway <gateway-name>
   ```

7. Uninstall {{< reuse "/docs/snippets/kgateway.md" >}}.
   
   1. Uninstall the {{< reuse "/docs/snippets/helm-kgateway.md" >}} Helm release.
      
      ```sh
      helm uninstall {{< reuse "/docs/snippets/helm-kgateway.md" >}} -n {{< reuse "docs/snippets/namespace.md" >}}
      ```

   2. Delete the {{< reuse "/docs/snippets/kgateway.md" >}} CRDs.

      ```sh
      helm uninstall {{< reuse "/docs/snippets/helm-kgateway-crds.md" >}} -n {{< reuse "docs/snippets/namespace.md" >}}
      ```

   3. Remove the `{{< reuse "docs/snippets/namespace.md" >}}` namespace. 
      
      ```sh
      kubectl delete namespace {{< reuse "docs/snippets/namespace.md" >}}
      ```

   4. Confirm that the CRDs are deleted.

      ```sh
      kubectl get crds | grep kgateway
      ```

8. Remove the Kubernetes Gateway API CRDs. If you installed a different version or channel of the Kubernetes Gateway API, update the following command accordingly.
   
   ```sh
   kubectl delete -f https://github.com/kubernetes-sigs/gateway-api/releases/download/v{{< reuse "docs/versions/k8s-gw-version.md" >}}/standard-install.yaml
   ```

## Uninstall with ArgoCD {#argocd}

For ArgoCD installations, use the following steps to clean up your environment.

{{< tabs tabTotal="2" items="Argo CD UI,Argo CD CLI" >}}
{{% tab tabName="Argo CD UI" %}}
1. Port-forward the Argo CD server on port 9999.
   ```sh
   kubectl port-forward svc/argocd-server -n argocd 9999:443
   ```

2. Open the [Argo CD UI](https://localhost:9999/applications).

3. Log in with the `admin` username and `{{< reuse "/docs/snippets/helm-kgateway.md" >}}` password.
4. Find the application that you want to delete and click **x**. 
5. Select **Foreground** and click **Ok**. 
6. Verify that the pods were removed from the `{{< reuse "docs/snippets/namespace.md" >}}` namespace. 
   ```sh
   kubectl get pods -n {{< reuse "docs/snippets/namespace.md" >}}
   ```
   
   Example output: 
   ```txt
   No resources found in {{< reuse "docs/snippets/namespace.md" >}} namespace.
   ```

{{% /tab %}}
{{% tab tabName="Argo CD CLI" %}}
1. Port-forward the Argo CD server on port 9999.
   ```sh
   kubectl port-forward svc/argocd-server -n argocd 9999:443
   ```
   
2. Log in to the Argo CD UI. 
   ```sh
   argocd login localhost:9999 --username admin --password {{< reuse "/docs/snippets/helm-kgateway.md" >}} --insecure
   ```
   
3. Delete the {{< reuse "/docs/snippets/helm-kgateway.md" >}} application.
   
   ```sh
   argocd app delete {{< reuse "/docs/snippets/helm-kgateway.md" >}}-helm --cascade --server localhost:9999 --insecure
   ```
   
   Example output: 
   ```txt
   Are you sure you want to delete '{{< reuse "/docs/snippets/helm-kgateway.md" >}}-helm' and all its resources? [y/n] y
   application '{{< reuse "/docs/snippets/helm-kgateway.md" >}}-helm' deleted   
   ```

4. Delete the {{< reuse "/docs/snippets/helm-kgateway.md" >}} CRD application.
   
   ```sh
   argocd app delete {{< reuse "/docs/snippets/helm-kgateway-crds.md" >}}-helm --cascade --server localhost:9999 --insecure
   ```
   
   Example output: 
   ```txt
   Are you sure you want to delete '{{< reuse "/docs/snippets/helm-kgateway-crds.md" >}}-helm' and all its resources? [y/n] y
   application '{{< reuse "/docs/snippets/helm-kgateway-crds.md" >}}-helm' deleted   
   ```

5. Verify that the pods were removed from the `{{< reuse "docs/snippets/namespace.md" >}}` namespace. 
   ```sh
   kubectl get pods -n {{< reuse "docs/snippets/namespace.md" >}}
   ```
   
   Example output: 
   ```txt  
   No resources found in {{< reuse "docs/snippets/namespace.md" >}} namespace.
   ```
{{% /tab %}}
{{< /tabs >}}

{{< conditional-text include-if="envoy" >}}

## Uninstall optional components {#optional}

Remove any optional components that you no longer need, such as sample apps.

1. If you no longer need the Prometheus stack to monitor resources in your cluster, uninstall the release and delete the namespace.
   
   ```sh
   helm uninstall kube-prometheus-stack -n monitoring
   kubectl delete namespace monitoring
   ``` 
2. Remove the httpbin sample app.
   
   ```sh
   kubectl delete -f https://raw.githubusercontent.com/kgateway-dev/kgateway/refs/heads/{{< reuse "docs/versions/github-branch.md" >}}/examples/httpbin.yaml
   ```

3. Remove the Petstore sample app.
   
   ```sh
   kubectl delete -f https://raw.githubusercontent.com/kgateway-dev/kgateway.dev/{{< reuse "docs/versions/github-branch.md" >}}/assets/docs/examples/petstore.yaml
   ```
{{< /conditional-text >}}
