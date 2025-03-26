---
title: Policies
weight: 30
prev: /docs/about/custom-resources
next: /docs/about/policies/routeoption
---

Learn more about the custom resources that you can use to apply policies in {{< reuse "docs/snippets/product-name.md" >}}. 


While the {{< reuse "docs/snippets/k8s-gateway-api-name.md" >}} allows you to do simple routing, such as to match, redirect, or rewrite requests, you might want additional capabilities in your API gateway, such direct responses or request and response transformations. Policies allow you to apply intelligent traffic management, resiliency, and security standards to an HTTPRoute or Gateway. 

## Policy CRDs

{{< reuse "docs/snippets/product-name-caps.md" >}} uses the following custom resources to attach policies to routes and gateway listeners. 

{{< cards >}}
  {{< card link="/docs/traffic-management/direct-response/" title="Direct response" subtitle="Directly respond to incoming requests with a custom HTTP response code and body." >}}
  {{< card link="/docs/about/policies/httplistenerpolicy/" title="HTTPListenerPolicy" subtitle="Apply policies to all HTTP and HTTPS listeners." >}}
  {{< card link="/docs/about/policies/routepolicy/" title="RoutePolicy" subtitle="Attach policies to all routes in an HTTPRoute resource." >}}
{{< /cards >}}



## Supported policies {#supported-policies}

Review the policies that you can configure in {{< reuse "docs/snippets/product-name.md" >}} and the level at which you can apply them.   

| Policy | Applied via |
| -- | -- | 
| [Access logging](/docs/security/access-logging) | HTTPListenerPolicy |
| [Direct response](/docs/traffic-management/direct-response/) | DirectResponse | 
| [Transformations](/docs/traffic-management/transformations) | RoutePolicy | 

<!--

## Policy inheritance rules when using route delegation

Policies that are defined in a RouteOption resource and that are applied to a parent HTTPRoute resource are automatically inherited by all the child or grandchild HTTPRoutes along the route delegation chain. The following rules apply: 

* Only policies that are specified in a RouteOption resource can be inherited by a child HTTPRoute. For inheritance to take effect, you must use the `spec.targetRefs` field in the RouteOption resource to apply the RouteOption resource to the parent HTTPRoute resource. Any child or grandchild HTTPRoute that the parent delegates traffic to inherits these policies. 
* Child RouteOption resources cannot override policies that are defined in a RouteOption resource that is applied to a parent HTTPRoute. If the child HTTPRoute sets a policy that is already defined on the parent HTTPRoute, the setting on the parent HTTPRoute takes precedence and the setting on the child is ignored. For example, if the parent HTTPRoute defines a data loss prevention policy, the child HTTPRoute cannot change these settings or disable that policy.
* Child HTTPRoutes can augment the inherited settings by defining RouteOption fields that were not already set on the parent HTTPRoute. 
* Policies are inherited along the complete delegation chain, with parent policies having a higher priority than their respective children.

For an example, see the [Policy inheritance](/docs/traffic-management/route-delegation/policy-inheritance/) guide.

--> 
