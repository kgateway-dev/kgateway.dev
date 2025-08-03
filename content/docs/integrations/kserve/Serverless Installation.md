
---
title: Serverless Installation Guide
weight: 10
---

KServe Serverless installation enables autoscaling based on request volume and supports scale down to and from zero. It also supports revision management and canary rollout based on revisions.  
Kubernetes 1.30 is the minimally required version and please check the following recommended Knative, kgateway versions for the corresponding Kubernetes version.

### Recommended Version Matrix

| Kubernetes Version | Recommended kgateway Version | Recommended Knative Version |
| -- | -- | -- |
| 1.30 | gateway.networking.k8s.io/v1beta1 | 1.15, 1.16 |
| 1.31 | gateway.networking.k8s.io/v1beta1 | 1.16, 1.17 |
| 1.32 | gateway.networking.k8s.io/v1 | 1.17, 1.18 |

### 1. Install Knative Serving

Please refer to [`Knative Serving install guide.`](https://knative.dev/docs/install/yaml-install/serving/install-serving-with-yaml/)

{{< callout type="note" >}}
**Note**: If you are looking to use PodSpec fields such as nodeSelector, affinity or tolerations which are now supported in the v1beta1 API spec, you need to turn on the corresponding [`feature flags`](https://knative.dev/docs/serving/configuration/feature-flags/) in your Knative configuration.
{{< /callout >}}

{{< callout type="warning" >}}
**Warning**: Knative v1.13.1 requires Istio v1.20 or later. gRPC routing does not work with earlier versions of Istio. Please refer to the Knative [`release notes`](https://github.com/knative/serving/releases/tag/knative-v1.13.1) for more information.
{{< /callout >}}

{{< callout type="note" >}}
**Note**: If you are installing Knative to work with kgateway, you must set the following during install:
```sh
 networking:
   ingressClass: "gateway.networking.k8s.io/kgateway-system"
 ```
 Refer to [kgateway ingress setup for Knative](https://kgateway.dev/docs/integrations/kgateway-kserve/ingress-setup/) for details.
{{< /callout >}}

### 2. Install Networking Layer

The recommended networking layer for KServe is now [`kgateway`](https://kgateway.dev) as it provides better integration with the Kubernetes Gateway API and supports advanced routing capabilities.

Refer to the [`kgateway ingress setup for KServe`](http://localhost:1313/docs/integrations/kserve/kserve-ingress-with-kgateway/) guide for detailed steps.

Alternatively, you can use other networking layers like [`Istio`](https://istio.io/), [`Kourier`](https://github.com/knative-extensions/net-kourier), or [`Contour`](https://projectcontour.io/).

{{< callout type="tip" >}}
**Tip**: kgateway simplifies gateway management via CRDs and is the recommended option when using KServe with Knative and Kubernetes Gateway API.
{{< /callout >}}

### 3. Install Cert Manager

The minimally required Cert Manager version is **v1.15.0**. You can refer to the [Cert Manager installation docs](https://cert-manager.io/docs/installation/).

{{< callout type="note" >}}
**Note**: Cert Manager is required to provision webhook certs for production-grade installation. Alternatively, you can run a self-signed cert generation script.
{{< /callout >}}

### 4. Install KServe

{{< tabs tabTotal="2" items="Install using Helm,Install using YAML" >}}

{{% tab tabName="Install using Helm" %}}

#### Install KServe CRDs

```sh
helm install kserve-crd oci://ghcr.io/kserve/charts/kserve-crd --version v0.15.0
```
### Install KServe Resources

```sh
helm install kserve oci://ghcr.io/kserve/charts/kserve --version v0.15.0
```
{{% /tab %}}

{{% tab tabName="Install using YAML" %}}

Install KServe CRDs and Controller, --server-side option is required as the InferenceService CRD is large, see [`this issue`](https://github.com/kserve/kserve/issues/3487) for details.

```sh
kubectl apply --server-side -f https://github.com/kserve/kserve/releases/download/v0.15.0/kserve.yaml
```
Install KServe Built-in ClusterServingRuntimes

```sh
kubectl apply --server-side -f https://github.com/kserve/kserve/releases/download/v0.15.0/kserve-cluster-resources.yaml
```
{{% /tab %}}

{{< /tabs >}}

{{< callout type="note" >}}
**Note**: ClusterServingRuntimes are required to create InferenceService for built-in model serving runtimes with KServe v0.8.0 or higher.
{{< /callout >}}