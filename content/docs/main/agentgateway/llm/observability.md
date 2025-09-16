---
title: Observe traffic
weight: 90
description:
---

Review LLM-specific metrics and logs. 

## Before you begin

Complete an LLM guide, such as an [LLM provider-specific guide]({{< link-hextra path="/agentgateway/llm/providers/" >}}). This guide sends a request to the LLM and receives a response. You can use this request and response example to verify metrics and logs.  

## View LLM metrics

You can access the {{< reuse "docs/snippets/agentgateway.md" >}} metrics endpoint to view LLM-specific metrics, such as the number of tokens that you used during a request or response. 

1. Port-forward the agentgateway proxy on port 15020. 
   ```sh
   kubectl port-forward deployment/agentgateway -n {{< reuse "docs/snippets/namespace.md" >}} 15020  
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
kubectl logs <agentgateway-pod> -n {{< reuse "docs/snippets/namespace.md" >}}
```

Example for a successful request to the OpenAI LLM: 
```
2025-09-12T18:23:54.661414Z	info	request gateway={{< reuse "docs/snippets/namespace.md" >}}/agentgateway listener=http 
route={{< reuse "docs/snippets/namespace.md" >}}/openai endpoint=api.openai.com:443 src.addr=10.0.9.76:38655 
http.method=POST http.host=a1cff4bd974a34d8b882b2fa01d357f0-119963959.us-east-2.elb.amazonaws.com
http.path=/openai http.version=HTTP/1.1 http.status=200 llm.provider=openai
llm.request.model= llm.request.tokens=39 llm.response.model=gpt-3.5-turbo-0125
llm.response.tokens=181 duration=3804ms
```
