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
Before integrating kagteway with Istio Ambient, ensure we have: 
1. Set-up `kind` cluster.
2. Setup Kuberntes Gateway API:
   ```
   kubectl apply --server-side -f https://github.com/kubernetes-sigs/gateway-api/releases/download/v1.4.0/experimental-install.yaml
   ```
4. Follow the [Get started guide](https://kgateway.dev/docs/latest/quickstart/) to install kgateway.
5. Follow the [Sample app guide](https://kgateway.dev/docs/latest/install/sample-app/) to create a gateway proxy with an HTTP listener and deploy the httpbin sample app.
6. Set up an ambient mesh in your cluster to secure service-to-service communication with mutual TLS by following the [ambientmesh.io](https://ambientmesh.io/docs/quickstart/) quickstart documentation.
7. Deploy the Ollama Container at port number 11434, binding to 0.0.0.0 so the Kubernetes virtual machine can access it via the host's bridge network.
   ```
   docker run -d -v ollama:/root/.ollama -p 11434:11434 -e OLLAMA_HOST=0.0.0.0 ollama/ollama --name ollama-server
   ```
8. Get the Container IP of ollama which will be inserted at all the **`address filds` which is 127.17.0.2 in our case.
   ```
   docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' ollama-server
   ```


While Istio ambient provides Authorization, Authentication and Egress still, there are several scenarios where kgateway can offer a more powerful alternative:

## Securely Egress Traffic with kGateway + Istio Integration

To establish a dedicated, policy-enforced egress path, we must combine three core resources: the **Istio ServiceEntry** (to register the external host), the **kGateway Egress Gateway** (to serve as the L7 egress waypoint), and the **HTTPRoute** (to apply the routing and security logic).

* Our target is an external Ollama container running on the host machine (host.docker.internal) on the default port 11434 and `ServiceEntries` injects the external Ollama endpoint into the Istio service registry for which we'll use static resolution for our local Docker Desktop bridge.
* Define the Gateway resource, leveraging the kgateway GatewayClass to instantiate a dedicated proxy that is explicitly listening for outbound traffic to the Ollama host with an HTTPRoute.

```yaml
kubectl apply -f - <<EOF
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
   # Container_IP address of your ollama conatiner
  - 127.17.0.2/32
  location: MESH_EXTERNAL
  ports:
  - number: 11434
    name: http-ollama
    protocol: HTTP
  resolution: DNS
  endpoints:
   # IP that the egress proxy attempts to connect to
  - address: 127.17.0.2
    ports:
      http-ollama: 11434
---

# egress-kgateway.yaml
apiVersion: gateway.networking.k8s.io/v1
kind: Gateway
metadata:
  name: egress-kgateway
  namespace: default
spec:
  gatewayClassName: kgateway
  listeners:
    - protocol: HTTP
      port: 8080
      name: http
      allowedRoutes:
        namespaces:
          from: All
---

# ollama-egress-route.yaml
apiVersion: gateway.networking.k8s.io/v1
kind: HTTPRoute
metadata:
  name: ollama-egress-route
  namespace: default 
spec:
  parentRefs:
  - name: egress-kgateway
    sectionName: http
  hostnames:
  - "host.docker.internal"
  rules:
  - backendRefs:
    - name: ollama-external-host
      port: 11434
      kind: ServiceEntry
      group: "networking.istio.io"
EOF
```
## Managing CEL based RBAC and integrating exAuth with Kyverno into our Request FLow
<!-- For exmple - Kyverno for applying with demo video
-->
While CEL RBAC (from the next section) is powerful for checking native Istio identities and headers, scenarios like API key validation, integration with corporate IdPs (Identity Providers), or checking complex external policies require delegating the decision outside the mesh proxy. This is where kGateway’s External Authorization (ExtAuth) feature, coupled with Kyverno, shines.

kGateway allows us to easily delegate the authorization step for the Ollama API call to an external gRPC service, implementing a Zero Trust defense-in-depth strategy. 
```
# Kyverno Envoy Plugin ExtAuth Configuration
kubectl apply -f - <<EOF
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
      name: kyverno-authz-server
---
# GatewayExtension defines the Kyverno server endpoint
apiVersion: gateway.kgateway.dev/v1alpha1
kind: GatewayExtension
metadata:
  name: kyverno-authz-server
  namespace: default
spec:
  type: ExtAuth
  extAuth:
    grpcService:
      backendRef:
        name: kyverno-authz-server
        port: 9081
---
# Kyverno AuthorizationPolicy (Envoy CRD) defines the L7 logic
apiVersion: envoy.kyverno.io/v1alpha1
kind: AuthorizationPolicy
metadata:
  name: demo-policy.example.com
spec:
  failurePolicy: Fail
  variables:
  - name: force_authorized
    expression: object.attributes.request.http.?headers["x-force-authorized"].orValue("")
  - name: allowed
    expression: variables.force_authorized in ["enabled", "true"]
  # The core authorization rule
  authorizations:
  - expression: >
      variables.allowed
        ? envoy.Allowed().Response()
        : envoy.Denied(403).Response()
EOF
```
This step involves configuring a TrafficPolicy to delegate authorization and a GatewayExtension to define the Kyverno server's network endpoint. AuthorizationPolicy will define the L7 logic through authorization rules with variables define based on the custom header presence.

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
kubectl apply -f - <<EOF
apiVersion: apps/v1
kind: Deployment
metadata:
  name: curl-test-client
  namespace: default
  labels:
    app: curl-client
    istio.io/dataplane-mode: ambient
spec:
  replicas: 1
  selector:
    matchLabels:
      app: curl-client
  template:
    metadata:
      labels:
        app: curl-client
        istio.io/dataplane-mode: ambient
    spec:
      containers:
      - name: client
        image: curlimages/curl
        # Keep the container running indefinitely for testing
        command: ["sleep", "3600"] 
        imagePullPolicy: IfNotPresent
EOF
```

### Testinig Client
We will use the client app to execute tests against the host.docker.internal via the kGateway path.

1. Authorized Test (With Required Header)
This test should be allowed because the header x-force-authorized: true satisfies the Kyverno Envoy AuthorizationPolicy. The traffic is then proxied by kGateway to the Ollama container.
```
kubectl exec -it deploy/curl-test-client -n default -- curl [http://egress-kgateway.istio-system:8080/](http://egress-kgateway.istio-system:8080/) -v -H "Host: host.docker.internal" -H "x-force-authorized: true"
```

Expected Output:
```
< HTTP/1.1 200 OK
...
Ollama is running%
```
# Demo

