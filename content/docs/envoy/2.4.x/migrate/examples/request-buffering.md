---
title: "Request Buffering"
description: Convert the NGINX proxy-body-size annotation to a kgateway TrafficPolicy buffer limit.
weight: 38
---

Managing the maximum allowed request size is a basic security requirement. NGINX uses the `proxy-body-size` annotation (equivalent to `client_max_body_size`). In kgateway, this is configured via the `buffer` field in a `TrafficPolicy`.

## Before: Ingress with Max Body Size

Configuration for an Ingress that allows uploads up to 20MB:

```bash
cat <<'EOF' > upload-ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: upload-demo
  annotations:
    nginx.ingress.kubernetes.io/proxy-body-size: "20m"
spec:
  ingressClassName: nginx
  rules:
  - host: upload.example.com
    http:
      paths:
      - backend:
          service:
            name: upload-svc
            port:
              number: 8080
        path: /
        pathType: Prefix
EOF
```

## Convert

```bash
ingress2gateway print --providers=ingress-nginx --emitter=kgateway \
  --input-file upload-ingress.yaml > upload-kgateway.yaml
```

The tool prints these warnings:

* The tool does not translate HTTPS for the `upload.example.com` host. By default, Ingress NGINX serves HTTPS for every host with a self-signed certificate. The generated Gateway has only an HTTP listener. To serve HTTPS, add an HTTPS listener to the Gateway. For more information, see [HTTPS listener]({{< link-hextra path="/setup/listeners/https/" >}}).
* `Failed to apply ... "nginx.ingress.kubernetes.io/proxy-body-size" ... Most Gateway API implementations have reasonable body size and buffering defaults`. Despite this warning, the output has a TrafficPolicy with the body size limit.

## After: TrafficPolicy with Buffer

```bash
cat upload-kgateway.yaml
```

The output has a Gateway, an HTTPRoute, and a `TrafficPolicy` that enforces the body size limit. The TrafficPolicy has the same name as the HTTPRoute that it targets. `buffer.maxRequestSize` accepts a Kubernetes [Quantity](https://kubernetes.io/docs/reference/kubernetes-api/definitions/quantity-resource/) string.

> [!NOTE]
> NGINX's `m` suffix uses binary multipliers (1024 × 1024), so `proxy-body-size: 20m` is identical to the Quantity `20Mi`. If you copied a value with a decimal suffix (`20M`), keep in mind it is ~5% smaller (20 × 10^6 bytes).

```yaml
apiVersion: gateway.networking.k8s.io/v1
kind: Gateway
metadata:
  name: nginx
spec:
  gatewayClassName: kgateway
  listeners:
  - hostname: upload.example.com
    name: upload-example-com-http
    port: 80
    protocol: HTTP
---
apiVersion: gateway.networking.k8s.io/v1
kind: HTTPRoute
metadata:
  name: upload-demo-upload-example-com
spec:
  hostnames:
  - upload.example.com
  parentRefs:
  - name: nginx
  rules:
  - backendRefs:
    - name: upload-svc
      port: 8080
    matches:
    - path:
        type: PathPrefix
        value: /
    name: rule-0
---
apiVersion: gateway.kgateway.dev/v1alpha1
kind: TrafficPolicy
metadata:
  name: upload-demo-upload-example-com
spec:
  buffer:
    maxRequestSize: 20Mi
  targetRefs:
  - group: gateway.networking.k8s.io
    kind: HTTPRoute
    name: upload-demo-upload-example-com
```

## Apply and verify

```bash
kubectl apply -f upload-kgateway.yaml
kubectl get trafficpolicies
```
