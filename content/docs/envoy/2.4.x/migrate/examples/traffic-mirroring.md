---
title: "Traffic Mirroring"
description: Convert an Ingress with the NGINX mirror-target annotation, and add a Gateway API HTTPRoute RequestMirror filter by hand.
weight: 39
---

Traffic mirroring (shadowing) allows you to copy live traffic to a test service without impacting the original request/response flow. NGINX uses the `mirror-target` annotation, while Gateway API uses the `RequestMirror` filter. The conversion tool does not translate the annotation, so you add the filter by hand.

## Before: Ingress with Mirror Target

This Ingress mirrors all traffic from `production-svc` to `staging-svc`. The `mirror-target` annotation takes a URL, not a Service name. The NGINX variable `$request_uri` keeps the path and query of each request.

```bash
cat <<'EOF' > shadow-ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: shadow-demo
  annotations:
    nginx.ingress.kubernetes.io/mirror-target: "http://staging-svc.default.svc.cluster.local$request_uri"
spec:
  ingressClassName: nginx
  rules:
  - host: app.example.com
    http:
      paths:
      - backend:
          service:
            name: production-svc
            port:
              number: 80
        path: /
        pathType: Prefix
EOF
```

## Convert

```bash
ingress2gateway print --providers=ingress-nginx --emitter=kgateway \
  --input-file shadow-ingress.yaml > shadow-kgateway.yaml
```

The tool prints these warnings:

* The tool does not translate HTTPS for the `app.example.com` host. By default, Ingress NGINX serves HTTPS for every host with a self-signed certificate. The generated Gateway has only an HTTP listener. To serve HTTPS, add an HTTPS listener to the Gateway. For more information, see [HTTPS listener]({{< link-hextra path="/setup/listeners/https/" >}}).
* `Unsupported annotation nginx.ingress.kubernetes.io/mirror-target`. The tool drops the annotation. The output does not mirror traffic.

## After: Gateway and HTTPRoute

```bash
cat shadow-kgateway.yaml
```

The output has a Gateway and an HTTPRoute. The HTTPRoute sends traffic to `production-svc` only. It has no `RequestMirror` filter.

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
  name: shadow-demo-app-example-com
spec:
  hostnames:
  - app.example.com
  parentRefs:
  - name: nginx
  rules:
  - backendRefs:
    - name: production-svc
      port: 80
    matches:
    - path:
        type: PathPrefix
        value: /
    name: rule-0
```

To mirror traffic, you add a `RequestMirror` filter to the HTTPRoute rule by hand. The filter refers to the `staging-svc` Service by name and port, instead of by URL.

## Apply and verify

Apply the converted resources.

```bash
kubectl apply -f shadow-kgateway.yaml
```

Replace the HTTPRoute with a version that mirrors each request to the `staging-svc` Service on port 80. The gateway sends the response from `production-svc` back to the client, and ignores the response from `staging-svc`.

```yaml
kubectl apply -f- <<EOF
apiVersion: gateway.networking.k8s.io/v1
kind: HTTPRoute
metadata:
  name: shadow-demo-app-example-com
spec:
  hostnames:
  - app.example.com
  parentRefs:
  - name: nginx
  rules:
  - backendRefs:
    - name: production-svc
      port: 80
    matches:
    - path:
        type: PathPrefix
        value: /
    name: rule-0
    filters:
    - type: RequestMirror
      requestMirror:
        backendRef:
          name: staging-svc
          port: 80
EOF
```

Check that the HTTPRoute has the mirror filter.

```bash
kubectl get httproute shadow-demo-app-example-com -o yaml
```
