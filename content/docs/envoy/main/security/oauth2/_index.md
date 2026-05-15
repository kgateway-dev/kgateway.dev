---
title: OAuth2/OIDC
weight: 15
description: Protect routes with browser-based OAuth2/OIDC login flows backed by any standards-compliant identity provider.
---

kgateway has built-in support for the OAuth2 authorization code flow. Configure a `GatewayExtension` with your provider's endpoints and client credentials, attach it to a route via `TrafficPolicy`, and the gateway takes over: redirecting unauthenticated users to the login page, exchanging codes for tokens, and storing sessions in cookies — all without touching your upstream service.

{{< cards >}}
  {{< card link="keycloak" title="Keycloak" >}}
{{< /cards >}}
