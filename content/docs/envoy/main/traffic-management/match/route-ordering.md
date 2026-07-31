---
title: Route ordering
weight: 425
description: Understand how HTTPRoute rules are ordered and prioritized when multiple routes match an incoming request.
---

{{< reuse "kgw-docs/snippets/kgateway-capital.md" >}} follows the Kubernetes Gateway API specification for route matching precedence. Understanding this ordering is important when you have multiple HTTPRoutes with overlapping matchers that are attached to the same listener.

## Specificity-based ordering {#ordering}

For all non-regex matchers, the Gateway API specification requires implementations to apply a specificity-based sort. Routes are ordered according to the following criteria that are evaluated in sequence:

| Priority | Criterion | Rule |
|---|---|---|
| 1 (highest) | Path match type | `Exact` before `PathPrefix` before `RegularExpression` matching |
| 2 | Prefix length | Longer `PathPrefix` wins |
| 3 | Method match | Route with a method match wins over a route without a method match |
| 4 | Header match count | More header matchers wins |
| 5 | Query param match count | More query param matchers wins |

This ordering applies across all routes from all HTTPRoutes that are attached to the same listener. A route with a longer prefix always takes precedence over a shorter one, regardless of which HTTPRoute it was defined in or in what order the HTTPRoutes were created.

## Tiebreakers

### Within a single HTTPRoute

When two rules within the same HTTPRoute are equally specific by all [specificity-based ordering criteria](#ordering), the rule that appears first in the `rules` list takes precedence. 

The following example specifies two route rules. Both rules use a `PathPrefix` match of the same length (`/api` and `/app`), so neither is more specific than the other. Because they are equally specific, rule 1 takes precedence over rule 2, because it appears first in the list.

```yaml
spec:
  rules:
    - matches:
        - path:
            type: PathPrefix
            value: /api    # rule 1 — same specificity, wins because it appears first
    - matches:
        - path:
            type: PathPrefix
            value: /app    # rule 2 — same prefix length, evaluated second
```

### Across HTTPRoutes

When two routes from different HTTPRoute objects are equally specific by all criteria, rules are ordered as follows: 

1. **Oldest creation timestamp**: The rule in the older HTTPRoute wins.
2. **Alphabetical `{namespace}/{name}` order**: If the HTTPRoutes have the same timestamp, rules are ordered alphabetically by namespace and name. 

## Regex match ordering

The Gateway API specification does not define a specificity ordering for `RegularExpression` path matches. Regex patterns cannot be reliably ranked by specificity from their string representation alone.

Regex routes are always placed after `Exact` and `PathPrefix` routes (see [Specificity-based ordering](#ordering)). However, when multiple regex routes match the same request, the winner is determined by the same tiebreakers that are used for equally-specific routes:

- **Within the same HTTPRoute**: The rule list position determines route precedence. The first matching rule in the list wins.
- **Across HTTPRoutes**: Route order is first determined by the HTTPRoute's creation timestamp, with older HTTPRoutes taking priority. If the HTTPRoute resources were created with the same timestamp, HTTPRoutes are orderd alphabetically by `{namespace}/{name}`. 

Consider the following two overlapping regex patterns: 
* `/api/homepage-beta-flag.*` (more specific)
* `/api/homepage.*` (broader). 

Even though one is more specific, {{< reuse "kgw-docs/snippets/kgateway-capital.md" >}} does not automatically rank them by specificity. The pattern that wins depends on the list position (if within the same HTTPRoute), or creation timestamp and HTTPRoute name (if multiple HTTPRoutes). 

### Configure ordering for overlapping regex matchers

You can choose between the following approaches to configure the order for overlapping regex matchers. 

- **Keep overlapping regex rules in a single HTTPRoute.** Within a single HTTPRoute, regex matchers are ordered by their position in the route rule list. You can place more specific patterns before broader ones.

  ```yaml
  spec:
    rules:
      - matches:
          - path:
              type: RegularExpression
              value: /api/homepage-beta-flag.*   # more specific — list first
      - matches:
          - path:
              type: RegularExpression
              value: /api/homepage.*              # broader — list second
  ```

- **Use the `kgateway.dev/route-weight` annotation** to assign explicit precedence when overlapping regex routes exist in separate HTTPRoute resources. For more information, see [Weighted routes]({{< link-hextra path="/traffic-management/weighted-routes/" >}}).

## Override route precedence with weights

{{< reuse "kgw-docs/snippets/kgateway-capital.md" >}} supports an explicit weight-based override for route precedence via the `kgateway.dev/route-weight` annotation. When applied to an HTTPRoute, this annotation causes the route to be sorted by weight before any Gateway API specificity criteria are applied. Higher weight values take precedence.

```yaml
apiVersion: gateway.networking.k8s.io/v1
kind: HTTPRoute
metadata:
  name: route-specific
  annotations:
    kgateway.dev/route-weight: "10"
spec:
  rules:
    - matches:
        - path:
            type: RegularExpression
            value: /api/homepage-beta-flag.*
```

> [!IMPORTANT]
> The `kgateway.dev/route-weight` annotation requires the `KGW_WEIGHTED_ROUTE_PRECEDENCE` feature flag to be enabled on the kgateway controller. For more information, see [Weighted routes]({{< link-hextra path="/traffic-management/weighted-routes/" >}}).
