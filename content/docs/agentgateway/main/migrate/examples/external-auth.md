title: "External Auth"
---
weight: 60
---

If you're using NGINX's `auth-url` to call an external authentication service, this becomes a agentgateway `AgentgatewayPolicy` with external auth configuration.

## Before: Ingress with external auth

```bash
cat <<'EOF' > external-auth-ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: ext-auth-demo
  annotations:
    nginx.ingress.kubernetes.io/auth-url: "http://auth-service.auth.svc.cluster.local/verify"
    nginx.ingress.kubernetes.io/auth-response-headers: "X-User-ID, X-User-Email"
spec:
  ingressClassName: nginx
  rules:
  - host: app.example.com
    http:
      paths:
      - backend:
          service:
            name: protected-app
            port:
              number: 8080
        path: /
        pathType: Prefix
EOF
```

## Convert

```bash
ingress2gateway print --providers=ingress-nginx --emitter=agentgateway \
  --input-file external-auth-ingress.yaml > external-auth-agentgateway.yaml
```

## After: AgentgatewayPolicy

The tool creates a `AgentgatewayPolicy` that configures the external auth service:

```yaml
apiVersion: extensions.agentgateway.kgateway.dev/v1alpha1
kind: AgentgatewayPolicy
metadata:
  name: ext-auth-demo-ext-auth
spec:
  targetRefs:
  - group: gateway.networking.k8s.io
    kind: HTTPRoute
    name: ext-auth-demo-app-example-com
  traffic:
    extAuth:
      backendRef:
        group: ""
        kind: Service
        name: auth-service
        namespace: auth
        port: 80
      http:
        path: '"/verify"'
        allowedResponseHeaders:
        - X-User-ID
        - X-User-Email
```

## Apply

```bash
kubectl apply -f external-auth-agentgateway.yaml
```
