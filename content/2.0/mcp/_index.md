---
title: MCP Gateway
weight: 460
description: Spin up an MCP Gateway with out-of-the-box authorization capabilities to protect your MCP tools. 
---

Spin up your own Model Context Protocol (MCP) Gateway to federate any number of MCP tool servers into a single MCP endpoint. An MCP Gateway allows you to centrally manage discovery, security, observability, traffic management, and governance of MCP tools, while seamlessly multiplexing requests from MCP clients to upstream MCP tool servers. 

## About the Model Context Protocol (MCP)

[Model Context Protocol (MCP)](https://modelcontextprotocol.io/introduction) is an open protocol that standardizes how Large Language Model (LLM) applications connect to various external data sources and tools. Without MCP, you need to implement custom integrations for each tool that your LLM application needs to access. However, this approach is hard to maintain and can cause issues when you want to scale your environment. With MCP, you can significantly speed up, simplify, and standardize these types of integrations.

### How can kgateway help?

While MCP provides an excellent foundation for interoperability between agents and tools, there are still challenges to address when integrating MCP clients and MCP tool server implementations. Kgateway addresses common friction points in securing, scaling, and integrating MCP clients with tool servers, including:

* Simplifying tool onboarding with automated discovery and registration of MCP tool servers.
* Providing developers with a centralized registry of MCP tools across heterogeneous tool servers regardless of their location.
* Enabling access to any MCP tool by using a single endpoint with innovative MCP multiplexing that turns an entire ecosystem of thousands of tools into a virtualized MCP tool server.
* Instantly securing MCP tool server implementations by providing consistent authentication and authorization controls for multi-tenant consumption.
* Providing deep insights and observability into AI agent and tool integrations with centralized metrics, logging, and tracing for all tool calls.


### MCP server security

An MCP server exposes external data sources and tools so that LLM applications can access them. Typically, you want to deploy these servers remotely and have authorization mechanisms in place so that LLM applications can safely access the data. 

MCP recently introduced the [MCP Authorization spec](https://spec.modelcontextprotocol.io/specification/2025-03-26/basic/authorization/) that is based on OAuth 2.1. While this spec describes how MCP servers should handle authorization requests to MCP tools, it now requires the MCP server to serve as both a resource server and an authorization server. This requirement can cause a burden on enterprises that implement their own MCP servers, especially if the server must be integrated into an existing security infrastructure or when other authorization mechanisms are already in place. 


## About this guide

In this guide, you explore how to configure kgateway as an MCP Gateway to protect access to a sample MCP tool, `convert_to_markdown`. You use a sample MCP server deployment that is exposed on the MCP Gateway. However, you can easily plug in your own MCP server image if you want to. 

{{< reuse-image src="img/mcp-example.svg" width="500px"  >}}

## Before you begin

1. Install the MCP Gateway custom resources. 
   ```sh
   helm upgrade -i --create-namespace --namespace kgateway-system --version v2.0.0-mcpdemo kgateway-crds oci://us-docker.pkg.dev/developers-369321/gloo-platform-dev/charts/kgateway-crds
   ```

2. Install or upgrade your kgateway installation to add the MCP Gateway capabilities.
   ```sh
   helm upgrade -i --namespace kgateway-system --version v2.0.0-mcpdemo kgateway oci://us-docker.pkg.dev/developers-369321/gloo-platform-dev/charts/kgateway --set controller.image.registry=us-docker.pkg.dev/developers-369321/gloo-platform-dev --set controller.image.tag=2.0.0-mcpdemo --set image.tag=v2.0.0
   ```

## Set up an MCP Gateway

Use a sample MCP server image to deploy your own MCP Gateway. 

1. Create a GatewayParameters resource that allows you to set up self-managed Gateways. The GatewayParameters resource instructs kgateway to not automatically spin up a gateway proxy, but instead wait for your custom gateway proxy deployment.  
   ```yaml
   kubectl apply -f- <<EOF
   kind: GatewayParameters
   apiVersion: gateway.kgateway.dev/v1alpha1
   metadata:
     name: kgateway
   spec:
     selfManaged: {}
   EOF
   ```

2. Create a GatewayClass for your MCP Gateway and bind it to the custom GatewayParameters that you created earlier. 
   ```yaml
   kubectl apply -f- <<EOF
   kind: GatewayClass
   apiVersion: gateway.networking.k8s.io/v1
   metadata:
     name: mcp
   spec:
     controllerName: kgateway.dev/kgateway
     parametersRef:
       group: gateway.kgateway.dev
       kind: GatewayParameters
       name: kgateway
       namespace: default
   EOF
   ```

3. Create a Gateway with the custom GatewayClass. The custom GatewayClass instructs kgateway to not automatically spin up a gateway proxy deployment and to wait for your custom deployment. In this example, you open up an MCP listener on port 8080. 
   ```yaml
   kubectl apply -f- <<EOF
   kind: Gateway
   apiVersion: gateway.networking.k8s.io/v1
   metadata:
     name: mcp-gateway
   spec:
     gatewayClassName: mcp
     listeners:
     - protocol: kgateway.dev/mcp
       port: 8080
       name: http
       allowedRoutes:
         namespaces:
           from: All
   EOF
   ```
   
4. Create your MCP server that serves as your custom gateway proxy deployment. This server is exposed on port 8080, which is the port the Gateway listens on. 
   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: apps/v1
   kind: Deployment
   metadata:
     name: mcp-gateway
   spec:
     selector:
       matchLabels:
         app: mcp-gateway
     template:
       metadata:
         labels:
           app: mcp-gateway
       spec:
         terminationGracePeriodSeconds: 1
         containers:
           - name: mcp-gateway
             image: ghcr.io/mcp-proxy/mcp-proxy:0.0.3
             args:
               - --file=/config/config.json
             env:
               - name: NODE_NAME
                 valueFrom:
                   fieldRef:
                     fieldPath: metadata.name
               - name: POD_NAMESPACE
                 valueFrom:
                   fieldRef:
                     fieldPath: metadata.namespace
               - name: POD_NAME
                 valueFrom:
                   fieldRef:
                     fieldPath: metadata.name
               - name: GW_NAME
                 value:  mcp-gateway
               - name: RUST_BACKTRACE
                 value: "1"
               - name: RUST_LOG
                 value: debug
             volumeMounts:
               - name: config-volume
                 mountPath: /config
         volumes:
           - name: config-volume
             configMap:
               name: mcp-gateway-config
   ---
   apiVersion: v1
   kind: Service
   metadata:
     name: mcp-gateway
   spec:
     selector:
       app: mcp-gateway
     ports:
       - protocol: TCP
         port: 8080
         targetPort: 8080
     type: ClusterIP
   ---
   apiVersion: v1
   kind: ConfigMap
   metadata:
     name: mcp-gateway-config
   data:
     config.json: |
       {
         "type": "xds",
         "xds_address": "http://kgateway.kgateway-system.svc.cluster.local:9977",
         "metadata": {},
         "alt_xds_hostname": "mcp-gateway.default.svc.cluster.local",
         "listener": {
           "type": "sse",
           "host": "0.0.0.0",
           "port": 8080,
           "authn": {
             "type":"jwt",
             "issuer": ["me"],
             "audience": ["me.com"],
               "jwks": {
                 "type": "local",
                   "source":
                     { "type": "file", "data": "/config/jwks.json" }
                   }
           }
         }
       }
     jwks.json: |
       {
         "use": "sig",
         "kty": "EC",
         "kid": "XhO06x8JjWH1wwkWkyeEUxsooGEWoEdidEpwyd_hmuI",
         "crv": "P-256",
         "alg": "ES256",
         "x": "XZHF8Em5LbpqfgewAalpSEH4Ka2I2xjcxxUt2j6-lCo",
         "y": "g3DFz45A7EOUMgmsNXatrXw1t-PG5xsbkxUs851RxSE"
       }
   EOF
   ```
   
5. Create the `convert_to_markdown` MCP tool and expose it on your MCP server. The tool takes human-readable text as an input and converts this input to markdown. 
   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: apps/v1
   kind: Deployment
   metadata:
     name: mcp-tool
   spec:
     selector:
       matchLabels:
         app: mcp-tool
     template:
       metadata:
         labels:
           app: mcp-tool
       spec:
         containers:
           - name: mcp-tool
             image: us-docker.pkg.dev/developers-369321/gloo-platform-dev/markitdown-mcp:2.0.0-mcpdemo
             args:
             - "--sse"
             - "--host=0.0.0.0"
             - "--port=8080"
             ports:
               - containerPort: 8080
   ---
   apiVersion: v1
   kind: Service
   metadata:
     name: mcp-tool
   spec:
     selector:
       app: mcp-tool
     type: ClusterIP
     ports:
       - protocol: TCP
         port: 8080
         targetPort: 8080
         appProtocol: kgateway.dev/mcp
   EOF
   ```
   
6. Verify that the MCP server and tool are up and running. 
   ```sh
   kubectl get pods 
   ```
   
   Example output: 
   ```
   NAME                           READY   STATUS             RESTARTS   AGE
   mcp-gateway-57cc679d99-gvnpp   1/1     Running            0          89s
   mcp-tool-866f878885-qqp2r      1/1     Running            0          89s
   ```
   
## Access the MCP tool

With your MCP Gateway in place, you can now test access to the MCP tool. 

1. Port-forward the MCP Gateway on port 8080. 
   ```sh
   kubectl port-forward svc/mcp-gateway 8080
   ```

2. Install the MCP model inspector tool. 
   
   ```sh
   npx @modelcontextprotocol/inspector
   ```

   Example output:

   ```
   Starting MCP inspector...
   ⚙️ Proxy server listening on port 6277
   🔍 MCP Inspector is up and running at http://127.0.0.1:6274 🚀
   ```


3. Open the MCP model inspector at the address from the output of the previous command, such as [http://127.0.0.1:6274](http://127.0.0.1:6274).

4. Connect to the MCP Gateway. 
   1. Switch the **Transport Type** to **SSE**. 
   2. Change the URL to `http://localhost:8080/sse`. 
   3. Expand the **Authentication** section. 
   4. In the **Bearer Token** field, add a JWT to access the MCP Gateway. You can use the following JWT to try out access to the MCP Gateway. 
      ```sh
      eyJhbGciOiJFUzI1NiIsImtpZCI6IlhoTzA2eDhKaldIMXd3a1dreWVFVXhzb29HRVdvRWRpZEVwd3lkX2htdUkiLCJ0eXAiOiJKV1QifQ.eyJhdWQiOiJtZS5jb20iLCJleHAiOjE5MDA2NTAyOTQsImlhdCI6MTc0MzYyNDc4NywiaXNzIjoibWUiLCJqdGkiOiJlM2MzNjhkYzBmNGUyODdiYzhkYmM2OTIyOTU5ZTA3M2YzMThkNTliYTlhZjdhY2Q0N2ViMWUzZGIyOTZlYTQwIiwibmJmIjoxNzQzNjI0Nzg3LCJzdWIiOiJtZSJ9.IshAKo62yWHwfnt62vR1nfa4SQmpSB-4ceAMXWs1P_rREl2gYj6nJ7HwLM5avv_eyOFbI-3rRZzCMCuNVLAF5w
      ```
   5. Click **Connect** to connect to the MCP Gateway. 
   
   {{< reuse-image src="img/mcp-connect.png" width="300px" >}}
   
5. List the MCP tools that are exposed on the MCP Gateway. 
   1. In the MCP model inspector, go to **Tools**. 
   2. Click **List Tools**. 
   3. Verify that you can see the `convert_to_markdown` tool. 
   
   {{< reuse-image src="img/mcp-tools.png"  >}}

6. Try out the **convert_to_markdown** MCP tool that you deployed earlier. 
   1. Click the **convert_to_markdown** tool. 
   2. In the **uri** field, provide a sample file that you want to convert to markdown. For example, you can download a PDF version of the [Git cheat sheet](https://education.github.com/git-cheat-sheet-education.pdf). 
   3. Click **Run Tool**. 
   
   {{< reuse-image src="img/mcp-run-tool.png" >}}

7. Verify that the request fails, because the MCP Gateway requires an MCPAuthPolicy to be in place to allow access to the tool. 
   
   {{< reuse-image src="img/mcp-failed.png" >}}
   
8. Create an MCPAuthPolicy that allows JWTs with the `sub: me` claim to access the MCP tool. The policy is applied to the `convert_to_markdown` tool. 
   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.kgateway.dev/v1alpha1
   kind: MCPAuthPolicy
   metadata:
     name: mcp-jq-auth
   spec:
     targetRefs:
     - name: mcp-gateway
       group: gateway.networking.k8s.io
       kind: Gateway
     rules:
       - matches:
         - type: JWT
           jwt:
             claim: sub
             value: me
         resource:
           kind: tool
           name: default/mcp-tool:convert_to_markdown
   EOF
   ```

9. To try the tool again, click **Clear**, select the `default/mcp-tool:convert_to_markdown` tool, and click **Run Tool**. Note that this time, the request succeeds, because the MCP Gateway successfully authorized the request. 

   {{< reuse-image src="img/mcp-success.png" >}}
   
## Cleanup


{{< reuse "docs/snippets/cleanup.md" >}}

```sh
kubectl delete mcpauthpolicy mcp-jq-auth
kubectl delete deployment mcp-tool
kubectl delete service mcp-tool
kubectl delete deployment mcp-gateway
kubectl delete service mcp-gateway
kubectl delete configmap mcp-gateway-config
kubectl delete gateway mcp-gateway
kubectl delete gatewayclass mcp
kubectl delete gatewayparameters kgateway
```
   
