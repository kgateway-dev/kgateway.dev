---
title: "SSL Redirect"
weight: 50
---

The `ssl-redirect` annotation tells NGINX to redirect HTTP to HTTPS. In Gateway API, this becomes a `RequestRedirect` filter on the HTTPRoute.

## Before: Ingress with SSL redirect

```bash
cat <<'EOF' > ssl-redirect-ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: ssl-redirect-demo
  annotations:
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
spec:
  ingressClassName: nginx
  rules:
  - host: secure.example.com
    http:
      paths:
      - backend:
          service:
            name: web-app
            port:
              number: 8080
        path: /
        pathType: Prefix
EOF
```

## Convert

```bash
ingress2gateway print --providers=ingress-nginx --emitter=kgateway \
  --input-file ssl-redirect-ingress.yaml > ssl-redirect-kgateway.yaml
```

## After: HTTPRoute with redirect filter

```bash
cat ssl-redirect-kgateway.yaml
```

The HTTPRoute includes a `RequestRedirect` filter that sends a 301 to HTTPS:

```yaml
apiVersion: gateway.networking.k8s.io/v1
kind: HTTPRoute
metadata:
  name: ssl-redirect-demo-secure-example-com
spec:
  hostnames:
  - secure.example.com
  parentRefs:
  - name: nginx
  rules:
  - matches:
    - path:
        type: PathPrefix
        value: /
    filters:
    - type: RequestRedirect
      requestRedirect:
        scheme: https
        statusCode: 301
```

{{% callout note %}}
NGINX uses status code 308 by default, but Gateway API standardizes on 301.
{{% /callout %}}

## Apply

```bash
kubectl apply -f ssl-redirect-kgateway.yaml
```
