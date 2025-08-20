---
title: Multiple parents
weight: 20
description: Set up route delegation for a child HTTPRoute resource that can receive traffic from one or more parent HTTPRoute resources. 
---

Set up route delegation for a child HTTPRoute resource that can receive traffic from one or more parent HTTPRoute resources.

## Configuration overview

In this guide you walk through a route delegation example that demonstrates route delegation between two parent HTTPRoute and two child HTTPRoute resources that forward traffic to an httpbin sample app. The following image illustrates the route delegation hierarchy:

{{< reuse-image src="img/route-delegation-multi-parent.svg" >}} 
{{< reuse-image-dark srcDark="img/route-delegation-multi-parent-dark.svg" >}} 

**`parent1` and `parent2` HTTPRoutes**: 
* The parent HTTPRoute resource `parent1` serves traffic for the `delegation-parent1.example` domain. 
* The parent HTTPRoute resource `parent2` serves traffic for the `delegation-parent2.example` domain. 
* Both parent HTTPRoute resources have routes that delegate traffic as follows: 
  * `/anything/team1` delegates traffic to the child HTTPRoute resource `child-team1` in namespace `team1`. 
  * `/anything/team2` delegates traffic to the child HTTPRoute resource `child-team2` in namespace `team2`. 

**`child-team1` HTTPRoute**: 
* The child HTTPRoute resource `child-team1` matches incoming traffic for the `/anything/team1/foo` prefix path and routes that traffic to the httpbin app in namespace `team1`. The resource does not select any parent HTTPRoute resource in the `parentRef` section. Both parent HTTPRoute resources can therefore delegate traffic to this child HTTPRoute resource. 

**`child-team2` HTTPRoute**: 
* The child HTTPRoute resource `child-team2` matches incoming traffic for the `/anything/team2/bar` exact prefix path and routes that traffic to the httpbin app in namespace `team2`. The resource selects the `parent1` HTTPRoute resource in the `parentRef` section. Because of that, only the `parent1` HTTPRoute resource can delegate traffic to this child HTTPRoute resource. The `parent2` HTTPRoute resource cannot delegate traffic to this child. 

## Before you begin

{{< reuse "docs/snippets/prereq-delegation.md" >}}

## Setup

1. Create the `parent1` HTTPRoute resource that matches incoming traffic on the `delegation-parent1.example` domain. The HTTPRoute resource specifies two routes: 
   * `/anything/team1`: The routing decision is delegated to a child HTTPRoute resource in the `team1` namespace. 
   * `/anything/team2`: The routing decision is delegated to a child HTTPRoute resource in the `team2` namespace. 
   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.networking.k8s.io/v1
   kind: HTTPRoute
   metadata:
     name: parent1
     namespace: {{< reuse "docs/snippets/namespace.md" >}}
   spec:
     parentRefs:
     - name: http
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

2. Create the second `parent2` HTTPRoute resource that serves traffic for the `delegation-parent2.example` domain. The HTTPRoute resource specifies two routes: 
   * `/anything/team1`: The routing decision is delegated to a child HTTPRoute resource in the `team1` namespace. 
   * `/anything/team2`: The routing decision is delegated to a child HTTPRoute resource in the `team2` namespace. 
   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.networking.k8s.io/v1
   kind: HTTPRoute
   metadata:
     name: parent2
     namespace: {{< reuse "docs/snippets/namespace.md" >}}
   spec:
     parentRefs:
     - name: http
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

3. Create the child HTTPRoute resource `child-team1` in the `team1` namespace that matches traffic on the `/anything/team1/foo` prefix and routes traffic to the httpbin app in the `team1` namespace. The child HTTPRoute resource does not select a specific parent HTTPRoute resource. Because of that, the child HTTPRoute resource is automatically selected by all parent HTTPRoute resources that delegate traffic to this child. 
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

4. Create the child HTTPRoute resource `child-team2` in the `team2` namespace that matches traffic on the `/anything/team1/bar` exact prefix and routes traffic to the httpbin app in the `team2` namespace. The child HTTPRoute resource specifies the `parent1` HTTPRoute resource in the `spec.parentRefs` section. Because of that, only `parent1` can delegate traffic to this child. 
   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.networking.k8s.io/v1
   kind: HTTPRoute
   metadata:
     name: child-team2
     namespace: team2
   spec:
     parentRefs:
     - name: parent1
       namespace: {{< reuse "docs/snippets/namespace.md" >}}
       group: gateway.networking.k8s.io
       kind: HTTPRoute
     rules:
     - matches:
       - path:
           type: Exact
           value: /anything/team2/bar
       backendRefs:
       - name: httpbin
         port: 8000
   EOF
   ```
   
6. Send a request to the `delegation-parent1.example` domain along the `/anything/team1/foo` path. Verify that you get back a 200 HTTP response code. 
   {{< tabs items="Cloud Provider LoadBalancer,Port-forward for local testing" tabTotal="2" >}}
   {{% tab tabName="Cloud Provider LoadBalancer" %}}
   ```sh
   curl -i http://$INGRESS_GW_ADDRESS:8080/anything/team1/foo -H "host: delegation-parent1.example"
   ```
   {{% /tab %}}
   {{% tab tabName="Port-forward for local testing" %}}
   ```sh
   curl -i localhost:8080/anything/team1/foo -H "host: delegation-parent1.example"
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

7. Send another request to the `delegation-parent1.example` domain along the `/anything/team2/bar` path. Verify that you get back a 200 HTTP response code. 
   {{< tabs items="Cloud Provider LoadBalancer,Port-forward for local testing" tabTotal="2" >}}
   {{% tab tabName="Cloud Provider LoadBalancer" %}}
   ```sh
   curl -i http://$INGRESS_GW_ADDRESS:8080/anything/team2/bar -H "host: delegation-parent1.example"
   ```
   {{% /tab %}}
   {{% tab tabName="Port-forward for local testing" %}}
   ```sh
   curl -i localhost:8080/anything/team2/bar -H "host: delegation-parent1.example"
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

8. Now, send a request to the `delegation-parent2.example` domain along the `/anything/team1/foo` path. Verify that you get back a 200 HTTP response code. 
   {{< tabs items="Cloud Provider LoadBalancer,Port-forward for local testing" tabTotal="2" >}}
   {{% tab tabName="Cloud Provider LoadBalancer" %}}
   ```sh
   curl -i http://$INGRESS_GW_ADDRESS:8080/anything/team1/foo -H "host: delegation-parent2.example"
   ```
   {{% /tab %}}
   {{% tab tabName="Port-forward for local testing" %}}
   ```sh
   curl -i localhost:8080/anything/team1/foo -H "host: delegation-parent2.example"
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
   
9. Send another request to the `delegation-parent2.example` domain. This time, you send traffic along the `/anything/team2/bar` path. Notice that although the `parent2` HTTPRoute resource delegates traffic to the `child-team2` HTTPRoute resource, the child resource allows traffic from the `parent1` HTTPRoute resource only. Because of that, the request fails and you get back a 404 HTTP response code. 
   {{< tabs items="Cloud Provider LoadBalancer,Port-forward for local testing" tabTotal="2" >}}
   {{% tab tabName="Cloud Provider LoadBalancer" %}}
   ```sh
   curl -i http://$INGRESS_GW_ADDRESS:8080/anything/team2/bar -H "host: delegation-parent2.example"
   ```
   {{% /tab %}}
   {{% tab tabName="Port-forward for local testing" %}}
   ```sh
   curl -i localhost:8080/anything/team2/bar  -H "host: delegation-parent2.example"
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
 
## Cleanup

{{< reuse "docs/snippets/cleanup.md" >}}

```sh
kubectl delete gateway http -n {{< reuse "docs/snippets/namespace.md" >}}
kubectl delete httproute parent1 -n {{< reuse "docs/snippets/namespace.md" >}}
kubectl delete httproute parent2 -n {{< reuse "docs/snippets/namespace.md" >}}
kubectl delete httproute child-team1 -n team1
kubectl delete httproute child-team2 -n team2
kubectl delete -n team1 -f https://raw.githubusercontent.com/kgateway-dev/kgateway.dev/main/assets/docs/examples/httpbin.yaml
kubectl delete -n team2 -f https://raw.githubusercontent.com/kgateway-dev/kgateway.dev/main/assets/docs/examples/httpbin.yaml
kubectl delete namespaces team1 team2
```

