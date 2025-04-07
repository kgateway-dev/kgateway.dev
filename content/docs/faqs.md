---
linkTitle: "FAQs"
title: Frequently asked questions
weight: 1000
next: /docs/quickstart
prev: /docs/reference
---

## What is kgateway?

Kgateway is an open source, cloud-native Layer 7 proxy that is based on [Envoy](https://www.envoyproxy.io/). The kgateway project implements gateway routing by using [{{< reuse "docs/snippets/k8s-gateway-api-name.md" >}}](https://gateway-api.sigs.k8s.io/) resources.

## Why would I want to use kgateway?

The kgateway project was built to support the difficult challenges of monolith to microservice migration, which includes being able to connect multiple types of compute resources, such as virtual machines (VMs) and on-premises monolithic apps with cloud-native, Kubernetes-based apps.

Other use cases kgateway can solve include the following:

* Kubernetes cluster ingress with a custom kgateway API as well as native support for the {{< reuse "docs/snippets/k8s-gateway-api-name.md" >}}.
* API gateway functionality for services that run outside Kubernetes
* Routing, resiliency, and security capabilities for enhanced traffic management

## What’s the difference between kgateway and Envoy? 

The Envoy proxy is a data-plane component with powerful routing, observability, and resilience capabilities. However, Envoy can be difficult to operationalize and complex to configure. 

The kgateway project comes with a simple yet powerful control plane for managing Envoy as an edge ingress, API Gateway, or service proxy. The kgateway control plane is built on a plugin model that enables extension and customization depending on your environment. This flexibility lets kgateway adapt both to the fast pace of development in the open source Envoy community, as well as to the unique needs of differing operational environments.

The kgateway includes the following capabilities beyond open source Envoy:

* A flexible control plane with extensibility in mind
* More ergonomic, domain-specific APIs to drive Envoy configuration
* Function-level routing that goes beyond routing to a `host:port` for clusters, including routing to a Swagger/OpenAPI spec endpoint, gRPC function, cloud provider function such as AWS Lambda, and more
* Transformation of request/response via a super-fast C++ templating filter built on Inja
* Envoy filters to call AWS Lambda directly, handling the complex security handshaking

## What is the difference between kgateway and Istio?

[Istio](https://istio.io/latest/docs/overview/what-is-istio/) is a service mesh that helps you manage, secure, and observe traffic for service-to-service communication. Although it includes some ingress gateway capabilities to get traffic into the cluster, Istio focuses more on east-west mesh use cases, especially in large, distributed environments. Istio operates the mesh by using either a per-pod sidecar or per-node ztunnel architecture.

The kgateway project is not a service mesh. Instead kgateway provides a lightweight control plane to manage Envoy-based API gateways, particularly for north-south edge ingress use cases in any Kubernetes-based environment. 

Kgateway can be deployed complementary to a service mesh like Istio. Istio solves the challenges of service-to-service communication by controlling requests as they flow through the system. Kgateway can be deployed at the edge of the service-mesh boundary, between service meshes, or within the mesh to add the following capabilities:

* Mutual TLS (mTLS) encryption of traffic between the gateway and services
* Transformation of request/response to decouple backend APIs from frontend
* Function routing such as AWS Lambda
* AI Gateway, MCP server, and other unique kgateway features

For examples, see the [Istio integration guides](/docs/integrations/istio/).

## What license is kgateway under?

The kgateway project uses [Apache License 2.0](http://www.apache.org/licenses/).

## What is the project roadmap?

The kgateway project organizes issues into milestones for release. For more details, see the [GitHub project](https://github.com/kgateway-dev/kgateway/milestones).

## What is the version support policy?

The kgateway project supports one latest version.

The `main` branch of the `kgateway-dev/kgateway` Git repository is for feature work under development, and is not stable.

## Where is the changelog?

The changelog is part of each [GitHub release](https://github.com/kgateway-dev/kgateway/releases).

<!--
## Is there enterprise software that is based on kgateway?

{{< cards >}}
  {{< card link="https://www.solo.io/products/gloo-gateway/" title="Solo.io" tag= "Enterprise" image="/img/gloo-gateway-ver-light-on-dark.png" icon="external-link">}}
{{< /cards >}} -->
