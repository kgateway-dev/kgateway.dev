Set up protective limits on your gateway proxy to prevent your proxy from overwhelming slow or unhealthy upstream services. 

## About circuit breakers

With circuit breakers, you can cap resources, such as the number of active connections, pending requests, concurrent requests, and retries, allowing Envoy to fail fast instead of letting queues grow unbounded. By shedding excess load early, circuit breakers help contain cascading failures, reduce latency under stress, and give upstream services time to recover, making them a key building block for resilient, self-protecting service meshes and gateways.

For more information, see the [Envoy documentation](https://www.envoyproxy.io/docs/envoy/latest/intro/arch_overview/upstream/circuit_breaking). 

## Before you begin

{{< reuse "docs/snippets/prereq.md" >}}


## Setup

1. Create a BackendConfigPolicy that configures limits for the number of requests, connections, and retries for the httpbin app. 
   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.kgateway.dev/v1alpha1
   kind: BackendConfigPolicy
   metadata:
     name: httpbin-circuit-breakers
     namespace: httpbin
   spec:
     targetRefs:
     - group: ""
       kind: Service
       name: httpbin
     circuitBreakers:
       maxConnections: 1000
       maxPendingRequests: 500
       maxRequests: 2000
       maxRetries: 10
   EOF
   ```

2. Verify that your configuration is applied to the httpbin app by reviewing the Envoy config dump. 
   ```sh
   kubectl port-forward deploy/http -n kgateway-system 19000 &
   PF_PID=$!

   sleep 2

   curl -s http://localhost:19000/config_dump | jq '
     .configs[]
     | select(.["@type"] == "type.googleapis.com/envoy.admin.v3.ClustersConfigDump")
     | .dynamic_active_clusters[]
     | select(.cluster.name == "kube_httpbin_httpbin_8000")
     | {
         name: .cluster.name,
         connect_timeout: .cluster.connect_timeout,
         max_connections: .cluster.circuit_breakers.thresholds[0].max_connections,
         max_pending_requests: .cluster.circuit_breakers.thresholds[0].max_pending_requests,
         max_requests: .cluster.circuit_breakers.thresholds[0].max_requests,
         max_retries: .cluster.circuit_breakers.thresholds[0].max_retries,
       }'

   kill $PF_PID
   ```
  
   Example output: 
   ```
   {
      "name": "kube_httpbin_httpbin_8000",
      "connect_timeout": "5s",
      "max_connections": 1000,
      "max_pending_requests": 500,
      "max_requests": 2000,
      "max_retries": 10
   }
   ```


## Cleanup

{{< reuse "docs/snippets/cleanup.md" >}}

```sh
kubectl delete backendconfigpolicy httpbin-circuit-breakers -n httpbin
```

