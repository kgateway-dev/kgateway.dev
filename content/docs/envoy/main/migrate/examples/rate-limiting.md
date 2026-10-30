---
title: "Rate Limiting"
description: Convert Ingress NGINX rate limit annotations to a kgateway TrafficPolicy.
weight: 30
---

NGINX's `limit-rps` and `limit-rpm` annotations map to a kgateway `TrafficPolicy` with local rate limiting.

## Mapping considerations

Note that the Ingress-NGINX annotation to kgateway TrafficPolicy mapping is not 1:1. The `limit-rps`/`limit-rpm` use a shared memory zone keyed by client IP, applying the rate limit **per client IP address, per pod**. In contrast, the kgateway local token bucket is shared across clients within the scope where the policy is attached (for example, a route), rather than per client IP address.

- Per-client IP address: If you need per-client-IP rate limiting, use global rate limiting with a `RemoteAddress` descriptor entry (keys on the effective downstream address).
- Forwarded headers: If you need a `Header` descriptor with `X-Forwarded-For`, only do so when XFF is validated via trusted-proxy or trusted-hops configuration and normalized to the intended client IP address (for example, the leftmost untrusted hop). Otherwise, clients can spoof or rotate the header and it might include multiple IP addresses.

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

The tool prints two warnings:

* The tool does not translate HTTPS for the `api.example.com` host. By default, Ingress NGINX serves HTTPS for every host with a self-signed certificate. The generated Gateway has only an HTTP listener. To serve HTTPS, add an HTTPS listener to the Gateway. For more information, see [HTTPS listener]({{< link-hextra path="/setup/listeners/https/" >}}).
* The tool failed to apply the `limit-rps` and `limit-burst-multiplier` annotations to the HTTPRoute. This warning is about the HTTPRoute only. The rate limit is still in the output, as a separate TrafficPolicy.

## After: TrafficPolicy with token bucket

```bash
cat ratelimit-kgateway.yaml
```

The output has a Gateway, an HTTPRoute, and a TrafficPolicy. The TrafficPolicy uses a token bucket algorithm. The rate is 10 requests per second, and the 2x burst multiplier sets `maxTokens` to 20. The `targetRefs` entry names the `rule-0` rule, so the policy applies to that rule of the HTTPRoute.

```yaml
apiVersion: gateway.networking.k8s.io/v1
kind: Gateway
metadata:
  name: nginx
spec:
  gatewayClassName: kgateway
  listeners:
  - hostname: api.example.com
    name: api-example-com-http
    port: 80
    protocol: HTTP
---
apiVersion: gateway.networking.k8s.io/v1
kind: HTTPRoute
metadata:
  name: ratelimit-demo-api-example-com
spec:
  hostnames:
  - api.example.com
  parentRefs:
  - name: nginx
  rules:
  - backendRefs:
    - name: api-service
      port: 8080
    matches:
    - path:
        type: PathPrefix
        value: /
    name: rule-0
---
apiVersion: gateway.kgateway.dev/v1alpha1
kind: TrafficPolicy
metadata:
  name: ratelimit-demo-api-example-com-0
spec:
  rateLimit:
    local:
      tokenBucket:
        fillInterval: 1s
        maxTokens: 20
        tokensPerFill: 10
  targetRefs:
  - group: gateway.networking.k8s.io
    kind: HTTPRoute
    name: ratelimit-demo-api-example-com
    sectionName: rule-0
```

## Apply

```bash
kubectl apply -f ratelimit-kgateway.yaml
```
