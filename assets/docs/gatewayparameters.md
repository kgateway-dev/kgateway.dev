GatewayParameters is a {{< reuse "docs/snippets/product-name.md" >}} custom resource that specifies the configuration for the gateway proxies in your cluster. 

When you install {{< reuse "docs/snippets/product-name.md" >}}, a default GatewayParameters resource is automatically created for you. You can review its configuration by using the following command:  
```sh
kubectl get gatewayparameters kgateway -n {{< reuse "docs/snippets/ns-system.md" >}} -o yaml
```

To spin up new gateway proxies, the {{< reuse "docs/snippets/product-name.md" >}} controller uses a [gateway proxy template](#gatewayproxytemplate) and the configuration in the default GatewayParameters and [Settings](#settings) resources. You can change the default configuration for your gateway proxies by updating the respective values in the Gloo Gateway Helm chart. You can also create additional GatewayParameters resources to spin up different types of gateway proxies.

{{% callout type="info" %}}
Do not edit or change the default GatewayParameters resource directly. Always update the values in the Gloo Gateway Helm chart so that they persist between upgrades, or create your own GatewayParameters resource that holds your custom values. Note that you are responsible to maintain any GatewayParameters resources that you manually created.  
{{% /callout %}} 

For example, you might want to pair your gateway with a Network Load Balancer (NLB) instance in AWS. To properly pair and configure the gateway with an NLB, specific annotations on the gateway proxy are required. These annotations are not included in the default GatewayParameters resource. To add them, you can create a separate GatewayParameters resource where you add these annotations. For more customization options, see [Customize the gateway](/docs/setup/customize).