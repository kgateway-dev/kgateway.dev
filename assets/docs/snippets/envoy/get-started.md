1. Deploy the Kubernetes Gateway API CRDs.

   {{< tabs >}}
   {{% tab name="Standard" %}}
   ```sh
   kubectl apply -f https://github.com/kubernetes-sigs/gateway-api/releases/download/v{{< reuse "docs/versions/k8s-gw-version.md" >}}/standard-install.yaml
   ```
   {{% /tab %}}
   {{% tab name="Experimental" %}}
   CRDs in the experimental channel are required to use some experimental features in the Gateway API. Guides that require experimental CRDs note this requirement in their prerequisites.
   ```sh
   kubectl apply --server-side -f https://github.com/kubernetes-sigs/gateway-api/releases/download/v{{< reuse "docs/versions/k8s-gw-version.md" >}}/experimental-install.yaml
   ```  
   {{% /tab %}}
   {{< /tabs >}}

2. Deploy the kgateway CRDs by using Helm.
   ```sh
   helm upgrade -i kgateway-crds oci://cr.kgateway.dev/kgateway-dev/charts/kgateway-crds \
   --create-namespace --namespace kgateway-system \
   --version v{{< reuse "docs/versions/n-patch.md" >}} \
   --set controller.image.pullPolicy=Always
   ```

3. Install kgateway by using Helm.
   ```sh
   helm upgrade -i kgateway oci://cr.kgateway.dev/kgateway-dev/charts/kgateway \
   --namespace kgateway-system \
   --version v{{< reuse "docs/versions/n-patch.md" >}} \
   --set controller.image.pullPolicy=Always
   ```
   
4. Make sure that the `kgateway` control plane is running.

   ```sh
   kubectl get pods -n kgateway-system
   ```

   Example output:

   ```console
   NAME                        READY   STATUS    RESTARTS   AGE
   kgateway-5495d98459-46dpk   1/1     Running   0          19s
   ```