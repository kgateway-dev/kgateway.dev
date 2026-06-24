# JWT validation in kgateway

JWT validation allows kgateway to verify incoming requests using JSON Web Tokens before forwarding them to backend services. This guide shows how to configure JWT validation using `GatewayExtension` and `TrafficPolicy` resources.

## What JWT validation does

When a client sends a request with a bearer token in the `Authorization` header, the gateway validates the token against the issuer's public keys. If the token is valid, the request is forwarded upstream. If the token is missing or invalid, the gateway rejects the request.

At a high level, JWT validation usually checks:

- the token signature
- the token issuer
- the token audience
- token expiration

## Basic JWT validation setup

For a basic setup, you need two things:

- an `issuer` value that matches the `iss` claim in the token
- a JWKS (JSON Web Key Set) source that provides the public keys used to verify token signatures

In kgateway, JWT validation is configured through a `GatewayExtension`, then attached to traffic with a `TrafficPolicy`.

### 1. Configure the JWT provider

The example below uses a remote JWKS endpoint.

```yaml
apiVersion: gateway.kgateway.dev/v1alpha1
kind: GatewayExtension
metadata:
  name: jwt-auth
  namespace: kgateway-system
spec:
  jwt:
    providers:
      - name: example-idp
        issuer: https://auth.example.com/realms/demo
        jwks:
          remote:
            url: https://auth.example.com/realms/demo/protocol/openid-connect/certs
```

### 2. Attach the JWT config to traffic

Use a `TrafficPolicy` to apply the JWT provider to a gateway or route.

```yaml
apiVersion: gateway.kgateway.dev/v1alpha1
kind: TrafficPolicy
metadata:
  name: jwt-auth
  namespace: default
spec:
  targetRefs:
    - group: gateway.networking.k8s.io
      kind: Gateway
      name: http
  jwtAuth:
    extensionRef:
      name: jwt-auth
      namespace: kgateway-system
```

## Audience validation

Audience validation checks that the token was issued for your API, not just for another application that trusts the same identity provider.

Add one or more expected audiences when your issuer includes an `aud` claim:

```yaml
spec:
  jwt:
    providers:
      - name: example-idp
        issuer: https://auth.example.com/realms/demo
        audiences:
          - https://api.example.com
        jwks:
          remote:
            url: https://auth.example.com/realms/demo/protocol/openid-connect/certs
```

Use the API identifier that your identity provider already puts in the token.

## Claim propagation

After a token is validated, you can forward selected claims to your backend as headers. This is useful when an upstream service needs caller identity without parsing the JWT itself.

For example, you might forward the `sub` or `email` claim:

```yaml
spec:
  jwt:
    providers:
      - name: example-idp
        issuer: https://auth.example.com/realms/demo
        jwks:
          remote:
            url: https://auth.example.com/realms/demo/protocol/openid-connect/certs
        claimsToHeaders:
          - name: sub
            header: x-jwt-subject
          - name: email
            header: x-jwt-email
```

Use claim forwarding for identity context, not for access control decisions.

## Example configuration

The following example shows JWT validation, audience checking, and claim forwarding.

```yaml
apiVersion: gateway.kgateway.dev/v1alpha1
kind: GatewayExtension
metadata:
  name: jwt-auth
  namespace: kgateway-system
spec:
  jwt:
    providers:
      - name: example-idp
        issuer: https://auth.example.com/realms/demo
        audiences:
          - https://api.example.com
        jwks:
          remote:
            url: https://auth.example.com/realms/demo/protocol/openid-connect/certs
        claimsToHeaders:
          - name: sub
            header: x-jwt-subject
        forwardToken: false
---
apiVersion: gateway.kgateway.dev/v1alpha1
kind: TrafficPolicy
metadata:
  name: jwt-auth
  namespace: default
spec:
  targetRefs:
    - group: gateway.networking.k8s.io
      kind: Gateway
      name: http
  jwtAuth:
    extensionRef:
      name: jwt-auth
      namespace: kgateway-system
```

In this example:

- the gateway validates tokens issued by the configured issuer
- the token must include the expected audience
- the `sub` claim is forwarded as `x-jwt-subject`
- the original token is not forwarded upstream

## Testing the setup

Use `curl` with a bearer token in the `Authorization` header.

Without a token, the request should fail:

```sh
curl -vi "http://$INGRESS_GW_ADDRESS:8080/headers" \
  -H "host: www.example.com"
```

With a valid token, the request should succeed:

```sh
curl -vi "http://$INGRESS_GW_ADDRESS:8080/headers" \
  -H "host: www.example.com" \
  -H "Authorization: Bearer $JWT"
```

If you are testing locally with port-forwarding, use the same header pattern:

```sh
curl -vi "http://localhost:8080/headers" \
  -H "host: www.example.com" \
  -H "Authorization: Bearer $JWT"
```

When the setup is working, the backend should return `200 OK`. If you configured claim forwarding, the upstream request should include the forwarded header.

## Common issues and troubleshooting

### Invalid issuer

If the token is rejected with an issuer-related error, compare the token's `iss` claim with the `issuer` value in your config.

Things to check:

- the issuer URL matches exactly
- the token comes from the same identity provider you configured
- there are no trailing slash mismatches unless your issuer uses them consistently

### JWKS fetch failure

If the gateway cannot retrieve the signing keys, the token cannot be verified.

Things to check:

- the JWKS URL is correct
- the JWKS endpoint is reachable from the gateway
- TLS and service connectivity are working if the JWKS endpoint is HTTPS

### Expired token

JWTs are time-bound. An expired token should be rejected.

Things to check:

- the token's `exp` claim is still valid
- your local clock is correct
- the client is refreshing tokens when needed

### Missing audience

If you configured audiences and the token does not include a matching `aud` claim, validation fails.

Things to check:

- the token includes an audience value
- the configured audience matches the API identifier used by your identity provider
- you are not confusing the gateway audience with a frontend application audience

## Summary

JWT validation gives kgateway a straightforward way to protect APIs at the edge. Start with issuer and JWKS validation, add audience checks when your tokens include them, and forward only the claims your backend actually needs.