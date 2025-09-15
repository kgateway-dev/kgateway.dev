---
title: Static MCP
weight: 10
---

Route to a Model Context Protocol (MCP) server through a static address. For more information, see the [About MCP]({{< link-hextra path="/agentgateway/mcp/about" >}}) topic.

## Before you begin

{{< reuse "docs/snippets/agentgateway-prereq.md" >}}

## Step 1: Deploy an MCP server {#mcp-server}

Deploy a Model Context Protocol (MCP) server that you want {{< reuse "docs/snippets/agentgateway.md" >}} to proxy traffic to. The following example sets up a simple MCP server with one tool, `fetch`, that retrieves the content of a website URL that you pass in.

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
       name: mcp-server
       targets:
       - name: mcp-target
         static:
           host: mcp-website-fetcher.default.svc.cluster.local
           port: 80
           protocol: SSE   
   EOF
   ```

## Step 2: Route with agentgateway {#agentgateway}

Route to the MCP server with {{< reuse "docs/snippets/agentgateway.md" >}}.

1. Create a Gateway resource that uses the `{{< reuse "docs/snippets/agw-gatewayclass.md" >}}` GatewayClass. Kgateway automatically spins up an {{< reuse "docs/snippets/agentgateway.md" >}} proxy for you.

   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.networking.k8s.io/v1
   kind: Gateway
   metadata:
     name: agentgateway
   spec:
     gatewayClassName: {{< reuse "/docs/snippets/agw-gatewayclass.md" >}}
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
   NAME            CLASS          ADDRESS                                  PROGRAMMED   AGE
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

## Step 3: Verify the connection {#verify}

Use the [MCP Inspector tool](https://modelcontextprotocol.io/legacy/tools/inspector) to verify that you can connect to your sample MCP server through agentgateway.

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

   {{< reuse-image src="img/mcp-inspector-connected.png" >}}
   {{< reuse-image-dark srcDark="img/mcp-inspector-connected-dark.png" >}}

4. From the menu bar, click the **Tools** tab. Then from the **Tools** pane, click **List Tools** and select the `fetch` tool. 
5. From the **fetch** pane, in the **url** field, enter a website URL, such as `https://lipsum.com/`, and click **Run Tool**.
6. Verify that you get back the fetched URL content.

   {{< reuse-image src="img/mcp-inspector-fetch.png" >}}
   {{< reuse-image-dark srcDark="img/mcp-inspector-fetch-dark.png" >}}

## Cleanup

{{< reuse "docs/snippets/cleanup.md" >}}

```sh
kubectl delete Deployment mcp-website-fetcher
kubectl delete Service mcp-website-fetcher
kubectl delete Backend mcp-backend
kubectl delete Gateway agentgateway
kubectl delete HTTPRoute mcp
```
