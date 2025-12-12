Route to a Model Context Protocol (MCP) server dynamically by using a label selector. This way, unlike a static backend, you can update the backing MCP server without having to update the Backend resource. For more information, see the [About MCP]({{< link-hextra path="/agentgateway/mcp/about" >}}) topic.

{{< callout type="warning" >}}
Note that only streamable HTTP is currently supported for label selectors. If you need to use an SSE listener, use a [static MCP Backend](../static-mcp/).
{{< /callout >}}

## Before you begin

Set up an [agentgateway proxy]({{< link-hextra path="/agentgateway/setup" >}}). 

## Step 1: Deploy an MCP server {#mcp-server}

Deploy an MCP server that you want {{< reuse "docs/snippets/agentgateway.md" >}} to proxy traffic to. The following example sets up an MCP server that provides various utility tools.

1. Create an MCP server (`mcp-server`) that provides various utility tools. Notice the following details about the Service:
   * `appProtocol: kgateway.dev/mcp` (required): Configure your service to use the MCP protocol. This way, the agentgateway proxy uses the MCP protocol when connecting to the service.
   * `kgateway.dev/mcp-path` annotation (optional): The default values are `/sse` for the SSE protocol or `/mcp` for the Streamable HTTP protocol. If you need to change the path of the MCP target endpoint, set this annotation on the Service.

   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: apps/v1
   kind: Deployment
   metadata:
     name: mcp-server-everything
     labels:
       app: mcp-server-everything
   spec:
     replicas: 1
     selector:
       matchLabels:
         app: mcp-server-everything
     template:
       metadata:
         labels:
           app: mcp-server-everything
       spec:
         containers:
           - name: mcp-server-everything
             image: node:20-alpine
             command: ["npx"]
             args: ["-y", "@modelcontextprotocol/server-everything", "streamableHttp"]
             ports:
               - containerPort: 3001
   ---
   apiVersion: v1
   kind: Service
   metadata:
     name: mcp-server-everything
     labels:
       app: mcp-server-everything
   spec:
     selector:
       app: mcp-server-everything
     ports:
       - protocol: TCP
         port: 3001
         targetPort: 3001
         appProtocol: kgateway.dev/mcp
     type: ClusterIP
   EOF
   ```

2. Create a {{< reuse "docs/snippets/backend.md" >}} for your MCP server that uses label selectors to select the MCP server.
   {{< version include-if="2.1.x" >}}
   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.kgateway.dev/v1alpha1
   kind: {{< reuse "docs/snippets/backend.md" >}}
   metadata:
     name: mcp-backend
   spec:
     mcp:
       targets:
         - name: mcp-server-everything
           selector:
             services:
               matchLabels:
                 app: mcp-server-everything
   EOF
   ```

   {{< callout type="info" >}}
   Plan to attach policies to your selector-based Backend later? You can still attach the policy to a particular backing Service. To do so, set the `targetRef` setting in the policy to the backing Service, not to the Backend's service selector. Include the `sectionName` of the port that you want the policy to apply to. For an example, check out the [BackendTLSPolicy guide](../../../security/backend-tls/).
   {{< /callout >}}

   {{< /version >}}{{< version include-if="2.2.x" >}}
   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: agentgateway.dev/v1alpha1
   kind: {{< reuse "docs/snippets/backend.md" >}}
   metadata:
     name: mcp-backend
   spec:
     mcp:
       targets:
         - name: mcp-server-everything
           selector:
             services:
               matchLabels:
                 app: mcp-server-everything
   EOF
   ```
   {{< /version >}}

## Step 2: Route with agentgateway {#agentgateway}

Create an HTTPRoute resource that routes to the Backend that you created in the previous step.
{{< version include-if="2.1.x" >}}
```yaml
kubectl apply -f- <<EOF
apiVersion: gateway.networking.k8s.io/v1
kind: HTTPRoute
metadata:
  name: mcp
  labels:
    example: mcp-route
spec:
  parentRefs:
    - name: agentgateway-proxy
      namespace: {{< reuse "docs/snippets/namespace.md" >}}
  rules:
    - backendRefs:
        - name: mcp-backend
          group: gateway.kgateway.dev
          kind: {{< reuse "docs/snippets/backend.md" >}}
EOF
```
{{< /version >}}
{{< version include-if="2.2.x" >}}
```yaml
kubectl apply -f- <<EOF
apiVersion: gateway.networking.k8s.io/v1
kind: HTTPRoute
metadata:
  name: mcp
  labels:
    example: mcp-route
spec:
  parentRefs:
  - name: agentgateway-proxy
    namespace: {{< reuse "docs/snippets/namespace.md" >}}
  rules:
  - backendRefs:
      - name: mcp-backend
        group: agentgateway.dev
        kind: {{< reuse "docs/snippets/backend.md" >}}
EOF
```
{{< /version >}}

## Step 3: Verify the connection {#verify}

Use the [MCP Inspector tool](https://modelcontextprotocol.io/docs/tools/inspector) to verify that you can connect to your MCP server through {{< reuse "docs/snippets/agentgateway.md" >}}.

1. Get the agentgateway address.
   
   {{< tabs items="Cloud Provider LoadBalancer,Port-forward for local testing" tabTotal="2" >}}
   {{% tab tabName="Cloud Provider LoadBalancer" %}}
   ```sh
   export INGRESS_GW_ADDRESS=$(kubectl get gateway agentgateway -n {{< reuse "docs/snippets/namespace.md" >}} -o=jsonpath="{.status.addresses[0].value}")
   echo $INGRESS_GW_ADDRESS
   ```
   {{% /tab %}}
   {{% tab tabName="Port-forward for local testing"%}}
   ```sh
   kubectl port-forward deployment/agentgateway -n {{< reuse "docs/snippets/namespace.md" >}} 8080:80
   ```
   {{% /tab %}}
   {{< /tabs >}}

2. From the terminal, install the MCP Inspector tool. Then, the MCP Inspector opens in your browser. If the MCP inspector tool does not open automatically, run `mcp-inspector`.
   ```sh
   npx modelcontextprotocol/inspector#{{% reuse "docs/versions/mcp-inspector.md" %}}
   ```

3. From the MCP Inspector menu, connect to your agentgateway address as follows:
   * **Transport Type**: Select `Streamable HTTP`.
   * **URL**: Enter the agentgateway address, port, and the `/mcp` path. If your agentgateway proxy is exposed with a LoadBalancer server, use `http://<lb-address>/mcp`. In local test setups where you port-forwarded the agentgateway proxy on your local machine, use `http://localhost:8080/mcp`.
   * Click **Connect**.

4. From the menu bar, click the **Tools** tab, then click **List Tools**.

   {{< reuse-image src="img/mcp-tools-everything.png" >}}
   {{< reuse-image-dark srcDark="img/mcp-tools-everything-dark.png" >}}

5. Test the tools: Select a tool, such as `echo`. In the **message** field, enter a message, such as `Hello, world!`, and click **Run Tool**.

   {{< reuse-image src="img/mcp-tool-echo.png" >}}
   {{< reuse-image-dark srcDark="img/mcp-tool-echo-dark.png" >}}

## Cleanup

{{< reuse "docs/snippets/cleanup.md" >}}

```sh
kubectl delete Deployment mcp-server-everything
kubectl delete Service mcp-server-everything
kubectl delete {{< reuse "docs/snippets/backend.md" >}} mcp-backend
kubectl delete HTTPRoute mcp
```