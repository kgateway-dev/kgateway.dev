---
title: Backends
weight: 20
prev: /docs/traffic-management/destination-types/kube-services
---

Use a Backend resource to define a backing destination that you want {{< reuse "docs/snippets/product-name.md" >}} to route to. For more information, see the [Backend API docs](/docs/reference/api/upstream). 

## About

To help you think about Backends, consider how they relate to the underlying open source projects that you might be familiar with:

* Envoy: The {{< reuse "docs/snippets/product-name.md" >}} Backend can be compared to a [cluster](https://www.envoyproxy.io/docs/envoy/latest/api-v3/config/cluster/v3/cluster.proto) in Envoy terminology.
* {{< reuse "docs/snippets/k8s-gateway-api-name.md" >}}: The {{< reuse "docs/snippets/product-name.md" >}} Backend is a backend destination that Gateway API routing resources refer to through `backendRefs` [extension points](https://gateway-api.sigs.k8s.io/concepts/api-overview/#extension-points).
* Gloo Edge API: The {{< reuse "docs/snippets/product-name.md" >}} Backend is similar to a [Gloo Upstream](https://docs.solo.io/gloo-edge/latest/guides/traffic_management/destination_types/), but with several important differences as follows: 
  * Destination-only, no policy: The Gloo Upstream combines both routing destination and policy rules. Unlike the Gloo Upstream, the {{< reuse "docs/snippets/product-name.md" >}} Backend sets up only routing destination. Routing policy rules, such as TLS connectivity or load balancing behavior, must be set up with a separate {{< reuse "docs/snippets/product-name.md" >}} resource, such as BackendTlsPolicy. 
  * No discovery: {{< reuse "docs/snippets/product-name.md" >}} does not automatically discover and create Backends for the Kubernetes Services in your cluster.

Each {{< reuse "docs/snippets/product-name.md" >}} Backend must define a type, such as `ai` or `static`. Each type is handled by a different plugin in {{< reuse "docs/snippets/product-name.md" >}}. For more information, see [Types](#types). 

To route to an Backend resource, you reference the Backend in the `backendRefs` section of your HTTPRoute, just like you do when routing to a Kubernetes service directly. For more information, see [Routing](#routing).

## Types

Check out the following guides for examples on how to use the supported Backends types with {{< reuse "docs/snippets/product-name.md" >}}. 

{{< cards >}}
  {{< card link="static" title="Static IP address or hostname" >}}
  {{< card link="lambda" title="AWS Lambda" >}}
  {{< card link="ec2" title="AWS EC2 instance" >}}
{{< /cards >}}

## Routing

You can route to an Backend by simply referencing that Backend in the `backendRefs` section of your HTTPRoute resource as shown in the following example. Note that if your Backend and HTTPRoute resources exist in different namespaces, you must create a Kubernetes ReferenceGrant resource to allow the HTTPRoute to access the Backend.

{{< callout type="warning" >}}
Do not specify a port in the `spec.backendRefs.port` field when referencing your Backend. The port is defined in your Backend resource and ignored if set on the HTTPRoute resource.
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
    namespace: {{< reuse "docs/snippets/ns-system.md" >}}
  hostnames:
    - static.example
  rules:
    - backendRefs:
      - name: json-backend
        kind: Backend
        group: gateway.kgateway.dev
      filters:
      - type: ExtensionRef
        extensionRef:
          group: gateway.kgateway.dev
          kind: RoutePolicy
          name: rewrite
```

For an example, see the [Static](/docs/traffic-management/destination-types/backends/static/) Backend guide. 
