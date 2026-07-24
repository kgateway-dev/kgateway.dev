---
title: "URL Rewriting"
description: Convert the NGINX rewrite-target annotation to a Gateway API HTTPRoute URLRewrite filter.
weight: 37
---

Path rewriting is common when backends expect a different path than what is exposed publicly. NGINX uses the `rewrite-target` annotation, while Gateway API uses the `URLRewrite` filter in an `HTTPRoute`.

## Before: Ingress with Rewrite Target

In this example, requests to `/api/v1/users` are rewritten to `/users` before reaching the backend:

```bash
cat <<'EOF' > rewrite-ingress.yaml
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
EOF
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

> [!NOTE]
> Edge case: a request to `/api/v1` (no trailing slash) matches the `PathPrefix` of `/api/v1`, and `ReplacePrefixMatch: /` leaves an empty replacement — the backend sees a request to an empty path. If clients can send a bare `/api/v1`, add a second match for `/api/v1/` or normalize on the backend.

## Apply and verify

```bash
kubectl apply -f rewrite-kgateway.yaml
kubectl get httproutes
```
