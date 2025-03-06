---
title: HTTPS redirect
weight: 441
description: Permanently redirect HTTP traffic to HTTPS. 
---

Permanently redirect HTTP traffic to HTTPS. 

For more information, see the [{{< reuse "docs/snippets/k8s-gateway-api-name.md" >}} documentation](https://gateway-api.sigs.k8s.io/api-types/httproute/#filters-optional).

## Before you begin

{{< reuse "docs/snippets/prereq.md" >}}

## Redirect HTTP traffic to HTTPS

1. Create an HTTP route for the httpbin app that you set up as part of the [Get started guide](/docs/quickstart/). In the following example, all HTTP requests are redirected to HTTPS, and a 301 HTTP response code is returned to the user. 
   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.networking.k8s.io/v1
   kind: HTTPRoute
   metadata:
     name: httpbin-https-redirect
     namespace: httpbin
     labels:
       example: httpbin-route
   spec:
     parentRefs:
       - name: http
         namespace: {{< reuse "docs/snippets/ns-system.md" >}}
     hostnames: 
       - redirect.example
     rules:
       - filters:
         - type: RequestRedirect
           requestRedirect:
             scheme: https
             statusCode: 301
   EOF  
   ```

   |Setting|Description|
   |--|--|
   |`spec.parentRefs.name`|The name and namespace of the gateway resource that serves the route. In this example, you use the gateway that you installed as part of the [Get started guide](/docs/quickstart). |
   |`spec.hostnames`| The hostname for which you want to apply the redirect.|
   |`spec.rules.filters.type`|The type of filter that you want to apply to incoming requests. In this example, the `RequestRedirect` is used.|
   |`spec.rules.filters.requestRedirect.scheme`|The type of redirect that you want to apply. The `https` scheme redirects all incoming traffic to HTTPS. |
   |`spec.rules.filters.requestRedirect.statusCode`|The HTTP status code that you want to return to the client in case of a redirect. For a permanent redirect, use the 301 HTTP status code.   |

2. Send a request to the httpbin app on the `redirect.example` domain. Verify that you get back a 301 HTTP response code and that your redirect location shows `https://redirect.example:8080/status/200`. 
   {{< tabs items="Cloud Provider LoadBalancer,Port-forward for local testing" >}}
   {{% tab %}}
   ```sh
   curl -vik http://$INGRESS_GW_ADDRESS:8080/status/200 -H "host: redirect.example"
   ```
   {{% /tab %}}
   {{% tab %}}
   ```sh
   curl -vik localhost:8080/status/200 -H "host: redirect.example"
   ```
   {{% /tab %}}
   {{< /tabs >}}

   Example output: 
   ```
   * Mark bundle as not supporting multiuse
   < HTTP/1.1 301 Moved Permanently
   HTTP/1.1 301 Moved Permanently
   < location: https://redirect.example:8080/status/200
   location: https://redirect.example:8080/status/200
   < date: Mon, 06 Nov 2023 01:48:12 GMT
   date: Mon, 06 Nov 2023 01:48:12 GMT
   < server: envoy
   server: envoy
   < content-length: 0
   content-length: 0
   ```


## Cleanup

{{< reuse "docs/snippets/cleanup.md" >}}
  
```sh
kubectl delete httproute httpbin-https-redirect -n httpbin
```