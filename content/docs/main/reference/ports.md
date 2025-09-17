---
title: Port reference
weight: 50
---

Review the ports that are used by kgateway.

Kgateway deploys containers that listen on certain ports for incoming traffic. In the following sections, you can review the pods and services that make up kgateway, and the ports that these pods and services listen on. ,<!--Note that if you choose to set up mutual TLS (mTLS) for communication between kgateway components, alternate ports and traffic flows are used. -->

<!--

{{< callout type="info" >}}
This list of ports reflects the default values that are included in an unmodified installation of kgateway. You can optionally change some port settings by providing custom values in your kgateway Helm chart.
{{< /callout >}} -->


## Installation

The {{< reuse "docs/snippets/kgateway.md" >}} installation process uses a Helm chart to create the necessary custom resource definitions (CRDs), deployments, services, pods, etc. The services and pods listen on specific ports to enable communication between the components that make up {{< reuse "docs/snippets/kgateway.md" >}}.

## Components

A standard installation of {{< reuse "docs/snippets/kgateway.md" >}} includes the following components:

* **{{< reuse "docs/snippets/kgateway-capital.md" >}} control plane**
  * Creates an Envoy configuration from multiple custom resources.
  * Serves Envoy configurations using xDS.
  * Validates Proxy configurations for the gateway proxy.
* **{{< reuse "docs/snippets/kgateway-capital.md" >}} data plane (gateway proxy)**
  * Receives and loads configuration from kgateway xDS.
  * Proxies incoming traffic.

## Pods and ports

The components are instantiated by using pods and services. The following table lists the deployed pods and ports in use by each pod.

### Control plane ports

| Pod | Port | Usage |
|-----|------|-------|
| {{< reuse "docs/snippets/kgateway.md" >}} | 9976 | REST xDS | 
| {{< reuse "docs/snippets/kgateway.md" >}} | 9977 | xDS Server |

### Gateway proxy ports

{{< reuse "docs/snippets/reserved-ports.md" >}}

<!--
## mTLS considerations

Kgateway supports the use of mutual TLS (mTLS) communication between the kgateway pod and other services, including the Envoy proxy, external auth server, and rate limiting server. Enabling mTLS includes the addition of sidecars for multiple pods, Envoy proxy for TLS termination, and SDS for certificate rotation and management. 

### Updated pods

The following pods are updated to support mTLS:
* **Kgateway pod**: Envoy and SDS sidecars are added.
* **Gateway proxies**: SDS sidecars are added and the ConfigMap is updated for mTLS.

The additional Envoy sidecar has an admin port listening on 8081 for each pod.

### Updated traffic flow

The Envoy sidecar on the kgateway intercepts the inbound traffic for each pod and performs the TLS decryption before passing the traffic to the main container. This process does not alter the ports that are used by the pods and services, but it does create additional ports that are used for internal communication within the pod. For instance, the kgateway pod continues to listen on 9977 as the xDS server. Internally, the kgateway container listens on 127.0.0.1:9999 for xDS requests. The Envoy sidecar in the pod accepts requests on 9977, decrypts the request, and sends it to port 9999 on the localhost for processing.
-->