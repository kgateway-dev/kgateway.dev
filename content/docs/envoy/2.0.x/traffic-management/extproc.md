---
title: External processing (ExtProc)
weight: 20
description: Modify aspects of an HTTP request or response with an external processing server. 
---

Modify aspects of an HTTP request or response with an external processing server. 

{{< callout >}}
{{< reuse "docs/snippets/proxy-kgateway.md" >}}
{{< /callout >}}

## About external processing

Envoy offers multiple filters that you can use to manage, monitor, and secure traffic to your apps. Although Envoy is extensible via C++ and WebAssembly modules, it might not be practical to implement these extensions for all of your apps. You might also have very specific requirements for how to process a request or response to allow traffic routing between different types of apps, such as adding specific headers to new and legacy apps.

With the Envoy external processing (ExtProc) filter, you can implement an external gRPC processing server that can read and modify all aspects of an HTTP request or response, and add that server to the Envoy filter chain. The external service can manipulate headers, body, and trailers of a request or response before it is forwarded to an upstream or downstream service. The request or response can also be terminated at any given time.

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

{{< callout type="info" >}}
ExtProc can be applied to an HTTPRoute. However, it can currently not be applied to a Gateway. 
{{< /callout >}}


## Before you begin

{{< reuse "docs/snippets/prereq.md" >}}

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
         app: ext-proc-grpc
     replicas: 1
     template:
       metadata:
         labels:
           app: ext-proc-grpc
       spec:
         containers:
           - name: ext-proc-grpc
             image: gcr.io/solo-test-236622/ext-proc-example-basic-sink:0.0.2
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
       app: ext-proc-grpc
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

1. Create a GatewayExtension resource to enable external processing in your environment. This resource points to the ExtProc service that you created earlier. 
   ```yaml
   kubectl apply -n {{< reuse "docs/snippets/namespace.md" >}} -f- <<EOF
   apiVersion: gateway.kgateway.dev/v1alpha1
   kind: GatewayExtension
   metadata:
     name: ext-proc-extension
   spec:
     type: ExtProc
     extProc:
       grpcService:
         backendRef:
           name: ext-proc-grpc
           port: 4444
   EOF
   ```
   
2. Create a {{< reuse "docs/snippets/trafficpolicy.md" >}} that references the GatewayExtension resource that you created earlier. 
   ```yaml
   kubectl apply -n {{< reuse "docs/snippets/namespace.md" >}} -f- <<EOF
   apiVersion: {{< reuse "docs/snippets/trafficpolicy-apiversion.md" >}}
   kind: {{< reuse "docs/snippets/trafficpolicy.md" >}}
   metadata:
     name: extproc
   spec:
     extProc:
       extensionRef:
         name: ext-proc-extension
   EOF
   ```
   
3. Create an HTTPRoute that exposes two routes for the httpbin app along the `extproc.example` domain. One route (`/headers`) is configured for external processing and the other one (`/get`) is not. 
   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.networking.k8s.io/v1
   kind: HTTPRoute
   metadata:
     name: extproc
     namespace: {{< reuse "docs/snippets/namespace.md" >}}
   spec:
     parentRefs:
       - name: http
         namespace: {{< reuse "docs/snippets/namespace.md" >}}
     hostnames:
       - "extproc.example"
     rules:
       - matches: 
           - path:
               type: PathPrefix
               value: /headers
         backendRefs:
           - name: httpbin
             port: 8000
             namespace: httpbin
         filters:
         - type: ExtensionRef
           extensionRef:
             group: {{< reuse "docs/snippets/trafficpolicy-group.md" >}}
             kind: {{< reuse "docs/snippets/trafficpolicy.md" >}}
             name: extproc
       - matches: 
          - path:
              type: PathPrefix
              value: /get
         backendRefs:
           - name: httpbin
             port: 8000
             namespace: httpbin
   EOF
   ```
 
4. Create a ReferenceGrant resource to allow the HTTPRoute to forward traffic to the httpbin app. This resource is required, because the HTTPRoute resource and httpbin app are deployed to different namespaces.
   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.networking.k8s.io/v1beta1
   kind: ReferenceGrant
   metadata:
     name: allow-httproute-to-httpbin
     namespace: httpbin  # The namespace where the target Service exists
   spec:
     from:
       - group: gateway.networking.k8s.io
         kind: HTTPRoute
         namespace: {{< reuse "docs/snippets/namespace.md" >}}  # The namespace of the HTTPRoute
     to:
       - group: ""  # Empty string means it's a core API (like Service)
         kind: Service
   EOF
   ```
   
5. Send a request to the httpbin app along the `/headers` path and provide your instructions in the `instruction` header. This example instructs the ExtProc server to add the `extproc: true` header. Verify that you get back a 200 HTTP response and that your response includes the `extproc: true` header. 

   {{< tabs items="Cloud Provider LoadBalancer,Port-forward for local testing" tabTotal="2"  >}}

   {{% tab tabName="Cloud Provider LoadBalancer" %}}
   ```sh
   curl -vi http://$INGRESS_GW_ADDRESS:8080/headers -H "host: extproc.example" -H 'instructions: {"addHeaders":{"extproc":"true"}}' 
   ```
   {{% /tab %}}

   {{% tab tabName="Port-forward for local testing" %}}
   ```sh
   curl -vi http://localhost:8080/headers -H "host: extproc.example" -H 'instructions: {"addHeaders":{"extproc":"true"}}' 
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

6. Send a request along the `/get` path. Verify that you get back a 200 HTTP response code. However, because this route is not configured for ExtProc, you do not see the `extproc: true` header in your response.

   {{< tabs items="Cloud Provider LoadBalancer,Port-forward for local testing" tabTotal="2" >}}

   {{% tab tabName="Cloud Provider LoadBalancer"  %}}
   ```sh
   curl -vi http://$INGRESS_GW_ADDRESS:8080/get -H "host: extproc.example" -H 'instructions: {"addHeaders":{"extproc":"true"}}' 
   ```
   {{% /tab %}}

   {{% tab tabName="Port-forward for local testing" %}}
   ```sh
   curl -vi http://localhost:8080/get -H "host: extproc.example" -H 'instructions: {"addHeaders":{"extproc":"true"}}' 
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

<!--
## Gateway configuration {#gateway}

You can enable ExtProc for all a Gateway. This way, the ExtProc configuration applies to all the routes that the Gateway serves.

1. Create a GatewayExtension resource to enable external processing in your environment. This resource points to the ExtProc service that you created earlier. 
   ```yaml
   kubectl apply -n kgateway-system -f- <<EOF
   apiVersion: gateway.kgateway.dev/v1alpha1
   kind: GatewayExtension
   metadata:
     name: ext-proc-extension
   spec:
     type: ExtProc
     extProc:
       grpcService:
         backendRef:
           name: ext-proc-grpc
           port: 4444
   EOF
   ```
   
2. Create a TrafficPolicy that references the GatewayExtension resource that you created earlier. Use the `targetRefs` section to apply the policy to your Gateway. 
   ```yaml
   kubectl apply -n kgateway-system -f- <<EOF
   apiVersion: gateway.kgateway.dev/v1alpha1
   kind: TrafficPolicy
   metadata:
     name: extproc
   spec:
     targetRefs: 
     - group: gateway.networking.k8s.io
       kind: HTTPRoute
       name: extproc
     extProc:
       extensionRef:
         name: ext-proc-extension
   EOF
   ```
   
3. Create an HTTPRoute that exposes two routes for the httpbin app along the `extproc.example` domain, `/headers` and `/get`. Note that the HTTPRoute does not include any ExtProc configuration. 
   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.networking.k8s.io/v1
   kind: HTTPRoute
   metadata:
     name: extproc
     namespace: kgateway-system
   spec:
     parentRefs:
       - name: http
         namespace: kgateway-system
     hostnames:
       - "extproc.example"
     rules:
       - matches: 
           - path:
               type: PathPrefix
               value: /headers
         backendRefs:
           - name: httpbin
             port: 8000
             namespace: httpbin
       - matches: 
          - path:
              type: PathPrefix
              value: /get
         backendRefs:
           - name: httpbin
             port: 8000
             namespace: httpbin
   EOF
   ```
   
4. Create a ReferenceGrant resource to allow the HTTPRoute to forward traffic to the httpbin app. This resource is required, because the HTTPRoute resource and httpbin app are deployed to different namespaces.
   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.networking.k8s.io/v1beta1
   kind: ReferenceGrant
   metadata:
     name: allow-httproute-to-httpbin
     namespace: httpbin  # The namespace where the target Service exists
   spec:
     from:
       - group: gateway.networking.k8s.io
         kind: HTTPRoute
         namespace: kgateway-system  # The namespace of the HTTPRoute
     to:
       - group: ""  # Empty string means it's a core API (like Service)
         kind: Service
   EOF
   ```
   
5. Send a request to the httpbin app along the `/headers` path and provide your instructions in the `instruction` header. This example instructs the ExtProc server to add the `extproc: true` header. Verify that you get back a 200 HTTP response and that your response includes the `extproc: true` header. 
   ```sh
   curl -vi http://$INGRESS_GW_ADDRESS:8080/headers -H "host: extproc.example" -H 'instructions: {"addHeaders":{"extproc":"true"}}' 
   ```
   
   Example output: 
   ```yaml {linenos=table,hl_lines=[10,11],linenostart=1}
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

6. Send a request along the `/get` path. Verify that you get back a 200 HTTP response code and that you also see the `extproc: true` header. 
   ```sh
   curl -vi http://$INGRESS_GW_ADDRESS:8080/get -H "host: extproc.example" -H 'instructions: {"addHeaders":{"extproc":"true"}}' 
   ```
   
   Example output: 
   ```yaml {linenos=table,hl_lines=[10,11],linenostart=1}
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
-->  
## Cleanup

{{< reuse "docs/snippets/cleanup.md" >}}

```sh
kubectl delete httproute extproc -n {{< reuse "docs/snippets/namespace.md" >}}
kubectl delete {{< reuse "docs/snippets/trafficpolicy.md" >}} extproc -n {{< reuse "docs/snippets/namespace.md" >}}
kubectl delete referencegrant allow-httproute-to-httpbin -n httpbin
kubectl delete gatewayextension ext-proc-extension -n {{< reuse "docs/snippets/namespace.md" >}}
kubectl delete deployment ext-proc-grpc -n {{< reuse "docs/snippets/namespace.md" >}}
kubectl delete service ext-proc-grpc -n {{< reuse "docs/snippets/namespace.md" >}}
```