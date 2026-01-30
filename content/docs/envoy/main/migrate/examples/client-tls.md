---
title: "Client TLS (mTLS)"
weight: 40
---

Mutual TLS (mTLS) allows the gateway to verify the identity of the client via a certificate. NGINX uses annotations like `auth-tls-verify-client`, whereas Gateway API (v1.1+) handles this through `frontendValidation` on a Gateway listener.

## Before: Ingress with Client Verification

An NGINX Ingress requiring a client certificate verified against a specific CA:

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: mtls-demo
  annotations:
    nginx.ingress.kubernetes.io/auth-tls-verify-client: "on"
    nginx.ingress.kubernetes.io/auth-tls-secret: "default/client-ca"
    nginx.ingress.kubernetes.io/auth-tls-verify-depth: "2"
spec:
  ingressClassName: nginx
  rules:
  - host: secure.example.com
    http:
      paths:
      - backend:
          service:
            name: secret-svc
            port:
              number: 8443
        path: /
```

## Convert

```bash
ingress2gateway print --providers=ingress-nginx --emitter=kgateway \
  --input-file mtls-ingress.yaml > mtls-kgateway.yaml
```

## After: Gateway Listener with Frontend Validation

In Gateway API, mTLS is configured on the `Gateway` resource's listener using `frontendValidation`.

```yaml
apiVersion: gateway.networking.k8s.io/v1
kind: Gateway
metadata:
  name: gateway-mtls
spec:
  gatewayClassName: kgateway
  listeners:
  - name: https
    hostname: secure.example.com
    port: 443
    protocol: HTTPS
    tls:
      mode: Terminate
      certificateRefs:
      - name: server-cert
      frontendValidation:
        caCertificateRefs:
        - name: client-ca
          kind: Secret
```

## Apply and verify

```bash
kubectl apply -f mtls-kgateway.yaml
kubectl get gateways
```
