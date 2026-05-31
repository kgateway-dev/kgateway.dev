---
title: "Rate Limiting"
weight: 30
---

NGINX's `limit-rps` and `limit-rpm` annotations map to a kgateway `TrafficPolicy` with local rate limiting.

{{< callout type="info" >}}
**Not an exact 1:1 mapping.** Ingress-NGINX's `limit-rps`/`limit-rpm` use a shared memory zone keyed by client IP, applying the rate limit **per client IP address, per pod**. The kgateway local token bucket is shared across clients within the scope where the policy is attached (for example, a route or virtual host), rather than per client IP. If you need per-client-IP rate limiting, prefer global rate limiting with a `RemoteAddress` descriptor entry (keys on the effective downstream address). If you must use a `Header` descriptor with `X-Forwarded-For`, only do so when XFF is validated via trusted-proxy or trusted-hops configuration and normalized to the intended client IP (for example, the leftmost untrusted hop); otherwise clients can spoof or rotate the header and it may include multiple IPs.
{{< /callout >}}

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
ingress2gateway print --providers=ingress-nginx --emitter=kgateway \
  --input-file ratelimit-ingress.yaml > ratelimit-kgateway.yaml
```

## After: TrafficPolicy with token bucket

```bash
cat ratelimit-kgateway.yaml
```

The generated `TrafficPolicy` uses a token bucket algorithm. With 10 RPS and a 2x burst multiplier, you get `maxTokens: 20`:

```yaml
apiVersion: gateway.kgateway.dev/v1alpha1
kind: TrafficPolicy
metadata:
  name: ratelimit-demo-policy
spec:
  targetRefs:
  - group: gateway.networking.k8s.io
    kind: HTTPRoute
    name: ratelimit-demo-api-example-com
  rateLimit:
    local:
      tokenBucket:
        maxTokens: 20
        tokensPerFill: 10
        fillInterval: 1s
```

## Apply

```bash
kubectl apply -f ratelimit-kgateway.yaml
```
