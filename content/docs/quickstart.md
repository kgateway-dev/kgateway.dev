---
linkTitle: "Get started"
title: Get started with kgateway
weight: 1
next: /docs/about
---

Get started with kgateway, a cloud-native Layer 7 proxy that is based on the [Envoy](https://www.envoyproxy.io/) and [{{< reuse "docs/snippets/k8s-gateway-api-name.md" >}}](https://gateway-api.sigs.k8s.io/) projects.

<!--metadata
test:
  - oss-glooctl
  - oss-helm
  - enterprise-glooctl
  - enterprise-helm
-->

## Before you begin

These quick start steps assume that you have `kubectl` and `helm` installed. For full installation instructions, see [Install kgateway](/docs/operations/install).

## Install kgateway

1. Use a Kubernetes cluster. For quick testing, you can use [Kind](https://kind.sigs.k8s.io/).

   ```sh {id="my-special-id"}
   kind create cluster
   ```

{{% reuse "docs/snippets/get-started.md" %}}

Good job! You now have the kgateway control plane running in your cluster.

## Next steps

Ready to try out more features? Check out the following guides:

- [Install a sample app such as httpbin](/docs/operations/sample-app/). This guide includes setting up an API gateway, configuring a basic HTTP listener on the API gateway, and routing traffic to httpbin by using an HTTPRoute resource.
- [Set up an API gateway with a listener](/docs/setup/listeners/) so that you can start routing traffic to your apps.

No longer need kgateway? Uninstall with the following command:

```sh {id="no-test"}
helm uninstall kgateway -n kgateway-system
```
