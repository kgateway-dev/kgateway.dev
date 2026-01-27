---
title: "CORS"
weight: 40
---

CORS annotations on an Ingress become a `TrafficPolicy` with CORS settings.

## Before: Ingress with CORS

```bash
cat <<'EOF' > cors-ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: cors-demo
  annotations:
    nginx.ingress.kubernetes.io/enable-cors: "true"
    nginx.ingress.kubernetes.io/cors-allow-origin: "https://example.com, https://app.example.com"
    nginx.ingress.kubernetes.io/cors-allow-methods: "GET, POST, PUT, DELETE, OPTIONS"
    nginx.ingress.kubernetes.io/cors-allow-headers: "Authorization, Content-Type"
    nginx.ingress.kubernetes.io/cors-max-age: "3600"
spec:
  ingressClassName: nginx
  rules:
  - host: api.example.com
    http:
      paths:
      - backend:
          service:
            name: api-service
            port:
              number: 8080
        path: /
        pathType: Prefix
EOF
```

## Convert

```bash
ingress2gateway print --providers=ingress-nginx --emitter=kgateway \
  --input-file cors-ingress.yaml > cors-kgateway.yaml
```

## After: TrafficPolicy with CORS

```yaml
apiVersion: gateway.kgateway.dev/v1alpha1
kind: TrafficPolicy
metadata:
  name: cors-demo-policy
spec:
  targetRefs:
  - group: gateway.networking.k8s.io
    kind: HTTPRoute
    name: cors-demo-api-example-com
  cors:
    allowOrigins:
    - https://example.com
    - https://app.example.com
    allowMethods:
    - GET
    - POST
    - PUT
    - DELETE
    - OPTIONS
    allowHeaders:
    - Authorization
    - Content-Type
    maxAge: 3600s
```

## Apply

```bash
kubectl apply -f cors-kgateway.yaml
```
