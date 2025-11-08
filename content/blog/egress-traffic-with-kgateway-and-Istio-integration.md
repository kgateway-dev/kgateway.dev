---
title: "Egress Traffic with kgateway and Istio Integration"
toc: 
author: Aryan Parashar
excludeSearch: 
---

[Istio Ambient Mesh](https://ambientmesh.io/docs/about/overview/) is a sidecar-less data plane model designed to reduce operational overhead and improve resource efficiency for service-to-service communication. Instead of using per-pod sidecar proxies, Ambient splits its data plane into two layers:

* **Secure Overlay Layer (L4)** — Handled by the lightweight *ztunnel*, providing mTLS, identity, and network telemetry.
* **Waypoint Proxy Layer (L7)** — Handles application-layer policies such as routing, authentication, RBAC, and external authorization.

This separation lets platform teams choose when L7 processing is necessary, reducing cost and computational overhead for workloads that only require transport security.

## Kgateway's integration with Ambient Mesh
kgateway integrates to Ambient Mesh for managing our workloads through Layer 4 and Layer 7 network policies. But the thing that sets its apart from other Gateway solutions is that, Kgateway is the first project that can be used as a pluggable waypoint for Istio. 
Kgateway has been built on same Envoy engine that Istio’s waypoint implementation uses, which has certain features including Istio API Compatability, Shared Observability, Faster Adoption of Security Featrues and Unified Configurational Model with Ambient Mesh.

## Prepare your kgateway environment
Before integrating kagteway with Istio Ambient, ensure we have: 
1. Follow the [Get started guide](https://kgateway.dev/docs/latest/quickstart/) to install kgateway in a kind cluster
2. Follow the [Sample app guide](https://kgateway.dev/docs/latest/install/sample-app/) to create a gateway proxy with an HTTP listener and deploy the httpbin sample app.
3. Set up an ambient mesh in your cluster to secure service-to-service communication with mutual TLS by following the [ambientmesh.io](https://ambientmesh.io/docs/quickstart/) quickstart documentation.
4. Deploy the Ollama Container at port number 11434, binding to 0.0.0.0 so the Kubernetes virtual machine can access it via the host's bridge network.
   ```
   docker run -d -v ollama:/root/.ollama -p 11434:11434 -e OLLAMA_HOST=0.0.0.0 ollama/ollama --name ollama-server
   ```
5. Get the Container IP of ollama container which will be inserted at all the **`address filds` which is 172.17.0.2 in our case.
   ```
   docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' <CONTIANER_NAME>
   ```
   Here it will get container's IP as an output:
   ```
   172.17.0.2
   ```
7. Deploy the Kyverno Authz Server as a GRPC server capable of processing Envoy External Authorization requests.
   ```
   helm install kyverno-authz-server --namespace default --create-namespace --wait \
   --version 0.1.0 --repo https://kyverno.github.io/kyverno-envoy-plugin \
   kyverno-authz-server
   ```

While Istio ambient provides Authorization, Authentication and Egress still, there are several scenarios where kgateway can offer a more powerful alternative:

## Securely Egress Traffic with kGateway + Istio Integration

To establish a dedicated, policy-enforced egress path, we must combine three core resources: the **Istio ServiceEntry** (to register the external host), the **kGateway Egress Gateway**, and the **HTTPRoute** (to apply the routing and security logic).

* Our target is an external Ollama container running on the host machine (host.docker.internal) on the default port 11434 and `ServiceEntries` injects the external Ollama endpoint into the Istio service registry for which we'll use static resolution for our local Docker Desktop bridge.
* Define the Gateway resource, leveraging the kgateway GatewayClass to instantiate a dedicated proxy that is explicitly listening for outbound traffic to the Ollama host with an HTTPRoute.

```yaml
kubectl apply -f - <<EOF
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

apiVersion: networking.istio.io/v1beta1
kind: ServiceEntry
metadata:
  name: ollama-external-host
  namespace: default
  labels:
    security.corp/egress-approved: "true"
spec:
  hosts:
  - "host.docker.internal"
  location: MESH_EXTERNAL
  ports:
  - number: 11434
    name: http-ollama
    protocol: HTTP
  resolution: DNS
---

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

While CEL RBAC (from the next section) is powerful for checking native Istio identities and headers, scenarios like API key validation, integration with corporate IdPs (Identity Providers), or checking complex external policies require delegating the decision outside the mesh proxy. This is where kGateway’s External Authorization (ExtAuth) feature, coupled with Kyverno, shines.

kGateway allows us to easily delegate the authorization step for the Ollama API call to an external gRPC service, implementing a Zero Trust defense-in-depth strategy. 
```YAML
kubectl apply -f - <<EOF
apiVersion: gateway.kgateway.dev/v1alpha1   # TrafficPolicy for ExtAuth + Corrected kGateway Resilience
kind: TrafficPolicy
metadata:
  name: ollama-external-auth-policy
  namespace: default
spec:
  targetRefs:
  - group: gateway.networking.k8s.io
    kind: HTTPRoute
    name: ollama-egress-route
  retry:
    attempts: 3
    perTryTimeout: 10s
    statusCodes:
    - 503
    - 504
  timeouts:
   request: 30s
  extAuth:
    extensionRef:
      name: kyverno-authz-server
---

apiVersion: gateway.kgateway.dev/v1alpha1   # GatewayExtension defines the Kyverno server endpoint
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

apiVersion: envoy.kyverno.io/v1alpha1   # Kyverno AuthorizationPolicy: RESTORING SECURITY (Conditional Access)
kind: AuthorizationPolicy
metadata:
  name: demo-policy.example.com
  namespace: default
spec:
  failurePolicy: Fail
  variables:
  - name: force_authorized
    expression: object.attributes.request.http.?headers["x-force-authorized"].orValue("")
  - name: allowed
    expression: variables.force_authorized in ["enabled", "true"]
  authorizations:
  - expression: >
      variables.allowed
        ? envoy.Allowed().Response()
        : envoy.Denied(403).Response()
EOF
```
This step involves configuring a TrafficPolicy to delegate authorization with kgateway native resiliency features for retires & timeouts then we have deployed a GatewayExtension to define the Kyverno server's network endpoint. AuthorizationPolicy will define the L7 logic through authorization rules with variables define based on the custom header presence.

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

### Deploy the test client

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
        command: ["sleep", "3600"] 
        imagePullPolicy: IfNotPresent
EOF
```

### Verify authorization policies for the Ollama service
We will use the client app that we previously deployed to execute tests against the `host.docker.internal` domain through the kgateway egress gateway.

Authorized Test (With Required Header)
This test should be allowed because the header x-force-authorized: true satisfies the Kyverno Envoy AuthorizationPolicy. The traffic is then proxied by kGateway to the Ollama container.
```sh
kubectl exec -it deploy/curl-test-client -n default -- curl http://egress-kgateway.default:8080/ -v -H "Host: host.docker.internal" -H "x-force-authorized: true"
```

Expected Output:
```sh
< HTTP/1.1 200 OK
...
Ollama is running%
```

### Verify retry policies on the Kyverno server

While the TrafficPolicy defines the retry logic (attempts: 3, on 503 or 504), we must prove that the kgateway egress gateway actually executes the retries when an upstream service fails. We will simulate an upstream connection failure by temporarily pausing the external Ollama container.
```sh
docker pause ollama-server   # Pause the container that is running the external Ollama service
echo "Ollama container is paused. Proceeding to send request..."
kubectl exec -it deploy/curl-test-client -n default -- curl http://egress-kgateway.default:8080/ -v -H "Host: host.docker.internal" -H "x-force-authorized: true"
```
Send a request. kgateway will try three times (as configured by attempts: 3 in the TrafficPolicy) before ultimately failing and returning a 5xx error to the client.

Now let's look at the logs from the kgateway egress gateway pod. We look for the final access log entry, which must contain the URX and UF flags to prove the retries occurred.

```sh
KGW_POD=$(kubectl get pods -n default -l gateway.networking.k8s.io/gateway-name=egress-kgateway -o jsonpath='{.items[0].metadata.name}')   # Get the pod name for the egress-kgateway

kubectl logs $KGW_POD -n default | grep 'POST /api/generate' | tail -n 1   # View the last request log entry
```
You should see an output similar to the following:
```
{
  "response_flags": "URX,UF",
  "upstream_transport_failure_reason": "delayed connect error: Connection refused",
  "attempt_count": 2
}
```
# Demo

[Demo](https://youtu.be/5PegECeu0v0)


{{< youtube 5PegECeu0v0 >}}
