---
title: "Backend TLS"
description: Convert Ingress NGINX backend TLS annotations to a kgateway BackendConfigPolicy.
weight: 80
---

When your backend requires TLS (re-encryption), NGINX's `proxy-ssl-*` annotations translate to a kgateway `BackendConfigPolicy` with TLS settings.

## Before: Ingress with backend TLS

The `backend-protocol: "HTTPS"` annotation tells Ingress NGINX to connect to the backend over HTTPS. Ingress NGINX applies the `proxy-ssl-*` settings only to HTTPS connections, and `ingress2gateway` creates the `BackendConfigPolicy` only when this annotation is set.

```bash
cat <<'EOF' > backend-tls-ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: backend-tls-demo
  annotations:
    nginx.ingress.kubernetes.io/backend-protocol: "HTTPS"
    nginx.ingress.kubernetes.io/proxy-ssl-secret: "default/backend-tls-secret"
    nginx.ingress.kubernetes.io/proxy-ssl-verify: "on"
    nginx.ingress.kubernetes.io/proxy-ssl-name: "internal-api.example.com"
spec:
  ingressClassName: nginx
  rules:
  - host: app.example.com
    http:
      paths:
      - backend:
          service:
            name: secure-api
            port:
              number: 443
        path: /api
        pathType: Prefix
EOF
```

## Convert

```bash
ingress2gateway print --providers=ingress-nginx --emitter=kgateway \
  --input-file backend-tls-ingress.yaml > backend-tls-kgateway.yaml
```

The tool prints these messages:

* The tool does not translate HTTPS for the `app.example.com` host. By default, Ingress NGINX serves HTTPS for every host with a self-signed certificate. The generated Gateway has only an HTTP listener. To serve HTTPS, add an HTTPS listener to the Gateway. For more information, see [HTTPS listener]({{< link-hextra path="/setup/listeners/https/" >}}).
* An `ERROR` that the Ingress `failed strict validation requirements to emit a BackendTLSPolicy`. This message is about the Gateway API `BackendTLSPolicy` resource. The output still has the kgateway `BackendConfigPolicy` with the TLS settings.

## After: BackendConfigPolicy with TLS

```bash
cat backend-tls-kgateway.yaml
```

The output has a Gateway, an HTTPRoute, and a BackendConfigPolicy that applies to the `secure-api` Service.

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
  name: backend-tls-demo-app-example-com
spec:
  hostnames:
  - app.example.com
  parentRefs:
  - name: nginx
  rules:
  - backendRefs:
    - name: secure-api
      port: 443
    matches:
    - path:
        type: PathPrefix
        value: /api
    name: rule-0
---
apiVersion: gateway.kgateway.dev/v1alpha1
kind: BackendConfigPolicy
metadata:
  name: secure-api-backend-config
spec:
  targetRefs:
  - group: ""
    kind: Service
    name: secure-api
  tls:
    secretRef:
      name: backend-tls-secret
    sni: internal-api.example.com
```

The `sni` value comes from the `proxy-ssl-name` annotation. The `secretRef` points to the Secret with the client certificate, the key, and optionally the root CA certificate to verify the backend.

The `secretRef` has no `namespace` field. The Secret must be in the same namespace as the `BackendConfigPolicy`.

## Apply

```bash
kubectl apply -f backend-tls-kgateway.yaml
```
