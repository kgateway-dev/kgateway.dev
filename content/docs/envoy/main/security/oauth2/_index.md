---
title: OAuth2/OIDC
weight: 15
description: Protect routes with browser-based OAuth2/OIDC login flows backed by any standards-compliant identity provider.
---

kgateway has built-in support for the OAuth2 authorization code flow. Point a `GatewayExtension` at your provider, attach it to a route via `TrafficPolicy`, and the gateway handles the rest - login redirects, token exchange, and session cookies - without touching your upstream service.

{{< cards >}}
  {{< card link="keycloak" title="Keycloak" >}}
{{< /cards >}}
