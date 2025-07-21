---
title: Policies
weight: 30
prev: /docs/about/custom-resources
next: /docs/about/policies/trafficpolicy
---

Learn more about the custom resources that you can use to apply policies in kgateway. 


While the {{< reuse "docs/snippets/k8s-gateway-api-name.md" >}} allows you to do simple routing, such as to match, redirect, or rewrite requests, you might want additional capabilities in your API gateway, such direct responses, local rate limiting, or request and response transformations. Policies allow you to apply intelligent traffic management, resiliency, and security standards to an HTTPRoute or Gateway. 

## Policy CRDs

Kgateway uses the following custom resources to attach policies to routes and gateway listeners. 

{{< cards >}}
  {{< card link="../policies/backendconfigpolicy/" title="BackendConfigPolicy" subtitle="Configure connection settings to an upstream service." >}}
  {{< card link="../../traffic-management/direct-response/" title="Direct response" subtitle="Directly respond to incoming requests with a custom HTTP response code and body." >}}
  {{< card link="../policies/httplistenerpolicy/" title="HTTPListenerPolicy" subtitle="Apply policies to all HTTP and HTTPS listeners." >}}
  {{< card link="../policies/trafficpolicy/" title="TrafficPolicy" subtitle="Attach policies to routes in an HTTPRoute or Gateway resource." >}}
{{< /cards >}}



## Supported policies {#supported-policies}

Review the policies that you can configure in kgateway and the level at which you can apply them.   

| Policy | Applied via |
| -- | -- | 
| [Access logging](../../security/access-logging) | HTTPListenerPolicy |
| [Backend connection config](../../resiliency/connection)| BackendConfigPolicy | 
| [Direct response](../../traffic-management/direct-response/) | DirectResponse | 
| [External authorization](../../security/external-auth) | GatewayExtension and {{< reuse "docs/snippets/trafficpolicy.md" >}} |
| [External processing (ExtProc)](../../traffic-management/extproc/) | {{< reuse "docs/snippets/trafficpolicy.md" >}} | 
| [Local rate limiting](../../security/local-ratelimit/) | {{< reuse "docs/snippets/trafficpolicy.md" >}} | 
| [Transformations](../../traffic-management/transformations) | {{< reuse "docs/snippets/trafficpolicy.md" >}} | 

## Policy merging {#policy-merging}

{{< reuse "/docs/snippets/kgateway-capital.md" >}} lets you define how policies are merged when they are applied to a parent and child resource. 

Parent-child hierarchies might be:

* Resources that target or serve other resources, such as Gateway > ListenerSet > HTTPRoute > Route rule.
* Routes that are delegated, such as Parent HTTPRoute A > Child HTTPRoute B > Grandchild HTTPRoute C.

Policy merging applies to the following policies:

* Native Kubernetes Gateway API policies, such as rewrites, timeouts, or retries.
* {{< reuse "/docs/snippets/kgateway-capital.md" >}} {{< reuse "docs/snippets/trafficpolicy.md" >}}.

Resources that are higher in the parent-child hierarchy can use a special annotation to define how child resources inherit policies. This way, parent resources such as a Gateway or HTTPRoute can decide whether child resources can override the parent policies or not.

### Merging annotation {#merging-annotation}

The annotation on the parent resource is: `kgateway.dev/inherited-policy-priority`.

The annotation takes four values:

- `ShallowMergePreferChild` (default): Child policies take precedence over parent policies and the policies are shallow merged.
- `ShallowMergePreferParent`: Parent policies take precedence over child policies and the policies are shallow merged.
- `DeepMergePreferChild`: Child policies take precedence over parent policies and the policies are deep merged.
- `DeepMergePreferParent`: Parent policies take precedence over child policies and the policies are deep merged.

### Shallow or deep merging {#shallow-deep-merging}

Merging ensures that policies from parent and child resources are combined without conflicts, using either _shallow_ or _deep_ strategies.

**Shallow merging** means that the policies are merged at the top level. Only the top-level fields of the policies are considered for merging. If a field is present in both parent and child policies, the value from the higher priority policy is used. Priority is typically determined by specificity and creation time. The more specific (such as HTTPRoute rule over all the routes in the HTTPRoute) and older (created-first) policy takes precedence. Consider the following shallow merge scenario:

* Parent policy adds a `x-season=summer` header.
* Child policy adds `x-season=winter` and `x-holiday=christmas` headers.
* Merging annotation is the default value, `ShallowMergePreferChild`.

Resulting merged policy: The parent's `x-season` header is not included in the merged policy because the strategy is `ShallowMergePreferChild`.

| Header | Value | Source |
| -- | -- | -- |
| `x-season` | `winter` | Child |
| `x-holiday` | `christmas` | Child |

**Deep merging** means that values from both parent and child policies can be combined. Currently, only [Transformation rules of a {{< reuse "docs/snippets/trafficpolicy.md" >}}](../../traffic-management/transformations) can be deep merged. Consider the following deep merge scenario:

* Parent policy adds an `x-season=summer` header.
* Child policy adds `x-season=winter` and `x-holiday=christmas` headers.
* Grandchild policy adds `x-season=spring`, `x-holiday=easter`, `x-discount=10%` headers.
* Merging annotation is `DeepMergePreferParent`.

Resulting merged policy's headers: The child and grandchild values merge with the parent's, with the parent's value ordered first because it takes precedence.

| Header | Value | Source |
| -- | -- | -- |
| `x-season` | `summer,winter,spring` | Parent, Child, Grandchild |
| `x-holiday` | `christmas,easter` | Child, Grandchild |
| `x-discount` | `10%` | Grandchild |

### Merging examples {#merging-examples}

For more information, check out the following guides:

* {{< reuse "docs/snippets/trafficpolicy.md" >}}'s [Policy priority and merging rules](../policies/trafficpolicy/#policy-priority-and-merging-rules)
* [Policy inheritance and overrides](../../traffic-management/route-delegation/inheritance/) for both Kubernetes Gateway API and {{< reuse "/docs/snippets/kgateway.md" >}} policies.
