---
title: HTTP/1.0 and HTTP/0.9
weight: 60
description:
---

Configure your gateway proxy to accept older HTTP protocols. 

## About HTTP/1.0 and HTTP/0.9

By default, Envoy-based gateway proxy return a 426 Upgrade Required HTTP response code for HTTP/1.0 and HTTP/0.9 requests. HTTP/0.9 was a simple, rudimentary protocol that was introduced in 1991 and supported only the `GET` HTTP method. Other methods, such as `POST`, `PUT`, and `DELETE` were later introduced in HTTP/1.0. 

Both protocol versions are rarely used nowadays. However, some applications might still require support for these versions for backwards compatibililty. To allow the gateway proxy to accept these types of requests, you can create an HTTPListenerPolicy and attach it to your Gateway. 


## Before you begin

{{< reuse "docs/snippets/prereq-listeners.md" >}}

## Set up HTTP 1.0 support

1. Create an HTTPListenerPolicy with the `acceptHttp10` field. 
   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.kgateway.dev/v1alpha1
   kind: HTTPListenerPolicy
   metadata:
     name: accept-http10
     namespace: {{< reuse "docs/snippets/namespace.md" >}}
   spec:
     targetRefs:
     - group: gateway.networking.k8s.io
       kind: Gateway
       name: http
     acceptHttp10: true
   EOF
   ```

2. Port-forward the gateway proxy on port 19000 to open the Envoy admin interface. 
   ```sh
   kubectl port-forward deploy/http -n {{< reuse "docs/snippets/namespace.md" >}} 19000
   ```

3. Open the [Envoy admin interface](http://localhost:19000/config_dump) and look for the `http_protocol_options` filter in your Envoy filter chain. Then, verify that the `accept_http_10` field is set to `true`. 
   
   Example output: 
   ```console
   "http_protocol_options": {
             "accept_http_10": true
      }
   ```

## Cleanup 

{{< reuse "docs/snippets/cleanup.md" >}}

```sh
kubectl delete httplistenerpolicy accept-http10 -n {{< reuse "docs/snippets/namespace.md" >}}
```