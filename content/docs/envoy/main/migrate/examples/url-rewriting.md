---
title: "URL Rewriting"
weight: 37
---

Path rewriting is common when backends expect a different path than what is exposed publicly. NGINX uses the `rewrite-target` annotation, while Gateway API uses the `URLRewrite` filter in an `HTTPRoute`.

## Before: Ingress with Rewrite Target

In this example, requests to `/api/v1/users` are rewritten to `/users` before reaching the backend:

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: rewrite-demo
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /$2
spec:
  ingressClassName: nginx
  rules:
  - host: api.example.com
    http:
      paths:
      - path: /api/v1(/|$)(.*)
        pathType: ImplementationSpecific
        backend:
          service:
            name: backend-svc
            port:
              number: 80
```

## Convert

```bash
ingress2gateway print --providers=ingress-nginx --emitter=kgateway \
  --input-file rewrite-ingress.yaml > rewrite-kgateway.yaml
```

## After: HTTPRoute with URLRewrite Filter

Gateway API's `URLRewrite` filter handles the path transformation:

```yaml
apiVersion: gateway.networking.k8s.io/v1
kind: HTTPRoute
metadata:
  name: rewrite-demo-api-example-com
spec:
  hostnames:
  - api.example.com
  parentRefs:
  - name: nginx
  rules:
  - matches:
    - path:
        type: PathPrefix
        value: /api/v1
    filters:
    - type: URLRewrite
      urlRewrite:
        path:
          type: ReplacePrefixMatch
          replacePrefixMatch: /
    backendRefs:
    - name: backend-svc
      port: 80
```

## Apply and verify

```bash
kubectl apply -f rewrite-kgateway.yaml
kubectl get httproutes
```
