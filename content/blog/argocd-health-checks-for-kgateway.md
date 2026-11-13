---
title: "Green means accepted: ArgoCD health checks for kgateway"
toc: false
publishDate: 2026-11-12T10:00:00-00:00
author: Duncan Doyle
excludeSearch: true
---

GitOps is a natural fit for kgateway: Gateways, routes and policies are all Kubernetes resources, so they live in Git, and ArgoCD keeps the cluster in sync. ArgoCD does more than apply manifests. It also asks every resource whether it is healthy, and that answer drives the Application's status, sync waves and notifications. Today I'm happy to introduce ArgoCD health checks for kgateway, so ArgoCD can give that answer for kgateway's own resources too.

## Health for kgateway resources

ArgoCD knows how to check the health of a Kubernetes Deployment or a Service, and recent releases also ship checks for Gateway API resources, such as Gateways and HTTPRoutes. Kgateway's own custom resources had no check yet, so ArgoCD left them without a health status and did not count them when it rolled up an Application. A TrafficPolicy that kgateway rejected could sit in an Application that still reported Healthy.

The new health checks close that gap. They read the status kgateway already writes on each resource, and turn it into one of ArgoCD's states:

- **Healthy**: kgateway accepted the resource.
- **Progressing**: kgateway has not reached a verdict yet, for example right after a change.
- **Degraded**: kgateway rejected all or part of the resource. The badge shows kgateway's own message, such as which reference it could not resolve.

Here is what that looks like for a small storefront application. Almost everything is green, and ArgoCD now points straight at the two resources that need attention. In this example, it shows a route where the backend Service was never deployed, and a TrafficPolicy that references an auth extension that does not exist.

{{< reuse-image src="blog/argocd-health-checks-for-kgateway-1.png" width="750px" >}}

Select a degraded resource and ArgoCD shows the health status of the resource in kgateway:

{{< reuse-image src="blog/argocd-health-checks-for-kgateway-2.png" width="750px" >}}

## What is covered

The health checks cover the kgateway resources that report a status:

| Kind | What it is |
|---|---|
| TrafficPolicy | Route-level traffic behavior, such as auth, rate limiting, and header changes |
| ListenerPolicy | Listener-level settings on a Gateway |
| `BackendConfigPolicy` | Connection settings towards a backend |
| `DirectResponse` | A canned response returned by the gateway |
| `Backend` | A destination that is external to the cluster |

They are tested against kgateway v2.4 and v2.5. For Gateway API kinds like `Gateway` and `HTTPRoute`, ArgoCD 3.1 and later include their own checks, so together you get health for the whole gateway configuration.

## Getting started

The health checks are a small set of Lua scripts that you add to ArgoCD's `argocd-cm` ConfigMap. There is nothing to deploy and nothing to restart. If you install ArgoCD with the argo-helm chart, you pass one extra values file; otherwise a single `kubectl patch` does it. Hosted ArgoCD offerings that accept health customizations can take the same entries.

You can find everything in the [kgateway-argocd-healthchecks](https://github.com/DuncanDoyle/kgateway-argocd-healthchecks) repository. The [installation guide](https://github.com/DuncanDoyle/kgateway-argocd-healthchecks/blob/main/docs/INSTALL.md) walks through each installation method, and an [in-depth appendix](https://github.com/DuncanDoyle/kgateway-argocd-healthchecks/blob/main/docs/HEALTH-MODEL.md) explains exactly how each state is decided.

## What's next

ArgoCD health is one piece of a bigger goal: making kgateway easy to run with confidence in large production environments, where many teams share gateways and changes flow through automated pipelines. The kgateway team is working on more management and observability features in that direction, so that you always know what your gateways are doing and why. Give the health checks a try, and let me know what you would like to see next on the [kgateway Slack](https://kgateway.dev/slack/).
