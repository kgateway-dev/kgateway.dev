---
title: "JWT Authentication"
description: Convert NGINX Plus JWT authentication to a kgateway GatewayExtension and TrafficPolicy.
weight: 32
---

This example migrates NGINX's `auth-jwt` (often used in NGINX Plus) or custom external authentication to kgateway's native JWT support. In kgateway, JWT configuration is split between a `GatewayExtension` (which defines the provider) and a `TrafficPolicy` (which applies it to a route).

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

The tool prints a warning that HTTPS for the `jwt.example.com` host is not translated. By default, Ingress NGINX serves HTTPS for every host with a self-signed certificate. The generated Gateway has only an HTTP listener. To serve HTTPS, add an HTTPS listener to the Gateway. For more information, see [HTTPS listener]({{< link-hextra path="/setup/listeners/https/" >}}).

## After: Gateway and HTTPRoute

The converted file has only a Gateway named `nginx` and an HTTPRoute named `jwt-demo-jwt-example-com`. The `nginx.com/auth-jwt*` annotations are NGINX Plus extensions that the `ingress-nginx` provider doesn't recognize, so `ingress2gateway` won't emit JWT config for them.

Write the JWT resources to a separate file. kgateway uses a `GatewayExtension` to define your JWT providers once, which can then be referenced by any `TrafficPolicy`. The gateway fetches the JWKS through the `issuer` Backend, and the `BackendConfigPolicy` sets up TLS to the issuer with the system's trusted CA certificates. Replace the issuer and JWKS URL with the values of your identity provider.

```bash
cat <<'EOF' > jwt-auth.yaml
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
          backendRef:
            group: gateway.kgateway.dev
            kind: Backend
            name: issuer
---
apiVersion: gateway.kgateway.dev/v1alpha1
kind: Backend
metadata:
  name: issuer
spec:
  type: Static
  static:
    hosts:
    - host: issuer.example.com
      port: 443
---
apiVersion: gateway.kgateway.dev/v1alpha1
kind: BackendConfigPolicy
metadata:
  name: issuer-tls
spec:
  targetRefs:
  - group: gateway.kgateway.dev
    kind: Backend
    name: issuer
  tls:
    sni: issuer.example.com
    wellKnownCACertificates: System
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
EOF
```

## Apply and verify

Apply the converted resources and the JWT resources. Then, check that the GatewayExtension and the TrafficPolicy exist.

```bash
kubectl apply -f jwt-kgateway.yaml
kubectl apply -f jwt-auth.yaml
kubectl get gatewayextensions
kubectl get trafficpolicies
```
