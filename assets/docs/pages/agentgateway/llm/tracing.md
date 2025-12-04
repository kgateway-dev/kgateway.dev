Use a custom ConfigMap to configure your {{< reuse "docs/snippets/agentgateway.md" >}} proxy for tracing. 

## Before you begin

{{< reuse "docs/snippets/agentgateway-prereq.md" >}}

## Set up an OpenTelemetry collector

Install an OpenTelemetry collector that the {{< reuse "docs/snippets/agentgateway.md" >}} proxy can send traces to. Depending on your environment, you can further configure your OpenTelemetry to export these traces to your preferred tracing platform, such as Jaeger. 

1. Install the OTel collector.
   ```sh
   helm upgrade --install opentelemetry-collector-traces opentelemetry-collector \
   --repo https://open-telemetry.github.io/opentelemetry-helm-charts \
   --version 0.127.2 \
   --set mode=deployment \
   --set image.repository="otel/opentelemetry-collector-contrib" \
   --set command.name="otelcol-contrib" \
   --namespace=telemetry \
   --create-namespace \
   -f -<<EOF
   config:
     receivers:
       otlp:
         protocols:
           grpc:
             endpoint: 0.0.0.0:4317
           http:
             endpoint: 0.0.0.0:4318
     exporters:
       otlp/tempo:
         endpoint: http://tempo.telemetry.svc.cluster.local:4317
         tls:
           insecure: true
       debug:
         verbosity: detailed
     service:
       pipelines:
         traces:
           receivers: [otlp]
           processors: [batch]
           exporters: [debug, otlp/tempo]
   EOF
   ```
   
2. Verify that the collector is up and running. 
   ```sh
   kubectl get pods -n telemetry
   ```
   
   Example output: 
   ```console
   NAME                                             READY   STATUS    RESTARTS   AGE
   opentelemetry-collector-traces-8f566f445-l82s6   1/1     Running   0          17m
   ```

## Configure your proxy

1. Create a ConfigMap with your agentgateway tracing configuration. The following example collects additional information about the request to the LLM and adds this information to the trace. The trace is then sent to the collector that you set up earlier. To learn more about the fields that you can configure, see the [agentgateway docs](https://agentgateway.dev/docs/reference/cel/#context-reference).

   {{< callout type="info" >}}
   For more tracing providers, see [Other tracing configurations](#other-tracing-configurations).
   {{< /callout>}}
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
           otlpEndpoint: http://opentelemetry-collector-traces.telemetry.svc.cluster.local:4317
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

2. Create a {{< reuse "docs/snippets/gatewayparameters.md" >}} resource that references the ConfigMap that you created. 
   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: {{< reuse "docs/snippets/gatewayparam-apiversion.md" >}}
   kind: {{< reuse "docs/snippets/gatewayparameters.md" >}}
   metadata:
     name: tracing
     namespace: {{< reuse "docs/snippets/namespace.md" >}}
   spec:
     kube:
       agentgateway:
         customConfigMapName: agent-gateway-config
   EOF
   ```

3. Create your {{< reuse "docs/snippets/agentgateway.md" >}} proxy. Make sure to reference the {{< reuse "docs/snippets/gatewayparameters.md" >}} resource that you created so that your proxy starts with the custom tracing configuration.
   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.networking.k8s.io/v1
   kind: Gateway
   metadata:
     name: agentgateway
     namespace: {{< reuse "docs/snippets/namespace.md" >}}
   spec:
     gatewayClassName: {{< reuse "docs/snippets/agw-gatewayclass.md" >}}
     infrastructure:
       parametersRef:
         name: tracing
         group: {{< reuse "docs/snippets/trafficpolicy-group.md" >}}  
         kind: {{< reuse "docs/snippets/gatewayparameters.md" >}}  
     listeners:
     - protocol: HTTP
       port: 80
       name: http
       allowedRoutes:
         namespaces:
           from: All
   EOF
   ```

4. Verify that your {{< reuse "docs/snippets/agentgateway.md" >}} proxy is up and running. 
   ```sh
   kubectl get pods -n {{< reuse "docs/snippets/namespace.md" >}}
   ```
   
   Example output: 
   ```console
   NAMESPACE            NAME                                 READY   STATUS    RESTARTS   AGE
   {{< reuse "docs/snippets/namespace.md" >}}      agentgateway-8b5dc4874-bl79q         1/1     Running   0          12s
   ```

5. Get the external address of the gateway and save it in an environment variable.
   {{< tabs tabTotal="2" items="Cloud Provider LoadBalancer,Port-forward for local testing" >}}
   {{% tab tabName="Cloud Provider LoadBalancer" %}}
   ```sh
   export INGRESS_GW_ADDRESS=$(kubectl get svc -n {{< reuse "docs/snippets/namespace.md" >}} agentgateway -o jsonpath="{.status.loadBalancer.ingress[0]['hostname','ip']}")
   echo $INGRESS_GW_ADDRESS  
   ```
   {{% /tab %}}
   {{% tab tabName="Port-forward for local testing" %}}
   ```sh
   kubectl port-forward deployment/agentgateway -n {{< reuse "docs/snippets/namespace.md" >}} 8080:80
   ```
   {{% /tab %}}
   {{< /tabs >}}
   
## Set up access to Gemini

Configure access to an LLM provider such as Gemini and send a sample request. You later use this request to verify your tracing configuration.

{{< reuse "docs/snippets/gemini-setup.md" >}}

## Verify tracing 

1. Get the logs of the agentgateway proxy. In the CLI output, find the `trace.id`.
   ```sh
   kubectl logs deploy/agentgateway -n {{< reuse "docs/snippets/namespace.md" >}}
   ```
   
   Example output:
   ```console{hl_lines=[5]}
   info	request gateway={{< reuse "docs/snippets/namespace.md" >}}/agentgateway listener=http 
   route={{< reuse "docs/snippets/namespace.md" >}}/google endpoint=generativelanguage.googleapis.com:443
   src.addr=127.0.0.1:49576 http.method=POST http.host=localhost 
   http.path=/gemini http.version=HTTP/1.1 http.status=200 
   trace.id=d65e4eeb983e2d964e71e8dc8c405f97 span.id=b836e1b1d51b3e74 
   llm.provider=gemini llm.request.model= llm.request.tokens=8 
   llm.response.model=gemini-1.5-flash-latest llm.response.tokens=313 duration=3165ms
   ```

2. Get the logs of the collector and search for the trace ID. Verify that you see the additional LLM that you configured initially.
   ```sh
   kubectl logs deploy/opentelemetry-collector-traces -n telemetry
   ```
   
   Example output: 
   ```console
   Span #0
    Trace ID       : d65e4eeb983e2d964e71e8dc8c405f97
    Parent ID      : 
    ID             : b836e1b1d51b3e74
    Name           : POST /gemini
    Kind           : Server
    Start time     : 2025-09-24 18:12:58.653868462 +0000 UTC
    End time       : 2025-09-24 18:13:01.821700755 +0000 UTC
    Status code    : Unset
    Status message : 
   Attributes:
     -> gateway: Str({{< reuse "docs/snippets/namespace.md" >}}/agentgateway)
     -> listener: Str(http)
     -> route: Str({{< reuse "docs/snippets/namespace.md" >}}/google)
     -> endpoint: Str(generativelanguage.googleapis.com:443)
     -> src.addr: Str(127.0.0.1:49576)
     -> http.method: Str(POST)
     -> http.host: Str(localhost)
     -> http.path: Str(/gemini)
     -> http.version: Str(HTTP/1.1)
     -> http.status: Int(200)
     -> trace.id: Str(d65e4eeb983e2d964e71e8dc8c405f97)
     -> span.id: Str(b836e1b1d51b3e74)
     -> llm.provider: Str(gemini)
     -> llm.request.model: Str()
     -> llm.request.tokens: Int(8)
     -> llm.response.model: Str(gemini-1.5-flash-latest)
     -> llm.response.tokens: Int(313)
     -> duration: Str(3165ms)
     -> url.scheme: Str(http)
     -> network.protocol.version: Str(1.1)
     -> gen_ai.operation.name: Str(chat)
     -> gen_ai.system: Str(gemini)
   ```



## Other tracing configurations

Review common tracing providers configurations that you can use with agentgateway.

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
            gen_ai.usage.completion_tokens: "llm.outputTokens"
            gen_ai.usage.prompt_tokens: "llm.inputTokens"
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
            llm.input_messages: 'flattenRecursive(llm.prompt.map(c, {"message": c}))'
            llm.output_messages: 'flattenRecursive(llm.completion.map(c, {"role":"assistant", "content": c}))'
            llm.token_count.completion: "llm.outputTokens"
            llm.token_count.prompt: "llm.inputTokens"
            llm.token_count.total: "llm.totalTokens"
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
            gen_ai.prompt: "flattenRecursive(llm.prompt)"
            gen_ai.completion: 'flattenRecursive(llm.completion.map(c, {"role":"assistant", "content": c}))'
            gen_ai.usage.completion_tokens: "llm.outputTokens"
            gen_ai.usage.prompt_tokens: "llm.inputTokens"
            llm.usage.total_tokens: 'llm.totalTokens'
            llm.is_streaming: "llm.streaming"
```
{{% /tab %}}
{{< /tabs >}}

## Cleanup

{{< reuse "docs/snippets/cleanup.md" >}}

```sh
kubectl delete gateway agentgateway -n {{< reuse "docs/snippets/namespace.md" >}}
kubectl delete {{< reuse "docs/snippets/gatewayparameters.md" >}}   tracing -n {{< reuse "docs/snippets/namespace.md" >}}
kubectl delete configmap agent-gateway-config -n {{< reuse "docs/snippets/namespace.md" >}}
helm uninstall opentelemetry-collector-traces -n telemetry
kubectl delete httproute google -n {{< reuse "docs/snippets/namespace.md" >}}
kubectl delete {{< reuse "docs/snippets/backend.md" >}} google -n {{< reuse "docs/snippets/namespace.md" >}}
kubectl delete secret google-secret -n {{< reuse "docs/snippets/namespace.md" >}}
```