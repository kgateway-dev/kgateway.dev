---
title: "PHP2Shell: Buying time at the gateway with kgateway"
toc: false
publishDate: 2026-10-21T00:00:00-00:00
author: Duncan Doyle
excludeSearch: true
---

If you run PHP anywhere, you've probably had a busy couple of days. On 20 October the PHP security team [announced](https://www.php.net/) an out-of-band security release for two critical vulnerabilities, both rated CVSS v4.0 9.2. Before that release shipped, details leaked, a proof-of-concept tool started circulating under the name "PHP2Shell", and the two issues are now tracked as CVE-2026-109618 and CVE-2026-109619. [Cloudflare reported](https://sansec.io/research/php2shell) early attack attempts hours before the patch was out.

Let me be clear up front: the fix is to patch PHP. Nothing in this post replaces that. But there is always a window between "the patch is out" and "every PHP pod in my fleet runs the patched version", and for a lot of teams that window is measured in days, not minutes. If your PHP applications sit behind kgateway, you can use the gateway to close the most likely attack path during that window. In this post I'll show you how.

## What we know, and what we don't

At the time of writing, PHP hasn't published the root cause. What follows comes from the leak and from third-party analysis by [Sansec](https://sansec.io/research/php2shell), [Tenable](https://www.tenable.com/blog/php2shell-cve-2026-109618-cve-2026-109619-frequently-asked-questions-about-critical-php-remote), [Phoenix Security](https://phoenix.security/php-core-rce-cve-2026-109618-109619-critical-remote-code-execution/) and others, so treat it as a working hypothesis.

The suspected vector is a crafted `multipart/form-data` request body. PHP parses multipart bodies itself, during request startup, before a single line of your application code runs. One of the bugs reportedly sits in the session upload progress handling (`session.upload_progress`), the other in the multipart parser itself. That's why the popular php.ini tweak, `session.upload_progress.enabled = Off`, is [disputed](https://www.tenable.com/blog/php2shell-cve-2026-109618-cve-2026-109619-frequently-asked-questions-about-critical-php-remote) as a mitigation: it may close one path and leave the other open.

The important consequence is this: because the attack fires before your code runs, nothing inside your application can stop it. Your framework's authentication, your CMS security plugin, your maintenance mode page: PHP has already parsed the request by the time any of those get a say. The only controls that help are the ones that sit *in front of* PHP. And that's exactly where your gateway is.

## Why the gateway is a good place for this

First of all, kgateway's data plane is Envoy, not PHP, so the gateway itself isn't affected. Second, for the mitigation below the gateway doesn't even need to look at the request body. It decides based on the `Content-Type` header alone, which is cheap, adds no buffering, and doesn't depend on Envoy parsing multipart content the same way PHP does.

This is the same idea as the Apache, nginx and Cloudflare rules that are circulating right now ([example](https://github.com/PasqualePillitteri/php2shell-hardening)). The difference is that with kgateway it's a Kubernetes resource you can apply, review and roll back through your normal GitOps flow.

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

If that's you, change the `targetRefs` from the Gateway to the HTTPRoutes that serve your PHP application, and leave out the routes that really need uploads. For those remaining routes, put authentication in front of them *at the gateway*. Remember, the bug fires before your application code, so your application's login doesn't help, but a gateway-level check does. kgateway supports [JWT](https://kgateway.dev/docs/envoy/latest/security/jwt/), [OAuth2/OIDC](https://kgateway.dev/docs/envoy/latest/security/oauth/) and [API keys](https://kgateway.dev/docs/envoy/latest/security/extauth/apikey/). For internal-only applications, an [IP allowlist](https://kgateway.dev/docs/envoy/latest/security/acl/) does the job as well. It doesn't eliminate the risk, but it shrinks the set of people who can try from "the internet" to "people who can log in".

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

## What this doesn't do

To set expectations correctly: this mitigation is built on an *unconfirmed* attack vector. If PHP's official advisory places one of the two bugs outside multipart parsing, this policy won't cover it, so revisit it as soon as the details are public. It's a header-based control, not a fix for PHP. And it only helps for traffic that actually flows through kgateway.

## Wrapping up

So, to summarize: patch PHP first, using the fixed versions from the [official PHP release](https://www.php.net/) or your distribution's backport. Until every PHP workload is patched, block multipart requests at the gateway, scope that block to your PHP routes if you need uploads, put gateway-level authentication on whatever you have to leave open, and make sure the gateway is the only way in. Once you're fully patched, remove the policy, and your uploads are back.

If you have questions, or you find a variant that slips past the policy, come and find us in the [kgateway Slack](https://kgateway.dev/slack/). We'd love to hear from you.
