Configure [Azure OpenAI](https://learn.microsoft.com/en-us/azure/ai-services/openai/) as an LLM provider in {{< reuse "docs/snippets/agentgateway.md" >}}.

## Before you begin

Set up an [agentgateway proxy]({{< link-hextra path="/agentgateway/setup" >}}). 

## Set up access to Azure OpenAI

1. Create an API key to access the [Azure OpenAI API](https://learn.microsoft.com/en-us/azure/api-management/api-management-authenticate-authorize-azure-openai).

2. Save the API key in an environment variable.
   
   ```sh
   export AZURE_OPENAI_API_KEY=<insert your API key>
   ```

3. Create a Kubernetes secret to store your Azure OpenAI API key.

   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: v1
   kind: Secret
   metadata:
     name: azure-openai-secret
     namespace: {{< reuse "docs/snippets/namespace.md" >}}
   type: Opaque
   stringData:
     Authorization: $AZURE_OPENAI_API_KEY
   EOF
   ```
   
4. Create a Backend resource to configure an LLM provider that references the Azure OpenAI API key secret.
   
   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.kgateway.dev/v1alpha1
   kind: Backend
   metadata:
     name: azure-openai
     namespace: {{< reuse "docs/snippets/namespace.md" >}}
   spec:
     type: AI
     ai:
       llm:
         azureopenai:
           endpoint: my-endpoint.openai.azure.com
           deploymentName: gpt-4o-mini
           apiVersion: 2024-02-15-preview
           authToken:
             kind: SecretRef
             secretRef:
               name: azure-openai-secret
   EOF
   ```

   {{% reuse "docs/snippets/review-table.md" %}} For more information, see the [API reference]({{< link-hextra path="/reference/api/#azureopenaiconfig" >}}).

   | Setting           | Description |
   |-------------------|-------------|
   | `type`            | Set to `AI` to configure this Backend for an AI provider. |
   | `ai`               | Define the AI backend configuration. The example uses Azure OpenAI (`spec.ai.llm.azureopenai`). |
   | `endpoint`         | The endpoint for the Azure OpenAI API to use, such as `my-endpoint.openai.azure.com`. |
   | `deploymentName`   | The name of the Azure OpenAI model deployment to use. For more information, see the [Azure OpenAI model docs](https://learn.microsoft.com/en-us/azure/ai-services/openai/concepts/models). |
   | `apiVersion`       | The version of the Azure OpenAI API to use. For more information, see the [Azure OpenAI API version reference](https://learn.microsoft.com/en-us/azure/ai-services/openai/reference#api-specs). |
   | `authToken`        | Configure the authentication token for Azure OpenAI API. The example refers to the secret that you previously created. The token is automatically sent in the `api-key` header. |

5. Create an HTTPRoute resource that routes incoming traffic to the Backend. The following example sets up a route on the `/azure-openai` path to the Backend that you previously created. Note that {{< reuse "docs/snippets/kgateway.md" >}} automatically rewrites the endpoint to the appropriate chat completion endpoint of the LLM provider for you, based on the LLM provider that you set up in the Backend resource.

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
         kind: Backend
   EOF
   ```

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
