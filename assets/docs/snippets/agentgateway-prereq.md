1. [Install {{< reuse "/docs/snippets/kgateway.md" >}}]({{< link-hextra path="/quickstart/" >}}) and enable the {{< gloss "Agentgateway" >}}agentgateway{{< /gloss >}} integration.
2. Verify that the {{< gloss "Agentgateway" >}}agentgateway{{< /gloss >}} integration is enabled. 
   ```sh
   helm get values {{< reuse "/docs/snippets/helm-kgateway.md" >}} -n {{< reuse "docs/snippets/namespace.md" >}} | grep agentgateway
   ```

   Example output: 
   ```
   agentgateway:
     enabled: true
   ```