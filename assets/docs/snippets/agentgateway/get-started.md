1. Deploy the Kubernetes Gateway API CRDs.

   {{< tabs items="Standard, Experimental" tabTotal="2" >}}
   {{% tab tabName="Standard" %}}
   ```sh
   kubectl apply -f https://github.com/kubernetes-sigs/gateway-api/releases/download/v{{< reuse "docs/versions/k8s-gw-version.md" >}}/standard-install.yaml
   ```
   {{% /tab %}}
   {{% tab tabName="Experimental" %}}
   ```sh
   kubectl apply --server-side -f https://github.com/kubernetes-sigs/gateway-api/releases/download/v{{< reuse "docs/versions/k8s-gw-version.md" >}}/experimental-install.yaml
   ```  
   {{% /tab %}}
   {{< /tabs >}}

2. Deploy the CRDs for the kgateway control plane and agentgateway data plane by using Helm.
   {{< version include-if="2.2.x" >}}
   ```sh
   helm upgrade -i --create-namespace --namespace kgateway-system --version v{{< reuse "docs/versions/patch-dev.md" >}} \
   kgateway-crds oci://cr.kgateway.dev/kgateway-dev/charts/kgateway-crds \
   --set controller.image.pullPolicy=Always
   ```
   {{< /version >}}
   {{< version include-if="2.1.x" >}}
   ```sh
   helm upgrade -i --create-namespace --namespace kgateway-system --version v{{< reuse "docs/versions/n-patch.md" >}} kgateway-crds oci://cr.kgateway.dev/kgateway-dev/charts/kgateway-crds
   ```
   {{< /version >}}

3. Install the kgateway control plane by using Helm. Make sure to enable the agentgateway feature flag, `--set agentgateway.enabled=true`. {{< version include-if="2.2.x" >}} To use experimental Gateway API features, include the experimental feature gate, `--set controller.extraEnv.KGW_ENABLE_GATEWAY_API_EXPERIMENTAL_FEATURES=true`.{{< /version >}}
   {{< version include-if="2.1.x" >}}
   ```sh
   helm upgrade -i --namespace kgateway-system --version v{{< reuse "docs/versions/n-patch.md" >}} kgateway oci://cr.kgateway.dev/kgateway-dev/charts/kgateway \
     --set agentgateway.enabled=true  \
     --set controller.image.pullPolicy=Always
   ```
   {{< /version >}}
   {{< version include-if="2.2.x" >}}
   ```sh
   helm upgrade -i --namespace kgateway-system --version v{{< reuse "docs/versions/patch-dev.md" >}} kgateway oci://cr.kgateway.dev/kgateway-dev/charts/kgateway \
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