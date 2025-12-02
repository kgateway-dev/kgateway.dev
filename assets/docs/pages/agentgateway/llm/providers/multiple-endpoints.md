Configure access to multiple OpenAI API endpoints such as for chat completions, embeddings, and models through the same Backend.

## About

To set up multiple LLM endpoints, use the `ai.llm.routes` field. This field maps the API paths to supported route types. The keys are URL suffix matches, like `/v1/models`. The values are the route types, like `completions` or `passthrough`.

- `completions`: Transforms to the LLM provider format and processes the request with the LLM provider. This route type supports full LLM features such as tokenization, rate limiting, transformations, and other policies like prompt guards.
- `passthrough`: Forwards the request to the LLM provider as-is. This route type does not support LLM features like route processing and policies. You might use this route type for non-chat endpoints such as health checks, `GET` requests like listing models, or custom endpoints that you want to pass traffic through to.

Paths are matched in order, and the first match determines how the request is handled. The wildcard character `*` can be used to match anything. If no route is set, the route defaults to the completions endpoint.

## Before you begin

1. Set up an [agentgateway proxy]({{< link-hextra path="/agentgateway/setup" >}}).
2. Set up [API access to each LLM provider]({{< link-hextra path="/agentgateway/llm/api-keys/" >}}) that you want to use. The example in this guide uses OpenAI.

## Configure multiple endpoints

Configure access to multiple endpoints in your LLM provider, such as for chat completions, embeddings, and models through the same Agentgatewaybackend. The following steps use OpenAI as an example.

1. Update your AgentgatewayBackend resource to include a `routes` field that maps API paths to route types.
   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.kgateway.dev/v1alpha1
   kind: AgentgatewayBackend
   metadata:
     name: openai
     namespace: {{< reuse "docs/snippets/namespace.md" >}}
   spec:
     ai:
       provider:
         openai:
           model: gpt-3.5-turbo  # Optional: specify default model
        # host: api.openai.com  # Optional: custom host if needed
        # port: 443  # Optional: custom port
     policies:
       auth:
         secretRef:
           name: openai-secret
       ai: 
         routes: 
           "/v1/chat/completions": "completions"
           "/v1/embeddings": "passthrough"
           "/v1/models": "passthrough"
           "*": "passthrough"
   EOF
   ```

   | Setting | Description |
   |---------|-------------|
   | `v1/chat/completions` | Routes to the chat completions endpoint with LLM-specific processing. This endpoint is used for chat-based interactions. For more information, see the [OpenAI API docs for the endpoint](https://platform.openai.com/docs/api-reference/chat).|
   | `v1/embeddings` | Routes to the embeddings endpoint with passthrough processing. This endpoint is used to to get vector embeddings that machine learning models can use more easily than chat-based interactions. For more information, see the [OpenAI API docs for the endpoint](https://platform.openai.com/docs/api-reference/embeddings).|
   | `v1/models` | Routes to the models endpoint with passthrough processing. This endpoint is used to get basic information about the models that are available. For more information, see the [OpenAI API docs for the endpoint](https://platform.openai.com/docs/api-reference/models/list).|
   | `*` | Matches any path that doesn't match the specific endpoints otherwise set. Typically, you set this value to `passthrough` to pass through to the provider API without LLM-specific processing.|

2. Create an HTTPRoute resource that routes traffic to the OpenAI Backend along the `/openai` path matcher. Note that because you set up the `routes` map on the AgentgatewayBackend, you do not need to create any URLRewrite filters to point your route matcher to the correct LLM provider endpoint.

   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.networking.k8s.io/v1
   kind: HTTPRoute
   metadata:
     name: openai
     namespace: {{< reuse "docs/snippets/namespace.md" >}}
   spec:
     parentRefs:
       - name: agentgateway
         namespace: {{< reuse "docs/snippets/namespace.md" >}}
     rules:
     - matches:
       - path:
           type: PathPrefix
           value: /openai
       backendRefs:
       - name: openai
         namespace: {{< reuse "docs/snippets/namespace.md" >}}
         group: gateway.kgateway.dev
         kind: AgentgatewayBackend
   EOF
   ```
3. Send requests to different OpenAI endpoints. With the routes configured, you can access different OpenAI endpoints by including the full path in your requests:

   {{< tabs tabTotal="2" items="Cloud Provider LoadBalancer,Port-forward for local testing" >}}
   {{% tab tabName="Cloud Provider LoadBalancer" %}}
   **Chat completions:**
   ```sh
   curl "$INGRESS_GW_ADDRESS:8080/openai/v1/chat/completions" \
     -H content-type:application/json \
     -d '{
       "model": "gpt-3.5-turbo",
       "messages": [{"role": "user", "content": "Hello!"}]
     }' | jq
   ```

   **Embeddings:**
   ```sh
   curl "$INGRESS_GW_ADDRESS:8080/openai/v1/embeddings" \
     -H content-type:application/json \
     -d '{
       "model": "text-embedding-ada-002",
       "input": "The food was delicious"
     }' | jq
   ```

   **Models list:**
   ```sh
   curl "$INGRESS_GW_ADDRESS:8080/openai/v1/models" | jq
   ```
   {{% /tab %}}
   {{% tab tabName="Port-forward for local testing" %}}
   **Chat completions:**
   ```sh
   curl "localhost:8080/openai/v1/chat/completions" \
     -H content-type:application/json \
     -d '{
       "model": "gpt-3.5-turbo",
       "messages": [{"role": "user", "content": "Hello!"}]
     }' | jq
   ```

   **Embeddings:**
   ```sh
   curl "localhost:8080/openai/v1/embeddings" \
     -H content-type:application/json \
     -d '{
       "model": "text-embedding-ada-002",
       "input": "The food was delicious"
     }' | jq
   ```

   **Models list:**
   ```sh
   curl "localhost:8080/openai/v1/models" | jq
   ```
   {{% /tab %}}
   {{< /tabs >}}
