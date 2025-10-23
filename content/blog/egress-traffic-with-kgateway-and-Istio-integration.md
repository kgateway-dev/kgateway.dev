---
title: "Egress Traffic with kgateway and Istio Integration"
toc: 
author: Aryan Parashar
excludeSearch: 
---

Ambeint Mesh is a sidecar-less data plane that can help us manage our  workloads in a tranparent, Secure and Better Resource usage manner. If someone is struggling with an invasive, high computation overhead and cost operation of service mesh then Ambient Mesh can be a lot better choice for their applciation workloads. Istio Ambient Mesh helps to provide Lower Computation Overhead and Cost operations by splitting its data plane into two layers: the secure overlay layer and Layer 7 waypoint proxy layer. 

This seperation of layers can help users to choose between the implementation and seperation of Layer 1(L4) and Layer 7(L7) behavior of their workloads. Amibient's Secure Overlay Layer handles Layer 4 behaviors including establishing mTLS and telemetry collections with a flexibility to choose what they want for their infrastructure without introducing unnecessary risk.

## kgateway's integration with Ambient Mesh
kgateway integrates to Ambient Mesh for managing our workloads through Layer 4 and Layer 7 network policies. But the thing that sets its apart from other Gateway solutions is that, Kgateway is the first project that can be used as a pluggable waypoint for Istio. 
Kgateway has been built on same Envoy engine that Istio’s waypoint implementation uses, which has certain features including Istio API Compatability, Shared Observability, Faster Adoption of Security Featrues and Unified Configurational Model with Ambient Mesh.

## Istio Authorization Policy for zero trust. Cover the difference of L4 vs. L7 auth policies
<!-- Differences between Layer 4 and Layer 7 policies to cover how do they effect our workloads under Ingress and Egress Traffic.
-->
# How important is kgateway's integration
While Istio ambient provides Authorization, Authentication and Egress still, there are several scenarios where kgateway can offer a more powerful alternative:

## Securely Egress Traffic with kGateway + Istio Integration

To establish a dedicated, policy-enforced egress path, we must combine three core resources: the **Istio ServiceEntry** (to register the external host), the **kGateway Egress Gateway** (to serve as the L7 egress waypoint), and the **HTTPRoute** (to apply the routing and security logic).

* Our target is an external Ollama container running on the host machine (host.docker.internal) on the default port 11434 and `ServiceEntries` injects the external Ollama endpoint into the Istio service registry for which we'll use static resolution for our local Docker Desktop bridge.
* Define the Gateway resource, leveraging the kgateway GatewayClass to instantiate a dedicated proxy that is explicitly listening for outbound traffic to the Ollama host with an HTTPRoute.

```yaml
# ollama-serviceentry.yaml
apiVersion: networking.istio.io/v1beta1
kind: ServiceEntry
metadata:
  name: ollama-external-host
  namespace: default
  labels:
    security.corp/egress-approved: "true" # Kyverno policy validation target
spec:
  hosts:
  - "host.docker.internal"
  addresses:
  - 127.0.0.1/32
  ports:
  - number: 11434
    name: http-ollama
    protocol: HTTP
  location: MESH_EXTERNAL
  resolution: STATIC
  endpoints:
  - address: 127.0.0.1 # IP that the egress proxy attempts to connect to
    ports:
      http-ollama: 11434

# egress-kgateway.yaml
apiVersion: gateway.networking.k8s.io/v1
kind: Gateway
metadata:
  name: egress-kgateway
  namespace: istio-system 
spec:
  gatewayClassName: kgateway 
  listeners:
  - name: egress-ollama-http
    port: 11434 
    protocol: HTTP
    hostname: "host.docker.internal" 
    allowedRoutes:
      namespaces:
        from: All

# ollama-egress-route.yaml
apiVersion: gateway.networking.k8s.io/v1
kind: HTTPRoute
metadata:
  name: ollama-egress-route
  namespace: default 
spec:
  parentRefs:
  - name: egress-kgateway
    namespace: istio-system
    sectionName: egress-ollama-http
  hostnames:
  - "host.docker.internal"
  rules:
  - backendRefs:
    - name: ollama-external-host
      port: 11434
```
## Managing CEL based RBAC and integrating exAuth with Kyverno into our Request FLow
<!-- For exmple - Kyverno for applying with demo video
-->
While CEL RBAC (from the next section) is powerful for checking native Istio identities and headers, scenarios like API key validation, integration with corporate IdPs (Identity Providers), or checking complex external policies require delegating the decision outside the mesh proxy. This is where kGateway’s External Authorization (ExtAuth) feature, coupled with Kyverno, shines.

kGateway allows us to easily delegate the authorization step for the Ollama API call to an external gRPC service, implementing a Zero Trust defense-in-depth strategy.
```YAML
# External Auth Service and Deployment (in istio-system)
kubectl apply -f - <<EOF
apiVersion: apps/v1
kind: Deployment
metadata:
  namespace: istio-system
  name: ext-authz-server
  labels: {app: ext-authz}
spec:
  selector: {matchLabels: {app: ext-authz}}
  template:
    metadata: {labels: {app: ext-authz}}
    spec:
      containers:
      - name: ext-authz
        # Using a mock GRPC AuthZ server for simplicity
        image: gcr.io/istio-testing/ext-authz-grpc:latest 
        imagePullPolicy: IfNotPresent
        ports:
        - containerPort: 9000
---
apiVersion: v1
kind: Service
metadata:
  namespace: istio-system
  name: ext-authz-server-svc
  labels: {app: ext-authz}
spec:
  ports:
  - name: grpc-authz
    port: 9000
    targetPort: 9000
    protocol: TCP
  selector:
    app: ext-authz
EOF
---
# kGateway External Auth Policy
apiVersion: gateway.kgateway.dev/v1alpha1
kind: TrafficPolicy
metadata:
  name: ollama-external-auth-policy
  namespace: default
spec:
  targetRefs:
  - group: gateway.networking.k8s.io
    kind: HTTPRoute
    name: ollama-egress-route 
  extAuth:
    extensionRef:
      name: ext-authz-server-svc.istio-system.svc.cluster.local 
      port: 9000 
      protocol: GRPC
    failOpen: false
    requestAttributes:
      allowedHeaders: ["x-ollama-apikey"]
```
# Kyverno Configuration Policy/ Configuration Governance

This ClusterPolicy ensures that any time a ServiceEntry is created for an external host, the developer must include the security label `security.corp/egress-approved: "true"`. This fulfills the requirement of using Kyverno for security governance on the configuration plane.

```YAML
kubectl apply -f - <<EOF
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata:
  name: enforce-serviceentry-egress-label
spec:
  validationFailureAction: Enforce 
  background: false 
  rules:
  - name: require-approved-egress-label
    match:
      any:
      - resources:
          kinds: ["ServiceEntry"]
          names: ["ollama-external-host"]
    validate:
      message: "External ServiceEntries must include the label 'security.corp/egress-approved: true' to ensure policy review."
      pattern:
        metadata:
          labels:
            security.corp/egress-approved: "?*"
EOF
```
# See it in Action/ Testing

To test the security policies applied by kGateway, we use a simple Pod named curl-test-client. Its primary role is to serve as the mesh-enabled client that originates the outbound traffic, allowing us to test Layer 4 security (mTLS) and Layer 7 policies (CEL RBAC/ExtAuth). It is labeled for Ambient Mesh enrollment.

```YAML
# Kubernetes Manifest: client-pod.yaml
apiVersion: v1
kind: Pod
metadata:
  name: curl-test-client
  namespace: default
  labels:
    app: curl-client
    istio.io/dataplane-mode: ambient
spec:
  containers:
  - name: client
    image: curlimages/curl
    command: ["sleep", "3600"]
    imagePullPolicy: IfNotPresent
```
We will use the client pod to execute tests against the ollama-external-host via the kGateway path. All tests below assume successful completion of the Host Firewall Fix.
# Demo

