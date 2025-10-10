---
title: gRPC services
weight: 20
description: Route traffic to gRPC services using GRPCRoute.
next: /docs/traffic-management/destination-types/backends
---

Route traffic to gRPC services using the GRPCRoute resource for protocol-aware routing.

## About

GRPCRoute provides protocol-aware routing for gRPC traffic within the Kubernetes Gateway API. Unlike HTTPRoute, which requires matching on HTTP paths and methods, GRPCRoute allows you to define routing rules using gRPC-native concepts like service and method names.

Consider the difference:
- **HTTPRoute Match**: `path:/com.example.User/Login`, `method: POST`
- **GRPCRoute Match**: `service: yages.Echo`, `method: Ping`

The GRPCRoute approach is more readable, less error-prone, and aligns with the Gateway API's role-oriented philosophy.

## Before you begin

1. [Install {{< reuse "/docs/snippets/kgateway.md" >}}](/docs/quickstart/).
2. [Install `grpcurl` for testing](https://github.com/fullstorydev/grpcurl).

## Deploy a sample gRPC service {#sample-grpc}

Deploy a sample gRPC service for testing purposes. The sample service has two APIs:

- `yages.Echo.Ping`: Takes no input (empty message) and returns a `pong` message.
- `yages.Echo.Reverse`: Takes input content and returns the content in reverse order, such as `hello world` becomes `dlrow olleh`.

Steps to set up the sample gRPC service:

1. Deploy the gRPC echo server and client.

   ```yaml
   kubectl apply -f - <<EOF
   apiVersion: apps/v1
   kind: Deployment
   metadata:
     name: grpc-echo
   spec:
     selector:
       matchLabels:
         app: grpc-echo
     replicas: 1
     template:
       metadata:
         labels:
           app: grpc-echo
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
   spec:
     type: ClusterIP
     ports:
       - port: 3000
         protocol: TCP
         targetPort: 9000
         appProtocol: kubernetes.io/h2c
     selector:
       app: grpc-echo
   ---
   apiVersion: v1
   kind: Pod
   metadata:
     name: grpcurl-client
   spec:
     containers:
       - name: grpcurl
         image: docker.io/fullstorydev/grpcurl:v1.8.7-alpine
         command:
           - sleep
           - "infinity"
   EOF
   ```

2. Create a ReferenceGrant to allow GRPCRoutes to reference the gRPC echo service.

   ```yaml
   kubectl apply -f - <<EOF
   apiVersion: gateway.networking.k8s.io/v1beta1
   kind: ReferenceGrant
   metadata:
     name: allow-grpc-route-to-echo
     namespace: default
   spec:
     from:
     - group: gateway.networking.k8s.io
       kind: GRPCRoute
       namespace: {{< reuse "docs/snippets/namespace.md" >}}
     to:
     - group: ""
       kind: Service
   EOF
   ```

## Set up the Gateway for gRPC routes {#gateway}

Create an HTTPS listener so that the gateway can route gRPC traffic. GRPCRoute requires HTTPS listeners for TLS termination. For more information, see the [HTTPS listener guide](../../../../setup/listeners/https/).

1. Create a TLS certificate for testing.

   ```bash
   openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
     -keyout grpc.example.com.key \
     -out grpc.example.com.crt \
     -subj "/CN=grpc.example.com"
   
   kubectl create secret tls grpc-example-com-cert \
     -n {{< reuse "docs/snippets/namespace.md" >}} \
     --key grpc.example.com.key \
     --cert grpc.example.com.crt
   ```

2. Create a Gateway resource with an HTTPS listener.

   ```yaml
   kubectl apply -f - <<EOF
   apiVersion: gateway.networking.k8s.io/v1
   kind: Gateway
   metadata:
     name: grpc-gateway
     namespace: {{< reuse "docs/snippets/namespace.md" >}}
     labels:
       app: grpc-echo
   spec:
     gatewayClassName: {{< reuse "/docs/snippets/gatewayclass.md" >}}
     listeners:
     - protocol: HTTPS
       port: 443
       name: https
       hostname: "grpc.example.com"
       tls:
         mode: Terminate
         certificateRefs:
         - name: grpc-example-com-cert
       allowedRoutes:
         namespaces:
           from: All
   EOF
   ```

   {{< reuse "docs/snippets/review-table.md" >}}

   | Setting | Description |
   |---------|-------------|
   | `spec.gatewayClassName` | The name of the Kubernetes GatewayClass. When you set up {{< reuse "/docs/snippets/kgateway.md" >}}, a default GatewayClass is set up for you. |
   | `spec.listeners` | Configure the listeners for this Gateway. GRPCRoute requires HTTPS listeners with TLS termination. |
   | `hostname` | The hostname for SNI-based routing. Must match the hostname in your GRPCRoute. |
   | `tls.mode: Terminate` | Terminates TLS at the gateway, required for GRPCRoute. |

3. Check the status of the Gateway.

   ```bash
   kubectl get gateway grpc-gateway -n {{< reuse "docs/snippets/namespace.md" >}} -o yaml
   ```

   Example output:
   ```yaml
   status:
     addresses:
     - type: IPAddress
       value: ${INGRESS_GW_ADDRESS}
     conditions:
     - lastTransitionTime: "2024-11-20T16:01:25Z"
       message: ""
       observedGeneration: 2
       reason: Accepted
       status: "True"
       type: Accepted
     - lastTransitionTime: "2024-11-20T16:01:25Z"
       message: ""
       observedGeneration: 2
       reason: Programmed
       status: "True" 
       type: Programmed
   ```

## Create a GRPCRoute {#create-grpcroute}

1. Create the GRPCRoute resource. Include the `grpc.reflection.v1alpha.ServerReflection` method to enable dynamic API exploration. For detailed information about GRPCRoute fields and configuration options, see the [Gateway API GRPCRoute documentation](https://gateway-api.sigs.k8s.io/reference/spec/#gateway.networking.k8s.io/v1.GRPCRoute).

   ```yaml
   kubectl apply -f - <<EOF
   apiVersion: gateway.networking.k8s.io/v1
   kind: GRPCRoute
   metadata:
     name: grpc-echo-route
     namespace: {{< reuse "docs/snippets/namespace.md" >}}
     labels:
       app: grpc-echo
   spec:
     parentRefs:
     - name: grpc-gateway
       namespace: {{< reuse "docs/snippets/namespace.md" >}}
       sectionName: https
     hostnames:
     - "grpc.example.com"
     rules:
     - matches:
       - method:
           service: "grpc.reflection.v1alpha.ServerReflection"
       backendRefs:
       - name: grpc-echo-svc
         namespace: default
         port: 3000
     - backendRefs:
       - name: grpc-echo-svc
         namespace: default
         port: 3000
   EOF
   ```

2. Verify that the GRPCRoute is applied successfully.

   ```bash
   kubectl get grpcroute grpc-echo-route -n {{< reuse "docs/snippets/namespace.md" >}} -o yaml
   ```

   Example output:
   ```yaml
   status:
     parents:
     - conditions:
       - lastTransitionTime: "2024-11-21T16:22:52Z"
         message: ""
         observedGeneration: 1
         reason: Accepted
         status: "True"
         type: Accepted
       - lastTransitionTime: "2024-11-21T16:22:52Z"
         message: ""
         observedGeneration: 1
         reason: ResolvedRefs
         status: "True"
         type: ResolvedRefs
       controllerName: kgateway.dev/kgateway
       parentRef:
         group: gateway.networking.k8s.io
         kind: Gateway
         name: grpc-gateway
         namespace: {{< reuse "docs/snippets/namespace.md" >}}
         sectionName: https
   ```

## Verify the gRPC route {#verify-grpcroute}

Verify that the gRPC route to the echo service is working.

1. Get the external address of the gateway and save it in an environment variable.

   {{< tabs tabTotal="2" items="Cloud Provider LoadBalancer,Port-forward for local testing" >}}
   {{% tab tabName="Cloud Provider LoadBalancer" %}}
   ```bash
   export GATEWAY_IP=$(kubectl get gateway grpc-gateway -n {{< reuse "docs/snippets/namespace.md" >}} -o jsonpath='{.status.addresses[0].value}')
   echo $GATEWAY_IP
   ```
   {{% /tab %}}
   {{% tab tabName="Port-forward for local testing" %}}
   ```bash
   kubectl port-forward svc/grpc-gateway -n {{< reuse "docs/snippets/namespace.md" >}} 8443:443
   ```
   {{% /tab %}}
   {{< /tabs >}}

2. Explore the API dynamically.

   {{< tabs tabTotal="2" items="Cloud Provider LoadBalancer,Port-forward for local testing" >}}
   {{% tab tabName="Cloud Provider LoadBalancer" %}}
   ```bash
   grpcurl -insecure -authority grpc.example.com $GATEWAY_IP:443 list
   grpcurl -insecure -authority grpc.example.com $GATEWAY_IP:443 describe yages.Echo
   ```
   {{% /tab %}}
   {{% tab tabName="Port-forward for local testing" %}}
   ```bash
   grpcurl -insecure -authority grpc.example.com localhost:8443 list
   grpcurl -insecure -authority grpc.example.com localhost:8443 describe yages.Echo
   ```
   {{% /tab %}}
   {{< /tabs >}}

   Expected response:
   ```
   grpc.health.v1.Health
   grpc.reflection.v1alpha.ServerReflection
   yages.Echo
   yages.Echo is a service:
   service Echo {
     rpc Ping ( .yages.Empty ) returns ( .yages.Content );
     rpc Reverse ( .yages.Content ) returns ( .yages.Content );
   }
   ```

3. Send a gRPC request to test the route.

   {{< tabs tabTotal="2" items="Cloud Provider LoadBalancer,Port-forward for local testing" >}}
   {{% tab tabName="Cloud Provider LoadBalancer" %}}
   ```bash
   grpcurl -insecure \
     -authority grpc.example.com \
     $GATEWAY_IP:443 \
     yages.Echo/Ping
   ```
   {{% /tab %}}
   {{% tab tabName="Port-forward for local testing" %}}
   ```bash
   grpcurl -insecure \
     -authority grpc.example.com \
     localhost:8443 \
     yages.Echo/Ping
   ```
   {{% /tab %}}
   {{< /tabs >}}

   Expected response:
   ```json
   {
     "text": "pong"
   }
   ```

## Next steps

Explore the traffic management, resiliency, and security policies that you can apply to make your gRPC services more robust and secure.

{{< cards >}}
  {{< card link="../../../../traffic-management/" title="Traffic management" >}}
  {{< card link="../../../../resiliency/" title="Resiliency" >}}
  {{< card link="../../../../security/" title="Security" >}}
{{< /cards >}}

## Cleanup

{{< reuse "docs/snippets/cleanup.md" >}}

```bash
kubectl delete -A gateways,grpcroutes,pod,svc,secrets -l app=grpc-echo
kubectl delete referencegrant allow-grpc-route-to-echo -n default
```
