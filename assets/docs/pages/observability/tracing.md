Configure distributed tracing for your gateway to gain visibility into request flows across services.

## About tracing

When tracing is enabled, the gateway proxy generates spans for incoming requests and exports them to a configured OpenTelemetry (OTel) collector. You can use these traces to understand request latency, identify bottlenecks, and debug issues across services.

Tracing is configured at two levels:

* **Listener level** (required): Configure the OTel provider, sampling rates, and span attributes using a `ListenerPolicy` that targets your Gateway.
* **Route level** (optional): Override sampling rates, add route-specific span attributes, or disable tracing for individual routes by using the {{< reuse "docs/snippets/trafficpolicy.md" >}} resource that targets an HTTPRoute or GRPCRoute.

### Auto-populated resource attributes

When tracing is enabled, the following [OTel semantic convention](https://opentelemetry.io/docs/specs/semconv/resource/) resource attributes are automatically added to all spans so that you can identify the origin of each trace without additional configuration.

| Attribute | Value |
|---|---|
| `service.name` | `<gateway-name>.<gateway-namespace>` |
| `service.namespace` | Gateway namespace |
| `service.instance.id` | Gateway UID |
| `service.version` | kgateway version |
| `k8s.namespace.name` | Proxy pod namespace |
| `k8s.container.name` | Envoy container name |
| `k8s.pod.name` | Proxy pod name |
| `k8s.pod.uid` | Proxy pod UID |
| `k8s.node.name` | Node name |
| `k8s.deployment.name` | Proxy deployment name |

User-configured resource attributes always take precedence over these defaults.

### Limitations

* A listener-level `ListenerPolicy` with an OTel provider must be configured for any tracing to occur. Route-level `{{< reuse "docs/snippets/trafficpolicy.md" >}}` tracing settings have no effect without it.
* Route-level tracing via `{{< reuse "docs/snippets/trafficpolicy.md" >}}` supports `HTTPRoute` and `GRPCRoute` targets only.
* When multiple `TrafficPolicies` with tracing are attached to the same route, the default merge strategy applies.

## Before you begin

{{< reuse "docs/snippets/prereq.md" >}}

## Deploy an OTel collector {#otel-collector}

Deploy a minimal OpenTelemetry collector to receive and log trace data. Deploying it in the same namespace as the `ListenerPolicy` (`{{< reuse "docs/snippets/namespace.md" >}}`) avoids the need for a `ReferenceGrant`. For a production-grade setup with Grafana Tempo and persistent storage, see the [OpenTelemetry stack guide]({{< link-hextra path="/observability/otel-stack/" >}}).

```yaml
kubectl apply -f- <<EOF
apiVersion: v1
kind: ConfigMap
metadata:
  name: otel-collector-conf
  namespace: {{< reuse "docs/snippets/namespace.md" >}}
data:
  otel-collector-config: |
    receivers:
      otlp:
        protocols:
          grpc:
            endpoint: 0.0.0.0:4317
    exporters:
      debug:
        verbosity: detailed
    service:
      pipelines:
        traces:
          receivers: [otlp]
          exporters: [debug]
---
apiVersion: v1
kind: Pod
metadata:
  name: otel-collector
  namespace: {{< reuse "docs/snippets/namespace.md" >}}
  labels:
    app.kubernetes.io/name: otel-collector
spec:
  containers:
  - name: otel-collector
    image: otel/opentelemetry-collector-contrib:0.143.0
    command:
    - /otelcol-contrib
    - --config
    - /conf/otel-collector-config.yaml
    ports:
    - containerPort: 4317
    volumeMounts:
    - name: otel-collector-config-vol
      mountPath: /conf
  volumes:
  - name: otel-collector-config-vol
    configMap:
      name: otel-collector-conf
      items:
      - key: otel-collector-config
        path: otel-collector-config.yaml
---
apiVersion: v1
kind: Service
metadata:
  name: otel-collector
  namespace: {{< reuse "docs/snippets/namespace.md" >}}
spec:
  ports:
  - name: otlp-grpc
    port: 4317
    protocol: TCP
    targetPort: 4317
    appProtocol: grpc
  selector:
    app.kubernetes.io/name: otel-collector
EOF
```

Verify that the collector pod is running.

```sh
kubectl get pod otel-collector -n {{< reuse "docs/snippets/namespace.md" >}}
```

Example output:
```
NAME             READY   STATUS    RESTARTS   AGE
otel-collector   1/1     Running   0          30s
```

## Enable tracing {#enable-tracing}

1. Create a `ListenerPolicy` resource to configure tracing at the listener level. The following example enables tracing on the `http` gateway and exports spans to the OTel collector over gRPC.
   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.kgateway.dev/v1alpha1
   kind: ListenerPolicy
   metadata:
     name: tracing
     namespace: {{< reuse "docs/snippets/namespace.md" >}}
   spec:
     targetRefs:
     - group: gateway.networking.k8s.io
       kind: Gateway
       name: http
     default:
       httpSettings:
         tracing:
           clientSampling: 100
           randomSampling: 100
           overallSampling: 100
           provider:
             openTelemetry:
               grpcService:
                 backendRef:
                   name: otel-collector
                   namespace: {{< reuse "docs/snippets/namespace.md" >}}
                   port: 4317
   EOF
   ```

   | Field | Description |
   |---|---|
   | `clientSampling` | Percentage of requests that are force-traced when the `x-client-trace-id` header is present. Range: 0–100. |
   | `randomSampling` | Percentage of requests that are randomly selected for tracing. Range: 0–100. |
   | `overallSampling` | Upper limit on the total percentage of requests traced after all other sampling checks. Range: 0–100. |
   | `provider.openTelemetry.grpcService.backendRef` | The Kubernetes Service that receives spans over gRPC (OTLP). |

2. Send a few requests to the httpbin app to generate trace data.
   {{< tabs items="Cloud Provider LoadBalancer,Port-forward for local testing" tabTotal="2" >}}
   {{% tab tabName="Cloud Provider LoadBalancer" %}}
   ```sh
   curl -si http://$INGRESS_GW_ADDRESS:8080/get \
   -H "host: www.example.com:8080"
   ```
   {{% /tab %}}
   {{% tab tabName="Port-forward for local testing" %}}
   ```sh
   curl -si localhost:8080/get \
   -H "host: www.example.com"
   ```
   {{% /tab %}}
   {{< /tabs >}}

3. Check the OTel collector logs to verify that spans are being received.
   ```sh
   kubectl logs otel-collector -n {{< reuse "docs/snippets/namespace.md" >}}
   ```

   Example output:
   ```
   ScopeSpans #0
   InstrumentationScope envoy
   Span #0
       Trace ID  : ...
       Name      : ingress
       Kind      : Server
   ResourceAttributes:
        -> service.name: Str(http.kgateway-system)
        -> service.namespace: Str(kgateway-system)
        -> k8s.pod.name: Str(http-...)
        -> k8s.namespace.name: Str(kgateway-system)
   ```

## Cleanup

{{< reuse "docs/snippets/cleanup.md" >}}

```sh
kubectl delete listenerpolicy tracing -n {{< reuse "docs/snippets/namespace.md" >}}
kubectl delete pod otel-collector -n {{< reuse "docs/snippets/namespace.md" >}}
kubectl delete service otel-collector -n {{< reuse "docs/snippets/namespace.md" >}}
kubectl delete configmap otel-collector-conf -n {{< reuse "docs/snippets/namespace.md" >}}
```

## Other configurations

Review other common tracing configurations. These examples assume that the listener-level `ListenerPolicy` from [Enable tracing](#enable-tracing) and the OTel collector from [Deploy an OTel collector](#otel-collector) are already in place.

### Custom span attributes {#custom-attributes}

Add custom attributes to all spans that are generated by the gateway listener. Attributes can be set from a literal value or from a request header.

```yaml
kubectl apply -f- <<EOF
apiVersion: gateway.kgateway.dev/v1alpha1
kind: ListenerPolicy
metadata:
  name: tracing
  namespace: {{< reuse "docs/snippets/namespace.md" >}}
spec:
  targetRefs:
  - group: gateway.networking.k8s.io
    kind: Gateway
    name: http
  default:
    httpSettings:
      tracing:
        clientSampling: 100
        randomSampling: 100
        overallSampling: 100
        provider:
          openTelemetry:
            grpcService:
              backendRef:
                name: otel-collector
                namespace: {{< reuse "docs/snippets/namespace.md" >}}
                port: 4317
        attributes:
        - name: environment
          literal:
            value: production
        - name: request-id
          requestHeader:
            name: x-request-id
EOF
```

| Field | Description |
|---|---|
| `default.httpSettings.tracing.attributes[].name` | The name of the span attribute. |
| `default.httpSettings.tracing.attributes[].literal.value` | A static string value for the attribute. |
| `default.httpSettings.tracing.attributes[].requestHeader.name` | The name of the request header that you want to use for the attribute. |

### Per-route sampling and attributes {#per-route-tracing}

Use the {{< reuse "docs/snippets/trafficpolicy.md" >}} resource to override sampling rates or add route-specific span attributes for individual HTTPRoutes or GRPCRoutes. Route-level attributes are merged with listener-level attributes; route-level values take priority on name collision.

```yaml
kubectl apply -f- <<EOF
apiVersion: {{< reuse "docs/snippets/trafficpolicy-apiversion.md" >}}
kind: {{< reuse "docs/snippets/trafficpolicy.md" >}}
metadata:
  name: tracing-route
  namespace: httpbin
spec:
  targetRefs:
  - group: gateway.networking.k8s.io
    kind: HTTPRoute
    name: httpbin
  tracing:
    randomSampling: 50
    overallSampling: 50
    attributes:
    - name: route-tag
      literal:
        value: httpbin-route
    - name: x-custom-header
      requestHeader:
        name: x-custom-header
EOF
```

| Field | Description |
|---|---|
| `tracing.clientSampling` | Override the percentage of force-traced requests (via `x-client-trace-id` header) for this route. Range: 0–100. |
| `tracing.randomSampling` | Override the percentage of randomly sampled requests for this route. Range: 0–100. |
| `tracing.overallSampling` | Override the total sampling upper limit for this route. Range: 0–100. |
| `tracing.attributes` | Route-specific span attributes, merged with listener-level attributes. Maximum 16 entries. |

### Disable tracing per route {#disable-tracing}

When listener-level tracing is configured, use `disable: {}` on a route-level {{< reuse "docs/snippets/trafficpolicy.md" >}} to exempt specific routes from tracing. The `disable` field is mutually exclusive with all other `tracing` fields.

```yaml
kubectl apply -f- <<EOF
apiVersion: {{< reuse "docs/snippets/trafficpolicy-apiversion.md" >}}
kind: {{< reuse "docs/snippets/trafficpolicy.md" >}}
metadata:
  name: tracing-disable
  namespace: httpbin
spec:
  targetRefs:
  - group: gateway.networking.k8s.io
    kind: HTTPRoute
    name: httpbin
  tracing:
    disable: {}
EOF
```
