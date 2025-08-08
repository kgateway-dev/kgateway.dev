1. Follow the [Get started guide](../../quickstart/) to install kgateway.

2. Make sure that agentgateway is enabled in kgateway. For example steps, see the [Setup agentgateway](../setup/#kgateway-setup) guide.

   ```shell
   helm get values {{< reuse "/docs/snippets/helm-kgateway.md" >}} -n {{< reuse "docs/snippets/namespace.md" >}} -o yaml
   ```

   Example output:

   ```yaml
   
   agentgateway:
     enabled: true
   ```