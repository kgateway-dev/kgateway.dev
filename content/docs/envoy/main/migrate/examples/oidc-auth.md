---
title: "OIDC Authentication"
weight: 34
---

Many teams use `oauth2-proxy` as a sidecar or external service to handle OIDC/OAuth2 for NGINX. kgateway simplifies this by providing native support via a `GatewayExtension` and `TrafficPolicy`.

## Before: Ingress with External Auth (OAuth2 Proxy)

Typical NGINX setup using `auth-url` to delegate to a proxy:

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: oidc-demo
  annotations:
    nginx.ingress.kubernetes.io/auth-url: "https://$host/oauth2/auth"
    nginx.ingress.kubernetes.io/auth-signin: "https://$host/oauth2/start?rd=$escaped_request_uri"
spec:
  ingressClassName: nginx
  rules:
  - host: oidc.example.com
    http:
      paths:
      - backend:
          service:
            name: httpbin
            port:
              number: 8000
        path: /
        pathType: Prefix
```

## Convert

```bash
ingress2gateway print --providers=ingress-nginx --emitter=kgateway \
  --input-file oidc-ingress.yaml > oidc-kgateway.yaml
```

## After: GatewayExtension and TrafficPolicy

Native OIDC support is configured using a `GatewayExtension` for the provider details and a `TrafficPolicy` to protect the route.

```yaml
apiVersion: gateway.kgateway.dev/v1alpha1
kind: GatewayExtension
metadata:
  name: google-oidc
spec:
  oauth2:
    issuerURI: https://accounts.google.com
    authorizationEndpoint: https://accounts.google.com/o/oauth2/v2/auth
    tokenEndpoint: https://oauth2.googleapis.com/token
    scopes:
    - openid
    - email
    credentials:
      clientId: my-client-id
      clientSecretRef:
        name: oidc-client-secret
---
apiVersion: gateway.kgateway.dev/v1alpha1
kind: TrafficPolicy
metadata:
  name: oidc-policy
spec:
  targetRefs:
  - group: gateway.networking.k8s.io
    kind: HTTPRoute
    name: oidc-demo-oidc-example-com
  oauth2:
    extensionRef:
      name: google-oidc
```

## Apply and verify

```bash
kubectl apply -f oidc-kgateway.yaml
kubectl get gatewayextensions
kubectl get trafficpolicies
```
