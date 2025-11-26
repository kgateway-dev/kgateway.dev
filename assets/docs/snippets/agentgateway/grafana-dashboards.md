You can use the pre-built Grafana dashboards to observe the control and data plane statuses. 

1. Create a Grafana dashboard for the control metrics. You can download the following sample Grafana dashboard configuration: 
   * [Kgateway operations dashboard](../kgateway.json) 
     ```sh
     curl -L "http://kgateway.dev/docs/main/agentgateway/observability/kgateway.json" >> kgateway.json 
     ```

2. Import the Grafana dashboard.
   ```sh
   kubectl -n telemetry create cm kgateway-dashboard \
   --from-file=kgateway.json
   kubectl label -n telemetry cm kgateway-dashboard grafana_dashboard=1
   ```

3. Open and log in to Grafana by using the username `admin` and password `prom-operator`. 
      
   {{< tabs items="Cloud Provider LoadBalancer,Port-forward for local testing" tabTotal="2">}}
{{% tab tabName="Cloud Provider LoadBalancer" %}}
```sh
open "http://$(kubectl -n telemetry get svc kube-prometheus-stack-grafana -o jsonpath="{.status.loadBalancer.ingress[0]['hostname','ip']}"):3000"
```
{{% /tab %}}
{{% tab tabName="Port-forward for local testing" %}}
1. Port-forward the Grafana service to your local machine.
   ```sh
   kubectl port-forward deployment/kube-prometheus-stack-grafana -n telemetry 3000
   ```
2. Open Grafana in your browser by using the following URL: [http://localhost:3000](http://localhost:3000)
{{% /tab %}}
   {{< /tabs >}}
            
4. Go to **Dashboards** > **Kgateway Operations** to open the Kgateway Operations dashboard that you imported. Verify that you see kgateway metrics, such as the translation and reconciliation time, total number of operations, or the number of resources in your cluster. 
      
   {{< reuse-image src="img/kgateway-dashboard.png" >}}
   {{< reuse-image-dark srcDark="img/kgateway-dashboard.png" >}}
   
   | Metric | Description |
   | -- | -- |
   | Number of translations running per translator | The number of active Kubernetes Gateway API translations. |
   | Number of reconciliations running per controller | The number of active reconciliations for each controller. |
   | Number of resources | The number of Kubernetes Gateway API and kgateway resources in your cluster. |
   | Translations rate by results | The rate of translations in seconds and their statuses. |
   | Reconciliation rate by results | The rate of reconciliations in seconds and their statuses. |
   | Status syncs rate by results | The rate of status syncs in seconds and their statuses. |
   | Total operations | The total number of reconciliations for each controller plus the total number of translations for each translator, and the total number of status syncs for each status syncer. |   
   | XDS resources by gateway | The total number of resources in the XDS snapshot for each gateway, such as clusters, endpoints, listeners, and routes. |
   | Routing domains per gateway port | The total number of routing domains for each gateway and port. |
   | Reconciliation latency | In the last 5 minutes, the amount of time that it took 70%, 90%, and 99% of reconciliation processes to finish. |
   | Status Syncer Latency |  In the last 5 minutes, the amount of time that it took 70%, 90%, and 99% of status syncs to finish. | 
   | Translation Latency | In the last 5 minutes, the amount of time that it took 70%, 90%, and 99% of translations to finish. |
   | XDS Snapshot Sync Latency | In the last 5 minutes, the amount of time that it took 70%, 90%, and 99% of xDS snapshots to finish. |
   | Resource Status Sync Latency | In the last 5 minutes, the amount of time that it took 70%, 90%, and 99% of resource status syncs to finish. |
   | Status Syncs by Resource | The total number of status syncs completed by resource type. |