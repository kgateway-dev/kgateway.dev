---
title: Multiplex MCP
weight: 30
---

To federate multiple MCP servers on the same gateway, you can use a label selector in the MCP Backend.

This approach makes it easier for you to add more MCP servers by adding labels. It also lets your clients access tools from multiple MCP servers through a single endpoint and MCP connection.

{{< callout type="warning" >}}
Note that only streamable HTTP is currently supported for label selectors. If you have SSE, use a [static MCP Backend](../static-mcp).
{{< /callout >}}

## Before you begin

Set up an [agentgateway proxy]({{< link-hextra path="/agentgateway/setup" >}}). 

## Step 1: Deploy the MCP servers {#mcp-server-everythings}

Deploy multiple Model Context Protocol (MCP) servers that you want agentgateway to proxy traffic to. The following example sets up two MCP servers with different tools: one `npx` based MCP server that provides various utility tools and an MCP sesrver with a website `fetch` tool.

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

2. Create an {{< reuse "docs/snippets/backend.md" >}} that selects the MCP server that you just created.

   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: agentgateway.dev/v1alpha1
   kind: {{< reuse "docs/snippets/backend.md" >}}
   metadata:
     name: mcp-server-everything
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

3. Create another MCP server workload with a website fetcher tool.

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

4. Create an {{< reuse "docs/snippets/backend.md" >}} for the MCP server. 

   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: agentgateway.dev/v1alpha1
   kind: {{< reuse "docs/snippets/backend.md" >}}
   metadata:
     name: mcp-website-fetcher
   spec:
     mcp:
       targets:
       - name: mcp-website-fetcher
         static:
           host: mcp-website-fetcher.default.svc.cluster.local
           port: 80
           protocol: StreamableHTTP
   EOF
   ```

## Step 2: Route with agentgateway {#agentgateway}

Route to the federated MCP servers with agentgateway.

1. Create an HTTPRoute resource that routes to the {{< reuse "docs/snippets/backend.md" >}}s that you created in the previous steps
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
         - name: mcp-server-everything
           group: agentgateway.dev
           kind: {{< reuse "docs/snippets/backend.md" >}} 
         - name: mcp-website-fetcher
           group: agentgateway.dev
           kind: {{< reuse "docs/snippets/backend.md" >}}  
   EOF
   ```

2. Check that the HTTPRoute is `Accepted`, selects the Gateway, and includes backend rules for both the {{< reuse "docs/snippets/backend.md" >}}s that you created.

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
         Kind:    {{< reuse "docs/snippets/backend.md" >}}
         Name:    mcp-server-everything
         Weight:  1
         Group:   agentgateway.dev
         Kind:    {{< reuse "docs/snippets/backend.md" >}}
         Name:    mcp-website-fetcher
         Weight:  1
       Matches:
         Path:
           Type:   PathPrefix
           Value:  /
   Status:
     Parents:
       Conditions:
         Last Transition Time:  2025-12-18T16:16:16Z
         Message:               Route is accepted
         Observed Generation:   1
         Reason:                Accepted
         Status:                True
         Type:                  Accepted
         Last Transition Time:  2025-12-18T16:17:22Z
         Message:               Route has valid refs
         Observed Generation:   1
         Reason:                ResolvedRefs
         Status:                True
         Type:                  ResolvedRefs
       Controller Name:         agentgateway.dev/agentgateway
       Parent Ref:
         Group:  gateway.networking.k8s.io
         Kind:   Gateway
         Name:   agentgateway-proxy   
   ```


## Step 3: Verify the connection {#verify}

Use the [MCP Inspector tool](https://modelcontextprotocol.io/legacy/tools/inspector) to verify that you can connect to your federated MCP servers through agentgateway.

1. Get the agentgateway address.
   
   {{< tabs items="Cloud Provider LoadBalancer,Port-forward for local testing" tabTotal="2" >}}
   {{% tab tabName="Cloud Provider LoadBalancer" %}}
   ```sh
   export INGRESS_GW_ADDRESS=$(kubectl get gateway agentgateway -o=jsonpath="{.status.addresses[0].value}")
   echo $INGRESS_GW_ADDRESS
   ```
   {{% /tab %}}
   {{% tab tabName="Port-forward for local testing"%}}
   ```sh
   kubectl port-forward deployment/agentgateway 8080:8080
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

4. From the menu bar, click the **Tools** tab. You should now see tools from both MCP servers:
   * **From `mcp-server-everything`**: Tools like `echo`, `add`, etc.
   * **From `mcp-website-fetcher`**: A `fetch` tool. 

5. Test the federated tools:
   * **Test the `echo` tool**: Click **List Tools** and select the `echo` tool. In the **message** field, enter any string, such as `Hello world`, and click **Run Tool**. Verify that your string is echoed back. 
   * **Test the `fetch` tool**: Click **List Tools** and select the `fetch` tool. In the **url** field, enter a website URL, such as `https://lipsum.com/`, and click **Run Tool**.
   

## Cleanup

{{< reuse "docs/snippets/cleanup.md" >}}

```sh
kubectl delete Deployment mcp-server-everything mcp-website-fetcher
kubectl delete Service mcp-server-everything mcp-website-fetcher 
kubectl delete {{< reuse "docs/snippets/backend.md" >}} mcp-server-everything mcp-website-fetcher
kubectl delete HTTPRoute mcp 
```

<!-- TODO CLI steps

You can verify the connection to the MCP server through a command line tool with `curl` requests or a user interface that is provided by the MCP Inspector tool.

### Curl requests in terminal {#cli}

1. Get the address of the Gateway for your MCP routes.
   
   {{< tabs items="Cloud Provider LoadBalancer,Port-forward for local testing" tabTotal="2"  >}}
   {{% tab tabName="Cloud Provider LoadBalancer" %}}
   ```sh
   export INGRESS_GW_ADDRESS=$(kubectl get svc -n default agentgateway -o jsonpath="{.status.loadBalancer.ingress[0]['hostname','ip']}")
   echo $INGRESS_GW_ADDRESS  
   ```
   {{% /tab %}}
   {{% tab tabName="Port-forward for local testing"  %}}
   ```sh
   kubectl port-forward deployment/agentgateway -n default 8080:8080
   ```
   {{% /tab %}}
   {{< /tabs >}}

2. Send a request through the Gateway to start a session.

   {{< tabs items="Cloud Provider LoadBalancer,Port-forward for local testing" tabTotal="2"  >}}
   {{% tab tabName="Cloud Provider LoadBalancer" %}}
   ```sh
   curl -v $INGRESS_GW_ADDRESS:8080/sse
   ```
   {{% /tab %}}
   {{% tab tabName="Port-forward for local testing"  %}}
   ```sh
   curl -v localhost:8080/sse
   ```
   {{% /tab %}}
   {{< /tabs >}}

   Example output:
   ```
   event: endpoint
   data: ?sessionId=c1a54dcb-be11-4f91-91b5-a1abf67deca2
   ```

3. Save the session ID from the output as an environment variable. In the example, the session ID is `c1a54dcb-be11-4f91-91b5-a1abf67deca2`.

   ```sh
   export SESSION_ID=c1a54dcb-be11-4f91-91b5-a1abf67deca2
   ``` 

4. Send a request to initialize the connection with your MCP server.

   {{< tabs items="Cloud Provider LoadBalancer,Port-forward for local testing" tabTotal="2" >}}
   {{% tab tabName="Cloud Provider LoadBalancer" %}}
   ```sh
   curl "$INGRESS_GW_ADDRESS:8080/mcp?sessionId=$SESSION_ID" -v \
     -H "Accept: text/event-stream,application/json" \
     --json '{"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{"roots":{}},"clientInfo":{"name":"claude-code","version":"1.0.60"}},"jsonrpc":"2.0","id":0}'
   ```
   {{% /tab %}}
   {{% tab tabName="Port-forward for local testing" %}}
   ```sh
   curl "http://localhost:8080/mcp?sessionId=$SESSION_ID" -v \
     -H "Accept: text/event-stream,application/json" \
     --json '{"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{"roots":{}},"clientInfo":{"name":"claude-code","version":"1.0.60"}},"jsonrpc":"2.0","id":0}'
   ```
   {{% /tab %}}
   {{< /tabs >}}

   **Note**: If you encounter connection issues, try using the MCP Inspector tool instead, which handles the protocol negotiation automatically.

### Browser-based MCP Inspector {#ui}

-->