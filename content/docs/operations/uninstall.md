---
title: Uninstall
weight: 50
description: Uninstall kgateway and related components.
---

If you no longer need your {{< reuse "docs/snippets/product-name.md" >}} environment, you can uninstall the control plane and all gateway proxies. You can also optionally remove related components such as Prometheus and sample apps.

## Uninstall kgateway

Remove the {{< reuse "docs/snippets/product-name.md" >}} control plane and gateway proxies.

{{< callout type="info" >}}
Did you use Argo CD to install {{< reuse "docs/snippets/product-name.md" >}}? Skip to the [Argo CD steps](#argocd).
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

5. Get all gateways in your environment that are configured by the `kgateway` gateway class. 
   
   ```sh
   kubectl get gateways -A | grep kgateway
   ```

6. Remove each gateway. 
   
   ```sh
   kubectl delete -n <namespace> gateway <gateway-name>
   ```

7. Uninstall {{< reuse "docs/snippets/product-name.md" >}}.
   
   1. Uninstall the {{< reuse "docs/snippets/product-name.md" >}} release.
      
      ```sh
      helm uninstall kgateway -n {{< reuse "docs/snippets/ns-system.md" >}}
      ```

   2. Remove the `{{< reuse "docs/snippets/ns-system.md" >}}` namespace. 
      
      ```sh
      kubectl delete namespace {{< reuse "docs/snippets/ns-system.md" >}}
      ```

   3. Delete the {{< reuse "docs/snippets/product-name.md" >}} CRDs.

      ```sh
      kubectl delete crd backends.gateway.kgateway.dev
      kubectl delete crd directresponses.gateway.kgateway.dev
      kubectl delete crd gatewayparameters.gateway.kgateway.dev
      kubectl delete crd httplistenerpolicies.gateway.kgateway.dev
      kubectl delete crd listenerpolicies.gateway.kgateway.dev
      kubectl delete crd routepolicies.gateway.kgateway.dev
      ```

   4. Confirm that the CRDs are deleted.

      ```sh
      kubectl get crds | grep {{< reuse "docs/snippets/product-name.md" >}}
      ```

8. Remove the {{< reuse "docs/snippets/k8s-gateway-api-name.md" >}} CRDs. 
   
   ```sh
   kubectl delete -f https://github.com/kubernetes-sigs/gateway-api/releases/download/v{{< reuse "docs/versions/k8s-gw-version.md" >}}/standard-install.yaml
   ```

## Uninstall with ArgoCD {#argocd}

For ArgoCD installations, use the following steps to clean up your environment.

{{< tabs items="Argo CD UI,Argo CD CLI" >}}
{{% tab %}}
1. Port-forward the Argo CD server on port 9999.
   ```sh
   kubectl port-forward svc/argocd-server -n argocd 9999:443
   ```

2. Open the [Argo CD UI](https://localhost:9999/applications).

3. Log in with the `admin` username and `kgateway` password.
4. Find the application that you want to delete and click **x**. 
5. Select **Foreground** and click **Ok**. 
6. Verify that the pods were removed from the `{{< reuse "docs/snippets/ns-system.md" >}}` namespace. 
   ```sh
   kubectl get pods -n {{< reuse "docs/snippets/ns-system.md" >}}
   ```
   
   Example output: 
   ```txt
   No resources found in {{< reuse "docs/snippets/ns-system.md" >}}namespace.
   ```

{{% /tab %}}
{{% tab %}}
1. Port-forward the Argo CD server on port 9999.
   ```sh
   kubectl port-forward svc/argocd-server -n argocd 9999:443
   ```
   
2. Log in to the Argo CD UI. 
   ```sh
   argocd login localhost:9999 --username admin --password kgateway --insecure
   ```
   
3. Delete the application.
   
   ```sh
   argocd app delete kgateway-oss-helm --cascade --server localhost:9999 --insecure
   ```
   
   Example output: 
   ```txt
   Are you sure you want to delete 'kgateway-oss-helm' and all its resources? [y/n] y
   application 'kgateway-oss-helm' deleted   
   ```

4. Verify that the pods were removed from the `{{< reuse "docs/snippets/ns-system.md" >}}` namespace. 
   ```sh
   kubectl get pods -n {{< reuse "docs/snippets/ns-system.md" >}}
   ```
   
   Example output: 
   ```txt  
   No resources found in {{< reuse "docs/snippets/ns-system.md" >}} namespace.
   ```
{{% /tab %}}
{{< /tabs >}}

## Uninstall optional components {#optional}

Remove any optional components that you no longer need, such as sample apps.

1. If you no longer need the Prometheus stack to monitor resources in your cluster, uninstall the release and delete the namespace.
   
   ```sh
   helm uninstall kube-prometheus-stack -n monitoring
   kubectl delete namespace monitoring
   ```

2. Remove the httpbin sample app.
   
   ```sh
   kubectl delete -f https://raw.githubusercontent.com/kgateway-dev/kgateway/refs/heads/main/examples/httpbin.yaml
   ```

3. Remove the Petstore sample app.
   
   ```sh
   kubectl delete -f https://raw.githubusercontent.com/kgateway-dev/kgateway.dev/main/assets/docs/examples/petstore.yaml
   ```
