---
title: Kubernetes services
weight: 10
next: /docs/traffic-management/destination-types/backends
---

Route traffic to a Kubernetes service.

You can route to a Kubernetes service by simply referencing that service in the `backendRefs` section of your HTTPRoute resource as shown in the following example.

{{< callout type="info" >}}
Most guides in this documentation route traffic to a Kubernetes service directly. If you want to route to external resources, such as a static hostname or AWS resource, create a [Backend](/docs/traffic-management/destination-types/backends/) resource. 
{{< /callout >}}

```yaml {linenos=table,hl_lines=[13,14,15],linenostart=1,filename="k8s-service-httproute.yaml"}
apiVersion: gateway.networking.k8s.io/v1
kind: HTTPRoute
metadata:
  name: kube-backend
  namespace: default
spec:
  parentRefs:
  - name: http
    namespace: {{< reuse "docs/snippets/ns-system.md" >}}
  hostnames:
    - httpbin.example.com
  rules:
    - backendRefs:
      - name: httpbin
        port: 8000
      filters:
      - type: ExtensionRef
        extensionRef:
          group: gateway.kgateway.dev
          kind: RoutePolicy
          name: rewrite
```
