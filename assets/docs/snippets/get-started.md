1. Deploy the Kubernetes Gateway API CRDs.

   {{< tabs items="Standard, Experimental" tabTotal="2" >}}
   {{% tab tabName="Standard" %}}
   ```sh
   kubectl apply -f https://github.com/kubernetes-sigs/gateway-api/releases/download/v{{< reuse "docs/versions/k8s-gw-version.md" >}}/standard-install.yaml
   ```
   {{% /tab %}}
   {{% tab tabName="Experimental" %}}
   ```sh
   kubectl apply {{< version include-if="2.2.x,2.1.x" >}}--server-side {{< /version >}}-f https://github.com/kubernetes-sigs/gateway-api/releases/download/v{{< reuse "docs/versions/k8s-gw-version.md" >}}/experimental-install.yaml
   ```  
   {{% /tab %}}
   {{< /tabs >}}

2. Deploy the kgateway CRDs by using Helm.
   {{< version include-if="2.2.x" >}}
   ```sh
   helm upgrade -i --create-namespace --namespace kgateway-system --version v{{< reuse "docs/versions/patch-dev.md" >}} \
   kgateway-crds oci://cr.kgateway.dev/kgateway-dev/charts/kgateway-crds \
   --set controller.image.pullPolicy=Always
   ```
   {{< /version >}}
   {{< version include-if="2.0.x,2.1.x" >}}
   ```sh
   helm upgrade -i --create-namespace --namespace kgateway-system --version v{{< reuse "docs/versions/n-patch.md" >}} kgateway-crds oci://cr.kgateway.dev/kgateway-dev/charts/kgateway-crds
   ```
   {{< /version >}}

3. Install kgateway by using Helm. Choose the [data plane gateway proxy]({{< link-hextra path="/about/proxies#supported" >}}) that you want to use, such as kgateway for API ingress or agentgateway for AI use cases.
   {{< version include-if="2.2.x" >}}
   {{< tabs items="Kgateway, Agentgateway" tabTotal="2">}}
   {{% tab tabName="Kgateway" %}}
   ```sh
   helm upgrade -i --namespace kgateway-system --version v{{< reuse "docs/versions/patch-dev.md" >}} \
   kgateway oci://cr.kgateway.dev/kgateway-dev/charts/kgateway \
   --set controller.image.pullPolicy=Always
   ```
   {{% /tab %}}
   {{% tab tabName="Agentgateway" %}}
   ```sh
   helm upgrade -i --namespace kgateway-system --version v{{< reuse "docs/versions/patch-dev.md" >}} kgateway oci://cr.kgateway.dev/kgateway-dev/charts/kgateway \
     --set agentgateway.enabled=true  \
     --set controller.image.pullPolicy=Always
   ```
   {{% /tab %}}
   {{< /tabs >}}
   {{< /version >}}
   {{< version include-if="2.0.x,2.1.x" >}}
   ```sh
   helm upgrade -i --namespace kgateway-system --version v{{< reuse "docs/versions/n-patch.md" >}} kgateway oci://cr.kgateway.dev/kgateway-dev/charts/kgateway
   ```
   {{< /version >}}

4. Make sure that `kgateway` is running.

   ```sh
   kubectl get pods -n kgateway-system
   ```

   Example output:

   ```console
   NAME                        READY   STATUS    RESTARTS   AGE
   kgateway-5495d98459-46dpk   1/1     Running   0          19s
   ```