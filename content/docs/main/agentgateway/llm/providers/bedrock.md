---
title: Amazon Bedrock
weight: 50
description:
---

Configure [Amazon Bedrock](https://aws.amazon.com/bedrock/) as an LLM provider in agentgateway.

## Before you begin

1. Set up an [agentgateway proxy]({{< link-hextra path="/agentgateway/setup/" >}}). 
2. Make sure that your [Amazon credentials](https://docs.aws.amazon.com/sdkref/latest/guide/creds-config-files.html) have access to the Bedrock models that you want to use.

## Set up access to Amazon Bedrock {#setup}

1. Log in to the [AWS console](https://console.aws.amazon.com) and store your access credentials as environment variables.

   ```bash
   export AWS_ACCESS_KEY_ID="<aws-access-key-id>"
   export AWS_SECRET_ACCESS_KEY="<aws-secret-access-key>"
   export AWS_SESSION_TOKEN="<aws-session-token>"
   ```

2. Create a secret with your Bedrock API key.

   ```yaml
   kubectl create secret generic bedrock-secret \
     -n {{< reuse "docs/snippets/namespace.md" >}} \
     --from-literal=aws_access_key_id="$AWS_ACCESS_KEY_ID" \
     --from-literal=aws_secret_access_key="$AWS_SECRET_ACCESS_KEY" \
     --from-literal=aws_session_token="$AWS_SESSION_TOKEN" \
     --type=Opaque \
     --dry-run=client -o yaml | kubectl apply -f -
   ```

3. Create a Backend resource to configure an LLM provider that references the AI API key secret.
   
   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.kgateway.dev/v1alpha1
   kind: Backend
   metadata:
     labels:
       app: agentgateway
     name: bedrock
     namespace: {{< reuse "docs/snippets/namespace.md" >}}
   spec:
     type: AI
     ai:
       llm:
         provider:
           bedrock:
             model: "amazon.titan-text-lite-v1"
             region: us-east-1
             auth:
               type: Secret
               secretRef:
                 name: bedrock-secret
   EOF
   ```

   {{% reuse "docs/snippets/review-table.md" %}} For more information or other providers, see the [API reference]({{< link-hextra path="/reference/api/#aibackend" >}}).

   | Setting     | Description |
   |-------------|-------------|
   | `type`      | Set to `AI` to configure this Backend for an AI provider. |
   | `ai`        | Define the AI backend configuration. The example uses Amazon Bedrock (`spec.ai.llm.provider.bedrock`). |
   | `model`     | The model to use to generate responses. In this example, you use the `amazon.titan-text-lite-v1` model. For more models, see the [AWS Bedrock docs](https://docs.aws.amazon.com/bedrock/latest/userguide/models-supported.html). |
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
5. Send a request to the LLM provider API. Verify that the request succeeds and that you get back a response from the chat completion API.

   {{< tabs tabTotal="2" items="Cloud Provider LoadBalancer,Port-forward for local testing" >}}
   {{% tab tabName="Cloud Provider LoadBalancer" %}}
   ```sh
   curl "$INGRESS_GW_ADDRESS:8080/bedrock" -H content-type:application/json -d '{
       "model": "",
       "messages": [
         {
           "role": "user",
           "content": [
             {
               "text": "You are a cloud native solutions architect, skilled in explaining complex technical concepts such as API Gateway, microservices, LLM operations, kubernetes, and advanced networking patterns. Write me a 20-word pitch on why I should use an AI gateway in my Kubernetes cluster."
             }
           ]
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
           "content": [
             {
               "text": "You are a cloud native solutions architect, skilled in explaining complex technical concepts such as API Gateway, microservices, LLM operations, kubernetes, and advanced networking patterns. Write me a 20-word pitch on why I should use an AI gateway in my Kubernetes cluster."
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
