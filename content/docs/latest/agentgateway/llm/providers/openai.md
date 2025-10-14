---
title: OpenAI
weight: 10
description:
---

Configure OpenAI as an LLM provider in {{< reuse "docs/snippets/agentgateway.md" >}}.

## Before you begin

Set up an [agentgateway proxy]({{< link-hextra path="/agentgateway/setup" >}}). 

## Set up access to OpenAI

1. [Create an API key to access the OpenAI API](https://platform.openai.com/api-keys). If you use another AI provider, create an API key for that provider's AI instead, and be sure to modify the example commands in these tutorials to use your provider's AI API instead.

2. Save the API key in an environment variable.
   
   ```sh
   export OPENAI_API_KEY=<insert your API key>
   ```

3. Create a Kubernetes secret to store your AI API key.

   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: v1
   kind: Secret
   metadata:
     name: openai-secret
     namespace: {{< reuse "docs/snippets/namespace.md" >}}
     labels:
       app: agentgateway
   type: Opaque
   stringData:
     Authorization: $OPENAI_API_KEY
   EOF
   ```
   
4. Create a Backend resource to configure an LLM provider that references the AI API key secret.
   
   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.kgateway.dev/v1alpha1
   kind: Backend
   metadata:
     labels:
       app: agentgateway
     name: openai
     namespace: {{< reuse "docs/snippets/namespace.md" >}}
   spec:
     type: AI
     ai:
       llm:
         openai:
           authToken:
             kind: SecretRef
             secretRef:
               name: openai-secret
           model: "gpt-3.5-turbo"
   EOF
   ```

   {{% reuse "docs/snippets/review-table.md" %}} For more information or other providers, see the [API reference]({{< link-hextra path="/reference/api/#aibackend" >}}).

   | Setting     | Description |
   |-------------|-------------|
   | `type`      | Set to `AI` to configure this Backend for an AI provider. |
   | `ai`        | Define the AI backend configuration. The example uses OpenAI (`spec.ai.llm.openai`). |
   | `authToken` | Configure the authentication token for OpenAI API. The example refers to the secret that you previously created. |
   | `model`     | The OpenAI model to use, such as `gpt-3.5-turbo`. |

5. Create an HTTPRoute resource that routes incoming traffic to the Backend. The following example sets up a route on the `/openai` path to the Backend backend that you previously created. The `URLRewrite` filter rewrites the path from `/openai` to the path of the API in the LLM provider that you want to use, `/v1/chat/completions`.

   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.networking.k8s.io/v1
   kind: HTTPRoute
   metadata:
     name: openai
     namespace: {{< reuse "docs/snippets/namespace.md" >}}
     labels:
       app: agentgateway
   spec:
     parentRefs:
       - name: agentgateway
         namespace: {{< reuse "docs/snippets/namespace.md" >}}
     rules:
     - matches:
       - path:
           type: PathPrefix
           value: /openai
       filters:
       - type: URLRewrite
         urlRewrite:
           path:
             type: ReplaceFullPath
             replaceFullPath: /v1/chat/completions
       backendRefs:
       - name: openai
         namespace: {{< reuse "docs/snippets/namespace.md" >}}
         group: gateway.kgateway.dev
         kind: Backend
   EOF
   ```

6. Send a request to the LLM provider API. Verify that the request succeeds and that you get back a response from the chat completion API.
   
   {{< tabs tabTotal="2" items="Cloud Provider LoadBalancer,Port-forward for local testing" >}}
   {{% tab tabName="Cloud Provider LoadBalancer" %}}
   ```sh
   curl "$INGRESS_GW_ADDRESS:8080/openai" -H content-type:application/json  -d '{
      "model": "",
      "messages": [
        {
          "role": "system",
          "content": "You are a poetic assistant, skilled in explaining complex programming concepts with creative flair."
        },
        {
          "role": "user",
          "content": "Compose a poem that explains the concept of recursion in programming."
        }
      ]
    }' | jq
   {{% /tab %}}
   {{% tab tabName="Port-forward for local testing" %}}
   ```sh
   curl "localhost:8080/openai" -H content-type:application/json  -d '{
      "model": "gpt-3.5-turbo",
      "messages": [
        {
          "role": "system",
          "content": "You are a poetic assistant, skilled in explaining complex programming concepts with creative flair."
        },
        {
          "role": "user",
          "content": "Compose a poem that explains the concept of recursion in programming."
        }
      ]
    }' | jq
   ```
   {{% /tab %}}
   {{< /tabs >}}
   
   Example output: 
   ```json
   {
     "id": "chatcmpl-AEHYs2B0XUlEioCduH1meERmMwBGF",
     "object": "chat.completion",
     "created": 1727967462,
     "model": "gpt-3.5-turbo-0125",
     "choices": [
       {
         "index": 0,
         "message": {
           "role": "assistant",
           "content": "In the world of code, a method elegant and rare,\nKnown as recursion, a loop beyond compare.\nLike a mirror reflecting its own reflection,\nIt calls upon itself with deep introspection.\n\nA function that calls itself with artful grace,\nDividing a problem into a smaller space.\nLike a nesting doll, layers deep and profound,\nIt solves complex tasks, looping around.\n\nWith each recursive call, a step is taken,\nTowards solving the problem, not forsaken.\nA dance of self-replication, a mesmerizing sight,\nUnraveling complexity with power and might.\n\nBut beware of infinite loops, a perilous dance,\nWithout a base case, it’s a risky chance.\nFor recursion is a waltz with a delicate balance,\nInfinite beauty, yet a risky dalliance.\n\nSo embrace the concept, in programming’s domain,\nLet recursion guide you, like a poetic refrain.\nA magical loop, a recursive song,\nIn the symphony of code, where brilliance belongs.",
           "refusal": null
         },
         "logprobs": null,
         "finish_reason": "stop"
       }
     ],
     "usage": {
       "prompt_tokens": 39,
       "completion_tokens": 200,
       "total_tokens": 239,
       "prompt_tokens_details": {
         "cached_tokens": 0
       },
       "completion_tokens_details": {
         "reasoning_tokens": 0
       }
     },
     "system_fingerprint": null
   }
   ```