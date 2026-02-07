---
title: "Rate Limiting"
weight: 30
---

NGINX's `limit-rps` and `limit-rpm` annotations map to a agentgateway `AgentgatewayPolicy` with local rate limiting.

## Before: Ingress with rate limits

```bash
cat <<'EOF' > ratelimit-ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: ratelimit-demo
  annotations:
    nginx.ingress.kubernetes.io/limit-rps: "10"
    nginx.ingress.kubernetes.io/limit-burst-multiplier: "2"
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
ingress2gateway print --providers=ingress-nginx --emitter=agentgateway \
  --input-file ratelimit-ingress.yaml > ratelimit-agentgateway.yaml
```

## After: AgentgatewayPolicy with token bucket

The generated `AgentgatewayPolicy` uses a token bucket algorithm. With 10 RPS and a 2x burst multiplier, you get `maxTokens: 20`:

```yaml
apiVersion: extensions.agentgateway.kgateway.dev/v1alpha1
kind: AgentgatewayPolicy
metadata:
  name: ratelimit-demo-nginx-ingress
spec:
  targetRefs:
  - group: gateway.networking.k8s.io
    kind: HTTPRoute
    name: ratelimit-demo-api-example-com
  localRateLimit:
    requests: 10
    unit: Seconds
    burst: 20
```

## Apply

```bash
kubectl apply -f ratelimit-agentgateway.yaml
```
