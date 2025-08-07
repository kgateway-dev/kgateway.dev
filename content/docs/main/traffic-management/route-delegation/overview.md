---
title: Route delegation overview
weight: 5
description:
---

Delegate routing decisions to another HTTPRoute resource.

## What is route delegation

As your environment grows, your gateways manage traffic for more and more routes. These routes typically belong to many different apps that are owned by different individuals or teams. Managing the routing rules for all of these routes can be cumbersome and route updates can easily impact the behavior of other routes. 

Route delegation allows you to split up big and complex routing configurations into smaller routing configurations that are easier to maintain. The ownership for these routing configurations are then delegated to the teams that own the app or domain. 

For example, let's assume you have three apps (`app-a`, `app-b`, and `app-c`) that are owned by three different teams (`team-a`, `team-b`, and `team-c`). Instead of creating one routing configuration that includes the routing rules for all apps, you create a routing configuration for each app and delegate ownership for this configuration to the team that is responsible for that app. Each team can then further delegate routing decisions to other teams. 

Each set of routing rules is defined in a dedicated HTTPRoute resource. These HTTPRoute resources are then organized into a routing hierarchy that consists of the following elements: 

| Element in routing hierarchy | Resource | Description|
|----------------|---|--|
|Parent|HTTPRoute| The parent HTTPRoute resource specifies the main domain under which all of the routes that are defined in the parent, child, or grandchild HTTPRoute resources are exposed on. The parent HTTPRoute resource also references the gateway that you want to use to fulfill the routing configuration in the `parentRef` section. To delegate traffic to a child HTTPRoute resource, a `PathPrefix` matcher must be used. |
|Child |HTTPRoute|The child HTTPRoute resource receives traffic from the parent HTTPRoute resource and can either forward traffic to the backing service, or delegate traffic decisions to grandchild HTTPRoute resources. To receive delegated traffic from a parent, the child HTTPRoute must match on a path that contains the path prefix for which the parent delegated traffic for. For example, if the parent delegates traffic for `/route`, the child must define a route that includes this prefix, such as `/route/a`. If traffic is further delegated to a grandchild HTTPRoute resource, a `PathPrefix` matcher must be used. |
|Grandchild|HTTPRoute|A grandchild HTTPRoute resource receives traffic from a child HTTPRoute resource and can either bind to a specific child by using the `parentRef` section or be selected by all child HTTPRoute resources that want to delegate traffic to this grandchild. To receive traffic from a child, the grandchild must match on a path that contains the path prefix for which the child delegated traffic for. For example, if the child delegates traffic for `/route/a`, the grandchild must define a route that includes this prefix, such as `/route/a/myservice`. If traffic is further delegated to a great-grandchild HTTPRoute resource, a `PathPrefix` matcher must be used. Note that great-grandchild or great-great-grandchild behave similar to a grandchild HTTPRoute resource. |

{{< callout type="info" >}}
For an example route delegation setup with a parent, child, and grandchild HTTPRoute resource, see [Multi-level delegation](/docs/traffic-management/route-delegation/multi-level-delegation/). 
{{< /callout >}}

## Benefits and use cases

Route delegation is often used as a security and risk mitigation strategy to allow multiple teams to own, add, remove, and update routes on a gateway without impacting the routing rules that other teams configured and requiring access to the entire routing configuration. 

Review some of the benefits that you can achieve with route delegation: 

|Benefit| Description| 
|--|--|
|Organize routing rules by user groups|With route delegation, you can break up large routing configurations into smaller routing configurations which makes them easier to maintain and to assign ownership to. Each routing configuration in the routing hierarchy contains the routing rules and policies for only a subset of routes.  |
|Restrict access to routing configuration| Because route delegation lets you break up large routing configurations into smaller, manageable pieces, you can easily assign ownership and restrict access to the smaller routing configurations to the individual or teams that are responsible for a specific app or domain. For example, the network administrator can configure the top level routing rules, such as the hostname and main route match, and delegate the individual routing rules to other teams. |
|Simplify blue-green route testing|To test new routing configuration, you can easily delegate a specific number of traffic to the new set of routes.|
| Optimize traffic flows| Route delegation can be used to distribute traffic load across multiple paths or nodes in the cluster, which can improve network performance and reliability. |
|Easier updates with limited blast radius| Individual teams can easily update the routing configuration for their apps and manage the policies for their routes. If errors are introduced, the blast radius is limited to the set of routes that were changed. | 

## Policy inheritance

Review how policies are inherited along the route delegation chain. 

For more information, see the [Policy inheritance](/docs/traffic-management/route-delegation/inheritance/) guides. 

### Native Gateway API policies

{{< reuse "docs/snippets/policy-inheritance-native.md" >}}

### Kgateway policies

{{< reuse "docs/snippets/policy-inheritance.md" >}}

## Automatic route replacement

If a destination that is defined in the HTTPRoute's `backendRefs` section cannot be found, such as when a parent HTTPRoute routes traffic to a child HTTPRoute that does not exist, the route is automatically replaced with a 500 HTTP direct response. However, valid routes are not replaced and continue to work.

## Weighted routing

You can use delegated routes together with [weighted routes](../../weighted-routes/). Make sure to enable the weighted routing feature. Then, add the `kgateway.dev/route-weight` annotation to the child HTTPRoute that you want to weight. Children **do not** inherit the weight of their parent HTTPRoute.

## Limitations

The current route delegation model imposes a few restrictions on how routes can be delegated. If a rule is violated, the corresponding rule is removed from the route. 

### Hostnames

Only parent HTTPRoutes can specify the `spec.hostnames` field. All child and grandchild HTTPRoute resources inherit the parent's hostname. 

### Route matchers
Parent HTTPRoute resources that delegate to child HTTPRoute resources _must_ use `PathPrefix` matchers as shown in the following example: 

```yaml {linenos=table,hl_lines=[2,3,4,5],linenostart=1},filename="route-matcher.yaml"
 rules:
 - matches:
   - path:
       type: PathPrefix
       value: /a
   backendRefs:
   - group: gateway.networking.k8s.io
     kind: HTTPRoute
     name: "*"
     namespace: abc
```

Child HTTPRoute resources can use prefix, exact, or regex path matchers in their matching rules as shown in the following example. Each path matcher must start with the prefix path that the parent HTTPRoute delegates traffic for, in this case `/a`. The child HTTPRoute in the following example defines three route matchers along the `/a` path: `/1`, `/1/foo`, and `/1/.*`. 
```yaml {linenos=table,hl_lines=[5,8,11],linenostart=1},filename="route-matcher.yaml"
 rules:
 - matches:
   - path:
       type: PathPrefix
       value: /a/1
   - path:
       type: Exact
       value: /a/1/foo
   - path:
       type: RegularExpression
       value: /a/1/.*
   backendRefs:
   - name: svc-a
     port: 8080
```

{{< callout type="info" >}}
Keep in mind that if a child HTTPRoute delegates routing decisions to a grandchild or great-grandchild HTTPRoute, a `PathPrefix` matcher must be used for that route. Check out the [Multi-level delegation](/docs/traffic-management/route-delegation/multi-level-delegation/) guide for an example of how to set up route delegation between a parent, child, and grandchild HTTPRoute. 
{{< /callout >}}

{{< callout type="info" >}}
You can optionally set the `delegation.kgateway.dev/inherit-parent-matcher: "true"` annotation on the child HTTPRoute to inherit all the matchers, headers, and query parameters from the parent. To find an example, see [Header and query match](/docs/traffic-management/route-delegation/header-query/).
{{< /callout >}}


### Headers, query parameters, HTTP methods

You can specify headers, query parameters, and HTTP method matchers on the parent HTTPRoute resource. However, any child HTTPRoute resource that you delegate traffic to must specify the same header, query parameters, or HTTP method matchers to be considered a valid configuration. You can optionally define additional header, query parameter, or HTTP method matchers on the child.  

{{< callout type="info" >}}
You can optionally set the `delegation.kgateway.dev/inherit-parent-matcher: "true"` annotation on the child HTTPRoute to inherit all the matchers, headers, and query parameters from the parent. That way, the headers and query parameters do not need to be defined on the child HTTPRoute.
{{< /callout >}}

For example, let's say you define the following parent and child HTTPRoute resources: 

| Example configuration | Valid route delegation configuration?|
|-------------|---|
| <ul><li>parent<ul><li>match on <code>/anything/team1</code> and delegate traffic to the <code>child</code> HTTPRoute</li><li>header1: val1</li><li>query1=val1</li></ul></li><li>child<ul><li>match on <code>/anything/team1/foo</code> and route traffic to the httpbin app </li><li>header1: val1</li><li>headerX: valX</li><li>query1=val1</li><li>queryX=valX</li></ul></li></ul> | ✅ </br></br> The headers and query parameters that are specified on the child HTTPRoute are a superset of the header and query parameters that are specified on the parent.  |
|<ul><li>parent<ul><li>match on <code>/anything/team1</code> and delegate traffic to the <code>child</code> HTTPRoute</li><li>header1: val1</li><li>query1=val1</li></ul></li><li>child<ul><li>match on <code>/anything/team1/foo</code> and route traffic to the httpbin app </li><li>headerX: valX</li><li>queryX=valX</li></ul></li></ul> | ❌ </br></br> The headers and query parameters that are specified on the child HTTPRoute do not include the header and query parameters that are specified on the parent.  |
|<ul><li>parent<ul><li>match on <code>/anything/team1</code> and delegate traffic to the <code>child</code> HTTPRoute</li><li>header1: val1</li><li>query1=val1</li></ul></li><li>child<ul><li>match on <code>/anything/team1/foo</code> and route traffic to the httpbin app </li><li>headerX: valX</li><li>queryX=valX</li><li><code>delegation.kgateway.dev/inherit-parent-matcher: "true"</code></li></ul></li></ul> | ✅  </br></br> The headers and query parameters that are specified on the child HTTPRoute do not include the header and query parameters that are specified on the parent. However, the `delegation.kgateway.dev/inherit-parent-matcher: "true"` annotation is set and allows the child HTTPRoute to inherit the matchers, headers, and query parameters from the parent.  |

{{< callout type="info" >}}
For an example route delegation setup that uses header and query parameters, see [Header and query match](/docs/traffic-management/route-delegation/header-query/). 
{{< /callout >}}

### Cyclic delegation

Cyclic route delegations, such as where HTTPRoute A delegates to B, B delegates to C, and C delegates back to A are not allowed as no proper backend is specified that fulfills the request. If cyclic route delegation is detected, the route that is part of the cycle is automatically replaced with a 500 HTTP direct response.   

