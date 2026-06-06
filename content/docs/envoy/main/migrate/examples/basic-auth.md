---
title: "Basic Auth"
weight: 31
---

This example demonstrates how to migrate NGINX-style basic authentication to kgateway. In NGINX, this is typically handled via `auth-type: basic` and a secret reference. In kgateway, we use a `TrafficPolicy` with the `basicAuth` configuration.

## Before: Ingress with Basic Auth

Here is a standard NGINX Ingress using basic authentication:

```bash
cat <<'EOF' > basic-auth-ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: basic-auth-demo
  annotations:
    nginx.ingress.kubernetes.io/auth-type: basic
    nginx.ingress.kubernetes.io/auth-secret: my-htpasswd-secret
    nginx.ingress.kubernetes.io/auth-realm: "Authentication Required"
spec:
  ingressClassName: nginx
  rules:
  - host: auth.example.com
    http:
      paths:
      - backend:
          service:
            name: httpbin
            port:
              number: 8000
        path: /
        pathType: Prefix
EOF
```

## Convert

Run the conversion tool to generate the Gateway API resources:

```bash
ingress2gateway print --providers=ingress-nginx --emitter=kgateway \
  --input-file basic-auth-ingress.yaml > basic-auth-kgateway.yaml
```

## After: TrafficPolicy with Basic Auth

While the tool helps with the structure, you'll want to ensure your `TrafficPolicy` correctly points to the secret containing your credentials. The secret should contain your `htpasswd` data (typically in a key named `.htpasswd`).

```yaml
apiVersion: gateway.kgateway.dev/v1alpha1
kind: TrafficPolicy
metadata:
  name: basic-auth-policy
spec:
  targetRefs:
  - group: gateway.networking.k8s.io
    kind: HTTPRoute
    name: basic-auth-demo-auth-example-com
  basicAuth:
    secretRef:
      name: my-htpasswd-secret
      namespace: default
```

## Apply and verify

```bash
kubectl apply -f basic-auth-kgateway.yaml
kubectl get trafficpolicies
```
