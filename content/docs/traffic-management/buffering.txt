---
linkTitle: "Buffering"
title: Buffering
weight: 70
next: /docs/traffic-management/header-control
prev: /docs/traffic-management/route-delegation
---

Fine-tune connection speeds for read and write operations. 

## About read and write buffer limits

By default, {{< reuse "docs/snippets/product-name.md" >}} is set up with 1MiB of request read and write buffer for each gateway listener. For large requests that must be buffered and that exceed the default buffer limit, {{< reuse "docs/snippets/product-name.md" >}} either disconnects the connection to the downstream service if headers were already sent, or returns a 500 HTTP response code. To make sure that large requests can be sent and received, you can specify the maximum number of bytes that can be buffered between the gateway and the downstream service.

## Before you begin

{{< reuse "docs/snippets/prereq.md" >}}

## Set up connection buffer limits

1. Create a ListenerPolicy resource to define your connection buffer limit rules. 
   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.kgateway.dev/v1alpha1
   kind: ListenerPolicy
   metadata:
     name: bufferlimits
     namespace: {{< reuse "docs/snippets/ns-system.md" >}}
   spec:
     targetRef:
       group: gateway.networking.k8s.io
       kind: Gateway
       name: http
     perConnectionBufferLimitBytes: 10485760
   EOF
   ```

2. Verify that your configuration is applied by reviewing the Envoy configuration. 
   1. Port forward the `gloo-gateway-http` deployment on port 19000. 
      ```sh
      kubectl port-forward deploy/http -n {{< reuse "docs/snippets/ns-system.md" >}} 19000 & 
      ```
   2. Open the `config_dump` endpoint. 
      ```sh
      open http://localhost:19000/config_dump
      ```
   3. Look for the `"per_connection_buffer_limit_bytes": 10485760` string in your Envoy configuration. 
   

## Cleanup

{{< reuse "docs/snippets/cleanup.md" >}}

```sh
kubectl delete listenerpolicy bufferlimits -n {{< reuse "docs/snippets/ns-system.md" >}}
```