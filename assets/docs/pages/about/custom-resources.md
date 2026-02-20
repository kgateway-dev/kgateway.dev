Learn about the custom resources that make up {{< reuse "/docs/snippets/kgateway.md" >}} and how they interact with each other. 

## Custom resource overview

{{< reuse "docs/snippets/cr-ov.md" >}}

<!--Source https://app.excalidraw.com/s/AKnnsusvczX/1HkLXOmi9BF-->

## Kubernetes Gateway API resources {#k8s}

Review the {{< reuse "docs/snippets/k8s-gateway-api-name.md" >}} resources that you use to set up gateway proxies and configure routing for your apps. 

For more information, see the [{{< reuse "docs/snippets/k8s-gateway-api-name.md" >}} introduction](https://gateway-api.sigs.k8s.io/#introduction). 

### Gateway and GatewayClass

The [Gateway](https://gateway-api.sigs.k8s.io/api-types/gateway/) custom resource is a network abstraction that defines a point of access at which traffic can be forwarded to a backend in a {{< gloss "Cluster (Kubernetes)" >}}Kubernetes cluster{{< /gloss >}}. A Gateway defines the listeners that you want to open, including the ports, protocols, and hostnames that you want to listen on for incoming traffic. You can also specify how incoming, encrypted traffic is handled. For example, encrypted traffic can be terminated at the gateway or passed through to a backend in the cluster. 

To spin up a Gateway and manage its lifecycle, a gateway controller is used. The gateway controller is defined in the  [GatewayClass](https://gateway-api.sigs.k8s.io/api-types/gatewayclass/) resource and manages the underlying infrastructure to ensure that traffic to endpoints is routed accordingly. When you install kgateway, a GatewayClass resource is automatically created that points to the kgateway controller. For more information, see [GatewayClass]({{< link-hextra path="/setup/default/#gatewayclass" >}}). 

### HTTPRoute and TCPRoute {#httproute}

To configure routing, the {{< reuse "docs/snippets/k8s-gateway-api-name.md" >}} provides several routing resources, such as an HTTPRoute and TCPRoute. These routes attach to a Gateway resource and define how incoming traffic is matched and forwarded to a backing destination.

* [HTTPRoute](https://gateway-api.sigs.k8s.io/api-types/httproute/): The most commonly used route resource, that configures traffic routing for HTTP and HTTPS traffic. 
* [TCPRoute](https://gateway-api.sigs.k8s.io/reference/spec/#gateway.networking.k8s.io/v1alpha2.TCPRoute): A resource to route TCP requests.

While the {{< reuse "docs/snippets/k8s-gateway-api-name.md" >}} provides the functionality for basic request matching, redirects, rewrites, and header manipulation, it is missing more complex traffic management, resiliency, and security features, such as transformations, access logging, or route delegation. 

You can extend the {{< reuse "docs/snippets/k8s-gateway-api-name.md" >}} features by leveraging the [kgateway-native policy custom resources](#policies). Policies allow you to apply intelligent traffic management, resiliency, and security standards to an HTTPRoute or Gateway. 

### Kubernetes Services

Kubernetes Services expose Kubernetes pods within and outside a Kubernetes cluster so that other network endpoints can communicate with them. In the context of the Kubernetes Gateway API, the Kubernetes Service represents an app within the cluster that you want to route traffic to from outside the cluster. The Service is referenced in the HTTPRoute resource, including the port that you want to send traffic to. 

If traffic matches the conditions that are defined in the HTTPRoute, the Gateway forwards traffic to the Kubernetes Service that is referenced in the HTTPRoute. 

### ReferenceGrant

A [ReferenceGrant](https://gateway-api.sigs.k8s.io/api-types/referencegrant/) allows a Kubernetes Gateway API resource, such as an HTTPRoute, to reference resources that exist in other namespaces. For example, if you create an HTTPRoute resource in `namespace1`, but the Kubernetes Service or Backend that you want to route to is in `namespace2`, you must create a ReferenceGrant to allow communication between these resources.

<!--

{{< callout type="info" >}}
Kgateway custom resources do not follow the same cross-namespace restrictions as the resources in the {{< reuse "docs/snippets/k8s-gateway-api-name.md" >}}. For example, access between a TrafficPolicy resource in `namespace1` and a Backend resource in `namespace2` is allowed by default and does not require a ReferenceGrant. However, if you need to reference a kgateway resource from a {{< reuse "docs/snippets/k8s-gateway-api-name.md" >}} resource, you must create a ReferenceGrant. 
{{< /callout >}}-->

## Kgateway resources {#kgateway}

Review the kgateway resources that you use to bootstrap, configure, and customize your gateway proxy, and the policies that you can leverage to add additional traffic management, resiliency, and security capabilities to your gateway and routes. 

### GatewayExtensions

A {{< gloss "Gateway Extension" >}}GatewayExtension{{< /gloss >}} is a {{< reuse "/docs/snippets/kgateway.md" >}} Custom Resource that serves as a configuration bridge between {{< reuse "/docs/snippets/kgateway.md" >}} and external services that extend a Gateway's functionality. These external services provide additional capabilities like authentication (`extAuth`), rate limiting (`rateLimit`), and request processing (`extProc`). TrafficPolicies can then refer to the GatewayExtension with the external service that the policy needs to be enforced. For more information, see the [API docs]({{< link-hextra path="/reference/api/#gatewayextension" >}}).

### {{< reuse "docs/snippets/gatewayparameters.md" >}}

When you create a Gateway resource, a [default gateway proxy template](https://github.com/kgateway-dev/kgateway/blob/{{< reuse "docs/versions/github-branch.md" >}}{{< reuse "docs/versions/github-kgateway-deployment.md" >}}) is used to automatically spin up and bootstrap a gateway proxy deployment and service in your cluster. The template includes Envoy configuration that binds the gateway proxy deployment to the Gateway resource that you created. In addition, the settings in the {{< gloss "GatewayParameters" >}}{{< reuse "docs/snippets/gatewayparameters.md" >}}{{< /gloss >}} resource are used to configure the gateway proxy.

To learn more about the default gateway setup and how these resource interact with each other, see [Default gateway proxy setup]({{< link-hextra path="/setup/default/" >}}). 

### Policies

While the {{< reuse "docs/snippets/k8s-gateway-api-name.md" >}} allows you to do simple routing, such as to match, redirect, or rewrite requests, you might want additional capabilities in your API gateway, such as access logging or transformations. [Policies]({{< link-hextra path="/about/policies/" >}}) allow you to apply intelligent traffic management, resiliency, and security standards to HTTPRoutes or Gateways.

Kgateway uses the following custom resources to attach policies to routes and gateway listeners: 

* [**DirectResponse**]({{< link-hextra path="/traffic-management/direct-response/" >}}): Directly respond to incoming requests with a custom HTTP response code and body.
* [**HTTPListenerPolicy**]({{< link-hextra path="/about/policies/httplistenerpolicy/" >}}): Apply policies to all HTTP and HTTPS listeners.
* [**TrafficPolicy**]({{< link-hextra path="/about/policies/trafficpolicy/" >}}): Attach policies to routes in an HTTPRoute resource.

### {{< reuse "docs/snippets/backend.md" >}}s

For workloads within your cluster, you can route incoming traffic to their Kubernetes Service. But what if you have external services such as static hostnames or AWS Lambda functions that you want to route traffic to?

You can use a {{< reuse "docs/snippets/backend.md" >}} resource to accomplish this task. Similar to using Kubernetes Services, you reference the {{< reuse "docs/snippets/backend.md" >}} in your HTTPRoute resource. For more information, see [{{< reuse "docs/snippets/backend.md" >}}s]({{< link-hextra path="/traffic-management/destination-types/backends/" >}}).
