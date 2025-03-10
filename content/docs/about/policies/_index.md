---
title: Policies
weight: 30
prev: /docs/about/custom-resources
next: /docs/about/policies/routeoption
---

Learn more about the custom resources that you can use to apply policies in {{< reuse "docs/snippets/product-name.md" >}}. 


While the {{< reuse "docs/snippets/k8s-gateway-api-name.md" >}} allows you to do simple routing, such as to match, redirect, or rewrite requests, you might want additional capabilities in your API gateway, such as fault injection, direct responses, or header control. Policies allow you to apply intelligent traffic management, resiliency, and security standards to individual routes or all the routes that the gateway serves. 

## Policy CRDs

{{< reuse "docs/snippets/product-name-caps.md" >}} uses the following custom resources to attach policies to routes and gateway listeners. 

{{< cards >}}
  {{< card link="/docs/traffic-management/direct-response/" title="Direct response" subtitle="Directly respond to incoming requests with a custom HTTP response code and body." >}}
  {{< card link="listeneroption" title="ListenerPolicy" subtitle="Attach policies to one, multiple, or all gateway listeners." >}}
  {{< card link="httplisteneroption" title="HTTPListenerPolicy patterns" subtitle="Apply policies to one, multiple, or all HTTP and HTTPS listeners." >}}
  {{< card link="routeoption" title="RouteOption" subtitle="Attach policies to one, multiple, or all routes in an HTTPRoute resource." >}}
  {{< card link="virtualhostoption" title="VirtualHostOption" subtitle="Attach policies to the hosts on one, multiple, or all gateway listeners." >}}
{{< /cards >}}

## Supported policies {#supported-policies}

Review the policies that you can configure in {{< reuse "docs/snippets/product-name.md" >}} and the level at which you can apply them.   

### Traffic management policies

| Policy | Applied via | Precedence and merging rules |
| -- | -- | -- | 
| [Connection buffer limits](/docs/traffic-management/buffering/) | ListenerPolicy | No cross-resource conflict. Policies can conflict only if applied in multiple ListenerPolicy resources. For more information, see [Conflicting policies](/docs/about/policies/listeneroption/#conflicting-policies).   | 
| [Direct response](/docs/traffic-management/direct-response/) | DirectResponse | No cross-resource conflict. If multiple DirectResponse resources are applied to the same route, only the one that is referenced first is enforced. | 
|[Fault injection](/docs/resiliency/fault-injection/) | RouteOption|  No cross-resource conflict. Policies can conflict only if applied in multiple RouteOption resources. For more information, see [Conflicting policies](/docs/about/policies/routeoption/#conflicting-policies-and-merging-rules). |
| [Header control](/docs/traffic-management/header-control/})  | <ul><li>RouteOption</li><li>VirtualHostOption</li></ul> |  Headers that are defined at the route and virtual host-level are merged as long as they do not conflict. If the same header is defined in both a RouteOption and VirtualHostOption resource, the RouteOption configuration takes precedence and the VirtualHostOption configuration is ignored.  |  
| [Proxy protocol](/docs/traffic-management/proxy-protocol/) | ListenerPolicy | No cross-resource conflict. Policies can conflict only if applied in multiple ListenerPolicy resources. For more information, see [Conflicting policies](/docs/about/policies/listeneroption/#conflicting-policies).  | 
| [Rewrites](/docs/traffic-management/rewrite/) | RouteOption |  No cross-resource conflict. Policies can conflict only if applied in multiple RouteOption resources. For more information, see [Conflicting policies](/docs/about/policies/routeoption/#conflicting-policies-and-merging-rules).  | 
| [Transformations](/docs/traffic-management/transformations) | <ul><li>RouteOption</li><li>VirtualHostOption</li></ul> | RouteOption configuration takes precedence over VirtualHostOption configuration. Policies that are defined at different levels are not merged. |

### Resiliency policies

| Policy | Applied to | Precedence and merging rules | 
| -- | -- | -- |
| [Fault injection](/docs/resiliency/fault-injection/) | RouteOption|  No cross-resource conflict. Policies can conflict only if applied in multiple RouteOption resources. For more information, see [Conflicting policies](/docs/about/policies/routeoption/#conflicting-policies-and-merging-rules). | 
| [Retries](/docs/resiliency/retry) | <ul><li>RouteOption</li><li>VirtualHostOption</li></ul> | RouteOption configuration takes precedence over VirtualHostOption configuration. Policies that are defined at different levels are not merged. | 
| [Shadowing](/docs/resiliency/shadowing/)  | RouteOption |  No cross-resource conflict. Policies can conflict only if applied in multiple RouteOption resources. For more information, see [Conflicting policies](/docs/about/policies/routeoption/#conflicting-policies-and-merging-rules).  | 
| [Timeouts](/docs/resiliency/timeouts) | RouteOption |  No cross-resource conflict. Policies can conflict only if applied in multiple RouteOption resources. For more information, see [Conflicting policies](/docs/about/policies/routeoption/#conflicting-policies-and-merging-rules).  |

### Security policies

| Policy | Applied to | Precedence and merging rules | 
| -- | -- | -- | 
| [Access logging](/docs/security/access-logging) | ListenerPolicy | No cross-resource conflict. Policies can conflict only if applied in multiple ListenerPolicy resources. For more information, see [Conflicting policies](/docs/about/policies/listeneroption/#conflicting-policies).    | 
| [CORS](/docs/security/cors) | <ul><li>RouteOption</li><li>VirtualHostOption</li></ul> | By default, the configuration of the RouteOption takes precedence over the VirtualHostOption. However, you can change this behavior for the `exposeHeaders` CORS option by using the `corsPolicyMergeSettings` field in the VirtualHostOption. Currently, only `exposeHeaders` is configurable. You cannot merge other CORS options such as `allowHeaders` or `allowOrigin`. For more information about this option, see the [CORS configuration options](/docs/security/cors/#configuration-options).  |
| [CSRF](/docs/security/csrf/) | <ul><li>RouteOption</li><li>VirtualHostOption</li><li>HTTPListenerPolicy</ul> | RouteOption configuration takes precedence over VirtualHostOption configuration, which takes precedence over HTTPListenerPolicy configuration. Policies that are defined at different levels are not merged.   |  
| [Local rate limiting](/docs/security/ratelimit/local/) | HTTPListenerPolicy | No cross-resource conflict. Policies can conflict only if applied in multiple HTTPListenerPolicy resources. For more information, see [Conflicting policies](/docs/about/policies/httplisteneroption/#conflicting-policies).| 


## Policy inheritance rules when using route delegation

Policies that are defined in a RouteOption resource and that are applied to a parent HTTPRoute resource are automatically inherited by all the child or grandchild HTTPRoutes along the route delegation chain. The following rules apply: 

* Only policies that are specified in a RouteOption resource can be inherited by a child HTTPRoute. For inheritance to take effect, you must use the `spec.targetRefs` field in the RouteOption resource to apply the RouteOption resource to the parent HTTPRoute resource. Any child or grandchild HTTPRoute that the parent delegates traffic to inherits these policies. 
* Child RouteOption resources cannot override policies that are defined in a RouteOption resource that is applied to a parent HTTPRoute. If the child HTTPRoute sets a policy that is already defined on the parent HTTPRoute, the setting on the parent HTTPRoute takes precedence and the setting on the child is ignored. For example, if the parent HTTPRoute defines a data loss prevention policy, the child HTTPRoute cannot change these settings or disable that policy.
* Child HTTPRoutes can augment the inherited settings by defining RouteOption fields that were not already set on the parent HTTPRoute. 
* Policies are inherited along the complete delegation chain, with parent policies having a higher priority than their respective children.

For an example, see the [Policy inheritance](/docs/traffic-management/route-delegation/policy-inheritance/) guide. 
