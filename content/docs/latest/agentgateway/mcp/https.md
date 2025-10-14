---
title: Connect via HTTPS
weight: 40 
description: 
---

Configure your agentgateway proxy to connect to an MCP server by using the HTTPS protocol. 

## About this guide 

In this guide, you configure your agentgateway proxy to connect to the remote [GitHub MCP server](https://github.com/github/github-mcp-server) by using the HTTPS protocol. The server allows you to interact with GitHub repositories, issues, pull requests, and more. All connections to the server must be secured via HTTPS and a GitHub access token must be provided for authentication. 

## Before you begin

Set up an [agentgateway proxy]({{< link-hextra path="/agentgateway/setup" >}}). 

## Connect to the MCP server

1. Create a personal acess token in GitHub and save it in an environment variable. For more information, see the [GitHub docs](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens).
   ```sh
   export GH_PAT=<personal-access-token>
   ```

2. Create a Backend for the remote GitHub MCP server. The server requires you to connect to it by using the HTTPS protocol. Because of that, you set the `mcp.targets.static.port` field to 443. 
   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.kgateway.dev/v1alpha1
   kind: Backend
   metadata:
     name: github-mcp-backend
     namespace: {{< reuse "docs/snippets/namespace.md" >}}
   spec:
     type: MCP
     mcp:
       targets:
       - name: mcp-target
         static:
           host: api.githubcopilot.com
           port: 443
           path: /mcp/
   EOF
   ```
   
   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.kgateway.dev/v1alpha1
   kind: Backend
   metadata:
     name: web-mcp-backend
     namespace: {{< reuse "docs/snippets/namespace.md" >}}
   spec:
     type: MCP
     mcp:
       targets:
       - name: mcp-target
         static:
           host: www.mcp.run
           port: 443
           path: /api/mcp/sse?sid=Fe26.2**3f65a0f4948e0a5cdefe39463778382c71d5355e47381786e9faca0a946937c1*HTf-pQXlsY3596VdrbUt3A*NsUmLUTIAeqcFCXNxxKAhNgaPkHobsKSe06X-QnLll8*1759510756907*00e6a1151933abe52d02142c1a4e3dfcc3e7dc57ba83b5b8e5ee978364994f44*jDQg0mN9ahClPQaS64Za-EGwd5dQbvo98q5JrW2sr5A
   EOF
   ```
   
3. Create a BackendTLSPolicy to configure your agentgateway to connect to your Backend by using HTTPS. To validate the MCP server's TLS certificate, you use the well-known system CA certificates. Note that to use the BackendTLSPolicy, you must have the experimental channel of the Kubernetes Gateway API version 1.4 or later.
   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.networking.k8s.io/v1
   kind: BackendTLSPolicy
   metadata:
     name: github-mcp-backend-tls
     namespace: {{< reuse "docs/snippets/namespace.md" >}}
   spec:
     targetRefs:
       - name: github-mcp-backend
         kind: Backend
         group: gateway.kgateway.dev
     validation:
       hostname: api.githubcopilot.com
       wellKnownCACertificates: System
   EOF
   ```
   
   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.networking.k8s.io/v1
   kind: BackendTLSPolicy
   metadata:
     name: github-mcp-backend-tls
     namespace: {{< reuse "docs/snippets/namespace.md" >}}
   spec:
     targetRefs:
       - name: web-mcp-backend
         kind: Backend
         group: gateway.kgateway.dev
     validation:
       hostname: api.githubcopilot.com
       wellKnownCACertificates: System
   EOF
   ```

4. Create an HTTPRoute that routes traffic to the GitHub MCP server along the `/mcp-github` path. To properly connect to the MCP server, you must allow traffic from `http://localhost:8080`, which is the domain and port you expose your agentgateway proxy on later. If you expose the proxy under a different domain, make sure to add this domain to the allowed origins. Because the MCP server also requires a GitHub access token to connect, you set the `Authorization` header to the token that you created earlier. 
   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.networking.k8s.io/v1
   kind: HTTPRoute
   metadata:
     name: mcp-github
     namespace: {{< reuse "docs/snippets/namespace.md" >}}
   spec:
     parentRefs:
     - name: agentgateway
     rules:
       - matches:
           - path:
               type: PathPrefix
               value: /mcp-github
         filters:
           - type: CORS
             cors:
               allowHeaders:
                 - "*"               
               allowMethods:            
                 - "*"              
               allowOrigins:
                 - "http://localhost:8080"
           - type: RequestHeaderModifier
             requestHeaderModifier:
               set: 
                 - name: Authorization
                   value: "Bearer ${GH_PAT}"
         backendRefs:
         - name: github-mcp-backend
           group: gateway.kgateway.dev
           kind: Backend  
   EOF
   ```
   
## Verify the connection {#verify}

Use the [MCP Inspector tool](https://modelcontextprotocol.io/legacy/tools/inspector) to verify that you can connect to your sample MCP server through agentgateway.

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
   kubectl port-forward deployment/agentgateway 8080:8080 -n {{< reuse "docs/snippets/namespace.md" >}}
   ```
   {{% /tab %}}
   {{< /tabs >}}

2. From your terminal, run the MCP Inspector command to open the MCP Inspector in your browser. If the MCP inspector tool does not open automatically, run `mcp-inspector`.
   ```sh
   npx modelcontextprotocol/inspector#{{% reuse "docs/versions/mcp-inspector.md" %}}
   ```
   
3. From the MCP Inspector menu, connect to your agentgateway address as follows:
   * **Transport Type**: Select `Streamable HTTP`.
   * **URL**: Enter the agentgateway address, port, and the `/mcp-github` path. If your agentgateway proxy is exposed with a LoadBalancer server, use `http://<lb-address>:8080/mcp-github`. In local test setups where you port-forwarded the agentgateway proxy on your local machine, use `http://localhost:8080/mcp-github`.
   * Click **Connect**.

4. From the menu bar, click the **Tools** tab. Then from the **Tools** pane, click **List Tools** and select the `get_issue` tool. 
5. From the **get_issue** pane, enter the following details, and click **Run Tool**.
   * `issue_number`: 427
   * `owner`: agentgateway
   * `repo`: agentgateway 
6. Verify that you get back the fetched issue content.

   {{< reuse-image src="img/mcp-inspector-gh.png" >}}
   {{< reuse-image-dark srcDark="img/mcp-inspector-gh-dark.png" >}}
   

   
## Cleanup

{{< reuse "docs/snippets/cleanup.md" >}}

```sh
kubectl delete Backend github-mcp-backend -n {{< reuse "docs/snippets/namespace.md" >}}
kubectl delete BackendTLSPolicy github-mcp-backend-tls -n {{< reuse "docs/snippets/namespace.md" >}}
kubectl delete HTTPRoute mcp-github -n {{< reuse "docs/snippets/namespace.md" >}}
```


