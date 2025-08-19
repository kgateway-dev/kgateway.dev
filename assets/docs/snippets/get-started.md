1. Deploy the Kubernetes Gateway API CRDs.

   ```sh
   kubectl apply -f https://github.com/kubernetes-sigs/gateway-api/releases/download/v{{< reuse "docs/versions/k8s-gw-version.md" >}}/standard-install.yaml
   ```

2. Deploy the kgateway CRDs by using Helm. The following command uses the latest stable release, v{{< reuse "docs/versions/n-patch.md" >}}. For active development, update the version to v{{< reuse "docs/versions/patch-dev.md" >}}.

   {{< tabs items="Latest, Development" tabTotal="2">}}
   {{% tab tabName="Latest" %}}
   ```sh
   helm upgrade -i --create-namespace --namespace kgateway-system --version v{{< reuse "docs/versions/n-patch.md" >}} kgateway-crds oci://cr.kgateway.dev/kgateway-dev/charts/kgateway-crds
   ```
   {{% /tab %}}

   {{% tab tabName="Development" %}}
   ```sh
   helm upgrade -i --create-namespace --namespace kgateway-system --version v{{< reuse "docs/versions/patch-dev.md" >}} \
   kgateway-crds oci://cr.kgateway.dev/kgateway-dev/charts/kgateway-crds \
   --set controller.image.pullPolicy=Always
   ```
   {{% /tab %}}
   {{< /tabs >}}
3. Install kgateway by using Helm. The following command uses the latest stable release, v{{< reuse "docs/versions/n-patch.md" >}}. For active development, update the version to v{{< reuse "docs/versions/patch-dev.md" >}}.

   {{< tabs items="Latest, Development" tabTotal="2">}}
   {{% tab tabName="Latest" %}}
   ```sh
   helm upgrade -i --namespace kgateway-system --version v{{< reuse "docs/versions/n-patch.md" >}} kgateway oci://cr.kgateway.dev/kgateway-dev/charts/kgateway
   ```
   {{% /tab %}}

   {{% tab tabName="Development" %}}
   ```sh
   helm upgrade -i --namespace kgateway-system --version v{{< reuse "docs/versions/patch-dev.md" >}} \
   kgateway oci://cr.kgateway.dev/kgateway-dev/charts/kgateway \
   --set controller.image.pullPolicy=Always
   ```
   {{% /tab %}}
   {{< /tabs >}}

4. Make sure that `kgateway` is running.

   ```sh
   kubectl get pods -n kgateway-system
   ```

   Example output:

   ```console
   NAME                        READY   STATUS    RESTARTS   AGE
   kgateway-5495d98459-46dpk   1/1     Running   0          19s
   ```