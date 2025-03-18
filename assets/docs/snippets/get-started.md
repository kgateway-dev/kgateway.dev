2. Deploy the Kubernetes Gateway API CRDs.

   ```sh
   kubectl apply -f https://github.com/kubernetes-sigs/gateway-api/releases/download/v{{< reuse "docs/versions/k8s-gw-version.md" >}}/standard-install.yaml
   ```

3. Deploy the {{< reuse "docs/snippets/product-name.md" >}} CRDs by using Helm.

   ```sh
   helm upgrade -i --create-namespace --namespace {{< reuse "docs/snippets/ns-system.md" >}} --version v{{< reuse "docs/versions/n-patch.md" >}} kgateway-crds oci://cr.kgateway.dev/kgateway-dev/charts/kgateway-crds
   ```

4. Install {{< reuse "docs/snippets/product-name.md" >}} by using Helm.

   ```sh
   helm upgrade -i --namespace {{< reuse "docs/snippets/ns-system.md" >}} --version v{{< reuse "docs/versions/n-patch.md" >}} kgateway oci://cr.kgateway.dev/kgateway-dev/charts/kgateway
   ```

5. Make sure that `kgateway` is running.

   ```sh
   kubectl get pods -n {{< reuse "docs/snippets/ns-system.md" >}}
   ```

   Example output:

   ```
   NAME                        READY   STATUS    RESTARTS   AGE
   kgateway-5495d98459-46dpk   1/1     Running   0          19s
   ```