---
title: Listeners
description: Add HTTP, HTTPS, TCP, TLS, mTLS, and SNI listeners to your gateway.
weight: 20
---

You can configure HTTP protocol upgrades at the listener level or the route level. Use `ListenerPolicy.spec.default.httpSettings.upgradeConfig.enabledUpgrades` to allow upgrade tokens, such as `websocket` or `CONNECT`, on a listener. Use `TrafficPolicy.spec.httpUpgrade` to override a listener-level upgrade for targeted Gateway, HTTPRoute, or ListenerSet resources. To terminate CONNECT requests, set `httpUpgrade[].connect.terminate` to `true`. Do not combine `httpUpgrade` with enabled request buffering in the same TrafficPolicy.
