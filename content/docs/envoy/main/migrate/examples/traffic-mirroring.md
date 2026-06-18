---
title: "Traffic Mirroring"
weight: 39
---

Traffic mirroring (shadowing) allows you to copy live traffic to a test service without impacting the original request/response flow. NGINX uses the `mirror-target` annotation, while Gateway API uses the `RequestMirror` filter.

## Before: Ingress with Mirror Target

This Ingress mirrors all traffic from `production-svc` to `staging-svc`:

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: shadow-demo
  annotations:
    nginx.ingress.kubernetes.io/mirror-target: "staging-svc"
spec:
  ingressClassName: nginx
  rules:
  - host: app.example.com
    http:
      paths:
      - backend:
          service:
            name: production-svc
            port:
              number: 80
        path: /
        pathType: Prefix
```

## Convert

```bash
ingress2gateway print --providers=ingress-nginx --emitter=kgateway \
  --input-file shadow-ingress.yaml > shadow-kgateway.yaml
```

## After: HTTPRoute with RequestMirror Filter

The resulting `HTTPRoute` copies traffic to the mirrored backend:

```yaml
apiVersion: gateway.networking.k8s.io/v1
kind: HTTPRoute
metadata:
  name: shadow-demo-app-example-com
spec:
  hostnames:
  - app.example.com
  parentRefs:
  - name: nginx
  rules:
  - backendRefs:
    - name: production-svc
      port: 80
    filters:
    - type: RequestMirror
      requestMirror:
        backendRef:
          name: staging-svc
          port: 80
```

## Apply and verify

```bash
kubectl apply -f shadow-kgateway.yaml
kubectl get httproutes
```
