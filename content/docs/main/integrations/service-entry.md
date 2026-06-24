---
title: ServiceEntries
weight: 20 # (Assuming a logical weight after External Auth, adjust as needed)
description: Register and route external services through kgateway using Istio ServiceEntries.
---

By creating a ServiceEntry, you can extend kgateway's capabilities to manage traffic for external services, even if they aren't a part of Istio's service registry. This allows you to apply traffic management, security, and observability features to a wider range of endpoints, such as virtual machines (VMs) communicating with services in your Kubernetes cluster.

# ServiceEntries with kgateway

An **[Istio ServiceEntry](https://istio.io/latest/docs/reference/config/networking/service-entry/)** is a Kubernetes custom resource that allows you to integrate and manage external services within your Istio service mesh. kgateway supports ServiceEntries for services residing outside your Kubernetes cluster. Whether it’s a legacy application, a third-party API, or a remote database, ServiceEntries allow you to treat these external dependencies as first-class citizens of your mesh, in addition to applying kgateway policies.

The `ServiceEntry` resource offers flexible mechanisms to define how these external services are discovered and addressed, tailored to different operational needs:

* **Static Endpoints:** Uses explicitly defined IP addresses or hostnames as endpoints.

* **DNS Resolution:** Dynamically discovers endpoints by performing a DNS lookup on the specified host.

* **Workload Selector:** Routes traffic to in-mesh workloads that match a specific set of Kubernetes labels.

* **Workload Entry**: Integrates non-Kubernetes workloads, such as virtual machines or bare-metal servers, into the service mesh.

## Before You Begin

1. Follow the [Get started guide](https://kgateway.dev/docs/main/quickstart/)  to install kgateway.
2. Follow the [Sample app guide](https://kgateway.dev/docs/main/operations/sample-app/) to create a gateway proxy with an HTTP listener and deploy the httpbin sample app.
3. Follow the [Istio documentation](https://istio.io/latest/docs/ambient/getting-started/) to install Istio and set up [Ambient Mesh](https://kgateway.dev/docs/main/integrations/istio/ambient/ambient-ingress/) in your cluster. 

## Targeting ServiceEntry Backends with HTTPRoute and TrafficPolicies

1. Create a Testing Namespace `gwtest` to deploy our Gateways, HTTPRoutes and ServiceEntries.

```yaml
kubectl create namespace gwtest
```

2. The `Gateway` resource, listens for HTTP traffic on port `8080`. The `HTTPRoute`, then matches incoming requests for the hostname and directs them to a backend specified as an Istio `ServiceEntry`. This separation of concerns means the ingress logic remains constant, while the `ServiceEntry` itself dictates the backend's discovery and resolution strategy.

```yaml
kubectl apply -f - <<EOF
kind: Gateway
apiVersion: gateway.networking.k8s.io/v1
metadata:
  name: http-gw-for-test
  namespace: gwtest
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
apiVersion: gateway.networking.k8s.io/v1beta1
kind: HTTPRoute
metadata:
  name: route-to-upstream
  namespace: gwtest
spec:
  parentRefs:
  - name: http-gw-for-test
  hostnames:
  - "se.example.com"
  rules:
  - backendRefs:
    - name: example-se
      port: 80
      kind: ServiceEntry
      group: networking.istio.io
EOF
```

3. A TrafficPolicy allows you to modify the behavior of traffic on a specific route, adding advanced rules like timeouts, retries, and request transformations. This example applies a 5-second timeout and 3 retries to any traffic that goes through the HTTPRoute you have already defined

```yaml
kubectl apply -f - <<EOF
apiVersion: gateway.networking.k8s.io/v1alpha2
kind: TrafficPolicy
metadata:
  name: external-service-policy
  namespace: gwtest
spec:
  targetRef:
    kind: HTTPRoute
    name: route-to-upstream
  http:
    timeout: 5s
    retry:
      retries: 3
      perTryTimeout: 2s
EOF
```

## Full Code Examples & Use Cases

Building on the common kgateway and HTTPRoute configuration, these examples demonstrate how different `ServiceEntry` types are implemented to integrate various external service scenarios.

### 1\. Static Endpoints

This configuration is the most straightforward, designed for external services with fixed, known network addresses. It's an excellent choice for integrating a legacy database, an on-premises application with a stable IP, or for controlled test environments.

The `ServiceEntry` explicitly lists the IP addresses of the external service in the `endpoints` array. With `resolution: STATIC`, Istio directly distributes traffic among these predefined addresses.

```yaml
kubectl apply -f - <<EOF
apiVersion: networking.istio.io/v1
kind: ServiceEntry
metadata:
  name: example-se
  namespace: gwtest
spec:
  hosts:
  - se.example.com
  ports:
  - number: 80
    name: http
    protocol: TCP
  resolution: STATIC
  location: MESH_INTERNAL
  endpoints:
  - address: 1.1.1.1
    locality: r1/z1/sz1
  - address: 2.2.2.2
    locality: r1/z1/sz1
  - address: 3.3.3.3
    locality: r3/z3/sz3
EOF
```
#### Verification Process 
The goal is to simulate a request from inside the mesh and confirm that the Istio sidecar proxy correctly routes it to one of the static endpoints you defined in the ServiceEntry YAML.
```
# Deploy a Test Pod & Verify Hostname Resolution
kubectl run -it test-pod --image=busybox:latest -- /bin/sh
nslookup se.example.com
```
You will see an output as: 
```
Name:      se.example.com
Address 1: 10.14.2.14 # This is the sidecar proxy's IP
```
 **Stimulate a Request & Inspect an Envoy Configuration**
```
# Note: Replace with the actual port your service is listening on
curl -s http://se.example.com/api/info
# (Find a pod running in your namespace, e.g., 'reviews-v1-abcde-fghij')
kubectl get pods
# Then, check its Envoy configuration with the Envoy Pod name
istioctl proxy-config endpoints <POD_NAME> | grep example-se

```
This command will show you a list of the configured endpoints for the example-se ServiceEntry, which should directly display 1.1.1.1, 2.2.2.2, and 3.3.3.3. This is the most robust way to prove the configuration is correctly loaded.

-----

### 2\. DNS Resolution

For external services hosted in dynamic cloud environments or those whose IP addresses are subject to change, DNS resolution is the recommended approach. This method eliminates the need for manual configuration updates, as Istio dynamically discovers and tracks the service's endpoints.

The key here is `resolution: DNS`. The `ServiceEntry` relies on DNS lookups for the specified `hosts` (`se.example.com` in this case) to determine the service's current IP addresses. The `endpoints` field is intentionally omitted, as discovery is handled automatically.

```yaml
kubectl apply -f - <<EOF
apiVersion: networking.istio.io/v1
kind: ServiceEntry
metadata:
  name: example-se
  namespace: gwtest
spec:
  hosts:
  - se.example.com
  ports:
  - number: 80
    name: http
    protocol: TCP
  resolution: DNS
  location: MESH_INTERNAL
EOF
```
#### Verification Process
DNS Resolution
With DNS resolution, the goal is to confirm that the ServiceEntries is dynamically resolving the external hostname and routing traffic to the correct external IPs.
```
# Verify DNS Resolution
kubectl run -it test-pod --image=busybox:latest -- /bin/sh
nslookup se.example.com
```
**Expected Output:**
```
Server:         10.96.0.10
Address:        10.96.0.10#53

Non-authoritative answer:
Name:   se.example.com
Address: 8.8.8.8 # An actual external IP
```
**Test Traffic Flow:** Use curl to send a request. A successful response proves that Istio correctly routed traffic to the dynamically discovered endpoint.
```
curl -s http://se.example.com
```
-----

### 3\. Workload Selector

This advanced method provides a flexible way to route to specific in-mesh workloads that might not be exposed via a standard Kubernetes Service. It's particularly useful for fine-grained control or when targeting individual pods directly based on their labels.

The `ServiceEntry` leverages a `workloadSelector` to identify its endpoints. Istio will automatically discover and include any workloads within the mesh that possess the label `app: reviews` as part of this service.

```yaml
kubectl apply -f - <<EOF
apiVersion: networking.istio.io/v1
kind: ServiceEntry
metadata:
  name: example-se
  namespace: gwtest
spec:
  hosts:
  - se.example.com
  ports:
  - number: 80
    name: http
    protocol: TCP
  resolution: STATIC
  location: MESH_INTERNAL
  workloadSelector:
    labels:
      app: reviews
EOF
```
#### Verification Process:
**Get Target Pod IPs and Verify Routinig**
```
# Look for the IP addresses in the 'IP' column.
kubectl get pods -l app=reviews -o wide
kubectl run -it test-pod --image=busybox:latest -- /bin/sh
curl -s http://se.example.com/info
```
**Expected output:**
```
Response from Pod IP: 10.244.0.5
```
-----

### 4\. Workload Entry (Hybrid Cloud)

This feature allows you to extend the Istio service mesh to include non-Kubernetes workloads, such as virtual machines (VMs) or bare-metal servers, by integrating them as first-class mesh participants. This is essential for managing hybrid-cloud architectures.

This approach involves two key resources:

`**WorkloadEntry:**` Defines the external, non-Kubernetes workload, specifying its network address, locality, and ports. It's assigned labels (e.g., app: reviews-workloadentry) for discovery.

`**ServiceEntry:**` Utilizes a `workloadSelector` that matches the labels defined in the `WorkloadEntry`. This instructs Istio to automatically discover and use these `WorkloadEntry` instances as its endpoints, effectively bridging your Kubernetes-native mesh with external infrastructure.

```yaml
kubectl apply -f - <<EOF
apiVersion: networking.istio.io/v1
kind: ServiceEntry
metadata:
  name: example-se
  namespace: gwtest
spec:
  hosts:
  - se.example.com
  ports:
  - number: 80
    name: http
    protocol: TCP
  resolution: STATIC
  location: MESH_INTERNAL
  workloadSelector:
    labels:
      app: reviews-workloadentry
---
apiVersion: networking.istio.io/v1
kind: WorkloadEntry
metadata:
  name: reviews-workloadentry-1
  namespace: gwtest
  labels:
    app: reviews-workloadentry
spec:
  address: 1.1.1.1
  locality: r1/z1/sz1
  ports:
    http: 8080
---
apiVersion: networking.istio.io/v1
kind: WorkloadEntry
metadata:
  name: reviews-workloadentry-2
  namespace: gwtest
  labels:
    app: reviews-workloadentry
spec:
  network: external-network
  locality: r2/z2/sz2
  ports:
    http: 8080
EOF
```
#### Verification Process: 
**Verify Envoy Endpoints & Test Traffic Flow**
```
# Get the name of a pod in your mesh
kubectl get pods
# Then, inspect its Envoy configuration
istioctl proxy-config endpoints <POD_NAME> | grep "reviews-workloadentry"
# Test Traffic Flow
kubectl run -it test-pod --image=busybox:latest -- /bin/sh
curl -s http://se.example.com/health
```
A successful response here proves that traffic is flowing correctly from your Kubernetes pod to the external VM.

-----

### 5\. Egress ServiceEntry (Outbound Traffic)

While the primary examples in this document focus on using `ServiceEntry` resources as backends for `kgateway`'s ingress traffic, `ServiceEntry` is also crucial for managing outbound (Egress) traffic from services *within* your mesh. This allows you to apply Istio's policies to traffic leaving your cluster, ensuring consistency and control over external dependencies.

Here's an example of a `ServiceEntry` that configures outbound access to `github.com` via HTTPS, demonstrating how to enable and manage Egress to a real-world external service.

```yaml
kubectl apply -f - <<EOF
apiVersion: networking.istio.io/v1alpha3
kind: ServiceEntry
metadata:
  name: github-https
spec:
  hosts:
  - github.com
  ports:
  - number: 443
    name: https
    protocol: HTTPS
  location: MESH_EXTERNAL
EOF
```
---
