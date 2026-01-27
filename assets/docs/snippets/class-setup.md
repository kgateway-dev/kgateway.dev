```yaml
apiVersion: gateway.networking.k8s.io/v1
kind: GatewayClass
metadata:
  name: kgateway
spec:
  controllerName: kgateway.dev/kgateway
  description: Standard class for managing Gateway API ingress traffic.
```

The `kgateway.dev/kgateway` controller watches the resources in your cluster. When a Gateway resource is created that references the GatewayClass, the controller spins up an Envoy-based gateway proxy by using the configuration that is defined in the GatewayParameters resource. The controller also translates other resources, such as HTTPRoute, {{< reuse "docs/snippets/trafficpolicy.md" >}}, HTTPListenerPolicy, and more, into valid Envoy configuration, and applies the configuration to the gateway proxies it manages. 
