---
title: Simple load balancing
weight: 10
---

Decide how to load balance incoming requests to backend services.

## About simple load balancing

{{< reuse "docs/snippets/kgateway-capital.md" >}} supports multiple load balancing algorithms for selecting backend services to forward incoming requests to. By default, incoming requests are forwarded to the instance with the least requests. You can change this behavior and instead use a round robin algorithm to forward the request to a backend service. 

### Least request

The [least request load balancer algorithm](https://www.envoyproxy.io/docs/envoy/latest/intro/arch_overview/upstream/load_balancing/load_balancers#weighted-least-request) that generally selects the host with the fewest requests. The following rules apply: 

* If no `localityType` is set, send the request to the host with the fewest requests. 
* If `localityType` is set, a weighted round robin approach is used, in which  higher weighted endpoints are considered more often in the round robin rotation to achieve the selected weight. 

### Round robin

The [round robin load balancer algorithm](https://www.envoyproxy.io/docs/envoy/latest/intro/arch_overview/upstream/load_balancing/load_balancers#weighted-least-request) selects a backend host in a round robin order. If a `localityType` is also defined, a weighted round robin algorithm is used, in which higher weighted endpoints are considered more often in the round robin rotation to achieve the selected weight. 

### Random

The [random load balancer algorithm](https://www.envoyproxy.io/docs/envoy/latest/intro/arch_overview/upstream/load_balancing/load_balancers#weighted-least-request) selects a random host that is available. This load balancing algorithm usually performs better than the round robin algorithm if no health checks are configured for the backend host. 

## Other load balancing options

TODO no idea if these are supported

Learn about other load balancing options that you can set in the load balancer policy.

{{% callout type="info" %}}
All settings in this section can be set only in conjunction with a simple load balancing mode or consistent hash algorithm.
{{% /callout %}}

### Healthy panic threshold 

By default, {{< reuse "docs/snippets/kgateway.md" >}} only considers services that are healthy and available when load balancing incoming requests among backend services. In the case that the number of healthy backend services becomes too low, you can instruct {{< reuse "docs/snippets/kgateway.md" >}} to disregard the backend health status and either load balance requests among all or no hosts by using the `healthy_panic_threshold` setting. If not set, the threshold defaults to 50%. To disable panic mode, set this field to 0.

To learn more about this setting and when to use it, see the [Envoy documentation](https://www.envoyproxy.io/docs/envoy/latest/intro/arch_overview/upstream/load_balancing/panic_threshold#arch-overview-load-balancing-panic-threshold). 

### Update merge window 

Sometimes, your deployments might have health checks and metadata updates that use a lot of CPU and memory. In such cases, you can use the `update_merge_window` setting. This way, {{< reuse "docs/snippets/kgateway.md" >}} merges all updates together within a specific timeframe. For more information about this setting, see the [Envoy documentation](https://www.envoyproxy.io/docs/envoy/latest/api-v3/config/cluster/v3/cluster.proto#config-cluster-v3-cluster-commonlbconfig). If not set, the update merge window defaults to 1000ms. To disable the update merge window, set this field to 0s.

### Warm up duration 

If you have new upstream services that need time to get ready for traffic, use the `warmupDurationSecs` setting. This way, {{< reuse "docs/snippets/kgateway.md" >}} gradually increases the amount of traffic for the service. This setting is effective in scaling events, such as when new replicas are added to handle increased load. However, if all services start at the same time, this setting might not be as effective as all endpoints receive the same amount of requests.

Note that the `warmupDurationSecs` field can only be set if the [load balancing mode](#about-simple-load-balancing) is set to `roundRobin` or `leastRequest`. 

To learn more about this setting, see the [Istio Destination Rule documentation](https://istio.io/latest/docs/reference/config/networking/destination-rule/). 

## Before you begin

{{< reuse "docs/snippets/prereq.md" >}}

## Set up a load balancing algorithm

Define the load balancing algorithm that you want to use for your backend app in a BackendConfigPolicy. Then, apply the algorithm to the backend app's HTTPRoute by creating a {{< reuse "docs/snippets/trafficpolicy.md" >}}.

1. Create a BackendConfigPolicy to configure your load balancing algorithm for the httpbin app. 
   {{< tabs tabTotal="3" items="Least requests,Round robin,Random" >}}
   {{% tab tabName="Least requests" %}}
   ```yaml
   kubectl apply -f- <<EOF
   kind: BackendConfigPolicy
   apiVersion: gateway.kgateway.dev/v1alpha1
   metadata:
     name: httpbin-policy
     namespce: httpbin
   spec:
     targetRefs:
       - name: httpbin
         group: ""
         kind: Service
     loadBalancer:
       leastRequest:
         choiceCount: 3
   EOF
   ```
   {{% /tab %}}
   {{% tab tabName="Round robin" %}}
   ```yaml
   kubectl apply -f- <<EOF
   kind: BackendConfigPolicy
   apiVersion: gateway.kgateway.dev/v1alpha1
   metadata:
     name: httpbin-policy
     namespce: httpbin
   spec:
     targetRefs:
       - name: httpbin
         group: ""
         kind: Service
     loadBalancer:
       roundRobin:
         slowStartConfig:
           window: 10s
           aggression: "1.5"
           minWeightPercent: 10
   EOF
   ```
   {{% /tab %}}
   {{% tab tabName="Round robin" %}}
   ```yaml
   kubectl apply -f- <<EOF
   kind: BackendConfigPolicy
   apiVersion: gateway.kgateway.dev/v1alpha1
   metadata:
     name: httpbin-policy
     namespce: httpbin
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

TODO does simply load balancing require a trafficpolicy on the route?
Apply the load balancing algorithm to the backend app's HTTPRoute by creating a {{< reuse "docs/snippets/trafficpolicy.md" >}}.

Testing: The load balancing algorithms are kind of hard to test with the exception of round robin. But random and least request will be harder. So we might need to show the Envoy configuration as a proof instead.