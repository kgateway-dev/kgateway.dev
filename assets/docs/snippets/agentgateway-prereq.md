1. [Install {{< reuse "/docs/snippets/kgateway.md" >}}]({{< link-hextra path="/quickstart/" >}}) and enable the {{< reuse "docs/snippets/agentgateway.md" >}} integration.
2. Verify that the {{< reuse "docs/snippets/agentgateway.md" >}} integration is enabled. 
   ```sh
   helm get values {{< reuse "/docs/snippets/helm-kgateway.md" >}} -n {{< reuse "docs/snippets/namespace.md" >}} -o yaml
   ```
   
   Example output: 
   ```
   agentGateway:
     enabled: true
   ```