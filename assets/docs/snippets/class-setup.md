{{< tabs items="kgateway,kgateway-waypoint,agentgateway">}}

{{% tab %}}
The `kgateway` GatewayClass is the standard class that you use for most Gateways.
```yaml
apiVersion: gateway.networking.k8s.io/v1
kind: GatewayClass
metadata:
  name: kgateway
spec:
  controllerName: kgateway.dev/kgateway
  description: Standard class for managing Gateway API ingress traffic.
```
{{% /tab %}}

{{% tab %}}
The `kgateway-waypoint` GatewayClass is for when you use kgateway as a waypoint in an Istio Ambient service mesh setup.
```yaml
apiVersion: gateway.networking.k8s.io/v1
kind: GatewayClass
metadata:
  name: kgateway-waypoint
spec:
  controllerName: kgateway.dev/kgateway
  description: Specialized class for Istio ambient mesh waypoint proxies.
```
{{% /tab %}}
{{% tab %}}
The `agentgateway` GatewayClass is for when you want to use an agentgateway proxy in kgateway.
```yaml
apiVersion: gateway.networking.k8s.io/v1
kind: GatewayClass
metadata:
  name: agentgateway
spec:
  controllerName: kgateway.dev/agentgateway
  description: Specialized class for agentgateway.
```
{{% /tab %}}
{{< /tabs >}}

The `kgateway.dev/kgateway` controller watches the resources in your cluster. When a Gateway resource is created that references the `kgateway` or `kgateway-waypoint` GatewayClass, the controller spins up an Envoy-based gateway proxy by using the configuration that is defined in the GatewayParameters resource. The controller also translates other resources, such as HTTPRoute, {{< reuse "docs/snippets/trafficpolicy.md" >}}, HTTPListenerPolicy, and more, into valid Envoy configuration, and applies the configuration to the gateway proxies it manages. 

Similarily, the `kgateway.dev/agentgateway` controller watches for Gateways with the `agentgateway` GatewayClass. The controller spins up an agentgateway proxy with the default [agentgateway proxy template](https://github.com/kgateway-dev/kgateway/blob/main/internal/kgateway/helm/kgateway/templates/gateway/agent-gateway-deployment.yaml). The controller also translates other resources, such as HTTPRoute, {{< reuse "docs/snippets/trafficpolicy.md" >}}, HTTPListenerPolicy, and more, into valid agentgateway configuration, and applies the configuration to the gateway proxies it manages. 