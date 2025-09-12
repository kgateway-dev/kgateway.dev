1. [Install {{< reuse "/docs/snippets/kgateway.md" >}}]({{< link path="/quickstart" >}}) and enable the agentgateway integration.
2. Verify that the agentgateway and AI extensions are enabled. 
   ```sh
   helm get values {{< reuse "/docs/snippets/helm-kgateway.md" >}} -n {{< reuse "docs/snippets/namespace.md" >}} -o yaml
   ```
   
   Example output: 
   ```
   
   agentGateway:
     enabled: true
   ```