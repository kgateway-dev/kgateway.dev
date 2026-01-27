---
title: "Basic Ingress"
weight: 10
---

This example shows the simplest case: an Ingress with no special annotations. The tool converts it into a Gateway and HTTPRoute.

## Before: Ingress

```bash
cat <<'EOF' > basic-ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: demo-localhost
spec:
  ingressClassName: nginx
  rules:
  - host: demo.localdev.me
    http:
      paths:
      - backend:
          service:
            name: echo-backend
            port:
              number: 8080
        path: /
        pathType: Prefix
EOF
```

## Convert

```bash
ingress2gateway print --providers=ingress-nginx --emitter=kgateway --input-file basic-ingress.yaml > basic-kgateway.yaml
```

## After: Gateway API resources

```yaml
apiVersion: gateway.networking.k8s.io/v1
kind: Gateway
metadata:
  name: nginx
spec:
  gatewayClassName: kgateway
  listeners:
  - hostname: demo.localdev.me
    name: demo-localdev-me-http
    port: 80
    protocol: HTTP
---
apiVersion: gateway.networking.k8s.io/v1
kind: HTTPRoute
metadata:
  name: demo-localhost-demo-localdev-me
spec:
  hostnames:
  - demo.localdev.me
  parentRefs:
  - name: nginx
  rules:
  - backendRefs:
    - name: echo-backend
      port: 8080
    matches:
    - path:
        type: PathPrefix
        value: /
```

## Apply and verify

```bash
kubectl apply -f basic-kgateway.yaml
kubectl get gateways
kubectl get httproutes
```
