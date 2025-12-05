Configure OpenAI-compatible LLM providers such as Mistral, DeepSeek, or any other provider that implements the OpenAI API format in {{< reuse "docs/snippets/agw-kgw.md" >}}.

## Overview

Many LLM providers offer APIs that are compatible with OpenAI's API format. You can configure these providers in agentgateway by using the `openai` provider type with custom `host`, `port`, `path`, and `authHeader` overrides.

Note that when you specify a custom `host` override, agentgateway requires explicit TLS configuration via `BackendTLSPolicy` for HTTPS endpoints. This differs from well-known providers (like OpenAI) where TLS is automatically enabled when using default hosts.

## Before you begin

Set up an [agentgateway proxy]({{< link-hextra path="/agentgateway/setup" >}}). 

## Set up access to an OpenAI-compatible provider

Review the following examples for common OpenAI-compatible provider endpoints:

- [Mistral AI](#mistral)
- [DeepSeek](#deepseek)  

### Mistral AI example {#mistral}

Set up OpenAI-compatible provider access to [Mistral AI](https://mistral.ai/) models.

1. Get a [Mistral AI API key](https://console.mistral.ai/). 

2. Save the API key in an environment variable.
   
   ```sh
   export MISTRAL_API_KEY=<insert your API key>
   ```

3. Create a Kubernetes secret to store your Mistral AI API key.

   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: v1
   kind: Secret
   metadata:
     name: mistral-secret
     namespace: {{< reuse "docs/snippets/namespace.md" >}}
   type: Opaque
   stringData:
     Authorization: $MISTRAL_API_KEY
   EOF
   ```

4. Create an {{< reuse "docs/snippets/backend.md" >}} resource to configure your LLM provider and reference the AI API key secret that you created earlier.
   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: agentgateway.dev/v1alpha1
   kind: {{< reuse "docs/snippets/backend.md" >}}
   metadata:
     name: mistral
     namespace: {{< reuse "docs/snippets/namespace.md" >}}
   spec:
     ai:
       provider:
         openai:
           model: mistral-medium-2505
         host: api.mistral.ai
         port: 443 
         path: "/v1/chat/completions"
     policies:
       auth:
         secretRef:
           name: mistral-secret
       tls: 
         sni: api.mistral.ai
   EOF
   ```

   {{% reuse "docs/snippets/review-table.md" %}} For more information, see the [API reference]({{< link-hextra path="/reference/api/#aibackend" >}}).

   | Setting     | Description |
   |-------------|-------------|
   | `ai.provider.openai` | Define the OpenAI-compatible provider. |
   | `openai.model`     | The model to use, such as `mistral-medium-2505`.  |
   | `openai.host` | **Required**: The hostname of the OpenAI-compatible provider, such as `api.mistral.ai`.  | 
   | `openai.port` | **Required**: The port number (typically `443` for HTTPS). Both `host` and `port` must be set together. |
   | `openai.path` | Optional: Override the API path. Defaults to `/v1/chat/completions` if not specified. | 
   | `policies.auth` | Configure the authentication token for OpenAI API. The example refers to the secret that you previously created.|
   | `policies.tls.sni` | The hostname for which to validate the server certificate (must match the `host` value). |

5. Create an HTTPRoute resource that routes incoming traffic to the {{< reuse "docs/snippets/backend.md" >}}. The following example sets up a route on the `/openai` path to the {{< reuse "docs/snippets/backend.md" >}} that you previously created. The `URLRewrite` filter rewrites the path from `/openai` to the path of the API in the LLM provider that you want to use, `/v1/chat/completions`.

   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.networking.k8s.io/v1
   kind: HTTPRoute
   metadata:
     name: mistral
     namespace: {{< reuse "docs/snippets/namespace.md" >}}
   spec:
     parentRefs:
       - name: agentgateway
         namespace: {{< reuse "docs/snippets/namespace.md" >}}
     rules:
     - matches:
       - path:
           type: PathPrefix
           value: /mistral
       filters:
         - type: URLRewrite
           urlRewrite:
             hostname: api.mistral.ai
       backendRefs:
       - name: mistral
         namespace: {{< reuse "docs/snippets/namespace.md" >}}
         group: agentgateway.dev
         kind: {{< reuse "docs/snippets/backend.md" >}}
   EOF
   ```
6. Send a request to the LLM provider API. Verify that the request succeeds and that you get back a response from the chat completion API.
   
   {{< tabs tabTotal="2" items="Cloud Provider LoadBalancer,Port-forward for local testing" >}}
   {{% tab tabName="Cloud Provider LoadBalancer" %}}
   ```sh
   curl "$INGRESS_GW_ADDRESS/mistral" -H content-type:application/json  -d '{
      "model": "",
      "messages": [
        {
          "role": "system",
          "content": "You are a helpful assistant."
        },
        {
          "role": "user",
          "content": "Write a short haiku about artificial intelligence."
        }
      ]
    }' | jq
   {{% /tab %}}
   {{% tab tabName="Port-forward for local testing" %}}
   ```sh
   curl "localhost:8080/mistral" -H content-type:application/json  -d '{
      "model": "",
      "messages": [
        {
          "role": "system",
          "content": "You are a helpful assistant."
        },
        {
          "role": "user",
          "content": "Write a short haiku about artificial intelligence."
        }
      ]
    }' | jq
   ```
   {{% /tab %}}
   {{< /tabs >}}
   
   Example output: 
   ```json
   {
     "model": "mistral-medium-2505",
     "usage": {
       "prompt_tokens": 20,
       "completion_tokens": 18,
       "total_tokens": 38
     },
     "choices": [
       {
         "message": {
           "content": "Silent circuits hum,\nLearning echoes through the void,\nWisdom without warmth.",
           "role": "assistant",
           "tool_calls": null
         },
         "index": 0,
         "finish_reason": "stop"
       }
     ],
     "id": "d05ef3973085435a8db8b51b580eeef8",
     "created": 1764614501,
     "object": "chat.completion"
   }
   ```

### DeepSeek example {#deepseek}

Set up OpenAI-compatible provider access to [DeepSeek](https://www.deepseek.com/en) models.

1. Get a [DeepSeek API key](https://platform.deepseek.com/). 

2. Save the API key in an environment variable.
   
   ```sh
   export DEEPSEEK_API_KEY=<insert your API key>
   ```

3. Create a Kubernetes secret to store your DeepSeek API key.

   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: v1
   kind: Secret
   metadata:
     name: deepseek-secret
     namespace: {{< reuse "docs/snippets/namespace.md" >}}
   type: Opaque
   stringData:
     Authorization: $DEEPSEEK_API_KEY
   EOF
   ```

4. Create an {{< reuse "docs/snippets/backend.md" >}} resource to configure your LLM provider and reference the AI API key secret that you created earlier.
   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: agentgateway.dev/v1alpha1
   kind: {{< reuse "docs/snippets/backend.md" >}}
   metadata:
     name: deepseek
     namespace: {{< reuse "docs/snippets/namespace.md" >}}
   spec:
     ai:
       provider:
         openai:
           model: deepseek-chat
         host: api.deepseek.com
         port: 443 
         path: "/v1/chat/completions"
     policies:
       auth:
         secretRef:
           name: deepseek-secret
       tls: 
         sni: api.deepseek.com
   EOF
   ```

5. Create an HTTPRoute resource that routes incoming traffic to the {{< reuse "docs/snippets/backend.md" >}}. Note that {{< reuse "docs/snippets/kgateway.md" >}} automatically rewrites the endpoint to the OpenAI chat completion endpoint of the LLM provider for you, based on the LLM provider that you set up in the {{< reuse "docs/snippets/backend.md" >}} resource.

   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.networking.k8s.io/v1
   kind: HTTPRoute
   metadata:
     name: deepseek
     namespace: {{< reuse "docs/snippets/namespace.md" >}}
   spec:
     parentRefs:
       - name: agentgateway
         namespace: {{< reuse "docs/snippets/namespace.md" >}}
     rules:
     - matches:
       - path:
           type: PathPrefix
           value: /deepseek
       backendRefs:
       - name: deepseek
         namespace: {{< reuse "docs/snippets/namespace.md" >}}
         group: agentgateway.dev
         kind: {{< reuse "docs/snippets/backend.md" >}}
   EOF
   ```

6. Send a request to the LLM provider API. Verify that the request succeeds and that you get back a response from the chat completion API.
   
   {{< tabs tabTotal="2" items="Cloud Provider LoadBalancer,Port-forward for local testing" >}}
   {{% tab tabName="Cloud Provider LoadBalancer" %}}
   ```sh
   curl "$INGRESS_GW_ADDRESS/deepseek" -H content-type:application/json  -d '{
      "model": "",
      "messages": [
        {
          "role": "system",
          "content": "You are a helpful assistant."
        },
        {
          "role": "user",
          "content": "Write a short haiku about artificial intelligence."
        }
      ]
    }' | jq
   {{% /tab %}}
   {{% tab tabName="Port-forward for local testing" %}}
   ```sh
   curl "localhost:8080/deepseek" -H content-type:application/json  -d '{
      "model": "",
      "messages": [
        {
          "role": "system",
          "content": "You are a helpful assistant."
        },
        {
          "role": "user",
          "content": "Write a short haiku about artificial intelligence."
        }
      ]
    }' | jq
   ```
   {{% /tab %}}
   {{< /tabs >}}
   
   Example output: 
   ```json
   {
     "id": "chatcmpl-deepseek-12345",
     "object": "chat.completion",
     "created": 1727967462,
     "model": "deepseek-chat",
     "choices": [
       {
         "index": 0,
         "message": {
           "role": "assistant",
           "content": "Neural networks learn,\nPatterns emerge from data streams,\nMind in silicon grows."
         },
         "finish_reason": "stop"
       }
     ],
     "usage": {
       "prompt_tokens": 20,
       "completion_tokens": 17,
       "total_tokens": 37
     }
   }
   ```

{{< reuse "docs/snippets/agentgateway/llm-next.md" >}}
