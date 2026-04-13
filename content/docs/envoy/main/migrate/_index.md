---
title: "Migrate from Ingress"
weight: 900
---

## Introduction

Welcome to the documentation for migrating from Ingress to **Gateway API** and **kgateway**. Migration is supported using the
[kgateway ingress2gateway](https://github.com/kgateway-dev/ingress2gateway) tool, which is a fork of
[Kubernetes ingress2gateway](https://github.com/kubernetes-sigs/ingress2gateway) with the following additional features:

- **Expanded Ingress NGINX Support:** Converts a wide range of Ingress NGINX-specific annotations, e.g. session affinity, authentication,
  rate limiting, CORS, TLS passthrough, service-upstream, and backend protocol hints.
- **Kgateway Emitter Support:** Generates Gateway API and kgateway-specific resources, e.g. TrafficPolicy, BackendConfigPolicy, etc.

[This upstream issue](https://github.com/kgateway-dev/ingress2gateway/issues/54) tracks merging these features into the Kubernetes ingress2gateway project.

## Prerequisites

Before you start the migration, ensure you have the following:

1. **Kgateway Installed**: You need kgateway running in the Kubernetes cluster containing the Ingresses to migrate.
2. **Kubernetes Cluster Access**: Ensure you have access to your Kubernetes cluster and necessary permissions to manage resources.

## Installation

The ingress2gateway tool can be installed on a variety of Linux platforms, macOS and Windows. Select your operating system below.

- [Install ingress2gateway on macOS]({{< relref "install/macos/_index.md" >}})
- [Install ingress2gateway on Linux]({{< relref "install/linux/_index.md" >}})
- [Install ingress2gateway on Windows]({{< relref "install/windows/_index.md" >}})

## Example Conversions

The following examples demonstrate how to use `ingress2gateway` to convert various Ingress resources to Gateway API and kgateway resources.

- [Basic Ingress]({{< relref "examples/basic.md" >}})
- [Session Affinity]({{< relref "examples/session-affinity.md" >}})
- [Rate Limiting]({{< relref "examples/rate-limiting.md" >}})
- [CORS]({{< relref "examples/cors.md" >}})
- [SSL Redirect]({{< relref "examples/ssl-redirect.md" >}})
- [External Auth]({{< relref "examples/external-auth.md" >}})
- [Canary Release]({{< relref "examples/canary.md" >}})
- [Backend TLS]({{< relref "examples/backend-tls.md" >}})

**Optional:** Use the Ingress NGINX [quickstart guide](https://kubernetes.github.io/ingress-nginx/deploy/#quick-start) to test connectivity
of the Ingress before converting.

## Common workflows

1. Convert Ingresses from the namespace in your current kubeconfig context.

    ```bash
    ingress2gateway print \
      --providers=ingress-nginx \
      --emitter=kgateway
    ```

2. Convert one or more manifest files.

    ```bash
    ingress2gateway print \
      --providers=ingress-nginx \
      --emitter=kgateway \
      --input-file ./ingress.yaml \
      --input-file ./more-ingresses.yaml
    ```

3. Select a custom Ingress NGINX class.

    ```bash
    ingress2gateway print \
      --providers=ingress-nginx \
      --emitter=kgateway \
      --ingress-nginx-ingress-class=internal-nginx
    ```

4. Include experimental Gateway API fields when your migration needs them.

    ```bash
    ingress2gateway print \
      --providers=ingress-nginx \
      --emitter=kgateway \
      --allow-experimental-gw-api \
      --input-file ./ingress.yaml
    ```

5. Check the tool version.

    ```bash
    ingress2gateway version
    ```

## Next steps

- Review the [ingress-nginx provider](./providers/ingressnginx/) to understand the supported Ingress NGINX annotations.
- Review the [kgateway emitter](./emitters/kgateway/) to understand how providers such as ingress-nginx map to kgateway-specific resources.
- Read the [emitter design](./emitters/) to learn more about emitters and providers.
