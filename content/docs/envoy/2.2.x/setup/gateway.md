---
title: Set up a gateway
weight: 5
description: Set up your first gateway proxy and explore how to use it to route traffic to a sample app. 
---

{{< reuse "docs/snippets/setup-gateway.md" >}}

## Next 

Deploy the [httpbin sample app]({{< link-hextra path="/install/sample-app/" >}}) and start routing traffic to the app. You can use this app to try out other traffic management, resiliency, and security guides in this documentation. 

## Other configuration examples

Review other common configuration examples for your Gateway. To customize your Gateway even further, such as with Kubernetes overlays, check out [Customize the proxy]({{< link-hextra path="/setup/customize" >}}). 

### Static IP address 

You can assign a static IP address to the service that exposes your gateway proxy by using the `spec.addresses` field. 

```yaml
kind: Gateway
apiVersion: gateway.networking.k8s.io/v1
metadata:
  name: http
  namespace: {{< reuse "docs/snippets/namespace.md" >}}
spec:
  gatewayClassName: {{< reuse "docs/snippets/gatewayclass.md" >}}
  addresses:
    - type: IPAddress
      value: 203.0.113.11
  listeners:
    - protocol: HTTP
      port: 80
      name: http
      allowedRoutes:
        namespaces:
          from: Same
```
