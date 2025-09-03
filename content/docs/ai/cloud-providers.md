---
title: Cloud LLM providers
weight: 15
description: Set up cloud LLM providers with AI Gateway.
---

Set up cloud LLM providers with AI Gateway.

## Before you begin

1. [Set up AI Gateway](../setup/).
2. {{< reuse "docs/snippets/ai-gateway-address.md" >}}
3. Choose a [supported LLM provider](#supported-llm-providers).

## Supported LLM providers {#supported-llm-providers}

The examples throughout the AI Gateway docs use OpenAI as the LLM provider, but you can use other providers that are supported by AI Gateway.

{{< callout type="info" >}}
The following sections in this guide provide examples that are tailored to the specific LLM provider. If the provider is not listed, you can adapt the examples to your own provider. Note that some differences might exist, such as different required fields in the Backend resource.
{{< /callout >}}

{{< reuse "docs/snippets/llm-providers.md" >}}

## OpenAI {#openai}

OpenAI is the most common LLM provider, and the examples throughout the AI Gateway docs use OpenAI. You can adapt these examples to your own provider, especially ones that use the OpenAI API, such as [DeepSeek](https://api-docs.deepseek.com/) and [Mistral](https://docs.mistral.ai/getting-started/quickstart/).

To set up OpenAI, continue with the [Authenticate to the LLM](../auth/) guide.

## Gemini {#google}

1. Save your Gemini API key as an environment variable. To retrieve your API key, [log in to the Google AI Studio and select **API Keys**](https://aistudio.google.com/app/apikey).

   ```bash
   export GOOGLE_KEY=<your-api-key>
   ```

2. Create a secret to authenticate to Google. For other ways to authenticate, see the [Auth guide](../auth/).

   ```yaml
   kubectl apply -f - <<EOF
   apiVersion: v1
   kind: Secret
   metadata:
     name: google-secret
     namespace: {{< reuse "docs/snippets/namespace.md" >}}
     labels:
       app: ai-gateway
   type: Opaque
   stringData:
     Authorization: $GOOGLE_KEY
   EOF
   ```

3. Create a Backend resource to define the Gemini destination.

   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.kgateway.dev/v1alpha1
   kind: Backend
   metadata:
     labels:
       app: ai-gateway
     name: google
     namespace: {{< reuse "docs/snippets/namespace.md" >}}
   spec:
     ai:
       llm:
         provider:
           gemini:
             apiVersion: v1beta
             authToken:
               kind: SecretRef
               secretRef:
                 name: google-secret
             model: gemini-1.5-flash-latest
     type: AI
   EOF
   ```

   {{< reuse "docs/snippets/review-table.md" >}}

   | Setting      | Description                                                                                                                                                                                                                                                                                                           |
   | ------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
   | `gemini`     | The Gemini AI provider.                                                                                                                                                                                                                                                                                               |
   | `apiVersion` | The API version of Gemini that is compatible with the model that you plan to use. In this example, you must use `v1beta` because the `gemini-1.5-flash-latest` model is not compatible with the `v1` API version. For more information, see the [Google AI docs](https://ai.google.dev/gemini-api/docs/api-versions). |
   | `authToken`  | The authentication token to use to authenticate to the LLM provider. The example refers to the secret that you created in the previous step.                                                                                                                                                                          |
   | `model`      | The model to use to generate responses. In this example, you use the `gemini-1.5-flash-latest` model. For more models, see the [Google AI docs](https://ai.google.dev/gemini-api/docs/models).                                                                                                                        |

4. Create an HTTPRoute resource to route requests to the Gemini backend. Note that kgateway automatically rewrites the endpoint that you set up (such as `/gemini`) to the appropriate chat completion endpoint of the LLM provider for you, based on the LLM provider that you set up in the Backend resource.

   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.networking.k8s.io/v1
   kind: HTTPRoute
   metadata:
     name: google
     namespace: {{< reuse "docs/snippets/namespace.md" >}}
     labels:
       app: ai-gateway
   spec:
     parentRefs:
       - name: ai-gateway
         namespace: {{< reuse "docs/snippets/namespace.md" >}}
     rules:
     - matches:
       - path:
           type: PathPrefix
           value: /gemini
       backendRefs:
       - name: google
         namespace: {{< reuse "docs/snippets/namespace.md" >}}
         group: gateway.kgateway.dev
         kind: Backend
   EOF
   ```

5. Send a request to the LLM provider API. Verify that the request succeeds and that you get back a response from the chat completion API.

   {{< tabs tabTotal="2" items="Cloud Provider LoadBalancer,Port-forward for local testing" >}}
   {{% tab tabName="Cloud Provider LoadBalancer" %}}

   ````sh
   curl "$INGRESS_GW_ADDRESS:8080/gemini" -H content-type:application/json  -d '{
     "contents": [
       {
         "parts": [
           {
             "text": "Explain how AI works in a few words"
           }
         ]
       }
     ]
   }' | jq
   {{% /tab %}}
   {{% tab tabName="Port-forward for local testing" %}}
   ```sh
   curl "localhost:8080/gemini" -H content-type:application/json -d '{
     "contents": [
       {
         "parts": [
           {
             "text": "Explain how AI works in a few words"
           }
         ]
       }
     ]
   }' | jq
   ````

   {{% /tab %}}
   {{< /tabs >}}

   Example output:

   ```json
   {
     "candidates": [
       {
         "content": {
           "parts": [
             {
               "text": "Learning patterns from data to make predictions.\n"
             }
           ],
           "role": "model"
         },
         "finishReason": "STOP",
         "avgLogprobs": -0.017732446392377216
       }
     ],
     "usageMetadata": {
       "promptTokenCount": 8,
       "candidatesTokenCount": 9,
       "totalTokenCount": 17,
       "promptTokensDetails": [
         {
           "modality": "TEXT",
           "tokenCount": 8
         }
       ],
       "candidatesTokensDetails": [
         {
           "modality": "TEXT",
           "tokenCount": 9
         }
       ]
     },
     "modelVersion": "gemini-1.5-flash-latest",
     "responseId": "UxQ6aM_sKbjFnvgPocrJaA"
   }
   ```

## Overriding LLM Provider Settings {#override-settings}

{{< callout >}}
{{< reuse "docs/snippets/proxy-kgateway.md" >}}
{{< /callout >}}

You can customize the default endpoint paths and authentication headers for LLM providers using override settings. Overrides are useful when you need to route requests to custom API endpoints or use different authentication schemes while maintaining compatibility with the provider's API structure. For example, Azure OpenAI supports authentication via an `Authorization` or `api-key` header. 

By default, {{< reuse "docs/snippets/kgateway.md" >}} assumes that you provide your credentials in an `Authorization` header. However, you might want to use an API key instead. This example walks you through how to override the default `Authorization` header and customize the host URL and path for your LLM provider. 

For more information, see the overrides in the [LLM provider API docs](/docs/reference/api/#llmprovider).

1. Save your OpenAI API key as an environment variable. To retrieve your API key, log in to your [OpenAI account dashboard](https://platform.openai.com/account/api-keys) and create or copy your API key.

   ```bash
   export OPENAI_API_KEY=<your-api-key>

2. Create the authentication secret:

   ```bash
   kubectl apply -f - <<EOF
   apiVersion: v1
   kind: Secret
   metadata:
     name: azure-openai-secret
     namespace: {{< reuse "docs/snippets/namespace.md" >}}
     labels:
       app: ai-gateway
   type: Opaque
   stringData:
     api-key: $AZURE_KEY
   EOF
   ```

3. Create a Backend resource that defines the custom overrides for your Azure OpenAI destination.

   ```yaml
   kubectl apply -f - <<EOF
   apiVersion: gateway.kgateway.dev/v1alpha1
   kind: Backend
   metadata:
     name: azure-openai
     namespace: {{< reuse "docs/snippets/namespace.md" >}}
     labels:
       app: ai-gateway
   spec:
     ai:
       llm:
         hostOverride: apic.ocp.provider.com
         pathOverride: /my-openai-service/gpt35/chat/completions
         provider:
           openai:
             model: gpt-4
             authToken:
               kind: SecretRef
               secretRef:
                 name: azure-openai-secret
             model: gpt-4o
         authHeaderOverride: 
           headerName: api-key
           prefix: ""
     type: AI
   EOF
   ```

   {{< reuse "docs/snippets/review-table.md" >}}

   | Setting              | Description                                                                                     |
   | -------------------- | ----------------------------------------------------------------------------------------------- |
   | `authHeaderOverride` | Overrides the default `Authorization` header that is sent to the AI provider.                             |
   | `headerName`         | The name of the header to use for authentication. Azure requires API keys to be sent in an `"api-key"` header. |
   | `prefix`             | The prefix for the auth token that is provided in the authentication header, such as `Bearer`. By default, the prefix is an empty string. In this example, the `prefix` is an empty string, because Azure OpenAI does not require a prefix for API keys that are provided in an `api-key` header.     |
   | `hostOverride` | Set a custom host for your LLM provider. This host is used for all providers that are defined in the Backend. | 
   | `pathOverride`       | Provide a full path override for all API requests to the AI backend.                            |

4. Create an HTTPRoute resource to route requests to the Azure OpenAI backend. Note that kgateway automatically rewrites the endpoint that you set up (such as `/azure-openai`) to the appropriate chat completion endpoint of the LLM provider for you, based on the LLM provider that you set up in the Backend resource.

   ```yaml
   kubectl apply -f - <<EOF
   apiVersion: gateway.networking.k8s.io/v1
   kind: HTTPRoute
   metadata:
     name: azure-openai
     namespace: {{< reuse "docs/snippets/namespace.md" >}}
     labels:
       app: ai-gateway
   spec:
     parentRefs:
       - name: ai-gateway
         namespace: {{< reuse "docs/snippets/namespace.md" >}}
     rules:
     - matches:
       - path:
           type: PathPrefix
           value: /azure-openai
       backendRefs:
       - name: azure-openai
         namespace: {{< reuse "docs/snippets/namespace.md" >}}
         group: gateway.kgateway.dev
         kind: Backend
   EOF
   ```

4. Send a request to the LLM provider API. Verify that the request succeeds and that you get back a response from the chat completion API.

   {{< tabs tabTotal="2" items="Cloud Provider LoadBalancer,Port-forward for local testing" >}}
   {{% tab tabName="Cloud Provider LoadBalancer" %}}

   ```bash
   curl "$INGRESS_GW_ADDRESS:8080/azure-openai" \
     -H "Content-Type: application/json" \
     -H "api-key: $API_KEY" \
     -d '{
       "messages": [
         {"role": "user", "content": "Hello from Azure OpenAI!"}
       ],
       "max_tokens": 100
     }' | jq
   ```

   {{% /tab %}}
   {{% tab tabName="Port-forward for local testing" %}}

   ```bash
   curl "localhost:8080/azure-openai" \
     -H "Content-Type: application/json" \
     -H "api-key: $API_KEY" \
     -d '{
       "messages": [
         {"role": "user", "content": "Hello from Azure OpenAI!"}
       ],
       "max_tokens": 100
     }' | jq
   ```

   {{% /tab %}}
   {{< /tabs >}}

   Example output:

   ```json
   {
     "id": "chatcmpl-abc123",
     "object": "chat.completion",
     "created": 1699896916,
     "model": "gpt-4",
     "choices": [
       {
         "index": 0,
         "message": {
           "role": "assistant",
           "content": "Hello! I'm Azure OpenAI, ready to help you with any questions or tasks you have."
         },
         "finish_reason": "stop"
       }
     ],
     "usage": {
       "prompt_tokens": 12,
       "completion_tokens": 20,
       "total_tokens": 32
     }
   }
   ```

## Next

Now that you can send requests to an LLM provider, explore the other AI Gateway features.

{{< cards >}}
{{< card link="../failover" title="Model failover" >}}
{{< card link="../functions" title="Function calling" >}}
{{< card link="../prompt-enrichment" title="Prompt enrichment" >}}
{{< card link="../prompt-guards" title="Prompt guards" >}}
{{< card link="../observability" title="AI Gateway metrics" >}}
{{< /cards >}}
