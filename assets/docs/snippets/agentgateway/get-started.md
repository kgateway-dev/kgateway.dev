1. Deploy the Kubernetes Gateway API CRDs.

   {{< tabs items="Standard, Experimental" tabTotal="2" >}}
   {{% tab tabName="Standard" %}}
   ```sh
   kubectl apply -f https://github.com/kubernetes-sigs/gateway-api/releases/download/v{{< reuse "docs/versions/k8s-gw-version.md" >}}/standard-install.yaml
   ```
   {{% /tab %}}
   {{% tab tabName="Experimental" %}}
   CRDs in the experimental channel are required to use some experimental features in the Gateway API. Guides that require experimental CRDs note this requirement in their prerequisites.
   ```sh
   kubectl apply --server-side -f https://github.com/kubernetes-sigs/gateway-api/releases/download/v{{< reuse "docs/versions/k8s-gw-version.md" >}}/experimental-install.yaml
   ```  
   {{% /tab %}}
   {{< /tabs >}}

2. Deploy the CRDs for the kgateway control plane and agentgateway data plane by using Helm.
   {{< version include-if="2.2.x" >}}
   ```sh
   helm upgrade -i kgateway-crds oci://cr.kgateway.dev/kgateway-dev/charts/kgateway-crds \
   --create-namespace --namespace kgateway-system \
   --version v{{< reuse "docs/versions/patch-dev.md" >}} \
   --set controller.image.pullPolicy=Always
   ```
   {{< /version >}}
   {{< version include-if="2.1.x" >}}
   ```sh
   helm upgrade -i kgateway-crds oci://cr.kgateway.dev/kgateway-dev/charts/kgateway-crds\
   --create-namespace --namespace kgateway-system \
   --version v{{< reuse "docs/versions/n-patch.md" >}} 
   ```
   {{< /version >}}

3. Install the kgateway control plane by using Helm. Make sure to enable the agentgateway feature flag, `--set agentgateway.enabled=true`. {{< version include-if="2.2.x" >}} To use experimental Gateway API features, include the experimental feature gate, `--set controller.extraEnv.KGW_ENABLE_GATEWAY_API_EXPERIMENTAL_FEATURES=true`.{{< /version >}}
   {{< version include-if="2.1.x" >}}
   ```sh
   helm upgrade -i kgateway oci://cr.kgateway.dev/kgateway-dev/charts/kgateway \
     --namespace kgateway-system \
     --version v{{< reuse "docs/versions/n-patch.md" >}} \
     --set agentgateway.enabled=true  \
     --set controller.image.pullPolicy=Always
   ```
   {{< /version >}}
   {{< version include-if="2.2.x" >}}
   ```sh
   helm upgrade -i kgateway oci://cr.kgateway.dev/kgateway-dev/charts/kgateway \
     --namespace kgateway-system \
     --version v{{< reuse "docs/versions/patch-dev.md" >}} \
     --set agentgateway.enabled=true  \
     --set controller.image.pullPolicy=Always \
     --set controller.extraEnv.KGW_ENABLE_GATEWAY_API_EXPERIMENTAL_FEATURES=true
   ```
   {{< /version >}}

4. Make sure that the `kgateway` control plane is running.

   ```sh
   kubectl get pods -n kgateway-system
   ```

   Example output:

   ```console
   NAME                        READY   STATUS    RESTARTS   AGE
   kgateway-5495d98459-46dpk   1/1     Running   0          19s
   ```