---
title: Header and query match
weight: 35
description: Use header and query matchers in a route delegation setup. 
---

Use header and query matchers in a route delegation setup. 

## Configuration overview

In this guide you walk through a route delegation example where headers and query parameters are added as matchers to the parent and child HTTPRoute resources. A routing hierarchy can be created only if the child defines the same header and query matchers that the parent HTTPResource defines. You can optionally define additional header or query matchers on the child HTTPRoute resource.

For example, if the parent HTTPRoute resource specifies the `header` header, the child must specify the same header matcher. 

The following image illustrates the route delegation hierarchy:

{{< reuse-image src="img/route-delegation-header-query.svg" width="800" >}}
{{< reuse-image-dark srcDark="img/route-delegation-header-query-dark.svg" width="800" >}}

**`parent` HTTPRoute**: 
* The parent HTTPRoute resource delegates traffic as follows: 
  * `/anything/team1` delegates traffic to the child HTTPRoute resource `child-team1` in namespace `team1` for requests that include the `header1; val1` request header and the `query1=val1` query parameter. 
  * `/anything/team2` delegates traffic to the child HTTPRoute resource `child-team2` in namespace `team2` for requests that include the `header2: val2` request header and the `query2=val2` query parameter. 
  
**`child-team1` HTTPRoute**: 
* The child HTTPRoute resource `child-team1` matches incoming traffic for the `/anything/team1/foo` prefix path if the `header1: val1` and `headerX: valX` request headers and `query1=val1` and `queryX=valX` query parameters are present in the request. Requests that match these conditions are forwarded to the httpbin app in namespace `team1`. Note that the headers and query parameters are a superset of the headers and query parameters that the parent HTTPRoute resource defines.

**`child-team2` HTTPRoute**: 
* The child HTTPRoute resource `child-team2` matches incoming traffic for the `/anything/team2/bar` exact prefix path if the `headerX: valX` request header and `queryX=valX` query parameter are present in the request. Because the child HTTPRoute resource does not specify the same header and query parameters that the parent HTTPRoute specified, the route is considered invalid.
* You later apply a different version of the `child-team2` HTTPRoute that specifies the `delegation.kgateway.dev/inherit-parent-matcher: "true"` annotation. This annotation allows the HTTPRoute to inherit the matchers, headers, and query parameters from the parent. Because of that, the route is considered valid and traffic can be routed to the httpbin app in the team2 namespace.

## Before you begin

{{< reuse "docs/snippets/prereq-delegation.md" >}}

## Setup

1. Create the parent HTTPRoute resource that matches incoming traffic on the `delegation.example` domain. The HTTPRoute resource specifies two routes: 
   * Route 1 matches on the following conditions. If these conditions are met, the routing decision is delegated to a child HTTPRoute resource in the `team1` namespace.
     * path prefix match on `/anything/team1` 
     * exact header match on `header1=val1` 
     * exact query parameter match on `query1=val1`  
   * Route 2 matches on the following conditions. If these conditions are met, the routing decision is delegated to a child HTTPRoute resource in the `team2` namespace.
     * path prefix match on `/anything/team2`
     * exact header match on `header2=val2`
     * exact query parameter match on `query2=val2` 
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
         headers:
         - type: Exact
           name: header1
           value: val1
         queryParams:
         - type: Exact
           name: query1
           value: val1
       backendRefs:
       - group: gateway.networking.k8s.io
         kind: HTTPRoute
         name: "*"
         namespace: team1
     - matches:
       - path:
           type: PathPrefix
           value: /anything/team2
         headers:
         - type: Exact
           name: header2
           value: val2
         queryParams:
         - type: Exact
           name: query2
           value: val2
       backendRefs:
       - group: gateway.networking.k8s.io
         kind: HTTPRoute
         name: "*"
         namespace: team2
   EOF
   ```

2. Create the `child-team1` HTTPRoute resource in the `team1` namespace that matches traffic on the `/anything/team1/foo` path prefix if the `header1=val1` and `headerX=valX` request headers and the `query1=val1` and `queryX=valX` query parameters are present in the request. Requests that meet these conditions are forwarded to the httpbin app in the `team1` namespace.
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
         headers:
         - type: Exact
           name: header1
           value: val1
         - type: Exact
           name: headerX
           value: valX
         queryParams:
         - type: Exact
           name: query1
           value: val1
         - type: Exact
           name: queryX
           value: valX
       backendRefs:
       - name: httpbin
         port: 8000
   EOF
   ```

3. Create the `child-team2` HTTPRoute resource in the `team2` namespace that matches traffic on the `/anything/team2/bar` exact path if the `headerX=valX` request header and `queryX=valX` query parameter are present in the request. Requests that meet these conditions are forwarded to the httpbin app in the `team2` namespace.
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
           type: Exact
           value: /anything/team2/bar
         headers:
         - type: Exact
           name: headerX
           value: valX
         queryParams:
         - type: Exact
           name: queryX
           value: valX
       backendRefs:
       - name: httpbin
         port: 8000
   EOF
   ```
      
5. Send a request to the `delegation.example` domain along the `/anything/team1/foo` path with the `header1=val1` request header and the `query1=val1` query parameter. Verify that you get back a 404 HTTP response code. Although you included the header and query parameters that are defined on the parent HTTPRoute resource, the headers and query parameters that the child HTTPRoute resource matches on are missing in your request.
   {{< tabs items="Cloud Provider LoadBalancer,Port-forward for local testing" tabTotal="2"  >}}
   {{% tab tabName="Cloud Provider LoadBalancer" %}}
   ```sh
   curl -i "http://$INGRESS_GW_ADDRESS:8080/anything/team1/foo?query1=val1" \
   -H "host: delegation.example" -H "header1: val1"
   ```
   {{% /tab %}}
   {{% tab tabName="Port-forward for local testing" %}}
   ```sh
   curl -i "localhost:8080/anything/team1/foo?query1=val1" \
   -H "host: delegation.example" -H "header1: val1"
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
   
6. Send another request to the `delegation.example` domain along the `/anything/team1/foo` path. This time, you include all of the header and query parameters that the parent and child HTTPRoute resources defined. Verify that you get back a 200 HTTP response code. 
   {{< tabs items="Cloud Provider LoadBalancer,Port-forward for local testing" tabTotal="2"  >}}
   {{% tab tabName="Cloud Provider LoadBalancer" %}}
   ```sh
   curl -i "http://$INGRESS_GW_ADDRESS:8080/anything/team1/foo?query1=val1&queryX=valX" \
   -H "host: delegation.example" -H "header1: val1" -H "headerX: valX"
   ```
   {{% /tab %}}
   {{% tab tabName="Port-forward for local testing" %}}
   ```sh
   curl -i "localhost:8080/anything/team1/foo?query1=val1&queryX=valX" \
   -H "host: delegation.example" -H "header1: val1" -H "headerX: valX"
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

7. Send another request to the `delegation.example` domain along the `/anything/team2/bar` path that is configured on the `child-team2` HTTPRoute resource and include all of the header and query parameters that are defined on the parent and child HTTPRoute resources. Verify that you get back a 404 HTTP response code. Because the `child-team2` HTTPRoute resource does not specify the same header and query matchers as the parent HTTPRoute resource, the routing configuration is considered invalid. 
   {{< tabs items="Cloud Provider LoadBalancer,Port-forward for local testing" tabTotal="2" >}}
   {{% tab tabName="Cloud Provider LoadBalancer" %}}
   ```sh
   curl -i "http://$INGRESS_GW_ADDRESS:8080/anything/team2/bar?queryX=valX&query2=val2" \
   -H "host: delegation.example" -H "headerX: valX" -H "header2: val2"
   ```
   {{% /tab %}}
   {{% tab tabName="Port-forward for local testing" %}}
   ```sh
   curl -i "localhost:8080/anything/team2/bar?queryX=valX&query2=val2" \
   -H "host: delegation.example" -H "headerX: valX" -H "header2: val2"
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
   
## Inherit parent attributes

Instead of requiring the child HTTPRoutes to define the same matchers, headers, and query parameters as the parent HTTPRoute, you can use the `delegation.kgateway.dev/inherit-parent-matcher: "true"` annotation on the child HTTPRoute to inherit these attributes from the parent. This setting is useful if you want to use paths that are relative to the parent path, or augment the headers and query parameters that are set on the parent. 

1. Update the `child-team2` HTTPRoute to include the `delegation.kgateway.dev/inherit-parent-matcher: "true"` annotation. This annotation allows the `child-team2` HTTPRoute to inherit the matchers, headers, and query parameters that are defined on the parent.

   The following configuration specifies the `/` prefix path and therefore allows all paths that are relative to the parent's `/anything/team2` prefix matcher. In addition, you augment the header and query parameters from the parent with custom header and query parameters. Note that when you sent requests to the `child-team2` HTTPRoute earlier, these requests failed, because the HTTPRoute did not define the same header and query parameters as the `parent` in addition to the custom values. 
   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.networking.k8s.io/v1
   kind: HTTPRoute
   metadata:
     name: child-team2
     namespace: team2
     annotations:
       delegation.kgateway.dev/inherit-parent-matcher: "true"
   spec:
     rules:
     - matches:
       - path:
           type: PathPrefix
           value: /
         headers:
         - type: Exact
           name: headerX
           value: valX
         queryParams:
         - type: Exact
           name: queryX
           value: valX
       backendRefs:
       - name: httpbin
         port: 8000
   EOF
   ```

2. Send a request to the `delegation.example` domain along the `/anything/team2/bar` path and include all of the header and query parameters that are defined on the parent and child HTTPRoute resources. Verify that this time, you get back a 200 HTTP response code, because `child-team2` inherited the matchers, headers, and query parameters from the `parent`. 
   {{< tabs items="Cloud Provider LoadBalancer,Port-forward for local testing" tabTotal="2">}}
   {{% tab tabName="Cloud Provider LoadBalancer" %}}
   ```sh
   curl -i "http://$INGRESS_GW_ADDRESS:8080/anything/team2/bar?queryX=valX&query2=val2" \
   -H "host: delegation.example" -H "headerX: valX" -H "header2: val2"
   ```
   {{% /tab %}}
   {{% tab tabName="Port-forward for local testing" %}}
   ```sh
   curl -i "localhost:8080/anything/team2/bar?queryX=valX&query2=val2" \
   -H "host: delegation.example:8080" -H "headerX: valX" -H "header2: val2"
   ```
   {{% /tab %}}
   {{< /tabs >}}
   
   Example output: 
   ```
   HTTP/1.1 200 OK
   access-control-allow-credentials: true
   access-control-allow-origin: *
   content-type: application/json; encoding=utf-8
   content-length: 681
   x-envoy-upstream-service-time: 0
   server: envoy

   {
     "args": {
       "query2": [
         "val2"
       ],
       "queryX": [
         "valX"
       ]
     },
     "headers": {
       "Accept": [
         "*/*"
       ],
       "Header2": [
         "val2"
       ],
       "Headerx": [
         "valX"
       ],
       "Host": [
         "delegation.example:8080"
       ],
       "User-Agent": [
         "curl/8.7.1"
       ],
       "X-Envoy-Expected-Rq-Timeout-Ms": [
         "15000"
       ],
       "X-Forwarded-Proto": [
         "http"
       ],
       "X-Request-Id": [
         "30dfc350-d546-4f53-857d-cb3edab68ebd"
       ]
     },
     "origin": "10.0.64.27:50590",
     "url": "http://delegation.example:8080/anything/team2/bar?queryX=valX&query2=val2",
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
