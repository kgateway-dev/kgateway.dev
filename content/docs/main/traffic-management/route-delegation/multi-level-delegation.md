---
title: Multi-level delegation
weight: 30
description: Create a 3-level route delegation hierarchy with a parent, child, and grandchild HTTPRoute resource.
---

Create a 3-level route delegation hierarchy with a parent, child, and grandchild HTTPRoute resource.

{{< callout >}}
{{< reuse "docs/snippets/proxy-kgateway.md" >}}
{{< /callout >}}

## Configuration overview

In this guide you walk through a route delegation example that demonstrates route delegation from a parent HTTPRoute resource to a child HTTPRoute resource, and from a child HTTPRoute resource to a grandchild HTTPRoute resource. The following image illustrates the route delegation hierarchy:

{{< reuse-image src="img//route-delegation-multi-level.svg" >}} 
{{< reuse-image-dark srcDark="img//route-delegation-multi-level-dark.svg" >}} 

**`parent` HTTPRoute**: 
* The parent HTTPRoute resource `parent` delegates traffic as follows: 
  * `/anything/team1` delegates traffic to the child HTTPRoute resource `child-team1` in namespace `team1`. 
  * `/anything/team2` delegates traffic to the child HTTPRoute resource `child-team2` in namespace `team2`. 
  
**`child-team1` HTTPRoute**: 
* The child HTTPRoute resource `child-team1` matches incoming traffic for the `/anything/team1/foo` prefix path and routes that traffic to the httpbin app in the `team1` namespace. 

**`child-team2` HTTPRoute**: 
* The child HTTPRoute resource `child-team2` delegates traffic on the `/anything/team2/grandchild` to a grandchild HTTPRoute resource in the `team2` namespace. 

**`grandchild` HTTPRoute**: 
* The grandchild HTTPRoute resource `grandchild-team2` matches incoming traffic for the `/anything/team2/grandchild/.*` regex path and routes that traffic to the httpbin app in the `team2` namespace. 

## Before you begin

{{< reuse "docs/snippets/prereq-delegation.md" >}}

## Setup

1. Create the parent HTTPRoute resource that matches incoming traffic on the `delegation.example` domain. The HTTPRoute resource specifies two routes: 
   * `/route1/team1`: The routing decision is delegated to a child HTTPRoute resource in the `team1` namespace. 
   * `/route2/team2`: The routing decision is delegated to a child HTTPRoute resource in the `team2` namespace. 
   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.networking.k8s.io/v1
   kind: HTTPRoute
   metadata:
     name: parent
     namespace: {{< reuse "docs/snippets/namespace.md" >}}
   spec:
     hostnames:
     - delegation.example
     parentRefs:
     - name: http
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
     - matches:
       - path:
           type: PathPrefix
           value: /anything/team2
       backendRefs:
       - group: gateway.networking.k8s.io
         kind: HTTPRoute
         name: "*"
         namespace: team2
   EOF
   ```

2. Create the `child-team1` HTTPRoute resource in the `team1` namespace that matches traffic on the `/anything/team1/foo` prefix and routes traffic to the httpbin app in the `team1` namespace. The child HTTPRoute resource does not select a specific parent HTTPRoute resource. Because of that, the child HTTPRoute resource is automatically selected by all parent HTTPRoute resources that delegate traffic to this child. 
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

3. Create the `child-team2` HTTPRoute resource in the `team2` namespace that matches traffic on the `/anything/team2/grandchild/` prefix and delegates traffic to an HTTPRoute resource in the `team2` namespace. Note that because the child delegates traffic to a grandchild, a `PathPrefix` matcher must be used. 
   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.networking.k8s.io/v1
   kind: HTTPRoute
   metadata:
     name: child-team2
     namespace: team2
   spec:
     rules:
     - matches:
       - path:
           type: PathPrefix
           value: /anything/team2/grandchild/
       backendRefs:
       - group: gateway.networking.k8s.io
         kind: HTTPRoute
         name: "*"
         namespace: team2
   EOF
   ```

4. Create a grandchild HTTPRoute resource that matches traffic on the `/anything/team2/grandchild/.*` regex path and routes traffic to the httpbin app in the `team2` namespace. 
   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.networking.k8s.io/v1
   kind: HTTPRoute
   metadata:
     name: grandchild
     namespace: team2
   spec:
     rules:
     - matches:
       - path:
           type: RegularExpression
           value: /anything/team2/grandchild/.*
       backendRefs:
       - name: httpbin
         port: 8000
   EOF
   ```
   
6. Send a request to the `delegation.example` domain along the `/anything/team1/foo` path. Verify that you get back a 200 HTTP response code. 
   {{< tabs items="Cloud Provider LoadBalancer,Port-forward for local testing" tabTotal="2" >}}
   {{% tab tabName="Cloud Provider LoadBalancer" %}}
   ```sh
   curl -i http://$INGRESS_GW_ADDRESS:8080/anything/team1/foo \
   -H "host: delegation.example"
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
   ```
   HTTP/1.1 200 OK
   access-control-allow-credentials: true
   access-control-allow-origin: *
   content-type: application/json; encoding=utf-8
   date: Mon, 06 May 2024 15:59:32 GMT
   x-envoy-upstream-service-time: 0
   server: envoy
   transfer-encoding: chunked
   ```
   
7. Send another request to the `delegation.example` domain along the `/anything/team1/bar` path. Verify that you get back a 404 HTTP response code, because this route is not specified in the child HTTPRoute resource `child-team1`. 
   {{< tabs items="Cloud Provider LoadBalancer,Port-forward for local testing" tabTotal="2" >}}
   {{% tab tabName="Cloud Provider LoadBalancer" %}}
   ```sh
   curl -i http://$INGRESS_GW_ADDRESS:8080/anything/team1/bar \
   -H "host: delegation.example"
   ```
   {{% /tab %}}
   {{% tab tabName="Port-forward for local testing" %}}
   ```sh
   curl -i localhost:8080/anything/team1/bar \
   -H "host: delegation.example"
   ```
   {{% /tab %}}
   {{< /tabs >}}

   Example output: 
   ```
   HTTP/1.1 404 Not Found
   date: Mon, 06 May 2024 16:01:48 GMT
   server: envoy
   transfer-encoding: chunked
   ```

8. Send another request to the `delegation.example` domain. This time, you use the `/anything/team2/grandchild/bar` path that is configured on the `grandchild` HTTPRoute resource. Verify that you get back a 200 HTTP response code.
   {{< tabs items="Cloud Provider LoadBalancer,Port-forward for local testing" tabTotal="2" >}}
   {{% tab tabName="Cloud Provider LoadBalancer" %}}
   ```sh
   curl -i http://$INGRESS_GW_ADDRESS:8080/anything/team2/grandchild/bar \
   -H "host: delegation.example"
   ```
   {{% /tab %}}
   {{% tab tabName="Port-forward for local testing" %}}
   ```sh
   curl -i localhost:8080/anything/team2/grandchild/bar \
   -H "host: delegation.example"
   ```
   {{% /tab %}}
   {{< /tabs >}}

   Example output: 
   ```
   HTTP/1.1 200 OK
   access-control-allow-credentials: true
   access-control-allow-origin: *
   content-type: application/json; encoding=utf-8
   date: Mon, 06 May 2024 15:59:32 GMT
   x-envoy-upstream-service-time: 0
   server: envoy
   transfer-encoding: chunked
   ```

9. Send another request to the `delegation.example` domain along the `/anything/team2/grandchild/foo` path. Because the grandchild HTTPRoute resource uses a regular expression to match incoming traffic, you can use any valid endpoint in the httpbin app to route traffic to the httpbin app in the `team2` namespace.  
   {{< tabs items="Cloud Provider LoadBalancer,Port-forward for local testing" tabTotal="2" >}}
   {{% tab tabName="Cloud Provider LoadBalancer" %}}
   ```sh
   curl -i http://$INGRESS_GW_ADDRESS:8080/anything/team2/grandchild/foo \
   -H "host: delegation.example"
   ```
   {{% /tab %}}
   {{% tab tabName="Port-forward for local testing" %}}
   ```sh
   curl -i localhost:8080/anything/team2/grandchild/foo \
   -H "host: delegation.example"
   ```
   {{% /tab %}}
   {{< /tabs >}}

   Example output: 
   ```
   HTTP/1.1 200 OK
   access-control-allow-credentials: true
   access-control-allow-origin: *
   content-type: application/json; encoding=utf-8
   date: Mon, 06 May 2024 15:59:32 GMT
   x-envoy-upstream-service-time: 0
   server: envoy
   transfer-encoding: chunked
   ```

## Cleanup

{{< reuse "docs/snippets/cleanup.md" >}}

```sh
kubectl delete gateway http -n {{< reuse "docs/snippets/namespace.md" >}}
kubectl delete httproute parent -n {{< reuse "docs/snippets/namespace.md" >}}
kubectl delete httproute child-team1 -n team1
kubectl delete httproute child-team2 -n team2
kubectl delete httproute grandchild -n team2
kubectl delete -n team1 -f https://raw.githubusercontent.com/kgateway-dev/kgateway.dev/main/assets/docs/examples/httpbin.yaml
kubectl delete -n team2 -f https://raw.githubusercontent.com/kgateway-dev/kgateway.dev/main/assets/docs/examples/httpbin.yaml
kubectl delete namespaces team1 team2
```

   