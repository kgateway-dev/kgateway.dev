---
title: Custom resources
weight: 30
next: /docs/about/policies
---

Learn how the {{< reuse "docs/snippets/product-name.md" >}} and {{< reuse "docs/snippets/k8s-gateway-api-name.md" >}} custom resources interact. 

## Custom resource overview

The following image illustrates how the {{< reuse "docs/snippets/product-name.md" >}} custom resources interact with the {{< reuse "docs/snippets/k8s-gateway-api-name.md" >}} custom resources to provide advanced routing, traffic management, security, resiliency, and integration capabilities. To learn more about each custom resource, see [{{< reuse "docs/snippets/k8s-gateway-api-name.md" >}} resources](#k8s) and [{{< reuse "docs/snippets/product-name.md" >}} resources](#kgateway).

{{< reuse-image src="img/gg-crs.svg" >}}

## Kubernetes Gateway API resources {#k8s}

Review the {{< reuse "docs/snippets/k8s-gateway-api-name.md" >}} resources that you use to set up gateway proxies and configure routing for your apps. 

For more information, see the [{{< reuse "docs/snippets/k8s-gateway-api-name.md" >}} introduction](https://gateway-api.sigs.k8s.io/#introduction). 

### Gateway and GatewayClass

The [Gateway](https://gateway-api.sigs.k8s.io/api-types/gateway/) custom resource is a network abstraction that defines a point of access at which traffic can be forwarded to a backend in a Kubernetes cluster. A Gateway defines the listeners that you want to open, including the ports, protocols, and hostnames that you want to listen on for incoming traffic. You can also specify how incoming, encrypted traffic is handled. For example, encrypted traffic can be terminated at the gateway or passed through to a backend in the cluster. 

To spin up a Gateway and manage its lifecycle, a gateway controller is used. The gateway controller is defined in the  [GatewayClass](https://gateway-api.sigs.k8s.io/api-types/gatewayclass/) resource and manages the underlying infrastructure to ensure that traffic to endpoints is routed accordingly. When you install {{< reuse "docs/snippets/product-name.md" >}}, a GatewayClass resource is automatically created that points to the {{< reuse "docs/snippets/product-name.md" >}} controller. For more information, see [GatewayClass](/docs/setup/default/#gatewayclass). 

### HTTPRoute and TCPRoute {#httproute}

To configure routing, the {{< reuse "docs/snippets/k8s-gateway-api-name.md" >}} provides several routing resources, such as an HTTPRoute and TCPRoute. These routes attach to a Gateway resource and define how incoming traffic is matched and forwarded to a backing destination.

* [HTTPRoute](https://gateway-api.sigs.k8s.io/api-types/httproute/): The most commonly used route resource, that configures traffic routing for HTTP and HTTPS traffic. 
* [TCPRoute](https://gateway-api.sigs.k8s.io/reference/spec/#gateway.networking.k8s.io/v1alpha2.TCPRoute): A resource to route TCP requests.

While the {{< reuse "docs/snippets/k8s-gateway-api-name.md" >}} provides the functionality for basic request matching, redirects, rewrites, and header manipulation, it is missing more complex traffic management, resiliency, and security features, such as transformations, fault injection, access logging, or route delegation. 

You can extend the {{< reuse "docs/snippets/k8s-gateway-api-name.md" >}} features by leveraging the [{{< reuse "docs/snippets/product-name.md" >}} policy custom resources](#policies). Policies allow you to apply intelligent traffic management, resiliency, and security standards to individual routes or all the routes that the Gateway serves.

### Kubernetes Services

Kubernetes Services expose Kubernetes pods within and outside a Kubernetes cluster so that other network endpoints can communicate with them. In the context of the Kubernetes Gateway API, the Kubernetes Service represents an app within the cluster that you want to route traffic to from outside the cluster. The Service is referenced in the HTTPRoute resource, including the port that you want to send traffic to. 

If traffic matches the conditions that are defined in the HTTPRoute, the Gateway forwards traffic to the Kubernetes Service that is referenced in the HTTPRoute. 

### ReferenceGrant

A [ReferenceGrant](https://gateway-api.sigs.k8s.io/api-types/referencegrant/) allows a Kubernetes Gateway API resource, such as an HTTPRoute, to reference resources that exist in other namespaces. For example, if you create an HTTPRoute resource in `namespace1`, but the Kubernetes Service or Backend that you want to route to is in `namespace2`, you must create a ReferenceGrant to allow communication between these resources.

{{% callout type="info" %}}
{{< reuse "docs/snippets/product-name-caps.md" >}} custom resources do not follow the same cross-namespace restrictions as the resources in the {{< reuse "docs/snippets/k8s-gateway-api-name.md" >}}. For example, access between a RouteOption resource in `namespace1` and an Backend resource in `namespace2` is allowed by default and does not require a ReferenceGrant. However, if you need to reference a {{< reuse "docs/snippets/product-name.md" >}} resource from a {{< reuse "docs/snippets/k8s-gateway-api-name.md" >}} resource, you must create a ReferenceGrant. 
{{% /callout %}}

## Kgateway resources {#kgateway}

Review the {{< reuse "docs/snippets/product-name.md" >}} resources that you use to bootstrap, configure, and customize your gateway proxy, and the policies that you can leverage to add additional traffic management, resiliency, and security capabilities to your gateway and routes. 

### GatewayParameters and Settings

When you create a Gateway resource, a default gateway proxy template is used to automatically spin up and bootstrap a gateway proxy deployment and service in your cluster. The template includes Envoy configuration that binds the gateway proxy deployment to the Gateway resource that you created. In addition, the settings in the GatewayParameters and Settings resources are used to configure the gateway proxy.

To learn more about the default gateway setup and how these resource interact with each other, see [Default gateway proxy setup](/docs/setup/default/). 


### Policies

While the {{< reuse "docs/snippets/k8s-gateway-api-name.md" >}} allows you to do simple routing, such as to match, redirect, or rewrite requests, you might want additional capabilities in your API gateway, such as fault injection, access logging, CORS, or CSRF. [Policies](/docs/about/policies/overview/) allow you to apply intelligent traffic management, resiliency, and security standards to individual routes or all the routes that the gateway serves. 

{{< reuse "docs/snippets/product-name-caps.md" >}} uses the following custom resources to attach policies to routes and gateway listeners: 

* [**DirectResponse**](/docs/traffic-management/direct-response/): Directly respond to incoming requests with a custom HTTP response code and body.
* [**ListenerPolicy**](/docs/about/policies/listeneroption/): Attach policies to one, multiple, or all gateway listeners.
* [**HTTPListenerPolicy**](/docs/about/policies/httplisteneroption/): Apply policies to one, multiple, or all HTTP and HTTPS listeners.
* [**RouteOption**](/docs/about/policies/routeoption/): Attach policies to one, multiple, or all routes in an HTTPRoute resource.
* [**VirtualHostOption**](/docs/about/policies/virtualhostoption/): Attach policies to the hosts on one, multiple, or all gateway listeners. 

### Backends

While you can route incoming traffic to a Kubernetes Service directly by referencing the Service in your HTTPRoute, you might want to add additional configuration to your service or point to endpoints outside your cluster. For example, you might want to route traffic to an AWS Lambda instance. You might also want to add settings to a Kubernetes Service, such as HTTP/2, traffic shadowing, or health check capabilities. 

You can use an [Backend](/docs/traffic-management/destination-types/backends/) resource to accomplish these tasks. Similar to using Kubernetes Services, you reference the Backend in your HTTPRoute resource. For more information about Backends, see [Backends](/docs/traffic-management/destination-types/backends/). 

