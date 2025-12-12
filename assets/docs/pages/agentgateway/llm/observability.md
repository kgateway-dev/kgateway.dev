Review LLM-specific metrics and logs. 

## Before you begin

Complete an LLM guide, such as an [LLM provider-specific guide]({{< link-hextra path="/agentgateway/llm/providers/" >}}). This guide sends a request to the LLM and receives a response. You can use this request and response example to verify metrics and logs.  

## View LLM metrics

You can access the {{< reuse "docs/snippets/agentgateway.md" >}} metrics endpoint to view LLM-specific metrics, such as the number of tokens that you used during a request or response. 

1. Port-forward the agentgateway proxy on port 15020. 
   ```sh
   kubectl port-forward deployment/agentgateway-proxy -n {{< reuse "docs/snippets/namespace.md" >}} 15020  
   ```
2. Open the {{< reuse "docs/snippets/agentgateway.md" >}} [metrics endpoint](http://localhost:15020/metrics). 
3. Look for the `agentgateway_gen_ai_client_token_usage` metric. This metric is a [histogram](https://prometheus.io/docs/concepts/metric_types/#histogram) and includes important information about the request and the response from the LLM, such as:
   * `gen_ai_token_type`: Whether this metric is about a request (`input`) or response (`output`). 
   * `gen_ai_operation_name`: The name of the operation that was performed. 
   * `gen_ai_system`: The LLM provider that was used for the request/response. 
   * `gen_ai_request_model`: The model that was used for the request. 
   * `gen_ai_response_model`: The model that was used for the response. 
   

For more information, see the [Semantic conventions for generative AI metrics](https://opentelemetry.io/docs/specs/semconv/gen-ai/gen-ai-metrics/) in the OpenTelemetry docs.


## View logs

{{< reuse "docs/snippets/agentgateway-capital.md" >}} automatically logs information to stdout. When you run {{< reuse "docs/snippets/agentgateway.md" >}} on your local machine, you can view a log entry for each request that is sent to {{< reuse "docs/snippets/agentgateway.md" >}} in your CLI output. 

To view the logs: 
```sh
kubectl logs deployment/agentgateway-proxy -n {{< reuse "docs/snippets/namespace.md" >}}
```

Example for a successful request to the OpenAI LLM: 
```
2025-12-12T21:56:02.809082Z	info	request gateway=agentgateway-system/agentgateway-proxy listener=http
route=agentgateway-system/openai endpoint=api.openai.com:443 src.addr=127.0.0.1:60862 http.method=POST
http.host=localhost http.path=/openai http.version=HTTP/1.1 http.status=200 protocol=llm gen_ai.
operation.name=chat gen_ai.provider.name=openai gen_ai.request.model=gpt-3.5-turbo gen_ai.response.
model=gpt-3.5-turbo-0125 gen_ai.usage.input_tokens=68 gen_ai.usage.output_tokens=298 duration=2488ms 
```
