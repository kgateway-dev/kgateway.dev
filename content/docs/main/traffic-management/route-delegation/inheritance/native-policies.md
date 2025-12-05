---
title: Native Gateway API policies
weight: 80
description: Learn how policy inheritance works in a route delegation setup. 
---

Learn how policy inheritance and overrides work for Kubernetes Gateway API-native policies in a route delegation setup. 

{{< callout type="info" >}} 
Want to learn more about policy inheritance and overrides for {{< reuse "/docs/snippets/kgateway.md" >}} policies? See [{{< reuse "/docs/snippets/kgateway.md" >}} policies](/docs/traffic-management/route-delegation/inheritance/kgateway-policies/). 
{{< /callout >}}
{{< callout type="warning" >}} 
{{< reuse "docs/versions/warn-2-1-only.md" >}} 
{{< /callout >}}

## About policy inheritance

{{< reuse "docs/snippets/policy-inheritance-native.md" >}}

## Configuration overview

In this guide you walk through a route delegation example where a child HTTPRoute inherits or overrides policies that are set on a parent HTTPRoute. 

The following image illustrates the route delegation hierarchy and policy inheritance:

{{< reuse-image src="img/route-delegation-inheritance-native.svg" width="700px" >}}
{{< reuse-image-dark srcDark="img/route-delegation-inheritance-native-dark.svg" width="700px" >}}
<!-- https://app.excalidraw.com/s/AKnnsusvczX/9uktq3x1i63-->

**`parent` HTTPRoute**: 
* The `parent` HTTPRoute resource delegates traffic as follows: 
  * Requests to`/anything/team1` are delegated to the child HTTPRoute resource `child-team1` in namespace `team1`. A timeout policy of 10s is defined on this route.
  * Requests to `/anything/team2` are delegated to the child HTTPRoute resource `child-team2` in namespace `team2`. A timeout policy of 20s is defined on this route.

**`child-team1` HTTPRoute**: 
* The child HTTPRoute resource `child-team1` matches incoming traffic for the `/anything/team1/foo` prefix path and routes that traffic to the httpbin app in the `team1` namespace. 
* The `child-team1` resource does not define any custom timeout policies. Because of that, the timeout policy that is set on the parent is automatically inherited and enforced. 

**`child-team2` HTTPRoute**: 
* The child HTTPRoute resource `child-team2` delegates traffic on the `/anything/team2/bar` path to a grandchild HTTPRoute resource in the `team2` namespace. 
* The `child-team2` resource defines a custom timeout policy. Because of that, the timeout policy on the parent is ignored and only the timeout policy on the `child-team2` resource is enforced. 

## Before you begin

{{< reuse "docs/snippets/prereq-delegation.md" >}}

## Setup

1. Create the parent HTTPRoute resource that matches incoming traffic on the `delegation.example` domain. The HTTPRoute resource specifies two routes and defines a timeout policy for each of the routes:
   * `/anything/team1`: The routing decision is delegated to a `child-team1` HTTPRoute resource in the `team1` namespace. A timeout policy of 10s is defined on this route.
   * `/anything/team2`: The routing decision is delegated to a `child-team2` HTTPRoute resource in the `team2` namespace. A timeout policy of 20s is defined on this route.

   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.networking.k8s.io/v1
   kind: HTTPRoute
   metadata:
    name: parent
    namespace: {{< reuse "docs/snippets/namespace.md" >}}
   spec:
    parentRefs:
    - name: http
    hostnames:
     - "delegation.example"
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
      timeouts:
        request: 10s
    - matches:
      - path:
          type: PathPrefix
          value: /anything/team2
      backendRefs:
      - group: gateway.networking.k8s.io
        kind: HTTPRoute
        name: "*"
        namespace: team2
      timeouts:
        request: 20s
   EOF
   ```

2. Create the `child-team1` HTTPRoute resource in the `team1` namespace that matches traffic on the `/anything/team1/foo` prefix and routes traffic to the httpbin app in the `team1` namespace. The child HTTPRoute resource does not define any timeout policies. Because of that, the HTTPRoute inherits the timeout setting of the `parent`.
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

3. Create the `child-team2` HTTPRoute resource in the `team2` namespace that specifies a custom timeout policy and matches traffic on the `/anything/team2/bar/` prefix. The custom timeout policy overrides the timeout policy that is set on the `parent`. 
   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.networking.k8s.io/v1
   kind: HTTPRoute
   metadata:
     name: child-team2
     namespace: team2
   spec:
     parentRefs:
     - name: parent
       namespace: {{< reuse "docs/snippets/namespace.md" >}}
       group: gateway.networking.k8s.io
       kind: HTTPRoute
     rules:
     - matches:
       - path:
           type: PathPrefix
           value: /anything/team2/bar
       backendRefs:
       - name: httpbin
         port: 8000
       timeouts: 
         request: 30s
   EOF
   ```

4. Send a request to the `delegation.example` domain along the `/anything/team1/foo` path. Verify that you get back a 200 HTTP response code and that the `X-Envoy-Expected-Rq-Timeout-Ms` header is set to 10000 milliseconds (10s) as defined on the `parent` HTTPRoute.
   {{< tabs items="Cloud Provider LoadBalancer,Port-forward for local testing" tabTotal="2" >}}
   {{% tab tabName="Cloud Provider LoadBalancer" %}}
   ```sh
   curl -i http://$INGRESS_GW_ADDRESS:8080/anything/team1/foo \
   -H "host: delegation.example:8080" 
   ```
   {{% /tab %}}
   {{% tab tabName="Port-forward for local testing" %}}
   ```sh
   curl -i localhost:8080/anything/team1/foo \
   -H "host: delegation.example" 
   ```
   {{% /tab %}}
   {{< /tabs >}}

   Example output: 
   ```console {hl_lines=[21,22]}
   HTTP/1.1 200 OK
   access-control-allow-credentials: true
   access-control-allow-origin: *
   content-type: application/json; encoding=utf-8
   content-length: 509
   x-envoy-upstream-service-time: 0
   server: envoy

   {
     "args": {},
     "headers": {
       "Accept": [
         "*/*"
       ],
       "Host": [
         "delegation.example:8080"
       ],
       "User-Agent": [
         "curl/8.7.1"
       ],
       "X-Envoy-Expected-Rq-Timeout-Ms": [
         "10000"
       ],
       "X-Forwarded-Proto": [
         "http"
       ],
       "X-Request-Id": [
        "65927858-2c6b-42ae-9278-8ff9d8bba3f8"
       ]
     },
     "origin": "10.0.64.27:49526",
     "url": "http://delegation.example:8080/anything/team1/foo",
     "data": "",
     "files": null,
     "form": null,
     "json": null
   }
   ```

5. Send a request to the `delegation.example` domain along the `/anything/team2/bar` path. Verify that you get back a 200 HTTP response code and that the `X-Envoy-Expected-Rq-Timeout-Ms` header is set to 30000 milliseconds (30s) as defined on the `child-team2` HTTPRoute. The timeout setting of 20s that was defined on the `parent` was not applied and overridden by the timeout setting of 30s on the `child-team2` HTTPRoute. 
   {{< tabs items="Cloud Provider LoadBalancer,Port-forward for local testing" tabTotal="2" >}}
   {{% tab tabName="Cloud Provider LoadBalancer" %}}
   ```sh
   curl -i http://$INGRESS_GW_ADDRESS:8080/anything/team2/bar \
   -H "host: delegation.example:8080" 
   ```
   {{% /tab %}}
   {{% tab tabName="Port-forward for local testing" %}}
   ```sh
   curl -i localhost:8080/anything/team2/bar \
   -H "host: delegation.example:8080" 
   ```
   {{% /tab %}}
   {{< /tabs >}}

   Example output: 
   ```console {hl_lines=[21,22]}
   HTTP/1.1 200 OK
   access-control-allow-credentials: true
   access-control-allow-origin: *
   content-type: application/json; encoding=utf-8
   content-length: 509
   x-envoy-upstream-service-time: 1
   server: envoy

   {
     "args": {},
     "headers": {
       "Accept": [
        "*/*"
       ],
       "Host": [
         "delegation.example:8080"
       ],
       "User-Agent": [
         "curl/8.7.1"
       ],
       "X-Envoy-Expected-Rq-Timeout-Ms": [
         "30000"
       ],
       "X-Forwarded-Proto": [
         "http"
       ],
       "X-Request-Id": [
         "d645dc37-5326-4b69-8c2c-4060e12ca4ff"
       ]
     },
     "origin": "10.0.64.27:53026",
     "url": "http://delegation.example:8080/anything/team2/bar",
     "data": "",
     "files": null,
     "form": null,
     "json": null
   }
   ```

## Cleanup

{{< reuse "docs/snippets/cleanup.md" >}}

```sh
kubectl delete gateway http -n {{< reuse "docs/snippets/namespace.md" >}}
kubectl delete httproute parent -n {{< reuse "docs/snippets/namespace.md" >}}
kubectl delete httproute child-team1 -n team1
kubectl delete httproute child-team2 -n team2
kubectl delete -n team1 -f https://raw.githubusercontent.com/kgateway-dev/kgateway.dev/main/assets/docs/examples/httpbin.yaml
kubectl delete -n team2 -f https://raw.githubusercontent.com/kgateway-dev/kgateway.dev/main/assets/docs/examples/httpbin.yaml
kubectl delete namespaces team1 team2
```