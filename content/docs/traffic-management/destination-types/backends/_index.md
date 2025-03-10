---
title: Backends
weight: 20
prev: /docs/traffic-management/destination-types/kube-services
---


Use Backend resources to define a backing destination for a route that you want {{< reuse "docs/snippets/product-name.md" >}} to route to.

Backends can be compared to a [cluster](https://www.envoyproxy.io/docs/envoy/latest/api-v3/config/cluster/v3/cluster.proto) in Envoy terminology. Each Backend must define a type. Supported types include `static` and `kubernetes`. Each type is handled by a different plugin in {{< reuse "docs/snippets/product-name.md" >}}. For more information, see [Types](#types). 

Backends allow you to add additional configuration to instruct {{< reuse "docs/snippets/product-name.md" >}} how to handle the request to the backing destination. For example, you can define that the destination requires the requests to be sent with the HTTP/2 protocol or that you want requests to be load balanced by using a specific load balancing algorithm. To route to an Backend resource, you reference the Backend in the `backendRefs` section of your HTTPRoute, just like you do when routing to a Kubernetes service directly. For more information, see [Routing](#routing). 

You can manually create Backends or enable Backend discovery in {{< reuse "docs/snippets/product-name.md" >}} to automatically create Backends for any Kubernetes service that is created and discovered in the cluster. 

For more information, see the [Backend API reference](/docs/reference/api/upstream). 

## Types

Check out the following guides for examples on how to use the supported Backends types with {{< reuse "docs/snippets/product-name.md" >}}. 

{{< cards >}}
  {{< card link="static" title="Static IP address or hostname" >}}
  {{< card link="kubernetes" title="Kubernetes Service" >}}
  {{< card link="lambda" title="AWS Lambda" >}}
  {{< card link="ec2" title="AWS EC2 instance" >}}
  {{< card link="http2" title="HTTP/2" >}}
{{< /cards >}}

<!-- TODO supported backends

You can create Backends of type `static`, `kube`, `aws`, and `gcp`. 

{{% callout type="info" %}}
Backends of type `azure`, `consul`, `grpc`, `rest`, or `awsEc2` are not supported in {{< reuse "docs/snippets/product-name.md" >}} when using the {{< reuse "docs/snippets/k8s-gateway-api-name.md" >}}. You can use these types of Backends when using a gateway proxy that is configured for the {{< reuse "docs/snippets/product-name.md" >}} API. For more information, see [Destination types in the {{< reuse "docs/snippets/product-name.md" >}} ({{< reuse "docs/snippets/product-name.md" >}} API) documentation](https://docs.solo.io/gloo-edge/latest/guides/traffic_management/destination_types/).
{{% /callout %}}

Check out the following guides for examples on how to use Backends with {{< reuse "docs/snippets/product-name.md" >}}:  
* [Static](/traffic-management/destination-types/backends/static/)
* [Kubernetes service](/traffic-management/destination-types/backends/kubernetes/)
* [Google Cloud Run](/traffic-management/destination-types/backends/cloud-run/)
* [AWS Lambda](/traffic-management/destination-types/backends/lambda/)
* [HTTP/2](/traffic-management/destination-types/backends/http2/)

-->

<!--

### Static

Static Backends are the 

### Kubernetes
-->

## Discovery

{{< reuse "docs/snippets/discovery-about.md" >}}

To enable service discovery: 

1. Get the current values for your Helm chart. 
   ```sh
   helm get values kgateway -n {{< reuse "docs/snippets/ns-system.md" >}} -o yaml > kgateway.yaml
   open kgateway.yaml
   ```

2. In your Helm values file, enable service discovery. 
   ```yaml
   gloo:
     discovery:
       enabled: true
   ```

3. Upgrade your {{< reuse "docs/snippets/product-name.md" >}} installation to enable service discovery. 
   ```sh
   helm upgrade -n {{< reuse "docs/snippets/ns-system.md" >}} kgateway kgateway/kgateway\
   --values kgateway.yaml \
   --version {{< reuse "docs/versions/n-patch.md" >}} 
   ```
   
4. Review the Backend resources that are automatically created for the Kubernetes services that you have in your cluster. 
   ```sh
   kubectl get backends -n {{< reuse "docs/snippets/ns-system.md" >}}
   ```

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
        group: gloo.solo.io
      filters:
      - type: ExtensionRef
        extensionRef:
          group: gateway.solo.io
          kind: RouteOption
          name: rewrite
```

For an example, see the [Static](/docs/traffic-management/destination-types/backends/static/) Backend guide. 
