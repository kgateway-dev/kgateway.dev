1. Create the MCP server workload. Notice the following details about the Service:
   * `appProtocol: kgateway.dev/mcp` (required): Configure your service to use the MCP protocol. This way, the {{< reuse "docs/snippets/agentgateway.md" >}} proxy uses the MCP protocol when connecting to the service.
   * `kgateway.dev/mcp-path` annotation (optional): The default values are `/sse` for the SSE protocol or `/mcp` for the Streamable HTTP protocol. If you need to change the path of the MCP target endpoint, set this annotation on the Service.

   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: apps/v1
   kind: Deployment
   metadata:
     name: mcp-website-fetcher
   spec:
     selector:
       matchLabels:
         app: mcp-website-fetcher
     template:
       metadata:
         labels:
           app: mcp-website-fetcher
       spec:
         containers:
         - name: mcp-website-fetcher
           image: ghcr.io/peterj/mcp-website-fetcher:main
           imagePullPolicy: Always
   ---
   apiVersion: v1
   kind: Service
   metadata:
     name: mcp-website-fetcher
     labels:
       app: mcp-website-fetcher
   spec:
     selector:
       app: mcp-website-fetcher
     ports:
     - port: 80
       targetPort: 8000
       appProtocol: kgateway.dev/mcp
   EOF
   ```

2. Create a Backend that sets up the {{< reuse "docs/snippets/agentgateway.md" >}} target details for the MCP server. 

   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.kgateway.dev/v1alpha1
   kind: Backend
   metadata:
     name: mcp-backend
   spec:
     type: MCP
     mcp:
       targets:
       - name: mcp-target
         static:
           host: mcp-website-fetcher.default.svc.cluster.local
           port: 80
           protocol: SSE   
   EOF
   ```
