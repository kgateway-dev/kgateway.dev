---
title: Add headers to body
weight: 60
description: Use extractors to capture request header values and add those values to the body. 
---

The following example walks you through how to use extractors to extract request header values by using regular expressions. The captured header values are then added to the response body by using the `mergeExtractorsToBody` setting. You can use the extractors to also indicate where you want to place the request header values in the body. 

## Before you begin

{{< reuse "docs/snippets/prereq.md" >}}

## Add header values to the response body
   
1. Create a VirtualHostOption resource with your transformation rules. In the following example, you extract the `root` and `nested` request headers and add them to the response body by using the `mergeExtractorsToBody` setting. The dot notation that you use for the extractor names determines the placement of the header in the body. For example, if no dot notation is used, such as in `root`, the header is added to the body's root level. If dot notation is used, such as in `payload.nested`, the extractor is added under the `payload.nested` field. 
   ```yaml
   kubectl apply -n {{< reuse "docs/snippets/ns-system.md" >}} -f- <<EOF
   apiVersion: gateway.kgateway.dev/v1alpha1
   kind: VirtualHostOption
   metadata:
     name: transformation
     namespace: {{< reuse "docs/snippets/ns-system.md" >}}
   spec:
     options:
       transformations:
         requestTransformation:
           transformationTemplate:
             # Merge the specified extractors to the request body
             mergeExtractorsToBody: {}
             extractors:
               # The name of this attribute determines where the value will be nested in the body. 
               # Because no dots are specified, such as root.nested, the root header value is added to the body's root level. 
               root:
                 # Name of the header to extract
                 header: 'root'
                 # Regex to apply to it. This value is required and is configured to capture the entire header. 
                 regex: '.*'
               # The name of this attribute determines where the value will be nested in the body. 
               # Because dot notation is used, the nested header is placed under the placeholder.nested field in the body. 
               payload.nested:
                 # Name of the header to extract
                 header: 'nested'
                 # Regex to apply to it. This value is required and is configured to capture the entire header.
                 regex: '.*'
     targetRefs:
     - group: gateway.networking.k8s.io
       kind: Gateway
       name: http
       namespace: {{< reuse "docs/snippets/ns-system.md" >}}
   EOF
   ```

2. Send a request to the httpbin app and include the `root` and `nested` request headers. Verify that you get back a 200 HTTP response code and that the value of the `root` header is added to the body's root level, and that the `nested` header value is added under the `payload.nested` field in your response. 
   {{< tabs items="Cloud Provider LoadBalancer,Port-forward for local testing" >}}
   {{% tab %}}
   ```sh
   curl -X POST -H "host: www.example.com:8080" \
   -H "Content-Type: application/json" \
   -H "root: root-val" \
   -H "nested: nested-val" http://$INGRESS_GW_ADDRESS:8080/post -d @data.json | jq
   ```
   {{% /tab %}}
   {{% tab %}}
   ```sh
   curl -X POST localhost:8080/post \
   -H "host: www.example.com" \
   -H "Content-Type: application/json" \
   -H "root: root-val" \
   -H "nested: nested-val" -d @data.json | jq
   ```
   {{% /tab %}}
   {{< /tabs >}}
   
   Example output: 
   ```yaml {linenos=table,hl_lines=[3,4,6],linenostart=1}
   ...
   "json": {
    "payload": {
      "nested": "nested-val"
    },
    "root": "root-val"
   }
   ```
   
## Cleanup

{{< reuse "docs/snippets/cleanup.md" >}}

```sh
kubectl delete virtualhostoption transformation -n {{< reuse "docs/snippets/ns-system.md" >}}
```
   