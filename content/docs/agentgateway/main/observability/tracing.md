---
title: Tracing
weight: 90
---

Integrate your agentgateway proxy with an OpenTelemetry (OTel) collector and configure custom metadata for your traces with an {{< reuse "docs/snippets/trafficpolicy.md" >}}.

{{< reuse "docs/snippets/agentgateway/prereq.md" >}}

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

## Set up tracing

1. Create an {{< reuse "docs/snippets/trafficpolicy.md" >}} resource with your tracing configuration. 
   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: {{< reuse "docs/snippets/trafficpolicy-apiversion.md" >}}
   kind: {{< reuse "docs/snippets/trafficpolicy.md" >}}
   metadata:
     name: tracing
     namespace: {{< reuse "docs/snippets/namespace.md" >}}
   spec:
     targetRefs:
       - kind: Gateway
         name: agentgateway-proxy
         group: gateway.networking.k8s.io
     frontend:
       tracing:
         backendRef:
           name: opentelemetry-collector-traces
           namespace: telemetry
           port: 4317
         protocol: GRPC
         clientSampling: "true"
         randomSampling: "true"
         resources:
           - name: deployment.environment.name
             expression: '"production"'
           - name: service.version
             expression: '"test"'
         attributes:
           add:
             - expression: 'request.headers["x-header-tag"]'
               name: request
             - expression: 'request.host'
               name: host
   EOF
   ```

## Verify traces

1. Send a request to the httpbin app with the `x-header-tag` header. 
   {{< tabs tabTotal="2" items="Cloud Provider LoadBalancer,Port-forward for local testing" >}}
   {{% tab tabName="Cloud Provider LoadBalancer" %}}
   ```sh
   curl -vi -X POST http://$INGRESS_GW_ADDRESS:8080/post \
    -H "host: www.example.com:8080" \
    -H "x-header-tag: custom-tracing"
   ```
   {{% /tab %}}
   {{% tab tabName="Port-forward for local testing" %}}
   ```sh
   curl -vi -X POST localhost:8080/post \
    -H "host: www.example.com" \
    -H "x-header-tag: custom-tracing"
   ```
   {{% /tab %}}
   {{< /tabs >}}

2. Get the trace ID from your request from the agentgateway proxy logs. 
   ```sh
   kubectl logs deploy/agentgateway-proxy -n {{< reuse "docs/snippets/namespace.md" >}}
   ```

3. Get the logs of the collector and search for the trace ID. Verify that you see the additional tracing attributes that you configured initially.
   ```sh
   kubectl logs deploy/opentelemetry-collector-traces -n telemetry \
   | grep -A 30 "Trace ID\s\+: <trace_id>"
   ```

   Example output: 
   ```console {hl_lines=[27,28]}
   Trace ID       : 2864d2f682a85ba0c44cb5122d2d11e5
    Parent ID      : 
    ID             : 947515b6316f7931
    Name           : POST /*
    Kind           : Server
    Start time     : 2026-01-20 16:28:30.717325796 +0000 UTC
    End time       : 2026-01-20 16:28:30.717960087 +0000 UTC
    Status code    : Unset
    Status message : 
   Attributes:
     -> gateway: Str(agentgateway-system/agentgateway-proxy)
     -> listener: Str(http)
     -> route: Str(httpbin/httpbin)
     -> endpoint: Str(10.244.0.31:8080)
     -> src.addr: Str(127.0.0.1:50314)
     -> http.method: Str(POST)
     -> http.host: Str(www.example.com)
     -> http.path: Str(/post)
     -> http.version: Str(HTTP/1.1)
     -> http.status: Int(200)
     -> trace.id: Str(2864d2f682a85ba0c44cb5122d2d11e5)
     -> span.id: Str(947515b6316f7931)
     -> protocol: Str(http)
     -> duration: Str(0ms)
     -> url.scheme: Str(http)
     -> network.protocol.version: Str(1.1)
     -> request: Str(custom-tracing)
     -> host: Str(www.example.com)

   ```
