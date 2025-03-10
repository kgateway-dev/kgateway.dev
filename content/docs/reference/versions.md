---
title: Version support
description: View supported kgateway versions and their release cycle.
weight: 50
---

Review the following information about supported release versions for {{< reuse "docs/snippets/product-name.md" >}} OSS (open source).

## Supported versions

| {{< reuse "docs/snippets/product-name-caps.md" >}} | Kubernetes | Envoy | Helm | Istio`†`|
|--------------|------------|-------|------|---------|
| 1.18.x | 1.25 - 1.31 | v3 xDS API | >= 3.12 | 1.16 - 1.22 |

## Image variants

For some {{< reuse "docs/snippets/product-name.md" >}} component images, the following image variants are supported. 

* **Standard**: The default image variant provided by {{< reuse "docs/snippets/product-name.md" >}}. The standard variant does not require a tag on the image. 
* **Distroless**: An image tagged with `-distroless` is a slimmed-down distribution with the minimum set of binary dependencies to run the image, for enhanced performance and security. Distroless images do not contain package managers, shells, or any other programs that are generally found in a standard Linux distribution. The use of distroless variants is a standard practice adopted by various open source projects and proprietary applications.

{{< reuse "docs/snippets/product-name-caps.md" >}} supports image variants for the following component images:
- `access-logger`
- `certgen`
- `discovery`
- `gloo`
- `gloo-envoy-wrapper`
- `ingress`
- `kubectl`
- `sds`

You have two options for specifying the variant for a {{< reuse "docs/snippets/product-name.md" >}} image in your Helm values:
* Specify the image variant for all {{< reuse "docs/snippets/product-name.md" >}} components in the `global.image.variant` Helm field. Supported values include `standard`, and `distroless`. If unset, the default value is `standard`.
* Specify images for individual components by using variant tags in the `gloo.<component>.deployment.image.tag` field of the component's Helm settings, such as `quay.io/solo-io/gloo:v{{< reuse "docs/versions/n-patch.md" >}}-distroless`.

## Release cadence

Stable builds for {{< reuse "docs/snippets/product-name.md" >}} are released as minor versions approximately every three months. A stable branch for a minor version, such as {{< reuse "docs/versions/short.md" >}}, is tagged from `main`, and stable builds are supported from that branch.

## Release development

### Beta release process

New features for {{< reuse "docs/snippets/product-name.md" >}} are developed on `main`. The latest version is released as a patch off of `main`.

### Stable release process

Development of a quality stable release on `main` typically follows this process:
1. New feature development is suspended on `main`.
2. Release candidates are created, such as `{{< reuse "docs/versions/short.md" >}}.0-rc1`, `{{< reuse "docs/versions/short.md" >}}.0-rc2`, and so on.
3. A full suite of tests is performed for each release candidate. Testing includes all documented workflows, a test matrix of all supported platforms, and more.
4. Documentation for that release is prepared, vetted, and staged.
5. The stable minor version is released.
6. Feature development on `main` is resumed.

## Additional release information

New features are not developed on or backported to stable branches. However, critical patches, bug fixes, and documentation fixes are backported to all actively supported branches.