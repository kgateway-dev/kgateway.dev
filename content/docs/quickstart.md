---
linkTitle: "Get started"
title: Get started with kgateway
weight: 1
next: /docs/about
---

Get started with {{< reuse "docs/snippets/product-name.md" >}}, a cloud-native Layer 7 proxy that is based on the [Envoy](https://www.envoyproxy.io/) and [{{< reuse "docs/snippets/k8s-gateway-api-name.md" >}}](https://gateway-api.sigs.k8s.io/) projects.

## Before you begin

These quick start steps assume that you have `kubectl` and `helm` installed. For full installation instructions, see [Install {{< reuse "docs/snippets/product-name.md" >}}](/docs/operations/install).

## Install kgateway

1. Use a Kubernetes cluster. For quick testing, you can use [Kind](https://kind.sigs.k8s.io/).

   ```sh
   kind create cluster
   ```

2. Deploy the Kubernetes Gateway API CRDs.

   ```sh
   kubectl apply -f https://github.com/kubernetes-sigs/gateway-api/releases/download/v{{< reuse "docs/versions/k8s-gw-version.md" >}}/standard-install.yaml
   ```

3. Install {{< reuse "docs/snippets/product-name.md" >}} by using Helm.

   ```sh
   helm install --create-namespace --namespace {{< reuse "docs/snippets/ns-system.md" >}} --version v{{< reuse "docs/versions/n-patch.md" >}} kgateway oci://cr.kgateway.dev/charts/kgateway
   ```

4. Make sure that `kgateway` is running.

   ```sh
   kubectl get pods -n {{< reuse "docs/snippets/ns-system.md" >}}
   ```

   Example output:

   ```
   NAME                        READY   STATUS    RESTARTS   AGE
   kgateway-5495d98459-46dpk   1/1     Running   0          19s
   ```

Good job! You now have the {{< reuse "docs/snippets/product-name.md" >}} control plane running in your cluster.

## Next steps

Ready to try out more features? Check out the following guides:

- [Install a sample app such as httpbin](/docs/operations/sample-app/). This guide includes setting up an API gateway, configuring a basic HTTP listener on the API gateway, and routing traffic to httpbin by using an HTTPRoute resource.
- [Set up an API gateway with a listener](/docs/setup/listeners/) so that you can start routing traffic to your apps.

No longer need {{< reuse "docs/snippets/product-name.md" >}}? Uninstall with the following command:

```sh
helm uninstall kgateway -n {{< reuse "docs/snippets/ns-system.md" >}}
```
