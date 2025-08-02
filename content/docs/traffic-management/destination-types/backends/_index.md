---
title: Backends
weight: 20
prev: /docs/traffic-management/destination-types/kube-services
---

Use a Backend resource to define a backing destination that you want kgateway to route to. A Backend destination is external to the cluster and, as such, cannot be represented as a Kubernetes Service. For more information, see the [Backend API docs](/docs/reference/api/#backend).

## Types

Check out the following guides for examples on how to use the supported Backends types with kgateway.

{{< cards >}}
{{< card link="static" title="Static IP address or hostname" >}}
{{< card link="lambda" title="AWS Lambda" >}}
{{< /cards >}}

## Routing

You can route to a Backend by simply referencing that Backend in the `backendRefs` section of your HTTPRoute resource as shown in the following example. Note that if your Backend and HTTPRoute resources exist in different namespaces, you must create a Kubernetes ReferenceGrant resource to allow the HTTPRoute to access the Backend.

{{< callout type="warning" >}}

- Avoid specifying a port in the `spec.backendRefs.port` field when referencing a Backend. Although the port is defined in the Backend resource, explicitly setting it in the HTTPRoute may lead to a `BackendNotFound` condition. To prevent misconfiguration, rely solely on the port defined within the Backend specification.
  {{< /callout >}}

```yaml {linenos=table,hl_lines=[13,14,15,16],linenostart=1,filename="backend-httproute.yaml"}
apiVersion: gateway.networking.k8s.io/v1
kind: HTTPRoute
metadata:
  name: static-backend
  namespace: default
spec:
  parentRefs:
    - name: http
      namespace: kgateway-system
  hostnames:
    - static.example
  rules:
    - backendRefs:
      - name: json-backend
        kind: Backend
        group: gateway.kgateway.dev
      filters:
        - type: URLRewrite
          urlRewrite:
            hostname: jsonplaceholder.typicode.com
   EOF
```

For an example, see the [Static](/docs/traffic-management/destination-types/backends/static/) Backend guide.
