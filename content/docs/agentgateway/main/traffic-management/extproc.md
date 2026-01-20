---
title: External processing (ExtProc)
weight: 10
description:
---

Modify aspects of an HTTP request or response with an external processing server. 

## About external processing

With the external processing, you can implement an external gRPC processing server that can read and modify all aspects of an HTTP request or response, and add that server to the agentgateway proxy processing chain. The external service can manipulate headers, body, and trailers of a request or response before it is forwarded to an upstream or downstream service. The request or response can also be terminated at any given time.

With this approach, you have the flexibility to apply your requirements to all types of apps, without the need to run WebAssembly or other custom scripts.

### How it works

The following diagram shows an example for how request header manipulation works when an external processing server is used. 

{{< reuse-image src="img/extproc.svg" width="400" caption="Request header manipulation with external processing" >}}
{{< reuse-image-dark srcDark="img/extproc.svg" width="400" caption="Request header manipulation with external processing" >}}

1. The downstream service sends a request with headers to the Envoy gateway. 
2. The gateway extracts the header information and sends it to the external processing server. 
3. The external processing server modifies, adds, or removes the request headers. 
4. The modified request headers are sent back to the gateway. 
5. The modified headers are added to the request.
6. The request is forwarded to the upstream application. 

### ExtProc server considerations

The ExtProc server is a gRPC interface that must be able to respond to events in the lifecycle of an HTTP request. When the ExtProc filter is enabled in Gloo Gateway and a request or response is received on the gateway, the filter communicates with the ExtProc server by using bidirectional gRPC streams.

To implement your own ExtProc server, make sure that you follow [Envoy's technical specification for an external processor](https://www.envoyproxy.io/docs/envoy/latest/api-v3/extensions/filters/http/ext_proc/v3/ext_proc.proto#extensions-filters-http-ext-proc-v3-externalprocessor). This guide uses a sample ExtProc server that you can use to try out the ExtProc functionality.

## Before you begin

1. [Set up an agentgateway proxy]({{< link-hextra path="/setup/" >}}). 
2. [Install the httpbin sample app]({{< link-hextra path="/operations/sample-app/" >}}).

## Set up an ExtProc server

Use a sample ExtProc server implementation to try out the ExtProc functionality in {{< reuse "docs/snippets/kgateway.md" >}}.

1. Set up the ExtProc server. This example uses a prebuilt ExtProc server that manipulates request and response headers based on instructions that are sent in an instructions header.
   ```yaml
   kubectl apply -n {{< reuse "docs/snippets/namespace.md" >}} -f- <<EOF
   apiVersion: apps/v1
   kind: Deployment
   metadata:
     name: ext-proc-grpc
   spec:
     selector:
       matchLabels:
         app.kubernetes.io/name: ext-proc-grpc
     replicas: 1
     template:
       metadata:
         labels:
           app.kubernetes.io/name: ext-proc-grpc
       spec:
         containers:
           - name: ext-proc-grpc
             # Source code for this image is in test/e2e/features/agentgateway/extproc/example
             image: ghcr.io/kgateway-dev/extproc-server:0.0.1
             imagePullPolicy: IfNotPresent
             ports:
               - containerPort: 18080
   ---
   apiVersion: v1
   kind: Service
   metadata:
     name: ext-proc-grpc
     labels:
       app: ext-proc-grpc
   spec:
     ports:
     - port: 4444
       targetPort: 18080
       protocol: TCP
       appProtocol: kubernetes.io/h2c
     selector:
       app.kubernetes.io/name: ext-proc-grpc
   EOF
   ```
   
   The `instructions` header must be provided as a JSON string in the following format:
   ```json
   {
     "addHeaders": {
       "header1": "value1",
       "header2": "value2"
     },
     "removeHeaders": [ "header3", "header4" ],
     }
   }
   ```

2. Verify that the ExtProc server is up and running.
   ```sh
   kubectl get pods -n {{< reuse "docs/snippets/namespace.md" >}} | grep ext-proc-grpc
   ```
<!--
3. Continue with configuring ExtProc for a [route](#route) or [gateway](#gateway).
-->

## Set up ExtProc for a route {#route}

You can enable ExtProc for a particular route in an HTTPRoute resource. 
   
1. Create an {{< reuse "docs/snippets/trafficpolicy.md" >}} that ... 
   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: {{< reuse "docs/snippets/trafficpolicy-apiversion.md" >}}
   kind: {{< reuse "docs/snippets/trafficpolicy.md" >}}
   metadata:
     name: extproc
     namespace: {{< reuse "docs/snippets/namespace.md" >}}
   spec:
     targetRefs:
     - group: gateway.networking.k8s.io
       kind: Gateway
       name: agentgateway-proxy
     traffic: 
       extProc:
         backendRef: 
           name: ext-proc-grpc
           namespace: {{< reuse "docs/snippets/namespace.md" >}}
           port: 4444
   EOF
   ```
   
2. Send a request to the httpbin app along the `/headers` path and provide your instructions in the `instruction` header. This example instructs the ExtProc server to add the `extproc: true` header. Verify that you get back a 200 HTTP response and that your response includes the `extproc: true` header. 

   {{< tabs items="Cloud Provider LoadBalancer,Port-forward for local testing" tabTotal="2"  >}}

   {{% tab tabName="Cloud Provider LoadBalancer" %}}
   ```sh
   curl -vi http://$INGRESS_GW_ADDRESS:8080/headers -H "host: www.example.com" -H 'instructions: {"addHeaders":{"extproc":"true"}}' 
   ```
   {{% /tab %}}

   {{% tab tabName="Port-forward for local testing" %}}
   ```sh
   curl -vi http://localhost:8080/headers -H "host: www.example.com" -H 'instructions: {"addHeaders":{"extproc":"true"}}' 
   ```
   {{% /tab %}}

   {{< /tabs >}}

   Example output:

   ```console {hl_lines=[10,11]}
   < HTTP/1.1 200 OK
   HTTP/1.1 200 OK
   ...
   < 
   {
     "headers": {
       "Accept": [
         "*/*"
       ],
       "Extproc": [
         "true"
       ],
       "Host": [
         "extproc.example"
       ],
       "Instructions": [
         "{\"addHeaders\":{\"extproc\":\"true\"}}"
       ],
       "User-Agent": [
         "curl/8.7.1"
       ],
   ...
   ```

6. Send a request along the `/get` path. Verify that you get back a 200 HTTP response code. However, because this route is not configured for ExtProc, you do not see the `"extproctest": "true"` header in your response.

   {{< tabs items="Cloud Provider LoadBalancer,Port-forward for local testing" tabTotal="2" >}}

   {{% tab tabName="Cloud Provider LoadBalancer"  %}}
   ```sh
   curl -vi http://$INGRESS_GW_ADDRESS:8080/get -H "host: www.example.com" -H 'instructions: {"addHeaders":{"extproc":"true"}}' 
   ```
   {{% /tab %}}

   {{% tab tabName="Port-forward for local testing" %}}
   ```sh
   curl -vi http://localhost:8080/get -H "host: www.example.com" -H 'instructions: {"addHeaders":{"extproc":"true"}}' 
   ```
   {{% /tab %}}

   {{< /tabs >}}

   Example output:

   ```json
   < HTTP/1.1 200 OK
   HTTP/1.1 200 OK
   ...
   < 
   {
     "headers": {
       "Accept": [
         "*/*"
       ],
       "Host": [
         "extproc.example"
       ],
       "Instructions": [
         "{\"addHeaders\":{\"extproc\":\"true\"}}"
       ],
       "User-Agent": [
         "curl/8.7.1"
       ],
   ...
   ```

## Cleanup

{{< reuse "docs/snippets/cleanup.md" >}}

```sh
kubectl delete {{< reuse "docs/snippets/trafficpolicy.md" >}} extproc -n {{< reuse "docs/snippets/namespace.md" >}}
kubectl delete deployment ext-proc-grpc -n {{< reuse "docs/snippets/namespace.md" >}}
kubectl delete service ext-proc-grpc -n {{< reuse "docs/snippets/namespace.md" >}}
```



