---
title: Simple load balancing
weight: 10
---

Decide how to load balance incoming requests to backend services.

## About simple load balancing

{{< reuse "docs/snippets/kgateway-capital.md" >}} supports multiple load balancing algorithms for selecting backend services to forward incoming requests to. By default, incoming requests are forwarded to the instance with the least requests. You can change this behavior and instead use a round robin algorithm to forward the request to a backend service. 

### Least request

The [least request load balancer algorithm](https://www.envoyproxy.io/docs/envoy/latest/intro/arch_overview/upstream/load_balancing/load_balancers#weighted-least-request) generally selects the host with the fewest requests. The following rules apply: 

* If no `localityType` is set, send the request to the host with the fewest requests. 
* If `localityType` is set, a weighted round robin approach is used, in which higher weighted endpoints are considered more often in the round robin rotation to achieve the selected weight. 

### Round robin

The [round robin load balancer algorithm](https://www.envoyproxy.io/docs/envoy/latest/intro/arch_overview/upstream/load_balancing/load_balancers#weighted-least-request) selects a backend host in a round robin order. If a `localityType` is also defined, a weighted round robin algorithm is used, in which higher weighted endpoints are considered more often in the round robin rotation to achieve the selected weight. 

### Random

The [random load balancer algorithm](https://www.envoyproxy.io/docs/envoy/latest/intro/arch_overview/upstream/load_balancing/load_balancers#weighted-least-request) selects a random host that is available. This load balancing algorithm usually performs better than the round robin algorithm if no health checks are configured for the backend host. 

## Other load balancing options

Learn about other load balancing options that you can set in the load balancer policy.

{{< callout type="info" >}}
All settings in this section can be set only in conjunction with a simple load balancing mode or consistent hash algorithm.
{{< /callout >}}

### Healthy panic threshold 

By default, {{< reuse "docs/snippets/kgateway.md" >}} only considers services that are healthy and available when load balancing incoming requests among backend services. In the case that the number of healthy backend services becomes too low, you can instruct {{< reuse "docs/snippets/kgateway.md" >}} to disregard the backend health status and either load balance requests among all or no hosts by using the `healthy_panic_threshold` setting. If not set, the threshold defaults to 50%. To disable panic mode, set this field to 0.

To learn more about this setting and when to use it, see the [Envoy documentation](https://www.envoyproxy.io/docs/envoy/latest/intro/arch_overview/upstream/load_balancing/panic_threshold#arch-overview-load-balancing-panic-threshold). 

### Update merge window 

Sometimes, your deployments might have health checks and metadata updates that use a lot of CPU and memory. In such cases, you can use the `update_merge_window` setting. This way, {{< reuse "docs/snippets/kgateway.md" >}} merges all updates together within a specific timeframe. For more information about this setting, see the [Envoy documentation](https://www.envoyproxy.io/docs/envoy/latest/api-v3/config/cluster/v3/cluster.proto#config-cluster-v3-cluster-commonlbconfig). If not set, the update merge window defaults to 1000ms. To disable the update merge window, set this field to 0s.

## Before you begin

{{< reuse "docs/snippets/prereq.md" >}}

## Set up a load balancing algorithm

Define the load balancing algorithm that you want to use for your backend app in a BackendConfigPolicy.

1. Create a BackendConfigPolicy to configure your load balancing algorithm for the httpbin app. 
   {{< tabs tabTotal="3" items="Least requests,Round robin,Random" >}}
   {{% tab tabName="Least requests" %}}
   ```yaml
   kubectl apply -f- <<EOF
   kind: BackendConfigPolicy
   apiVersion: gateway.kgateway.dev/v1alpha1
   metadata:
     name: httpbin-lb-policy
     namespace: httpbin
   spec:
     targetRefs:
       - name: httpbin
         group: ""
         kind: Service
     loadBalancer:
       leastRequest:
         choiceCount: 3
         slowStart:
           window: 10s
           aggression: "1.5"
           minWeightPercent: 10
   EOF
   ```

   {{< reuse "/docs/snippets/review-table.md" >}}

   | Setting | Description |
   | -- | -- |
   | `choiceCount` | The number of random available backend hosts to consider when choosing the host with the fewest requests. Deafults to 2. |
   | `slowStart` | When you add new backend hosts to the pool of endpoints to route to, slow start mode progressively increases the amount of traffic that is routed to those backends. This can be useful for services that require warm-up time to serve full production loads, to prevent request timeouts, loss of data, and deteriorated user experience. |
   | `slowStart.window` | The duration of the slow start window. If set, a newly-created backend endpoint remains in slow start mode from its creation time until the duration of the slow start window has elapsed. |
   | `slowStart.aggression` | The rate of traffic increase over the duration of the slow start window. Defaults to 1.0, so that the endpoint receives a linearly-increasing amount of traffic. For more information about fine-tuning this value, see the [API docs](../../../../reference/api/#slowstart). |
   | `slowStart.minWeightPercent` | The minimum percentage of weight that an endpoint must have in the caluclation of aggression. This helps prevent weights that are so small that endpoints receive no traffic during the slow start window. Defaults to 10%. |
   {{% /tab %}}
   {{% tab tabName="Round robin" %}}
   ```yaml
   kubectl apply -f- <<EOF
   kind: BackendConfigPolicy
   apiVersion: gateway.kgateway.dev/v1alpha1
   metadata:
     name: httpbin-lb-policy
     namespace: httpbin
   spec:
     targetRefs:
       - name: httpbin
         group: ""
         kind: Service
     loadBalancer:
       roundRobin:
         slowStart:
           window: 10s
           aggression: "1.5"
           minWeightPercent: 10
   EOF
   ```

   {{< reuse "/docs/snippets/review-table.md" >}}

   | Setting | Description |
   | -- | -- |
   | `slowStart` | When you add new backend hosts to the pool of endpoints to route to, slow start mode progressively increases the amount of traffic that is routed to those backends. This can be useful for services that require warm-up time to serve full production loads, to prevent request timeouts, loss of data, and deteriorated user experience. |
   | `slowStart.window` | The duration of the slow start window. If set, any newly-created backend endpoints remain in slow start mode from its creation time until the duration of the slow start window has elapsed. |
   | `slowStart.aggression` | The rate of traffic increase over the duration of the slow start window. Defaults to 1.0, so that the endpoint receives a linearly-increasing amount of traffic. For more information about fine-tuning this value, see the [API docs](../../../../reference/api/#slowstart). |
   | `slowStart.minWeightPercent` | The minimum percentage of weight that an endpoint must have in the caluclation of aggression. This helps prevent weights that are so small that endpoints receive no traffic during the slow start window. Defaults to 10%. |
   {{% /tab %}}
   {{% tab tabName="Random" %}}
   Note that no further settings are required because the load balancing is random.
   ```yaml
   kubectl apply -f- <<EOF
   kind: BackendConfigPolicy
   apiVersion: gateway.kgateway.dev/v1alpha1
   metadata:
     name: httpbin-lb-policy
     namespace: httpbin
   spec:
     targetRefs:
       - name: httpbin
         group: ""
         kind: Service
     loadBalancer:
       random: {}
   EOF
   ```
   {{% /tab %}}
   {{< /tabs >}}

2. Verify that your configuration is applied by reviewing the Envoy configuration. 
   1. Port forward the `http` deployment on port 19000. 
      ```sh
      kubectl port-forward deploy/http -n {{< reuse "docs/snippets/namespace.md" >}} 19000 & 
      ```
   2. Open the `config_dump` endpoint. 
      ```sh
      open http://localhost:19000/config_dump
      ```
   3. Search for the `lb_policy` field, and verify that the policy that you set is listed, along with your other load balancing settings. For example, the following output shows the `LEAST_REQUEST` policy, with the `choice_count` field set to `3`, and settings for the slow start window.
      ```json
      ...
      "lb_policy": "LEAST_REQUEST",
      "metadata": {},
      "common_lb_config": {
       "consistent_hashing_lb_config": {}
      },
      "ignore_health_on_host_removal": true,
      "least_request_lb_config": {
       "choice_count": 3,
       "slow_start_config": {
        "slow_start_window": "10s",
        "aggression": {
         "default_value": 1.5,
         "runtime_key": "upstream.kube_httpbin_httpbin_9000.slowStart.aggression"
        },
        "min_weight_percent": {
         "value": 10
        }
       }
      }
      ...
      ```
   4. Stop port-forwarding the `http` deployment.
      ```sh
      lsof -ti:19000 | xargs kill -9
      ```

## Cleanup

{{< reuse "docs/snippets/cleanup.md" >}}

```sh
kubectl delete BackendConfigPolicy httpbin-lb-policy -n httpbin
```