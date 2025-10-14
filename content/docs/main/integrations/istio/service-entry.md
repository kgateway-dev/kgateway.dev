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
4. Label the `httpbin` namespace to add the httpbin sample-app to the ambient mode.
```sh
kubectl label ns httpbin istio.io/dataplane-mode=ambient
```

## Targeting ServiceEntry Backends with HTTPRoute and TrafficPolicies

1. Create a Testing Namespace `gwtest` to deploy our Gateways, HTTPRoutes and ServiceEntries.

```sh
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
    filters:
        - type: RequestHeaderModifier
          requestHeaderModifier:
            add:
              - name: App
                value: ServiceEntry
            set:
              - name: User-Agent
                value: custom
            remove:
              - X-Remove
EOF
```
3. It is also using a Header Manipulation rule that we apply to our `http-gw-for-test` apps to:
* Add the App: httpbin2 header to all requests.
* Set the User-Agent header to custom. If the User-Agent header is not present, it is added to the request.
* Remove the X-Remove header from the request.
For more information about Header Control, you can read [L7 policies integration](https://kgateway.dev/docs/main/integrations/istio/ambient/waypoint/#waypoint-policies) to our Gateway.

## Full Code Examples & Use Cases

Building on the common kgateway and HTTPRoute configuration, these examples demonstrate how different `ServiceEntry` types are implemented to integrate various external service scenarios.

### 1\. Static Endpoints

This configuration is the most straightforward, designed for external services with fixed, known network addresses. It's an excellent choice for integrating a legacy database, an on-premises application with a stable IP, or for controlled test environments.

The `ServiceEntry` explicitly lists the IP addresses of the external service in the `endpoints` array. With `resolution: STATIC`, Istio directly distributes traffic among these predefined addresses.

First, identify the `Cluster IP` of your `httpbin` service:

```sh
kubectl get svc -n httpbin httpbin
```
Now use `HTTPBIN_Cluster_IP`to address the endpoints

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
  - address: <HTTPBIN_CLUSTER_IP>
    locality: r3/z3/sz3
EOF
```
---
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
---

#### 3\. Workload Selector

This method routes traffic to specific in-mesh workloads that match a defined set of Kubernetes labels. It's useful for fine-grained control when you want to target individual pods or groups of pods directly, rather than relying on a standard Kubernetes Service.

For this example, we'll configure the `ServiceEntry` to discover `httpbin` pods based on their labels.

First, identify the labels on your `httpbin` pods in the `httpbin` namespace:

```bash
kubectl get pod -n httpbin -l app=httpbin -o jsonpath='{.items[0].metadata.labels}'
```

Expected output will include something like: 
```sh
"app": "httpbin"
```

Now, define the `ServiceEntry`. This `ServiceEntry` leverages a `workloadSelector` that matches the `app: httpbin` label. Istio will automatically discover and include any `httpbin` pods within the `httpbin` namespace that possess this label as part of this service's endpoints.

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
      app: httpbin
  exportTo:
  - "." # To Makes the ServiceEntry visible across all namespaces for selector
  EOF
```

**Ensure the selector matches the labels on your httpbin pods**

---
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
---
### Verification Process

The following command automatically finds the service created by your Gateway resource and will perform the port-forwarding.

```sh
# Deploy a Test Pod & Verify Hostname Resolution
GATEWAY_SVC=$(kubectl get svc -n gwtest -l gateway.networking.k8s.io/gateway-name=http-gw-for-test -o jsonpath='{.items[0].metadata.name}')
kubectl -n gwtest port-forward service/$GATEWAY_SVC 8080:8080```
You will see an output as: 
```

The -H "Host: se.example.com" header is essential as it tells kgateway which HTTPRoute to match.

```
curl -s -H "Host: se.example.com" localhost:8080/headers
```

Expected Output:

```json
{
  "headers": {
    "Accept": "*/*",
    "Host": "se.example.com",
    "User-Agent": "curl/...",
    // ... other headers from your external httpbin-like service
  }
}
```
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
  - httpbin.org
  location: MESH_EXTERNAL
  ports:
  - number: 443
    name: https
    protocol: HTTPS
  resolution: DNS
EOF
```
---
