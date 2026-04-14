Route traffic to gRPC services by using the GRPCRoute resource for protocol-aware routing.

## About gRPC routing

The GRPCRoute resource provides protocol-aware routing for gRPC traffic within the Kubernetes Gateway API. Unlike the HTTPRoute, which requires matching on HTTP paths and methods, the GRPCRoute allows you to define routing rules by using gRPC-native concepts, such as service and method names.

Consider the difference:
- **HTTPRoute Match**: `path:/com.example.User/Login`, `method: POST`
- **GRPCRoute Match**: `service: yages.Echo`, `method: Ping`

The GRPCRoute approach is more readable, less error-prone, and aligns with the Gateway API's role-oriented philosophy.

## Before you begin

1. Follow the [Get started guide]({{< link-hextra path="/quickstart/" >}}) to install kgateway.
2. Install [`grpcurl`](https://github.com/fullstorydev/grpcurl) for testing on your computer.

## Deploy a sample gRPC service {#sample-grpc}

Deploy a sample gRPC service for testing purposes. The sample service has two APIs:

- `yages.Echo.Ping`: Takes no input (empty message) and returns a `pong` message.
- `yages.Echo.Reverse`: Takes input content and returns the content in reverse order, such as `hello world` becomes `dlrow olleh`.

Steps to set up the sample gRPC service:

1. Deploy the gRPC echo server and client.

   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: apps/v1
   kind: Deployment
   metadata:
     name: grpc-echo
     namespace: {{< reuse "docs/snippets/namespace.md" >}}
     labels:
       app.kubernetes.io/name: grpc-echo
   spec:
     selector:
       matchLabels:
         app.kubernetes.io/name: grpc-echo
     replicas: 1
     template:
       metadata:
         labels:
          app.kubernetes.io/name: grpc-echo
       spec:
         containers:
           - name: grpc-echo
             image: ghcr.io/projectcontour/yages:v0.1.0
             ports:
               - containerPort: 9000
                 protocol: TCP
             env:
               - name: POD_NAME
                 valueFrom:
                   fieldRef:
                     fieldPath: metadata.name
               - name: NAMESPACE
                 valueFrom:
                   fieldRef:
                     fieldPath: metadata.namespace
               - name: GRPC_ECHO_SERVER
                 value: "true"
               - name: SERVICE_NAME
                 value: grpc-echo
   ---
   apiVersion: v1
   kind: Service
   metadata:
     name: grpc-echo-svc
     namespace: {{< reuse "docs/snippets/namespace.md" >}}
     labels:
       app.kubernetes.io/name: grpc-echo
   spec:
     type: ClusterIP
     ports:
       - port: 3000
         protocol: TCP
         targetPort: 9000
         appProtocol: kubernetes.io/h2c
     selector:
       app.kubernetes.io/name: grpc-echo
   ---
   apiVersion: v1
   kind: Pod
   metadata:
     name: grpcurl-client
     namespace: {{< reuse "docs/snippets/namespace.md" >}}
     labels:
       app.kubernetes.io/name: grpcurl-client
   spec:
    containers:
       - name: grpcurl
         image: docker.io/fullstorydev/grpcurl:v1.8.7-alpine
         command:
           - sleep
           - "infinity"
   EOF
   ```

2. Verify that the sample app is up and running. 
   ```sh
   kubectl get pods -n {{< reuse "docs/snippets/namespace.md" >}} | grep grpc
   ```

   Example output: 
   ```console
   grpc-echo-5fc549b5fc-tdlzw            1/1     Running            0                39s
   grpcurl-client                        1/1     Running            0                6s
   ```


## Set up gRPC routing {#grpcroute}

1. Create the gRPC Gateway. The following Gateway accepts routes from all namespaces. 
   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.networking.k8s.io/v1
   kind: Gateway
   metadata:
     name: grpc              
     namespace: {{< reuse "docs/snippets/namespace.md" >}}
   spec:
     gatewayClassName: {{< reuse "docs/snippets/gatewayclass.md" >}}
     listeners:
     - protocol: HTTP
       port: 80
       name: http
       allowedRoutes:
         namespaces:
          from: All
   EOF
   ```

2. Create the GRPCRoute. The GRPCRoute includes a match for `grpc.reflection.v1alpha.ServerReflection` to enable dynamic API exploration and a match for the `Ping` method. For detailed information about GRPCRoute fields and configuration options, see the [Gateway API GRPCRoute documentation](https://gateway-api.sigs.k8s.io/reference/spec/#grpcroute).

   ```yaml
   kubectl apply -f - <<EOF
   apiVersion: gateway.networking.k8s.io/v1
   kind: GRPCRoute
   metadata:
     name: example-route
     namespace: {{< reuse "docs/snippets/namespace.md" >}}
   spec:
     parentRefs:
       - name: grpc
     hostnames:
       - "grpc.com"
     rules:
       - matches:
           - method:
               method: ServerReflectionInfo
               service: grpc.reflection.v1alpha.ServerReflection
           - method:
               method: Ping
         backendRefs:
           - name: grpc-echo-svc
             port: 3000
   EOF
   ```

3. Verify that the GRPCRoute is applied successfully.

   ```bash
   kubectl get grpcroute example-route -n {{< reuse "docs/snippets/namespace.md" >}} -o yaml
   ```

   Example output:
   ```console
   status:
     parents:
     - conditions:
       - lastTransitionTime: "yyyy-mm-ddThh:mm:ssZ"
         message: Successfully accepted Route
         observedGeneration: 1
         reason: Accepted
         status: "True"
         type: Accepted
       - lastTransitionTime: "yyyy-mm-ddThh:mm:ssZ"
         message: Successfully resolved all references
         observedGeneration: 1
         reason: ResolvedRefs
         status: "True"
        type: ResolvedRefs
       controllerName: kgateway.dev/kgateway
       parentRef:
         group: gateway.networking.k8s.io
         kind: Gateway
         name: grpc
   ```

## Verify the gRPC route {#verify-grpcroute}

Verify that the gRPC route to the echo service is working. The steps vary depending on whether your Gateway is exposed with a LoadBalancer service or set up for local testing only. 

{{< tabs items="Cloud Provider LoadBalancer,Port-forward for local testing" tabTotal="2" >}}
{{% tab tabName="Cloud Provider LoadBalancer" %}}
1. Send a request to the gRPC echo service by using the gRPC client app. Verify that you see the `pong` message in your response. 
   ```sh
   kubectl exec -n kgateway-system grpcurl-client -c grpcurl -- \
     grpcurl -plaintext -authority grpc.com -vv grpc:80 yages.Echo/Ping
   ```

   Example output: 
   ```console
   {
      "text": "pong"
   }
   ```

2. Optional: Explore other gRPC endpoints. 
   ```sh
   kubectl exec -n kgateway-system grpcurl-client -c grpcurl -- \
     grpcurl -plaintext -authority grpc.com -vv grpc:80 list

   kubectl exec -n kgateway-system grpcurl-client -c grpcurl -- \
     grpcurl -plaintext -authority grpc.com -vv grpc:80 describe yages.Echo
   ```

   Example output: 
   ```console
   grpc.health.v1.Health
   grpc.reflection.v1alpha.ServerReflection
   yages.Echo
   yages.Echo is a service:
   service Echo {
     rpc Ping ( .yages.Empty ) returns ( .yages.Content );
     rpc Reverse ( .yages.Content ) returns ( .yages.Content );
   }
   ```
   
{{% /tab %}}
{{% tab tabName="Port-forward for local testing" %}}
1. Port-forward the gateway proxy pod on port 8080.
   ```sh
   kubectl port-forward svc/grpc -n {{< reuse "docs/snippets/namespace.md" >}} 8080:80
   ```

2. Send a request to the gRPC echo service. Verify that you see the `pong` message in your response. 
   ```sh
   grpcurl -plaintext -authority grpc.com -vv localhost:8080 yages.Echo/Ping
   ```

   Example output: 

   ```console
   {
     "text": "pong"
   }
   ```

3. Optional: Explore other gRPC endpoints. 
   ```sh
   grpcurl -plaintext -authority grpc.com localhost:8080 list
   grpcurl -plaintext -authority grpc.com localhost:8080 describe yages.Echo
   ```

   Example output: 
   ```console
   grpc.health.v1.Health
   grpc.reflection.v1alpha.ServerReflection
   yages.Echo

   yages.Echo is a service:
   service Echo {
     rpc Ping ( .yages.Empty ) returns ( .yages.Content );
     rpc Reverse ( .yages.Content ) returns ( .yages.Content );
   }
   ```

{{% /tab %}}
{{< /tabs >}}

  
## Cleanup

{{< reuse "docs/snippets/cleanup.md" >}}

```bash
kubectl delete grpcroute example-route -n {{< reuse "docs/snippets/namespace.md" >}}
kubectl delete deployment grpc-echo -n {{< reuse "docs/snippets/namespace.md" >}}
kubectl delete service grpc-echo-svc -n {{< reuse "docs/snippets/namespace.md" >}}
kubectl delete pod grpcurl-client -n {{< reuse "docs/snippets/namespace.md" >}}
kubectl delete gateway grpc -n {{< reuse "docs/snippets/namespace.md" >}}
```
