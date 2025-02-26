---
title: Extract query parameters
weight: 50
description: Extract query parameters, transform them, and add them in to the response body. 
---

The following example walks you through how to use an Inja template to find specific query parameters in a request, extract the parameter values, and to add these values to specific response headers. 

## Before you begin

{{< reuse "docs/snippets/prereq.md" >}}

## Extract query parameters
   
1. Create a VirtualHostOption resource with your transformation rules. In the following example, you use a regular expression to find the `foo` and `bar` query parameters in the request path and to capture their values. Then, these values are added to the response headers `foo-response` and `bar-response`.  
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
             extractors:
               # This extracts the 'foo' query param to an extractor named 'foo'
               foo:
                 # The :path pseudo-header contains the URI
                 header: ':path'
                 # Use a nested capturing group to extract the query param
                 regex: '(.*foo=([^&]*).*)'
                 subgroup: 2
               # This extracts the 'bar' query param to an extractor named 'bar'
               bar:
                 # The :path pseudo-header contains the URI
                 header: ':path'
                 # Use a nested capturing group to extract the query param
                 regex: '(.*bar=([^&]*).*)'
                 subgroup: 2
             # Add two new headers with the values of the 'foo' and 'bar' extractions
             headers:
               foo-response:
                 text: '{{ foo }}'
               bar-response:
                 text: '{{ bar }}'
     targetRefs:
     - group: gateway.networking.k8s.io
       kind: Gateway
       name: http
       namespace: {{< reuse "docs/snippets/ns-system.md" >}}
   EOF
   ```

2. Send a request to the httpbin app and include the `foo` and `bar` query parameters. Verify that you get back a 200 HTTP response code and that the value of the `foo` and `bar` query parameters were added to the response headers `foo-response` and `bar-response`. 
   {{< tabs items="Cloud Provider LoadBalancer,Port-forward for local testing" >}}
   {{% tab %}}
   ```sh
   curl -vik http://$INGRESS_GW_ADDRESS:8080/anything?foo=foo-value&bar=bar-value \
    -H "host: www.example.com:8080" 
   ```
   {{% /tab %}}
   {{% tab %}}
   ```sh
   curl -vik localhost:8080/anything?foo=foo-value&bar=bar-value \
   -H "host: www.example.com" \
   ```
   {{% /tab %}}
   {{< /tabs >}}
   
   Example output:
   ```yaml {linenos=table,hl_lines=[4,5,7,8,15,16,18,19],linenostart=1}
   ...
   {
    "args": {
      "bar": [
        "bar-value"
      ],
      "foo": [
        "foo-value"
      ]
    },
    "headers": {
      "Accept": [
        "*/*"
      ],
      "Bar-Response": [
        "bar-value"
      ],
      "Foo-Response": [
        "foo-value"
      ],
      "Host": [
        "www.example.com:8080"
      ],
      "User-Agent": [
        "curl/7.77.0"
      ],
      "X-B3-Sampled": [
        "0"
      ],
      "X-B3-Spanid": [
        "5003b7987ed56d7f"
      ],
      "X-B3-Traceid": [
        "eac0a28ecb32b9e15003b7987ed56d7f"
      ],
      "X-Forwarded-Proto": [
        "http"
      ],
      "X-Request-Id": [
        "b43982a7-cdb5-4bab-9ce5-cba0cf4c2ae5"
      ]
    },
    "origin": "127.0.0.6:41223",
    "url": "http://www.example.com:8080/anything?foo=foo-value&bar=bar-value",
    "data": "",
    "files": null,
    "form": null,
    "json": null
   }
   ```
   
## Cleanup

{{< reuse "docs/snippets/cleanup.md" >}}

```sh
kubectl delete virtualhostoption transformation -n {{< reuse "docs/snippets/ns-system.md" >}}
```
   