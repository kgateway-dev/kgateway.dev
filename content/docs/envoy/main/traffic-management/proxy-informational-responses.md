---
title: Proxy informational responses
description: Forward HTTP 100 Continue requests upstream and proxy informational responses back to downstream clients.
weight: 15
---

Configure the gateway proxy to forward HTTP requests with an `Expect: 100-continue` header to the upstream service. When the upstream service sends a `100 Continue` response, the gateway proxy returns that response to the downstream client instead of handling the exchange locally.

Use this configuration when a client and backend rely on end-to-end HTTP informational responses, such as `100 Continue` or `103 Early Hints`.

## Before you begin {#before-you-begin}

{{< reuse "kgw-docs/snippets/prereq.md" >}}

## Configure 100 Continue proxying {#configure-100-continue-proxying}

Set `spec.default.httpSettings.proxy100Continue` to `true` in a ListenerPolicy resource. If you omit the field or set the field to `false`, the gateway proxy handles `100 Continue` responses locally.

1. Create a ListenerPolicy resource that enables `proxy100Continue` for the HTTP listener on the gateway.

   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.kgateway.dev/v1alpha1
   kind: ListenerPolicy
   metadata:
     name: proxy-100-continue
     namespace: {{< reuse "kgw-docs/snippets/namespace.md" >}}
   spec:
     targetRefs:
     - group: gateway.networking.k8s.io
       kind: Gateway
       name: http
     default:
       httpSettings:
         proxy100Continue: true
   EOF
   ```

   | Field | Description |
   | --- | --- |
   | `spec.targetRefs` | The Gateway resources that the ListenerPolicy applies to. In this example, the policy applies to the `http` Gateway from the sample app guide. |
   | `spec.default.httpSettings.proxy100Continue` | Set to `true` to forward requests with an `Expect: 100-continue` header upstream and proxy upstream `100 Continue` responses downstream. Omit the field or set the field to `false` to let the gateway proxy handle the response locally. |

2. Port-forward the gateway proxy admin endpoint on port 19000.

   ```sh
   kubectl port-forward deployment/http -n {{< reuse "kgw-docs/snippets/namespace.md" >}} 19000
   ```

3. Get the HTTP connection manager settings from the proxy config dump. Verify that `proxy100Continue` is set to `true`.

   ```sh
   curl -s 127.0.0.1:19000/config_dump | jq '.. | .proxy100Continue? // empty'
   ```

   Example output:

   ```console
   true
   ```

## Cleanup {#cleanup}

{{< reuse "kgw-docs/snippets/cleanup.md" >}}

```sh
kubectl delete listenerpolicy proxy-100-continue -n {{< reuse "kgw-docs/snippets/namespace.md" >}}
```
