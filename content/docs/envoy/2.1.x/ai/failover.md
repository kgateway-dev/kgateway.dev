---
title: Model failover
weight: 30
---

{{< reuse "docs/snippets/ai-deprecation-note.md" >}}

Prioritize the failover of requests across different models from an LLM provider.

## About failover {#about}

Failover is a way to keep services running smoothly by automatically switching to a backup system when the main one fails or becomes unavailable.

For AI gateways, you can set up failover for the models of the LLM providers that you want to prioritize. If the main model from one provider goes down, slows, or has any issue, the system quickly switches to a backup model from that same provider. This keeps the service running without interruptions.

This approach increases the resiliency of your network environment by ensuring that apps that call LLMs can keep working without problems, even if one model has issues.

## Before you begin

1. [Set up AI Gateway](../setup/).
2. [Authenticate to the LLM](../auth/).
3. {{< reuse "docs/snippets/ai-gateway-address.md" >}}

## Fail over to other models {#model-failover}

You can configure failover across multiple models and providers by using priority groups. Each priority group represents a set of providers that share the same priority level. Failover priority is determined by the order in which the priority groups are listed in the Backend. The priority group that is listed first is assigned the highest priority. Models within the same priority group are load balanced (round-robin), not prioritized.

1. Create or update the Backend for your LLM providers.

   {{< tabs tabTotal="2" items="OpenAI model priority,Cost-based priority across providers" >}}
   {{% tab tabName="OpenAI model priority" %}}
   
   In this example, you configure separate priority groups for failover across multiple models from the same LLM provider, OpenAI. The priority order of the models is as follows:
   
   1. OpenAI `gpt-4o` model (highest priority)
   2. OpenAI `gpt-4.0-turbo` model (fallback)
   3. OpenAI `gpt-3.5-turbo` model (lowest priority)

   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.kgateway.dev/v1alpha1
   kind: Backend
   metadata:
     labels:
       app: model-failover
     name: model-failover
     namespace: {{< reuse "docs/snippets/namespace.md" >}}
   spec:
     type: AI
     ai:
       priorityGroups:
       - providers:
         - name: openai-gpt-4o
           openai:
             model: "gpt-4o"
             authToken:
               kind: SecretRef
               secretRef:
                 name: openai-secret
       - providers:
         - name: openai-gpt-4.0-turbo
           openai:
             model: "gpt-4.0-turbo"
             authToken:
               kind: SecretRef
               secretRef:
                 name: openai-secret
       - providers:
         - name: openai-gpt-3.5-turbo
           openai:
             model: "gpt-3.5-turbo"
             authToken:
               kind: SecretRef
               secretRef:
                 name: openai-secret
   EOF
   ```
   
   {{% /tab %}}
   {{% tab tabName="Cost-based priority across providers" %}}
   
   In this example, you configure failover across multiple providers with cost-based priority. The first priority group contains cheaper models. Responses are load-balanced across these models. In the event that both models are unavailable, requests fall back to the second priority group of more premium models.
   - Highest priority: Load balance across cheaper OpenAI `gpt-3.5-turbo` and Anthropic `claude-3-5-haiku-latest` models.
   - Fallback: Load balance across more premium OpenAI `gpt-4.0-turbo` and Anthropic `claude-opus-4-1` models.

   Make sure that you configured both Anthropic and OpenAI providers.

   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.kgateway.dev/v1alpha1
   kind: Backend
   metadata:
     labels:
       app: model-failover
     name: model-failover
     namespace: {{< reuse "docs/snippets/namespace.md" >}}
   spec:
     type: AI
     ai:
       priorityGroups:
       - providers:
         - name: openai-gpt-3.5-turbo
           openai:
             model: "gpt-3.5-turbo"
             authToken:
               kind: SecretRef
               secretRef:
                 name: openai-secret
         - name: claude-haiku
           anthropic:
             model: "claude-3-5-haiku-latest"
             authToken:
               kind: SecretRef
               secretRef:
                 name: anthropic-secret
       - providers:
         - name: openai-gpt-4.0-turbo
           openai:
             model: "gpt-4.0-turbo"
             authToken:
               kind: SecretRef
               secretRef:
                 name: openai-secret
         - name: claude-opus
           anthropic:
             model: "claude-opus-4-1"
             authToken:
               kind: SecretRef
               secretRef:
                 name: anthropic-secret
   EOF
   ```
   
   {{% /tab %}}
   {{< /tabs >}}

2. Create an HTTPRoute resource that routes incoming traffic on the `/model` path to the Backend that you created in the previous step. In this example, the URLRewrite filter rewrites the path from `/model` to the path of the API in the LLM provider that you want to use, such as `/v1/chat/` completions for OpenAI.

   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.networking.k8s.io/v1
   kind: HTTPRoute
   metadata:
     name: model-failover
     namespace: {{< reuse "docs/snippets/namespace.md" >}}
     labels:
       app: model-failover
   spec:
     parentRefs:
       - name: ai-gateway
         namespace: {{< reuse "docs/snippets/namespace.md" >}}
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
         namespace: {{< reuse "docs/snippets/namespace.md" >}}
         group: gateway.kgateway.dev
         kind: Backend
   EOF
   ```

3. Send a request to observe the failover. In your request, do not specify a model. Instead, the Backend automatically uses the model from the first pool in the priority order.

   {{< tabs tabTotal="2" items="Cloud Provider LoadBalancer,Port-forward for local testing" >}}
   {{% tab tabName="Cloud Provider LoadBalancer" %}}
   ```bash
   curl -v "$INGRESS_GW_ADDRESS:8080/model" -H content-type:application/json -d '{
     "messages": [
       {
         "role": "user",
         "content": "What is kubernetes?"
       }
   ]}' | jq
   ```
   {{% /tab %}}
   {{% tab tabName="Port-forward for local testing" %}}
   ```bash
   curl -v "localhost:8080/model" -H content-type:application/json -d '{
     "messages": [
       {
         "role": "user",
         "content": "What is kubernetes?"
       }
   ]}' | jq
   ```
   {{< /tab >}}
   {{< /tabs >}}
   
   Example output:

   {{< tabs tabTotal="2" items="OpenAI model priority,Cost-based priority across providers" >}}
   {{% tab tabName="OpenAI model priority" %}}
   
   Note the response is from the `gpt-4o` model, which is the first model in the priority order from the Backend.

   ```json {linenos=table,hl_lines=[5],linenostart=1,filename="model-response.json"}
   {
     "id": "chatcmpl-BFQ8Lldo9kLC56S1DFVbIonOQll9t",
     "object": "chat.completion",
     "created": 1743015077,
     "model": "gpt-4o-2024-08-06",
     "choices": [
       {
         "index": 0,
         "message": {
           "role": "assistant",
           "content": "Kubernetes is an open-source container orchestration platform designed to automate the deployment, scaling, and management of containerized applications. Originally developed by Google, it is now maintained by the Cloud Native Computing Foundation (CNCF).\n\nKubernetes provides a framework to run distributed systems resiliently. It manages containerized applications across a cluster of machines, offering features such as:\n\n1. **Automatic Bin Packing**: It can optimize resource usage by automatically placing containers based on their resource requirements and constraints while not sacrificing availability.\n\n2. **Self-Healing**: Restarts failed containers, replaces and reschedules containers when nodes die, and kills and reschedules containers that are unresponsive to user-defined health checks.\n\n3. **Horizontal Scaling**: Scales applications and resources up or down automatically, manually, or based on CPU usage.\n\n4. **Service Discovery and Load Balancing**: Exposes containers using DNS names or their own IP addresses and balances the load across them.\n\n5. **Automated Rollouts and Rollbacks**: Automatically manages updates to applications or configurations and can rollback changes if necessary.\n\n6. **Secret and Configuration Management**: Enables you to deploy and update secrets and application configuration without rebuilding your container images and without exposing secrets in your stack configuration and environment variables.\n\n7. **Storage Orchestration**: Allows you to automatically mount the storage system of your choice, whether from local storage, a public cloud provider, or a network storage system.\n\nBy providing these functionalities, Kubernetes enables developers to focus more on creating applications, while the platform handles the complexities of deployment and scaling. It has become a de facto standard for container orchestration, supporting a wide range of cloud platforms and minimizing dependencies on any specific infrastructure.",
           "refusal": null,
           "annotations": []
         },
         "logprobs": null,
         "finish_reason": "stop"
       }
     ],
     ...
   }
   ```
   
   {{% /tab %}}
   {{% tab tabName="Cost-based priority across providers" %}}
   
   Note the response is from the `claude-3-5-haiku-20241022` model. With the cost-based priority configuration, requests are load balanced across the cheaper models (OpenAI `gpt-3.5-turbo` and Anthropic `claude-3-5-haiku-latest`) in the first priority group.

   ```json {linenos=table,hl_lines=[2],linenostart=1,filename="model-response.json"}
   {
     "model": "claude-3-5-haiku-20241022",
     "usage": {
       "prompt_tokens": 11,
       "completion_tokens": 299,
       "total_tokens": 310
     },
     "choices": [
       {
         "message": {
           "content": "Kubernetes (often abbreviated as K8s) is an open-source container orchestration platform designed to automate the deployment, scaling, and management of containerized applications. Here's a comprehensive overview:\n\nKey Features:\n1. Container Orchestration\n- Manages containerized applications\n- Handles deployment and scaling\n- Ensures high availability\n\n2. Core Components\n- Cluster: Group of machines (nodes)\n- Master Node: Controls the cluster\n- Worker Nodes: Run containerized applications\n- Pods: Smallest deployable units\n- Containers: Isolated application environments\n\n3. Main Capabilities\n- Automatic scaling\n- Self-healing\n- Load balancing\n- Rolling updates\n- Service discovery\n- Configuration management\n\n4. Key Concepts\n- Deployments: Define desired application state\n- Services: Network communication between components\n- Namespaces: Logical separation of resources\n- ConfigMaps: Configuration management\n- Secrets: Sensitive data management\n\n5. Benefits\n- Portability across different environments\n- Efficient resource utilization\n- Improved scalability\n- Enhanced reliability\n- Simplified management of complex applications\n\n6. Popular Use Cases\n- Microservices architecture\n- Cloud-native applications\n- Continuous deployment\n- Distributed systems\n\nKubernetes has become the standard for container orchestration in modern cloud-native application development.",
           "role": "assistant"
         },
         "index": 0,
         "finish_reason": "stop"
       }
     ],
     "id": "msg_016PLweC4jgJnpwH7V1tZaqj",
     "created": 1762790436,
     "object": "chat.completion"
   }
   ```
   
   {{% /tab %}}
   {{< /tabs >}}

## Cleanup

{{< reuse "docs/snippets/cleanup.md" >}}

   ```shell
   kubectl delete backend,httproute -n {{< reuse "docs/snippets/namespace.md" >}} -l app=model-failover
   ```

## Next

Explore other AI Gateway features.

* Pass in [functions](../functions/) to an LLM to request as a step towards agentic AI.
* Set up [prompt guards](../prompt-guards/) to block unwanted requests and mask sensitive data.
* [Enrich your prompts](../prompt-enrichment/) with system prompts to improve LLM outputs.
