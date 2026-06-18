---
title: "JWT Authentication"
description: Convert NGINX Plus JWT authentication to a kgateway GatewayExtension and TrafficPolicy.
weight: 32
---

Migrating from NGINX's `auth-jwt` (often used in NGINX Plus) or custom external authentication to kgateway's native JWT support. In kgateway, JWT configuration is split between a `GatewayExtension` (which defines the provider) and a `TrafficPolicy` (which applies it to a route).

## Before: Ingress with JWT Auth

If you are using NGINX Plus, your Ingress might look like this:

```bash
cat <<'EOF' > jwt-ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: jwt-demo
  annotations:
    nginx.com/auth-jwt: "realm"
    nginx.com/auth-jwt-key: "jwt-key"
spec:
  ingressClassName: nginx
  rules:
  - host: jwt.example.com
    http:
      paths:
      - backend:
          service:
            name: httpbin
            port:
              number: 8000
        path: /
        pathType: Prefix
EOF
```

## Convert

```bash
ingress2gateway print --providers=ingress-nginx --emitter=kgateway \
  --input-file jwt-ingress.yaml > jwt-kgateway.yaml
```

## After: GatewayExtension and TrafficPolicy

The `nginx.com/auth-jwt*` annotations are NGINX Plus extensions that the `ingress-nginx` provider doesn't recognize, so `ingress2gateway` won't emit JWT config for them. You author the following resources by hand. kgateway uses a `GatewayExtension` to define your JWT providers once, which can then be referenced by any `TrafficPolicy`.

```yaml
apiVersion: gateway.kgateway.dev/v1alpha1
kind: GatewayExtension
metadata:
  name: jwt-provider
spec:
  jwt:
    providers:
    - name: my-issuer
      issuer: "https://issuer.example.com"
      jwks:
        remote:
          url: "https://issuer.example.com/.well-known/jwks.json"
---
apiVersion: gateway.kgateway.dev/v1alpha1
kind: TrafficPolicy
metadata:
  name: jwt-policy
spec:
  targetRefs:
  - group: gateway.networking.k8s.io
    kind: HTTPRoute
    name: jwt-demo-jwt-example-com
  jwtAuth:
    extensionRef:
      name: jwt-provider
```

## Apply and verify

```bash
kubectl apply -f jwt-kgateway.yaml
kubectl get gatewayextensions
kubectl get trafficpolicies
```
