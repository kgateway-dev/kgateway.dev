{{% conditional-text include-if="envoy" %}}
```yaml
apiVersion: gateway.networking.k8s.io/v1
kind: GatewayClass
metadata:
  name: kgateway
spec:
  controllerName: kgateway.dev/kgateway
  description: Standard class for managing Gateway API ingress traffic.
```
{{% /conditional-text %}}
{{< conditional-text include-if="agentgateway" >}}
{{< tabs items="agentgateway,agentgateway-waypoint" tabTotal="2">}}
{{% tab %}}
The `agentgateway` GatewayClass is the standard class for when you want to use an agentgateway proxy in kgateway.
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
{{% tab %}}
The `agentgateway-waypoint` GatewayClass is for when you use agentgateway as a waypoint in an Istio Ambient service mesh setup.
```yaml
apiVersion: gateway.networking.k8s.io/v1
kind: GatewayClass
metadata:
  name: agentgateway-waypoint
spec:
  controllerName: kgateway.dev/kgateway
  description: Specialized class for Istio ambient mesh waypoint proxies.
```
{{% /tab %}}
{{< /tabs >}}
{{< /conditional-text >}}

The `kgateway.dev/kgateway` controller watches the resources in your cluster. When a Gateway resource is created that references the GatewayClass, the controller spins up an {{< conditional-text include-if="envoy" >}}Envoy-based gateway{{< /conditional-text >}}{{< conditional-text include-if="agentgateway" >}}agentgateway{{< /conditional-text >}} proxy by using the configuration that is defined in the GatewayParameters resource. The controller also translates other resources, such as HTTPRoute, {{< reuse "docs/snippets/trafficpolicy.md" >}}, HTTPListenerPolicy, and more, into valid {{< conditional-text include-if="envoy" >}}Envoy{{< /conditional-text >}}{{< conditional-text include-if="agentgateway" >}}agentgateway{{< /conditional-text >}} configuration, and applies the configuration to the gateway proxies it manages. 
