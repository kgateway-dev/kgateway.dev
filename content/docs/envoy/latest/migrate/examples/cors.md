---
title: "CORS"
description: Convert Ingress NGINX CORS annotations to a kgateway TrafficPolicy.
weight: 40
---

CORS annotations on an Ingress become a `TrafficPolicy` with CORS settings.

## Before: Ingress with CORS

```bash
cat <<'EOF' > cors-ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: cors-demo
  annotations:
    nginx.ingress.kubernetes.io/enable-cors: "true"
    nginx.ingress.kubernetes.io/cors-allow-origin: "https://example.com, https://app.example.com"
    nginx.ingress.kubernetes.io/cors-allow-methods: "GET, POST, PUT, DELETE, OPTIONS"
    nginx.ingress.kubernetes.io/cors-allow-headers: "Authorization, Content-Type"
    nginx.ingress.kubernetes.io/cors-max-age: "3600"
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
  --input-file cors-ingress.yaml > cors-kgateway.yaml
```

The tool prints a warning that HTTPS for the `api.example.com` host is not translated. By default, Ingress NGINX serves HTTPS for every host with a self-signed certificate. The generated Gateway has only an HTTP listener. To serve HTTPS, add an HTTPS listener to the Gateway. For more information, see [HTTPS listener]({{< link-hextra path="/setup/listeners/https/" >}}).

## After: TrafficPolicy with CORS

```bash
cat cors-kgateway.yaml
```

The output has a Gateway, an HTTPRoute, and a TrafficPolicy. The TrafficPolicy applies to the rule named `rule-0` in the HTTPRoute.

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
  name: cors-demo-api-example-com
spec:
  hostnames:
  - api.example.com
  parentRefs:
  - name: nginx
  rules:
  - backendRefs:
    - name: api-service
      port: 8080
    filters:
    - responseHeaderModifier:
        remove:
        - Access-Control-Allow-Origin
        - Access-Control-Allow-Methods
        - Access-Control-Allow-Headers
        - Access-Control-Expose-Headers
        - Access-Control-Max-Age
        - Access-Control-Allow-Credentials
      type: ResponseHeaderModifier
    matches:
    - path:
        type: PathPrefix
        value: /
    name: rule-0
---
apiVersion: gateway.kgateway.dev/v1alpha1
kind: TrafficPolicy
metadata:
  name: cors-demo-api-example-com-0
spec:
  cors:
    allowCredentials: true
    allowHeaders:
    - Authorization
    - Content-Type
    allowMethods:
    - GET
    - POST
    - PUT
    - DELETE
    - OPTIONS
    allowOrigins:
    - https://example.com
    - https://app.example.com
    maxAge: 3600
  targetRefs:
  - group: gateway.networking.k8s.io
    kind: HTTPRoute
    name: cors-demo-api-example-com
    sectionName: rule-0
```

The output has two settings that are not in the Ingress:

* `allowCredentials: true`. The Ingress has no `cors-allow-credentials` annotation, and the default value of that annotation in Ingress NGINX is `true`. If cross-origin requests must not include credentials, such as cookies, set `allowCredentials: false` before you apply the file.
* A `ResponseHeaderModifier` filter on the HTTPRoute rule. The filter removes any `Access-Control-*` headers from the backend response. This way, the client gets the CORS headers from the TrafficPolicy, not from the backend.

## Apply

```bash
kubectl apply -f cors-kgateway.yaml
```
