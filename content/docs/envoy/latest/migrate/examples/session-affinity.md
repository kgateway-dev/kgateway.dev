---
title: "Session Affinity"
weight: 20
---

If you're using NGINX's cookie-based session affinity, this example shows how those annotations translate to a kgateway `BackendConfigPolicy`.

## Before: Ingress with session affinity

```bash
cat <<'EOF' > session-affinity-ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: session-affinity-localhost
  annotations:
    nginx.ingress.kubernetes.io/affinity: "cookie"
    nginx.ingress.kubernetes.io/session-cookie-name: "session-id"
    nginx.ingress.kubernetes.io/session-cookie-path: "/api"
    nginx.ingress.kubernetes.io/session-cookie-samesite: "Strict"
    nginx.ingress.kubernetes.io/session-cookie-max-age: "604800"
    nginx.ingress.kubernetes.io/session-cookie-secure: "true"
spec:
  ingressClassName: nginx
  rules:
  - host: app.example.com
    http:
      paths:
      - backend:
          service:
            name: my-app
            port:
              number: 8080
        path: /
        pathType: Prefix
EOF
```

## Convert

```bash
ingress2gateway print --providers=ingress-nginx --emitter=kgateway \
  --input-file session-affinity-ingress.yaml > session-affinity-kgateway.yaml
```

## After: Gateway API + BackendConfigPolicy

The tool generates the usual Gateway and HTTPRoute, plus a `BackendConfigPolicy` that configures ring-hash load balancing with cookie-based hashing:

```yaml
apiVersion: gateway.kgateway.dev/v1alpha1
kind: BackendConfigPolicy
metadata:
  name: my-app-backend-config
spec:
  targetRefs:
  - group: ""
    kind: Service
    name: my-app
  loadBalancer:
    ringHash:
      hashPolicies:
      - cookie:
          name: session-id
          path: /api
          sameSite: Strict
          secure: true
          ttl: 168h0m0s
```

## Apply and verify

```bash
kubectl apply -f session-affinity-kgateway.yaml
kubectl get backendconfigpolicies
```
