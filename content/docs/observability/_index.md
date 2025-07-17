---
title: Observability
weight: 700
description: Gain insight into the health and performance of your gateways.
next: /docs/operations
prev: /docs/integrations
---

Gain insight into the health and performance of your gateway environment.

Observability tools are essential to gain insight into the health and performance of your gateway proxies. [OpenTelemetry](https://opentelemetry.io/) (OTel) is a flexible, open source framework that provides a set of APIs, libraries, and instrumentation to help capture and export observability data.

## Observability data types {#data-types}

Observability is built on three core pillars as described in the following table. By combining these three data types, you get a complete picture of your system's health and performance.

| Pillar | Description |
| -- | -- |
| Logs | Discrete events that happen at a specific time with detailed context. |
| Metrics | Numerical measurements aggregated over time intervals. |
| Traces | Records of requests as they flow through distributed systems. |




 OpenTelemetry collector that scapes metrics from the kgateway control plane and data plane gateway proxies. The metrics that are collected by the OpenTelemetry collector are exposed in Prometheus format. To visualize these metrics, you also deploy a Grafana instance that scrapes the metrics from the OpenTelemetry collector.

## Before you begin

{{< reuse "docs/snippets/prereq.md" >}}

## Set up an OpenTelemetry collector {#otel}

Deploy the open source OpenTelemetry collector in your cluster.

1. Add the Helm repository for OpenTelemetry. 
   
   ```sh
   helm repo add open-telemetry https://open-telemetry.github.io/opentelemetry-helm-charts
   helm repo update
   ```

2. Install the OpenTelemetry collector in your cluster. This command sets up pipelines that scrape metrics from the kgateway control plane and data plane gateway, and exposes them in Prometheus format.
   
   ```sh
   helm upgrade --install opentelemetry-collector open-telemetry/opentelemetry-collector \
   --version 0.97.1 \
   --set mode=deployment \
   --set image.repository="otel/opentelemetry-collector-contrib" \
   --set command.name="otelcol-contrib" \
   --namespace=otel \
   --create-namespace \
   -f -<<EOF
   clusterRole:
     create: true
     rules:
     - apiGroups:
       - ''
       resources:
       - 'pods'
       - 'nodes'
       verbs:
       - 'get'
       - 'list'
       - 'watch'
   ports:
     promexporter:
       enabled: true
       containerPort: 9099
       servicePort: 9099
       protocol: TCP
   config:
     receivers:
       prometheus/kgateway-dataplane:
         config:
           scrape_configs:
           # Scrape the kgateway Gateway pods
           - job_name: kgateway-gateways
             honor_labels: true
             kubernetes_sd_configs:
             - role: pod
             relabel_configs:
               - action: keep
                 regex: (.+)
                 source_labels:
                 - __meta_kubernetes_pod_label_gateway_networking_k8s_io_gateway_name
               - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_scrape]
                 action: keep
                 regex: true
               - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_path]
                 action: replace
                 target_label: __metrics_path__
                 regex: (.+)
               - action: replace
                 source_labels:
                 - __meta_kubernetes_pod_ip
                 - __meta_kubernetes_pod_annotation_prometheus_io_port
                 separator: ':'
                 target_label: __address__
               - action: labelmap
                 regex: __meta_kubernetes_pod_label_(.+)
               - source_labels: [__meta_kubernetes_namespace]
                 action: replace
                 target_label: kube_namespace
               - source_labels: [__meta_kubernetes_pod_name]
                 action: replace
                 target_label: pod
       prometheus/kgateway-controlplane:
         config:
           scrape_configs:
           # Scrape the kgateway pods
           - job_name: kgateway-gateways
             honor_labels: true
             kubernetes_sd_configs:
             - role: pod
             relabel_configs:
               - action: keep
                 regex: kgateway
                 source_labels:
                 - __meta_kubernetes_pod_label_kgateway
               - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_scrape]
                 action: keep
                 regex: true
               - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_path]
                 action: replace
                 target_label: __metrics_path__
                 regex: (.+)
               - action: replace
                 source_labels:
                 - __meta_kubernetes_pod_ip
                 - __meta_kubernetes_pod_annotation_prometheus_io_port
                 separator: ':'
                 target_label: __address__
               - action: labelmap
                 regex: __meta_kubernetes_pod_label_(.+)
               - source_labels: [__meta_kubernetes_namespace]
                 action: replace
                 target_label: kube_namespace
               - source_labels: [__meta_kubernetes_pod_name]
                 action: replace
                 target_label: pod
     exporters:
       prometheus:
         endpoint: 0.0.0.0:9099
       debug: {}
     service:
       pipelines:
         metrics:
           receivers: [prometheus/kgateway-dataplane, prometheus/kgateway-controlplane]
           processors: [batch]
           exporters: [debug, prometheus]
   EOF
   ```

3. Verify that the OpenTelemetry collector pod is running. 
   
   ```sh
   kubectl get pods -n otel
   ```
   
   Example output: 
   ```console
   NAME                                       READY   STATUS    RESTARTS   AGE
   opentelemetry-collector-6d658bf47c-hw6v8   1/1     Running   0          12m
   ```

Good job! Now you have an OpenTelemetry collector that scrapes and exposes metrics in Prometheus format.

## Set up Grafana {#grafana}

To visualize the metrics that you collect with the OpenTelemetry collector, deploy Grafana as part of the Prometheus stack in your cluster.

1. Deploy Grafana and other Prometheus components in your cluster. The following example uses the [kube-prometheus-stack community Helm chart](https://github.com/prometheus-community/helm-charts/tree/main/charts/kube-prometheus-stack) to install these components. 
   
   ```yaml
   helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
   helm repo update

   helm upgrade --install kube-prometheus-stack \
   prometheus-community/kube-prometheus-stack \
   --version 61.2.0 \
   --namespace monitoring \
   --create-namespace \
   --values - <<EOF
   alertmanager:
     enabled: false
   grafana: 
     service: 
       type: LoadBalancer
       port: 3000
   prometheus: 
     prometheusSpec: 
       ruleSelectorNilUsesHelmValues: false
       serviceMonitorSelectorNilUsesHelmValues: false
       podMonitorSelectorNilUsesHelmValues: false
   EOF
   ```
   
2. Verify that the Prometheus stack's components are up and running. 
   
   ```sh
   kubectl get pods -n monitoring
   ```
   
   Example output: 
   ```console
   NAME                                                        READY   STATUS    RESTARTS   AGE
   kube-prometheus-stack-grafana-86844f6b47-frwn9              3/3     Running   0          20s
   kube-prometheus-stack-kube-state-metrics-7c8d64d446-6cs7m   1/1     Running   0          21s
   kube-prometheus-stack-operator-75fc8896c7-r7bgk             1/1     Running   0          20s
   prometheus-kube-prometheus-stack-prometheus-0               2/2     Running   0          17s 
   ```

3. Create a PodMonitor resource to scrape metrics from the OpenTelemetry collector. 
   
   ```yaml
   kubectl apply -n otel -f- <<EOF
   apiVersion: monitoring.coreos.com/v1
   kind: PodMonitor
   metadata:
     name: otel-monitor
   spec:
     podMetricsEndpoints:
     - interval: 30s
       port: promexporter
       scheme: http
     selector:
       matchLabels:
         app.kubernetes.io/name: opentelemetry-collector
   EOF
   ```
   
4. Save the [sample Grafana dashboard configuration](grafana.json) as `envoy.json`. 

5. Import the Grafana dashboard. 
   
   ```sh
   kubectl -n monitoring create cm envoy-dashboard \
   --from-file=envoy.json
   kubectl label -n monitoring cm envoy-dashboard grafana_dashboard=1
   ```
   
## Visualize metrics in Grafana
   
1. Generate traffic for the httpbin app. 

   {{< tabs items="Cloud Provider LoadBalancer,Port-forward for local testing" >}}
   {{% tab %}}
   ```sh
   for i in {1..5}; do curl -v http://$INGRESS_GW_ADDRESS:8080/headers -H "host: www.example.com:8080"; done
   ```
   {{% /tab %}}
   {{% tab  %}}
   ```sh
   for i in {1..5}; do curl -v localhost:8080/headers -H "host: www.example.com:8080"; done
   ```
   {{% /tab %}}
   {{< /tabs >}}

2. Open Grafana and log in to Grafana by using the username `admin` and password `prom-operator`. 
   
   {{< tabs items="Cloud Provider LoadBalancer,Port-forward for local testing" >}}
   {{% tab %}}
   ```sh
   open "http://$(kubectl -n monitoring get svc kube-prometheus-stack-grafana -o jsonpath="{.status.loadBalancer.ingress[0]['hostname','ip']}"):3000"
   ```
   {{% /tab %}}
   {{% tab  %}}
   1. Port-forward the Grafana service to your local machine.
      ```sh
      kubectl port-forward deployment/kube-prometheus-stack-grafana -n monitoring 3000
      ```
   2. Open Grafana in your browser by using the following URL: [http://localhost:3000](http://localhost:3000)
   {{% /tab %}}
   {{< /tabs >}}
   
3. Go to **Dashboards** > **Envoy** to open the dashboard that you imported. Verify that you see the traffic that you generated for the httpbin app. 
   
   {{< reuse-image src="img/grafana-dashboard.png" >}}

## Cleanup

{{< reuse "docs/snippets/cleanup.md" >}}

1. Remove the configmap for the Envoy dashboard. 
   ```sh
   kubectl delete cm envoy-dashboard -n monitoring
   ```

2. Remove the PodMonitor. 
   ```sh
   kubectl delete podmonitor otel-monitor -n otel
   ```

3. Uninstall Grafana. 
   ```sh
   helm uninstall kube-prometheus-stack -n monitoring  
   ```

4. Uninstall the OpenTelemetry collector. 
   ```sh
   helm uninstall opentelemetry-collector -n otel
   ```

5. Remove the `monitoring` and `otel` namespaces. 
   ```sh
   kubectl delete namespace monitoring otel
   ```
