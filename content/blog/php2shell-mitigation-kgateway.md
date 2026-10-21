---
title: "PHP2Shell: Buying time at the gateway with kgateway"
toc: false
publishDate: 2026-10-21T00:00:00-00:00
author: Duncan Doyle
excludeSearch: true
---

> [!NOTE]
> **Last updated: 21 October 2026, 14:30 UTC.** PHP has published its official advisories and fixed releases, and this post now reflects them. An earlier version was written before the advisory, based on details that surfaced ahead of the coordinated disclosure.

On 20 October the PHP security team [announced](https://www.php.net/) an out-of-band security release for two critical vulnerabilities, both rated CVSS v4.0 9.2. Before that release shipped, details leaked, and a proof-of-concept tool started circulating under the name "PHP2Shell". On 21 October PHP released 8.5.12, 8.4.27, 8.3.36 and 8.2.35, which fix both issues: [CVE-2026-109618](https://github.com/php/php-src/security/advisories/GHSA-w8hw-w9fx-j79w) and [CVE-2026-109619](https://github.com/php/php-src/security/advisories/GHSA-6wmf-4rv5-p3rp). Both allow unauthenticated remote code execution.

Let me be clear up front: the fix is to patch PHP. Nothing in this post replaces that, and PHP's own advisories say the same. But there is always a window between "the patch is out" and "every PHP pod in my fleet runs the patched version", and for a lot of teams that window is measured in days, not minutes. If your PHP applications sit behind kgateway, you can use the gateway to cut off the attack paths PHP has documented during that window. In this post I'll show you how.

## What the advisories say

**CVE-2026-109618, RCE via out-of-memory corruption.** When PHP runs out of memory, it aborts the request with a `longjmp()`. If that happens while internal request data is only partially initialized, the request shutdown code later treats the invalid data as valid. The advisory lists several ways to drive a request into that state while it stays within PHP's apparent limits, and all of them are multipart tricks: a multipart body without a usable `Content-Length`, a multipart part with an unlimited number of headers, and empty file controls with nested field names. With Apache mod_php this happens entirely while PHP parses the request body, before any application code runs. PHP-FPM is susceptible through other paths, though no complete FPM exploit has been demonstrated.

**CVE-2026-109619, RCE via stale global state.** A fatal error, including running out of memory or hitting the execution time limit, can leave state behind that points to freed memory. A later request handled by the same worker can then use that state before PHP initializes it. One of the two confirmed ways to reach the stale state is session upload progress, which PHP triggers on multipart uploads. The other is a diagnostic raised by per-request INI configuration, which is a server-side setting and not something a request can control.

The fixed versions are 8.5.12, 8.4.27, 8.3.36 and 8.2.35. PHP 8.1 and older no longer get releases from the PHP project, but PHP has published source backports for 7.4, 8.0 and 8.1, and your distribution or LTS vendor may ship fixed packages. PHP considers the risk highest for mod_php, and also lists PHP-FPM, php-cgi, FrankenPHP and LiteSpeed as at risk.

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

If that's you, change the `targetRefs` from the Gateway to the HTTPRoutes that serve your PHP application, and leave out the routes that really need uploads. For those remaining routes, cap the request size at the gateway, as the advisory recommends:

```yaml
apiVersion: gateway.kgateway.dev/v1alpha1
kind: TrafficPolicy
metadata:
  name: php2shell-limit-upload-size
  namespace: my-php-app
spec:
  targetRefs:
    - group: gateway.networking.k8s.io
      kind: HTTPRoute
      name: my-upload-route
  buffer:
    # Envoy buffers the body and returns 413 once it exceeds this size,
    # whether or not the client sent a Content-Length.
    maxRequestSize: 1Mi
```

In my tests a 512Ki upload went through and a 2Mi upload got a `413`, both with a `Content-Length` and as a chunked request without one. Pick the smallest limit your uploads actually need, and keep it at or below PHP's `post_max_size`. The advisory suggests 32M for applications that accept uploads. Keep in mind that Envoy holds each request body in memory up to this limit, so don't set it higher than you have to.

A size cap makes the out-of-memory attack much harder, but it doesn't remove it, so also put authentication in front of these routes *at the gateway*. kgateway supports [JWT](https://kgateway.dev/docs/envoy/latest/security/jwt/), [OAuth2/OIDC](https://kgateway.dev/docs/envoy/latest/security/oauth/) and [API keys](https://kgateway.dev/docs/envoy/latest/security/extauth/apikey/). For internal-only applications, an [IP allowlist](https://kgateway.dev/docs/envoy/latest/security/acl/) does the job as well. It shrinks the set of people who can try from "the internet" to "people who can log in".

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

To set expectations correctly: these policies cut off the attack paths that the advisories describe as working regardless of your application, but they don't cover everything. Envoy doesn't parse multipart bodies, so it can't count the parts, the headers inside each part, or the nesting depth of field names. Set `max_input_vars` and `max_input_nesting_level` in PHP for that. Your application can also run out of memory on its own, for example on a large import. CVE-2026-109619 can also be triggered through fatal errors in your own application code, or through per-request INI settings on the server, and no gateway policy sees those. For PHP-side settings that reduce exposure until you patch, such as `session.upload_progress.enabled=0`, `memory_limit=-1` and, on PHP 8.5, `fatal_error_backtraces=0`, follow the mitigation sections of the [two](https://github.com/php/php-src/security/advisories/GHSA-w8hw-w9fx-j79w) [advisories](https://github.com/php/php-src/security/advisories/GHSA-6wmf-4rv5-p3rp). And again, everything here only helps for traffic that actually flows through kgateway.

## Wrapping up

So, to summarize: patch PHP first, to 8.5.12, 8.4.27, 8.3.36 or 8.2.35, or a backport from your vendor. Until every PHP workload is patched, block multipart requests at the gateway. On the routes that need uploads, cap the request size and put gateway-level authentication in front of them. Then make sure the gateway is the only way in. Once you're fully patched, remove the multipart block. The size limits are worth keeping, since the advisory recommends them even after patching.

If you have questions, or you find a variant that slips past the policy, come and find us in the [kgateway Slack](https://kgateway.dev/slack/). We'd love to hear from you.
