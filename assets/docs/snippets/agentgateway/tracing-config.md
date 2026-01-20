{{< tabs tabTotal="4" items="Jaeger,Langfuse,Phoenix (Arize),OpenLLMetry" >}}
{{% tab tabName="Jaeger" %}}
```yaml
kubectl apply -f- <<EOF
apiVersion: {{< reuse "docs/snippets/gatewayparam-apiversion.md" >}}
kind: {{< reuse "docs/snippets/gatewayparameters.md" >}}
metadata:
  name: jaeger-tracing-config
  namespace: {{< reuse "docs/snippets/namespace.md" >}}
spec:
  rawConfig:
    config: 
      tracing:
        otlpEndpoint: http://jaeger-collector.jaeger.svc.cluster.local:4317
        otlpProtocol: grpc
        randomSampling: true
        fields:
          add:
            gen_ai.operation.name: '"chat"'
            gen_ai.system: "llm.provider"
            gen_ai.request.model: "llm.requestModel"
            gen_ai.response.model: "llm.responseModel"
            gen_ai.usage.completion_tokens: "llm.outputTokens"
            gen_ai.usage.prompt_tokens: "llm.inputTokens"
EOF
```
{{% /tab %}}
{{% tab tabName="Langfuse" %}}
```yaml
kubectl apply -f- <<EOF
apiVersion: {{< reuse "docs/snippets/gatewayparam-apiversion.md" >}}
kind: {{< reuse "docs/snippets/gatewayparameters.md" >}}
metadata:
  name: langfuse-tracing-config
  namespace: {{< reuse "docs/snippets/namespace.md" >}}
spec:
  rawConfig:
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
            gen_ai.usage.completion_tokens: "llm.outputTokens"
            gen_ai.usage.prompt_tokens: "llm.inputTokens"
            gen_ai.request: "flatten(llm.params)"
EOF
```
{{% /tab %}}
{{% tab tabName="Phoenix (Arize)" %}}
```yaml
kubectl apply -f- <<EOF
apiVersion: {{< reuse "docs/snippets/gatewayparam-apiversion.md" >}}
kind: {{< reuse "docs/snippets/gatewayparameters.md" >}}
metadata:
  name: phoenix-tracing-config
  namespace: {{< reuse "docs/snippets/namespace.md" >}}
spec:
  rawConfig:
    config: 
      tracing:
        otlpEndpoint: http://localhost:4317
        randomSampling: true
        fields:
          add:
            span.name: '"openai.chat"'
            openinference.span.kind: '"LLM"'
            llm.system: "llm.provider"
            llm.input_messages: 'flattenRecursive(llm.prompt.map(c, {"message": c}))'
            llm.output_messages: 'flattenRecursive(llm.completion.map(c, {"role":"assistant", "content": c}))'
            llm.token_count.completion: "llm.outputTokens"
            llm.token_count.prompt: "llm.inputTokens"
            llm.token_count.total: "llm.totalTokens"
EOF
```
{{% /tab %}}
{{% tab tabName="OpenLLMetry" %}}
```yaml
kubectl apply -f- <<EOF
apiVersion: {{< reuse "docs/snippets/gatewayparam-apiversion.md" >}}
kind: {{< reuse "docs/snippets/gatewayparameters.md" >}}
metadata:
  name: openllmetry-tracing-config
  namespace: {{< reuse "docs/snippets/namespace.md" >}}
spec:
  rawConfig:
    config: 
      tracing:
        otlpEndpoint: http://localhost:4317
        randomSampling: true
        fields:
          add:
            span.name: '"openai.chat"'
            gen_ai.operation.name: '"chat"'
            gen_ai.system: "llm.provider"
            gen_ai.prompt: "flattenRecursive(llm.prompt)"
            gen_ai.completion: 'flattenRecursive(llm.completion.map(c, {"role":"assistant", "content": c}))'
            gen_ai.usage.completion_tokens: "llm.outputTokens"
            gen_ai.usage.prompt_tokens: "llm.inputTokens"
            llm.usage.total_tokens: 'llm.totalTokens'
            llm.is_streaming: "llm.streaming"
EOF
```
{{% /tab %}}
{{< /tabs >}}