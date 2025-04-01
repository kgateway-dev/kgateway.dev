---
title: TrafficPolicy
weight: 10
description: Use a TrafficPolicy resource to attach policies to one, multiple, or all routes in an HTTPRoute resource, or all the routes that a Gateway serves. 
prev: /docs/about/policies
---

Use a TrafficPolicy resource to attach policies to one, multiple, or all routes in an HTTPRoute resource, or all the routes that a Gateway serves. 

## Policy attachment {#policy-attachment-TrafficPolicy}

You can apply TrafficPolicy policies to all routes in an HTTPRoute resource or only to specific routes. 

### Option 1: Attach the policy to all HTTPRoute routes (`targetRefs`)

You can use the `spec.targetRefs` section in the TrafficPolicy resource to apply policies to all the routes that are specified in a particular HTTPRoute resource. 

The following example TrafficPolicy resource specifies transformation rules. Because the `httpbin` HTTPRoute resource is referenced in the `spec.targetRefs` section, the transformation rules are applied to all routes in that HTTPRoute resource. 

```yaml {hl_lines=[7,8,9,10]}
apiVersion: gateway.kgateway.dev/v1alpha1
kind: TrafficPolicy
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

The following example shows a TrafficPolicy resource that defines a transformation rule. Note that the `spec.targetRef` field is not set. Because of that, the TrafficPolicy policy does not apply until it is referenced in an HTTPRoute by using the `ExtensionRef` filter. 

```yaml
apiVersion: gateway.kgateway.dev/v1alpha1
kind: TrafficPolicy
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

To apply the policy to a particular route, you use the `ExtensionRef` filter on the desired HTTPRoute route. In the following example, the TrafficPolicy is applied to the `/anything/path1` route. However, it is not applied to the `/anything/path2` path.   

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
    - TrafficPolicy.example
  rules:
  - matches:
    - path:
        type: PathPrefix
        value: /anything/path1
    filters:
      - type: ExtensionRef
        extensionRef:
          group: gateway.kgateway.dev
          kind: TrafficPolicy
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

Some policies, such as a local rate limiting policy, can be applied to all the routes that the Gateway serves. This way, you can apply gateway-level rules and do not have to keep track of new HTTPRoutes that are attached to the Gateway in your environment. 

To attach a TrafficPolicy to a Gateway, you simply use the `targetRefs` section in the TrafficPolicy to reference the Gateway you want the policy to apply to as shown in the following example. 

```yaml
kubectl apply -f- <<EOF
apiVersion: gateway.kgateway.dev/v1alpha1
kind: TrafficPolicy
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

Review how policies are merged if you apply multiple TrafficPolicy resources to the same route. 

### `ExtensionRef` vs. `targetRefs`

If you apply two TrafficPolicy resources that both specify the same top-level policy type and you attach one TrafficPolicy via the `extensionRef` filter and one via the `targetRefs` section, only the TrafficPolicy resource that is attached via the `extensionRef` filter is applied. The policy that is attached via `targetRefs` is ignored. 

Note that the `targetRefs` TrafficPolicy resource can augment the `extensionRef` TrafficPolicy if it specifies different top-level policies. <!-- For example, the `extensionRef` TrafficPolicy might define a policy that adds request headers. While you cannot specify additional or other request header rules in the `targetRefs` TrafficPolicy, you can define different policies, such as response headers or fault injection policies.  -->

<!--

In the following image, you have three TrafficPolicy resources that each define a {{< reuse "docs/snippets/product-name.md" >}} policy. One CORS policy (policy 1) is applied to all routes in an HTTPRoute resource via the `targetRefs` section. Another CORS policy (policy 2) and a fault injection policy (policy 3) are applied to only route A by using the `extensionRef` filter in the HTTPRoute resource.  

Because policies that are attached via `extensionRef` take precedence over policies that are attached via `targetRefs`, the CORS policy 2 is attached to route A. In addition, the fault injection policy is attached to route A. Route B does not attach any `extensionRef` TrafficPolicies. Because of that, the CORS policy 1 from the `targetRefs` TrafficPolicy is attached to route B. 

{{< reuse-image src="img/policy-ov-extensionref-targetref.svg" width="800px" >}} --> 

### Multiple `targetRefs` TrafficPolicies

If you create multiple TrafficPolicy resources and attach them to the same HTTPRoute by using the `targetRefs` option, only the TrafficPolicy that was last created is applied. To apply multiple policies to the same route, define the rules in the same TrafficPolicy. 

If you create multiple TrafficPolicy resources and attach one to a Gateway and one to an HTTPRoute, the policy is applied as follows: 
* The TrafficPolicy that is applied to the HTTPRoute takes precedence over the TrafficPolicy that is applied to the Gateway. This means that the HTTPRoutes routes are not affected by the gateway-level policy. 
* The TrafficPolicy that is applied to the Gateway is applied to all other routes that the Gateway serves. 

<!--
{{% callout type="info" %}}
You cannot attach multiple TrafficPolicy resources to the same route by using the `targetRefs` option, *even if* they define different top-level policies. To add multiple policies, define them in the same TrafficPolicy resource.
{{% /callout %}}

In the following image, you attach two TrafficPolicy resources to route A. One adds request headers and the other one a fault injection policy. Because only one TrafficPolicy can be applied to a route via `targetRefs` at any given time, only the policy that is created first is enforced (policy 1). 

{{< reuse-image src="img/policy-ov-multiple-trafficpolicy.svg" width="800" >}} -->

### Multiple `ExtensionRef` TrafficPolicies

If you attach multiple TrafficPolicy resources to an HTTPRoute by using the `ExtensionRef` filter, the TrafficPolicies are merged as follows: 

* TrafficPolicies that define different top-level policies are merged and applied to the route. 
* TrafficPolicies that define the same top-level policies, such as two transformation policies, are not merged. Instead, the TrafficPolicy that is referenced last is applied to the route. 

<!--
In the following image, you have an HTTPRoute that defines two routes (route A and route B). Route A attaches two TrafficPolicy resources via the `ExtensionRef` filter that specify the same top-level header manipulation policy. For route B, two TrafficPolicy resources with different top-level policies (fault injection and CORS) are applied via the `ExtensionRef` filter. 

Because you cannot apply two `ExtensionRef` TrafficPolicies with the same top-level policies, only the policy that is referenced first (policy 1, request header `foo`) is enforced. The request header bar in policy 2 is ignored. For route B, both the CORS and fault injection policies are applied, because these TrafficPolicy resources define different top-level policies. 

{{< reuse-image src="img/policy-ov-multiple-trafficpolicy-extensionref.svg" width="800" >}} -->

<!--

## Policy inheritance rules when using route delegation

Policies that are defined in a TrafficPolicy resource and that are applied to a parent HTTPRoute resource are automatically inherited by all the child or grandchild HTTPRoutes along the route delegation chain. The following rules apply: 

* Only policies that are specified in a TrafficPolicy resource can be inherited by a child HTTPRoute. For inheritance to take effect, you must use the `spec.targetRefs` field in the TrafficPolicy resource to apply the TrafficPolicy resource to the parent HTTPRoute resource. Any child or grandchild HTTPRoute that the parent delegates traffic to inherits these policies. 
* Child TrafficPolicy resources cannot override policies that are defined in a TrafficPolicy resource that is applied to a parent HTTPRoute. If the child HTTPRoute sets a policy that is already defined on the parent HTTPRoute, the setting on the parent HTTPRoute takes precedence and the setting on the child is ignored. For example, if the parent HTTPRoute defines a data loss prevention policy, the child HTTPRoute cannot change these settings or disable that policy.
* Child HTTPRoutes can augment the inherited settings by defining TrafficPolicy fields that were not already set on the parent HTTPRoute. 
* Policies are inherited along the complete delegation chain, with parent policies having a higher priority than their respective children.

For an example, see the [Policy inheritance](/docs/traffic-management/route-delegation/policy-inheritance/) guide. 

-->