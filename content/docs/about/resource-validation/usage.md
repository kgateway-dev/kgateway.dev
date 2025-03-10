---
title: Test resources
weight: 20
description: Try out the resource validation capability in kgateway to check configuration before you apply it to your cluster.

---

You can use the Kubernetes [dry run capability](#dry-run) to verify your resource configuration or [send requests directly to the {{< reuse "docs/snippets/product-name.md" >}} validation API](#validation-api). 

{{% callout type="info" %}}
The information in this guide assumes that you enabled strict validation, including the rejection of resources that result in a `Warning` state. To enable these settings, update your {{< reuse "docs/snippets/product-name.md" >}} installation and include `--set gateway.validation.alwaysAcceptResources=false`, `--set gateway.validation.enabled=true`, and `--set gateway.validation.allowWarnings=false`. You can also edit the Settings resource directly. For more information, see [Enable strict resource validation](/docs/about/resource-validation/setup/#strict-validation). 
{{% /callout %}}

## Use the dry run capability in Kubernetes {#dry-run}

To test whether a YAML file is accepted by the validation webhook, you can use the `kubectl apply --dry-run=server` command as shown in the following examples.  

{{< tabs items="RouteOption,VirtualHostOption" >}}
{{% tab  %}}

Try to create a RouteOption with an invalid fault injection configuration and verify that your resource is denied by the validation API. The following example is missing the required HTTP status code field that is returned when the request is aborted. 
```yaml
kubectl apply -n httpbin --dry-run=server -f- <<EOF
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
   

Example output:
```console
Error from server: error when creating "STDIN": admission webhook "gloo.{{< reuse "docs/snippets/ns-system.md" >}}.svc" denied the request: resource incompatible with current Gloo snapshot: [Validating *v1.RouteOption failed: 1 error occurred:
* Validating *v1.RouteOption failed: validating *v1.RouteOption name:"faults"  namespace:"httpbin": 1 error occurred:
* Route Error: ProcessingError. Reason: *faultinjection.plugin: invalid abort status code '0', must be in range of [200,600). Route Name: 
```

{{% /tab %}}
{{% tab %}}

Try to create a VirtualHostOption resource with an invalid retry policy. In the following example, the `baseInterval` is greater than the `maxInterval`. Verify that the configuration is rejected.  
```yaml
kubectl apply --dry-run=server -f- <<EOF
apiVersion: gateway.kgateway.dev/v1alpha1
kind: VirtualHostOption
metadata:
  name: bad-retries
spec:
  targetRefs:
  - group: gateway.networking.k8s.io
    kind: Gateway
    name: http
    sectionName: http
  options:
    retries:
      retryOn: "5xx"
      retryBackOff:
        # An error is expected when the baseInterval is greater than the maxInterval
        baseInterval: "1s"
        maxInterval: "1ms"
EOF
```
   
Example output: 
```console
Error from server: error when creating "STDIN": admission webhook "gloo.{{< reuse "docs/snippets/ns-system.md" >}}.svc" denied the request: resource incompatible with current Gloo snapshot: [Validating *v1.VirtualHostOption failed: 1 error occurred:
  * Validating *v1.VirtualHostOption failed: validating *v1.VirtualHostOption name:"bad-retries"  namespace:"default": 1 error occurred:
  * VirtualHost Error: ProcessingError. Reason: invalid virtual host [vhost] while processing plugin basic_route: base interval: 1000 is > max interval: 1
```



{{% /tab %}}

{{< /tabs >}}

## Send requests to the validation API directly {#validation-api}

Send a curl request to the validation API to test your resource configurations. For an overview of the fields that you must include as part of your request, see [Validation API reference](#validation-api-reference). 

{{% callout type="info" %}}
If an empty response <code>{}</code> is returned from the validation API, you might need to add or remove a bracket from your request. This response is returned also if the wrong bracket type is used, such as when you used <code>{}</code> instead of <code>[]</code>. 
{{% /callout %}}
{{% callout type="info" %}}
The validation API currently assumes that all configuration that is sent to the API passes the Kubernetes object schema validation. For example, if your configuration contains valid {{< reuse "docs/snippets/product-name.md" >}} configuration, but you use an API version or API kind that does not exist in your cluster, the validation API logs a warning, but accepts the request. To ensure that your resource configuration passes the Kubernetes object schema validation, use the [dry run capability in Kubernetes](#dry-run) instead.
{{% /callout %}}

1. Port-forward the gloo service on port 8443. 
   ```sh
   kubectl -n {{< reuse "docs/snippets/ns-system.md" >}} port-forward service/gloo 8443:443
   ```

2. Send a request with your resource configuration to the {{< reuse "docs/snippets/product-name.md" >}} validation API. The following example shows successful and unsuccessful resource configuration validation for the RouteOption and VirtualHostOption resources.
   {{< tabs items="RouteOption,VirtualHostOption" >}}
   {{% tab %}}
   
   The following RouteOption resource configures an invalid fault injection policy that aborts 50% of all traffic. The configuration is missing an HTTP status code. 

   ```yaml
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
   ```

   </br>
   
   1. Send a request to the validation API and pass in the invalid RouteOption configuration. Verify that the configuration is rejected.
      ```sh
      curl -k -XPOST -d '{"request":{"uid":"1234","kind":{"group":"gateway.solo.io","version":"v1","kind":"RouteOption"},"resource":{"group":"","version":"","resource":""},"name":"faults","namespace":"httpbin","operation":"CREATE","userInfo":{},"object": { "apiVersion": "gateway.kgateway.dev/v1alpha1", "kind": "RouteOption", "metadata": { "name": "faults", "namespace": "httpbin" }, "spec": { "options": { "faults": { "abort": { "percentage": "50" } }}}}}}' \
      -H 'Content-Type: application/json' https://localhost:8443/validation 
      ```
      
      Example output: 
      ```console
      {"response":{"uid":"1234","allowed":false,"status":{"metadata":{},"message":"resource incompatible with current Gloo snapshot: [Validating *v1.RouteOption failed: 1 error occurred:\n\t* Validating *v1.RouteOption failed: validating *v1.RouteOption name:\"faults\"  namespace:\"httpbin\": 1 error occurred:\n\t* Route Error: ProcessingError. Reason: *faultinjection.plugin: invalid abort status code '0', must be in range of [200,600). Route Name: \n\n\n\n]","details":{"name":"faults","group":"gateway.solo.io","kind":"RouteOption","causes":[{"message":"Error Validating *v1.RouteOption failed: 1 error occurred:\n\t* Validating *v1.RouteOption failed: validating *v1.RouteOption name:\"faults\"  namespace:\"httpbin\": 1 error occurred:\n\t* Route Error: ProcessingError. Reason: *faultinjection.plugin: invalid abort status code '0', must be in range of [200,600). Route Name: \n\n\n\n"}]}}}}
      ```

   2. Add the HTTP status code field to the RouteOption configuration (`"httpStatus": "503"`). Verify that the configuration is accepted. 
      ```sh
      curl -k -XPOST -d '{"request":{"uid":"1234","kind":{"group":"gateway.solo.io","version":"v1","kind":"RouteOption"},"resource":{"group":"","version":"","resource":""},"name":"faults","namespace":"httpbin","operation":"CREATE","userInfo":{},"object": { "apiVersion": "gateway.kgateway.dev/v1alpha1", "kind": "RouteOption", "metadata": { "name": "faults", "namespace": "httpbin" }, "spec": { "options": { "faults": { "abort": { "percentage": "50", "httpStatus": "503" } }}}}}}' \
      -H 'Content-Type: application/json' https://localhost:8443/validation 
      ```

      Example output for successful validation:
      ```console
      {"response":{"uid":"1234","allowed":true}}
      ```


   {{% /tab %}}
   {{% tab  %}}
   
   The following VirtualHostOption resource configures an invalid retry policy that sets a `maxInterval` that is smaller than the `baseInterval`. 

   ```yaml
   apiVersion: gateway.kgateway.dev/v1alpha1
   kind: VirtualHostOption
   metadata:
     name: bad-retries
     namespace: httpbin
   spec:
     targetRefs:
     - group: gateway.networking.k8s.io
       kind: Gateway
       name: http
       sectionName: http
     options:
       retries:
         retryOn: "5xx"
         retryBackOff:
           # An error is expected when the maxInterval is smaller than the baseInterval
           baseInterval: "1s"
           maxInterval: "1ms"
   ```

   </br>
   
   1. Send a request to the validation API and pass in the invalid VirtualHostOption configuration. Verify that the configuration is rejected.
      ```sh
      curl -k -XPOST -d '{"request":{"uid":"1234","kind":{"group":"gateway.solo.io","version":"v1","kind":"VirtualHostOption"},"resource":{"group":"","version":"","resource":""},"name":"bad-retries","namespace":"httpbin","operation":"CREATE","userInfo":{},"object": { "apiVersion": "gateway.kgateway.dev/v1alpha1", "kind": "VirtualHostOption", "metadata": { "name": "bad-retries", "namespace": "httpbin" }, "spec": { "targetRefs": [{ "group": "gateway.networking.k8s.io", "kind": "Gateway", "name": "http", "sectionName": "http" }], "options": { "retries": { "retryOn": "5xx", "retryBackOff": { "baseInterval": "1s", "maxInterval":"1ms"} } }}}}}' \
      -H 'Content-Type: application/json' https://localhost:8443/validation 
      ```

      Example output:
      ```console
      {"response":{"uid":"1234","allowed":false,"status":{"metadata":{},"message":"resource incompatible with current Gloo snapshot: [Validating *v1.VirtualHostOption failed: 1 error occurred:\n\t* Validating *v1.VirtualHostOption failed: validating *v1.VirtualHostOption name:\"bad-retries\"  namespace:\"httpbin\": 1 error occurred:\n\t* VirtualHost Error: ProcessingError. Reason: invalid virtual host [vhost] while processing plugin basic_route: base interval: 1000 is \u003e max interval: 1\n\n\n\n]","details":{"name":"bad-retries","group":"gateway.solo.io","kind":"VirtualHostOption","causes":[{"message":"Error Validating *v1.VirtualHostOption failed: 1 error occurred:\n\t* Validating *v1.VirtualHostOption failed: validating *v1.VirtualHostOption name:\"bad-retries\"  namespace:\"httpbin\": 1 error occurred:\n\t* VirtualHost Error: ProcessingError. Reason: invalid virtual host [vhost] while processing plugin basic_route: base interval: 1000 is \u003e max interval: 1\n\n\n\n"}]}}}}%  
      ```
  
   2. Change the `maxInterval` to an invalid value, such as `5` (`"maxInterval":"5"`). This value is missing the time unit. Verify that the configuration is rejected. 
      ```sh
      curl -k -XPOST -d '{"request":{"uid":"1234","kind":{"group":"gateway.solo.io","version":"v1","kind":"VirtualHostOption"},"resource":{"group":"","version":"","resource":""},"name":"bad-retries","namespace":"httpbin","operation":"CREATE","userInfo":{},"object": { "apiVersion": "gateway.kgateway.dev/v1alpha1", "kind": "VirtualHostOption", "metadata": { "name": "bad-retries", "namespace": "httpbin" }, "spec": { "targetRefs": [{ "group": "gateway.networking.k8s.io", "kind": "Gateway", "name": "http", "sectionName": "http" }], "options": { "retries": { "retryOn": "5xx", "retryBackOff": { "baseInterval": "1s", "maxInterval":"5"} } }}}}}' \
      -H 'Content-Type: application/json' https://localhost:8443/validation
      ```
      
      Example output: 
      ```console
      {"response":{"uid":"1234","allowed":false,"status":{"metadata":{},"message":"resource incompatible with current Gloo snapshot: [1 error occurred:\n\t* could not unmarshal raw object: parsing resource from crd spec bad-retries in namespace httpbin into *v1.VirtualHostOption: bad Duration: time: missing unit in duration \"5\"\n\n]","details":{"name":"bad-retries","group":"gateway.solo.io","kind":"VirtualHostOption","causes":[{"message":"Error 1 error occurred:\n\t* could not unmarshal raw object: parsing resource from crd spec bad-retries in namespace httpbin into *v1.VirtualHostOption: bad Duration: time: missing unit in duration \"5\"\n\n"}]}}}}%  
      ```

   3. Change the `maxInterval` to a value that is greater than the `baseInterval`, such as `5s` (`"maxInterval":"5s"`). Verify that your configuration is now accepted. 
      ```sh
      curl -k -XPOST -d '{"request":{"uid":"1234","kind":{"group":"gateway.solo.io","version":"v1","kind":"VirtualHostOption"},"resource":{"group":"","version":"","resource":""},"name":"bad-retries","namespace":"httpbin","operation":"CREATE","userInfo":{},"object": { "apiVersion": "gateway.kgateway.dev/v1alpha1", "kind": "VirtualHostOption", "metadata": { "name": "bad-retries", "namespace": "httpbin" }, "spec": { "targetRefs": [{ "group": "gateway.networking.k8s.io", "kind": "Gateway", "name": "http", "sectionName": "http" }], "options": { "retries": { "retryOn": "5xx", "retryBackOff": { "baseInterval": "1s", "maxInterval":"5s"} } }}}}}' \
      -H 'Content-Type: application/json' https://localhost:8443/validation
      ```

      Example output:
      ```console
      {"response":{"uid":"1234","allowed":true}}%
      ```
   
   {{% /tab %}}
   {{< /tabs >}}

## Validation API reference {#validation-api-reference}

The {{< reuse "docs/snippets/product-name.md" >}} validation API is implemented as a validating admission webhook in Kubernetes with the following sample JSON structure:

```json
{
  "request": {
    "uid": "12345",
    "kind": {
      "group": "gateway.solo.io",
      "version": "v1",
      "kind": "RouteOption"
    },
    "resource": {
      "group": "",
      "version": "",
      "resource": ""
    },
    "name": "vs-dry-run",
    "namespace": "{{< reuse "docs/snippets/ns-system.md" >}}",
    "operation": "CREATE",
    "userInfo": {
      "username": "system:serviceaccount:kube-system:my-serviceaccount",
      "uid": "system:serviceaccount:kube-system:my-serviceaccount"
    },
    "object": {
      // The resource configuration that you want to validate in JSON format.
    }
  
```

|Parameter|Type|Required|Description|
|--|--|--|--|
|`request.uid`|String|No|A unique identifier for the validation request. You can use this field to find the validation output for a specific resource more easily.|
|`request.kind` |Object|Yes|Information about the type of Kubernetes object that is involved in the validation request. The following fields can be defined: <ul><li> `request.kind.group` (string): The API group of the resource that you want to validate, such as `gateway.solo.io`. </li><li>`request.kind.version` (string): The API version of the resource that you want to validate, such as `v1`. </li><li>`request.kind.kind` (string): The kind of resource that you want to validate, such as `RouteOption`. </li></ul> To find a list of supported group, version, and kind combinations, see the `rules` section in the {{< reuse "docs/snippets/product-name.md" >}} [validating admission webhook configuration](https://github.com/solo-io/gloo/blob/main/install/helm/gloo/templates/5-gateway-validation-webhook-configuration.yaml).|
|`request.resource`|Object|Yes|Information about the resource that is admitted to the webhook. In most cases, the resource defined in `request.kind` and `request.resource` is the same. They might differ only when changes in API versions or variations in resource naming were introduced, or if the resource that you admit belongs to a subresource. If this is the case, you must include the `request.resource` field in your request to the validation API. If `request.kind` and `request.resource` are the same, the `request.resource` section can be omitted. </br></br>  The following fields can be defined: <ul><li> `request.resource.group` (string): The API group of the resource that you admit to the validation API. </li><li>`request.resource.version` (string): The API version of the resource that you want to admit. </li><li>`request.resource.kind` (string): The type of resource that you want to admit. </li></ul> |
|`request.name`|String|No|The name of the resource that you want to validate.|
|`request.namespace`|String|No|The namespace where you want to create, update, or delete the resource. |
|`request.operation`|String|Yes|The operation in Kubernetes that you want to use for your resource. The operation that you can set depends on the resource that you want to validate. You can find supported operations in the `rules` section in the {{< reuse "docs/snippets/product-name.md" >}} [validating admission webhook configuration](https://github.com/solo-io/gloo/blob/main/install/helm/gloo/templates/5-gateway-validation-webhook-configuration.yaml).  |
|`request.userInfo`|Object|No|Information about the user that sends the validation request. The following fields can be provided: <ul><li>`request.userInfo.username` (string): The name of the user that sends the validation request, such as `my-serviceaccount`. </li><li>`request.userInfo.uid` (string): The unique identifier of the user. </li><li>`request.userInfo.groups` (array of strings): A list of groups that the user belongs to.</li></ul> 
|`request.object`|Object|Yes|The resource configuration that you want to validate, such as a RouteOption or VirtualHostOption, in JSON format. Refer to the [API reference](/reference/api) for more information about the fields that you can set for each resource.|

   
