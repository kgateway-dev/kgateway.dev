---
title: "Header Modifiers"
description: Convert NGINX header directives to a Gateway API HTTPRoute RequestHeaderModifier filter.
weight: 35
---

To add security headers to responses or pass custom metadata to your backends, you use the `add_header` directive or a `configuration-snippet` in NGINX. In Gateway API, header changes are a native feature of the `HTTPRoute` resource.

## Before: Ingress with Custom Headers

The following NGINX Ingress adds a custom header to requests. The `more_set_input_headers` directive sets request headers.

```bash
cat <<'EOF' > headers-ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: headers-demo
  annotations:
    nginx.ingress.kubernetes.io/configuration-snippet: |
      more_set_input_headers "X-Environment: production";
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

The tool prints these warnings:

* The tool does not translate HTTPS for the `app.example.com` host. By default, Ingress NGINX serves HTTPS for every host with a self-signed certificate. The generated Gateway has only an HTTP listener. To serve HTTPS, add an HTTPS listener to the Gateway. For more information, see [HTTPS listener]({{< link-hextra path="/setup/listeners/https/" >}}).
* `Unsupported annotation nginx.ingress.kubernetes.io/configuration-snippet`. The snippet is raw NGINX configuration, so the tool drops it. The output does not set the header.

## After: Gateway and HTTPRoute

```bash
cat headers-kgateway.yaml
```

The output has a Gateway and an HTTPRoute without the header.

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
    matches:
    - path:
        type: PathPrefix
        value: /
    name: rule-0
```

To set the header, you add a `RequestHeaderModifier` filter to the rule of the generated HTTPRoute by hand.

## Apply and verify

Apply the converted resources.

```bash
kubectl apply -f headers-kgateway.yaml
```

Update the `headers-demo-app-example-com` HTTPRoute with a `RequestHeaderModifier` filter that sets the `X-Environment` header. Like `more_set_input_headers`, `set` replaces any value that the request already has. The rest of the HTTPRoute stays the same as the tool output.

```yaml
kubectl apply -f- <<EOF
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
        set:
        - name: X-Environment
          value: production
    matches:
    - path:
        type: PathPrefix
        value: /
    name: rule-0
EOF
```

Check that the HTTPRoute has the filter.

```bash
kubectl get httproute headers-demo-app-example-com -o yaml
```
