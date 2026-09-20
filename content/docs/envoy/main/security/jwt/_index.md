---
title: JWT
weight: 10
description: Control access or route traffic based on verified claims in a JSON web token (JWT).
---

{{< reuse "kgw-docs/snippets/jwt-about.md" >}}

## JWT caching

You can enable Envoy JWT caching for verified tokens in a `JWTProvider` configuration. The cache stores tokens that already passed signature verification, so repeated requests with the same token do not repeat the parse, JWKS lookup, and signature verification work.

Set `spec.jwt.providers[].cache` on the GatewayExtension resource to turn on the cache. Leaving `cache` unset keeps JWT caching disabled. The `cache.size` field sets the number of verified tokens to cache per Envoy worker thread and defaults to `100` when omitted. The `cache.maxTokenSize` field sets the maximum cached token size in bytes and defaults to `4096` when omitted.

```yaml
apiVersion: gateway.kgateway.dev/v1alpha1
kind: GatewayExtension
metadata:
  name: selfminted-jwt
spec:
  jwt:
    providers:
      - name: selfminted
        issuer: kgateway.dev
        cache:
          size: 1024
          maxTokenSize: 8192
        jwks:
          local:
            inline: '{"keys":[{"kty":"RSA","kid":"kgateway-public-key-001","use":"sig","alg":"RS256","n":"...","e":"AQAB"}]}'
```

| Field | Description |
| ----- | ----------- |
| `cache` | Enables Envoy JWT caching for this provider. An empty object turns on caching with Envoy defaults. |
| `cache.size` | The number of verified tokens to cache per Envoy worker thread. If unset, Envoy uses `100`. |
| `cache.maxTokenSize` | The maximum size of one cached token in bytes. If unset, Envoy uses `4096`. |

Caching does not extend a token's validity. Envoy caches only verified tokens, checks token time constraints on each cache hit, and removes expired tokens from the cache.
