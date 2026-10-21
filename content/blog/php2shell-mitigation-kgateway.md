---
title: "PHP2Shell: Buying time at the gateway with kgateway"
toc: false
publishDate: 2026-10-21T14:15:00-00:00
author: Duncan Doyle
excludeSearch: true
---

> [!NOTE]
> This post is based on PHP's official advisories of 21 October 2026.

On 20 October the PHP security team [announced](https://www.php.net/) an out-of-band security release for two critical vulnerabilities, both rated CVSS v4.0 9.2. Before that release shipped, details leaked, and a proof-of-concept tool started circulating under the name "PHP2Shell". On 21 October PHP released 8.5.12, 8.4.27, 8.3.36 and 8.2.35, which fix both issues: [CVE-2026-109618](https://github.com/php/php-src/security/advisories/GHSA-w8hw-w9fx-j79w) and [CVE-2026-109619](https://github.com/php/php-src/security/advisories/GHSA-6wmf-4rv5-p3rp). Both allow unauthenticated remote code execution.

Let me be clear up front: the fix is to patch PHP. Nothing in this post replaces that, and PHP's own advisories say the same. But there is always a window between "the patch is out" and "every PHP pod in my fleet runs the patched version", and for a lot of teams that window is measured in days, not minutes. If your PHP applications sit behind kgateway, you can use the gateway to reduce your exposure during that window. In this post I'll share some example policies that you can adapt to your own setup.

The policies below are example ideas, not a complete or guaranteed mitigation. They're based on what PHP has published so far and on our own tests, and attackers may find variants that slip past them. Test them in your own environment before you rely on them.

## What the advisories say

In short: [CVE-2026-109618](https://github.com/php/php-src/security/advisories/GHSA-w8hw-w9fx-j79w) corrupts request state when PHP runs out of memory, and [CVE-2026-109619](https://github.com/php/php-src/security/advisories/GHSA-6wmf-4rv5-p3rp) lets a later request reuse state left behind by a failed one. What matters for this post is how an attacker gets there without help from your application: crafted multipart request bodies that exhaust PHP's memory while it parses them, and session upload progress, which PHP runs on multipart uploads. With Apache mod_php, that all happens before any application code runs.

PHP considers the risk highest for mod_php, but PHP-FPM, php-cgi, FrankenPHP and LiteSpeed are affected too. The fixed versions are 8.5.12, 8.4.27, 8.3.36 and 8.2.35. For older branches, check with your distribution or LTS vendor. The advisories linked above have the full technical details.

## Why the gateway is a good place for this

First of all, kgateway's data plane is Envoy, not PHP, so the gateway itself isn't affected. Second, and more importantly, the advisories ask for exactly the kind of controls a gateway is built for. CVE-2026-109618 recommends to *"block such requests at the frontend before they reach PHP"* if your application doesn't use multipart form data, and to enforce request size limits at the frontend, including for requests without a usable `Content-Length`.

Both controls run in front of PHP. That matters, because in the mod_php case the attack fires before your application code runs, so your framework's authentication, your CMS security plugin and your maintenance page never get a say. And with kgateway these controls are Kubernetes resources you can apply, review and roll back through your normal GitOps flow.

## Block multipart requests at the gateway

The `TrafficPolicy` below uses kgateway's CEL-based RBAC to deny every multipart request that passes through the Gateway:

```yaml
apiVersion: gateway.kgateway.dev/v1alpha1
kind: TrafficPolicy
metadata:
  name: php2shell-block-multipart
  namespace: my-gateway-ns   # the namespace of your Gateway
spec:
  targetRefs:
    - group: gateway.networking.k8s.io
      kind: Gateway
      name: my-gateway
  rbac:
    action: Deny
    policy:
      matchExpressions:
        # Matches "multipart" anywhere in the header, case-insensitive, for every HTTP method.
        - "'content-type' in request.headers && request.headers['content-type'].matches('(?i)multipart')"
```

A few details in that expression are deliberate. PHP lowercases the content type and cuts it off at the first `;` or `,` before deciding how to parse the body, so a rule that only matches `multipart/form-data;` in exactly that casing can be bypassed with `MULTIPART/FORM-DATA,boundary=...`. Matching case-insensitively, anywhere in the value, avoids that. The rule also ignores the HTTP method, because since PHP 8.4 `request_parse_body()` can parse multipart bodies on `PUT` and `PATCH` as well. Requests that match get a `403` from Envoy and never reach your PHP backend. The match is intentionally broad: it also blocks other multipart types such as `multipart/mixed`, which I think is the right trade-off for a temporary stopgap.

Apply it, and verify:

```bash
kubectl apply -f php2shell-block-multipart.yaml

# Regular requests still pass
curl -i http://$GATEWAY/ -d 'a=b'

# Multipart requests are now rejected by the gateway: 403, "RBAC: access denied"
curl -i http://$GATEWAY/ -F 'a=b'
```

I tested this on kgateway v2.4.7 over HTTP/1.1 and HTTP/2, including uppercase and comma-separated content types, `PUT` and `PATCH`, and requests with duplicate `Content-Type` headers. All multipart variants were blocked, and regular form posts, JSON and `GET` requests passed through untouched.

## Keep uploads working where you need them

I'll be honest: this is a blunt instrument. It breaks every file upload, and any HTML form that posts as multipart. For a lot of PHP applications (think WordPress or Magento admin screens) that's a real problem.

If that's you, change the `targetRefs` from the Gateway to the HTTPRoutes that serve your PHP application, and leave out the routes that really need uploads. For those remaining routes, cap the size of multipart requests at the gateway, as the advisory recommends. Give multipart requests their own rule in your existing HTTPRoute, so you can attach the size limit to just that rule:

```yaml
apiVersion: gateway.networking.k8s.io/v1
kind: HTTPRoute
metadata:
  name: my-upload-route
  namespace: my-php-app
spec:
  parentRefs:
    - name: my-gateway
      namespace: my-gateway-ns
  rules:
    # Multipart requests get their own rule, so only they are buffered and capped.
    - name: multipart
      matches:
        - path: {type: PathPrefix, value: /upload}
          headers:
            - name: Content-Type
              type: RegularExpression
              value: "(?i).*multipart.*"
      backendRefs:
        - name: my-php-app
          port: 80
    # Everything else on this path streams through to PHP as before.
    - name: default
      matches:
        - path: {type: PathPrefix, value: /upload}
      backendRefs:
        - name: my-php-app
          port: 80
---
apiVersion: gateway.kgateway.dev/v1alpha1
kind: TrafficPolicy
metadata:
  name: php2shell-limit-multipart-size
  namespace: my-php-app
spec:
  targetRefs:
    - group: gateway.networking.k8s.io
      kind: HTTPRoute
      name: my-upload-route
      sectionName: multipart   # only the multipart rule
  buffer:
    # Envoy buffers the body and returns 413 once it exceeds this size,
    # whether or not the client sent a Content-Length.
    maxRequestSize: 1Mi
```

In my tests a 512Ki upload went through, and a 2Mi upload got a `413` from the gateway. That held with and without a `Content-Length`, over HTTP/2, and for the same casing, comma and duplicate-header variants as before. JSON and form posts on the same path weren't buffered and went straight to the backend. Pick the smallest limit your uploads actually need, and keep it at or below PHP's `post_max_size`. The advisory suggests 32M for applications that accept uploads. Keep in mind that Envoy holds each multipart body in memory up to this limit, so don't set it higher than you have to.

A size cap reduces the risk of the out-of-memory attack, but it doesn't remove it, so also put authentication in front of these routes *at the gateway*. kgateway supports [JWT](https://kgateway.dev/docs/envoy/latest/security/jwt/), [OAuth2/OIDC](https://kgateway.dev/docs/envoy/latest/security/oauth/) and [API keys](https://kgateway.dev/docs/envoy/latest/security/extauth/apikey/). For internal-only applications, an [IP allowlist](https://kgateway.dev/docs/envoy/latest/security/acl/) does the job as well. It shrinks the set of people who can try from "the internet" to "people who can log in".

## Don't forget the side door

A gateway policy only protects traffic that goes through the gateway. If your PHP pods are also reachable through a NodePort, a second ingress controller, or directly from other workloads in the cluster, attackers can simply go around it. A `NetworkPolicy` (which needs a CNI that enforces network policies) that only admits traffic from your kgateway proxy pods closes that gap:

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: php-only-from-gateway
  namespace: my-php-app
spec:
  podSelector:
    matchLabels:
      app: my-php-app
  policyTypes:
    - Ingress
  ingress:
    - from:
        # The proxy pods run in the Gateway's namespace (not the kgateway-system control plane
        # namespace) and carry the name of the Gateway they serve as a label.
        - namespaceSelector:
            matchLabels:
              kubernetes.io/metadata.name: my-gateway-ns
          podSelector:
            matchLabels:
              gateway.networking.k8s.io/gateway-name: my-gateway
```

## What the gateway can't do

To set expectations correctly: these policies target the attack paths that the advisories describe as working regardless of your application, but they may not catch every variant, and they don't cover everything. Envoy doesn't parse multipart bodies, so it can't count the parts, the headers inside each part, or the nesting depth of field names. Set `max_input_vars` and `max_input_nesting_level` in PHP for that. Your application can also run out of memory on its own, for example on a large import. CVE-2026-109619 can also be triggered through fatal errors in your own application code, or through per-request INI settings on the server, and no gateway policy sees those. For PHP-side settings that reduce exposure until you patch, such as `session.upload_progress.enabled=0`, `memory_limit=-1` and, on PHP 8.5, `fatal_error_backtraces=0`, follow the mitigation sections of the [two](https://github.com/php/php-src/security/advisories/GHSA-w8hw-w9fx-j79w) [advisories](https://github.com/php/php-src/security/advisories/GHSA-6wmf-4rv5-p3rp). And again, everything here only helps for traffic that actually flows through kgateway.

## Wrapping up

So, to summarize: patch PHP first, to 8.5.12, 8.4.27, 8.3.36 or 8.2.35, or a backport from your vendor. Until every PHP workload is patched, block multipart requests at the gateway. On the routes that need uploads, cap the size of multipart requests and put gateway-level authentication in front of them. Then make sure the gateway is the only way in. Once you're fully patched, remove the multipart block. The size limits are worth keeping, since the advisory recommends them even after patching.

If you have questions, or you find a variant that slips past the policy, come and find us in the [kgateway Slack](https://kgateway.dev/slack/). We'd love to hear from you.
