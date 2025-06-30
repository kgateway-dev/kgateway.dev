---
title: Inject response headers
weight: 20
description: Extract values from a request header and inject it as a header to your response. 
---

Use an Inja template to extract a value from a request header and add it as a header to your responses. 

## Before you begin

{{< reuse "docs/snippets/prereq.md" >}}

## Inject response headers
   
1. Create a TrafficPolicy resource with the folloing transformation rules: 
   * `x-gateway-response`: Use the value from the `x-gateway-request` request header and populate the value of that header into an `x-gateway-response` response header.
   * `x-podname`: Retrieve the value of the `POD_NAME` environment variable and add the value to the `x-podname` response header. Because the transformation is processed in the gateway proxy, these environment variables refer to the variables that are set on the proxy. You can view supported environment variables when you run `kubectl get deployment http -n {{< reuse "docs/snippets/namespace.md" >}} -o yaml and look at the `spec.containers.env` section.
   * `x-season`: Adds a static string value of summer to the `x-season` response header.
   * `x-response-raw`: Adds a static string hello value with all escape characters intact.
   * `x-replace`: Replaces the pattern-to-replace text in the `baz` header with a random string.
   
   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.kgateway.dev/v1alpha1
   kind: TrafficPolicy
   metadata:
     name: transformation
     namespace: httpbin
   spec:
     transformation:
       response:
         set:
         - name: x-gateway-response
           value: '{{ request_header("x-gateway-request") }}' 
         - name: x-podname
           value: '{{ env("POD_NAME") }}'
         - name: x-season
           value: 'summer'
         - name: x-response-raw
           value: '{{ raw_string("hello") }}'
         - name: x-replace
           value: '{{ replace_with_random(request_header("baz"), "pattern-to-replace") }}'
   EOF
   ```

2. Update the HTTPRoute resource to apply the TrafficPolicy to the httpbin route by using an `extensionRef` filter.

   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.networking.k8s.io/v1
   kind: HTTPRoute
   metadata:
     name: httpbin
     namespace: httpbin
     labels:
       example: httpbin-route
   spec:
     parentRefs:
       - name: http
         namespace: {{< reuse "docs/snippets/namespace.md" >}}
     hostnames:
       - "www.example.com"
     rules:
       - backendRefs:
           - name: httpbin
             port: 8000
         filters:
         - type: ExtensionRef
           extensionRef:
             group: gateway.kgateway.dev
             kind: TrafficPolicy
             name: transformation
   EOF
   ```

3. Send a request to the httpbin app and include the `x-gateway-request` and `baz` request headers. Verify that you get back a 200 HTTP response code and that the following response headers are included:
   * `x-podname` with the name of the gateway proxy pod
   * `x-season` that is set to `summer`
   * `x-gateway-response` that is set to the value of the `x-gateway-request` request header.
   * `x-response-raw` that is set to `hello`.
   * `x-replace` that is set to a random string.
   
   {{< tabs items="Cloud Provider LoadBalancer,Port-forward for local testing" tabTotal="2" >}}
   {{% tab tabName="Cloud Provider LoadBalancer" %}}
   ```sh
   curl -vi http://$INGRESS_GW_ADDRESS:8080/response-headers \
    -H "host: www.example.com:8080" \
    -H "x-gateway-request: my custom request header" \
    -H "baz: pattern-to-replace"
   ```
   {{% /tab %}}
   {{% tab tabName="Port-forward for local testing" %}}
   ```sh
   curl -vi localhost:8080/response-headers \
   -H "host: www.example.com" \
   -H "x-gateway-request: my custom request header" \
   -H "baz: pattern-to-replace"
   ```
   {{% /tab %}}
   {{< /tabs >}}
   
   Example output: 

   ```console {hl_lines=[3,4,20,21,22,23,24,25,26,27,28,29]}
   ...
   * Request completely sent off
   < HTTP/1.1 200 OK
   HTTP/1.1 200 OK
   < access-control-allow-credentials: true
   access-control-allow-credentials: true
   < access-control-allow-origin: *
   access-control-allow-origin: *
   < content-type: application/json; encoding=utf-8
   content-type: application/json; encoding=utf-8
   < content-length: 3
   content-length: 3
   < x-envoy-upstream-service-time: 2
   x-envoy-upstream-service-time: 2
   < server: envoy
   server: envoy
   < x-envoy-decorator-operation: httpbin.httpbin.svc.cluster.local:8000/*
   x-envoy-decorator-operation: httpbin.httpbin.svc.cluster.local:8000/*
   < x-envoy-upstream-service-time: 1
   < x-podname: http-85d5775587-tkxmt
   x-podname: http-85d5775587-tkxmt
   < x-replace: zljPMhO86gJCFc69jZ0+kQ
   x-replace: zljPMhO86gJCFc69jZ0+kQ
   < x-response-raw: hello
   x-response-raw: hello
   < x-gateway-response: my custom request header
   x-gateway-response: my custom request header
   < x-season: summer
   x-season: summer
   ```
   
## Cleanup

{{< reuse "docs/snippets/cleanup.md" >}}

1. Delete the TrafficPolicy resource.

   ```sh
   kubectl delete TrafficPolicy transformation -n httpbin
   ```
   
2. Remove the `extensionRef` filter from the HTTPRoute resource.

   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.networking.k8s.io/v1
   kind: HTTPRoute
   metadata:
     name: httpbin
     namespace: httpbin
     labels:
       example: httpbin-route
   spec:
     parentRefs:
       - name: http
         namespace: {{< reuse "docs/snippets/namespace.md" >}}
     hostnames:
       - "www.example.com"
     rules:
       - backendRefs:
           - name: httpbin
             port: 8000
   EOF
   ```
   
