---
title: "Backend TLS"
weight: 80
---

When your backend requires TLS (re-encryption), NGINX's `proxy-ssl-*` annotations translate to a agentgateway `AgentgatewayPolicy` with TLS settings.

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
ingress2gateway print --providers=ingress-nginx --emitter=agentgateway \
  --input-file backend-tls-ingress.yaml > backend-tls-agentgateway.yaml
```

## After: AgentgatewayPolicy with TLS

```yaml
apiVersion: extensions.agentgateway.kgateway.dev/v1alpha1
kind: AgentgatewayPolicy
metadata:
  name: secure-api-backend-tls
spec:
  targetRefs:
  - group: ""
    kind: Service
    name: secure-api
  backend:
    tls:
      mtlsCertificateRef:
      - name: backend-tls-secret
      sni: internal-api.example.com
```

The `insecureSkipVerify: false` means certificate verification is enabled (matching `proxy-ssl-verify: "on"`).

## Apply

```bash
kubectl apply -f backend-tls-agentgateway.yaml
```
