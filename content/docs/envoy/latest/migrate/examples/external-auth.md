---
title: "External Auth"
description: Convert Ingress NGINX auth-url annotations to a kgateway external auth GatewayExtension.
weight: 60
---

If you're using NGINX's `auth-url` to call an external authentication service, this becomes a kgateway `GatewayExtension` with external auth configuration.

## Before: Ingress with external auth

```bash
cat <<'EOF' > external-auth-ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: ext-auth-demo
  annotations:
    nginx.ingress.kubernetes.io/auth-url: "http://auth-service.auth.svc.cluster.local/verify"
    nginx.ingress.kubernetes.io/auth-response-headers: "X-User-ID, X-User-Email"
spec:
  ingressClassName: nginx
  rules:
  - host: app.example.com
    http:
      paths:
      - backend:
          service:
            name: protected-app
            port:
              number: 8080
        path: /
        pathType: Prefix
EOF
```

## Convert

```bash
ingress2gateway print --providers=ingress-nginx --emitter=kgateway \
  --input-file external-auth-ingress.yaml > external-auth-kgateway.yaml
```

The tool prints these warnings:

* The tool does not translate HTTPS for the `app.example.com` host. By default, Ingress NGINX serves HTTPS for every host with a self-signed certificate. The generated Gateway has only an HTTP listener. To serve HTTPS, add an HTTPS listener to the Gateway. For more information, see [HTTPS listener]({{< link-hextra path="/setup/listeners/https/" >}}).
* `Unsupported annotation` for `auth-url` and `auth-response-headers`. Despite these warnings, the output has a GatewayExtension and a TrafficPolicy for both annotations.

The TrafficPolicy in the output has an empty namespace in its reference to the GatewayExtension:

```yaml
extAuth:
  extensionRef:
    name: ext-auth-demo-extauth
    namespace: ""
```

This empty value is an issue in `ingress2gateway` v0.5.0. The TrafficPolicy CRD does not allow an empty namespace, so `kubectl apply` rejects the TrafficPolicy. Remove the line before you apply the file. Without a namespace, kgateway looks for the GatewayExtension in the namespace of the TrafficPolicy. The following command keeps a copy of the original file in `external-auth-kgateway.yaml.bak`.

```bash
sed -i.bak '/namespace: ""/d' external-auth-kgateway.yaml
```

## After: GatewayExtension and TrafficPolicy

```bash
cat external-auth-kgateway.yaml
```

After you remove the empty namespace, the file has a Gateway and an HTTPRoute. It also has a `GatewayExtension` that configures the external auth service, and a `TrafficPolicy` that applies it to the HTTPRoute.

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
  name: ext-auth-demo-app-example-com
spec:
  hostnames:
  - app.example.com
  parentRefs:
  - name: nginx
  rules:
  - backendRefs:
    - name: protected-app
      port: 8080
    matches:
    - path:
        type: PathPrefix
        value: /
    name: rule-0
---
apiVersion: gateway.kgateway.dev/v1alpha1
kind: GatewayExtension
metadata:
  name: ext-auth-demo-extauth
spec:
  extAuth:
    httpService:
      authorizationResponse:
        headersToBackend:
        - X-User-ID
        - X-User-Email
      backendRef:
        name: auth-service
        namespace: auth
        port: 80
      pathPrefix: /verify
---
apiVersion: gateway.kgateway.dev/v1alpha1
kind: TrafficPolicy
metadata:
  name: ext-auth-demo
spec:
  extAuth:
    extensionRef:
      name: ext-auth-demo-extauth
  targetRefs:
  - group: gateway.networking.k8s.io
    kind: HTTPRoute
    name: ext-auth-demo-app-example-com
```

## Apply

```bash
kubectl apply -f external-auth-kgateway.yaml
```
