---
title: Listeners
description: Add HTTP, HTTPS, TCP, TLS, mTLS, and SNI listeners to your gateway.
weight: 20
---

Use a ListenerPolicy to configure listener-level connection behavior. For example, `spec.default.httpSettings.maxConnectionDuration` limits how long a downstream HTTP connection can stay open before Envoy starts draining it.
