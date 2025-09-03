---
title: Kubernetes services
weight: 10
description: Route traffic to different types of Kubernetes services.
---

Route traffic to different types of Kubernetes services.

Use Kubernetes services as destinations for traffic routing within your cluster. Unlike Backend resources that define external destinations, Kubernetes services represent applications running inside your cluster that are discoverable through Kubernetes' native service discovery.

## Types

Check out the following guides for examples on how to route to different types of Kubernetes services with kgateway.

{{< cards >}}
  {{< card link="grpc-services" title="gRPC services" >}}
  {{< card link="kube-services" title="HTTP services" >}}
{{< /cards >}}
