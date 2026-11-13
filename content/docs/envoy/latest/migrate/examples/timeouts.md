---
title: "Timeouts"
description: Convert NGINX proxy timeout annotations to an HTTPRoute request timeout, and add the connect timeout in a kgateway BackendConfigPolicy.
weight: 36
---

Connection and request timeouts are critical for stability. NGINX uses proxy-level directives like `proxy_read_timeout` and `proxy_connect_timeout`. The conversion tool turns these timeouts into one request timeout on the HTTPRoute rule. In kgateway, the upstream connection timeout belongs to a `BackendConfigPolicy`, which you add by hand.

## Before: Ingress with Timeouts

An NGINX Ingress configured with custom read and connect timeouts (values in seconds):

```bash
cat <<'EOF' > timeouts-ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: timeouts-demo
  annotations:
    nginx.ingress.kubernetes.io/proxy-connect-timeout: "15"
    nginx.ingress.kubernetes.io/proxy-read-timeout: "60"
spec:
  ingressClassName: nginx
  rules:
  - host: timeouts.example.com
    http:
      paths:
      - backend:
          service:
            name: slow-svc
            port:
              number: 80
        path: /
        pathType: Prefix
EOF
```

## Convert

```bash
ingress2gateway print --providers=ingress-nginx --emitter=kgateway \
  --input-file timeouts-ingress.yaml > timeouts-kgateway.yaml
```

The tool prints these warnings:

* The tool does not translate HTTPS for the `timeouts.example.com` host. By default, Ingress NGINX serves HTTPS for every host with a self-signed certificate. The generated Gateway has only an HTTP listener. To serve HTTPS, add an HTTPS listener to the Gateway. For more information, see [HTTPS listener]({{< link-hextra path="/setup/listeners/https/" >}}).
* `ingress-nginx only supports TCP-level timeouts; i2gw has made a best-effort translation to Gateway API timeouts.request`. The NGINX timeouts apply to single network operations, such as one read. A Gateway API request timeout applies to the whole request.

## After: HTTPRoute with a request timeout

```bash
cat timeouts-kgateway.yaml
```

The output has a Gateway and an HTTPRoute. The output has no TrafficPolicy or BackendConfigPolicy. Instead, the HTTPRoute rule has a `timeouts.request` value of `10m0s`. The tool takes the largest NGINX timeout, 60 seconds, and multiplies it by 10. Check whether 10 minutes fits your app, and change the value if it does not.

```yaml
apiVersion: gateway.networking.k8s.io/v1
kind: Gateway
metadata:
  name: nginx
spec:
  gatewayClassName: kgateway
  listeners:
  - hostname: timeouts.example.com
    name: timeouts-example-com-http
    port: 80
    protocol: HTTP
---
apiVersion: gateway.networking.k8s.io/v1
kind: HTTPRoute
metadata:
  name: timeouts-demo-timeouts-example-com
spec:
  hostnames:
  - timeouts.example.com
  parentRefs:
  - name: nginx
  rules:
  - backendRefs:
    - name: slow-svc
      port: 80
    matches:
    - path:
        type: PathPrefix
        value: /
    name: rule-0
    timeouts:
      request: 10m0s
```

The output does not keep the 15-second connect timeout from the `proxy-connect-timeout` annotation. To keep it, you add a `BackendConfigPolicy` with `connectTimeout` that targets the `slow-svc` Service.

## Apply and verify

Apply the converted resources.

```bash
kubectl apply -f timeouts-kgateway.yaml
```

Create a BackendConfigPolicy that sets the connect timeout for the `slow-svc` Service. The policy takes effect only when the `slow-svc` Service exists in the same namespace.

```yaml
kubectl apply -f- <<EOF
apiVersion: gateway.kgateway.dev/v1alpha1
kind: BackendConfigPolicy
metadata:
  name: slow-svc-backend-config
spec:
  targetRefs:
  - group: ""
    kind: Service
    name: slow-svc
  connectTimeout: 15s
EOF
```

Check the request timeout on the HTTPRoute and the BackendConfigPolicy.

```bash
kubectl get httproute timeouts-demo-timeouts-example-com -o jsonpath='{.spec.rules[0].timeouts}'
kubectl get backendconfigpolicies
```
