---
title: "Backend TLS"
weight: 80
---

When your backend requires TLS (re-encryption), NGINX's `proxy-ssl-*` annotations translate to a kgateway `BackendConfigPolicy` with TLS settings.

## Before: Ingress with backend TLS

```bash
cat <<'EOF' > backend-tls-ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: backend-tls-demo
  annotations:
    nginx.ingress.kubernetes.io/proxy-ssl-secret: "default/backend-tls-secret"
    nginx.ingress.kubernetes.io/proxy-ssl-verify: "on"
    nginx.ingress.kubernetes.io/proxy-ssl-name: "internal-api.example.com"
spec:
  ingressClassName: nginx
  rules:
  - host: app.example.com
    http:
      paths:
      - backend:
          service:
            name: secure-api
            port:
              number: 443
        path: /api
        pathType: Prefix
EOF
```

## Convert

```bash
ingress2gateway print --providers=ingress-nginx --emitter=kgateway \
  --input-file backend-tls-ingress.yaml > backend-tls-kgateway.yaml
```

## After: BackendConfigPolicy with TLS

```bash
cat backend-tls-kgateway.yaml
```

```yaml
apiVersion: gateway.kgateway.dev/v1alpha1
kind: BackendConfigPolicy
metadata:
  name: secure-api-backend-config
spec:
  targetRefs:
  - group: ""
    kind: Service
    name: secure-api
  tls:
    secretRef:
      name: backend-tls-secret
      namespace: default
    sni: internal-api.example.com
    insecureSkipVerify: false
```

The `insecureSkipVerify: false` means certificate verification is enabled (matching `proxy-ssl-verify: "on"`).

## Apply

```bash
kubectl apply -f backend-tls-kgateway.yaml
```
