---
title: "OIDC Authentication"
description: Convert an NGINX oauth2-proxy setup to native kgateway OIDC with a GatewayExtension and TrafficPolicy.
weight: 34
---

Many teams use `oauth2-proxy` as a sidecar or external service to handle OIDC/OAuth2 for NGINX. kgateway provides native support for OIDC via a `GatewayExtension` and `TrafficPolicy`.

> [!NOTE]
> This is an architectural change, not a one-for-one annotation translation. The NGINX side delegates auth to an external `oauth2-proxy` deployment via `auth-url`. The kgateway side moves OIDC into the gateway itself, so you can decommission the proxy once the migration is verified. Because the `auth-url` annotation only points at an external service, `ingress2gateway` can't infer your OIDC provider settings; you author the resources below by hand.

## Before: Ingress with External Auth (OAuth2 Proxy)

Typical NGINX setup using `auth-url` to delegate to a proxy:

```bash
cat <<'EOF' > oidc-ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: oidc-demo
  annotations:
    nginx.ingress.kubernetes.io/auth-url: "https://$host/oauth2/auth"
    nginx.ingress.kubernetes.io/auth-signin: "https://$host/oauth2/start?rd=$escaped_request_uri"
spec:
  ingressClassName: nginx
  rules:
  - host: oidc.example.com
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
  --input-file oidc-ingress.yaml > oidc-kgateway.yaml
```

The tool prints these warnings:

* The tool does not translate HTTPS for the `oidc.example.com` host. By default, Ingress NGINX serves HTTPS for every host with a self-signed certificate. The generated Gateway has only an HTTP listener. To serve HTTPS, add an HTTPS listener to the Gateway. For more information, see [HTTPS listener]({{< link-hextra path="/setup/listeners/https/" >}}).
* `Unsupported annotation` for `auth-signin` and `auth-url`.

## After: Gateway and HTTPRoute

The converted file has only a Gateway named `nginx` and an HTTPRoute named `oidc-demo-oidc-example-com`. It has no auth resources.

Write the OIDC resources to a separate file. Native OIDC support is configured using a `GatewayExtension` for the provider details and a `TrafficPolicy` to protect the route. The gateway exchanges the authorization code for tokens through the `google-oauth2` Backend, which points to Google's token endpoint host. The `BackendConfigPolicy` sets up TLS to that host with the system's trusted CA certificates. Replace `my-client-id` with the client ID of your OAuth2 application.

```bash
cat <<'EOF' > oidc-auth.yaml
apiVersion: gateway.kgateway.dev/v1alpha1
kind: GatewayExtension
metadata:
  name: google-oidc
spec:
  oauth2:
    backendRef:
      group: gateway.kgateway.dev
      kind: Backend
      name: google-oauth2
    issuerURI: https://accounts.google.com
    authorizationEndpoint: https://accounts.google.com/o/oauth2/v2/auth
    tokenEndpoint: https://oauth2.googleapis.com/token
    scopes:
    - openid
    - email
    credentials:
      clientID: my-client-id
      clientSecretRef:
        name: oidc-client-secret
---
apiVersion: gateway.kgateway.dev/v1alpha1
kind: Backend
metadata:
  name: google-oauth2
spec:
  type: Static
  static:
    hosts:
    - host: oauth2.googleapis.com
      port: 443
---
apiVersion: gateway.kgateway.dev/v1alpha1
kind: BackendConfigPolicy
metadata:
  name: google-oauth2-tls
spec:
  targetRefs:
  - group: gateway.kgateway.dev
    kind: Backend
    name: google-oauth2
  tls:
    sni: oauth2.googleapis.com
    wellKnownCACertificates: System
---
apiVersion: gateway.kgateway.dev/v1alpha1
kind: TrafficPolicy
metadata:
  name: oidc-policy
spec:
  targetRefs:
  - group: gateway.networking.k8s.io
    kind: HTTPRoute
    name: oidc-demo-oidc-example-com
  oauth2:
    extensionRef:
      name: google-oidc
EOF
```

## Apply and verify

Create the `oidc-client-secret` Secret with the client secret of your OAuth2 application. kgateway reads the value from the `client-secret` key, so the key name matters. Replace `YOUR_CLIENT_SECRET` with your client secret.

```bash
kubectl create secret generic oidc-client-secret \
  --from-literal=client-secret=YOUR_CLIENT_SECRET
```

Apply the converted resources and the OIDC resources. Then, check that the GatewayExtension and the TrafficPolicy exist.

```bash
kubectl apply -f oidc-kgateway.yaml
kubectl apply -f oidc-auth.yaml
kubectl get gatewayextensions
kubectl get trafficpolicies
```
