---
title: View metrics and logs
weight: 80
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


## View traces

Use a custom ConfigMap to configure your {{< reuse "docs/snippets/agentgateway.md" >}} proxy for tracing. 

## About tracing

The {{< reuse "docs/snippets/agentgateway.md" >}} proxy integrates with [Jaeger](https://www.jaegertracing.io/) as the tracing platform. Jaeger is an open source tool that helps you follow the path of a request as it is forwarded between agents. The chain of events and interactions are captured by an OpenTelemetry pipeline that is configured to send traces to the Jaeger agent. You can then visualize the traces by using the Jaeger UI.

## Before you begin

{{< reuse "docs/snippets/agentgateway-prereq.md" >}}

## Set up Jaeger

Use [`docker compose`](https://docs.docker.com/compose/install/linux/) to spin up a Jaeger instance with the following components:
* An OpenTelemetry collector that receives traces from the agentgateway. The collector is exposed on http://localhost:4317.
* A Jaeger agent that receives the collected traces. The agent is exposed on http://localhost:14268.
* A Jaeger UI that is exposed on http://localhost:16686.
```yaml
docker compose -f - up -d <<EOF
  services:
    jaeger:
      container_name: jaeger
      restart: unless-stopped
      image: jaegertracing/all-in-one:latest
      ports:
      - "127.0.0.1:16686:16686"
      - "127.0.0.1:14268:14268"
      - "127.0.0.1:4317:4317"
      environment:
      - COLLECTOR_OTLP_ENABLED=true
EOF
```

## Configure agentgateway

1. Create a ConfigMap with your agentgateway tracing configuration. 
   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: v1
   kind: ConfigMap
   metadata:
     name: agent-gateway-config
     namespace: {{< reuse "docs/snippets/namespace.md" >}}
   data:
     config.yaml: |-
       config:
         tracing:
           otlpEndpoint: http://localhost:4317
           otlpProtocol: grpc
           randomSampling: true
           fields:
             add:
               gen_ai.operation.name: '"chat"'
               gen_ai.system: "llm.provider"
               gen_ai.request.model: "llm.request_model"
               gen_ai.response.model: "llm.response_model"
               gen_ai.usage.completion_tokens: "llm.output_tokens"
               gen_ai.usage.prompt_tokens: "llm.input_tokens"
   EOF
   ```

2. Create a GatewayParameters resource that references the ConfigMap that you created. 
   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.kgateway.dev/v1alpha1
   kind: GatewayParameters
   metadata:
     name: tracing
     namespace: {{< reuse "docs/snippets/namespace.md" >}}
   spec:
     kube:
       agentgateway:
         enabled: true
         customConfigMapName: agent-gateway-config
   EOF
   ```

3. Create a Gateway  
   ```yaml
   kubectl apply -f- <<EOF
   kind: Gateway
   apiVersion: gateway.networking.k8s.io/v1
   metadata:
     name: agentgateway-tracing
     namespace: {{< reuse "docs/snippets/namespace.md" >}}
     labels:
       app: agentgateway
   spec:
     gatewayClassName: {{< reuse "docs/snippets/agw-gatewayclass.md" >}}
     infrastructure:
       parametersRef:
         name: tracing
         group: gateway.kgateway.dev
         kind: GatewayParameters  
     listeners:
     - protocol: HTTP
       port: 8080
       name: http
       allowedRoutes:
         namespaces:
           from: All
   EOF
   ```

4. Verify that your agentgateway proxy is up and running. 
   ```sh
   kubectl get pods -n {{< reuse "docs/snippets/namespace.md" >}}
   ```
   
   Example output: 
   ```console
   NAMESPACE            NAME                                         READY   STATUS    RESTARTS   AGE
   kgateway-system      agentgateway-tracing-8b5dc4874-bl79q         1/1     Running   0          12s
   ```

## Set up an MCP server

{{% reuse "docs/snippets/static-mcp.md" %}}

3. Create an HTTPRoute. 
   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.networking.k8s.io/v1
   kind: HTTPRoute
   metadata:
     name: mcp
     namespace: default
   spec:
     parentRefs:
     - name: agentgateway-tracing
       namespace: {{< reuse "docs/snippets/namespace.md" >}}
     rules:
       - backendRefs:
         - name: mcp-backend
           group: gateway.kgateway.dev
           kind: Backend   
   EOF
   ```
   
## Verify tracing 

1. Get the agentgateway address.
   
   {{< tabs items="Cloud Provider LoadBalancer,Port-forward for local testing" tabTotal="2" >}}
   {{% tab tabName="Cloud Provider LoadBalancer" %}}
   ```sh
   export INGRESS_GW_ADDRESS=$(kubectl get gateway -n {{< reuse "docs/snippets/namespace.md" >}} agentgateway-tracing -o=jsonpath="{.status.loadBalancer.ingress[0]['hostname','ip']}")
   echo $INGRESS_GW_ADDRESS
   ```
   {{% /tab %}}
   {{% tab tabName="Port-forward for local testing"%}}
   ```sh
   kubectl port-forward deployment/agentgateway-tracing -n {{< reuse "docs/snippets/namespace.md" >}}  8080:8080
   ```
   {{% /tab %}}
   {{< /tabs >}}

2. From the terminal, run the MCP Inspector command. Then, the MCP Inspector opens in your browser. If the MCP inspector tool does not open automatically, run `mcp-inspector`. 
   ```sh
   npx modelcontextprotocol/inspector#{{% reuse "docs/versions/mcp-inspector.md" %}}
   ```
   
3. From the MCP Inspector menu, connect to your agentgateway address as follows:
   * **Transport Type**: Select `Streamable HTTP`.
   * **URL**: Enter the agentgateway address, port, and the `/mcp` path. If your agentgateway proxy is exposed with a LoadBalancer server, use `http://<lb-address>:8080/mcp`. In local test setups where you port-forwarded the agentgateway proxy on your local machine, use `http://localhost:8080/mcp`.
   * Click **Connect**.
   
4. From the menu bar, click the **Tools** tab. Then from the **Tools** pane, click **List Tools** and select the `fetch` tool. 
5. From the **fetch** pane, in the **url** field, enter a website URL, such as `https://lipsum.com/`, and click **Run Tool**.
6. Verify that you get back the fetched URL content.
7. Open the [Jaeger UI](http://localhost:16686/search). 



## Other tracing configurations

Review common tracing providers configurations that you can use with agentgateway. s


{{< tabs tabTotal="4" items="Jaeger,Langfuse,Phoenix (Arize),OpenLLMetry" >}}
{{% tab tabName="Jaeger" %}}
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: jaeger-tracing-config
data:
  config.yaml: |-
    config:
      tracing:
        otlpEndpoint: http://jaeger-collector.jaeger.svc.cluster.local:4317
        otlpProtocol: grpc
        randomSampling: true
        fields:
          add:
            gen_ai.operation.name: '"chat"'
            gen_ai.system: "llm.provider"
            gen_ai.request.model: "llm.request_model"
            gen_ai.response.model: "llm.response_model"
            gen_ai.usage.completion_tokens: "llm.output_tokens"
            gen_ai.usage.prompt_tokens: "llm.input_tokens"
```
{{% /tab %}}
{{% tab tabName="Langfuse" %}}
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: langfuse-tracing-config
data:
  config.yaml: |-
    config:
      tracing:
        otlpEndpoint: https://us.cloud.langfuse.com/api/public/otel
        otlpProtocol: http
        headers:
          Authorization: "Basic <base64-encoded-credentials>"
        randomSampling: true
        fields:
          add:
            gen_ai.operation.name: '"chat"'
            gen_ai.system: "llm.provider"
            gen_ai.prompt: "llm.prompt"
            gen_ai.completion: 'llm.completion.map(c, {"role":"assistant", "content": c})'
            gen_ai.usage.completion_tokens: "llm.output_tokens"
            gen_ai.usage.prompt_tokens: "llm.input_tokens"
            gen_ai.request.model: "llm.request_model"
            gen_ai.response.model: "llm.response_model"
            gen_ai.request: "flatten(llm.params)"
```
{{% /tab %}}
{{% tab tabName="Phoenix (Arize)" %}}
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: phoenix-tracing-config
data:
  config.yaml: |-
    config:
      tracing:
        otlpEndpoint: http://localhost:4317
        randomSampling: true
        fields:
          add:
            span.name: '"openai.chat"'
            openinference.span.kind: '"LLM"'
            llm.system: "llm.provider"
            llm.input_messages: 'flatten_recursive(llm.prompt.map(c, {"message": c}))'
            llm.output_messages: 'flatten_recursive(llm.completion.map(c, {"role":"assistant", "content": c}))'
            llm.token_count.completion: "llm.output_tokens"
            llm.token_count.prompt: "llm.input_tokens"
            llm.token_count.total: "llm.total_tokens"
```
{{% /tab %}}
{{% tab tabName="OpenLLMetry" %}}
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: openllmetry-tracing-config
data:
  config.yaml: |-
    config:
      tracing:
        otlpEndpoint: http://localhost:4317
        randomSampling: true
        fields:
          add:
            span.name: '"openai.chat"'
            gen_ai.operation.name: '"chat"'
            gen_ai.system: "llm.provider"
            gen_ai.prompt: "flatten_recursive(llm.prompt)"
            gen_ai.completion: 'flatten_recursive(llm.completion.map(c, {"role":"assistant", "content": c}))'
            gen_ai.usage.completion_tokens: "llm.output_tokens"
            gen_ai.usage.prompt_tokens: "llm.input_tokens"
            gen_ai.request.model: "llm.request_model"
            gen_ai.response.model: "llm.response_model"
            gen_ai.request: "flatten(llm.params)"
            llm.is_streaming: "llm.streaming"
```
{{% /tab %}}
{{< /tabs >}}