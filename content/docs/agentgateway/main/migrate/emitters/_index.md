---
title: "Emitters"
weight: 20
---

This page is the [upstream design](https://github.com/kubernetes-sigs/ingress2gateway/blob/main/docs/emitters.md) for ingress2gateway’s **provider/emitter** architecture.

> Tip: If you're here to understand **how ingress-nginx annotations are mapped to AgentGateway**, jump directly to the [AgentGateway emitter](./agentgateway/).

## Motivation

At KubeCon NA 2025 in Atlanta, SIG Network announced the [retirement of Ingress NGINX](https://kubernetes.io/blog/2025/11/11/ingress-nginx-retirement/), giving users only four months to migrate to another solution.
Ingress NGINX has ~100 custom annotations that extend the Kubernetes Ingress resource that don't have a direct mapping to Gateway API.
Thus, for ingress2gateway to be useful at helping users migrate, we need to output implementation-specific resources to maximize coverage of said annotations.

We expect third-party implementations to write and maintain emitters for their specific Gateway API implementations.
This document outlines the design of the emitter system and the policies around third-party code contributions.

## Architecture

At a high level, ingress2gateway will have two main components: providers and emitters.
Providers will read in Ingress-related resources and output an intermediate representation (IR) that is ingress-implementation-neutral.
Specifically, providers will output `EmitterIR` (standard Gateway API resources and some IR that captures any additional information that cannot be expressed in Standard Gateway API).

There will be a common emitter that reads the `EmitterIR` of the provider and translates it to potentially nonstandard Gateway API resources depending on configuration.
This gives us a common component that will implement logic "use any Gateway API feature vs only use stable Gateway API features".
The common emitter will output `EmitterIR`.

Implementation-specific Emitters will read the `EmitterIR` from the common emitter and output Gateway API resources along with implementation-specific resources.
Both providers and emitters MUST log any information that is lost in translation.
Ideally, when there is new IR and an emitter does not implement it, ingress2gateway should automatically emit notifications.

Note that the emitters MAY modify the Gateway API resources as needed.
That said, emitters MUST NOT output non-Gateway API resources unless absolutely necessary.
For example, once Gateway API's CORS support is stable, ingress2gateway should no longer output [Envoy Gateway CORS](https://gateway.envoyproxy.io/docs/tasks/security/cors/).

The architecture looks as follows.
The `provider` and `emitter` are implementation-specific components.
So the `provider` could be an "Ingress NGINX provider" that understands Ingress NGINX annotations,
and the `emitter` could be an "Envoy Gateway emitter" that outputs Envoy Gateway resources.

```bash
+------------------------------+
|(Ingress + related Resources) |
+-----+------------------------+
      |
      | 1) provider.ToIR(resources)
      v
+-----+--------+
| Emitter IR 1 |
+-----+--------+
      |
      | 2) CommonEmitter.Emit(IR 1)
      v
+-----+--------+
| Emitter IR 2 |
+-----+--------+
      |
      | 3) emitter.Emit(IR 2)
      v
+-----+-----------------------------+
| Gateway API Resources             |
| Implementation-specific Resources |
+-----------------------------------+
```
