---
title: "Basic Auth"
description: Convert NGINX basic authentication annotations to a kgateway TrafficPolicy with basicAuth.
weight: 31
---

This example demonstrates how to migrate NGINX-style basic authentication to kgateway. In NGINX, you set `auth-type: basic` and a reference to a secret. In kgateway, you use a `TrafficPolicy` with the `basicAuth` configuration.

## Before: Ingress with Basic Auth

Here is a standard NGINX Ingress using basic authentication:

```bash
cat <<'EOF' > basic-auth-ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: basic-auth-demo
  annotations:
    nginx.ingress.kubernetes.io/auth-type: basic
    nginx.ingress.kubernetes.io/auth-secret: my-htpasswd-secret
    nginx.ingress.kubernetes.io/auth-realm: "Authentication Required"
spec:
  ingressClassName: nginx
  rules:
  - host: auth.example.com
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

Run the conversion tool to generate the Gateway API resources:

```bash
ingress2gateway print --providers=ingress-nginx --emitter=kgateway \
  --input-file basic-auth-ingress.yaml > basic-auth-kgateway.yaml
```

The tool prints these warnings:

* The tool does not translate HTTPS for the `auth.example.com` host. By default, Ingress NGINX serves HTTPS for every host with a self-signed certificate. The generated Gateway has only an HTTP listener. To serve HTTPS, add an HTTPS listener to the Gateway. For more information, see [HTTPS listener]({{< link-hextra path="/setup/listeners/https/" >}}).
* `Unsupported annotation` for `auth-type`, `auth-secret`, and `auth-realm`. Despite these warnings, the output has a TrafficPolicy for `auth-type` and `auth-secret`. The TrafficPolicy has no field for the `auth-realm` value, so the tool drops it.

## After: TrafficPolicy with Basic Auth

```bash
cat basic-auth-kgateway.yaml
```

The output has a Gateway, an HTTPRoute, and a TrafficPolicy. The TrafficPolicy reads the htpasswd data from the `auth` key of the `my-htpasswd-secret` Secret, the same key that Ingress NGINX uses. The Secret must be in the same namespace as the TrafficPolicy. The tool does not create the Secret.

```yaml
apiVersion: gateway.networking.k8s.io/v1
kind: Gateway
metadata:
  name: nginx
spec:
  gatewayClassName: kgateway
  listeners:
  - hostname: auth.example.com
    name: auth-example-com-http
    port: 80
    protocol: HTTP
---
apiVersion: gateway.networking.k8s.io/v1
kind: HTTPRoute
metadata:
  name: basic-auth-demo-auth-example-com
spec:
  hostnames:
  - auth.example.com
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
---
apiVersion: gateway.kgateway.dev/v1alpha1
kind: TrafficPolicy
metadata:
  name: basic-auth-demo
spec:
  basicAuth:
    secretRef:
      key: auth
      name: my-htpasswd-secret
  targetRefs:
  - group: gateway.networking.k8s.io
    kind: HTTPRoute
    name: basic-auth-demo-auth-example-com
```

## Apply and verify

Apply the converted resources.

```bash
kubectl apply -f basic-auth-kgateway.yaml
```

Create the `my-htpasswd-secret` Secret with your htpasswd data under the `auth` key. You can use only `{SHA}` password hashes. If your NGINX Secret uses another hash format, such as bcrypt or MD5 (`$apr1$`), generate a new entry for each user, for example with `htpasswd -nbs user password`. The following example has one user, `user`, with the password `password`.

```yaml
kubectl apply -f- <<EOF
apiVersion: v1
kind: Secret
metadata:
  name: my-htpasswd-secret
type: Opaque
stringData:
  auth: |
    user:{SHA}W6ph5Mm5Pz8GgiULbPgzG37mj9g=
EOF
```

Check that the Secret and the TrafficPolicy exist.

```bash
kubectl get secret my-htpasswd-secret
kubectl get trafficpolicies
```
