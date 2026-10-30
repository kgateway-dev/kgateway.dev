---
title: "URL Rewriting"
description: Convert the NGINX rewrite-target annotation to a regular expression HTTPRoute match and a kgateway TrafficPolicy path rewrite.
weight: 37
---

Path rewriting is common when backends expect a different path than what is exposed publicly. NGINX uses the `rewrite-target` annotation. When the rewrite uses capture groups from a regular expression path, the conversion tool creates a kgateway `TrafficPolicy` with a `urlRewrite.pathRegex` rewrite instead of a Gateway API `URLRewrite` filter.

## Before: Ingress with Rewrite Target

In this example, requests to `/api/v1/users` are rewritten to `/users` before reaching the backend:

```bash
cat <<'EOF' > rewrite-ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: rewrite-demo
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /$2
spec:
  ingressClassName: nginx
  rules:
  - host: api.example.com
    http:
      paths:
      - path: /api/v1(/|$)(.*)
        pathType: ImplementationSpecific
        backend:
          service:
            name: backend-svc
            port:
              number: 80
EOF
```

## Convert

```bash
ingress2gateway print --providers=ingress-nginx --emitter=kgateway \
  --input-file rewrite-ingress.yaml > rewrite-kgateway.yaml
```

The tool prints these messages:

* The tool does not translate HTTPS for the `api.example.com` host. By default, Ingress NGINX serves HTTPS for every host with a self-signed certificate. The generated Gateway has only an HTTP listener. To serve HTTPS, add an HTTPS listener to the Gateway. For more information, see [HTTPS listener]({{< link-hextra path="/setup/listeners/https/" >}}).
* `Using case-insensitive regex path matches`. The tool adds `(?i)` to the start of the path pattern, so the match ignores upper and lower case, like Ingress NGINX does.
* `Path rewrites with capture group references are not supported`. Despite this warning, the output has a TrafficPolicy with the rewrite. The rewrite needs one fix, as described in the next section.

## After: Regular expression match and TrafficPolicy

```bash
cat rewrite-kgateway.yaml
```

The output has a Gateway, an HTTPRoute, and a TrafficPolicy. The HTTPRoute rule matches the path with a regular expression and has no `URLRewrite` filter. The TrafficPolicy targets only that rule, through the `sectionName: rule-0` setting, and rewrites the path.

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
  name: rewrite-demo-api-example-com
spec:
  hostnames:
  - api.example.com
  parentRefs:
  - name: nginx
  rules:
  - backendRefs:
    - name: backend-svc
      port: 80
    matches:
    - path:
        type: RegularExpression
        value: (?i)/api/v1(/|$)(.*).*
    name: rule-0
---
apiVersion: gateway.kgateway.dev/v1alpha1
kind: TrafficPolicy
metadata:
  name: rewrite-demo-api-example-com-0
spec:
  targetRefs:
  - group: gateway.networking.k8s.io
    kind: HTTPRoute
    name: rewrite-demo-api-example-com
    sectionName: rule-0
  urlRewrite:
    pathRegex:
      pattern: (?i)/api/v1(/|$)(.*).*
      substitution: /$2
```

The tool copies the NGINX value `/$2` into the `substitution` field as is. In kgateway, a `substitution` refers to a capture group with a backslash, such as `\2`, not with a dollar sign. With `/$2`, the backend gets the path `/$2` instead of `/users`. To fix the rewrite, change the substitution to `/\2`.

## Apply and verify

Apply the converted resources.

```bash
kubectl apply -f rewrite-kgateway.yaml
```

Replace the TrafficPolicy with a version that uses `/\2` as the substitution. A request to `/api/v1/users` now reaches the backend as `/users`.

```yaml
kubectl apply -f- <<'EOF'
apiVersion: gateway.kgateway.dev/v1alpha1
kind: TrafficPolicy
metadata:
  name: rewrite-demo-api-example-com-0
spec:
  targetRefs:
  - group: gateway.networking.k8s.io
    kind: HTTPRoute
    name: rewrite-demo-api-example-com
    sectionName: rule-0
  urlRewrite:
    pathRegex:
      pattern: (?i)/api/v1(/|$)(.*).*
      substitution: /\2
EOF
```

Check the HTTPRoute and the TrafficPolicy.

```bash
kubectl get httproutes
kubectl get trafficpolicy rewrite-demo-api-example-com-0 -o jsonpath='{.spec.urlRewrite.pathRegex.substitution}'
```
