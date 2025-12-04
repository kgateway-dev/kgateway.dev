Configure [Vertex AI](https://cloud.google.com/vertex-ai) as an LLM provider in {{< reuse "docs/snippets/agentgateway.md" >}}.

## Before you begin

Set up an [agentgateway proxy]({{< link-hextra path="/agentgateway/setup" >}}). 

## Set up access to Vertex AI

1. [Set up authentication for Vertex AI](https://docs.cloud.google.com/vertex-ai/docs/authentication). Make sure to have your:
   
   - Google Cloud Project ID
   - Project location, such as `us-central1`
   - API key or service account credentials

2. Save your Vertex AI API key as an environment variable.
   
   ```sh
   export VERTEX_AI_API_KEY=<insert your API key>
   ```

3. Create a Kubernetes secret to store your Vertex AI API key.

   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: v1
   kind: Secret
   metadata:
     name: vertex-ai-secret
     namespace: {{< reuse "docs/snippets/namespace.md" >}}
   type: Opaque
   stringData:
     Authorization: $VERTEX_AI_API_KEY
   EOF
   ```
   {{% version include-if="2.1.x" %}}   
4. Create a {{< reuse "docs/snippets/backend.md" >}} resource to configure an LLM provider that references the Vertex AI API key secret.
   
   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.kgateway.dev/v1alpha1
   kind: {{< reuse "docs/snippets/backend.md" >}}
   metadata:
     name: vertex-ai
     namespace: {{< reuse "docs/snippets/namespace.md" >}}
   spec:
     type: AI
     ai:
       llm:
         vertexai:
           authToken:
             kind: SecretRef
             secretRef:
               name: vertex-ai-secret
           model: "gemini-pro"
           apiVersion: "v1"
           projectId: "my-gcp-project"
           location: "us-central1"
           publisher: "GOOGLE"
   EOF
   ```

   {{% reuse "docs/snippets/review-table.md" %}} For more information, see the [API reference]({{< link-hextra path="/reference/api/#aibackend" >}}).

   | Setting      | Description |
   |--------------|-------------|
   | `type`       | Set to `AI` to configure this {{< reuse "docs/snippets/backend.md" >}} for an AI provider. |
   | `ai`         | Define the AI backend configuration. The example uses Vertex AI (`spec.ai.llm.vertexai`). |
   | `authToken`  | Configure the authentication token for Vertex AI API. The example refers to the secret that you previously created. The token is automatically sent in the `key` header. |
   | `model`      | The Vertex AI model to use. For more information, see the [Vertex AI model docs](https://cloud.google.com/vertex-ai/generative-ai/docs/learn/models). |
   | `apiVersion` | The version of the Vertex AI API to use. For more information, see the [Vertex AI API reference](https://cloud.google.com/vertex-ai/docs/reference#versions). |
   | `projectId`  | The ID of the Google Cloud Project that you use for Vertex AI. |
   | `location`   | The location of the Google Cloud Project that you use for Vertex AI (e.g., `us-central1`). |
   | `publisher`  | The type of publisher model to use. Currently, only `GOOGLE` is supported. |
   | `modelPath`  | Optional: The model path to route to. Defaults to the Gemini model path, `generateContent`. |

5. Create an HTTPRoute resource that routes incoming traffic to the {{< reuse "docs/snippets/backend.md" >}}. The following example sets up a route on the `/vertex` path. Note that {{< reuse "docs/snippets/kgateway.md" >}} automatically rewrites the endpoint to the appropriate chat completion endpoint of the LLM provider for you, based on the LLM provider that you set up in the {{< reuse "docs/snippets/backend.md" >}} resource.

   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.networking.k8s.io/v1
   kind: HTTPRoute
   metadata:
     name: vertex-ai
     namespace: {{< reuse "docs/snippets/namespace.md" >}}
   spec:
     parentRefs:
       - name: agentgateway
         namespace: {{< reuse "docs/snippets/namespace.md" >}}
     rules:
     - matches:
       - path:
           type: PathPrefix
           value: /vertex
       backendRefs:
       - name: vertex-ai
         namespace: {{< reuse "docs/snippets/namespace.md" >}}
         group: gateway.kgateway.dev
         kind: {{< reuse "docs/snippets/backend.md" >}}
   EOF
   ```
   {{% /version %}}{{% version include-if="2.2.x" %}}
4. Create an {{< reuse "docs/snippets/backend.md" >}} resource to configure an LLM provider that references the AI API key secret.
   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: agentgateway.dev/v1alpha1
   kind: {{< reuse "docs/snippets/backend.md" >}}
   metadata:
     name: vertex-ai
     namespace: {{< reuse "docs/snippets/namespace.md" >}}
   spec:
     ai:
       provider:
         vertexai:
           model: gemini-pro
           projectId: "my-gcp-project"
           region: "us-central1"
     policies:
       auth:
         secretRef:
           name: vertex-ai-secret
   EOF
   ```
5. Create an HTTPRoute resource that routes incoming traffic to the {{< reuse "docs/snippets/backend.md" >}}. The following example sets up a route on the `/openai` path to the {{< reuse "docs/snippets/backend.md" >}} that you previously created. The `URLRewrite` filter rewrites the path from `/openai` to the path of the API in the LLM provider that you want to use, `/v1/chat/completions`.

   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.networking.k8s.io/v1
   kind: HTTPRoute
   metadata:
     name: vertex-ai
     namespace: {{< reuse "docs/snippets/namespace.md" >}}
   spec:
     parentRefs:
       - name: agentgateway
         namespace: {{< reuse "docs/snippets/namespace.md" >}}
     rules:
     - matches:
       - path:
           type: PathPrefix
           value: /vertex
       backendRefs:
       - name: vertex-ai
         namespace: {{< reuse "docs/snippets/namespace.md" >}}
         group: agentgateway.dev
         kind: {{< reuse "docs/snippets/backend.md" >}}
   EOF
   ```
   {{% /version %}}

6. Send a request to the LLM provider API. Verify that the request succeeds and that you get back a response from the API.
   
   {{< tabs tabTotal="2" items="Cloud Provider LoadBalancer,Port-forward for local testing" >}}
   {{% tab tabName="Cloud Provider LoadBalancer" %}}
   ```sh
   curl "$INGRESS_GW_ADDRESS/vertex" -H content-type:application/json  -d '{
      "model": "",
      "messages": [
        {
          "role": "user",
          "content": "Write me a short poem about Kubernetes and clouds."
        }
      ]
    }' | jq
   {{% /tab %}}
   {{% tab tabName="Port-forward for local testing" %}}
   ```sh
   curl "localhost:8080/vertex" -H content-type:application/json  -d '{
      "model": "",
      "messages": [
        {
          "role": "user",
          "content": "Write me a short poem about Kubernetes and clouds."
        }
      ]
    }' | jq
   ```
   {{% /tab %}}
   {{< /tabs >}}
   
   Example output: 
   ```json
   {
     "id": "chatcmpl-vertex-12345",
     "object": "chat.completion",
     "created": 1727967462,
     "model": "gemini-pro",
     "choices": [
       {
         "index": 0,
         "message": {
           "role": "assistant",
           "content": "In the cloud, Kubernetes reigns,\nOrchestrating pods with great care,\nContainers float like clouds,\nScaling up and down,\nAutomation everywhere."
         },
         "finish_reason": "stop"
       }
     ],
     "usage": {
       "prompt_tokens": 12,
       "completion_tokens": 28,
       "total_tokens": 40
     }
   }
   ```

{{< reuse "docs/snippets/agentgateway/llm-next.md" >}}
