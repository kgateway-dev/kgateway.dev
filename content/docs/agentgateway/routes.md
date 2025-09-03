---
title: Routes
weight: 20
---

The agentgateway data plane supports the Gateway API routing resources, including HTTPRoute, GRPCRoute, TCPRoute, and TLSRoute.

## Before you begin

{{< reuse "docs/snippets/prereq-agw.md" >}}

## HTTP

Use agentgateway to proxy HTTP requests to your backend services.

1. Follow the [Sample HTTP app](../../operations/sample-app/) instructions to create a sample HTTP app, a Gateway with an HTTP listener that uses the `agentgateway` GatewayClass, and an HTTPRoute.

2. Check out the following guides for more advanced routing use cases.

   * [Traffic management](../../traffic-management/)
   * [Resiliency](../../resiliency/)
   * [Security](../../security/)
   * [AI](../../ai/)

## Routes to external services {#static}

Follow the [Static backend](../../traffic-management/destination-types/backends/static/) guide to create a static backend for an external HTTP service. Then, use an HTTPRoute to route traffic to that service through your agentgateway. When you set up your Gateway, make sure to use the `agentgateway` GatewayClass.

## gRPC

Use agentgateway to proxy gRPC requests to your backend services.

1. Deploy a gRPC sample echo app and a sample gRPC curl client.

   ```yaml
   kubectl apply -f- <<EOF
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

2. Create a Gateway that uses the `agentgateway` GatewayClass and an HTTP listener that can be used for gRPC.

   ```yaml
   kubectl apply -f- <<EOF
   kind: Gateway
   apiVersion: gateway.networking.k8s.io/v1
   metadata:
     name: agentgateway
   spec:
     gatewayClassName: agentgateway
     listeners:
       - protocol: HTTP
         port: 8080
         name: http
         allowedRoutes:
           namespaces:
             from: All
   EOF
   ```

3. Create a GRPCRoute that routes traffic to the sample echo app.

   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.networking.k8s.io/v1
   kind: GRPCRoute
   metadata:
     name: grpc-route
   spec:
     parentRefs:
       - name: agentgateway
     hostnames:
       - "example.com"
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

4. Get the address of the Gateway for your gRPC routes.
   
   {{< tabs items="Cloud Provider LoadBalancer,Port-forward for local testing" tabTotal="2"  >}}
   {{% tab tabName="Cloud Provider LoadBalancer" %}}
   ```sh
   export INGRESS_GW_ADDRESS=$(kubectl get svc -n default agentgateway -o jsonpath="{.status.loadBalancer.ingress[0]['hostname','ip']}")
   echo $INGRESS_GW_ADDRESS  
   ```
   {{% /tab %}}
   {{% tab tabName="Port-forward for local testing"  %}}
   ```sh
   kubectl port-forward deployment/agentgateway -n default 8080:8080
   ```
   {{% /tab %}}
   {{< /tabs >}}

5. Send a request to the gRPC server with the `grpcurl` client. If you do not have this client locally, you can log in to the gRPC client pod that you previously deployed.

   {{< tabs items="Cloud Provider LoadBalancer,Port-forward for local testing" tabTotal="2"  >}}
   {{% tab tabName="Cloud Provider LoadBalancer" %}}
   ```sh
   grpcurl \
     -plaintext \
     -authority example.com \
     -d '{}' $INGRESS_GW_ADDRESS$:8080 yages.Echo/Ping 
   ```
   {{% /tab %}}
   {{% tab tabName="Port-forward for local testing"  %}}
   ```sh
   grpcurl \
     -plaintext \
     -authority example.com \
     -d '{}' localhost:8080 yages.Echo/Ping 
   ```
   {{% /tab %}}
   {{< /tabs >}}

   Example output:
   
   ```json
   {
     "text": "pong"
   }
   ```

6. Optional: {{< reuse "docs/snippets/cleanup.md" >}}
   
   ```sh
   kubectl delete Deployment grpc-echo
   kubectl delete Service grpc-echo-svc
   kubectl delete Pod grpcurl-client
   kubectl delete Gateway agentgateway
   kubectl delete GRPCRoute grpc-route
   ```

## TCP

Follow the [TCP listener guide](../../setup/listeners/tcp/) to create a TCP listener and a TCPRoute. 

Make sure to create the Gateway with the `agentgateway` GatewayClass.

Example TCP listener configuration:

{{< tabs items="Gateway listeners,ListenerSets (experimental)" tabTotal="2" >}}
{{% tab tabName="Gateway listeners" %}}
```yaml
kubectl apply -f- <<EOF
apiVersion: gateway.networking.k8s.io/v1
kind: Gateway
metadata:
  name: tcp-gateway
  namespace: {{< reuse "docs/snippets/namespace.md" >}}
  labels:
    app: tcp-echo
spec:
  gatewayClassName: {{< reuse "/docs/snippets/agw-gatewayclass.md" >}}
  listeners:
  - protocol: TCP
    port: 8000
    name: tcp
    allowedRoutes:
      kinds:
      - kind: TCPRoute
EOF
```
 
{{< reuse "docs/snippets/review-table.md" >}}
 
|Setting|Description|
|--|--|
|`spec.gatewayClassName`| The name of the Kubernetes GatewayClass that you want to use to configure the Gateway. When you set up {{< reuse "docs/snippets/kgateway.md" >}}, a default GatewayClass is set up for you. {{< reuse "docs/snippets/agw-gatewayclass-choice.md" >}}|
|`spec.listeners`|Configure the listeners for this Gateway. In this example, you configure a TCP Gateway that listens for incoming traffic on port 8000. The Gateway can serve TCPRoutes from any namespace. |

{{% /tab %}}
{{% tab tabName="ListenerSets (experimental)" %}}

1. Create a Gateway that enables the attachment of ListenerSets.

   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.networking.k8s.io/v1
   kind: Gateway
   metadata:
     name: tcp-gateway
     namespace: {{< reuse "docs/snippets/namespace.md" >}}
     labels:
       app: tcp-echo
   spec:
     gatewayClassName: {{< reuse "/docs/snippets/agw-gatewayclass.md" >}}
     allowedListeners:
       namespaces:
         from: All
     listeners:
     - protocol: TCP
       port: 80
       name: generic-tcp
       allowedRoutes:
         kinds:
         - kind: TCPRoute
   EOF
   ```

   {{< reuse "docs/snippets/review-table.md" >}}

   |Setting|Description|
   |---|---|
   |`spec.gatewayClassName`|The name of the Kubernetes GatewayClass that you want to use to configure the Gateway. When you set up {{< reuse "docs/snippets/kgateway.md" >}}, a default GatewayClass is set up for you. {{< reuse "docs/snippets/agw-gatewayclass-choice.md" >}} |
   |`spec.allowedListeners`|Enable the attachment of ListenerSets to this Gateway. The example allows listeners from any namespace.|
   |`spec.listeners`|{{< reuse "docs/snippets/generic-listener.md" >}} In this example, the generic listener is configured on port 80, which differs from port 8000 in the ListenerSet that you create later.|

2. Create a ListenerSet that configures a TCP listener for the Gateway.

   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.networking.x-k8s.io/v1alpha1
   kind: XListenerSet
   metadata:
     name: my-tcp-listenerset
     namespace: {{< reuse "docs/snippets/namespace.md" >}}
     labels:
       app: tcp-echo
   spec:
     parentRef:
       name: tcp-gateway
       namespace: {{< reuse "docs/snippets/namespace.md" >}}
       kind: Gateway
       group: gateway.networking.k8s.io
     listeners:
     - protocol: TCP
       port: 8000
       name: tcp-listener-set
       allowedRoutes:
         kinds:
         - kind: TCPRoute
   EOF
   ```

   {{< reuse "docs/snippets/review-table.md" >}}

   |Setting|Description|
   |--|--|
   |`spec.parentRef`|The name of the Gateway to attach the ListenerSet to. |
   |`spec.listeners`|Configure the listeners for this ListenerSet. In this example, you configure a TCP listener for port 8000. The gateway can serve TCPRoutes from any namespace. |
{{% /tab %}}
{{< /tabs >}}

## TLS

Follow the [TLS listener guide](../../setup/listeners/tls/) to create a TLS listener and a TLSRoute. Make sure to create the Gateway with the `agentgateway` GatewayClass.

Example TLS listener configuration:

{{< tabs items="Gateway listeners,ListenerSets (experimental)" tabTotal="2" >}}
{{% tab tabName="Gateway listeners" %}}
1. Create a Gateway that passes through incoming TLS requests for the `nginx.example.com` domain.

   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.networking.k8s.io/v1
   kind: Gateway
   metadata:
     name: tls-passthrough
     namespace: {{< reuse "docs/snippets/namespace.md" >}}
   spec:
     gatewayClassName: {{< reuse "/docs/snippets/agw-gatewayclass.md" >}}
     listeners:
     - name: tls
       protocol: TLS
       hostname: "nginx.example.com"
       tls:
         mode: Passthrough
       port: 8443
       allowedRoutes:
         namespaces:
           from: All
   EOF
   ```

   {{< reuse "docs/snippets/review-table.md" >}}

   |Setting|Description|
   |---|---|
   |`spec.gatewayClassName`|The name of the Kubernetes GatewayClass that you want to use to configure the Gateway. When you set up {{< reuse "docs/snippets/kgateway.md" >}}, a default GatewayClass is set up for you. {{< reuse "docs/snippets/agw-gatewayclass-choice.md" >}}|
   |`spec.listeners`|Configure the listeners for this Gateway. In this example, you configure a TLS passthrough Gateway that listens for incoming traffic for the `nginx.example.com` domain on port 8443. The Gateway can serve TLS routes from any namespace.|
   |`spec.listeners.tls.mode`|The TLS mode for incoming requests. In this example, TLS requests are passed through to the backend service without being terminated at the Gateway.|

{{% /tab %}}
{{% tab tabName="ListenerSets (experimental)" %}}

1. Create a Gateway that enables the attachment of ListenerSets.

   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.networking.k8s.io/v1
   kind: Gateway
   metadata:
     name: tls-passthrough
     namespace: {{< reuse "docs/snippets/namespace.md" >}}
   spec:
     gatewayClassName: {{< reuse "/docs/snippets/agw-gatewayclass.md" >}}
     allowedListeners:
       namespaces:
         from: All
     listeners:
     - protocol: TLS
       port: 80
       name: generic-tls
       allowedRoutes:
         namespaces:
           from: All
   EOF
   ```

   {{< reuse "docs/snippets/review-table.md" >}}

   |Setting|Description|
   |---|---|
   |`spec.gatewayClassName`|The name of the Kubernetes GatewayClass that you want to use to configure the Gateway. When you set up {{< reuse "docs/snippets/kgateway.md" >}}, a default GatewayClass is set up for you. {{< reuse "docs/snippets/agw-gatewayclass-choice.md" >}} |
   |`spec.allowedListeners`|Enable the attachment of ListenerSets to this Gateway. The example allows listeners from any namespace.|
   |`spec.listeners`|{{< reuse "docs/snippets/generic-listener.md" >}} In this example, the generic listener is configured on port 80, which differs from port 443 in the ListenerSet that you create later.|

2. Create a ListenerSet that configures a TLS passthrough listener for the Gateway.

   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.networking.x-k8s.io/v1alpha1
   kind: XListenerSet
   metadata:
     name: my-tls-listenerset
     namespace: {{< reuse "docs/snippets/namespace.md" >}}
   spec:
     parentRef:
       name: tls-passthrough
       namespace: {{< reuse "docs/snippets/namespace.md" >}}
       kind: Gateway
       group: gateway.networking.k8s.io
     listeners:
     - protocol: TLS
       port: 8443
       hostname: nginx.example.com
       name: tls-listener-set
       tls:
         mode: Passthrough
       allowedRoutes:
         namespaces:
           from: All
   EOF
   ```

   {{< reuse "docs/snippets/review-table.md" >}}

   |Setting|Description|
   |--|--|
   |`spec.parentRef`|The name of the Gateway to attach the ListenerSet to.|
   |`spec.listeners`|Configure the listeners for this ListenerSet. In this example, you configure a TLS passthrough listener for the `nginx.example.com` domain on port 8443.|
   |`spec.listeners.tls.mode`|The TLS mode for incoming requests. TLS requests are passed through to the backend service without being terminated at the Gateway.|

{{% /tab %}}
{{< /tabs >}}