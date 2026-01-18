---
title: Transformations
weight: 10
description: Use CEL expressions to transform requests and responses to LLMs, MCP servers, and agents. 
---

## About CEL expressions

CEL (Common Expression Language) transformations allows you to use dynamic expressions to extract and transform values from requests and responses. 

For an overview of supported CEL expressions, see the [agentgateway docs](https://agentgateway.dev/docs/reference/cel/).

## About this guide

This guide walks you through how to set up CEL-based transformations for the OpenAI LLM provider. Note that you can use the same {{< reuse "docs/snippets/trafficpolicy.md" >}} resource to apply transformations to MCP server, inference, or agent routes. 

## Before you begin

{{< reuse "docs/snippets/agw-prereq-llm.md" >}}

{{< callout type="info" >}}
Note that this guide assumes that you want to apply external auth to the OpenAI LLM provider. You can use other LLM providers or apply external auth to an MCP server or agent. Make sure to adjust these steps to apply to your {{< reuse "docs/snippets/backend.md" >}} type.
{{< /callout >}}

## Set up transformations

1. Create an {{< reuse "docs/snippets/trafficpolicy.md" >}} with your transformation rules. In this example, you use a CEL expression to extract the path from the request. The request path is then added to the `response-gateway` header.
   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: {{< reuse "docs/snippets/trafficpolicy-apiversion.md" >}}
   kind: {{< reuse "docs/snippets/trafficpolicy.md" >}}
   metadata:
     name: transformation
     namespace: {{< reuse "docs/snippets/namespace.md" >}}
   spec:
     targetRefs:
     - group: gateway.networking.k8s.io
       kind: Gateway
       name: agentgateway-proxy
     traffic:
       transformation:
         response:
           set:
           - name: response-gateway
             value: "'response path ' + request.path"
   EOF
   ```

2. Send a request to the OpenAI API. Verify that the request succeeds and that you see the `response-gateway` header with a value of `response path /openai`. 
   
   {{< tabs tabTotal= "2" items="Cloud Provider LoadBalancer,Port-forward for local testing" >}}
   {{% tab tabName="Cloud Provider LoadBalancer" %}}
   ```sh
   curl -v "${INGRESS_GW_ADDRESS}:8080/openai" -H content-type:application/json -H "X-User-ID: user123" -d '{
    "model": "gpt-3.5-turbo",
    "messages": [
      {
        "role": "system",
        "content": "You are a poetic assistant, skilled in explaining complex programming concepts with creative flair."
      },
      {
        "role": "user",
        "content": "In the style of Shakespeare, write a series of sonnets that explain the concept of recursion in programming."
      }
    ]
   }'
   ```
   {{% /tab %}}
   {{% tab tabName="Port-forward for local testing" %}}
   ```sh
   curl -v "localhost:8080/openai" -H content-type:application/json -H "X-User-ID: user123" -d '{
    "model": "gpt-3.5-turbo",
    "messages": [
      {
        "role": "system",
        "content": "You are a poetic assistant, skilled in explaining complex programming concepts with creative flair."
      },
      {
        "role": "user",
        "content": "In the style of Shakespeare, write a series of sonnets that explain the concept of recursion in programming."
      }
    ]
   }'
   ```
   {{% /tab %}}
   {{< /tabs >}}

   Example output: 
   ```console {hl_lines=[9]}
   * upload completely sent off: 358 bytes
   < HTTP/1.1 200 OK
   < content-type: application/json
   < access-control-expose-headers: X-Request-ID
   < openai-organization: solo-io-1
   < openai-processing-ms: 1082
   < openai-version: 2020-10-01
   ...
   < response-gateway: response path /openai
   < content-length: 1198
   ```

## Cleanup

{{< reuse "docs/snippets/cleanup.md" >}}

```sh
kubectl delete {{< reuse "docs/snippets/trafficpolicy.md" >}} transformation -n {{< reuse "docs/snippets/namespace.md" >}}
```