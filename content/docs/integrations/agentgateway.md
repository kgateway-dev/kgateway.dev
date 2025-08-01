---
title: Agentgateway
weight: 10
description: Use kgateway with agentgateway. 
---

Use {{< reuse "/docs/snippets/kgateway.md" >}} as to manage [agentgateway](https://agentgateway.dev/) proxies for AI gateways in a Kubernetes environment. 

## About agentgateway {#about}

Agentgateway is an open source, highly available, highly scalable, and enterprise-grade data plane that provides AI connectivity for agents and tools in any environment. For more information, see the [agentgateway docs](https://agentgateway.dev/docs/about/).

## Step 1: Set up kgateway {#kgateway-setup}

Enable the agentgateway feature in kgateway.

1. Complete the [Get started guide](../../quickstart/) to create a Kubernetes cluster, deploy the Kubernetes Gateway API CRDs, and install kgateway. **Note**: Agentgateway is currently available in the v{{< reuse "docs/versions/patch-dev.md" >}} development release.

2. Upgrade your kgateway installation to enable agentgateway. For complete upgrade instructions, see the [upgrade guide](../../reference/upgrade/).

   ```sh
   helm upgrade -i --namespace kgateway-system --version v{{< reuse "docs/versions/patch-dev.md" >}} kgateway oci://cr.kgateway.dev/kgateway-dev/charts/kgateway \
     --set agentGateway.enabled=true \
     --set agentGateway.enableAlphaAPIs=true
   ```

3. Make sure that `kgateway` is running.

   ```sh
   kubectl get pods -n kgateway-system
   ```

   Example output:

   ```console
   NAME                        READY   STATUS    RESTARTS   AGE
   kgateway-5495d98459-46dpk   1/1     Running   0          19s
   ```

## Step 2: Deploy an MCP server {#mcp-server}

Deploy a Model Context Protocol (MCP) server that you want agentgateway to route traffic to. The following example sets up a simple MCP server.

1. Create the MCP server workload. Notice that the Service uses the `appProtocol: kgateway.dev/mcp` setting. This setting lets the Backend target the Service in the next step.

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

2. Create a Backend that sets up the agentgateway target details for the MCP server. 

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
       - static:
           name: mcp-target
           host: mcp-website-fetcher.default.svc.cluster.local
           port: 80
           protocol: SSE   
   EOF
   ```

## Step 3: Route with agentgateway {#agentgateway}

Route to the MCP server with agentgateway.

1. Create an Gateway resource that uses the `agentgateway` GatewayClass. Kgateway automatically spins up an agentgateway proxy for you.

   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.networking.k8s.io/v1
   kind: Gateway
   metadata:
     name: agent-gateway
   spec:
     gatewayClassName: agentgateway
     listeners:
     - protocol: HTTP
       port: 80
       name: http
   EOF
   ```

2. Verify that the Gateway is created successfully. You can also review the external address that is assigned to the Gateway. Note that depending on your environment it might take a few minutes for the load balancer service to be assigned an external address. If you are using a local Kind cluster without a load balancer such as `metallb`, you might not have an external address.

   ```sh
   kubectl get gateway agent-gateway
   ```

   Example output: 
   
   ```txt
   NAME            CLASS          ADDRESS                                  PROGRAMMED   AGE
   agent-gateway   agentgateway   1234567890.us-east-2.elb.amazonaws.com   True         93s
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
     - name: agent-gateway
     rules:
       - backendRefs:
         - name: mcp-backend
           group: gateway.kgateway.dev
           kind: Backend   
   EOF
   ```

## Step 4: Verify the connection {#verify}

Use the [MCP Inspector tool](https://modelcontextprotocol.io/legacy/tools/inspector) to verify that you can connect to your sample MCP server through agentgateway.

1. Get the agentgateway address.
   
   {{< tabs items="Cloud Provider LoadBalancer,Port-forward for local testing" tabTotal="2" >}}
   {{% tab tabName="Cloud Provider LoadBalancer" %}}
   ```sh
   export AGENTGATEWAY_ADDRESS=$(kubectl get gateway agent-gateway -o=jsonpath="{.status.addresses[0].value}")
   echo $AGENTGATEWAY_ADDRESS
   ```
   {{% /tab %}}
   {{% tab tabName="Port-forward for local testing"%}}
   ```sh
   kubectl port-forward deployment/agent-gateway 8080:80
   ```
   {{% /tab %}}
   {{< /tabs >}}

2. From the terminal, run the MCP Inspector command.
   
   ```sh
   npx github:modelcontextprotocol/inspector
   ```

   The MCP Inspector opens in your browser.

   {{< reuse-image src="img/mcp-inspector-landing.png" >}}
   {{< reuse-image-dark srcDark="img/mcp-inspector-landing-dark.png" >}}
   
3. From the MCP Inspector menu, connect to your agentgateway address as follows:
   * **Transport Type**: Select `Streamable HTTP`.
   * **URL**: Enter the agentgateway address and the `/mcp` path, such as `${AGENTGATEWAY_ADDRESS}/mcp` or `http://localhost:8080/mcp`.
   * Click **Connect**.

   {{< reuse-image src="img/mcp-inspector-connected.png" >}}
   {{< reuse-image-dark srcDark="img/mcp-inspector-connected-dark.png" >}}

4. In the MCP Inspector, select the `mcp-server` server.

   {{< reuse-image src="img/mcp-inspector-connected.png" >}}
   {{< reuse-image-dark srcDark="img/mcp-inspector-connected-dark.png" >}}

5. From the menu bar, click the **Tools** tab. Then from the **Tools** pane, click **List Tools** and select the `fetch` tool. 
6. From the **fetch** pane, in the **url** field, enter a website URL, such as `https://lipsum.com/`, and click **Run Tool**.
7. Verify that you get back the the fetched URL content.

   {{< reuse-image src="img/mcp-inspector-fetch.png" >}}
   {{< reuse-image-dark srcDark="img/mcp-inspector-fetch-dark.png" >}}
