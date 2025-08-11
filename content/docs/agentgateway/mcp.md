---
title: MCP
weight: 30
---

Route to Model Context Protocol (MCP) servers through agentgateway.

## About MCP {#about}

[Model Context Protocol (MCP)](https://modelcontextprotocol.io/introduction) is an open protocol that standardizes how Large Language Model (LLM) applications connect to various external data sources and tools. Without MCP, you need to implement custom integrations for each tool that your LLM application needs to access. However, this approach is hard to maintain and can cause issues when you want to scale your environment. With MCP, you can significantly speed up, simplify, and standardize these types of integrations.

An MCP server exposes external data sources and tools so that LLM applications can access them. Typically, you want to deploy these servers remotely and have authorization mechanisms in place so that LLM applications can safely access the data.

With agentgateway, you can connect to one or multiple MCP servers in any environment. The agentgateway proxies requests to the MCP tool that is exposed on the server. You can also use the agentgateway to federate tools from multiple MCP servers.

## Before you begin

{{< reuse "docs/snippets/prereq-agw.md" >}}

## Static MCP {#static}

Follow the [Setup guide](../setup/) to deploy a static MCP server and create a Backend that routes to it.

Static MCP supports both SSE and streamable HTTP protocols.

## Dynamic label-based MCP {#dynamic}

You can use a label selector in the MCP Backend.

{{< callout type="warning" >}}
Note that only streamable HTTP is currently supported for label selectors. If you have SSE, use a [static MCP Backend](#static).
{{< /callout >}}

### Step 1: Deploy an MCP server {#mcp-server}

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

### Step 2: Route with agentgateway {#agentgateway}

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

### Step 3: Verify the connection {#verify}

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

### Cleanup

{{< reuse "docs/snippets/cleanup.md" >}}

```sh
kubectl delete Deployment mcp-server
kubectl delete Service mcp-server
kubectl delete Backend mcp-backend
kubectl delete Gateway agentgateway
kubectl delete HTTPRoute mcp
```

<!-- TODO: Multiplex MCP

## Multiplex MCP {#multiplex}

To federate multiple MCP servers on the same gateway, you can use a label selector in the MCP Backend.

This approach makes it easier for you to add more MCP servers by adding labels. It also lets your clients access tools from multiple MCP servers through a single endpoint and MCP connection.

{{< callout type="warning" >}}
Note that only streamable HTTP is currently supported for label selectors. If you have SSE, use a [static MCP Backend](#static).
{{< /callout >}}

### Step 1: Deploy MCP servers {#mcp-servers}

Deploy multiple Model Context Protocol (MCP) servers that you want agentgateway to proxy traffic to. The following example sets up two MCP servers with different tools: one `npx` based MCP server that provides various utility tools and a Python-based `uvx` MCP server that provides time-related tools.

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
           - name: mcp-everything
             image: node:20-alpine
             command: ["npx"]
             args: ["-y", "@modelcontextprotocol/server-everything", "streamableHttp", "--port", "3002"]
             ports:
               - containerPort: 3002
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
       - name: mcp-server
         protocol: TCP
         port: 3001
         targetPort: 3001
         appProtocol: kgateway.dev/mcp
       - name: mcp-everything
         protocol: TCP
         port: 3002
         targetPort: 3002
         appProtocol: kgateway.dev/mcp
     type: ClusterIP
   EOF
   ```

2. Create a Backend that uses label selectors to discover and federate both MCP servers.

   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.kgateway.dev/v1alpha1
   kind: Backend
   metadata:
     name: mcp-backend
   spec:
     type: MCP
     mcp:
       name: mcp-federated-server
       targets:
         - selectors:
             serviceSelector:
               matchLabels:
                 app: mcp-server
   EOF
   ```

### Step 2: Route with agentgateway {#agentgateway}

Route to the federated MCP servers with agentgateway.

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
     rules:
       - backendRefs:
         - name: mcp-backend
           group: gateway.kgateway.dev
           kind: Backend   
   EOF
   ```

### Step 3: Verify the connection {#verify}

You can verify the connection to the MCP server through a command line tool with `curl` requests or a user interface that is provided by the MCP Inspector tool.

#### Curl requests in terminal {#cli}

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

#### Browser-based MCP Inspector {#ui}

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

4. From the menu bar, click the **Tools** tab. You should now see tools from both MCP servers:
   * **From `mcp-server`**: Tools like `fetch`, `echo`, `random_number`, etc.
   * **From `mcp-server-filesystem`**: Tools like `read_file`, `write_file`, `list_directory`, etc.

5. Test the federated tools:
   * **Test the `fetch` tool**: Click **List Tools** and select the `fetch` tool. In the **url** field, enter a website URL, such as `https://lipsum.com/`, and click **Run Tool**.
   * **Test the `list_directory` tool**: Click **List Tools** and select the `list_directory` tool. In the **path** field, enter `/tmp`, and click **Run Tool** to list the contents of the temporary directory.

### Cleanup

{{< reuse "docs/snippets/cleanup.md" >}}

```sh
kubectl delete Deployment mcp-server
kubectl delete Deployment mcp-server-filesystem
kubectl delete Service mcp-server
kubectl delete Service mcp-server-filesystem
kubectl delete Backend mcp-backend
kubectl delete Gateway agentgateway
kubectl delete HTTPRoute mcp
```

-->