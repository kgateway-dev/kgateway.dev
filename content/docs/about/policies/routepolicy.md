---
title: RoutePolicy
weight: 10
description: Use a RouteOption resource to attach policies to one, multiple, or all routes in an HTTPRoute resource, or all the routes that a Gateway serves. 
prev: /docs/about/policies
---

Use a RouteOption resource to attach policies to one, multiple, or all routes in an HTTPRoute resource, or all the routes that a Gateway serves. 

## Policy attachment {#policy-attachment-routeoption}

You can apply RouteOption policies to all routes in an HTTPRoute resource or only to specific routes. 

### Option 1: Attach the policy to all HTTPRoute routes (`targetRefs`)

You can use the `spec.targetRefs` section in the RoutePolicy resource to apply policies to all the routes that are specified in a particular HTTPRoute resource. 

The following example RoutePolicy resource specifies transformation rules. Because the `httpbin` HTTPRoute resource is referenced in the `spec.targetRefs` section, the transformation rules are applied to all routes in that HTTPRoute resource. 

```yaml {hl_lines=[7,8,9,10]}
apiVersion: gateway.kgateway.dev/v1alpha1
kind: RoutePolicy
metadata:
  name: transformation
  namespace: httpbin
spec:
  targetRefs: 
  - group: gateway.networking.k8s.io
    kind: HTTPRoute
    name: httpbin
  transformation:
    response:
      set:
      - name: x-solo-response
        value: '{{ request_header("x-solo-request") }}' 
```

### Option 2: Attach the policy to an individual route (`ExtensionRef`)

Instead of applying the policy to all routes that are defined in an HTTPRoute resource, you can apply them to specific routes by using the `ExtensionRef` filter in the HTTPRoute resource. 

The following example shows a RoutePolicy resource that defines a transformation rule. Note that the `spec.targetRef` field is not set. Because of that, the RoutePolicy policy does not apply until it is referenced in an HTTPRoute by using the `ExtensionRef` filter. 

```yaml
apiVersion: gateway.kgateway.dev/v1alpha1
kind: RoutePolicy
metadata:
  name: transformation
  namespace: httpbin
spec:
  transformation:
    response:
      set:
      - name: x-solo-response
        value: '{{ request_header("x-solo-request") }}' 
```

To apply the policy to a particular route, you use the `ExtensionRef` filter on the desired HTTPRoute route. In the following example, the RoutePolicy is applied to the `/anything/path1` route. However, it is not applied to the `/anything/path2` path.   

```yaml {hl_lines=[17,18,19,20,21,22]}
apiVersion: gateway.networking.k8s.io/v1
kind: HTTPRoute
metadata:
  name: httpbin-policy
  namespace: httpbin
spec:
  parentRefs:
  - name: http
    namespace: {{< reuse "docs/snippets/ns-system.md" >}}
  hostnames:
    - routepolicy.example
  rules:
  - matches:
    - path:
        type: PathPrefix
        value: /anything/path1
    filters:
      - type: ExtensionRef
        extensionRef:
          group: gateway.kgateway.dev
          kind: RoutePolicy
          name: transformation
    backendRefs:
    - name: httpbin
      port: 8000
  - matches:
    - path:
        type: PathPrefix
        value: /anything/path2
    backendRefs:
      - name: httpbin
        port: 8000
```

### Option 3: Attach the policy to a Gateway (#attach-to-gateway)

Some policies, such as a local rate limiting policy, can be applied to all the routes that the Gateway services. This way, you can apply gateway-level rules and do not have to keep track of new HTTPRoutes that are attached to the Gateway in your environment. 

To attach a RoutePolicy to a Gateway, you simply use the `targetRefs` section in the RoutePolicy to reference the Gateway you want the policy to apply to as shown in the following example. 

```yaml
kubectl apply -f- <<EOF
apiVersion: gateway.kgateway.dev/v1alpha1
kind: RoutePolicy
metadata:
  name: local-ratelimit
  namespace: {{< reuse "docs/snippets/ns-system.md" >}}
spec:
  targetRefs: 
  - group: gateway.networking.k8s.io
    kind: Gateway
    name: http
  rateLimit:
    local:
      tokenBucket:
        maxTokens: 1
        tokensPerFill: 1
        fillInterval: 100s
EOF
```

## Conflicting policies and merging rules

Review how policies are merged if you apply multiple RoutePolicy resources to the same route. 

### `ExtensionRef` vs. `targetRefs`

If you apply two RoutePolicy resources that both specify the same top-level policy type and you attach one RoutePolicy via the `extensionRef` filter and one via the `targetRefs` section, only the RoutePolicy resource that is attached via the `extensionRef` filter is applied. The policy that is attached via `targetRefs` is ignored. 

Note that the `targetRefs` RoutePolicy resource can augment the `extensionRef` RoutePolicy if it specifies different top-level policies. <!-- For example, the `extensionRef` RouteOption might define a policy that adds request headers. While you cannot specify additional or other request header rules in the `targetRefs` RouteOption, you can define different policies, such as response headers or fault injection policies.  -->

<!--

In the following image, you have three RouteOption resources that each define a {{< reuse "docs/snippets/product-name.md" >}} policy. One CORS policy (policy 1) is applied to all routes in an HTTPRoute resource via the `targetRefs` section. Another CORS policy (policy 2) and a fault injection policy (policy 3) are applied to only route A by using the `extensionRef` filter in the HTTPRoute resource.  

Because policies that are attached via `extensionRef` take precedence over policies that are attached via `targetRefs`, the CORS policy 2 is attached to route A. In addition, the fault injection policy is attached to route A. Route B does not attach any `extensionRef` RouteOptions. Because of that, the CORS policy 1 from the `targetRefs` RouteOption is attached to route B. 

{{< reuse-image src="img/policy-ov-extensionref-targetref.svg" width="800px" >}} --> 

### Multiple `targetRefs` RoutePolicies

If you create multiple RoutePolicy resources and attach them to the same HTTPRoute by using the `targetRefs` option, only the RoutePolicy that was last created is applied. To apply multiple policies to the same route, define the rules in the same RoutePolicy. 

If you create multiple RoutePolicy resources and attach one to a Gateway and one to an HTTPRoute, the policy is applied as follows: 
* The RoutePolicy that is applied to the HTTPRoute takes precedence over the RoutePolicy that is applied to the Gateway. This means that the HTTPRoutes routes are not affected by the gateway-level policy. 
* The RoutePolicy that is applied to the Gateway is applied to all other routes that the Gateway serves. 

<!--
{{% callout type="info" %}}
You cannot attach multiple RouteOption resources to the same route by using the `targetRefs` option, *even if* they define different top-level policies. To add multiple policies, define them in the same RouteOption resource.
{{% /callout %}}

In the following image, you attach two RouteOption resources to route A. One adds request headers and the other one a fault injection policy. Because only one RouteOption can be applied to a route via `targetRefs` at any given time, only the policy that is created first is enforced (policy 1). 

{{< reuse-image src="img/policy-ov-multiple-routeoption.svg" width="800" >}} -->

### Multiple `ExtensionRef` RoutePolicies

If you attach multiple RoutePolicy resources to an HTTPRoute by using the `ExtensionRef` filter, the RoutePolicies are merged as follows: 

* RoutePolicies that define different top-level policies are merged and applied to the route. 
* RoutePolicies that define the same top-level policies, such as two transformation policies, are not merged. Instead, the RoutePolicy that is referenced last is applied to the route. 

<!--
In the following image, you have an HTTPRoute that defines two routes (route A and route B). Route A attaches two RouteOption resources via the `ExtensionRef` filter that specify the same top-level header manipulation policy. For route B, two RouteOption resources with different top-level policies (fault injection and CORS) are applied via the `ExtensionRef` filter. 

Because you cannot apply two `ExtensionRef` RouteOptions with the same top-level policies, only the policy that is referenced first (policy 1, request header `foo`) is enforced. The request header bar in policy 2 is ignored. For route B, both the CORS and fault injection policies are applied, because these RouteOption resources define different top-level policies. 

{{< reuse-image src="img/policy-ov-multiple-routeoption-extensionref.svg" width="800" >}} -->

<!--

## Policy inheritance rules when using route delegation

Policies that are defined in a RouteOption resource and that are applied to a parent HTTPRoute resource are automatically inherited by all the child or grandchild HTTPRoutes along the route delegation chain. The following rules apply: 

* Only policies that are specified in a RouteOption resource can be inherited by a child HTTPRoute. For inheritance to take effect, you must use the `spec.targetRefs` field in the RouteOption resource to apply the RouteOption resource to the parent HTTPRoute resource. Any child or grandchild HTTPRoute that the parent delegates traffic to inherits these policies. 
* Child RouteOption resources cannot override policies that are defined in a RouteOption resource that is applied to a parent HTTPRoute. If the child HTTPRoute sets a policy that is already defined on the parent HTTPRoute, the setting on the parent HTTPRoute takes precedence and the setting on the child is ignored. For example, if the parent HTTPRoute defines a data loss prevention policy, the child HTTPRoute cannot change these settings or disable that policy.
* Child HTTPRoutes can augment the inherited settings by defining RouteOption fields that were not already set on the parent HTTPRoute. 
* Policies are inherited along the complete delegation chain, with parent policies having a higher priority than their respective children.

For an example, see the [Policy inheritance](/docs/traffic-management/route-delegation/policy-inheritance/) guide. 

-->