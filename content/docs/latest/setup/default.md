---
title: Default gateway proxy setup
weight: 10
next: /docs/setup/customize
---

Learn about the different kgateway and Kubernetes resources that make up your gateway proxy deployment.

## GatewayClass

The GatewayClass is a {{< reuse "docs/snippets/k8s-gateway-api-name.md" >}}-native resource that defines the controller that spins up and configures gateway proxies in your environment. 

When you install kgateway, two default GatewayClass resources are automatically created with the following configuration. 

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

The `kgateway.dev/kgateway` controller implements the {{< reuse "docs/snippets/k8s-gateway-api-name.md" >}} and provides an abstraction of the gateway's underlying infrastructure. The controller watches the resources in your cluster. When a Gateway resource is created that references this GatewayClass, the controller spins up an Envoy-based gateway proxy by using the configuration that is defined in the GatewayParameters resource. The controller also translates other resources, such as HTTPRoute, TrafficPolicy, HTTPListenerPolicy, and more, into valid Envoy configuration, and applies the configuration to the gateway proxies it manages. 

## Gateway proxy template

When you create a Gateway resource, a default [gateway proxy template](https://github.com/kgateway-dev/kgateway/blob/{{< reuse "docs/versions/github-branch.md" >}}/internal/kgateway/helm/kgateway/templates/gateway/proxy-deployment.yaml) is used to automatically spin up and bootstrap a gateway proxy deployment and service in your cluster. The template includes Envoy configuration that binds the gateway proxy deployment to the Gateway resource that you created. In addition, the settings in the [GatewayParameters](#gatewayparameters) resource are used to configure the gateway proxy. 

The resulting gateway proxy is managed for you and its configuration is automatically updated based on the settings in the GatewayParameters resource. To publicly expose the gateway proxy deployment, a service of type LoadBalancer is created for you. Depending on the cloud provider that you use, the LoadBalancer service is assigned a public IP address or hostname that you can use to reach the gateway. To expose an app on the gateway, you must create an HTTPRoute resource and define the matchers and filter rules that you want to apply before forwarding the request to the app in your cluster. You can review the [Get started](/docs/quickstart/), [traffic management](/docs/traffic-management/), [security](/docs/security/), and [resiliency](/docs/resiliency/) guides to find examples for how to route and secure traffic to an app. 

You can change the default configuration of your gateway proxy by creating custom GatewayParameters resources, or updating the default GatewayParameters values in your kgateway Helm chart. If you change the values in the Helm chart, kgateway automatically applies the changes to the default GatewayParameters resources. 

{{< callout type="info" >}}
Do not edit or change the default GatewayParameters resource directly. Always update the values in the kgateway Helm chart so that they persist between upgrades.
{{< /callout >}} 

If you do not want to use the default gateway proxy template to bootstrap your proxies, you can choose to create a self-managed gateway. With self-managed gateways, you are responsible for defining the proxy deployment template that you want to bootstrap your proxies with. For more information, see [Self-managed gateways (BYO)](/docs/setup/customize/selfmanaged/).

## GatewayParameters 

{{< reuse "docs/gatewayparameters.md" >}}
