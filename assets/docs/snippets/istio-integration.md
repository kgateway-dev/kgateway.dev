Upgrade your {{< reuse "/docs/snippets/kgateway.md" >}} installation to enable the Istio integration so that {{< reuse "/docs/snippets/kgateway.md" >}} works with Istio DestinationRules.

1. Get the Helm values for your current Helm installation. 
   ```sh
   helm get values {{< reuse "/docs/snippets/helm-kgateway.md" >}} -n {{< reuse "docs/snippets/namespace.md" >}} -o yaml > {{< reuse "/docs/snippets/helm-kgateway.md" >}}.yaml
   open {{< reuse "/docs/snippets/helm-kgateway.md" >}}.yaml
   ```
   
2. Add the following values to the Helm values file to enable the Istio integration in {{< reuse "/docs/snippets/kgateway.md" >}}.
   ```yaml

   controller:
     extraEnv:
       KGW_ENABLE_ISTIO_INTEGRATION: true
   ```
   
3. Upgrade your Helm installation.
   
   ```sh
   helm upgrade -i --namespace {{< reuse "docs/snippets/namespace.md" >}} --version {{< reuse "/docs/versions/helm-version-flag.md" >}} {{< reuse "/docs/snippets/helm-kgateway.md" >}} oci://{{< reuse "/docs/snippets/helm-path.md" >}}/charts/{{< reuse "/docs/snippets/helm-kgateway.md" >}} -f {{< reuse "/docs/snippets/helm-kgateway.md" >}}.yaml
   ```
