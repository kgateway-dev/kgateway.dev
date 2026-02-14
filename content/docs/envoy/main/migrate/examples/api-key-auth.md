---
title: "API Key Authentication"
weight: 33
---

In open-source NGINX, API key validation is often implemented using a `configuration-snippet` that checks for a specific header. kgateway provides a more robust, native `apiKeyAuth` mechanism in its `TrafficPolicy`.

## Before: Ingress with API Key Check

This is a common way to enforce API keys in NGINX Ingress:

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: api-key-demo
  annotations:
    nginx.ingress.kubernetes.io/configuration-snippet: |
      if ($http_x_api_key = "") {
        return 401;
      }
spec:
  ingressClassName: nginx
  rules:
  - host: api.example.com
    http:
      paths:
      - backend:
          service:
            name: httpbin
            port:
              number: 8000
        path: /
        pathType: Prefix
```

## Convert

```bash
ingress2gateway print --providers=ingress-nginx --emitter=kgateway \
  --input-file api-key-ingress.yaml > api-key-kgateway.yaml
```

## After: TrafficPolicy with API Key Auth

Instead of a raw if-statement, you define the source (e.g., header name) and a secret containing the valid keys.

```yaml
apiVersion: gateway.kgateway.dev/v1alpha1
kind: TrafficPolicy
metadata:
  name: api-key-policy
spec:
  targetRefs:
  - group: gateway.networking.k8s.io
    kind: HTTPRoute
    name: api-key-demo-api-example-com
  apiKeyAuth:
    keySources:
    - header: X-API-Key
    secretRef:
      name: valid-api-keys
```

Each entry in the secret represents a valid client/key pair:

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: valid-api-keys
stringData:
  client-a: "key-12345"
  client-b: "key-67890"
```

## Apply and verify

```bash
kubectl apply -f api-key-kgateway.yaml
kubectl get trafficpolicies
```
