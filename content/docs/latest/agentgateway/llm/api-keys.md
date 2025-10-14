---
title: Manage API keys
weight: 30
description:
---

Managing API keys is an important security mechanism to prevent unauthorized access to your LLM provider. If API keys are compromised, attackers can deliberately run expensive queries, such as large and recursive prompts, at your expense. 

Follow the instructions in this guide to learn how to use these different methods. 

## Before you begin

Set up an [agentgateway proxy]({{< link-hextra path="/agentgateway/setup" >}}). 

## Manage API keys

You can choose between the following options to provide an API key to agentgateway: 
* [Inline](#inline)
* [Kubernetes secret](#api-key)
* [Passthrough token](#passthrough)

### Inline token {#inline}

Provide the token directly in the configuration for the Backend. This option is the least secure. Only use this option for quick tests such as trying out AI Gateway.

1. Get the token from your LLM provider, such as an API key to OpenAI.

   ```sh
   export TOKEN=<your-ai-provider-token>
   ```

2. Provide the token inline in the Backend configuration.

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
             kind: Inline
             inline: "$TOKEN"
           model: "gpt-3.5-turbo"
   EOF
   ``` 

   {{% reuse "docs/snippets/review-table.md" %}} For more information or other providers, see the [API reference]({{< link-hextra path="/reference/api/#aibackend" >}}).

   | Setting     | Description |
   |-------------|-------------|
   | `type`      | Set to `AI` to configure this Backend for an AI provider. |
   | `ai`        | Define the AI backend configuration. The example uses OpenAI (`spec.ai.llm.openai`). |
   | `authToken` | Configure the authentication token for OpenAI API. The example uses an inline token. |
   | `model`     | The OpenAI model to use, such as `gpt-3.5-turbo`. |

3. Create an HTTPRoute resource that routes incoming traffic to the Backend. The following example sets up a route on the `/openai` path to the Backend backend that you previously created. The `URLRewrite` filter rewrites the path from `/openai` to the path of the API in the LLM provider that you want to use, `/v1/chat/completions`.

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

4. Send a request to the LLM provider API. Verify that the request succeeds and that you get back a response from the chat completion API.
   
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
    }' 
   {{% /tab %}}
   {{% tab tabName="Port-forward for local testing" %}}
   ```sh
   curl "localhost:8080/openai" -H content-type:application/json  -d '{
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
    }' 
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

### API key in a secret {#api-key}

Store the API key in a Kubernetes secret. Then, refer to the secret in the Backend configuration. This option is more secure than an inline token, because the API key is encoded and you can restrict access to secrets through RBAC rules. Like the inline option, the API key and secret are fairly simple to create and set up. You might use this option in proofs of concept, controlled development and staging environments, or well-controlled prod environments that use secrets.

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
    }' 
   {{% /tab %}}
   {{% tab tabName="Port-forward for local testing" %}}
   ```sh
   curl "localhost:8080/openai" -H content-type:application/json  -d '{
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
    }'
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

### Passthrough token {#passthrough}

Pass through an existing token directly from the client or a successful OpenID Connect (OIDC) connect flow before the request is sent to the Backend. This option is useful for environments where you set up federated identity for backend clients so that they are already authenticated to the LLM providers that you create Backends for. Currently, the request must place the token in the `Authorization` header.

1. Make sure that your client is set up as follows:

   * The client that sends a request to the Backend can authenticate to the LLM provider, such as through an OIDC flow.
   * The authenticated token is sent in requests to the Backend in an `Authorization` header.

2. Configure the Backend to use passthrough auth.

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
             kind: Passthrough
           model: "gpt-3.5-turbo"
   EOF
   ``` 

   {{% reuse "docs/snippets/review-table.md" %}} For more information or other providers, see the [API reference]({{< link-hextra path="/reference/api/#aibackend" >}}).

   | Setting     | Description |
   |-------------|-------------|
   | `type`      | Set to `AI` to configure this Backend for an AI provider. |
   | `ai`        | Define the AI backend configuration. The example uses OpenAI (`spec.ai.llm.openai`). |
   | `authToken` | Configure the authentication token for OpenAI API. The example uses passthrough authentication. |
   | `model`     | The OpenAI model to use, such as `gpt-3.5-turbo`. |

3. Create an HTTPRoute resource that routes incoming traffic to the Backend. The following example sets up a route on the `/openai` path to the Backend backend that you previously created. The `URLRewrite` filter rewrites the path from `/openai` to the path of the API in the LLM provider that you want to use, `/v1/chat/completions`.

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

4. Trigger your authenticated client to send a request to the Backend, and verify that you get back a successful response. For example, you might instruct your client to send a curl request through the AI Gateway. Note that the request includes the `Authorization` header, which is required for passthrough authentication.

   {{< tabs tabTotal="2" items="Cloud Provider LoadBalancer,Port-forward for local testing" >}}
   {{% tab tabName="Cloud Provider LoadBalancer" %}}
   ```sh
   curl "$INGRESS_GW_ADDRESS:8080/openai" -H "Authorization: Bearer $TOKEN" -H content-type:application/json -d '{
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
    }'
   {{% /tab %}}
   {{% tab tabName="Port-forward for local testing" %}}
   ```sh
   curl "localhost:8080/openai" -H "Authorization: Bearer $TOKEN" -H content-type:application/json -d '{
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
    }'
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

