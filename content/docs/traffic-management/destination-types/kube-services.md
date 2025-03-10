---
title: Kubernetes services
weight: 10
next: /docs/traffic-management/destination-types/upstreams
---

Route traffic to a Kubernetes service.

You can route to a Kubernetes service by simply referencing that service in the `backendRefs` section of your HTTPRoute resource as shown in the following example.

{{< callout type="info" >}}
Most guides in this documentation route traffic to a Kubernetes service directly. If you want to configure additional settings for your Kubernetes service, such as the HTTP/2 protocol or a different load balancing algorithm, use an Backend resource as your backing destination instead. For more information, see [Backends](/docs/traffic-management/destination-types/backends/). 
{{< /callout >}}

```yaml {linenos=table,hl_lines=[13,14,15],linenostart=1,filename="k8s-service-httproute.yaml"}
apiVersion: gateway.networking.k8s.io/v1
kind: HTTPRoute
metadata:
  name: static-backend
  namespace: default
spec:
  parentRefs:
  - name: http
    namespace: {{< reuse "docs/snippets/ns-system.md" >}}
  hostnames:
    - static.example
  rules:
    - backendRefs:
      - name: httpbin
        port: 8000
      filters:
      - type: ExtensionRef
        extensionRef:
          group: gateway.solo.io
          kind: RouteOption
          name: rewrite
```
