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

   | Setting | Description |
   |---------|-------------|
   | `gemini` | The Gemini AI provider. |
   | `apiVersion` | The API version of Gemini that is compatible with the model that you plan to use. In this example, you must use `v1beta` because the `gemini-1.5-flash-latest` model is not compatible with the `v1` API version. For more information, see the [Google AI docs](https://ai.google.dev/gemini-api/docs/api-versions). |
   | `authToken` | The authentication token to use to authenticate to the LLM provider. The example refers to the secret that you created in the previous step. |
   | `model` | The model to use to generate responses. In this example, you use the `gemini-1.5-flash-latest` model. For more models, see the [Google AI docs](https://ai.google.dev/gemini-api/docs/models). |

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
   ```sh
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
   ```
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

## Next

Now that you can send requests to an LLM provider, explore the other AI Gateway features.

{{< cards >}}
  {{< card link="../failover" title="Model failover" >}}
  {{< card link="../functions" title="Function calling" >}}
  {{< card link="../prompt-enrichment" title="Prompt enrichment" >}}
  {{< card link="../prompt-guards" title="Prompt guards" >}}
  {{< card link="../observability" title="AI Gateway metrics" >}}
{{< /cards >}}