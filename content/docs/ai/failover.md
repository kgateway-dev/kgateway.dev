---
title: Model failover
weight: 20
---

Prioritize the failover of requests across different models from an LLM provider.

## About failover {#about}

Failover is a way to keep services running smoothly by automatically switching to a backup system when the main one fails or becomes unavailable.

For AI gateways, you can set up failover for the models of the LLM providers that you want to prioritize. If the main model from one provider goes down, slows, or has any issue, the system quickly switches to a backup model from that same provider. This keeps the service running without interruptions.

This approach increases the resiliency of your network environment by ensuring that apps that call LLMs can keep working without problems, even if one model has issues.

## Before you begin

1. [Set up AI Gateway](/ai/tutorials/setup-gw/).
2. [Authenticate to the LLM](/ai/guides/auth/).
3. {{< reuse "docs/snippets/ai-gateway-address.md" >}}

## Fail over to other models {#model-failover}

In this example, you deploy an example `model-failover` app to your cluster. The app simulates a failure scenario for three models from the OpenAI LLM provider.

1. Deploy the example `model-failover` app. The app simulates a failure scenario for three models from the OpenAI LLM provider. This way, you can check that the request fails over to each model in turn.

   ```shell
   kubectl apply -f- <<EOF
   apiVersion: apps/v1
   kind: Deployment
   metadata:
     name: model-failover
     namespace: {{< reuse "docs/snippets/ns-system.md" >}}
     labels:
       app: model-failover
   spec:
     selector:
       matchLabels:
         app: model-failover
     replicas: 1
     template:
       metadata:
         labels:
           app: model-failover
       spec:
         containers:
           - name: model-failover
             image: gcr.io/field-engineering-eu/model-failover:latest
             imagePullPolicy: IfNotPresent
             ports:
               - containerPort: 8080
   ---
   apiVersion: v1
   kind: Service
   metadata:
     name: model-failover
     namespace: {{< reuse "docs/snippets/ns-system.md" >}}
     labels:
       app: model-failover
   spec:
     ports:
     - port: 80
       targetPort: 8080
       protocol: TCP
     selector:
       app: model-failover
   EOF
   ```

2. Verify that the `model-failover` app is running.

   ```shell
   kubectl -n {{< reuse "docs/snippets/ns-system.md" >}} rollout status deploy model-failover
   ```

3. Create or update the Backend for your LLM providers. The following example uses the `spec.ai.multi.priorities` setting to configure three pools for the example OpenAI LLM provider. Each pool represents a specific model from the LLM provider that fails over in the following order of priority. By default, each request is tried 3 times before marked as failed. The Backend uses the `model-failover` app as the destination for requests instead of the actual OpenAI API endpoint. For more information, see the [MultiPool API reference docs](/docs/reference/api/#multipoolconfig).
   
   1. OpenAI `gpt-4o` model
   2. OpenAI `gpt-4.0-turbo` model
   3. OpenAI `gpt-3.5-turbo` model

   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.kgateway.dev/v1alpha1
   kind: Backend
   metadata:
     labels:
       app: model-failover
     name: model-failover
     namespace: kgateway-system
   spec:
     type: AI
     ai:
       multipool:
         priorities:
         - pool:
           - hostOverride:
               host: model-failover.kgateway-system.svc.cluster.local
               port: 80
             provider:
               openai:
                 model: "gpt-4o"
                 authToken:
                   kind: SecretRef
                   secretRef:
                     name: openai-secret
         - pool:
           - hostOverride:
               host: model-failover.kgateway-system.svc.cluster.local
               port: 80
             provider:
               openai:
                 model: "gpt-4.0-turbo"
                 authToken:
                   kind: SecretRef
                   secretRef:
                     name: openai-secret
         - pool:
           - hostOverride:
               host: model-failover.kgateway-system.svc.cluster.local
               port: 80
             provider:
               openai:
                 model: "gpt-3.5-turbo"
                 authToken:
                   kind: SecretRef
                   secretRef:
                     name: openai-secret
   EOF
   ```

4. Create an HTTPRoute resource that routes incoming traffic on the `/model` path to the Backend backend that you created in the previous step. In this example, the URLRewrite filter rewrites the path from `/model` to the path of the API in the LLM provider that you want to use, such as `/v1/chat/` completions for OpenAI.

   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.networking.k8s.io/v1
   kind: HTTPRoute
   metadata:
     name: model-failover
     namespace: {{< reuse "docs/snippets/ns-system.md" >}}
     labels:
       app: model-failover
   spec:
     parentRefs:
       - name: ai-gateway
         namespace: {{< reuse "docs/snippets/ns-system.md" >}}
     rules:
     - matches:
       - path:
           type: PathPrefix
           value: /model
       filters:
       - type: URLRewrite
         urlRewrite:
           path:
             type: ReplaceFullPath
             replaceFullPath: /v1/chat/completions
       backendRefs:
       - name: model-failover
         namespace: {{< reuse "docs/snippets/ns-system.md" >}}
         group: gateway.kgateway.dev
         kind: Backend
   EOF
   ```

5. Send a request to observe the failover.

   {{< tabs items="Cloud Provider LoadBalancer,Port-forward for local testing" >}}
   {{< tab >}}
   ```bash
   curl -v "$INGRESS_GW_ADDRESS:8080/model" -H content-type:application/json -d '{
     "model": "gpt-4o",
     "messages": [
       {
         "role": "system",
         "content": "You are a poetic assistant, skilled in explaining complex programming concepts with creative flair."
       },
       {
         "role": "user",
         "content": "Compose a poem that explains the concept of recursion in programming."
       }
     ]
   }' | jq
   ```
   {{< /tab >}}
   {{< tab >}}
   ```bash
   curl -v "localhost:8080/model" -H content-type:application/json -d '{
     "model": "gpt-4o",
     "messages": [
       {
         "role": "system",
         "content": "You are a poetic assistant, skilled in explaining complex programming concepts with creative flair."
       },
       {
         "role": "user",
         "content": "Compose a poem that explains the concept of recursion in programming."
       }
     ]
   }'
   ```
   {{< /tab >}}
   {{< /tabs >}}
   Example output: Note the example `model-failover` app is configured to return a 429 response to simulate a model failure.

   ```
   ...
   < HTTP/1.1 429 Too Many Requests
   ```

7. Check the logs of the `model-failover` app to verify that the requests were received in the order of priority, starting with the `gpt-4o` model.

   ```shell
   kubectl logs deploy/model-failover -n {{< reuse "docs/snippets/ns-system.md" >}}
   ```

   Example output: Notice the 3 log lines that correspond to the initial request (sent to model `gpt-4o`) and the two failover requests (sent to models `gpt-4.0-turbo` and `gpt-3.5-turbo` respectively).

   ```json
   {"time":"2024-07-01T17:11:23.994822887Z","level":"INFO","msg":"Request received","msg":"{\"messages\":[{\"content\":\"You are a poetic assistant, skilled in explaining complex programming concepts with creative flair.\",\"role\":\"system\"},{\"content\":\"Compose a poem that explains the concept of recursion in programming.\",\"role\":\"user\"}],\"model\":\"gpt-4o\"}"}
   {"time":"2024-07-01T17:11:24.006768184Z","level":"INFO","msg":"Request received","msg":"{\"messages\":[{\"content\":\"You are a poetic assistant, skilled in explaining complex programming concepts with creative flair.\",\"role\":\"system\"},{\"content\":\"Compose a poem that explains the concept of recursion in programming.\",\"role\":\"user\"}],\"model\":\"gpt-4.0-turbo\"}"}
   {"time":"2024-07-01T17:11:24.012805385Z","level":"INFO","msg":"Request received","msg":"{\"messages\":[{\"content\":\"You are a poetic assistant, skilled in explaining complex programming concepts with creative flair.\",\"role\":\"system\"},{\"content\":\"Compose a poem that explains the concept of recursion in programming.\",\"role\":\"user\"}],\"model\":\"gpt-3.5-turbo\"}"}
   ```

## Cleanup

{{< reuse "docs/snippets/cleanup.md" >}}

   ```shell
   kubectl delete secret -n {{< reuse "docs/snippets/ns-system.md" >}} openai-secret
   kubectl delete backend,deployment,httproute,service -n {{< reuse "docs/snippets/ns-system.md" >}} -l app=model-failover
   ```

## Next

* Explore how to set up [prompt guards](/docs/ai/prompt-guards/) to block unwanted requests and mask sensitive data.
* [Enrich your prompts](/docs/ai/prompt-enrichment/) with system prompts to improve LLM outputs.
