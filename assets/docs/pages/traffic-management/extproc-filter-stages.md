Use the `filterStage` field in a GatewayExtension resource to control where in the Envoy filter chain an ExtProc filter runs. This way, you can apply multiple ExtProc filters to the same route at different stages.

## About ExtProc filter stages

The Envoy filter chain processes each request through a series of ordered stages before forwarding it to the upstream service. By default, the ExtProc filter runs after the `AuthZ` (authorization) stage. You can use the `filterStage` field in your GatewayExtension resource to position the ExtProc filter at a different stage in the filter chain, or to run ExtProc at multiple stages for the same route.

The following stages are supported. The stages are listed in the order that a request passes through them. When a response is received from the upstream service, the stages are traversed in reverse order.

| `filterStage.stage` | Position in the filter chain |
|---|---|
| `Fault` | Earliest stage. ExtProc is executed before fault injection. |
| `AuthN` | External authentication stage. |
| `AuthZ` | Authorization stage. This setting is the default when the `filterStage` field is not set. |
| `RateLimit` | Rate limiting stage. |
| `Route` | Final processing stage before the request leaves the gateway proxy. |

In addition to the filter stage, you use the `filterStage.predicate` field to configure when to run ExtProc relative to the stage. 

The following predicates are supported: 

| `filterStage.predicate` | Description |
|---|---|
| `Before` | Run the ExtProc filter before the specified stage. |
| `During` | Run the ExtProc filter during the specified stage. This setting is the default when the `predicate` field is not set. |
| `After` | Run the ExtProc filter after the specified stage. |

{{< callout >}}
When multiple ExtProc filters target the same route at the same stage and predicate, use the `filterStage.weight` field to control their relative order. A higher weight runs earlier in the chain. Filters with the same weight are sorted alphabetically by GatewayExtension name.
{{< /callout >}}

## Before you begin

{{< reuse "docs/snippets/prereq.md" >}}

## Set up multiple ExtProc filters at different stages {#multiple-extproc}

You can apply multiple ExtProc filters to the same route, each running at a different position in the filter chain. To do that, you create a separate GatewayExtension and {{< reuse "docs/snippets/trafficpolicy.md" >}} resource for each stage. Then, you reference both from the same HTTPRoute.

A common use case is to observe how a request changes as it passes through the filter chain. For example, you can run one ExtProc filter before authentication to capture the raw incoming request, and another after the routing decision is made to capture the request before it leaves the gateway proxy.

{{< callout type="info" >}}
By default, creating multiple {{< reuse "docs/snippets/trafficpolicy.md" >}} resources that all specify the same `extProc` field results in a policy conflict error. To ensure that you can apply multiple ExtProc stages to the same route, enable deep merging for ExtProc policies by either setting `policyMerge.trafficPolicy.extProc=DeepMerge` in your Helm installation or using the `KGW_POLICY_MERGE={"trafficPolicy":{"extProc":"DeepMerge"}}` environment variable. 
{{< /callout >}}

1. Optional: Get the values of your current Helm installation. 
   ```sh
   helm get values {{< reuse "/docs/snippets/helm-kgateway.md" >}} -n {{< reuse "docs/snippets/namespace.md" >}} -o yaml > values.yaml
   ```

2. Upgrade your Helm installation to enable deep merging for multiple {{< reuse "docs/snippets/trafficpolicy.md" >}} resources that all specify the same `extProc` field. 
   ```sh
   helm upgrade {{< reuse "/docs/snippets/helm-kgateway.md" >}} oci://{{< reuse "/docs/snippets/helm-path.md" >}}/charts/{{< reuse "/docs/snippets/helm-kgateway.md" >}} \
     -n {{< reuse "docs/snippets/namespace.md" >}} \
     --version {{< reuse "docs/versions/helm-version-flag.md" >}} \
     -f values.yaml \
     --set policyMerge.trafficPolicy.extProc=DeepMerge
   ```

3. Verify that the control plane pods are up and running. 
   ```sh
   kubectl get pods -n {{< reuse "docs/snippets/namespace.md" >}}
   ```

4. Set up the ExtProc server. This example uses a prebuilt ExtProc server that manipulates request and response headers based on instructions that are sent in an instructions header.
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
             image: ghcr.io/kgateway-dev/extproc-server:0.0.1
             imagePullPolicy: IfNotPresent
             command: ["./server", "--add-header", "x-extproc-processed:true"]
             ports:
               - containerPort: 18080
   ---
   apiVersion: v1
   kind: Service
   metadata:
     name: ext-proc-grpc
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

5. Verify that the ExtProc server is running.
   ```sh
   kubectl get pods -n {{< reuse "docs/snippets/namespace.md" >}} | grep ext-proc-grpc
   ```

6. Create two GatewayExtension resources with different `filterStage` settings, one that applies ExtProc before the `AuthN` stage and one that runs after the `Route` stage. You use the same ExtProc server for both stages. However, you can also point to different ExtProc servers for each stage. 
   ```yaml
   kubectl apply -n {{< reuse "docs/snippets/namespace.md" >}} -f- <<EOF
   apiVersion: gateway.kgateway.dev/v1alpha1
   kind: GatewayExtension
   metadata:
     name: ext-proc-before-authn
   spec:
     extProc:
       grpcService:
         backendRef:
           name: ext-proc-grpc
           port: 4444
       filterStage:
         stage: AuthN
         predicate: Before
   ---
   apiVersion: gateway.kgateway.dev/v1alpha1
   kind: GatewayExtension
   metadata:
     name: ext-proc-after-route
   spec:
     extProc:
       grpcService:
         backendRef:
           name: ext-proc-grpc
           port: 4444
       filterStage:
         stage: Route
         predicate: After
   EOF
   ```

7. Create a separate {{< reuse "docs/snippets/trafficpolicy.md" >}} resource for each GatewayExtension resource.
   ```yaml
   kubectl apply -n {{< reuse "docs/snippets/namespace.md" >}} -f- <<EOF
   apiVersion: {{< reuse "docs/snippets/trafficpolicy-apiversion.md" >}}
   kind: {{< reuse "docs/snippets/trafficpolicy.md" >}}
   metadata:
     name: extproc-before-authn
   spec:
     extProc:
       extensionRef:
         name: ext-proc-before-authn
   ---
   apiVersion: {{< reuse "docs/snippets/trafficpolicy-apiversion.md" >}}
   kind: {{< reuse "docs/snippets/trafficpolicy.md" >}}
   metadata:
     name: extproc-after-route
   spec:
     extProc:
       extensionRef:
         name: ext-proc-after-route
   EOF
   ```

8. Create an HTTPRoute resource that routes traffic along the `extproc.example` domain to the httpbin app and applies both {{< reuse "docs/snippets/trafficpolicy.md" >}} resources to the same route rule.
   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.networking.k8s.io/v1
   kind: HTTPRoute
   metadata:
     name: extproc-mixed-stages
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
               name: extproc-before-authn
           - type: ExtensionRef
             extensionRef:
               group: {{< reuse "docs/snippets/trafficpolicy-group.md" >}}
               kind: {{< reuse "docs/snippets/trafficpolicy.md" >}}
               name: extproc-after-route
   EOF
   ```

9. Create a ReferenceGrant resource to allow the HTTPRoute to forward traffic to the httpbin app. This resource is required because the HTTPRoute and the httpbin app are in different namespaces.
   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.networking.k8s.io/v1beta1
   kind: ReferenceGrant
   metadata:
     name: allow-httproute-mixed-stages-to-httpbin
     namespace: httpbin
   spec:
     from:
       - group: gateway.networking.k8s.io
         kind: HTTPRoute
         namespace: {{< reuse "docs/snippets/namespace.md" >}}
     to:
       - group: ""
         kind: Service
   EOF
   ```

10. Send a request to the `/headers` path. The ExtProc server is invoked twice. Verify that you see the `x-extproc-processed: true` header in your response.

    {{< tabs items="Cloud Provider LoadBalancer,Port-forward for local testing" tabTotal="2"  >}}

    {{% tab tabName="Cloud Provider LoadBalancer" %}}
    ```sh
    curl -vi http://$INGRESS_GW_ADDRESS:8080/headers -H "host: extproc.example"
    ```
    {{% /tab %}}

    {{% tab tabName="Port-forward for local testing" %}}
    ```sh
    curl -vi http://localhost:8080/headers -H "host: extproc.example"
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
       "X-Extproc-Processed": [
         "true"
       ],
       "Host": [
         "extproc.example"
       ],
    ...
    ```

11. Check the ExtProc server logs. Verify that you see two `Process` log entries, one for each stage. 
    ```sh
    kubectl logs -n {{< reuse "docs/snippets/namespace.md" >}} -l app.kubernetes.io/name=ext-proc-grpc
    ```

    Example output: 
    ```console
    Process
    Got RequestHeaders
    Sending ProcessingResponse
    Process
    Got RequestHeaders
    Sending ProcessingResponse
    Got ResponseHeaders
    Sending ProcessingResponse
    Got ResponseHeaders
    Sending ProcessingResponse
    ```


## Cleanup

{{< reuse "docs/snippets/cleanup.md" >}}

```sh
kubectl delete httproute extproc-mixed-stages -n {{< reuse "docs/snippets/namespace.md" >}}
kubectl delete {{< reuse "docs/snippets/trafficpolicy.md" >}} extproc-before-authn extproc-after-route -n {{< reuse "docs/snippets/namespace.md" >}}
kubectl delete referencegrant allow-httproute-mixed-stages-to-httpbin -n httpbin
kubectl delete gatewayextension ext-proc-before-authn ext-proc-after-route -n {{< reuse "docs/snippets/namespace.md" >}}
kubectl delete deployment ext-proc-grpc -n {{< reuse "docs/snippets/namespace.md" >}}
kubectl delete service ext-proc-grpc -n {{< reuse "docs/snippets/namespace.md" >}}
```
