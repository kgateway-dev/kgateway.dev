---
title: TrafficPolicy
weight: 10
description: Use a TrafficPolicy resource to attach policies to one, multiple, or all routes in an HTTPRoute resource, or all the routes that a Gateway serves. 
prev: /docs/about/policies
---

Use a {{< reuse "docs/snippets/trafficpolicy.md" >}} resource to attach policies to one, multiple, or all routes in an HTTPRoute resource, or all the routes that a Gateway serves. 

## Policy attachment {#policy-attachment-TrafficPolicy}

You can apply {{< reuse "docs/snippets/trafficpolicies.md" >}} to all routes in an HTTPRoute resource or only to specific routes. 

{{< callout type="info" >}}
{{< reuse "docs/snippets/global-policy.md" >}}
{{< /callout >}}

### All HTTPRoute routes {#attach-to-all-routes}

You can use the `spec.targetRefs` section in the {{< reuse "docs/snippets/trafficpolicy.md" >}} resource to apply policies to all the routes that are specified in a particular HTTPRoute resource. 

The following example {{< reuse "docs/snippets/trafficpolicy.md" >}} resource specifies transformation rules that are applied to all routes in the `httpbin` HTTPRoute resource. 

```yaml {hl_lines=[7,8,9,10]}
apiVersion: {{< reuse "docs/snippets/trafficpolicy-apiversion.md" >}}
kind: {{< reuse "docs/snippets/trafficpolicy.md" >}}
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
      - name: x-kgateway-response
        value: '{{ request_header("x-kgateway-request") }}' 
```

You can also apply the same {{< reuse "docs/snippets/trafficpolicy.md" >}} to multiple HTTPRoutes by referencing them in the `targetRefs` section, as shown in the following example. 

```yaml {hl_lines=[7,8,9,10,11,12,13,14,15,16]}
apiVersion: {{< reuse "docs/snippets/trafficpolicy-apiversion.md" >}}
kind: {{< reuse "docs/snippets/trafficpolicy.md" >}}
metadata:
  name: transformation
  namespace: httpbin
spec:
  targetRefs: 
  - group: gateway.networking.k8s.io
    kind: HTTPRoute
    name: httpbin
  - group: gateway.networking.k8s.io
    kind: HTTPRoute
    name: petstore
  - group: gateway.networking.k8s.io
    kind: HTTPRoute
    name: echo
  transformation:
    response:
      set:
      - name: x-kgateway-response
        value: '{{ request_header("x-kgateway-request") }}' 
```


### Individual route {#attach-to-route}

Instead of applying the policy to all routes that are defined in an HTTPRoute resource, you can apply them to specific routes by using the `ExtensionRef` filter in the HTTPRoute resource. 

{{< callout type="warning" >}}
Attaching a policy via the `ExtensionRef` filter is legacy behavior and might be deprecated in a future release. Instead, use the [HTTPRoute rule attachment option](#attach-to-rule) to apply a policy to an individual route, which requires the Kubernetes Gateway API experimental channel version 1.3.0 or later.
{{< /callout >}}

The following example shows a {{< reuse "docs/snippets/trafficpolicy.md" >}} resource that defines a transformation rule. Note that the `spec.targetRef` field is not set. Because of that, the {{< reuse "docs/snippets/trafficpolicy.md" >}} does not apply until it is referenced in an HTTPRoute by using the `ExtensionRef` filter. 

```yaml
apiVersion: {{< reuse "docs/snippets/trafficpolicy-apiversion.md" >}}
kind: {{< reuse "docs/snippets/trafficpolicy.md" >}}
metadata:
  name: transformation
  namespace: httpbin
spec:
  transformation:
    response:
      set:
      - name: x-kgateway-response
        value: '{{ request_header("x-kgateway-request") }}' 
```

To apply the policy to a particular route, you use the `ExtensionRef` filter on the desired HTTPRoute route. In the following example, the {{< reuse "docs/snippets/trafficpolicy.md" >}} is applied to the `/anything/path1` route. However, it is not applied to the `/anything/path2` path.   

```yaml {hl_lines=[17,18,19,20,21,22]}
apiVersion: gateway.networking.k8s.io/v1
kind: HTTPRoute
metadata:
  name: httpbin-policy
  namespace: httpbin
spec:
  parentRefs:
  - name: http
    namespace: kgateway-system
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
          group: {{< reuse "docs/snippets/trafficpolicy-group.md" >}}
          kind: {{< reuse "docs/snippets/trafficpolicy.md" >}}
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

### HTTPRoute rule {#attach-to-rule}

{{< callout type="info" >}}
To use this feature, you must install the Kubernetes Gateway API experimental channel version 1.3.0 or later.
{{< /callout >}}

Instead of using the `extensionRef` filter to apply a policy to a specific route, you can attach a {{< reuse "docs/snippets/trafficpolicy.md" >}} to an HTTPRoute rule by using the {{< reuse "docs/snippets/trafficpolicy.md" >}}'s `targetRefs.sectionName` option. 

You can also use this attachment option alongside the `extensionRef` filter. However, policies that are attached via the `extensionRef` filter take precedence over policies that are attached via the `targetRefs.sectionName` option. For more information, see [Conflicting policies and merging rules](#conflicting-policies-and-merging-rules). 

The following HTTPRoute defines two HTTPRoute rules that both route traffic to the httpbin app. 
```yaml
kubectl apply -f- <<EOF
apiVersion: gateway.networking.k8s.io/v1
kind: HTTPRoute
metadata:
  name: httpbin
  namespace: httpbin
spec:
  parentRefs:
  - name: http
    namespace: kgateway-system
  hostnames:
    - TrafficPolicy.example
  rules:
  - name: rule0
    matches:
    - path:
        type: PathPrefix
        value: /anything/path1
    backendRefs:
    - name: httpbin
      port: 8000
  - name: rule1
    matches:
    - path:
        type: PathPrefix
        value: /anything/path2
    backendRefs:
      - name: httpbin
        port: 8000
EOF
```

To apply a {{< reuse "docs/snippets/trafficpolicy.md" >}} to a specific HTTPRoute rule (`rule1`), use the {{< reuse "docs/snippets/trafficpolicy.md" >}}'s `targetRefs.sectionName` option as shown in the following example. 

```yaml
kubectl apply -f- <<EOF
apiVersion: {{< reuse "docs/snippets/trafficpolicy-apiversion.md" >}}
kind: {{< reuse "docs/snippets/trafficpolicy.md" >}}
metadata:
  name: local-ratelimit
  namespace: kgateway-system
spec:
  targetRefs: 
  - group: gateway.networking.k8s.io
    kind: HTTPRoute
    name: httpbin
    sectionName: rule1
  rateLimit:
    local:
      tokenBucket:
        maxTokens: 1
        tokensPerFill: 1
        fillInterval: 100s
EOF
```

### Gateway {#attach-to-gateway}

Some policies, such as a local rate limiting policy, can be applied to all the routes that the Gateway serves. This way, you can apply gateway-level rules and do not have to keep track of new HTTPRoutes that are attached to the Gateway in your environment. 

To attach a {{< reuse "docs/snippets/trafficpolicy.md" >}} to a Gateway, you simply use the `targetRefs` section in the {{< reuse "docs/snippets/trafficpolicy.md" >}} to reference the Gateway you want the policy to apply to as shown in the following example. 

```yaml
apiVersion: {{< reuse "docs/snippets/trafficpolicy-apiversion.md" >}}
kind: {{< reuse "docs/snippets/trafficpolicy.md" >}}
metadata:
  name: local-ratelimit
  namespace: kgateway-system
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
```

### Gateway listener {#attach-to-listener}

Instead of applying a {{< reuse "docs/snippets/trafficpolicy.md" >}} to all the routes that the Gateway serves, you can select specific Gateway listeners by using the `targetRefs.sectionName` option. 

The following Gateway resource defines two listeners, an HTTP (`http`) and HTTPS (`https`) listener. 

```yaml
kind: Gateway
apiVersion: gateway.networking.k8s.io/v1
metadata:
  name: http
  namespace: kgateway-system
spec:
  gatewayClassName: kgateway
  listeners:
  - name: http
    protocol: HTTP
    port: 8080
    allowedRoutes:
      namespaces:
        from: All
  - name: https
    port: 443
    protocol: HTTPS
    tls:
      mode: Terminate
      certificateRefs:
        - name: https
          kind: Secret
    allowedRoutes:
      namespaces:
        from: All
```

To apply the policy to only the `https` listener, you specify the listener name in the `spec.targetRefs.sectionName` field in the {{< reuse "docs/snippets/trafficpolicy.md" >}} resource as shown in the following example. 

```yaml
apiVersion: {{< reuse "docs/snippets/trafficpolicy-apiversion.md" >}}
kind: {{< reuse "docs/snippets/trafficpolicy.md" >}}
metadata:
  name: local-ratelimit
  namespace: kgateway-system
spec:
  targetRefs: 
  - group: gateway.networking.k8s.io
    kind: Gateway
    name: http
    sectionName: https
  rateLimit:
    local:
      tokenBucket:
        maxTokens: 1
        tokensPerFill: 1
        fillInterval: 100s
```

## Policy priority and merging rules

If you apply multiple {{< reuse "docs/snippets/trafficpolicies.md" >}} by using different attachment options, policies are merged based on specificy and priority. 

By default, the following rules apply. You can update the behavior by using the `kgateway.dev/inherited-policy-priority` annotation. For more information, see [Policy merging](/docs/about/policies/merging/).

* If you apply multiple {{< reuse "docs/snippets/trafficpolicies.md" >}} that define the same top-level policy, the policies are not merged and only the oldest policy is enforced. Policies with a later timestamp are ignored. 
* {{< reuse "docs/snippets/trafficpolicies.md" >}} that define different top-level policies are merged and are enforced in combination. 
* In addition to the timestamp, the attachment option of a policy determines the policy priority. In general, more specific policy targets have higher priority and take precedence over less specific policies. For example, a policy targeting an individual route has higher priority than a policy targeting all the routes in an HTTPRoute resource. However, keep in mind that these rules might be different in a route delegation setup. For more information, see [Policy inheritance and overrides in delegation setups](#delegation). 
* Lower priority policies can augment higher priority policies by defining other top-level policies. For example, if you already attached a local rate limiting policy to a Gateway listener by using the `targetRefs.sectionName` option, you can add another {{< reuse "docs/snippets/trafficpolicy.md" >}} that defines a transformation policy and apply that policy to the entire Gateway. 
* Native Kubernetes Gateway API policies have higher priority than any kgateway policies that must be attached via the `targetRefs` or `extensionRef` option.

### Priority order

Review the following Gateway and HTTPRoute policy priorities, sorted from highest to lowest.

**Gateway**: 

| Priority | Attachment option | Description | 
| -- | -- | -- | 
| 1 | [Gateway listener policy](#attach-to-listener) | A {{< reuse "docs/snippets/trafficpolicy.md" >}} references a Gateway listener by using the `targetRefs.sectionName` field has the highest priority. Note that if you have multiple Gateway listener policies that define the same top-level policy, only the one with the oldest timestamp is applied. |
| 2 | [Gateway policy](#attach-to-gateway) | A {{< reuse "docs/snippets/trafficpolicy.md" >}} references a Gateway in the `targetRefs` section has the lowest priority. This policy can still augment any higher priority policies by defining different top-level policies. Note that if you have multiple Gateway policies that all define the same top-level policy, only the one with the oldest timestamp is applied. |

**HTTPRoute**: 

| Priority | Attachment option | Description | 
| -- | -- | -- | 
| 1 | [Individual HTTPRoute policy](#attach-to-route) | A {{< reuse "docs/snippets/trafficpolicy.md" >}} that is attached to an individual route by using the `extensionRef` filter in the HTTPRoute has the highest priority. Note that if you have multiple HTTPRoute policies that are attached via the `extensionRef` option and all define the same top-level policy, only the one with the oldest timestamp is applied. | 
| 2 | [HTTPRoute rule policy](#attach-to-rule) | A {{< reuse "docs/snippets/trafficpolicy.md" >}} that is attached to an HTTPRoute rule by using the `targetRefs.sectionName` option has a lower priority. This policy can still augment any `extensionRef` policies by defining different top-level policies. Note that if you have multiple HTTPRoute rule policies and all define the same top-level policy, only the one with the oldest timestamp is applied. | 
| 3 | [All HTTPRoute routes policy](#attach-to-all-routes) | A {{< reuse "docs/snippets/trafficpolicy.md" >}} that is attached to all routes in an HTTPRoute resource by using the `targetRefs` option has the lowest priority. You can still augment any higher priority policies by defining different top-level policies. If you have multiple HTTPRoute rule policies and they all specify the same top-level policy, only the one with the oldest timestamp is applied. | 

{{< callout type="info" >}} 
If you apply a {{< reuse "docs/snippets/trafficpolicy.md" >}} with the same top-level policy to a Gateway and an HTTPRoute, the policy on the HTTPRoute takes precedence and the one on the Gateway is ignored. For example, you might have two local rate limiting policies. One is applied to a Gateway and one is applied to the HTTPRoute. Because the same top-level policy is defined, the policy on the HTTPRoute is considered higher priority and therefore enforced. 
{{< /callout >}}

### Policy inheritance and overrides in delegation setups {#delegation}

The way policies are inherited along the route delegation chain depends on the type of policy that you want to apply. 

#### Native Gateway API policies

{{< reuse "docs/snippets/policy-inheritance-native.md" >}}

For an example, see the policy inheritance guide for [Native Gateway API policies](/docs/traffic-management/route-delegation/inheritance/native-policies/). 

#### kgateway policies

{{< reuse "docs/snippets/policy-inheritance.md" >}}

For an example, see the policy inheritance guide for [kgateway policies](/docs/traffic-management/route-delegation/inheritance/kgateway-policies/). 

