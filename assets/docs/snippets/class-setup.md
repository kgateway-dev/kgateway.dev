{{< tabs items="kgateway,kgateway-waypoint">}}

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
{{< /tabs >}}