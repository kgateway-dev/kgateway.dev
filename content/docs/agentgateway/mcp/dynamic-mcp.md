---
title: Dynamic MCP
weight: 20
---

Route to a dynamic Model Context Protocol (MCP) server by using a label selector. For more information, see the [About MCP](../#about) topic.

{{< callout type="warning" >}}
Note that only streamable HTTP is currently supported for label selectors. If you have SSE, use a [static MCP Backend](../static-mcp/).
{{< /callout >}}

## Before you begin

{{< reuse "docs/snippets/prereq-agw.md" >}}

## Step 1: Deploy an MCP server {#mcp-server}

Deploy an MCP server that you want agentgateway to proxy traffic to. The following example sets up an MCP server that provides various utility tools.

1. Create an MCP server (`mcp-server`) that provides various utility tools. Notice that the Service uses the `appProtocol: kgateway.dev/mcp` setting. This way, kgateway configures the agentgateway proxy to use MCP for the Backend that you create in the next step.

   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: apps/v1
   kind: Deployment
   metadata:
     name: mcp-server
     labels:
       app: mcp-server
   spec:
     replicas: 1
     selector:
       matchLabels:
         app: mcp-server
     template:
       metadata:
         labels:
           app: mcp-server
       spec:
         containers:
           - name: mcp-server
             image: node:20-alpine
             command: ["npx"]
             args: ["-y", "@modelcontextprotocol/server-everything", "streamableHttp"]
             ports:
               - containerPort: 3001
   ---
   apiVersion: v1
   kind: Service
   metadata:
     name: mcp-server
     labels:
       app: mcp-server
   spec:
     selector:
       app: mcp-server
     ports:
       - protocol: TCP
         port: 3001
         targetPort: 3001
         appProtocol: kgateway.dev/mcp
     type: ClusterIP
   EOF
   ```

2. Create a Backend that uses label selectors.

   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.kgateway.dev/v1alpha1
   kind: Backend
   metadata:
     name: mcp-backend
   spec:
     type: MCP
     mcp:
       name: mcp-virtual-server
       targets:
         - selectors:
             serviceSelector:
               matchLabels:
                 app: mcp-server
   EOF
   ```

## Step 2: Route with agentgateway {#agentgateway}

Route to the MCP server with agentgateway.

1. Create a Gateway resource that uses the `agentgateway` GatewayClass. Kgateway automatically creates an agentgateway proxy for you.

   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.networking.k8s.io/v1
   kind: Gateway
   metadata:
     name: agentgateway
   spec:
     gatewayClassName: agentgateway
     listeners:
     - protocol: HTTP
       port: 8080
       name: http
       allowedRoutes:
         namespaces:
           from: All
   EOF
   ```

2. Verify that the Gateway is created successfully. You can also review the external address that is assigned to the Gateway. Note that depending on your environment it might take a few minutes for the load balancer service to be assigned an external address. If you are using a local Kind cluster without a load balancer such as `metallb`, you might not have an external address.

   ```sh
   kubectl get gateway agentgateway
   ```

   Example output: 
   
   ```txt
   NAME           CLASS          ADDRESS                                  PROGRAMMED   AGE
   agentgateway   agentgateway   1234567890.us-east-2.elb.amazonaws.com   True         93s
   ```

3. Create an HTTPRoute resource that routes to the Backend that you created in the previous step.

   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.networking.k8s.io/v1
   kind: HTTPRoute
   metadata:
     name: mcp
   spec:
     parentRefs:
     - name: agentgateway
       namespace: default
     rules:
       - backendRefs:
         - name: mcp-backend
           group: gateway.kgateway.dev
           kind: Backend   
   EOF
   ```

## Step 3: Verify the connection {#verify}

Use the [MCP Inspector tool](https://modelcontextprotocol.io/legacy/tools/inspector) to verify that you can connect to your MCP server through agentgateway.

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
   kubectl port-forward deployment/agentgateway 8080:80
   ```
   {{% /tab %}}
   {{< /tabs >}}

2. From the terminal, run the MCP Inspector command. Then, the MCP Inspector opens in your browser.
   
   ```sh
   npx github:modelcontextprotocol/inspector
   ```
   
3. From the MCP Inspector menu, connect to your agentgateway address as follows:
   * **Transport Type**: Select `Streamable HTTP`.
   * **URL**: Enter the agentgateway address and the `/mcp` path, such as `${INGRESS_GW_ADDRESS}/mcp` or `http://localhost:8080/mcp`.
   * Click **Connect**.

   {{< reuse-image src="img/mcp-inspector-connected.png" >}}
   {{< reuse-image-dark srcDark="img/mcp-inspector-connected-dark.png" >}}

4. From the menu bar, click the **Tools** tab. You should now see tools from the MCP server, such as `fetch`, `echo`, `random_number`, etc.

5. Test the tools: Click **List Tools** and select the `fetch` tool. In the **url** field, enter a website URL, such as `https://lipsum.com/`, and click **Run Tool**.

## Cleanup

{{< reuse "docs/snippets/cleanup.md" >}}

```sh
kubectl delete Deployment mcp-server
kubectl delete Service mcp-server
kubectl delete Backend mcp-backend
kubectl delete Gateway agentgateway
kubectl delete HTTPRoute mcp
```