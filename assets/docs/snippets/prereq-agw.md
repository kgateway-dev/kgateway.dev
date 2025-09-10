1. Follow the [Get started guide](../../quickstart/) to install kgateway with agentgateway enabled.

2. Make sure that agentgateway is enabled in kgateway.

   ```shell
   helm get values {{< reuse "/docs/snippets/helm-kgateway.md" >}} -n {{< reuse "docs/snippets/namespace.md" >}} -o yaml
   ```

   Example output:

   ```yaml
   
   agentGateway:
     enabled: true
   ```