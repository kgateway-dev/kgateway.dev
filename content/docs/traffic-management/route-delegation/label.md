---
title: Delegation via labels
weight: 15
description: Use labels to delegate traffic from a parent HTTPRoute to different child HTTPRoutes.
---


{{< callout type="warning" >}} 
{{< reuse "docs/versions/warn-2-1-only.md" >}} 
{{< /callout >}}

In this example, you learn how to use labels to delegate traffic. The parent HTTPRoute defines the labels that must be present on the child HTTPRoute to allow traffic to be forwarded. 

You typically configure the parent to find an HTTPRoute with a specific label in a specific namespace. However, you can also use a wildcard for the namespace when you have multiple HTTPRoutes in different namespaces that can all receive delegated traffic. This configuration can significantly simplify your route delegation setup, as it allows you to quickly add new child HTTPRoutes to the delegation chain without changing the parent HTTPRoute configuration. 

{{< tabs items="Specific namespace,Wildcard namespace" tabTotal="2" >}}
{{% tab tabName="Specific namespace" %}}

Explore an example for delegating traffic to an HTTPRoute with a specific label in a specific namespace. To try out this example, see the [Before you begin](#before-you-begin) section and then continue with [HTTPRoutes in specific namespaces](#specific-namespace). 

{{< reuse-image src="img/route-delegation-labels.svg" >}} 
{{< reuse-image-dark srcDark="img/route-delegation-labels-dark.svg" >}} 

`parent` HTTPRoute: </br>
* The parent HTTPRoute resource delegates traffic as follows:
  * Requests to `/anything/team1` are delegated to the child HTTPRoute resource `child-team1` in namespace `team1` with the `delegation.kgateway.dev/label: team1` label.
  * Requests to `/anything/team2` are delegated to the child HTTPRoute resource `child-team2` in namespace `team2` with the `delegation.kgateway.dev/label: team2` label.

`child-team1` HTTPRoute: </br>

* The child HTTPRoute resource `child-team1` matches incoming traffic for the `/anything/team1/foo` prefix path and routes that traffic to the httpbin app in the `team1` namespace.

`child-team2` HTTPRoute:

* The child HTTPRoute resource `child-team2` matches incoming traffic for the `/anything/team1/bar` prefix path and routes that traffic to the httpbin app in the `team2` namespace.

{{% /tab %}}
{{% tab tabName="Wildcard namespace" %}}

Learn how to use a wildcard for the namespace to streamline your route delegation setup. To try out this example, see the [Before you begin](#before-you-begin) section and then continue with [Use wildcard namespaces](#wildcard). 

{{< reuse-image src="img/route-delegation-labels-wildcard.svg" >}} 
{{< reuse-image-dark srcDark="img/route-delegation-labels-wildcard-dark.svg" >}} 

`parent` HTTPRoute: </br>
* The parent HTTPRoute resource delegates traffic as follows:
  * Requests to `/` are delegated to all child HTTPRoute resources with the `delegation.kgateway.dev/label: wildcard` label. The `/` matcher is used so that the child HTTPRoutes can define any path prefix that they want to match traffic on.

`child-team1` HTTPRoute: </br>

* The child HTTPRoute resource `child-team1` matches incoming traffic for the `/anything/team1/foo` prefix path and routes that traffic to the httpbin app in the `team1` namespace. The HTTPRoute is configured with the `delegation.kgateway.dev/label: wildcard` label so that it can receive delegated traffic from the `parent`. 

`child-team2` HTTPRoute:

* The child HTTPRoute resource `child-team2` matches incoming traffic for the `/anything/team1/bar` prefix path and routes that traffic to the httpbin app in the `team2` namespace. The HTTPRoute is configured with the `delegation.kgateway.dev/label: wildcard` label so that it can receive delegated traffic from the `parent`. 
{{% /tab %}}

{{< /tabs >}}

## Before you begin

{{< reuse "docs/snippets/prereq-delegation.md" >}}

## HTTPRoutes in specific namespaces {#specific-namespace}

1. Create the parent HTTPRoute resource that matches incoming traffic on the `delegation.example` domain. The HTTPRoute resource specifies two routes: 
   * Route 1 matches traffic on the path prefix `/anything/team1` and delegates traffic to the HTTPRoute with the `delegation.kgateway.dev/label: team1` label. 
   * Route 2 matches traffic on the path prefix `/anything/team2` and delegates traffic to the HTTPRoute with the `delegation.kgateway.dev/label: team2` label. 
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
     - delegation.example
     rules:
     - matches:
       - path: 
           type: PathPrefix
           value: /anything/team1
       backendRefs:
       # Delegate to routes with the label delegation.kgateway.dev/label:team1
       # in the team1 namespace
       - group: delegation.kgateway.dev
         kind: label 
         name: team1
         namespace: team1
     - matches:
       - path: 
           type: PathPrefix
           value: /anything/team2
       backendRefs:
       # Delegate to routes with the label delegation.kgateway.dev/label:team2
       # in the team2 namespace
       - group: delegation.kgateway.dev
         kind: label 
         name: team2
         namespace: team2
   EOF
   ```

2. Create the `child-team1` HTTPRoute resource in the `team1` namespace that matches traffic on the `/anything/team1/foo` path prefix. To delegate traffic to this HTTPRoute, you must label the route with the `delegation.kgateway.dev/label: team1` label that you defined on the `parent` HTTPRoute. 
   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.networking.k8s.io/v1
   kind: HTTPRoute
   metadata:
     name: child-team1
     namespace: team1
     labels: 
       delegation.kgateway.dev/label: team1
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

3. Create the `child-team2` HTTPRoute resource in the `team2` namespace that matches traffic on the `/anything/team2/bar` exact prefix. To delegate traffic to this HTTPRoute, you must label the route with the `delegation.kgateway.dev/label: team2` label that you defined on the `parent` HTTPRoute. 
   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.networking.k8s.io/v1
   kind: HTTPRoute
   metadata:
     name: child-team2
     namespace: team2
     labels: 
       delegation.kgateway.dev/label: team2
   spec:
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
      
5. Send a request to the `delegation.example` domain along the `/anything/team1/foo` path. Verify that you get back a 200 HTTP response code. 
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
   ```
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
         "15000"
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

6. Send a request to the `delegation.example` domain along the `/anything/team2/bar` path. Verify that you also get back a 200 HTTP response code.  
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
   ```
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
         "15000"
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

## Use wildcard namespaces {#wildcard}

Instead of routing to an HTTPRoute with a specific label in a specific namespace, you can use a wildcard for the namespace. This configuration can streamline your route delegation setup, as it allows you to easily add new child HTTPRoutes to the delegation chain. 

1. Update the `parent` HTTPRoute to delegate traffic to all child HTTPRoutes with the `wildcard` label. 
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
     - delegation.example
     rules:
     - matches:
       - path:
           type: PathPrefix
           value: /
       backendRefs:
       - group: delegation.kgateway.dev
         kind: label
         name: wildcard
         namespace: all
   EOF
   ```

2. Update the `child-team1` HTTPRoute to add the `delegation.kgateway.dev/label: wildcard` label so that the `parent` HTTPRoute can delegate traffic to this route. 
   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.networking.k8s.io/v1
   kind: HTTPRoute
   metadata:
     name: child-team1
     namespace: team1
     labels: 
       delegation.kgateway.dev/label: wildcard
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

3. Update the `child-team2` HTTPRoute to also add the `delegation.kgateway.dev/label: wildcard` label. 
   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.networking.k8s.io/v1
   kind: HTTPRoute
   metadata:
     name: child-team2
     namespace: team2
     labels: 
       delegation.kgateway.dev/label: wildcard
   spec:
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

4. Send a request to the `delegation.example` domain along the `/anything/team1/foo` path. Verify that you get back a 200 HTTP response code. 
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
   ```
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
         "15000"
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

5. Send a request to the `delegation.example` domain along the `/anything/team2/bar` path. Verify that you also get back a 200 HTTP response code.  
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
   ```
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
         "15000"
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
kubectl delete httproute parent -n {{< reuse "docs/snippets/namespace.md" >}}
kubectl delete httproute child-team1 -n team1
kubectl delete httproute child-team2 -n team2
kubectl delete -n team1 -f https://raw.githubusercontent.com/kgateway-dev/kgateway.dev/main/assets/docs/examples/httpbin.yaml
kubectl delete -n team2 -f https://raw.githubusercontent.com/kgateway-dev/kgateway.dev/main/assets/docs/examples/httpbin.yaml
kubectl delete namespaces team1 team2
```