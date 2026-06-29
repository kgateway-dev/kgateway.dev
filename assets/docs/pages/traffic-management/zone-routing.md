Route traffic preferentially to backend endpoints in the same availability zone as the gateway proxy to reduce cross-zone latency and network costs.

## About zone-aware routing

By default, the gateway proxy evenly distributes requests across all healthy endpoints regardless of their location. In multi-zone deployments, this can result in cross-zone traffic that adds latency and, on some cloud providers, incurs additional bandwidth costs.

Zone-aware routing instructs the gateway proxy to prefer endpoints in its own availability zone. If the local zone has enough healthy endpoints, requests stay within the zone. If local capacity falls below a configurable threshold, the proxy targets endpoints in other zones to maintain availability.

You enable zone-aware routing for a backend by configuring the `loadBalancer.zoneAware.preferLocal` fields in a BackendConfigPolicy resource. Two modes are available:

- **Prefer local (default)**: A soft preference. The proxy favors local-zone endpoints but still routes some traffic to other zones to maintain overall load balance. You can tune when zone-aware routing activates (`minEndpointsThreshold`) and what percentage of requests it applies to (`routingEnabled`). This mode is suitable for most deployments where you want to reduce cross-zone traffic without eliminating it entirely.
- **Force local**: A hard constraint. The proxy sends all traffic exclusively to the local zone as long as it has at least `minEndpointsInZoneThreshold` healthy endpoints. No traffic goes to other zones while that threshold is met. If local capacity drops below the threshold, the proxy falls back to prefer-local behavior. Use this mode when cross-zone traffic must be eliminated, for example for cost or compliance reasons, but be aware that it can overload the local zone if endpoints are unevenly distributed.

To configure how traffic is distributed within the local zone, you can also set a load balancing algorithm in the `loadBalancer` section of your BackendConfigPolicy resource. If you do not set one, traffic distribution defaults to round robin within the local zone. The following algorithms are supported:

- **`leastRequest`**: Sends each request to the local-zone endpoint with the fewest active connections.
- **`roundRobin`**: Distributes requests across local-zone endpoints in a round-robin order.
- **`random`**: Selects a random healthy endpoint from the local zone.

Zone-aware routing cannot be combined with `ringHash`, `maglev`, or `localityType`.

{{< callout >}}
Zone-aware routing is only applied when backend endpoints exist in at least two zones. If all endpoints are in the same zone as the proxy, the proxy routes traffic normally without applying zone-aware logic.
{{< /callout >}}

### How the proxy determines locality

The gateway proxy determines locality as follows: 

- **Gateway proxy locality**: The proxy determines its locality from the `KGATEWAY_NODE_ZONE`, `KGATEWAY_NODE_REGION`, and `KGATEWAY_NODE_SUBZONE` environment variables. These environment variables are not populated automatically from Kubernetes node labels. Instead, you must explicitly set them on the proxy by using a {{< reuse "docs/snippets/gatewayparameters.md" >}} resource. The environment variables are added to the `node.locality` section of the Envoy configuration and automatically injected into the proxy during startup. 
- **Endpoint locality**: Envoy does not discover backend endpoints on its own. Instead, the {{< reuse "docs/snippets/kgateway.md" >}} controller watches Kubernetes Services and their backing pods, then pushes endpoint data to the gateway proxy over a gRPC connection by using the Endpoint Discovery Service (EDS) API. For each pod, the controller looks up the Kubernetes node it is running on and reads the `topology.kubernetes.io/zone` label from that node. This information is then included in the EDS snapshot and sent to the gateway proxy. 

The gateway proxy compares its own `node.locality.zone` information against the `locality.zone` of each endpoint group. Endpoints where the zone matches the proxy's zone are added to the local endpoint pool.

## Before you begin

{{< reuse "docs/snippets/prereq.md" >}}

## Set the proxy's locality

Configure the locality on the gateway proxy. The proxy must know which zone it is running in for zone-aware routing to take effect.

1. Create a {{< reuse "docs/snippets/gatewayparameters.md" >}} resource and set the proxy's locality information as environment variables. The following example pins the proxy to the `us-east-1a` zone.

   {{< callout type="info" >}}
   Replace the example region, zone, and subzone values with values that match your cluster. To find the zone labels on your nodes, run `kubectl get nodes -o custom-columns='NAME:.metadata.name,ZONE:.metadata.labels.topology\.kubernetes\.io/zone'`. The `KGATEWAY_NODE_*` environment variables are static and set once when the proxy pod starts. The variables are not updated if the pod reschedules to a different node. You can use a `nodeSelector` to ensure that the proxy always runs on a node in the declared zone. If you remove the `nodeSelector` or change the zone without updating the environment variables, the proxy might use the wrong locality and zone-aware routing can behave incorrectly.
   {{< /callout >}}

   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: {{< reuse "docs/snippets/gatewayparam-apiversion.md" >}}
   kind: {{< reuse "docs/snippets/gatewayparameters.md" >}}
   metadata:
     name: zone-aware-gw-params
     namespace: kgateway-system
   spec:
     kube:
       podTemplate:
         nodeSelector:
           topology.kubernetes.io/zone: us-east-1a
       envoyContainer:
         env:
           - name: KGATEWAY_NODE_REGION
             value: us-east-1
           - name: KGATEWAY_NODE_ZONE
             value: us-east-1a
           - name: KGATEWAY_NODE_SUBZONE
             value: rack-a
   EOF
   ```

2. Create a Gateway resource that references the {{< reuse "docs/snippets/gatewayparameters.md" >}} resource.

   ```yaml
   kubectl apply -f- <<EOF
   kind: Gateway
   apiVersion: gateway.networking.k8s.io/v1
   metadata:
     name: http
     namespace: {{< reuse "docs/snippets/namespace.md" >}}
   spec:
     gatewayClassName: {{< reuse "docs/snippets/gatewayclass.md" >}}
     infrastructure:
       parametersRef:
         name: zone-aware-gw-params
         group: {{< reuse "docs/snippets/gatewayparam-group.md" >}}
         kind: {{< reuse "docs/snippets/gatewayparameters.md" >}}
     listeners:
     - protocol: HTTP
       port: 8080
       name: http
       allowedRoutes:
         namespaces:
           from: All
   EOF
   ```

3. Verify that the `KGATEWAY_NODE_*` environment variables are set on the proxy deployment.
   ```sh
   kubectl get deploy/http -n {{< reuse "docs/snippets/namespace.md" >}} -o yaml | grep -A 1 'KGATEWAY_NODE'
   ```

   Example output:
   ```console
   - name: KGATEWAY_NODE_REGION
     value: us-east-1
   - name: KGATEWAY_NODE_ZONE
     value: us-east-1a
   - name: KGATEWAY_NODE_SUBZONE
     value: rack-a
   ```

## Set up zone-aware routing

After proxy locality is configured, create a BackendConfigPolicy resource that enables zone-aware routing for the httpbin app.

{{< tabs >}}
{{% tab name="Prefer local zone" %}}

The `preferLocal` mode instructs Envoy to prefer sending traffic to endpoints in the local zone while still maintaining overall load balance across zones. Unlike force-local mode, some traffic can still go to other zones. The gateway proxy calculates zone weights so that the local zone receives a higher amount of traffic without fully isolating it. You can control two thresholds:

- `minEndpointsThreshold`: The minimum total number of endpoints across all zones that are required for zone-aware routing to activate. If the cluster has fewer endpoints than this value, the proxy falls back to distributing traffic evenly across all zones regardless of locality. This prevents zone-aware routing from making poor routing decisions when the backend is too small for zone weights to be meaningful.
- `routingEnabled`: The percentage of requests (0–100) that go through the zone-aware routing logic after the `minEndpointsThreshold` condition is met. Setting this field to `100` means all requests use zone-aware routing, but some requests might still be sent to other zones if routing all traffic locally overloads the local zone's endpoints relative to their proportional share. Requests that are not included in the `routingEnabled` percentage are distributed across all zones by using the load balancing algorithm that you configured in the `loadBalancer` section of the BackendConfigPolicy.

```yaml
kubectl apply -f- <<EOF
apiVersion: gateway.kgateway.dev/v1alpha1
kind: BackendConfigPolicy
metadata:
  name: httpbin-zone-aware
  namespace: httpbin
spec:
  targetRefs:
    - group: ""
      kind: Service
      name: httpbin
  loadBalancer:
    roundRobin: {}
    zoneAware:
      preferLocal:
        minEndpointsThreshold: 3
        routingEnabled: 100
EOF
```

{{% /tab %}}
{{% tab name="Force local zone" %}}

The `force` mode routes all traffic exclusively to the local zone as long as the local zone has at least `minEndpointsInZoneThreshold` healthy endpoints. If the local zone drops below that threshold, the gateway proxy falls back to prefer-local zone-aware routing.

```yaml
kubectl apply -f- <<EOF
apiVersion: gateway.kgateway.dev/v1alpha1
kind: BackendConfigPolicy
metadata:
  name: httpbin-zone-aware
  namespace: httpbin
spec:
  targetRefs:
    - group: ""
      kind: Service
      name: httpbin
  loadBalancer:
    roundRobin: {}
    zoneAware:
      preferLocal:
        minEndpointsThreshold: 3
        routingEnabled: 100
        force:
          minEndpointsInZoneThreshold: 2
EOF
```

{{% /tab %}}
{{< /tabs >}}

## Verify zone-aware routing

Confirm that Envoy received the zone-aware routing configuration by checking the config dump.
```sh
kubectl port-forward deploy/http -n {{< reuse "docs/snippets/namespace.md" >}} 19000 &
sleep 2
curl -s http://localhost:19000/config_dump | grep -A 6 'zone_aware_lb_config'
lsof -ti:19000 | xargs kill -9
```

Example output:
```console
"zone_aware_lb_config": {
"routing_enabled": {
  "value": 100
},
"min_cluster_size": "3"
}
--
"zone_aware_lb_config": {
"routing_enabled": {
  "value": 100
},
"min_cluster_size": "3"
}
```

{{< callout type="tip" >}}
You can optionally verify zone-aware routing by checking the `lb_zone_*` metrics that the gateway proxy emits after sending traffic to the backend. For example, look for stats, such as `lb_zone_routing_sampled` for requests that went through zone-aware routing and `lb_zone_no_capacity_left` to see whether or not enough endpoints exist in the local zone that can handle incoming requests. 
{{< /callout >}}

## Cleanup

{{< reuse "docs/snippets/cleanup.md" >}}

```sh
kubectl delete BackendConfigPolicy httpbin-zone-aware -n httpbin
kubectl delete {{< reuse "docs/snippets/gatewayparameters.md" >}} zone-aware-gw-params -n kgateway-system
```
