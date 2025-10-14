---
title: Model failover
weight: 30
---

{{< reuse "docs/snippets/ai-deprecation-note.md" >}}

Prioritize the failover of requests across different models from an LLM provider.

{{< callout >}}
{{< reuse "docs/snippets/proxy-kgateway.md" >}}
{{< /callout >}}

## About failover {#about}

Failover is a way to keep services running smoothly by automatically switching to a backup system when the main one fails or becomes unavailable.

For AI gateways, you can set up failover for the models of the LLM providers that you want to prioritize. If the main model from one provider goes down, slows, or has any issue, the system quickly switches to a backup model from that same provider. This keeps the service running without interruptions.

This approach increases the resiliency of your network environment by ensuring that apps that call LLMs can keep working without problems, even if one model has issues.

## Before you begin

1. [Set up AI Gateway](../setup/).
2. [Authenticate to the LLM](../auth/).
3. {{< reuse "docs/snippets/ai-gateway-address.md" >}}

## Fail over to other models {#model-failover}

In this example, you create a Backend with multiple pools for the same LLM provider. Each pool represents a specific model from the LLM provider that fails over in the following order of priority. For more information, see the [Priority Groups API reference docs](/docs/reference/api/#prioritygroups).

1. Create or update the Backend for your LLM providers. The priority order of the models is as follows:
   
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
     namespace: {{< reuse "docs/snippets/namespace.md" >}}
   spec:
     type: AI
     ai:
       priorityGroups:
       - providers:
         - openai:
             model: "gpt-4o"
           authToken:
             kind: SecretRef
             secretRef:
               name: openai-secret
         - openai:
             model: "gpt-4.0-turbo"
           authToken:
             kind: SecretRef
             secretRef:
               name: openai-secret
         - openai:
             model: "gpt-3.5-turbo"
           authToken:
             kind: SecretRef
             secretRef:
               name: openai-secret
   EOF
   ```

2. Create an HTTPRoute resource that routes incoming traffic on the `/model` path to the Backend backend that you created in the previous step. In this example, the URLRewrite filter rewrites the path from `/model` to the path of the API in the LLM provider that you want to use, such as `/v1/chat/` completions for OpenAI.

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

3. Send a request to observe the failover. In your request, do not specify a model. Instead, the Backend will automatically use the model from the first pool in the priority order.

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
   
   Example output: Note the response is from the `gpt-4o` model, which is the first model in the priority order from the Backend.

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
