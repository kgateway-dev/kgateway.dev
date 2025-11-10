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
   
4. Create a Backend resource to configure an LLM provider that references the Anthropic API key secret.
   
   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.kgateway.dev/v1alpha1
   kind: Backend
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
   | `type`      | Set to `AI` to configure this Backend for an AI provider. |
   | `ai`        | Define the AI backend configuration. The example uses Anthropic (`spec.ai.llm.anthropic`). |
   | `authToken` | Configure the authentication token for Anthropic API. The example refers to the secret that you previously created. The token is automatically sent in the `x-api-key` header. |
   | `model`     | Optional: Override the model name, such as `claude-3-opus-20240229`. If unset, the model name is taken from the request. |
   | `apiVersion` | Optional: A version header to pass to the Anthropic API. For more information, see the [Anthropic API versioning docs](https://docs.anthropic.com/en/api/versioning). |

5. Create an HTTPRoute resource that routes incoming traffic to the Backend. The following example sets up a route on the `/anthropic` path. Note that {{< reuse "docs/snippets/kgateway.md" >}} automatically rewrites the endpoint to the Anthropic `/v1/messages` endpoint.

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
         kind: Backend
   EOF
   ```

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
     "id": "msg_0123456789abcdef",
     "type": "message",
     "role": "assistant",
     "content": [
       {
         "type": "text",
         "text": "AI, or artificial intelligence, works by training computers to recognize patterns in data and make predictions or decisions based on those patterns. Think of it like teaching a computer to recognize cats in photos by showing it thousands of cat pictures - eventually it learns what makes a cat a cat. AI systems use algorithms and mathematical models to process information, learn from examples, and then apply that knowledge to new situations."
       }
     ],
     "model": "claude-3-opus-20240229",
     "stop_reason": "end_turn",
     "stop_sequence": null,
     "usage": {
       "input_tokens": 10,
       "output_tokens": 85
     }
   }
   ```

{{< reuse "docs/snippets/agentgateway/llm-next.md" >}}
