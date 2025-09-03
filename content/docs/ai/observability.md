---
title: AI observability
weight: 90
---

Observability helps you understand how your system is performing, identify issues, and troubleshoot problems. AI Gateway provides a rich set of observability features that help you monitor and analyze the performance of your AI Gateway and the LLM providers that it interacts with. 

{{< callout >}}
{{< reuse "docs/snippets/proxy-kgateway.md" >}}
{{< /callout >}}

## Before you begin

1. [Set up AI Gateway](../setup/).

2. [Authenticate to the LLM](../auth/).

3. Get the external address of the gateway and save it in an environment variable.
   
   {{< tabs tabTotal="2" items="Cloud Provider LoadBalancer,Port-forward for local testing" >}}
   {{% tab tabName="Cloud Provider LoadBalancer" %}}
   ```sh
   export INGRESS_GW_ADDRESS=$(kubectl get svc -n {{< reuse "docs/snippets/namespace.md" >}} ai-gateway -o jsonpath="{.status.loadBalancer.ingress[0]['hostname','ip']}")
   echo $INGRESS_GW_ADDRESS  
   ```
   {{% /tab %}}
   {{% tab tabName="Port-forward for local testing" %}}
   ```sh
   kubectl port-forward deployment/ai-gateway -n {{< reuse "docs/snippets/namespace.md" >}} 8080:8080
   ```
   {{% /tab %}}
   {{< /tabs >}}

## Metrics

Metrics are helpful for understanding the overall health and performance of your system. AI Gateway provides a rich set of metrics for you to monitor and analyze the performance of your AI Gateway and the LLM providers that it interacts with.

### Dynamic metadata

Dynamic metadata is a powerful feature of Envoy that allows you to attach arbitrary key-value pairs to requests and responses as they flow through the Envoy proxy. AI Gateway uses dynamic metadata to expose key metrics related to LLM provider usage. These metrics can be used to monitor and analyze the performance of your AI Gateway and the LLM providers that it interacts with.

| Dynamic Metadata Field | Description |
|-----------------------|-------------|
| `ai.kgateway.io:total_tokens` | The total number of tokens used in the request |
| `ai.kgateway.io:prompt_tokens` | The number of tokens used in the prompt |
| `ai.kgateway.io:completion_tokens` | The number of tokens used in the completion |
| `envoy.ratelimit:hits_addend` | The number of tokens that were calculated to be rate limited |
| `ai.kgateway.io:model` | The model which was specified by the user in the request |
| `ai.kgateway.io:provider_model` | The model which the LLM provider used and returned in the response |
| `ai.kgateway.io:provider` | The LLM provider being used, such as `OpenAI`, `Anthropic`, etc. |
| `ai.kgateway.io:streaming` | A boolean indicating whether the request was streamed |

### Default metrics

Take a look at the default metrics that the system outputs.

1. In another tab in your terminal, port-forward the `ai-gateway` container of the gateway proxy.
   ```sh
   kubectl port-forward -n {{< reuse "docs/snippets/namespace.md" >}} deploy/ai-gateway 9092
   ```

2. In the previous tab, run the following command to view the metrics.
   ```sh
   curl localhost:9092/metrics
   ```

3. In the output, search for the `ai_completion_tokens_total` and `ai_prompt_tokens_total` metrics. These metrics total the number of tokens used in the prompt and completion for the `openai` model `gpt-3.5-turbo`. 
   ```
   # HELP ai_completion_tokens_total Completion tokens
   # TYPE ai_completion_tokens_total counter
   ai_completion_tokens_total{llm="openai",model="gpt-3.5-turbo"} 539.0
   ...
   # HELP ai_prompt_tokens_total Prompt tokens
   # TYPE ai_prompt_tokens_total counter
   ai_prompt_tokens_total{llm="openai",model="gpt-3.5-turbo"} 204.0
   ```

4. Stop port-forwarding the `ai-gateway` container.

### Integrate with the OTel stack {#otel-integration}

Review the Observability guides to set up an OpenTelemetry stack to collect logs, metrics, and traces.

{{< cards >}}
  {{< card link="../../observability/" title="Observability guides" >}}
{{< /cards >}}

## Next

If you haven't already, set up other features and start collecting metrics on your AI Gateway usage.

{{< cards >}}
  {{< card link="../failover" title="Model failover" >}}
  {{< card link="../functions" title="Function calling" >}}
  {{< card link="../prompt-enrichment" title="Prompt enrichment" >}}
  {{< card link="../prompt-guards" title="Prompt guards" >}}
{{< /cards >}}
