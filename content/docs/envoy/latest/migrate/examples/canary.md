---
title: "Canary Deployments"
description: Convert Ingress NGINX canary annotations to weighted HTTPRoute backends.
weight: 70
---

NGINX's canary annotations let you split traffic between versions. The tool merges these into a single HTTPRoute with weighted backends.

## Before: Primary and canary Ingresses

```bash
cat <<'EOF' > canary-ingress.yaml
# Primary Ingress
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: app-primary
spec:
  ingressClassName: nginx
  rules:
  - host: app.example.com
    http:
      paths:
      - backend:
          service:
            name: app-v1
            port:
              number: 80
        path: /
        pathType: Prefix
---
# Canary Ingress (20% of traffic)
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: app-canary
  annotations:
    nginx.ingress.kubernetes.io/canary: "true"
    nginx.ingress.kubernetes.io/canary-weight: "20"
spec:
  ingressClassName: nginx
  rules:
  - host: app.example.com
    http:
      paths:
      - backend:
          service:
            name: app-v2
            port:
              number: 80
        path: /
        pathType: Prefix
EOF
```

## Convert

```bash
ingress2gateway print --providers=ingress-nginx --emitter=kgateway \
  --input-file canary-ingress.yaml > canary-kgateway.yaml
```

The tool prints a warning that it does not translate HTTPS for the `app.example.com` host. By default, Ingress NGINX serves HTTPS for every host with a self-signed certificate. The generated Gateway has only an HTTP listener. To serve HTTPS, add an HTTPS listener to the Gateway. For more information, see [HTTPS listener]({{< link-hextra path="/setup/listeners/https/" >}}).

## After: HTTPRoute with weighted backends

```bash
cat canary-kgateway.yaml
```

The output has a Gateway and one HTTPRoute. Both Ingresses merge into the HTTPRoute, which takes its name from the canary Ingress, `app-canary`. The weights send 80% of traffic to `app-v1` and 20% to `app-v2`. The order of the two backends in the output can change from one run to the next.

```yaml
apiVersion: gateway.networking.k8s.io/v1
kind: Gateway
metadata:
  name: nginx
spec:
  gatewayClassName: kgateway
  listeners:
  - hostname: app.example.com
    name: app-example-com-http
    port: 80
    protocol: HTTP
---
apiVersion: gateway.networking.k8s.io/v1
kind: HTTPRoute
metadata:
  name: app-canary-app-example-com
spec:
  hostnames:
  - app.example.com
  parentRefs:
  - name: nginx
  rules:
  - backendRefs:
    - name: app-v1
      port: 80
      weight: 80
    - name: app-v2
      port: 80
      weight: 20
    matches:
    - path:
        type: PathPrefix
        value: /
    name: rule-0
```

## Apply

```bash
kubectl apply -f canary-kgateway.yaml
```
