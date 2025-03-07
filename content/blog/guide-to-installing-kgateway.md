---
title: Guide to Installing kgateway
toc: false
publishDate: 2025-03-06T00:00:00-00:00
author: Eitan Suez, Technical Marketing Manager @ Solo.io & Alex Ly, Field Engineer @ Solo.io
---

[kgateway](https://kgateway.dev/) is an implementation of the Kubernetes Gateway API developed by Solo.io and donated to the CNCF at KubeCon Salt Lake City in Fall 2024. It’s designed to program Envoy, the CNCF's popular cloud-native proxy, offering modern traffic management across Kubernetes (and even non-Kubernetes) workloads. For more information around the motivations behind the kgateway project, Lin Sun recently [penned a blog](https://kgateway.dev/blog/advancing-open-source-gateways/) providing an update on the project.

To help the community learn about Gateway API, we plan to publish [blogs](http://kgateway.dev/blog), [videos](https://kgateway.dev/resources/videos/), and [hands-on labs](https://kgateway.dev/resources/labs/) using kgateway as a reference implementation example. Here is what you can expect from this series:

* Starting with a Gateway API “explainer” series, we will dive into the concepts of the specification, focusing on the “why” behind the decisions made in Gateway API, starting with this blog that dives into the installation of the control plane components
* Next we will explore data plane concepts, how to configure gateways and routes to complete an end-to-end example that demonstrates how the control plane and data plane work together
* We’ll then highlight the fundamental building blocks common to every Gateway API implementation, to establish a solid grasp of the standard features and practices.
* Moving forward, we’ll discuss the unique capabilities and advanced functionality offered by kgateway, including special extensions and policy attachments.
* Finally, we’ll wrap up by examining how kgateway integrates with service mesh and AI-based features, offering insights into where the technology is headed.

Although we are using kgateway as a reference example, the same concepts can be applied to any of the [over two dozen implementations](https://gateway-api.sigs.k8s.io/implementations/) of Gateway API, which is one of the major strengths of an open, vendor-neutral standard discussed in part one of this blog series. Whether you’re new to the Gateway API or simply looking for a modern, flexible solution for traffic routing and policy management, kgateway is a great starting point for experimenting with Gateway API.

In this first writeup, we simply want to point you in the right direction, by following the [quickstart](https://kgateway.dev/docs/quickstart/) instructions to install kgateway and diving deeper into the underlying components

## Installation

The installation is rather straightforward, even downright boring (and this is a good thing!)

Before installing on a Kubernetes cluster, it’s important to understand that the [Gateway API project](https://gateway-api.sigs.k8s.io/guides/?h=experimental#installing-gateway-api) provides two “channels” for its CRDs:

**Standard:** Contains CRDs and fields that have graduated to GA or beta. Suitable for production or risk-averse environments requiring stability.

**Experimental:** Includes everything in the standard channel, plus alpha features (e.g., TCPRoute, TLSRoute, UDPRoute) that may be removed or changed in the future. Suitable for development environments or rapid feature testing.

The Gateway API community provides guidance in their [versioning](https://gateway-api.sigs.k8s.io/concepts/versioning/) documentation around how CRDs in the experimental channel eventually graduate to be provided in the standard channel.

kgateway's instructions steer us to the experimental channel, which enables us to quickly
iterate and test the latest and greatest features. Currently this includes CRDs that are still deemed to be "alpha" quality such as TCPRoute, TLSRoute, UDPRoute, and others.

```
kubectl apply --kustomize "https://github.com/kubernetes-sigs/gateway-api/config/crd/experimental?ref=v1.2.1"
```

We can look at the associated API resources just applied to review which resources are stable vs alpha:

```
kubectl api-resources --api-group=gateway.networking.k8s.io
```

```
NAME                 SHORTNAMES   APIVERSION                           NAMESPACED   KIND
backendlbpolicies    blbpolicy    gateway.networking.k8s.io/v1alpha2   true         BackendLBPolicy
backendtlspolicies   btlspolicy   gateway.networking.k8s.io/v1alpha3   true         BackendTLSPolicy
gatewayclasses       gc           gateway.networking.k8s.io/v1         false        GatewayClass
gateways             gtw          gateway.networking.k8s.io/v1         true         Gateway
grpcroutes                        gateway.networking.k8s.io/v1         true         GRPCRoute
httproutes                        gateway.networking.k8s.io/v1         true         HTTPRoute
referencegrants      refgrant     gateway.networking.k8s.io/v1beta1    true         ReferenceGrant
tcproutes                         gateway.networking.k8s.io/v1alpha2   true         TCPRoute
tlsroutes                         gateway.networking.k8s.io/v1alpha2   true         TLSRoute
udproutes                         gateway.networking.k8s.io/v1alpha2   true         UDPRoute
```

Next, we’ll install the kgateway controller. This component is responsible for watching Gateway API related resources and configuring Envoy proxies accordingly.

Installation consists of deploying the following helm chart. 

As of March 2025, note that the build we are currently using is v2.0.0-main, which is a nightly build of kgateway, we expect to have a formal generally available (GA) release of kgateway announced by Kubecon EU in April 2025.

```
helm install --create-namespace --namespace kgateway-system \
  --version v2.0.0-main kgateway \
  oci://ghcr.io/kgateway-dev/charts/kgateway
```

Once installation is complete, we can take a peek at kgateway and its additional extensions and policy attachments that support a wider set of advanced traffic management and configuration capabilities.

```
kubectl api-resources --api-group=gateway.kgateway.dev
```

```
NAME                   SHORTNAMES   APIVERSION                      NAMESPACED   KIND
directresponses        dr           gateway.kgateway.dev/v1alpha1   true         DirectResponse
gatewayparameters      gwp          gateway.kgateway.dev/v1alpha1   true         GatewayParameters
httplistenerpolicies   hlp          gateway.kgateway.dev/v1alpha1   true         HTTPListenerPolicy
listenerpolicies       lp           gateway.kgateway.dev/v1alpha1   true         ListenerPolicy
routepolicies          rp           gateway.kgateway.dev/v1alpha1   true         RoutePolicy
upstreams              up           gateway.kgateway.dev/v1alpha1   true         Upstream
```

We can also inspect the default [GatewayClass](https://gateway-api.sigs.k8s.io/api-types/gatewayclass/) that gets created as part of the Helm installation:

```
kubectl get gatewayclass kgateway -o yaml | bat -l yaml
```

```
apiVersion: gateway.networking.k8s.io/v1
kind: GatewayClass
metadata:
  name: kgateway
  ...
spec:
  controllerName: kgateway.io/kgateway
  description: KGateway Controller
  parametersRef:
    group: gateway.kgateway.dev
    kind: GatewayParameters
    name: kgateway
    namespace: kgateway-system
status:
  conditions:
  - lastTransitionTime: "2025-02-11T22:43:33Z"
    message: ""
    observedGeneration: 1
    reason: Accepted
    status: "True"
    type: Accepted
  - lastTransitionTime: "2025-02-11T22:43:33Z"
    message: ""
    observedGeneration: 1
    reason: SupportedVersion
    status: "True"
    type: SupportedVersion
```

The GatewayClass resource comes with a status section that helps us ascertain that indeed our controller is up and running. **SupportedVersion** with a **True** status indicates that the CRDs installed in the cluster are supported by the implementation defined in the gateway class. **Accepted** with a **True** status indicates that the controller (kgateway in this case) was successfully deployed.

## What is GatewayClass?

The GatewayClass is a cluster-scoped resource that infrastructure providers (e.g. platform or gateway teams) define to represent a class of Gateways that can be instantiated. The concept is similar to a StorageClass in Kubernetes, where users can define different classes of storage that PersistentVolumeClaims (PVCs) can request. Both resources allow providers to create resources in the cluster from these classes based on the user-defined requirements.

The GatewayClass immediately solves a problem that existed with the legacy Ingress API, the ability to easily configure multiple implementations that can coexist in the same cluster. This allows users to easily switch between gateway implementations as the ecosystem and its features evolve, leading to reduced friction and vendor lock-in.

## Final Check

After installing kgateway, let’s confirm that it’s running properly in the kgateway-system namespace. Should you encounter any issues, check the controller logs for more details.

```
% kubectl get pods -n kgateway-system
NAME                        READY   STATUS    RESTARTS   AGE
kgateway-6848684bc9-t4d78   1/1     Running   0          10m
```

Unlike a traditional Ingress API setup, no data-plane proxy (Envoy, in this case) is automatically deployed at this stage. The Gateway API’s design provisions proxies on-demand when a user or platform admin creates a Gateway resource. We’ll discuss how to define and configure Gateway resources in the next blog post in this series.

## Summary

We have laid the groundwork for creating and programming a Gateway resource, deploying a sample application, and defining routing and policy configurations for your workloads. In the next blog, we will show you exactly how to accomplish this using kgateway.

In the meantime, we encourage you to explore the [kgateway documentation concepts](https://kgateway.dev/docs/about/), recap the concepts in this [demo](https://youtu.be/eGo8uJDsBEc?si=kIqltssNdFIRIh5g) video or get hands on and test out the concepts in the free technical lab on [installing kgateway](http://www.solo.io/resources/lab/install-kgateway-open-source-implementation-of-the-gateway-api?web&utm_source=organic&utm_medium=FY26&utm_campaign=WW_GEN_LAB_kgateway.dev&utm_content=community).

Thanks to the standards set forth by the Gateway API specification, you’d be surprised how intuitive it is to get started. Stay tuned for the next part of the series writeup!
