---
title: "Request Buffering"
weight: 38
---

Managing the maximum allowed request size is a basic security requirement. NGINX uses the `proxy-body-size` annotation (equivalent to `client_max_body_size`). In kgateway, this is configured via the `buffer` field in a `TrafficPolicy`.

## Before: Ingress with Max Body Size

Configuration for an Ingress that allows uploads up to 20MB:

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: upload-demo
  annotations:
    nginx.ingress.kubernetes.io/proxy-body-size: "20m"
spec:
  ingressClassName: nginx
  rules:
  - host: upload.example.com
    http:
      paths:
      - backend:
          service:
            name: upload-svc
            port:
              number: 8080
        path: /
        pathType: Prefix
```

## Convert

```bash
ingress2gateway print --providers=ingress-nginx --emitter=kgateway \
  --input-file upload-ingress.yaml > upload-kgateway.yaml
```

## After: TrafficPolicy with Buffer

The `TrafficPolicy` enforces the body size limit:

```yaml
apiVersion: gateway.kgateway.dev/v1alpha1
kind: TrafficPolicy
metadata:
  name: buffering-policy
spec:
  targetRefs:
  - group: gateway.networking.k8s.io
    kind: HTTPRoute
    name: upload-demo-upload-example-com
  buffer:
    maxRequestSize: "20Mi"
```

## Apply and verify

```bash
kubectl apply -f upload-kgateway.yaml
kubectl get trafficpolicies
```
