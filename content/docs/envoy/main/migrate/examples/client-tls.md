---
title: "Client TLS (mTLS)"
description: Convert NGINX client certificate verification to Gateway API frontend TLS validation (mTLS).
weight: 40
---

Mutual TLS (mTLS) allows the gateway to verify the identity of the client via a certificate. NGINX uses annotations like `auth-tls-verify-client`, whereas Gateway API handles this through the `spec.tls.frontend` field on the Gateway. The validation settings apply to every HTTPS listener on the Gateway. For more options, such as different settings per port, see [mTLS listener]({{< link-hextra path="/setup/listeners/mtls/" >}}).

## Before: Ingress with Client Verification

An NGINX Ingress requiring a client certificate verified against a specific CA:

```bash
cat <<'EOF' > mtls-ingress.yaml
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
        pathType: Prefix
EOF
```

## Convert

```bash
ingress2gateway print --providers=ingress-nginx --emitter=kgateway \
  --input-file mtls-ingress.yaml > mtls-kgateway.yaml
```

The tool prints these warnings:

* The tool does not translate HTTPS for the `secure.example.com` host. By default, Ingress NGINX serves HTTPS for every host with a self-signed certificate. The generated Gateway has only an HTTP listener.
* `Unsupported annotation` for `auth-tls-verify-client`, `auth-tls-secret`, and `auth-tls-verify-depth`. The tool does not translate client certificate validation. You add it to the Gateway yourself in the next section.

## After: Gateway with an HTTP listener

```bash
cat mtls-kgateway.yaml
```

The output has a Gateway with one HTTP listener and an HTTPRoute. The output has no TLS settings.

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
  name: mtls-demo-secure-example-com
spec:
  hostnames:
  - secure.example.com
  parentRefs:
  - name: nginx
  rules:
  - backendRefs:
    - name: secret-svc
      port: 8443
    matches:
    - path:
        type: PathPrefix
        value: /
    name: rule-0
```

To verify client certificates, write a new version of the `nginx` Gateway to a separate file. This version keeps the HTTP listener from the output and adds the following settings:

* An HTTPS listener for `secure.example.com` that terminates TLS with the server certificate in the `server-cert` Secret. Create this TLS Secret for your host before you apply the Gateway, for example with `kubectl create secret tls server-cert --cert=<server-cert-file> --key=<server-key-file>`.
* The `spec.tls.frontend.default.validation` field, which checks client certificates against the CA certificate in the `client-ca` Secret. This Secret is the same Secret that the `auth-tls-secret` annotation refers to. kgateway reads the CA certificate from the `ca.crt` key, the same key that Ingress NGINX uses.
* The `AllowValidOnly` mode, which matches `auth-tls-verify-client: "on"`. The gateway accepts a connection only if the client presents a valid certificate.

The `auth-tls-verify-depth` annotation has no equivalent field in the Gateway.

```bash
cat <<'EOF' > mtls-gateway.yaml
apiVersion: gateway.networking.k8s.io/v1
kind: Gateway
metadata:
  name: nginx
spec:
  gatewayClassName: kgateway
  tls:
    frontend:
      default:
        validation:
          mode: AllowValidOnly
          caCertificateRefs:
          - group: ""
            kind: Secret
            name: client-ca
  listeners:
  - hostname: secure.example.com
    name: secure-example-com-http
    port: 80
    protocol: HTTP
  - hostname: secure.example.com
    name: secure-example-com-https
    port: 443
    protocol: HTTPS
    tls:
      mode: Terminate
      certificateRefs:
      - name: server-cert
EOF
```

## Apply and verify

Apply the converted resources, and then apply the Gateway with client certificate validation. The second file replaces the Gateway from the first file. The HTTPRoute attaches to both listeners.

```bash
kubectl apply -f mtls-kgateway.yaml
kubectl apply -f mtls-gateway.yaml
kubectl get gateways
```
