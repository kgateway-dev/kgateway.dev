Learn about the different {{< reuse "docs/snippets/kgateway.md" >}} and Kubernetes resources that make up your gateway proxy deployment.

## GatewayClass

The GatewayClass is a {{< reuse "docs/snippets/k8s-gateway-api-name.md" >}}-native resource that defines the controller that spins up and configures gateway proxies in your environment. 

When you install {{< reuse "docs/snippets/kgateway.md" >}}, the following GatewayClass resources are automatically created with the following configuration. 

{{< reuse "docs/snippets/class-setup.md" >}}

## Gateway proxy template

When you create a Gateway resource, a default gateway proxy template for {{% conditional-text include-if="envoy" %}}[Envoy](https://github.com/kgateway-dev/kgateway/blob/{{< reuse "docs/versions/github-branch.md" >}}/internal/kgateway/helm/kgateway/templates/gateway/proxy-deployment.yaml){{% /conditional-text %}}{{% conditional-text include-if="agentgateway" %}}[{{< reuse "docs/snippets/agentgateway.md" >}}](https://github.com/kgateway-dev/kgateway/blob/main/internal/kgateway/helm/kgateway/templates/gateway/agent-gateway-deployment.yaml){{% /conditional-text %}} proxies is used to automatically spin up and bootstrap a gateway proxy deployment and service in your cluster. The template includes {{< conditional-text include-if="envoy" >}}Envoy{{< /conditional-text >}}{{< conditional-text include-if="agentgateway" >}}agentgateway{{< /conditional-text >}} configuration that binds the gateway proxy deployment to the Gateway resource that you created. In addition, the settings in the [{{< reuse "docs/snippets/gatewayparameters.md" >}}](#gatewayparameters) resource are used to configure the gateway proxy. 

The resulting gateway proxy is managed for you and its configuration is automatically updated based on the settings in the GatewayParameters resource. To publicly expose the gateway proxy deployment, a service of type LoadBalancer is created for you. Depending on the cloud provider that you use, the LoadBalancer service is assigned a public IP address or hostname that you can use to reach the gateway. To expose an app on the gateway, you must create an HTTPRoute resource and define the matchers and filter rules that you want to apply before forwarding the request to the app in your cluster. You can review the [Get started]({{< link-hextra path="/quickstart/" >}}), [traffic management]({{< link-hextra path="/traffic-management/" >}}), [security]({{< link-hextra path="/security/" >}}), and [resiliency]({{< link-hextra path="/resiliency/" >}}) guides to find examples for how to route and secure traffic to an app. 

You can change the default configuration of your gateway proxy by creating custom {{< reuse "docs/snippets/gatewayparameters.md" >}} resources, or updating the default {{< reuse "docs/snippets/gatewayparameters.md" >}} values in your {{< reuse "docs/snippets/kgateway.md" >}} Helm chart. If you change the values in the Helm chart, {{< reuse "docs/snippets/kgateway.md" >}} automatically applies the changes to the default {{< reuse "docs/snippets/gatewayparameters.md" >}} resources. 

{{< callout type="info" >}}
Do not edit or change the default {{< reuse "docs/snippets/gatewayparameters.md" >}} resource directly. Always update the values in the {{< reuse "docs/snippets/kgateway.md" >}} Helm chart so that they persist between upgrades.
{{< /callout >}} 

{{% conditional-text include-if="envoy" %}}
If you do not want to use the default gateway proxy template to bootstrap your proxies, you can choose to create a self-managed gateway. With self-managed gateways, you are responsible for defining the proxy deployment template that you want to bootstrap your proxies with. For more information, see [Self-managed gateways (BYO)](../selfmanaged/).
{{% /conditional-text %}}

## {{< reuse "docs/snippets/gatewayparameters.md" >}}

{{< reuse "docs/snippets/gatewayparameters-about.md" >}}

## Reserved ports

{{< reuse "docs/snippets/reserved-ports.md" >}}