---
title: Enable resource validation
weight: 15
prev: /docs/about/resource-validation
---

Enable or disable resource validation in {{< reuse "docs/snippets/product-name.md" >}} and view the current alidating admission webhook configuration.

## View the current validating admission webhook configuration

You can check whether strict or permissive validation is enabled in your {{< reuse "docs/snippets/product-name.md" >}} installation by checking the Settings resource. 

1. Get the details of the default settings resource. 
   ```sh
   kubectl get settings default -n {{< reuse "docs/snippets/ns-system.md" >}} -o yaml
   ```

2. In your CLI output, find the `spec.gateway.validation.alwaysAccept` setting.
    * If set to `true`, permissive mode is enabled in your {{< reuse "docs/snippets/product-name.md" >}} setup and invalid Gloo resources are only logged, but not rejected.
    * If set to `false`, strict validation mode is enabled and invalid resource configuration is rejected before being applied in the cluster.
    * If `allowWarnings=false` is set alongside `alwaysAccept=false`, resources that result in a `Warning` status are also rejected. 

## Enable strict resource validation {#strict-validation}

Configure the validating admission webhook to reject invalid {{< reuse "docs/snippets/product-name.md" >}} custom resources before they are applied in the cluster. 

1. Enable strict resource validation. Resource validation is enabled by using the Settings resource in {{< reuse "docs/snippets/product-name.md" >}}. You can update the Settings resource by editing it directly or by enabling it in your {{< reuse "docs/snippets/product-name.md" >}} Helm installation. 
   {{< tabs items="Update the Settings resource,Update your installation" >}}
   {{% tab %}}
   
   Edit the Settings resource directly. Note that manually editing the Settings resource does not change the resource validation setting in the Helm installation. Because of that, this setting gets overwritten when you upgrade your Helm installation. 
   
   1. Edit the default Settings resource. 
      ```sh
      kubectl edit settings default -n {{< reuse "docs/snippets/ns-system.md" >}}
      ```
      
   2. In your Settings resource, set `spec.gateway.validation.alwaysAccept=false` to enable strict resource validation. 
      ```yaml {hl_lines=[9]}
      ...
      spec:
        gateway:
          enableGatewayController: true
          isolateVirtualHostsBySslConfig: false
          readGatewaysFromAllNamespaces: false
          validation:
            allowWarnings: true
            alwaysAccept: false
            disableTransformationValidation: false
            proxyValidationServerAddr: gloo:9988
            serverEnabled: true
            validationServerGrpcMaxSizeBytes: 104857600
            warnRouteShortCircuiting: false
      ```
   {{% /tab %}}
   {{% tab  %}}
   1. Get the current values for your Helm chart.
      ```sh
      helm get values kgateway -n {{< reuse "docs/snippets/ns-system.md" >}} -o yaml > kgateway.yaml
      open kgateway.yaml
      ```
   2. In your Helm values file, enable strict resource validation.
      ```yaml
      gateway:
        validation:
          enabled: true
          alwaysAcceptResources: false    
      ```
      
      {{% callout type="info" %}}
To also reject {{< reuse "docs/snippets/product-name.md" >}} custom resources that result in a `Warning` status, include `gateway.validation.allowWarnings: false`.
      {{% /callout %}}
    
   3. Upgrade your installation. 
      ```sh
      helm upgrade -n {{< reuse "docs/snippets/ns-system.md" >}} kgateway kgateway/kgateway \
       --values kgateway.yaml \
       --version {{< reuse "docs/versions/n-patch.md" >}}
      ```
   
   {{% /tab %}}
   
   {{< /tabs >}}


2. Verify that the validating admission webhook is enabled. 
   1. Create a RouteOption resource with an invalid fault injection configuration. The following example aborts 50% of all incoming requests. However, no HTTP status code is defined. 
      ```yaml
      kubectl apply -n httpbin -f- <<EOF
      apiVersion: gateway.kgateway.dev/v1alpha1
      kind: RouteOption
      metadata:
        name: faults
        namespace: httpbin
      spec:
        options:
          faults:
            abort:
              percentage: 50
              # httpStatus: 503
      EOF
      ```

   2. Verify that the RouteOption resource is rejected. You see an error message similar to the following.
      ```
      Error from server: error when creating "STDIN": admission webhook "gloo.{{< reuse "docs/snippets/ns-system.md" >}}.svc" denied the request: resource incompatible with current Gloo snapshot: [Validating *v1.RouteOption failed: 1 error occurred:
	  * Validating *v1.RouteOption failed: validating *v1.RouteOption name:"faults"  namespace:"httpbin": 1 error occurred:
	  * Route Error: ProcessingError. Reason: *faultinjection.plugin: invalid abort status code '0', must be in range of [200,600). Route Name: 
      ```

      {{< callout type="info" >}}
      You can also use the validating admission webhook by running the <code>kubectl apply --dry-run=server</code> command to test your Gloo configuration before you apply it to your cluster. For more information, see <a href="/about/rersource-validation/usage/">Test resource configurations</a>. 
      {{< /callout >}}

## Disable resource validation

Because the validation admission webhook is set up automatically in {{< reuse "docs/snippets/product-name.md" >}}, a `ValidationWebhookConfiguration` resource is created in your cluster. You can disable the webhook, which prevents the `ValidationWebhookConfiguration` resource from being created. When validation is disabled, any Gloo resources that you create in your cluster are translated to Envoy proxy config, even if the config has errors or warnings. 

To disable validation, use the following `--set` options during your Helm installation.

```sh
--set gateway.enabled=false
--set gateway.validation.enabled=false
--set gateway.validation.webhook.enabled=false
```




