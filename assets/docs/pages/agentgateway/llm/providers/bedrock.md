Configure [Amazon Bedrock](https://aws.amazon.com/bedrock/) as an LLM provider in agentgateway.

## Before you begin

1. Set up an [agentgateway proxy]({{< link-hextra path="/agentgateway/setup/" >}}). 
2. Make sure that your [Amazon credentials](https://docs.aws.amazon.com/sdkref/latest/guide/creds-config-files.html) have access to the Bedrock models that you want to use. You can alternatively use an [AWS Bedrock API key](https://docs.aws.amazon.com/bedrock/latest/userguide/api-keys.html). 

## Set up access to Amazon Bedrock {#setup}

1. Store your credentials to access the AWS Bedrock API. 
   {{< tabs tabTotal="2" items="AWS credentials,AWS Bedrock API key" >}}
   {{% tab tabName="AWS credentials" %}}

   1. Log in to the [AWS console](https://console.aws.amazon.com) and store your access credentials as environment variables.
      ```bash
      export AWS_ACCESS_KEY_ID="<aws-access-key-id>"
      export AWS_SECRET_ACCESS_KEY="<aws-secret-access-key>"
      export AWS_SESSION_TOKEN="<aws-session-token>"
      ```

   2. Create a secret with your Bedrock API key. Optionally provide the session token.
      ```yaml
      kubectl create secret generic bedrock-secret \
        -n {{< reuse "docs/snippets/namespace.md" >}} \
        --from-literal=accessKey="$AWS_ACCESS_KEY_ID" \
        --from-literal=secretKey="$AWS_SECRET_ACCESS_KEY" \
        --from-literal=sessionToken="$AWS_SESSION_TOKEN" \
        --type=Opaque \
        --dry-run=client -o yaml | kubectl apply -f -
      ```
   {{% /tab %}}
   {{% tab tabName="AWS Bedrock API key" %}}
   1. Save the API key in an environment variable.
      ```sh
      export BEDROCK_API_KEY=<insert your API key>
      ```

   2. Create a Kubernetes secret to store your Amazon Bedrock API key.
      ```yaml
      kubectl apply -f- <<EOF
      apiVersion: v1
      kind: Secret
      metadata:
        name: bedrock-secret
        namespace: {{< reuse "docs/snippets/namespace.md" >}}
      type: Opaque
      stringData:
        Authorization: $BEDROCK_API_KEY
      EOF
      ```
   {{% /tab %}}
   {{< /tabs >}}
   {{% version include-if="2.1.x" %}}

3. Create a Backend resource to configure an LLM provider that references the AI API key secret.
   
   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.kgateway.dev/v1alpha1
   kind: Backend
   metadata:
     name: bedrock
     namespace: {{< reuse "docs/snippets/namespace.md" >}}
   spec:
     type: AI
     ai:
       llm:
         bedrock:
           model: "amazon.titan-text-lite-v1"
           region: us-east-1
           auth:
             type: Secret
             secretRef:
               name: bedrock-secret
   EOF
   ```

   {{% reuse "docs/snippets/review-table.md" %}} For more information, see the [API reference]({{< link-hextra path="/reference/api/#aibackend" >}}).

   | Setting     | Description |
   |-------------|-------------|
   | `type`      | Set to `AI` to configure this Backend for an AI provider. |
   | `ai`        | Define the AI backend configuration. The example uses Amazon Bedrock (`spec.ai.llm.bedrock`). |
   | `model`     | The model to use to generate responses. In this example, you use the `amazon.titan-text-lite-v1` model. Keep in mind that some models support cross-region inference. These models begin with a `us.` prefix, such as `us.anthropic.claude-sonnet-4-20250514-v1:0`. For more models, see the [AWS Bedrock docs](https://docs.aws.amazon.com/bedrock/latest/userguide/models-supported.html). |
   | `region`    | The AWS region where your Bedrock model is deployed. Multiple regions are not supported. |
   | `auth` | Provide the credentials to use to access the Amazon Bedrock API. The example refers to the secret that you previously created. To use IRSA, omit the `auth` settings.|

4. Create an HTTPRoute resource to route requests through your agentgateway proxy to the Bedrock Backend. Note that {{< reuse "docs/snippets/kgateway.md" >}} automatically rewrites the endpoint that you set up (such as `/bedrock`) to the appropriate chat completion endpoint of the LLM provider for you, based on the LLM provider that you set up in the Backend resource.
   ```yaml
   kubectl apply -f- <<EOF                                             
   apiVersion: gateway.networking.k8s.io/v1
   kind: HTTPRoute
   metadata:       
     name: bedrock
     namespace: {{< reuse "docs/snippets/namespace.md" >}}
   spec:
     parentRefs:
       - name: agentgateway
         namespace: {{< reuse "docs/snippets/namespace.md" >}}
     rules:
     - matches:
       - path:
           type: PathPrefix
           value: /bedrock
       backendRefs:
       - name: bedrock
         namespace: {{< reuse "docs/snippets/namespace.md" >}}
         group: gateway.kgateway.dev
         kind: Backend
   EOF
   ```
   {{% /version %}}{{% version include-if="2.2.x" %}}

3. Create an AgentgatewayBackend resource to configure your LLM provider. Make sure to reference the secret that holds your credentials to access the LLM. 
   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.kgateway.dev/v1alpha1
   kind: AgentgatewayBackend
   metadata:
     name: bedrock
     namespace: {{< reuse "docs/snippets/namespace.md" >}}
   spec:
     ai:
       provider:
         bedrock:
           model: "amazon.titan-text-lite-v1"
           region: "us-east-1"
     policies:
       auth:
         secretRef:
           name: bedrock-secret
   EOF
   ```

   {{% reuse "docs/snippets/review-table.md" %}} For more information, see the [API reference]({{< link-hextra path="/reference/api/#aibackend" >}}).

   | Setting     | Description |
   |-------------|-------------|
   | `ai.provider.bedrock` | Define the LLM provider that you want to use. The example uses Amazon Bedrock. |
   | `bedrock.model`     | The model to use to generate responses. In this example, you use the `amazon.titan-text-lite-v1` model. Keep in mind that some models support cross-region inference. These models begin with a `us.` prefix, such as `us.anthropic.claude-sonnet-4-20250514-v1:0`. For more models, see the [AWS Bedrock docs](https://docs.aws.amazon.com/bedrock/latest/userguide/models-supported.html). |
   | `bedrock.region`    | The AWS region where your Bedrock model is deployed. Multiple regions are not supported. |
   | `policies.auth` | Provide the credentials to use to access the Amazon Bedrock API. The example refers to the secret that you previously created. To use IRSA, omit the `auth` settings.|

4. Create an HTTPRoute resource to route requests through your agentgateway proxy to the Bedrock AgentgatewayBackend. Note that {{< reuse "docs/snippets/kgateway.md" >}} automatically rewrites the endpoint that you set up (such as `/bedrock`) to the appropriate chat completion endpoint of the LLM provider for you, based on the LLM provider that you set up in the Backend resource.
   ```yaml
   kubectl apply -f- <<EOF                                             
   apiVersion: gateway.networking.k8s.io/v1
   kind: HTTPRoute
   metadata:       
     name: bedrock
     namespace: {{< reuse "docs/snippets/namespace.md" >}}
   spec:
     parentRefs:
       - name: agentgateway
         namespace: {{< reuse "docs/snippets/namespace.md" >}}
     rules:
     - matches:
       - path:
           type: PathPrefix
           value: /bedrock
       backendRefs:
       - name: bedrock
         namespace: {{< reuse "docs/snippets/namespace.md" >}}
         group: gateway.kgateway.dev
         kind: AgentgatewayBackend
   EOF
   ```
   {{% /version %}}
5. Send a request to the LLM provider API. Verify that the request succeeds and that you get back a response from the chat completion API.

   {{< tabs tabTotal="2" items="Cloud Provider LoadBalancer,Port-forward for local testing" >}}
   {{% tab tabName="Cloud Provider LoadBalancer" %}}
   ```sh
   curl "$INGRESS_GW_ADDRESS:8080/bedrock" -H content-type:application/json -d '{
       "model": "",
       "messages": [
         {
           "role": "user",
           "content": "You are a cloud native solutions architect, skilled in explaining complex technical concepts such as API Gateway, microservices, LLM operations, kubernetes, and advanced networking patterns. Write me a 20-word pitch on why I should use an AI gateway in my Kubernetes cluster."
         }
       ]
     }' | jq
   {{% /tab %}}
   {{% tab tabName="Port-forward for local testing" %}}
   ```sh
   curl "localhost:8080/bedrock" -H content-type:application/json  -d '{
       "model": "",
       "messages": [
         {
           "role": "user",
           "content": "You are a cloud native solutions architect, skilled in explaining complex technical concepts such as API Gateway, microservices, LLM operations, kubernetes, and advanced networking patterns. Write me a 20-word pitch on why I should use an AI gateway in my Kubernetes cluster."
         }
       ]
     }' | jq
   ```
   {{% /tab %}}
   {{< /tabs >}}
   
   Example output: 
   ```json
   {
     "metrics": {
       "latencyMs": 2097
     },
     "output": {
       "message": {
         "content": [
           {
             "text": "\nAn AI gateway in your Kubernetes cluster can enhance performance, scalability, and security while simplifying complex operations. It provides a centralized entry point for AI workloads, automates deployment and management, and ensures high availability."
           }
         ],
         "role": "assistant"
       }
     },
     "stopReason": "end_turn",
     "usage": {
       "inputTokens": 60,
       "outputTokens": 47,
       "totalTokens": 107
     }
   }
   ```

{{< reuse "docs/snippets/agentgateway/llm-next.md" >}}
