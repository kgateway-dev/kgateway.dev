Configure [Azure OpenAI](https://learn.microsoft.com/en-us/azure/ai-services/openai/) as an LLM provider in {{< reuse "docs/snippets/agentgateway.md" >}}.

## Before you begin

Set up an [agentgateway proxy]({{< link-hextra path="/agentgateway/setup" >}}). 

## Set up access to Azure OpenAI

1. [Deploy a Microsoft Foundry Model](https://learn.microsoft.com/en-us/azure/ai-foundry/foundry-models/how-to/deploy-foundry-models?view=foundry) in the Foundry portal.  
2. Go to the Foundry portal to access your model deployment. From the **Details** tab, retrieve the endpoint and key to access your model deployment. Later, you use this endpoint information to configure your Azure OpenAI backend, including the base URL, your deployment model name, and API version.

   For example, the following URL `https://my-endpoint.cognitiveservices.azure.com/openai/deployments/gpt-4.1-mini/chat/completions?api-version=2025-01-01-preview` is composed of the following details: 
   * `my-endpoint.cognitiveservices.azure.com` as the base URL
   * `gpt-4.1-mini` as the name of your model deployment 
   * `2025-01-01-preview` as the API version 

3. Store the key to access your model deployment in an environment variable. 
   ```sh
   export AZURE_OPENAI_KEY=<insert your model deployment key>
   ```

4. Create a Kubernetes secret to store your model deployment key.

   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: v1
   kind: Secret
   metadata:
     name: azure-openai-secret
     namespace: {{< reuse "docs/snippets/namespace.md" >}}
   type: Opaque
   stringData:
     Authorization: $AZURE_OPENAI_KEY
   EOF
   ```
   {{% version include-if="2.1.x" %}}
   
4. Create a {{< reuse "docs/snippets/backend.md" >}} resource to configure an LLM provider that references the Azure OpenAI key secret.
   
   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.kgateway.dev/v1alpha1
   kind: {{< reuse "docs/snippets/backend.md" >}}
   metadata:
     name: azure-openai
     namespace: {{< reuse "docs/snippets/namespace.md" >}}
   spec:
     type: AI
     ai:
       llm:
         azureopenai:
           endpoint: my-endpoint.cognitiveservices.azure.com
           deploymentName: gpt-4.1-mini
           apiVersion: 2025-01-01-preview
           authToken:
             kind: SecretRef
             secretRef:
               name: azure-openai-secret
   EOF
   ```

   {{% reuse "docs/snippets/review-table.md" %}} For more information, see the [API reference]({{< link-hextra path="/reference/api/#azureopenaiconfig" >}}).

   | Setting           | Description |
   |-------------------|-------------|
   | `type`            | Set to `AI` to configure this {{< reuse "docs/snippets/backend.md" >}} for an AI provider. |
   | `ai`               | Define the AI backend configuration. The example uses Azure OpenAI (`spec.ai.llm.azureopenai`). |
   | `endpoint`         | The endpoint of the Azure OpenAI deployment that you created, such as `my-endpoint.cognitiveservices.azure.com`. |
   | `deploymentName`   | The name of the Azure OpenAI model deployment to use. For more information, see the [Azure OpenAI model docs](https://learn.microsoft.com/en-us/azure/ai-foundry/foundry-models/concepts/models-sold-directly-by-azure?view=foundry-classic&tabs=global-standard-aoai%2Cstandard-chat-completions%2Cglobal-standard&pivots=azure-openai). |
   | `apiVersion`       | The version of the Azure OpenAI API to use. For more information, see the [Azure OpenAI API version reference](https://learn.microsoft.com/en-us/azure/ai-services/openai/reference#api-specs). |
   | `authToken`        | Configure the authentication token for Azure OpenAI API. The example refers to the secret that you previously created. The token is automatically sent in the `api-key` header. |

5. Create an HTTPRoute resource that routes incoming traffic to the {{< reuse "docs/snippets/backend.md" >}}. The following example sets up a route on the `/azure-openai` path to the {{< reuse "docs/snippets/backend.md" >}} that you previously created. Note that {{< reuse "docs/snippets/kgateway.md" >}} automatically rewrites the endpoint to the appropriate chat completion endpoint of the LLM provider for you, based on the LLM provider that you set up in the {{< reuse "docs/snippets/backend.md" >}} resource.

   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.networking.k8s.io/v1
   kind: HTTPRoute
   metadata:
     name: azure-openai
     namespace: {{< reuse "docs/snippets/namespace.md" >}}
   spec:
     parentRefs:
       - name: agentgateway
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
         kind: {{< reuse "docs/snippets/backend.md" >}}
   EOF
   ```
   {{% /version %}}{{% version include-if="2.2.x" %}}
4. Create an {{< reuse "docs/snippets/backend.md" >}} resource to configure Azure OpenAI LLM provider.
   
   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: agentgateway.dev/v1alpha1
   kind: {{< reuse "docs/snippets/backend.md" >}}
   metadata:
     name: azure-openai
     namespace: {{< reuse "docs/snippets/namespace.md" >}}
   spec:
     ai:
       provider:
         azureopenai:
           endpoint: my-endpoint.cognitiveservices.azure.com
           deploymentName: gpt-4.1-mini
           apiVersion: 2025-01-01-preview
     policies:
       auth:
         secretRef:
           name: azure-openai-secret
   EOF
   ```

   {{% reuse "docs/snippets/review-table.md" %}} For more information, see the [API reference]({{< link-hextra path="/reference/api/#azureopenaiconfig" >}}).

   | Setting     | Description |
   |-------------|-------------|
   | `ai.provider.azureopenai` | Define the Azure OpenAI provider. |
   | `azureopenai.endpoint`     | The endpoint of the Azure OpenAI deployment that you created, such as `my-endpoint.cognitiveservices.azure.com`. |
   | `azureopenai.deployment`    | The name of the Azure OpenAI model deployment that you created earlier. For more information, see the [Azure OpenAI model docs](https://learn.microsoft.com/en-us/azure/ai-foundry/foundry-models/how-to/deploy-foundry-models?view=foundry).|
   | `azureopenai.apiVersion`    | The version of the Azure OpenAI API to use. For more information, see the [Azure OpenAI API version reference](https://learn.microsoft.com/en-us/azure/ai-services/openai/reference#api-specs).|
   | `policies.auth` | Configure the authentication token for Azure OpenAI API. The example refers to the secret that you previously created. The token is automatically sent in the `api-key` header.|

5. Create an HTTPRoute resource that routes incoming traffic to the {{< reuse "docs/snippets/backend.md" >}}. The following example sets up a route on the `/azure-openai` path to the {{< reuse "docs/snippets/backend.md" >}} that you previously created. Note that {{< reuse "docs/snippets/kgateway.md" >}} automatically rewrites the endpoint to the appropriate chat completion endpoint of the LLM provider for you, based on the LLM provider that you set up in the {{< reuse "docs/snippets/backend.md" >}} resource.

   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.networking.k8s.io/v1
   kind: HTTPRoute
   metadata:
     name: azure-openai
     namespace: {{< reuse "docs/snippets/namespace.md" >}}
   spec:
     parentRefs:
       - name: agentgateway
         namespace: {{< reuse "docs/snippets/namespace.md" >}}
     rules:
     - matches:
       - path:
           type: PathPrefix
           value: /azure-openai
       backendRefs:
       - name: azure-openai
         namespace: {{< reuse "docs/snippets/namespace.md" >}}
         group: agentgateway.dev
         kind: {{< reuse "docs/snippets/backend.md" >}}
   EOF
   ```

   {{% /version %}}

6. Send a request to the LLM provider API. Verify that the request succeeds and that you get back a response from the chat completion API.
   
   {{< tabs tabTotal="2" items="Cloud Provider LoadBalancer,Port-forward for local testing" >}}
   {{% tab tabName="Cloud Provider LoadBalancer" %}}
   ```sh
   curl "$INGRESS_GW_ADDRESS:8080/azure-openai" -H content-type:application/json  -d '{
      "model": "",
      "messages": [
        {
          "role": "system",
          "content": "You are a helpful assistant."
        },
        {
          "role": "user",
          "content": "Write a short haiku about cloud computing."
        }
      ]
    }' | jq
   {{% /tab %}}
   {{% tab tabName="Port-forward for local testing" %}}
   ```sh
   curl "localhost:8080/azure-openai" -H content-type:application/json  -d '{
      "model": "",
      "messages": [
        {
          "role": "system",
          "content": "You are a helpful assistant."
        },
        {
          "role": "user",
          "content": "Write a short haiku about cloud computing."
        }
      ]
    }' | jq
   ```
   {{% /tab %}}
   {{< /tabs >}}
   
   Example output: 
   ```json
   {
     "id": "chatcmpl-9A8B7C6D5E4F3G2H1",
     "object": "chat.completion",
     "created": 1727967462,
     "model": "gpt-4o-mini",
     "choices": [
       {
         "index": 0,
         "message": {
           "role": "assistant",
           "content": "Floating servers bright,\nData streams through endless sky,\nClouds hold all we need."
         },
         "finish_reason": "stop"
       }
     ],
     "usage": {
       "prompt_tokens": 28,
       "completion_tokens": 19,
       "total_tokens": 47
     }
   }
   ```

{{< reuse "docs/snippets/agentgateway/llm-next.md" >}}
