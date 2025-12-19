To federate multiple MCP servers on the same gateway, you can use a label selector in the MCP Backend.

This approach makes it easier for you to add more MCP servers by adding labels. It also lets your clients access tools from multiple MCP servers through a single endpoint and MCP connection.

{{< callout type="warning" >}}
Note that only streamable HTTP is currently supported for label selectors. If you have SSE, use a [static MCP Backend](../static-mcp).
{{< /callout >}}

## Before you begin

Set up an [agentgateway proxy]({{< link-hextra path="/agentgateway/setup" >}}). 

## Step 1: Deploy the MCP servers {#mcp-server-everythings}

Deploy multiple Model Context Protocol (MCP) servers that you want agentgateway to proxy traffic to. The following example sets up two MCP servers with different tools: one `npx` based MCP server that provides various utility tools and an MCP server with a website `fetch` tool.

1. Create an MCP server (`mcp-server-everything`) that provides various utility tools. Notice that the Service uses the `appProtocol: kgateway.dev/mcp` setting. This way, {{< reuse "docs/snippets/kgateway.md" >}} configures the agentgateway proxy to look for an equivalent {{< reuse "docs/snippets/backend.md" >}} resource.

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

2. Create another MCP server workload with a website fetcher tool.

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

3. Create an {{< reuse "docs/snippets/backend.md" >}} that selects both MCP servers that you created.

   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: agentgateway.dev/v1alpha1
   kind: {{< reuse "docs/snippets/backend.md" >}}
   metadata:
     name: mcp
   spec:
     mcp:
       targets:
         - name: mcp-server-everything
           selector:
             services:
               matchLabels:
                 app: mcp-server-everything
         - name: mcp-website-fetcher
           static:
             host: mcp-website-fetcher.default.svc.cluster.local
             port: 80
             protocol: SSE
   EOF
   ```

## Step 2: Route with agentgateway {#agentgateway}

Route to the federated MCP servers with agentgateway.

1. Create an HTTPRoute resource that routes to the {{< reuse "docs/snippets/backend.md" >}} that you created in the previous step.
   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.networking.k8s.io/v1
   kind: HTTPRoute
   metadata:
     name: mcp
   spec:
     parentRefs:
     - name: agentgateway-proxy
       namespace: {{< reuse "docs/snippets/namespace.md" >}}
     rules:
       - backendRefs:
         - name: mcp
           group: agentgateway.dev
           kind: {{< reuse "docs/snippets/backend.md" >}} 
   EOF
   ```

2. Check that the HTTPRoute is `Accepted`, selects the Gateway, and includes backend rules for the {{< reuse "docs/snippets/backend.md" >}} that you created.

   ```sh
   kubectl describe httproute mcp
   ```

   Example output:

   ```
   Name:         mcp
   Namespace:    default
   Labels:       <none>
   Annotations:  <none>
   API Version:  gateway.networking.k8s.io/v1
   Kind:         HTTPRoute
   Metadata:
     Creation Timestamp:  2025-08-11T16:16:16Z
     Generation:          1
     Resource Version:    13598
     UID:                    78f649b9-310e-4f21-ac0f-e516f06d8f22
   Spec:
     Parent Refs:
       Group:        gateway.networking.k8s.io
       Kind:         Gateway
       Name:         agentgateway-proxy 
       Namespace:    {{< reuse "docs/snippets/namespace.md" >}}
     Rules:
       Backend Refs:
         Group:   agentgateway.dev
         Kind:    AgentgatewayBackend
         Name:    mcp
         Weight:  1
       Matches:
         Path:
           Type:   PathPrefix
           Value:  /
   Status:
     Parents:
       Conditions:
         Last Transition Time:  2025-12-19T03:13:18Z
         Message:               
         Observed Generation:   2
         Reason:                Accepted
         Status:                True
         Type:                  Accepted
         Last Transition Time:  2025-12-19T14:24:01Z
         Message:               
         Observed Generation:   2
         Reason:                ResolvedRefs
         Status:                True
         Type:                  ResolvedRefs
       Controller Name:         agentgateway.dev/agentgateway
       Parent Ref:
         Group:      gateway.networking.k8s.io
         Kind:       Gateway
         Name:       agentgateway-proxy
         Namespace:  agentgateway-system
   ```


## Step 3: Verify the connection {#verify}

Use the [MCP Inspector tool](https://modelcontextprotocol.io/legacy/tools/inspector) to verify that you can connect to your federated MCP servers through agentgateway.

1. Get the agentgateway address.
   
   {{< tabs items="Cloud Provider LoadBalancer,Port-forward for local testing" tabTotal="2" >}}
   {{% tab tabName="Cloud Provider LoadBalancer" %}}
   ```sh
   export INGRESS_GW_ADDRESS=$(kubectl get gateway agentgateway-proxy -n {{< reuse "docs/snippets/namespace.md" >}} -o=jsonpath="{.status.addresses[0].value}")
   echo $INGRESS_GW_ADDRESS
   ```
   {{% /tab %}}
   {{% tab tabName="Port-forward for local testing"%}}
   ```sh
   kubectl port-forward deployment/agentgateway-proxy -n {{< reuse "docs/snippets/namespace.md" >}} 8080:80
   ```
   {{% /tab %}}
   {{< /tabs >}}

2. From the terminal, run the MCP Inspector command. Then, the MCP Inspector opens in your browser.
   
   ```sh
   npx modelcontextprotocol/inspector#{{% reuse "docs/versions/mcp-inspector.md" %}}
   ```
   
3. From the MCP Inspector menu, connect to your agentgateway address as follows:
   * **Transport Type**: Select `Streamable HTTP`.
   * **URL**: Enter the agentgateway address and the `/mcp` path, such as `${INGRESS_GW_ADDRESS}/mcp` or `http://localhost:8080/mcp`.
   * Click **Connect**.

4. From the menu bar, click the **Tools** tab, and then **List tools**. Verify that you see the tools from both servers. The name of the tools are prepended with the names of the MCP servers that you set up in the {{< reuse "docs/snippets/backend.md" >}}.
   * **`mcp-server-everything-3001_*`**: Tools from the `server-everything` MCP server, like `echo`, `add`, etc.
   * **`mcp-website-fetcher_fetch`**: The `fetch` tool from the website fetcher MCP server.

   {{< reuse-image src="img/mcp-multiplex.png" >}}
   {{< reuse-image-dark srcDark="img/mcp-multiplex-dark.png" >}}

5. Test the federated tools:
   * **Test the `mcp-server-everything-3001_echo` tool**: Click **List Tools** and select the `echo` tool. In the **message** field, enter any string, such as `Hello world`, and click **Run Tool**. Verify that your string is echoed back. 
   * **Test the `mcp-website-fetcher_fetch` tool**: Click **List Tools** and select the `fetch` tool. In the **url** field, enter a website URL, such as `https://lipsum.com/`, and click **Run Tool**.
   

## Cleanup

{{< reuse "docs/snippets/cleanup.md" >}}

```sh
kubectl delete Deployment mcp-server-everything mcp-website-fetcher
kubectl delete Service mcp-server-everything mcp-website-fetcher 
kubectl delete {{< reuse "docs/snippets/backend.md" >}} mcp
kubectl delete HTTPRoute mcp 
```
