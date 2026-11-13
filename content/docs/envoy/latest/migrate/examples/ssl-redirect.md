---
title: "SSL Redirect"
description: Convert the Ingress NGINX SSL redirect annotation, and add an HTTPRoute RequestRedirect filter by hand.
weight: 50
---

The `ssl-redirect` annotation tells NGINX to redirect HTTP to HTTPS. In Gateway API, a redirect is a `RequestRedirect` filter on the HTTPRoute. The conversion tool does not create this filter, so you add it by hand.

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

The tool prints a warning that HTTPS for the `secure.example.com` host is not translated. By default, Ingress NGINX serves HTTPS for every host with a self-signed certificate. The generated Gateway has only an HTTP listener. To serve HTTPS, add an HTTPS listener to the Gateway. For more information, see [HTTPS listener]({{< link-hextra path="/setup/listeners/https/" >}}).

## After: Gateway and HTTPRoute

```bash
cat ssl-redirect-kgateway.yaml
```

The output has a Gateway and an HTTPRoute. The HTTPRoute has no `RequestRedirect` filter. The rule sends traffic to the `web-app` backend.

```yaml
apiVersion: gateway.networking.k8s.io/v1
kind: Gateway
metadata:
  name: nginx
spec:
  gatewayClassName: kgateway
  listeners:
  - hostname: secure.example.com
    name: secure-example-com-http
    port: 80
    protocol: HTTP
---
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
  - backendRefs:
    - name: web-app
      port: 8080
    matches:
    - path:
        type: PathPrefix
        value: /
    name: rule-0
```

This output matches what Ingress NGINX does with this Ingress. Ingress NGINX redirects to HTTPS only for hosts in the Ingress's `tls` section. This Ingress has no `tls` section, so Ingress NGINX does not redirect.

If you serve HTTPS for the host, you add the redirect yourself. Ingress NGINX redirects with the status code 308 by default. Gateway API accepts the status codes 301, 302, 303, 307, and 308, and uses 302 if you do not set one.

## Apply

Apply the converted resources.

```bash
kubectl apply -f ssl-redirect-kgateway.yaml
```

Replace the HTTPRoute with a version that redirects HTTP requests to HTTPS with a 308 status code. The `sectionName` attaches the route to the HTTP listener only, so that HTTPS requests are not redirected again. Before you send traffic, add an HTTPS listener to the Gateway and a route for it, as described in [HTTPS listener]({{< link-hextra path="/setup/listeners/https/" >}}). Otherwise, the redirect points to an HTTPS port that does not exist.

```yaml
kubectl apply -f- <<EOF
apiVersion: gateway.networking.k8s.io/v1
kind: HTTPRoute
metadata:
  name: ssl-redirect-demo-secure-example-com
spec:
  hostnames:
  - secure.example.com
  parentRefs:
  - name: nginx
    sectionName: secure-example-com-http
  rules:
  - matches:
    - path:
        type: PathPrefix
        value: /
    name: rule-0
    filters:
    - type: RequestRedirect
      requestRedirect:
        scheme: https
        statusCode: 308
EOF
```

Check that the HTTPRoute has the redirect filter.

```bash
kubectl get httproute ssl-redirect-demo-secure-example-com -o yaml
```
