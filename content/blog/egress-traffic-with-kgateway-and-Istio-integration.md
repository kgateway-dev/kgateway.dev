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
# How importantis kgateway's integration
While Istio ambient provides Authorization, Authentication and Egress still, there are several scenarios where kgateway can offer a more powerful alternative:

## Managing External Authorization into our Request FLow
<!-- For exmple - Kyverno for applying with demo video
-->

## How kgateway can help in managing CEL based RBAC policies

## Securely Egress Traffic with kgateway + Istio integration

# See it in Action
<!-- For Demo
-->
# Demo

