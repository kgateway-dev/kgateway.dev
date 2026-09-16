---
title: JWT
weight: 10
description: Control access or route traffic based on verified claims in a JSON web token (JWT).
---

{{< reuse "kgw-docs/snippets/jwt-about.md" >}}

## Remote JWKS fetch timeout

When a JWT provider uses a remote JSON Web Key Set (JWKS), kgateway fetches the signing keys from the remote JWKS server. By default, kgateway waits up to 5 seconds for the remote JWKS server to respond. To use a different fetch limit, set `timeout` in the `jwks.remote` configuration.

```yaml
apiVersion: gateway.kgateway.dev/v1alpha1
kind: GatewayExtension
metadata:
  name: jwt-ext
spec:
  jwt:
    providers:
      - name: timeout-provider
        issuer: https://dev.example.com
        jwks:
          remote:
            url: https://dev.example.com/jwks
            backendRef:
              name: remote-jwks
              port: 8080
            timeout: 10s
```

| Field | Description |
| ----- | ----------- |
| `spec.jwt.providers[].jwks.remote.timeout` | The maximum time that kgateway waits when it fetches signing keys from the remote JWKS server. If omitted, kgateway uses `5s`. The value is a duration string, can be up to 32 characters, and must be at least `1ms`. |
