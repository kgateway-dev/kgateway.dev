---
title: "Canary Deployments"
weight: 70
---

NGINX's canary annotations let you split traffic between versions. The tool merges these into a single HTTPRoute with weighted backends.

## Before: Primary and canary Ingresses

```bash
cat <<'EOF' > canary-ingress.yaml
# Primary Ingress
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: app-primary
spec:
  ingressClassName: nginx
  rules:
  - host: app.example.com
    http:
      paths:
      - backend:
          service:
            name: app-v1
            port:
              number: 80
        path: /
        pathType: Prefix
---
# Canary Ingress (20% of traffic)
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: app-canary
  annotations:
    nginx.ingress.kubernetes.io/canary: "true"
    nginx.ingress.kubernetes.io/canary-weight: "20"
spec:
  ingressClassName: nginx
  rules:
  - host: app.example.com
    http:
      paths:
      - backend:
          service:
            name: app-v2
            port:
              number: 80
        path: /
        pathType: Prefix
EOF
```

## Convert

```bash
ingress2gateway print --providers=ingress-nginx --emitter=kgateway \
  --input-file canary-ingress.yaml > canary-kgateway.yaml
```

## After: HTTPRoute with weighted backends

```bash
cat canary-kgateway.yaml
```

Both Ingresses merge into one HTTPRoute. Traffic is split 80/20:

```yaml
apiVersion: gateway.networking.k8s.io/v1
kind: HTTPRoute
metadata:
  name: app-primary-app-example-com
spec:
  hostnames:
  - app.example.com
  parentRefs:
  - name: nginx
  rules:
  - matches:
    - path:
        type: PathPrefix
        value: /
    backendRefs:
    - name: app-v1
      port: 80
      weight: 80
    - name: app-v2
      port: 80
      weight: 20
```

## Apply

```bash
kubectl apply -f canary-kgateway.yaml
```
