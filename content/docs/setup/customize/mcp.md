---
title: Model Context Protocol (MCP)
weight: 
description: Spin up your own MCP gateway with out-of-the-box authorization capabilities to protect your MCP tools. 
---

Spin up your own MCP gateway with out-of-the-box authorization capabilities to protect your MCP tools. 

## About the Model Context Protocol (MCP)

[Model Context Protocol (MCP)](https://modelcontextprotocol.io/introduction) is an open protocol that standardizes how Large Language Model (LLM) applications connect to various external data sources and tools. Without MCP, you need to implement custom integrations for each tool that your LLM application needs to access. However, this approach is hard to maintain and can cause issues when you want to scale your environment. With MCP, you can significantly speed up, simplify, and standardize these types of integrations.

### MCP server security

An MCP server exposes external data sources and tools so that LLM applications can access them. Typically, you want to deploy these servers remotely and have authorization mechanisms in place so that LLM applications can safely access the data. 

MCP recently introduced the [MCP Authorization spec](https://spec.modelcontextprotocol.io/specification/2025-03-26/basic/authorization/]) that is based on OAuth 2.1. While this spec describes how MCP servers should handle authorization requests to MCP tools, it now requires the MCP server to serve as both a resource server and an authorization server. This requirement can cause a burden on enterprises that implement their own MCP servers, especially if the server must be integrated into an existing security infrastructure or when other authorization mechanisms are already in place. 

### How can kgateway help?

With kgateway, you can spin up your own MCP Gateway that provides out-of-the-box authorization capabilities for your MCP server. Because the MCP Gateway leverages the Kubernetes Gateway API, you can further harden your MCP Gateway with the traffic management, resiliency, and security policies that you are used to. 

## About this guide

In this guide, you explore how to configure kgateway as an MCP gateway to protect access to a sample MCP tool, `convert_to_markdown`. You use a sample MCP server deployment that is exposed on the MCP Gateway. However, you can easily plug in your own MCP server image if you want to. 

{{< reuse-image src="/img/mcp-example.svg" width="500px"  >}}

## Before you begin

Follow the [Get started with kgateway](/docs/quickstart/) guide to install kgateway. 

## Set up an MCP Gateway

Use a sample MCP server image to deploy your own MCP gateway. 

1. Create a GatewayParameters resource that allows you set up selfmanaged Gateways. The GatewayParameters resource instructs kgateway to not automatically spin up a gateway proxy, but instead wait for your custom gateway proxy deployment.  
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
             image: ctlptl-registry:5000/mcp-gateway:latest
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
             image: ctlptl-registry:5000/markitdown-mcp:latest
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

With your MCP Gateway in place, let's test access to the MCP tool. 

1. Install the MCP model inspector tool. 
   ```sh
   npx @modelcontextprotocol/inspector
   ```
   
2. [Open the MCP model inspector](http://localhost:5173).

3. Click **Connect** to connect to the MCP Gateway that you deployed. 

4. Try out the **convert_to_markdown** MCP tool that you deployed earlier. 
   1. Click the **convert_to_markdown** tool. 
   2. Provide a sample input file. For example, you can downoad a pdf version of the [US constitution](https://uscode.house.gov/static/constitution.pdf). 
   3. Provide a JWT to access the tool. You can use the following JWT to test the tool.  
      ```sh
      JWT
      ```
   4. Verify that the request fails, because the MCP Gateway requires an MCPAuthPolicy to be in place to allow access to the tool. 
   
   {{< reuse-image src="img/mcp-inspector-request-failed.png" >}}
   
5. Create an MCPAuthPolicy that allows JWTs with the `sub: me` claim to access to the MCP tool. The policy is applied to the `convert_to_markdown` tool. 
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

6. Try to use the tool again. Note that this time, the request succeeds, because the MCP Gateway successfully authorized the request. 
   
   
