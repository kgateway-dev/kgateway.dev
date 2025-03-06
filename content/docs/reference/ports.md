---
title: Port reference
weight: 50
---

Review the ports that are used by {{< reuse "docs/snippets/product-name.md" >}}.

{{< reuse "docs/snippets/product-name-caps.md" >}} deploys containers that listen on certain ports for incoming traffic. In the following sections, you can review the pods and services that make up {{< reuse "docs/snippets/product-name.md" >}}, and the ports that these pods and services listen on. Note that if you choose to set up mutual TLS (mTLS) for communication between {{< reuse "docs/snippets/product-name.md" >}} components, alternate ports and traffic flows are used.

{{% callout type="info" %}}
This list of ports reflects the default values that are included in an unmodified installation of {{< reuse "docs/snippets/product-name.md" >}}. You can optionally change some port settings by providing custom values in your {{< reuse "docs/snippets/product-name.md" >}} Helm chart.
{{% /callout %}}


## Kgateway 

{{< reuse "docs/snippets/product-name-caps.md" >}} open source software is the free, open source version of {{< reuse "docs/snippets/product-name.md" >}}. The installation process uses a Helm chart to create the necessary custom resource definitions (CRDs), deployments, services, pods, etc. The services and pods listen on specific ports to enable communication between the components that make up {{< reuse "docs/snippets/product-name.md" >}} and outside sources that will consume Backend resources through {{< reuse "docs/snippets/product-name.md" >}}.

### What's included

A standard installation of {{< reuse "docs/snippets/product-name.md" >}} includes four primary components:

* **Gateway**
  * Translates {{< reuse "docs/snippets/product-name.md" >}} custom resources, such as RouteOption and VirtualHostOption into a Proxy custom resource.
  * Validates proposed configurations before application.
* **{{< reuse "docs/snippets/product-name-caps.md" >}}**
  * Creates an Envoy configuration from multiple custom resources.
  * Serves Envoy configurations using xDS.
  * Validates Proxy configurations for the gateway.
* **Proxy**
  * Receives and loads configuration from {{< reuse "docs/snippets/product-name.md" >}} xDS.
  * Proxies incoming traffic.
* **Discovery**
  * Discovers Backends in the cluster.
  * Discovers functions with the Function Discovery Service.

### Pods and ports

The four primary components are instantiated using pods and services. The following table lists the deployed pods and ports in use by each pod, as well as the optional `access-log` pod if Access Logging has been enabled.

| Pod | Port | Usage |
|-----|------|-------|
| gloo | 8443 | Validation |
| gloo | 9976 | REST xDS | 
| gloo | 9977 | xDS Server |
| gloo | 9988 | Validation |
| gloo | 9979 | WASM cache |
| gateway-proxy | 8080 | HTTP |
| gateway-proxy | 8443 | HTTPS |
| gateway-proxy | 19000 | Envoy admin |
| access-log | 8083 | Access logging |

The `discovery` pod does not listen on any ports as it uses outbound connections only.

### Services and ports

The following table lists the services backed by the deployed pods.

| Service | Port | Target | Target Port | Usage            |
|---------|------|--------|-------------|------------------|
| gloo | 443 | gateway | 8443 | Validation       |
| gloo | 9976 | gloo | 9976 | REST xDS         |
| gloo | 9977 | gloo | 9977 | xDS Server       |
| gloo | 9988 | gloo | 9988 | Validation       |
| gloo | 9979 | gloo | 9979 | WASM cache       |
| gloo | 9966 | gloo | 9966 | Proxy Debug gRPC |
| gateway-proxy | 80 | gateway-proxy | 8080 | HTTP             |
| gateway-proxy | 443 | gateway-proxy | 8443 | HTTPS            |
| access-log | 8083 | access-log | 8083 | Access logging   |


## mTLS considerations

{{< reuse "docs/snippets/product-name-caps.md" >}} supports the use of mutual TLS (mTLS) communication between the {{< reuse "docs/snippets/product-name.md" >}} pod and other services, including the Envoy proxy, external auth server, and rate limiting server. Enabling mTLS includes the addition of sidecars for multiple pods, Envoy proxy for TLS termination, and SDS for certificate rotation and management. 

### Updated pods

The following pods are updated to support mTLS:
* **{{< reuse "docs/snippets/product-name-caps.md" >}} pod**: Envoy and SDS sidecars are added.
* **Gateway proxies**: SDS sidecars are added and the ConfigMap is updated for mTLS.

The additional Envoy sidecar has an admin port listening on 8081 for each pod.

### Updated traffic flow

The Envoy sidecar on the {{< reuse "docs/snippets/product-name.md" >}} intercepts the inbound traffic for each pod and performs the TLS decryption before passing the traffic to the main container. This process does not alter the ports that are used by the pods and services, but it does create additional ports that are used for internal communication within the pod. For instance, the {{< reuse "docs/snippets/product-name.md" >}} pod continues to listen on 9977 as the xDS server. Internally, the {{< reuse "docs/snippets/product-name.md" >}} container listens on 127.0.0.1:9999 for xDS requests. The Envoy sidecar in the pod accepts requests on 9977, decrypts the request, and sends it to port 9999 on the localhost for processing.
