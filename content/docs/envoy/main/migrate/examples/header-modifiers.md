---
title: "Header Modifiers"
description: Convert NGINX header directives to a Gateway API HTTPRoute RequestHeaderModifier filter.
weight: 35
---

Whether you're adding security headers or passing custom metadata to your backends, NGINX uses the `add_header` directive or `configuration-snippet`. In Gateway API, this is a native feature of the `HTTPRoute` resource.

## Before: Ingress with Custom Headers

An NGINX Ingress adding a custom header to requests:

```bash
cat <<'EOF' > headers-ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: headers-demo
  annotations:
    nginx.ingress.kubernetes.io/configuration-snippet: |
      more_set_headers "X-Environment: production";
spec:
  ingressClassName: nginx
  rules:
  - host: app.example.com
    http:
      paths:
      - backend:
          service:
            name: web-backend
            port:
              number: 80
        path: /
        pathType: Prefix
EOF
```

## Convert

```bash
ingress2gateway print --providers=ingress-nginx --emitter=kgateway \
  --input-file headers-ingress.yaml > headers-kgateway.yaml
```

## After: HTTPRoute with Header Filters

Because the header is set in a raw `configuration-snippet`, `ingress2gateway` can't translate it. You add the filter to the generated `HTTPRoute` by hand. The Gateway API `HTTPRoute` includes a `RequestHeaderModifier` filter to handle this natively:

```yaml
apiVersion: gateway.networking.k8s.io/v1
kind: HTTPRoute
metadata:
  name: headers-demo-app-example-com
spec:
  hostnames:
  - app.example.com
  parentRefs:
  - name: nginx
  rules:
  - backendRefs:
    - name: web-backend
      port: 80
    filters:
    - type: RequestHeaderModifier
      requestHeaderModifier:
        add:
        - name: X-Environment
          value: production
```

## Apply and verify

```bash
kubectl apply -f headers-kgateway.yaml
kubectl get httproutes
```
