---
title: "Timeouts"
description: Convert NGINX proxy timeout annotations to kgateway TrafficPolicy and BackendConfigPolicy timeouts.
weight: 36
---

Connection and request timeouts are critical for stability. NGINX uses proxy-level directives like `proxy_read_timeout` and `proxy_connect_timeout`. In kgateway, request and idle-stream timeouts live on a `TrafficPolicy`, while the upstream connection timeout belongs to a `BackendConfigPolicy`.

## Before: Ingress with Timeouts

An NGINX Ingress configured with custom read and connect timeouts (values in seconds):

```bash
cat <<'EOF' > timeouts-ingress.yaml
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
EOF
```

## Convert

```bash
ingress2gateway print --providers=ingress-nginx --emitter=kgateway \
  --input-file timeouts-ingress.yaml > timeouts-kgateway.yaml
```

## After: TrafficPolicy and BackendConfigPolicy

The `TrafficPolicy` defines the request and idle-stream timeouts on the targeted route. The kgateway `Timeouts` type exposes two fields: `request` (overall request timeout) and `streamIdle` (idle stream timeout, equivalent to NGINX's `proxy_read_timeout`).

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
    streamIdle: 60s
```

The NGINX `proxy-connect-timeout` annotation has no equivalent under `TrafficPolicy.timeouts`. Connection-level timeouts are configured on a `BackendConfigPolicy` that targets the upstream Service:

```yaml
apiVersion: gateway.kgateway.dev/v1alpha1
kind: BackendConfigPolicy
metadata:
  name: timeouts-backend
spec:
  targetRefs:
  - group: ""
    kind: Service
    name: slow-svc
  connectTimeout: 15s
```

## Apply and verify

```bash
kubectl apply -f timeouts-kgateway.yaml
kubectl get trafficpolicies
kubectl get backendconfigpolicies
```
