Configure [Anthropic (Claude)](https://claude.ai/) as an LLM provider in {{< reuse "docs/snippets/agentgateway.md" >}}.

## Before you begin

Set up an [agentgateway proxy]({{< link-hextra path="/agentgateway/setup" >}}). 

## Set up access to Anthropic

1. Get an API key to access the [Anthropic API](https://console.anthropic.com/). 

2. Save the API key in an environment variable.
   
   ```sh
   export ANTHROPIC_API_KEY=<insert your API key>
   ```

3. Create a Kubernetes secret to store your Anthropic API key.

   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: v1
   kind: Secret
   metadata:
     name: anthropic-secret
     namespace: {{< reuse "docs/snippets/namespace.md" >}}
   type: Opaque
   stringData:
     Authorization: $ANTHROPIC_API_KEY
   EOF
   ```
   {{% version include-if="2.1.x" %}}
   
4. Create a {{< reuse "docs/snippets/backend.md" >}} resource to configure an LLM provider that references the Anthropic API key secret.
   
   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.kgateway.dev/v1alpha1
   kind: {{< reuse "docs/snippets/backend.md" >}}
   metadata:
     name: anthropic
     namespace: {{< reuse "docs/snippets/namespace.md" >}}
   spec:
     type: AI
     ai:
       llm:
         anthropic:
           authToken:
             kind: SecretRef
             secretRef:
               name: anthropic-secret
           model: "claude-3-opus-20240229"
           apiVersion: "2023-06-01"
   EOF
   ```

   {{% reuse "docs/snippets/review-table.md" %}} For more information, see the [API reference]({{< link-hextra path="/reference/api/#aibackend" >}}).

   | Setting     | Description |
   |-------------|-------------|
   | `type`      | Set to `AI` to configure this {{< reuse "docs/snippets/backend.md" >}} for an AI provider. |
   | `ai`        | Define the AI backend configuration. The example uses Anthropic (`spec.ai.llm.anthropic`). |
   | `authToken` | Configure the authentication token for Anthropic API. The example refers to the secret that you previously created. The token is automatically sent in the `x-api-key` header. |
   | `model`     | Optional: Override the model name, such as `claude-3-opus-20240229`. If unset, the model name is taken from the request. |
   | `apiVersion` | Optional: A version header to pass to the Anthropic API. For more information, see the [Anthropic API versioning docs](https://docs.anthropic.com/en/api/versioning). |

5. Create an HTTPRoute resource that routes incoming traffic to the {{< reuse "docs/snippets/backend.md" >}}. The following example sets up a route on the `/anthropic` path. Note that {{< reuse "docs/snippets/kgateway.md" >}} automatically rewrites the endpoint to the Anthropic `/v1/messages` endpoint.

   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.networking.k8s.io/v1
   kind: HTTPRoute
   metadata:
     name: anthropic
     namespace: {{< reuse "docs/snippets/namespace.md" >}}
   spec:
     parentRefs:
       - name: agentgateway
         namespace: {{< reuse "docs/snippets/namespace.md" >}}
     rules:
     - matches:
       - path:
           type: PathPrefix
           value: /anthropic
       backendRefs:
       - name: anthropic
         namespace: {{< reuse "docs/snippets/namespace.md" >}}
         group: gateway.kgateway.dev
         kind: {{< reuse "docs/snippets/backend.md" >}}
   EOF
   ```
   {{% /version %}} {{% version include-if="2.2.x" %}}
4. Create an {{< reuse "docs/snippets/backend.md" >}} resource to configure your LLM provider that references the Anthropic API key secret.
   
   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: agentgateway.dev/v1alpha1
   kind: {{< reuse "docs/snippets/backend.md" >}}
   metadata:
     name: anthropic
     namespace: {{< reuse "docs/snippets/namespace.md" >}}
   spec:
     ai:
       provider:
         anthropic:
           model: "claude-3-opus-20240229"
     policies:
       auth:
         secretRef:
           name: anthropic-secret
   EOF
   ```

   {{% reuse "docs/snippets/review-table.md" %}} For more information, see the [API reference]({{< link-hextra path="/reference/api/#agentgatewaybackend" >}}).

   | Setting     | Description |
   |-------------|-------------|
   | `ai.provider.anthropic` | Define the LLM provider that you want to use. The example uses Anthropic. |
   | `anthropic.model`     | The model to use to generate responses. In this example, you use the `claude-3-opus-20240229` model. |
   | `policies.auth` | Provide the credentials to use to access the Anthropic API. The example refers to the secret that you previously created. The token is automatically sent in the `x-api-key` header.|

5. Create an HTTPRoute resource that routes incoming traffic to the {{< reuse "docs/snippets/backend.md" >}}. The following example sets up a route on the `/anthropic` path. Note that {{< reuse "docs/snippets/kgateway.md" >}} automatically rewrites the endpoint to the Anthropic `/v1/messages` endpoint.

   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.networking.k8s.io/v1
   kind: HTTPRoute
   metadata:
     name: anthropic
     namespace: {{< reuse "docs/snippets/namespace.md" >}}
   spec:
     parentRefs:
       - name: agentgateway
         namespace: {{< reuse "docs/snippets/namespace.md" >}}
     rules:
     - matches:
       - path:
           type: PathPrefix
           value: /anthropic
       backendRefs:
       - name: anthropic
         namespace: {{< reuse "docs/snippets/namespace.md" >}}
         group: agentgateway.dev
         kind: {{< reuse "docs/snippets/backend.md" >}}
   EOF
   ```
   {{% /version %}}

6. Send a request to the LLM provider API. Note that Anthropic uses the `/v1/messages` endpoint format instead of `/v1/chat/completions`. Verify that the request succeeds and that you get back a response from the API.
   
   {{< tabs tabTotal="2" items="Cloud Provider LoadBalancer,Port-forward for local testing" >}}
   {{% tab tabName="Cloud Provider LoadBalancer" %}}
   ```sh
   curl "$INGRESS_GW_ADDRESS:8080/anthropic" -H content-type:application/json  -d '{
      "model": "",
      "messages": [
        {
          "role": "user",
          "content": "Explain how AI works in simple terms."
        }
      ]
    }' | jq
   {{% /tab %}}
   {{% tab tabName="Port-forward for local testing" %}}
   ```sh
   curl "localhost:8080/anthropic" -H content-type:application/json  -d '{
      "model": "",
      "messages": [
        {
          "role": "user",
          "content": "Explain how AI works in simple terms."
        }
      ]
    }' | jq
   ```
   {{% /tab %}}
   {{< /tabs >}}
   
   Example output: 
   ```json
   {
     "model": "claude-3-opus-20240229",
     "usage": {
       "prompt_tokens": 16,
       "completion_tokens": 318,
       "total_tokens": 334
     },
     "choices": [
       {
         "message": {
           "content": "Artificial Intelligence (AI) is a field of computer science that focuses on creating machines that can perform tasks that typically require human intelligence, such as visual perception, speech recognition, decision-making, and language translation. Here's a simple explanation of how AI works:\n\n1. Data input: AI systems require data to learn and make decisions. This data can be in the form of images, text, numbers, or any other format.\n\n2. Training: The AI system is trained using this data. During training, the system learns to recognize patterns, relationships, and make predictions based on the input data.\n\n3. Algorithms: AI uses various algorithms, which are sets of instructions or rules, to process and analyze the data. These algorithms can be simple or complex, depending on the task at hand.\n\n4. Machine Learning: A subset of AI, machine learning, enables the system to automatically learn and improve from experience without being explicitly programmed. As the AI system is exposed to more data, it can refine its algorithms and become more accurate over time.\n\n5. Output: Once the AI system has processed the data, it generates an output. This output can be a prediction, a decision, or an action, depending on the purpose of the AI system.\n\nAI can be categorized into narrow (weak) AI and general (strong) AI. Narrow AI is designed to perform a specific task, such as playing chess or recognizing speech, while general AI aims to have human-like intelligence that can perform any intellectual task.",
           "role": "assistant"
         },
         "index": 0,
         "finish_reason": "stop"
       }
     ],
     "id": "msg_01PbaJfDHnjEBG4BueJNR2ff",
     "created": 1764627002,
     "object": "chat.completion"
   }
   ```

{{< reuse "docs/snippets/agentgateway/llm-next.md" >}}
