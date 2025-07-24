---
linkTitle: "Get started"
title: Get started with kgateway
weight: 1
next: /docs/about
---

Get started with {{< reuse "/docs/snippets/kgateway.md" >}}, a cloud-native Layer 7 proxy that is based on the [Envoy](https://www.envoyproxy.io/) and [{{< reuse "docs/snippets/k8s-gateway-api-name.md" >}}](https://gateway-api.sigs.k8s.io/) projects.

## Before you begin

These quick start steps assume that you have a Kubernetes cluster, `kubectl`, and `helm` already set up. For quick testing, you can use [Kind](https://kind.sigs.k8s.io/).

```sh
kind create cluster
```

## Install

The following steps get you started with a basic installation. For instructions, see the [installation guide](/docs/operations/install).

{{< reuse "docs/snippets/get-started.md" >}}

{{< callout type="info" >}}
Want to quickly validate the health of your kgateway control plane? Check out the [`kgwctl` CLI](/docs/reference/cli/install/) and run the `kgwctl check` command to assess your kgateway installation. 
{{< /callout >}}

Good job! You now have the {{< reuse "/docs/snippets/kgateway.md" >}} control plane running in your cluster.

## Next steps

Ready to try out more features? Check out the following guides:

- [Install a sample app such as httpbin](../operations/sample-app/). This guide includes setting up an API gateway, configuring a basic HTTP listener on the API gateway, and routing traffic to httpbin by using an HTTPRoute resource.
- [Set up an API gateway with a listener](../setup/listeners/) so that you can start routing traffic to your apps.

No longer need {{< reuse "/docs/snippets/kgateway.md" >}}? Uninstall with the following command:

```sh
helm uninstall {{< reuse "/docs/snippets/helm-kgateway.md" >}} -n {{< reuse "docs/snippets/namespace.md" >}}
```
