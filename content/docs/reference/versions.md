---
title: Version support
description: View supported kgateway versions and their release cycle.
weight: 50
---

Review the following information about supported release versions for kgateway.

## Supported versions

| Kgateway | Kubernetes | Gateway API`*` | Envoy | Helm | Istio`†` |
|----------|------------|----------------|-------|------|----------|
| 2.0.x | 1.27 - 1.31 | 1.2.x | Proxy 1.33, API v3 | >= 3.12 | 1.18 - 1.23 |

<!--See tested min/max versions in https://github.com/kgateway-dev/kgateway/tree/main/.github/workflows/.env/nightly-tests-->
<!--| 2.1.x | 1.30 - 1.33 | 1.3.x | Proxy 1.33, API v3 | >= 3.12 | 1.23 - 1.25 |-->

`*` Gateway API versions: The kgateway project is conformant to the Kubernetes Gateway API specification. For more details, see the [Gateway API docs](https://gateway-api.sigs.k8s.io/implementations/#kgateway) and kgateway conformance report per version, such as Gateway API [v1.2.1](https://github.com/kubernetes-sigs/gateway-api/tree/main/conformance/reports/v1.2.1/kgateway).

`†` Istio versions: Istio must run on a compatible version of Kubernetes. For example, Istio 1.22 is tested, but not supported, on Kubernetes 1.26. For more information, see the [Istio docs](https://istio.io/latest/docs/releases/supported-releases/). 

<!--
## Image variants

For some kgateway component images, the following image variants are supported. 

* **Standard**: The default image variant provided by kgateway. The standard variant does not require a tag on the image. 
* **Distroless**: An image tagged with `-distroless` is a slimmed-down distribution with the minimum set of binary dependencies to run the image, for enhanced performance and security. Distroless images do not contain package managers, shells, or any other programs that are generally found in a standard Linux distribution. The use of distroless variants is a standard practice adopted by various open source projects and proprietary applications.

Kgateway supports image variants for the following component images:
- `access-logger`
- `certgen`
- `discovery`
- `gloo`
- `gloo-envoy-wrapper`
- `ingress`
- `kubectl`
- `sds`

You have two options for specifying the variant for a kgateway image in your Helm values:
* Specify the image variant for all kgateway components in the `global.image.variant` Helm field. Supported values include `standard`, and `distroless`. If unset, the default value is `standard`.
* Specify images for individual components by using variant tags in the `gloo.<component>.deployment.image.tag` field of the component's Helm settings, such as `quay.io/solo-io/gloo:v{{< reuse "docs/versions/n-patch.md" >}}-distroless`. -->

## Release cadence {#cadence}

Stable builds for kgateway are released as minor versions approximately every three months. A stable branch for a minor version, such as {{< reuse "docs/versions/short.md" >}}, is tagged from `main`, and stable builds are supported from that branch.

## Release development {#release}

New features for kgateway are developed on `main` and available as development builds. Stable branches are created off of `main` for each minor version, such as `v2.0.x`.

### Release process {#release-process}

Development of a quality stable release on `main` typically follows this process:

1. New feature development is suspended on `main`.
2. Release candidates are created, such as `{{< reuse "docs/versions/short.md" >}}.0-rc1`, `{{< reuse "docs/versions/short.md" >}}.0-rc2`, and so on.
3. A full suite of tests is performed for each release candidate. Testing includes all documented workflows, a test matrix of all supported platforms, and more.
4. Documentation for that release is prepared, vetted, and staged.
5. The stable minor version is released as part of a stable branch, such as `v2.0.x`.
6. Feature development on `main` is resumed.

### Feature development on main branch {#release-main}

Feature development for kgateway is performed on the `main` branch. Upon a merge to `main`, a development build is automatically released. The current development release is `{{< reuse "docs/versions/patch-dev.md" >}}`. 

{{< callout type="warning" >}}
Development releases are unstable, subject to change, and not recommended for production usage.
{{< /callout >}}

### Backports to stable branches {#release-backport}

New features are not developed on or backported to stable branches, such as `v2.0.x`. However, critical patches, bug fixes, and documentation fixes are backported as needed.

## Experimental features in Gateway API {#experimental-features}

The following features are experimental in the upstream Kubernetes Gateway API project, and are subject to change.

| Feature | Minimum Gateway API version |
| --- | --- |
| [ListenerSets](/docs/setup/listeners/#listenersets) | 1.3 |
| [TCPRoutes](/docs/setup/listeners/tcp/) | 1.3 |
| [BackendTLSPolicy](/docs/security/backend-tls/) | 1.2 |
| [CORS policies](/docs/security/cors/) | 1.2 |
| [Retries](/docs/resiliency/retries/) | 1.2 |
| [Session persistence](/docs/traffic-management/session-affinity/session-persistence) | 1.3 | 
| [HTTPRoute rule attachment option](/docs/about/policies/trafficpolicy/#attach-to-rule) | 1.3 |

**Sample command for version {{< reuse "docs/versions/k8s-gw-version.md" >}}**: Note that some CRDs are prefixed with `X` to indicate that the entire CRD is experimental and subject to change.
     
```sh
kubectl apply -f https://github.com/kubernetes-sigs/gateway-api/releases/download/v{{< reuse "docs/versions/k8s-gw-version.md" >}}/experimental-install.yaml
```  