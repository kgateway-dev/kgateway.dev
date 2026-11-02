---
title: "Session Affinity"
description: Convert Ingress NGINX session affinity annotations to a kgateway BackendConfigPolicy.
weight: 20
---

If you're using NGINX's cookie-based session affinity, this example shows how those annotations translate to a kgateway `BackendConfigPolicy`.

## Before: Ingress with session affinity

```bash
cat <<'EOF' > session-affinity-ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: session-affinity-localhost
  annotations:
    nginx.ingress.kubernetes.io/affinity: "cookie"
    nginx.ingress.kubernetes.io/session-cookie-name: "session-id"
    nginx.ingress.kubernetes.io/session-cookie-path: "/api"
    nginx.ingress.kubernetes.io/session-cookie-samesite: "Strict"
    nginx.ingress.kubernetes.io/session-cookie-max-age: "604800"
    nginx.ingress.kubernetes.io/session-cookie-secure: "true"
spec:
  ingressClassName: nginx
  rules:
  - host: app.example.com
    http:
      paths:
      - backend:
          service:
            name: my-app
            port:
              number: 8080
        path: /
        pathType: Prefix
EOF
```

## Convert

```bash
ingress2gateway print --providers=ingress-nginx --emitter=kgateway \
  --input-file session-affinity-ingress.yaml > session-affinity-kgateway.yaml
```

The tool prints these warnings:

* The tool does not translate HTTPS for the `app.example.com` host. By default, Ingress NGINX serves HTTPS for every host with a self-signed certificate. The generated Gateway has only an HTTP listener. To serve HTTPS, add an HTTPS listener to the Gateway. For more information, see [HTTPS listener]({{< link-hextra path="/setup/listeners/https/" >}}).
* `failed to parse ... "nginx.ingress.kubernetes.io/affinity": Session affinity is not supported`. Despite this warning, the output has a BackendConfigPolicy with the cookie settings.

## After: Gateway API + BackendConfigPolicy

```bash
cat session-affinity-kgateway.yaml
```

The tool generates the usual Gateway and HTTPRoute, plus a `BackendConfigPolicy` that configures ring-hash load balancing with cookie-based hashing. The policy targets the `my-app` Service. The cookie's `max-age` of 604800 seconds becomes a `ttl` of `168h0m0s`.

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
  name: session-affinity-localhost-app-example-com
spec:
  hostnames:
  - app.example.com
  parentRefs:
  - name: nginx
  rules:
  - backendRefs:
    - name: my-app
      port: 8080
    matches:
    - path:
        type: PathPrefix
        value: /
    name: rule-0
---
apiVersion: gateway.kgateway.dev/v1alpha1
kind: BackendConfigPolicy
metadata:
  name: my-app-backend-config
spec:
  loadBalancer:
    ringHash:
      hashPolicies:
      - cookie:
          name: session-id
          path: /api
          sameSite: Strict
          secure: true
          ttl: 168h0m0s
  targetRefs:
  - group: ""
    kind: Service
    name: my-app
```

## Apply and verify

The BackendConfigPolicy takes effect only when the `my-app` Service exists in the same namespace.

```bash
kubectl apply -f session-affinity-kgateway.yaml
kubectl get backendconfigpolicies
```
