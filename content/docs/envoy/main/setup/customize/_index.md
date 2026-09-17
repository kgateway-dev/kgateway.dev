---
title: Customize the gateway
description: Customize the proxy deployment, service, and pod settings with GatewayParameters.
weight: 30
---

Use GatewayParameters to customize generated gateway proxy resources without replacing the default proxy template. When a GatewayClass and a Gateway both reference GatewayParameters, kgateway merges built-in security context fields by field. For Windows pods, `spec.kube.podTemplate.securityContext.windowsOptions.gmsaCredentialSpecName` remains separate from `gmsaCredentialSpec`, so a Gateway-level credential spec name can override the GatewayClass default.
