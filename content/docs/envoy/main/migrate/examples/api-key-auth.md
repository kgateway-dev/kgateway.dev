---
title: "API Key Authentication"
description: Convert an NGINX API key check to a kgateway TrafficPolicy with native apiKeyAuth.
weight: 33
---

In open-source NGINX, API key validation is often implemented using a `configuration-snippet` that checks for a specific header. In kgateway, you use the native `apiKeyAuth` setting of a `TrafficPolicy` instead.

## Before: Ingress with API Key Check

This is a common way to enforce API keys in NGINX Ingress:

```bash
cat <<'EOF' > api-key-ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: api-key-demo
  annotations:
    nginx.ingress.kubernetes.io/configuration-snippet: |
      if ($http_x_api_key = "") {
        return 401;
      }
spec:
  ingressClassName: nginx
  rules:
  - host: api.example.com
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

```bash
ingress2gateway print --providers=ingress-nginx --emitter=kgateway \
  --input-file api-key-ingress.yaml > api-key-kgateway.yaml
```

The tool prints these warnings:

* The tool does not translate HTTPS for the `api.example.com` host. By default, Ingress NGINX serves HTTPS for every host with a self-signed certificate. The generated Gateway has only an HTTP listener. To serve HTTPS, add an HTTPS listener to the Gateway. For more information, see [HTTPS listener]({{< link-hextra path="/setup/listeners/https/" >}}).
* `Unsupported annotation nginx.ingress.kubernetes.io/configuration-snippet`. The snippet is raw NGINX configuration, so the tool drops it. The output has no API key check.

## After: Gateway and HTTPRoute

```bash
cat api-key-kgateway.yaml
```

The output has only a Gateway and an HTTPRoute.

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
  name: api-key-demo-api-example-com
spec:
  hostnames:
  - api.example.com
  parentRefs:
  - name: nginx
  rules:
  - backendRefs:
    - name: httpbin
      port: 8000
    matches:
    - path:
        type: PathPrefix
        value: /
    name: rule-0
```

To replace the snippet, you write a TrafficPolicy with `apiKeyAuth` by hand. Instead of an `if` statement, you set where to read the key from, such as a header, and a Secret that holds the valid keys. Each entry in the Secret is one client name and its key. Unlike the NGINX snippet, which accepts any value that is not empty, the policy accepts only the keys in the Secret. By default, the policy removes the key from the request before the request reaches the backend. To keep the key in the request, set `forwardCredential: true`.

## Apply and verify

Apply the converted resources.

```bash
kubectl apply -f api-key-kgateway.yaml
```

Create the Secret with the valid keys and the TrafficPolicy that targets the `api-key-demo-api-example-com` HTTPRoute.

```yaml
kubectl apply -f- <<EOF
apiVersion: v1
kind: Secret
metadata:
  name: valid-api-keys
type: Opaque
stringData:
  client-a: "key-12345"
  client-b: "key-67890"
---
apiVersion: gateway.kgateway.dev/v1alpha1
kind: TrafficPolicy
metadata:
  name: api-key-demo
spec:
  targetRefs:
  - group: gateway.networking.k8s.io
    kind: HTTPRoute
    name: api-key-demo-api-example-com
  apiKeyAuth:
    keySources:
    - header: X-API-Key
    secretRef:
      name: valid-api-keys
EOF
```

Check that the Secret and the TrafficPolicy exist.

```bash
kubectl get secret valid-api-keys
kubectl get trafficpolicies
```
