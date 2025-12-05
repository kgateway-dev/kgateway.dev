---
title: Kgateway policies
weight:
description: Learn how policy inheritance and overrides work for kgateway policies in a route delegation setup.
---

Learn how policy inheritance and overrides work for {{< reuse "/docs/snippets/kgateway.md" >}} policies in a route delegation setup.

{{< callout type="info" >}} 
Want to learn more about policy inheritance and overrides for Kubernetes Gateway API-native policies? See [Native Gateway API policies](/docs/traffic-management/route-delegation/inheritance/native-policies/). 
{{< /callout >}}

{{< callout type="warning" >}} 
{{< reuse "docs/versions/warn-2-1-only.md" >}} 
{{< /callout >}}

## About policy inheritance

{{< reuse "docs/snippets/policy-inheritance.md" >}}

## Configuration overview

In this guide you walk through a route delegation example where a child HTTPRoute inherits or overrides policies that are set on a parent HTTPRoute. 

The following image illustrates the route delegation hierarchy and policy inheritance:

{{< reuse-image src="img/route-delegation-inheritance-kgateway.svg" >}}
{{< reuse-image-dark srcDark="img/route-delegation-inheritance-kgateway-dark.svg" >}}
<!-- https://app.excalidraw.com/s/AKnnsusvczX/9uktq3x1i63-->

**Parent HTTPRoutes**:

| HTTPRoute | Delegation | Policy merge strategy |
| --- | --- | --- |
| `parent1` | Delegates to the `child-team1` HTTPRoute in `team1` namespace on the `/anything/team1` prefix path for the `delegation-parent1.example` domain. | `ShallowMergePreferParent`, so that policies of the parent HTTPRoute override the policies of the child HTTPRoute. |
| `parent2` | Delegates to the `child-team1` HTTPRoute in `team1` namespace on the `/anything/team1` prefix path for the `delegation-parent2.example` domain. | `ShallowMergePreferChild`, (the default behavior) so that policies of the child HTTPRoute override the policies of the parent HTTPRoute. |

**Child HTTPRoute**:

| HTTPRoute | Delegation | Policy merge strategy |
| --- | --- | --- |
| `child-team1` | Matches incoming traffic for the `/anything/team1/foo` prefix path and routes that traffic to the httpbin app in the `team1` namespace. | Policies are merged depending on the parent HTTPRoute's policy merge strategy for the delegated route. |

**TrafficPolicies**:

| TrafficPolicy | TargetRefs | Description |
| --- | --- | --- |
| Transformation Policy 1 | `parent1` and `parent2` HTTPRoutes | Policy 1 is inherited for the `delegation-parent1.example` domain, but overridden by the child policy for the `delegation-parent2.example` domains. |
| Local rate limit Policy 2 | `parent1` and `parent2` HTTPRoutes | Policy 2 is inherited by both delegated routes because the child does not override the parent policy. |
| Transformation Policy 3 | `child-team1` HTTPRoute | Policy 3 does not apply to the `delegation-parent1.example` domain because that route's annotation overrides the default child inheritance with the `ShallowMergePreferParent` annotation. However, Policy 3 applies to the `delegation-parent2.example` domain because the child policy merge strategy is the default `ShallowMergePreferChild`. |

## Before you begin

{{< reuse "docs/snippets/prereq-delegation.md" >}}

## Setup 

1. Create the `parent1` HTTPRoute resource that matches incoming traffic on the `delegation-parent1.example` domain. The HTTPRoute resource specifies the following route:
   * `/anything/team1`: The routing decision is delegated to a child HTTPRoute resource in the `team1` namespace.
   * `kgateway.dev/inherited-policy-priority: ShallowMergePreferParent`: Overrides the default policy inheritance behavior so that parent policies take precedence over child policies.

   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.networking.k8s.io/v1
   kind: HTTPRoute
   metadata:
     name: parent1
     namespace: {{< reuse "docs/snippets/namespace.md" >}}
     annotations:
      kgateway.dev/inherited-policy-priority: ShallowMergePreferParent
   spec:
     parentRefs:
     - name: http
       namespace: {{< reuse "docs/snippets/namespace.md" >}}
     hostnames:
     - "delegation-parent1.example"
     rules:
     - matches:
       - path:
           type: PathPrefix
           value: /anything/team1
       backendRefs:
       - group: gateway.networking.k8s.io
         kind: HTTPRoute
         name: "*"
         namespace: team1
   EOF
   ```

2. Create the `parent2` HTTPRoute resource that matches incoming traffic on the `delegation-parent2.example` domain.
   * `anything/team1`: The routing decision is delegated to the same child HTTPRoute resource in the `team1` namespace.
   * `kgateway.dev/inherited-policy-priority: ShallowMergePreferChild`: Keeps the default behavior, so that policies of the child HTTPRoute override the policies of the parent HTTPRoute.

   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.networking.k8s.io/v1
   kind: HTTPRoute
   metadata:
     name: parent2
     namespace: {{< reuse "docs/snippets/namespace.md" >}}
     annotations:
      delegation.kgateway.dev/inherited-policy-priority: PreferChild
   spec:
     parentRefs:
     - name: http
       namespace: {{< reuse "docs/snippets/namespace.md" >}}
     hostnames:
     - "delegation-parent2.example"
     rules:
     - matches:
       - path:
           type: PathPrefix
           value: /anything/team1
       backendRefs:
       - group: gateway.networking.k8s.io
         kind: HTTPRoute
         name: "*"
         namespace: team1
   EOF
   ```

3. Create a TrafficPolicy that defines the following policies: 
   * **Transformation policy**: The `x-parent-policy: This policy is inherited from the parent.` header is set on any request.
   * **Local rate limiting**: Requests to the routes are limited to 1 request per minute. 

   The TrafficPolicy is applied to the `parent1` and `parent2` HTTPRoutes by using the `targetRefs` option. 
   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.kgateway.dev/v1alpha1
   kind: TrafficPolicy
   metadata:
     name: parent-policy
     namespace: {{< reuse "docs/snippets/namespace.md" >}}
   spec:
     targetRefs:
     - group: gateway.networking.k8s.io
       kind: HTTPRoute
       name: parent1
     - group: gateway.networking.k8s.io
       kind: HTTPRoute
       name: parent2
     transformation:
       request:
         set:
           - name: x-parent-policy
             value: This policy is inherited from the parent.
     rateLimit:
       local:
         tokenBucket:
           maxTokens: 1
           tokensPerFill: 1
           fillInterval: 60s
   EOF
   ```

4. Create the child HTTPRoute resource for the `team1` namespace that matches traffic on the `/anything/team1/foo` prefix and routes traffic to the httpbin app in the `team1` namespace. 
   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.networking.k8s.io/v1
   kind: HTTPRoute
   metadata:
     name: child-team1
     namespace: team1
   spec:
     rules:
     - matches:
       - path:
           type: PathPrefix
           value: /anything/team1/foo
       backendRefs:
       - name: httpbin
         port: 8000
   EOF
   ```

5. Create a TrafficPolicy that defines a custom transformation policy for the `child-team1` HTTPRoute. The policy sets the `x-child-team1: This is the child-team1 policy.` request header. 
   ```yaml 
   kubectl apply -f- <<EOF
   apiVersion: gateway.kgateway.dev/v1alpha1
   kind: TrafficPolicy
   metadata:
     name: child-policy
     namespace: team1
   spec:
     targetRefs:
     - group: gateway.networking.k8s.io
       kind: HTTPRoute
       name: child-team1
     transformation:
       request:
         set:
           - name: x-child-team1
             value: This is the child-team1 policy.
   EOF
   ```

6. Send a request to the httpbin app on the `delegation.parent1.example` domain. Because the `parent1` HTTPRoute annotation lets parent policies override the child policies, the child HTTPRoute inherits the policies that are set on the `parent1` HTTPRoute. The TrafficPolicy that you created earlier and applied to the `child-team1` HTTPRoute is ignored. Verify that you see the `X-Parent-Policy` header in your response.
   {{< tabs items="Cloud Provider LoadBalancer,Port-forward for local testing" tabTotal="2" >}}
   {{% tab tabName="Cloud Provider LoadBalancer" %}}
   ```sh
   curl -i http://$INGRESS_GW_ADDRESS:8080/anything/team1/foo \
   -H "host: delegation-parent1.example:8080" 
   ```
   {{% /tab %}}
   {{% tab tabName="Port-forward for local testing" %}}
   ```sh
   curl -i localhost:8080/anything/team1/foo \
   -H "host: delegation-parent1.example" 
   ```
   {{% /tab %}}
   {{< /tabs >}}

   Example output: 
   ```console {hl_lines=[20,21]}
   HTTP/1.1 200 OK
   access-control-allow-credentials: true
   access-control-allow-origin: *
   content-type: application/json; encoding=utf-8
   ...

   {
     "args": {},
     "headers": {
       "Accept": [
         "*/*"
       ],
       "Host": [
         "delegation-parent1.example:8080"
       ],
       "User-Agent": [
         "curl/8.7.1"
       ],
    ...
       "X-Parent-Policy": [
         "This policy is inherited from the parent."
       ],
       "X-Request-Id": [
         "db2affa4-2d03-4ee7-8624-75c3f9b40889"
       ]
     },
     "origin": "10.X.XX.XXX",
     "url": "http://delegation-parent1.example:8080/anything/team1/foo",
     "data": "",
     "files": null,
     "form": null,
    "json": null
   }
   ```

7. Send another request to the `delegation.parent1.example` domain. Verify that this time the request is rate limited and a 429 HTTP response is returned, because only 1 request is allowed in a 60 second timeframe. 
   {{< tabs items="Cloud Provider LoadBalancer,Port-forward for local testing" tabTotal="2" >}}
   {{% tab tabName="Cloud Provider LoadBalancer" %}}
   ```sh
   curl -i http://$INGRESS_GW_ADDRESS:8080/anything/team1/foo \
   -H "host: delegation-parent1.example:8080" 
   ```
   {{% /tab %}}
   {{% tab tabName="Port-forward for local testing" %}}
   ```sh
   curl -i localhost:8080/anything/team1/foo \
   -H "host: delegation-parent1.example" 
   ```
   {{% /tab %}}
   {{< /tabs >}}

   Example output: 
   ```console
   HTTP/1.1 429 Too Many Requests
   content-length: 18
   content-type: text/plain
   date: Fri, 06 Jun 2025 15:43:43 GMT
   server: envoy

   local_rate_limited%
   ```     

8. Send a request to the `delegation.parent2.example` domain. Because the `parent2` HTTPRoute annotation keeps the default policy merging behavior, the child HTTPRoute overrides any top-level policies that are defined on `parent2`. Policies that are not overridden are still inherited from the parent and applied to the child HTTPRoute. 

   Verify that you see the custom `X-Child-Team1` header in your response. 
   {{< tabs items="Cloud Provider LoadBalancer,Port-forward for local testing" tabTotal="2" >}}
   {{% tab tabName="Cloud Provider LoadBalancer" %}}
   ```sh
   curl -i http://$INGRESS_GW_ADDRESS:8080/anything/team1/foo \
   -H "host: delegation-parent2.example:8080" 
   ```
   {{% /tab %}}
   {{% tab tabName="Port-forward for local testing" %}}
   ```sh
   curl -i localhost:8080/anything/team1/foo \
   -H "host: delegation-parent2.example" 
   ```
   {{% /tab %}}
   {{< /tabs >}}

   Example output: 
   ```console {hl_lines=[18,19]}
   HTTP/1.1 200 OK
   access-control-allow-credentials: true
   access-control-allow-origin: *
   content-type: application/json; encoding=utf-8
   ...
   { 
     "args": {},
     "headers": {
       "Accept": [
         "*/*"
       ],
       "Host": [
         "delegation-parent2.example:8080"
       ],
       "User-Agent": [
         "curl/8.7.1"
       ],
       "X-Child-Team1": [
         "This is the child-team1 policy."
       ],
       "X-Envoy-Expected-Rq-Timeout-Ms": [
         "15000"
       ],
      ...
     "origin": "10.X.X.XXX",
     "url": "http://delegation-parent2.example:8080/anything/team1/foo",
     "data": "",
     "files": null,
     "form": null,
     "json": null
   }
   ```

9. Send another request to the `delegation.parent2.example` domain. Because the child HTTPRoute does not define any rate limiting policies, it inherits the rate limiting policy of `parent2`. Verify that the request is rate limited and a 429 HTTP response is returned, because only 1 request is allowed in a 60 second timeframe. 
   {{< tabs items="Cloud Provider LoadBalancer,Port-forward for local testing" tabTotal="2" >}}
   {{% tab tabName="Cloud Provider LoadBalancer" %}}
   ```sh
   curl -i http://$INGRESS_GW_ADDRESS:8080/anything/team1/foo \
   -H "host: delegation-parent2.example:8080" 
   ```
   {{% /tab %}}
   {{% tab tabName="Port-forward for local testing" %}}
   ```sh
   curl -i localhost:8080/anything/team1/foo \
   -H "host: delegation-parent2.example" 
   ```
   {{% /tab %}}
   {{< /tabs >}}

   Example output: 
   ```console
   HTTP/1.1 429 Too Many Requests
   content-length: 18
   content-type: text/plain
   date: Fri, 06 Jun 2025 15:43:43 GMT
   server: envoy

   local_rate_limited%
   ``` 

## Cleanup

{{< reuse "docs/snippets/cleanup.md" >}}

```sh
kubectl delete gateway http -n {{< reuse "docs/snippets/namespace.md" >}}
kubectl delete httproute parent1 -n {{< reuse "docs/snippets/namespace.md" >}}
kubectl delete httproute parent2 -n {{< reuse "docs/snippets/namespace.md" >}}
kubectl delete httproute child-team1 -n team1
kubectl delete trafficpolicy parent-policy -n {{< reuse "docs/snippets/namespace.md" >}}
kubectl delete trafficpolicy child-policy -n team1 
kubectl delete -n team1 -f https://raw.githubusercontent.com/kgateway-dev/kgateway.dev/main/assets/docs/examples/httpbin.yaml
kubectl delete -n team2 -f https://raw.githubusercontent.com/kgateway-dev/kgateway.dev/main/assets/docs/examples/httpbin.yaml
kubectl delete namespaces team1 team2
```
