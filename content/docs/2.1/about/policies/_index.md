---
title: Policies
weight: 30
prev: /docs/about/custom-resources
next: /docs/about/policies/TrafficPolicy
---

Learn more about the custom resources that you can use to apply policies in kgateway. 


While the {{< reuse "docs/snippets/k8s-gateway-api-name.md" >}} allows you to do simple routing, such as to match, redirect, or rewrite requests, you might want additional capabilities in your API gateway, such direct responses, local rate limiting, or request and response transformations. Policies allow you to apply intelligent traffic management, resiliency, and security standards to an HTTPRoute or Gateway. 

## Policy CRDs

Kgateway uses the following custom resources to attach policies to routes and gateway listeners. 

{{< cards >}}
  {{< card link="/docs/traffic-management/direct-response/" title="Direct response" subtitle="Directly respond to incoming requests with a custom HTTP response code and body." >}}
  {{< card link="/docs/about/policies/httplistenerpolicy/" title="HTTPListenerPolicy" subtitle="Apply policies to all HTTP and HTTPS listeners." >}}
  {{< card link="/docs/about/policies/trafficpolicy/" title="TrafficPolicy" subtitle="Attach policies to routes in an HTTPRoute or Gateway resource." >}}
{{< /cards >}}



## Supported policies {#supported-policies}

Review the policies that you can configure in kgateway and the level at which you can apply them.   

| Policy | Applied via |
| -- | -- | 
| [Access logging](/docs/security/access-logging) | HTTPListenerPolicy |
| [Direct response](/docs/traffic-management/direct-response/) | DirectResponse | 
| [External authorization](/docs/security/external-auth) | GatewayExtension and TrafficPolicy |
| [External processing (ExtProc)](/docs/traffic-management/extproc/) | TrafficPolicy | 
| [Local rate limiting](/docs/security/local-ratelimit/) | TrafficPolicy | 
| [Transformations](/docs/traffic-management/transformations) | TrafficPolicy | 

<!--

## Policy inheritance rules when using route delegation

Policies that are defined in a TrafficPolicy resource and that are applied to a parent HTTPRoute resource are automatically inherited by all the child or grandchild HTTPRoutes along the route delegation chain. The following rules apply: 

* Only policies that are specified in a TrafficPolicy resource can be inherited by a child HTTPRoute. For inheritance to take effect, you must use the `spec.targetRefs` field in the TrafficPolicy resource to apply the TrafficPolicy resource to the parent HTTPRoute resource. Any child or grandchild HTTPRoute that the parent delegates traffic to inherits these policies. 
* Child TrafficPolicy resources cannot override policies that are defined in a TrafficPolicy resource that is applied to a parent HTTPRoute. If the child HTTPRoute sets a policy that is already defined on the parent HTTPRoute, the setting on the parent HTTPRoute takes precedence and the setting on the child is ignored. For example, if the parent HTTPRoute defines a data loss prevention policy, the child HTTPRoute cannot change these settings or disable that policy.
* Child HTTPRoutes can augment the inherited settings by defining TrafficPolicy fields that were not already set on the parent HTTPRoute. 
* Policies are inherited along the complete delegation chain, with parent policies having a higher priority than their respective children.

For an example, see the [Policy inheritance](/docs/traffic-management/route-delegation/policy-inheritance/) guide.

--> 
