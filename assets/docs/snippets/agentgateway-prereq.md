1. [Install the {{< reuse "/docs/snippets/kgateway.md" >}} control plane]({{< link-hextra path="/quickstart/" >}}) and enable the {{< gloss "Agentgateway" >}}agentgateway{{< /gloss >}} integration.
2. Verify that the agentgateway integration is enabled. 
   ```sh
   helm get values {{< reuse "/docs/snippets/helm-kgateway.md" >}} -n {{< reuse "docs/snippets/namespace.md" >}} 
   ```

   Example output: 
   ```
   agentgateway:
     enabled: true
   ```