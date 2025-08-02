---
title: gRPC services
weight: 10
description: Route traffic to gRPC services using GRPCRoute.
---

Route traffic to gRPC services using the GRPCRoute resource for protocol-aware routing.

## About

GRPCRoute provides protocol-aware routing for gRPC traffic within the Kubernetes Gateway API. Unlike HTTPRoute, which requires matching on HTTP paths and methods, GRPCRoute allows you to define routing rules using gRPC-native concepts like service and method names.

Consider the difference:
- **HTTPRoute Match**: `path: /com.example.User/Login`, `method: POST`
- **GRPCRoute Match**: `service: com.example.User`, `method: Login`

The GRPCRoute approach is more readable, less error-prone, and aligns with the Gateway API's role-oriented philosophy.

## Before you begin

1. [Set up kgateway](/docs/setup/).
2. Install `grpcurl` for testing: [Installation guide](https://github.com/fullstorydev/grpcurl).
3. Deploy the sample gRPC service (covered in the next section).

## Deploy a sample gRPC service

Deploy a gRPC echo server for testing:

```yaml
kubectl apply -f - <<EOF
apiVersion: v1
kind: Service
metadata:
  name: grpc-echo
  labels:
    app: grpc-echo
spec:
  ports:
  - port: 9000
    name: grpc
  selector:
    app: grpc-echo
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: grpc-echo
  labels:
    app: grpc-echo
spec:
  replicas: 1
  selector:
    matchLabels:
      app: grpc-echo
  template:
    metadata:
      labels:
        app: grpc-echo
    spec:
      containers:
      - name: grpc-echo
        image: docker.io/soloio/grpc-echo-server:v0.1.0
        ports:
        - containerPort: 9000
EOF
```

## Set up the Gateway for gRPC routes

Create an HTTPS listener so that the gateway can route gRPC traffic. GRPCRoute requires HTTPS listeners for TLS termination.

1. Create a TLS certificate for testing:

   ```bash
   openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
     -keyout grpc.example.com.key \
     -out grpc.example.com.crt \
     -subj "/CN=grpc.example.com"
   
   kubectl create secret tls grpc-example-com-cert \
     --key grpc.example.com.key \
     --cert grpc.example.com.crt
   ```

2. Create a Gateway resource with an HTTPS listener:

   ```yaml
   kubectl apply -f - <<EOF
   apiVersion: gateway.networking.k8s.io/v1
   kind: Gateway
   metadata:
     name: grpc-gateway
     namespace: kgateway-system
     labels:
       app: grpc-echo
   spec:
     gatewayClassName: kgateway
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
         kinds:
         - kind: GRPCRoute
   EOF
   ```

   {{< reuse "docs/snippets/review-table.md" >}}

   | Setting | Description |
   |---------|-------------|
   | `spec.gatewayClassName` | The name of the Kubernetes GatewayClass. When you set up kgateway, a default GatewayClass is set up for you. |
   | `spec.listeners` | Configure the listeners for this Gateway. GRPCRoute requires HTTPS listeners with TLS termination. |
   | `hostname` | The hostname for SNI-based routing. Must match the hostname in your GRPCRoute. |
   | `tls.mode: Terminate` | Terminates TLS at the gateway, required for GRPCRoute. |

3. Check the status of the Gateway:

   ```bash
   kubectl get gateway grpc-gateway -n kgateway-system -o yaml
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

4. Create a ReferenceGrant to allow GRPCRoutes to reference the grpc-echo service:

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
       namespace: kgateway-system
     to:
     - group: ""
       kind: Service
   EOF
   ```

## Create a GRPCRoute

1. Create the GRPCRoute resource. For detailed information about GRPCRoute fields and configuration options, see the [Gateway API GRPCRoute documentation](https://gateway-api.sigs.k8s.io/reference/spec/#gateway.networking.k8s.io/v1.GRPCRoute).

   ```yaml
   kubectl apply -f - <<EOF
   apiVersion: gateway.networking.k8s.io/v1
   kind: GRPCRoute
   metadata:
     name: grpc-echo-route
     namespace: kgateway-system
     labels:
       app: grpc-echo
   spec:
     parentRefs:
     - name: grpc-gateway
       namespace: kgateway-system
       sectionName: https
     hostnames:
     - "grpc.example.com"
     rules:
     - backendRefs:
       - name: grpc-echo
         namespace: default
         port: 9000
   EOF
   ```

2. Verify that the GRPCRoute is applied successfully:

   ```bash
   kubectl get grpcroute grpc-echo-route -n kgateway-system -o yaml
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
         namespace: kgateway-system
         sectionName: https
   ```

## Verify the gRPC route

Verify that the gRPC route to the echo service is working.

1. Get the external address of the gateway and save it in an environment variable:

   {{< tabs tabTotal="2" items="Cloud Provider LoadBalancer,Port-forward for local testing" >}}
   {{% tab tabName="Cloud Provider LoadBalancer" %}}
   ```bash
   export GATEWAY_IP=$(kubectl get gateway grpc-gateway -n kgateway-system -o jsonpath='{.status.addresses[0].value}')
   echo $GATEWAY_IP
   ```
   {{% /tab %}}
   {{% tab tabName="Port-forward for local testing" %}}
   ```bash
   kubectl port-forward deployment/grpc-gateway -n kgateway-system 8443:443
   export GATEWAY_IP=localhost:8443
   ```
   {{% /tab %}}
   {{< /tabs >}}

2. Send a gRPC request to test the route:

   {{< tabs tabTotal="2" items="Cloud Provider LoadBalancer,Port-forward for local testing" >}}
   {{% tab tabName="Cloud Provider LoadBalancer" %}}
   ```bash
   grpcurl -insecure \
     -authority grpc.example.com \
     -d '{"text": "hello world"}' \
     $GATEWAY_IP:443 \
     echo.Echo/Echo
   ```
   {{% /tab %}}
   {{% tab tabName="Port-forward for local testing" %}}
   ```bash
   grpcurl -insecure \
     -authority grpc.example.com \
     -d '{"text": "hello world"}' \
     localhost:8443 \
     echo.Echo/Echo
   ```
   {{% /tab %}}
   {{< /tabs >}}

   Expected response:
   ```json
   {
     "text": "hello world",
     "source": "grpc-echo-..."
   }
   ```

## Advanced routing patterns

### Method-based routing

Route specific gRPC methods to different backend services:

```yaml
kubectl apply -f - <<EOF
apiVersion: gateway.networking.k8s.io/v1
kind: GRPCRoute
metadata:
  name: grpc-echo-route
spec:
  parentRefs:
  - name: https-gateway
    namespace: kgateway-system
  hostnames:
  - "grpc.example.com"
  rules:
  - matches:
    - method:
        service: "echo.Echo"
        method: "EchoV2"
    backendRefs:
    - name: grpc-echo-v2
      port: 9000
  - backendRefs:
    - name: grpc-echo
      port: 9000
EOF
```

### Header-based routing

Route requests based on headers for A/B testing:

```yaml
kubectl apply -f - <<EOF
apiVersion: gateway.networking.k8s.io/v1
kind: GRPCRoute
metadata:
  name: grpc-echo-route
spec:
  parentRefs:
  - name: https-gateway
    namespace: kgateway-system
  hostnames:
  - "grpc.example.com"
  rules:
  - matches:
    - headers:
      - type: Exact
        name: "env"
        value: "canary"
    backendRefs:
    - name: grpc-echo-v2
      port: 9000
  - backendRefs:
    - name: grpc-echo
      port: 9000
EOF
```

Test with header:
```bash
grpcurl -insecure \
  -H 'env: canary' \
  -authority grpc.example.com \
  -d '{"text": "hello canary"}' \
  $GATEWAY_IP:443 \
  echo.Echo/Echo
```

### Enable gRPC Reflection

Add routing for gRPC Reflection to enable dynamic API exploration:

```yaml
kubectl apply -f - <<EOF
apiVersion: gateway.networking.k8s.io/v1
kind: GRPCRoute
metadata:
  name: grpc-echo-route
spec:
  parentRefs:
  - name: https-gateway
    namespace: kgateway-system
  hostnames:
  - "grpc.example.com"
  rules:
  - matches:
    - method:
        service: "grpc.reflection.v1alpha.ServerReflection"
    backendRefs:
    - name: grpc-echo
      port: 9000
  - backendRefs:
    - name: grpc-echo
      port: 9000
EOF
```

Explore the API dynamically:
```bash
# List services
grpcurl -insecure -authority grpc.example.com $GATEWAY_IP:443 list

# Describe a service
grpcurl -insecure -authority grpc.example.com $GATEWAY_IP:443 describe echo.Echo
```

## Troubleshooting

Check the GRPCRoute status for issues:

```bash
kubectl get grpcroute grpc-echo-route -o yaml
```

Common issues:
- **Listener Protocol Mismatch**: GRPCRoute requires HTTPS listeners
- **Hostname Conflict**: Hostnames must be unique per listener across HTTPRoute and GRPCRoute
- **Backend Not Found**: Verify the Service exists and ports are correct
- **Cross-namespace Access**: Use ReferenceGrant for cross-namespace routing

## Next steps

{{< cards >}}
  {{< card link="/docs/traffic-management/traffic-policies/" title="Traffic policies" >}}
  {{< card link="/docs/observability/" title="Observability" >}}
  {{< card link="/docs/ai/" title="AI Gateway for gRPC" >}}
{{< /cards >}}

## Cleanup

Remove the resources that you created in this guide:

```bash
kubectl delete -A gateways,grpcroutes,pod,svc,secrets -l app=grpc-echo
kubectl delete referencegrant allow-grpc-route-to-echo -n default
```