---
title: Auth0
weight: 11
description: Set up OAuth2/OIDC authentication with Auth0 to protect routes through kgateway's built-in authorization code flow.
---

Protect an HTTPRoute with Auth0 as an OIDC provider. Kgateway handles the OAuth2 authorization code flow: unauthenticated browser requests get redirected to Auth0, the code is exchanged for tokens, and those tokens are stored in session cookies. Your upstream service doesn't need to know any of this happened.

You need three resources: a `Backend` pointing at your Auth0 host, a `GatewayExtension` to configure the OAuth2 provider, and a `TrafficPolicy` to attach it to a route.

## Before you begin

{{< reuse "kgw-docs/snippets/prereq.md" >}}

1. An Auth0 account with a configured Regular Web Application.
2. A test user created in your Auth0 database connection.

## Guides

{{< cards >}}
  {{< card link="setup" title="Setup Auth0" subtitle="Configure Auth0, create a test user, and set up the kgateway Backend and TLS." >}}
  {{< card link="authorization-code" title="Authorization code flow" subtitle="Protect browser traffic by redirecting users to Auth0 to log in." >}}
  {{< card link="access-token" title="Access token validation" subtitle="Validate tokens that API clients already hold." >}}
{{< /cards >}}