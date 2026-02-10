---
title: OTel stack
weight: 10
---

{{< reuse "docs/snippets/otel-prereq.md" >}}

{{< reuse "docs/pages/observability/otel-stack.md" >}}

## Step 4: Configure telemetry policies {#policies}

Now that you have the telemetry stack set up, you can configure the telemetry policies to collect logging and tracing data for your gateway environment. The HTTPListenerPolicy lets you configure how to collect, process, and route logs and traces for your Gateway or ListenerSet resources. Note that metrics are collected automatically.

1. Create an HTTPListenerPolicy to collect and store logs in Loki. The policy applies to the `http` Gateway that serves traffic to the `httpbin` app that you set up before you began.

   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.kgateway.dev/v1alpha1
   kind: HTTPListenerPolicy
   metadata:
     name: logging-policy
     namespace: {{< reuse "docs/snippets/namespace.md" >}}
   spec:
     targetRefs:
     - group: gateway.networking.k8s.io
       kind: Gateway
       name: http
     accessLog:
     - openTelemetry:
         grpcService:
           backendRef:
             name: opentelemetry-collector-logs
             namespace: telemetry
             port: 4317
           logName: "http-gateway-access-logs"
         body: >-
           "%REQ(:METHOD)% %REQ(X-ENVOY-ORIGINAL-PATH?:PATH)% %RESPONSE_CODE% "%REQ(:AUTHORITY)%" "%UPSTREAM_CLUSTER%"'
   EOF
   ```

2. Create a Kubernetes ReferenceGrant so that the HTTPListenerPolicy can apply to the OTel logs collector service.

   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.networking.k8s.io/v1beta1
   kind: ReferenceGrant
   metadata:
     name: allow-otel-collector-logs-access
     namespace: telemetry
   spec:
     from:
     - group: gateway.kgateway.dev
       kind: HTTPListenerPolicy
       namespace: {{< reuse "docs/snippets/namespace.md" >}}
     to:
     - group: ""
       kind: Service
       name: opentelemetry-collector-logs
   EOF
   ```

3. Create another HTTPListenerPolicy to collect and store traces in Tempo.

   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.kgateway.dev/v1alpha1
   kind: HTTPListenerPolicy
   metadata:
     name: tracing-policy
     namespace: {{< reuse "docs/snippets/namespace.md" >}}
   spec:
     targetRefs:
     - group: gateway.networking.k8s.io
       kind: Gateway
       name: http
     tracing:
       provider:
         openTelemetry:
           serviceName: http
           grpcService:
             backendRef:
               name: opentelemetry-collector-traces
               namespace: telemetry
               port: 4317
       spawnUpstreamSpan: true
   EOF
   ```

4. Create a Kubernetes ReferenceGrant so that the HTTPListenerPolicy can apply to the OTel traces collector service.

   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.networking.k8s.io/v1beta1
   kind: ReferenceGrant
   metadata:
     name: allow-otel-collector-traces-access
     namespace: telemetry
   spec:
     from:
     - group: gateway.kgateway.dev
       kind: HTTPListenerPolicy
       namespace: {{< reuse "docs/snippets/namespace.md" >}}
     to:
     - group: ""
       kind: Service
       name: opentelemetry-collector-traces
   EOF
   ```

## Step 5: Verify your setup {#verify}

To verify that your setup is working, generate sample traffic and review the logs and Grafana dashboard.
   
1. Generate traffic for the httpbin app. 

   {{< tabs items="Cloud Provider LoadBalancer,Port-forward for local testing" tabTotal="2">}}
   {{% tab tabName="Cloud Provider LoadBalancer" %}}
   ```sh
   for i in {1..5}; do curl -v http://$INGRESS_GW_ADDRESS:8080/status/418 -H "host: www.example.com:8080"; done
   ```
   {{% /tab %}}
   {{% tab tabName="Port-forward for local testing" %}}
   ```sh
   for i in {1..5}; do curl -v localhost:8080/status/418 -H "host: www.example.com:8080"; done
   ```
   {{% /tab %}}
   {{< /tabs >}}

   Example output:

   ```
   < HTTP/1.1 418 Unknown
   I'm a teapot!
   ...
   ```

2. Check that logs are being collected.

   ```sh
   kubectl -n telemetry logs deploy/opentelemetry-collector-logs | grep '/status/418' | wc -l
   ```

   Example output: The count matches the number of requests that you sent, such as `5`.

   ```

       5
   ```

3. Check that traces are being collected.

   ```sh
   kubectl -n telemetry logs deploy/opentelemetry-collector-traces | grep 'http.status_code: Str(418)' | wc -l
   ```

   Example output: The count traces the number of services that were involved in responding to the request, such as `10`.

   ```

      10
   ```
   
## Step 6: Explore Grafana dashboards

{{< reuse "docs/snippets/grafana-dashboards.md" >}}


## Cleanup

{{< reuse "docs/snippets/cleanup.md" >}}

1. Remove the configmap for the Envoy gateway proxy dashboard and delete the `envoy.json` file.
   ```sh
   kubectl delete cm envoy-dashboard -n telemetry
   rm envoy.json
   kubectl delete cm {{< reuse "docs/snippets/pod-name.md" >}}-dashboard -n telemetry
   rm {{< reuse "docs/snippets/pod-name.md" >}}.json
   ```

2. Delete the HTTPListenerPolicy policies that collect logs and traces.

   ```sh
   kubectl delete httplistenerpolicy logging-policy -n {{< reuse "docs/snippets/namespace.md" >}}
   kubectl delete httplistenerpolicy tracing-policy -n {{< reuse "docs/snippets/namespace.md" >}}
   ```

3. Uninstall the Grafana Loki and Tempo components. 
   ```sh
   helm uninstall loki -n telemetry
   helm uninstall tempo -n telemetry
   ```

4. Uninstall the OpenTelemetry collectors. 
   ```sh
   helm uninstall opentelemetry-collector-metrics -n telemetry
   helm uninstall opentelemetry-collector-logs -n telemetry
   helm uninstall opentelemetry-collector-traces -n telemetry
   ```

5. Uninstall the Prometheus stack. 
   ```sh
   helm uninstall kube-prometheus-stack -n telemetry
   ```

6. Remove the `telemetry` namespace. 
   ```sh
   kubectl delete namespace telemetry
   ```
