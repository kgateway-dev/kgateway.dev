---
title: Update response body
weight: 80
description: Learn how to return a customized response body and how replace specific values in the body.
next: /docs/resiliency/
---

Learn how to return a customized response body and how replace specific values in the body.

In this guide, you use the following methods to transform a JSON body:

* Directly access fields in the JSON body and inject them into a custom JSON body.
* Use the `replace_with_random` Inja function to replace specific patterns in the JSON body.

{{< callout >}}
{{< reuse "docs/snippets/proxy-kgateway.md" >}} {{< reuse "docs/snippets/agentgateway-capital.md" >}}
{{< /callout >}}

<!--TODO agentgateway transformations-->

## Before you begin

{{< reuse "docs/snippets/prereq.md" >}}

## Update response body

1. Send a request to the `json` endpoint of the httpbin app. The request returns a JSON body that you later transform.
   {{< tabs items="Cloud Provider LoadBalancer,Port-forward for local testing" tabTotal="2" >}}
   {{% tab tabName="Cloud Provider LoadBalancer" %}}
   ```sh
   curl -vi http://$INGRESS_GW_ADDRESS:8080/json \
    -H "host: www.example.com:8080" 
   ```
   {{% /tab %}}
   {{% tab tabName="Port-forward for local testing" %}}
   ```sh
   curl -vi localhost:8080/json \
   -H "host: www.example.com"
   ```
   {{% /tab %}}
   {{< /tabs >}}
   
   Example output:
   ```console
   {
     "slideshow": {
       "author": "Yours Truly",
       "date": "date of publication",
      "slides": [
         {
           "title": "Wake up to WonderWidgets!",
           "type": "all"
         },
         {
           "items": [
             "Why <em>WonderWidgets</em> are great",
             "Who <em>buys</em> WonderWidgets"
           ],
           "title": "Overview",
           "type": "all"
         }
       ],
       "title": "Sample Slide Show"
     }
   }
   ```

2. Create a {{< reuse "docs/snippets/trafficpolicy.md" >}} resource with your transformation rules: 
   * A new body is created in the response with the values of the `author`, `title`, and `slides` fields.
   * To extract the values, you use dot notation. Because the response is parsed as a JSON file, no extractors need to be defined. Instead, you can access the fields directly.   

   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: {{< reuse "docs/snippets/trafficpolicy-apiversion.md" >}}
   kind: {{< reuse "docs/snippets/trafficpolicy.md" >}}
   metadata:
     name: transformation
     namespace: httpbin
   spec:
     targetRefs:
     - group: gateway.networking.k8s.io
       kind: HTTPRoute
       name: httpbin
     transformation:
       response:
         body: 
           parseAs: AsJson
           value: '{"author": "{{ slideshow.author }}", "title": "{{ slideshow.title }}", "slides": "{{ slideshow.slides }}}'
   EOF
   ```
   
3. Send a request to the `json` endpoint of the httpbin app again. Verify that you see the transformed response body.
   {{< tabs items="Cloud Provider LoadBalancer,Port-forward for local testing" tabTotal="2" >}}
   {{% tab tabName="Cloud Provider LoadBalancer" %}}
   ```sh
   curl -vi http://$INGRESS_GW_ADDRESS:8080/json \
    -H "host: www.example.com:8080" 
   ```
   {{% /tab %}}
   {{% tab tabName="Port-forward for local testing" %}}
   ```sh
   curl -vi localhost:8080/json \
   -H "host: www.example.com"
   ```
   {{% /tab %}}
   {{< /tabs >}}
   
   Example output:
   ```console
   {"author": "Yours Truly", "title": "Sample Slide Show", "slides":
   "[{"title":"Wake up to WonderWidgets!","type":"all"},{"items":
   ["Why <em>WonderWidgets</em> are great","Who <em>buys</em> WonderWidgets"],
   "title":"Overview","type":"all"}]}
   ```

4. Update the {{< reuse "docs/snippets/trafficpolicy.md" >}} resource to replace the `all` pattern with a random string.

   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: {{< reuse "docs/snippets/trafficpolicy-apiversion.md" >}}
   kind: {{< reuse "docs/snippets/trafficpolicy.md" >}}
   metadata:
     name: transformation
     namespace: httpbin
   spec:
     targetRefs:
     - group: gateway.networking.k8s.io
       kind: HTTPRoute
       name: httpbin
     transformation:
       response:
         body: 
           parseAs: AsJson
           value: '{{ replace_with_random(body(), "all") }}'
   EOF
   ```

5. Send another request to the `json` endpoint of the httpbin app. Verify that every `all` value is replaced with a random string.
   {{< tabs items="Cloud Provider LoadBalancer,Port-forward for local testing" tabTotal="2" >}}
   {{% tab tabName="Cloud Provider LoadBalancer" %}}
   ```sh
   curl -vi http://$INGRESS_GW_ADDRESS:8080/json \
    -H "host: www.example.com:8080" 
   ```
   {{% /tab %}}
   {{% tab tabName="Port-forward for local testing" %}}
   ```sh
   curl -vi localhost:8080/json \
   -H "host: www.example.com"
   ```
   {{% /tab %}}
   {{< /tabs >}}
   
   Example output: 
   ```console {hl_lines=[8,16]}
   {
     "slideshow": {
       "author": "Yours Truly",
       "date": "date of publication",
       "slides": [
         {
           "title": "Wake up to WonderWidgets!",
           "type": "5pESMzYNtg8W9AG/eVZ13A"
         },
         {
           "items": [
             "Why <em>WonderWidgets</em> are great",
             "Who <em>buys</em> WonderWidgets"
           ],
           "title": "Overview",
           "type": "5pESMzYNtg8W9AG/eVZ13A"
         }
       ],
       "title": "Sample Slide Show"
     }
   }
   ```

## Cleanup

{{< reuse "docs/snippets/cleanup.md" >}}

```sh
kubectl delete {{< reuse "docs/snippets/trafficpolicy.md" >}} transformation -n httpbin
```