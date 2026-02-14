---
title: "Timeouts"
weight: 36
---

Connection and request timeouts are critical for stability. NGINX uses proxy-level directives like `proxy_read_timeout`. In kgateway, these are consolidated into the `timeouts` section of a `TrafficPolicy`.

## Before: Ingress with Timeouts

An NGINX Ingress configured with custom read and connect timeouts (values in seconds):

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: timeouts-demo
  annotations:
    nginx.ingress.kubernetes.io/proxy-connect-timeout: "15"
    nginx.ingress.kubernetes.io/proxy-read-timeout: "60"
spec:
  ingressClassName: nginx
  rules:
  - host: timeouts.example.com
    http:
      paths:
      - backend:
          service:
            name: slow-svc
            port:
              number: 80
        path: /
        pathType: Prefix
```

## Convert

```bash
ingress2gateway print --providers=ingress-nginx --emitter=kgateway \
  --input-file timeouts-ingress.yaml > timeouts-kgateway.yaml
```

## After: TrafficPolicy with Timeouts

The `TrafficPolicy` defines the timeout behavior for the targeted route:

```yaml
apiVersion: gateway.kgateway.dev/v1alpha1
kind: TrafficPolicy
metadata:
  name: timeouts-policy
spec:
  targetRefs:
  - group: gateway.networking.k8s.io
    kind: HTTPRoute
    name: timeouts-demo-timeouts-example-com
  timeouts:
    request: 60s
    backendRequest: 60s
```

## Apply and verify

```bash
kubectl apply -f timeouts-kgateway.yaml
kubectl get trafficpolicies
```
