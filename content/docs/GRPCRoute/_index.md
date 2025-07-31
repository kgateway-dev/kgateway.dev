---
title: "GRPC Route"
description: "Route gRPC traffic with the Kubernetes Gateway API GRPCRoute resource"
weight: 15
---

# A Comprehensive Guide to gRPC Routing with GRPCRoute on kgateway

Effectively managing gRPC traffic becomes a crucial infrastructure concern as more and more contemporary cloud-native applications use gRPC due to its strong-typed contracts and high performance. To address this issue, kgateway, a potent Kubernetes Gateway API implementation driven by Envoy, offers reliable and protocol-aware tools.

The best resource for learning how to use kgateway and the GRPCRoute resource to manage gRPC traffic in Kubernetes is this guide. The fundamentals of GRPCRoute will be taught to you, along with practical tutorials on common routing patterns, a comprehensive API reference, and operational insights for executing gRPC services in production.

## Comprehending GRPCRoute

The basic ideas of GRPCRoute are established in this section, so you will know what it is and—more importantly—why it is the best tool for handling gRPC traffic.

### GRPCRoute: What is it?

Within the Kubernetes Gateway API, GRPCRoute is a dedicated, protocol-aware resource specifically made for gRPC request routing. Since version 1.1.0, it has been a part of the Gateway API's Standard Channel and has graduated to General Availability (GA), indicating its stability and preparedness for use in production settings.

GRPCRoute is fully supported by kgateway, a conformant Gateway API implementation that uses Envoy Proxy's functionality and performance to examine gRPC traffic and implement routing rules at Layer 7.

### Why Opt for GRPCRoute for gRPC Traffic Instead of HTTPRoute?

The fact that gRPC uses HTTP/2 raises a frequent query. Can't HTTPRoute handle gRPC since it's made for HTTP traffic? Although technically feasible, it is regarded as an anti-pattern that compromises the Gateway API's objectives.

You would have to set up routing according to the implementation details of the underlying transport protocol if you were using an HTTPRoute. For example, a gRPC call to the com.example's Login method.An HTTP/2 POST request to the path /com.example is mapped to the user service.User/Login. An HTTPRoute could be made to match this particular path. This method, however, is fragile and links the internal operations of the gRPC protocol to the configuration of your infrastructure.

GRPCRoute provides a crucial layer of abstraction. Instead of matching on HTTP paths and methods, GRPCRoute allows you to define routing rules using gRPC-native concepts: the service name and method name.

Consider the difference:

- **HTTPRoute Match**: `path: /com.example.User/Login`, `method: POST`
- **GRPCRoute Match**: `service: com.example.User`, `method: Login`

The GRPCRoute approach is more readable, less error-prone, and aligns with the role-oriented philosophy of the Gateway API. It empowers application developers to define routing logic in terms of their application's API contract, not the transport protocol's encoding details. kgateway handles the translation from this high-level, protocol-aware rule to the necessary low-level Envoy configuration.

### The Role of the Gateway and Listener

The Gateway API decouples infrastructure from application routing using a layered set of resources:

- A **GatewayClass** defines a template for Gateways, managed by the cluster administrator. kgateway automatically creates a GatewayClass named `kgateway` upon installation.
- A **Gateway** requests a traffic entry point (like a cloud load balancer) and defines one or more Listeners. A listener specifies the port, protocol, and other parameters for incoming traffic.
- A **GRPCRoute** attaches to a specific listener on a Gateway to define the actual routing rules for traffic that arrives on that listener.

A critical requirement for GRPCRoute is that it MUST attach to a listener configured with the HTTPS protocol. This means that TLS termination is always handled by kgateway when routing gRPC traffic. Additionally, the Gateway API enforces hostname uniqueness: an implementation must reject a GRPCRoute if it attempts to attach to a listener using a hostname that is already claimed by an HTTPRoute on that same listener.

## Hands-On Tutorial: Routing gRPC Traffic with kgateway

This section provides a practical, step-by-step guide to deploying and managing gRPC services with kgateway.

### Prerequisites

Before you begin, ensure you have the following tools installed and configured:

- A running Kubernetes cluster.
- `kubectl`, the Kubernetes command-line tool.
- `helm`, the Kubernetes package manager.
- `grpcurl`, a command-line tool for interacting with gRPC servers. You can find installation instructions on its [official repository](https://github.com/fullstorydev/grpcurl).

### Installing kgateway

First, install the Gateway API Custom Resource Definitions (CRDs) and then deploy kgateway using its Helm chart.

#### Install Gateway API CRDs

Since GRPCRoute is now GA, the standard channel CRDs are sufficient.

```bash
kubectl apply -k "https://github.com/kubernetes-sigs/gateway-api/config/crd/standard?ref=v1.1.0"
```

#### Install kgateway

Add the kgateway Helm repository and install the chart into the `kgateway-system` namespace.

```bash
helm repo add kgateway oci://cr.kgateway.dev/kgateway-dev/charts
helm repo update
helm install kgateway kgateway/kgateway -n kgateway-system --create-namespace
```

#### Verify the Installation

Check that the kgateway control plane pod is running.

```bash
kubectl get pods -n kgateway-system
```

You should see output similar to this:

```
NAME                        READY   STATUS    RESTARTS   AGE
kgateway-78658959cd-cz6jt   1/1     Running   0          60s
```

### Deploying a Sample gRPC Application

For this tutorial, you will deploy a simple gRPC echo server. This server includes the gRPC Reflection service, which will allow you to dynamically explore its API later on.

Apply the following manifest to create the Deployment and Service for the echo application.

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
  name: grpc-echo-v1
  labels:
    app: grpc-echo
    version: v1
spec:
  replicas: 1
  selector:
    matchLabels:
      app: grpc-echo
      version: v1
  template:
    metadata:
      labels:
        app: grpc-echo
        version: v1
    spec:
      containers:
      - name: grpc-echo
        image: docker.io/soloio/grpc-echo-server:v0.1.0
        imagePullPolicy: IfNotPresent
        ports:
        - containerPort: 9000
        env:
        - name: POD_NAME
          valueFrom:
            fieldRef:
              fieldPath: metadata.name
EOF
```

## Scenario 1: Basic Hostname-Based Routing

Your first goal is to expose the gRPC service to the outside world by routing all traffic for the hostname `grpc.example.com` to the `grpc-echo` service.

### Step 1: Create a TLS Certificate

Because GRPCRoute requires an HTTPS listener, you must provide a TLS certificate. For this tutorial, you will generate a self-signed certificate.

Generate the certificate and private key using `openssl`.

```bash
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout grpc.example.com.key \
  -out grpc.example.com.crt \
  -subj "/CN=grpc.example.com"
```

Create a Kubernetes Secret to store the certificate. The Gateway resource will reference this secret.

```bash
kubectl create secret tls grpc-example-com-cert \
  --key grpc.example.com.key \
  --cert grpc.example.com.crt
```

### Step 2: Deploy a Gateway

Now, create a Gateway resource that uses the `kgateway` GatewayClass. This Gateway will listen on port 443 for HTTPS traffic and use the TLS secret you just created.

```yaml
kubectl apply -f - <<EOF
apiVersion: gateway.networking.k8s.io/v1
kind: Gateway
metadata:
  name: grpc-gateway
spec:
  gatewayClassName: kgateway
  listeners:
  - name: https
    protocol: HTTPS
    port: 443
    hostname: "grpc.example.com"
    tls:
      mode: Terminate
      certificateRefs:
      - name: grpc-example-com-cert
    allowedRoutes:
      namespaces:
        from: Same
EOF
```

### Step 3: Create the GRPCRoute

Next, create the GRPCRoute to direct traffic from the Gateway to your service. This route attaches to the `grpc-gateway` and defines a single, default rule to forward all traffic for `grpc.example.com` to the `grpc-echo` service.

```yaml
kubectl apply -f - <<EOF
apiVersion: gateway.networking.k8s.io/v1
kind: GRPCRoute
metadata:
  name: echo-route
spec:
  parentRefs:
  - name: grpc-gateway
  hostnames:
  - "grpc.example.com"
  rules:
  - backendRefs:
    - name: grpc-echo
      port: 9000
EOF
```

### Step 4: Test with grpcurl

With all the resources deployed, you can now test the configuration.

Get the external IP address of the gateway.

```bash
export GATEWAY_IP=$(kubectl get gateway grpc-gateway -o jsonpath='{.status.addresses[0].value}')
echo $GATEWAY_IP
```

Send a request using grpcurl. The following command sends an echo request to your service through the gateway.

- `-insecure`: Skips TLS certificate validation, necessary because you are using a self-signed certificate.
- `-authority grpc.example.com`: Sets the Host header, which is used by kgateway for SNI and hostname-based routing.
- `-d '{"text": "hello world"}'`: Provides the request payload in JSON format.

```bash
grpcurl -insecure \
  -authority grpc.example.com \
  -d '{"text": "hello world"}' \
  $GATEWAY_IP:443 \
  echo.Echo/Echo
```

You should receive a successful response from the v1 pod:

```json
{
  "text": "hello world",
  "source": "grpc-echo-v1-..."
}
```

## Scenario 2: Advanced Content-Based Routing

Now, you will implement a more complex scenario: an A/B test where traffic is routed based on a request header, alongside method-based routing.

### Step 1: Deploy a v2 "Canary" Service

First, deploy a second version of the echo application. This will serve as your canary deployment.

```yaml
kubectl apply -f - <<EOF
apiVersion: apps/v1
kind: Deployment
metadata:
  name: grpc-echo-v2
  labels:
    app: grpc-echo
    version: v2
spec:
  replicas: 1
  selector:
    matchLabels:
      app: grpc-echo
      version: v2
  template:
    metadata:
      labels:
        app: grpc-echo
        version: v2
    spec:
      containers:
      - name: grpc-echo
        image: docker.io/soloio/grpc-echo-server:v0.1.0
        imagePullPolicy: IfNotPresent
        ports:
        - containerPort: 9000
        env:
        - name: POD_NAME
          valueFrom:
            fieldRef:
              fieldPath: metadata.name
EOF
```

You also need a dedicated Kubernetes Service for this v2 deployment.

```yaml
kubectl apply -f - <<EOF
apiVersion: v1
kind: Service
metadata:
  name: grpc-echo-v2
  labels:
    app: grpc-echo
spec:
  ports:
  - port: 9000
    name: grpc
  selector:
    app: grpc-echo
    version: v2
EOF
```

### Step 2: Update the GRPCRoute

Modify the GRPCRoute to include multiple rules. The Gateway API specifies that the most specific match wins. Therefore, you will place the header-based match first.

- **Rule 1**: Matches requests with the header `env: canary` and routes them to the `grpc-echo-v2` service.
- **Rule 2**: Matches requests to the specific `EchoV2` method and also routes them to the `grpc-echo-v2` service.
- **Rule 3**: The default rule, which catches all other traffic and routes it to the original `grpc-echo` (v1) service.

```yaml
kubectl apply -f - <<EOF
apiVersion: gateway.networking.k8s.io/v1
kind: GRPCRoute
metadata:
  name: echo-route
spec:
  parentRefs:
  - name: grpc-gateway
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

### Step 3: Test Each Rule

Now, test each routing condition independently.

**Test the header-based route.** Include the `-H 'env: canary'` flag to send the request to the v2 service.

```bash
grpcurl -insecure \
  -H 'env: canary' \
  -authority grpc.example.com \
  -d '{"text": "hello canary"}' \
  $GATEWAY_IP:443 \
  echo.Echo/Echo
```

The response should come from the v2 pod:

```json
{
  "text": "hello canary",
  "source": "grpc-echo-v2-..."
}
```

**Test the method-based route.** Call the `EchoV2` method, which should also route to the v2 service.

```bash
grpcurl -insecure \
  -authority grpc.example.com \
  -d '{"text": "hello method"}' \
  $GATEWAY_IP:443 \
  echo.Echo/EchoV2
```

The response should again come from the v2 pod.

**Test the default route.** Make a standard request without the header or special method. It should be routed to the v1 service.

```bash
grpcurl -insecure \
  -authority grpc.example.com \
  -d '{"text": "hello default"}' \
  $GATEWAY_IP:443 \
  echo.Echo/Echo
```

The response should come from the v1 pod.

## Scenario 3: Enabling Dynamic Interaction with gRPC Reflection

gRPC Reflection is a service protocol that allows clients to query a server for its available RPCs at runtime, eliminating the need for clients to have pre-compiled `.proto` files. This is incredibly useful for developer tooling.

### Step 1: Update the GRPCRoute for Reflection

To enable reflection through the gateway, you must add a routing rule that explicitly matches the gRPC Reflection service and forwards the request to your backend application (which is running the reflection service).

Update your GRPCRoute to include this new match. It should be placed before the default rule.

```yaml
kubectl apply -f - <<EOF
apiVersion: gateway.networking.k8s.io/v1
kind: GRPCRoute
metadata:
  name: echo-route
spec:
  parentRefs:
  - name: grpc-gateway
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
  - matches:
    - method:
        service: "echo.Echo"
        method: "EchoV2"
    backendRefs:
    - name: grpc-echo-v2
      port: 9000
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

### Step 2: Explore the API with grpcurl

With reflection enabled, you can now use grpcurl's discovery commands without providing local `.proto` files.

**List all available services on the server.**

```bash
grpcurl -insecure \
  -authority grpc.example.com \
  $GATEWAY_IP:443 \
  list
```

The output will show the services implemented by your application, plus the reflection service itself:

```
echo.Echo
grpc.reflection.v1alpha.ServerReflection
```

**Describe a specific service to see its methods.**

```bash
grpcurl -insecure \
  -authority grpc.example.com \
  $GATEWAY_IP:443 \
  describe echo.Echo
```

The output details the service definition:

```
echo.Echo is a service:
service Echo {
  rpc Echo (.echo.EchoRequest ) returns (.echo.EchoResponse );
  rpc EchoV2 (.echo.EchoRequest ) returns (.echo.EchoResponse );
}
```

**Describe a message to see its fields.**

```bash
grpcurl -insecure \
  -authority grpc.example.com \
  $GATEWAY_IP:443 \
  describe echo.EchoRequest
```

This command shows the structure of the request message:

```
echo.EchoRequest is a message:
message EchoRequest {
  string text = 1;
}
```

This dynamic exploration capability significantly improves the developer experience when working with gRPC services behind kgateway.

## GRPCRoute API Reference

This section provides a technical reference for the fields within the GRPCRoute resource specification (`spec`). It is based on the official Gateway API standards that kgateway implements.

| Field               | Type              | Required | Description                                                                                                                                                                                                                                                   |
| ------------------- | ----------------- | -------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `parentRefs`        | `ParentReference` | Yes      | A list of parent resources this route attaches to. For kgateway, this will be a Gateway resource. The name and namespace identify the Gateway, while `sectionName` (matching a listener name) or `port` selects the specific listener to attach to.           |
| `hostnames`         | `Hostname`        | No       | A list of hostnames to match against the request's Host header (or SNI in TLS). Wildcards are supported (e.g., `*.example.com`). If both the Listener and GRPCRoute specify hostnames, there must be an intersection for the route to be accepted.            |
| `rules`             | `GRPCRouteRule`   | Yes      | A list of rules that define matching criteria and forwarding behavior. Rules are evaluated in order, and the first rule that matches the request is used.                                                                                                     |
| `rules.matches`     | `GRPCRouteMatch`  | No       | A list of match conditions. A request must satisfy any of the matches in this list for the rule to apply. If matches is omitted, the rule is a default catch-all for the hostnames. Matches can be on method (with service and method sub-fields) or headers. |
| `rules.filters`     | `GRPCRouteFilter` | No       | An extension point for processing requests or responses. Filters can modify requests/responses (e.g., `RequestHeaderModifier`) or perform other actions. kgateway may support implementation-specific filters.                                                |
| `rules.backendRefs` | `BackendRef`      | No       | A list of backend Kubernetes Service objects to forward traffic to. If multiple backends are specified, traffic can be split between them using the weight field. The name, namespace, and port identify the target service.                                  |

## Operational Guide & Best Practices

This section covers common operational tasks, troubleshooting, and advanced patterns for managing GRPCRoute resources in a production environment.

### Checking Route Status

The primary tool for diagnosing issues with a GRPCRoute is its status field. You can inspect it with kubectl.

```bash
kubectl get grpcroute echo-route -o yaml
```

The most important part of the status is the parents array, which shows the condition of the route with respect to each Gateway it tries to attach to.

```yaml
status:
  parents:
    - parentRef:
        name: grpc-gateway
        namespace: default
      controllerName: kgateway.dev/kgateway-controller
      conditions:
        - lastTransitionTime: "2024-05-20T18:00:00Z"
          message: "Route is accepted"
          reason: Accepted
          status: "True"
          type: Accepted
        - lastTransitionTime: "2024-05-20T18:00:00Z"
          message: "All references are resolved"
          reason: ResolvedRefs
          status: "True"
          type: ResolvedRefs
```

- **Accepted Condition**: This tells you if the Gateway controller has accepted the route. If status is "False", check the reason and message for details. Common reasons for rejection include listener protocol mismatches or conflicts with other routes.
- **ResolvedRefs Condition**: This indicates whether the controller could successfully resolve all references within the route, such as the Service specified in backendRefs. If status is "False", it usually means the backend service does not exist or is in a different namespace without proper permissions.

### Common Pitfalls and Troubleshooting

- **Listener Protocol Mismatch**: A GRPCRoute can only attach to an HTTPS listener. If you try to attach it to an HTTP listener, the Accepted condition will be False.
- **Hostname Conflict**: If an HTTPRoute is already attached to a listener for `grpc.example.com`, your GRPCRoute for the same hostname on the same listener will be rejected. Hostnames must be unique per listener across HTTPRoute and GRPCRoute.
- **TLS Configuration Errors**: If the Gateway listener status shows it is not ready, verify that the TLS Secret referenced in certificateRefs exists, is valid, and is in the correct namespace.
- **Backend Not Found**: If the ResolvedRefs condition is False, ensure the Service named in backendRefs exists and that its namespace and port are correct. If the Service is in a different namespace from the GRPCRoute, you will need a ReferenceGrant.

### Advanced Pattern: Cross-Namespace Routing

In production, it is common for a platform team to manage a central Gateway in a dedicated namespace (e.g., `kgateway-system`), while application teams deploy their GRPCRoute and Service resources in their own namespaces.

To make this work securely, the Gateway API uses the ReferenceGrant resource. A ReferenceGrant is created by the owner of the target resource (the "to" side) to explicitly permit a reference from another resource (the "from" side).

For example, to allow a GRPCRoute in the `app-namespace` to attach to a Gateway in the `kgateway-system` namespace, the platform team would create the following ReferenceGrant in the `kgateway-system` namespace:

```yaml
apiVersion: gateway.networking.k8s.io/v1beta1
kind: ReferenceGrant
metadata:
  name: allow-grpcroutes-from-app-namespace
  namespace: kgateway-system
spec:
  from:
    - group: gateway.networking.k8s.io
      kind: GRPCRoute
      namespace: app-namespace
  to:
    - group: gateway.networking.k8s.io
      kind: Gateway
```

This object grants permission for any GRPCRoute in `app-namespace` to reference any Gateway in `kgateway-system`. This explicit, directional grant is a key security feature of the Gateway API.

## Appendix: Gateway API Route Comparison

The Gateway API provides several route types to handle different protocols. Choosing the correct one is essential for a well-architected system. This table provides a quick comparison of the primary L4/L7 route types supported by kgateway.

| Route Type | OSI Layer | Routing Discriminator                         | TLS Support               | Primary Use Case on kgateway                                                                    |
| ---------- | --------- | --------------------------------------------- | ------------------------- | ----------------------------------------------------------------------------------------------- |
| GRPCRoute  | Layer 7   | gRPC Service/Method, Headers                  | Terminated Only           | For routing gRPC traffic with protocol-aware rules.                                             |
| HTTPRoute  | Layer 7   | HTTP Host/Path, Headers, Query Params, Method | Terminated Only           | For all standard HTTP/HTTPS traffic, including REST APIs and websites.                          |
| TCPRoute   | Layer 4   | Destination Port, SNI (for TLS)               | Passthrough or Terminated | For non-HTTP TCP traffic (e.g., databases, message queues) or when TLS passthrough is required. |
| UDPRoute   | Layer 4   | Destination Port                              | None                      | For forwarding UDP streams (e.g., DNS, game servers).                                           |

## Cleanup

Remove the example resources:

```bash
kubectl delete gateway grpc-gateway
kubectl delete grpcroute echo-route
kubectl delete service grpc-echo grpc-echo-v2
kubectl delete deployment grpc-echo-v1 grpc-echo-v2
kubectl delete secret grpc-example-com-cert
```

## Next steps

- Explore [AI Gateway](/docs/ai-gateway/) features for LLM gRPC traffic
- Configure [external processing](/docs/reference/api/ext-proc/) for custom gRPC filters
- Set up [observability](/docs/observability/) for gRPC traffic monitoring
- Learn about [traffic policies](/docs/traffic-management/traffic-policies/) for advanced gRPC management
