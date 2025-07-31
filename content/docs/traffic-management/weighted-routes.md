---
title: Weighted routing
weight: 20
---

By default, the Kubernetes Gateway API sorts HTTPRoute rules based on their order and specificity, as defined in the [Gateway API docs](https://gateway-api.sigs.k8s.io/reference/spec/#httprouterule). When a route matches a request, no further routes are evaluated for matching, which might affect the gateway's routing decision and the policies that are applied to the traffic. With {{< reuse "/docs/snippets/kgateway.md" >}}, you can configure weights for more fine-grained control over your routing rules.

## Before you begin

{{< reuse "docs/snippets/prereq.md" >}}

## Step 1: Review the default routing behavior {#default-routing}

By default, the Kubernetes Gateway API sorts HTTPRoute rules as defined in the [Gateway API docs](https://gateway-api.sigs.k8s.io/reference/spec/#httprouterule).

1. Specificity of the route matching rule, such as a header match with largest number of matching headers.
2. Oldest route based on creation timestamp.
3. Alphabetical order of the route based on the `namespace/name` of the route.
4. Order of the route in the list of the HTTPRoute resource.

Review route precedence in action:

1. Deploy a hello-world app to demonstrate different backend responses.

   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: apps/v1
   kind: Deployment
   metadata:
     name: hello-world
     namespace: httpbin
   spec:
     replicas: 1
     selector:
       matchLabels:
         app: hello-world
     template:
       metadata:
         labels:
           app: hello-world
       spec:
         containers:
         - name: hello-world
           image: nginxdemos/hello:plain-text
           ports:
           - containerPort: 80
   ---
   apiVersion: v1
   kind: Service
   metadata:
     name: hello-world
     namespace: httpbin
   spec:
     selector:
       app: hello-world
     ports:
     - port: 80
       targetPort: 80
   EOF
   ```

2. Update the HTTPRoute to demonstrate the default Gateway API precedence behavior by configuring two routes: `/anything` that routes traffic to the httpbin app and `/anything/a` that targets the hello-world app you just deployed.

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
         namespace: {{< reuse "docs/snippets/namespace.md" >}}
     hostnames:
       - "www.example.com"
     rules:
       - matches:
         - path:
             type: PathPrefix
             value: /anything
         backendRefs:
           - name: httpbin
             port: 8000
       - matches:
         - path:
             type: PathPrefix
             value: /anything/a
         backendRefs:
           - name: hello-world
             port: 80
   EOF
   ```

3. Send a request to the `/anything/a` path. The request matches both the rules for `/anything` and `/anything/a`. Because the more specific `/anything/a` rule takes precedence, the request routes to the hello-world service instead of the httpbin service.
   
   {{< tabs items="Cloud Provider LoadBalancer,Port-forward for local testing" tabTotal="2" >}}
   {{% tab tabName="Cloud Provider LoadBalancer" %}}
   ```sh
   curl -i http://$INGRESS_GW_ADDRESS:8080/anything/a -H "host: www.example.com:8080"
   ```
   {{% /tab %}}
   {{% tab tabName="Port-forward for local testing"%}}
   ```sh
   curl -i localhost:8080/anything/a -H "host: www.example.com"
   ```
   {{% /tab %}}
   {{< /tabs >}}

   Example output from the hello-world service:
   
   ```txt
   HTTP/1.1 200 OK
   server: envoy
   date: Tue, 29 Jul 2025 20:07:36 GMT
   content-type: text/plain
   content-length: 167
   expires: Tue, 29 Jul 2025 20:07:35 GMT
   cache-control: no-cache
   x-envoy-upstream-service-time: 0
   
   Server address: 10.244.0.8:80
   Server name: hello-world-669dfbd799-g4jkg
   Date: 29/Jul/2025:20:07:36 +0000
   URI: /anything/a
   Request ID: 796644ce8bda8ae5ecc36c5f4117a590
   ```

4. Send a request to the `/anything` path. This example routes to the httpbin service because it only matches the less specific rule.
   
   {{< tabs items="Cloud Provider LoadBalancer,Port-forward for local testing" tabTotal="2" >}}
   {{% tab tabName="Cloud Provider LoadBalancer" %}}
   ```sh
   curl -i http://$INGRESS_GW_ADDRESS:8080/anything -H "host: www.example.com:8080"
   ```
   {{% /tab %}}
   {{% tab tabName="Port-forward for local testing"%}}
   ```sh
   curl -i localhost:8080/anything -H "host: www.example.com"
   ```
   {{% /tab %}}
   {{< /tabs >}}

   Example output from the httpbin service:
   
   ```txt
   HTTP/1.1 200 OK
   access-control-allow-credentials: true
   access-control-allow-origin: *
   content-type: application/json; encoding=utf-8
   date: Tue, 29 Jul 2025 20:08:21 GMT
   content-length: 587
   x-envoy-upstream-service-time: 1
   server: envoy
   ```
   ```json
   {
     "args": {},
     "headers": {
       "Accept": [
         "*/*"
       ],
       "Host": [
         "www.example.com"
       ],
       "User-Agent": [
         "curl/8.7.1"
       ],
       "X-Envoy-Expected-Rq-Timeout-Ms": [
         "15000"
       ],
       "X-Envoy-External-Address": [
         "127.0.0.1"
       ],
       "X-Forwarded-For": [
         "10.244.0.7"
       ],
       "X-Forwarded-Proto": [
         "http"
       ],
       "X-Request-Id": [
         "7ec1f5f7-72b7-4053-b2e4-0117a2438d4c"
       ]
     },
     "origin": "10.244.0.7",
     "url": "http://www.example.com/anything",
     "data": "",
     "files": null,
     "form": null,
     "json": null
   }
   ```

## Step 2: Enable weighted route precedence {#enable-weighted-route-precedence}

By default, weighted routes are disabled. Upgrade your {{< reuse "/docs/snippets/kgateway.md" >}} Helm installation to enable the feature.

1. Get the Helm values for your current Helm installation. 
   ```sh
   helm get values {{< reuse "/docs/snippets/helm-kgateway.md" >}} -n {{< reuse "docs/snippets/namespace.md" >}} -o yaml > {{< reuse "/docs/snippets/helm-kgateway.md" >}}.yaml
   open {{< reuse "/docs/snippets/helm-kgateway.md" >}}.yaml
   ```
   
2. Add the following values to the Helm values file to enable the weighted routes feature in {{< reuse "/docs/snippets/kgateway.md" >}}.
   ```yaml
   
   controller:
     extraEnv:
       KGW_WEIGHTED_ROUTE_PRECEDENCE: true
   ```
   
3. Upgrade your Helm installation. Replace the `--version {{< reuse "/docs/versions/helm-version-flag.md" >}}` option to match your current version.
   
   ```sh
   helm upgrade -i --namespace {{< reuse "docs/snippets/namespace.md" >}} --version {{< reuse "/docs/versions/helm-version-flag.md" >}} {{< reuse "/docs/snippets/helm-kgateway.md" >}} oci://{{< reuse "/docs/snippets/helm-path.md" >}}/charts/{{< reuse "/docs/snippets/helm-kgateway.md" >}} -f {{< reuse "/docs/snippets/helm-kgateway.md" >}}.yaml
   ```

## Step 3: Add weights to routes {#weight-routes}

Apply an annotation at the HTTPRoute level that sets a weight for the route, which can be any 32-bit integer, including negative numbers. HTTPRoutes without the annotation are given a weight of `0`. Routes are sorted as follows:

1. In descending order by weight, from highest to lowest.
2. By [Gateway API route precedence](https://gateway-api.sigs.k8s.io/reference/spec/#httprouterule) for routes with the same weight.

{{< callout type="info" >}}
Using route delegation? Make sure to add the `kgateway.dev/route-weight` annotation to the child HTTPRoute that you want to weight. Children **do not** inherit the weight of their parent HTTPRoute.
{{< /callout >}}

Steps to weight routes:

1. Create separate HTTPRoutes for the `/anything` and `/anything/a` paths.

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
         namespace: {{< reuse "docs/snippets/namespace.md" >}}
     hostnames:
       - "www.example.com"
     rules:
       - matches:
         - path:
             type: PathPrefix
             value: /anything
         backendRefs:
           - name: httpbin
             port: 8000
   ---
   apiVersion: gateway.networking.k8s.io/v1
   kind: HTTPRoute
   metadata:
     name: hello-world-a
     namespace: httpbin
   spec:
     parentRefs:
       - name: http
         namespace: {{< reuse "docs/snippets/namespace.md" >}}
     hostnames:
       - "www.example.com"
     rules:
       - matches:
         - path:
             type: PathPrefix
             value: /anything/a
         backendRefs:
           - name: hello-world
             port: 80
   EOF
   ```

2. Send a request to the httpbin app on the `/anything/a` path. Because the default Gateway API sorting rules give precedence to the more specific `/anything/a` route, the request is served by the hello-world service instead of the httpbin service.

   {{< tabs items="Cloud Provider LoadBalancer,Port-forward for local testing" tabTotal="2" >}}
   {{% tab tabName="Cloud Provider LoadBalancer" %}}
   ```sh
   curl -i http://$INGRESS_GW_ADDRESS:8080/anything/a -H "host: www.example.com:8080"
   ```
   {{% /tab %}}
   {{% tab tabName="Port-forward for local testing"%}}
   ```sh
   curl -i localhost:8080/anything/a -H "host: www.example.com"
   ```
   {{% /tab %}}
   {{< /tabs >}}

   Example output:
   
   ```txt
   HTTP/1.1 200 OK
   access-control-allow-credentials: true
   access-control-allow-origin: *
   content-type: application/json; encoding=utf-8
   date: Thu, 13 Feb 2025 18:49:32 GMT
   content-length: 330
   x-envoy-upstream-service-time: 4
   server: envoy
   ```
   ```txt
   Server address: 10.244.0.8:80
   Server name: hello-world-669dfbd799-g4jkg
   Date: 29/Jul/2025:20:19:01 +0000
   URI: /anything/a
   Request ID: dbfe6dd762fc25ae7297f2ef881ae30b
   ```

3. Add a weight of `10` to the HTTPRoute with the matching rule for the `/anything` path that is served by the httpbin service, and a weight of `1` to the HTTPRoute with the matching rule for the `/anything/a` path that is served by the hello-world service.

   ```yaml
   kubectl annotate httproute -n httpbin httpbin kgateway.dev/route-weight=10
   kubectl annotate httproute -n httpbin hello-world-a kgateway.dev/route-weight=1
   ```

4. Send another request on the `/anything/a` path. Because the weight of the httpbin HTTPRoute is higher than the hello-world route, the request is served by the httpbin service instead of the hello-world service.

   {{< tabs items="Cloud Provider LoadBalancer,Port-forward for local testing" tabTotal="2" >}}
   {{% tab tabName="Cloud Provider LoadBalancer" %}}
   ```sh
   curl -i http://$INGRESS_GW_ADDRESS:8080/anything/a -H "host: www.example.com:8080"
   ```
   {{% /tab %}}
   {{% tab tabName="Port-forward for local testing"%}}
   ```sh
   curl -i localhost:8080/anything/a -H "host: www.example.com"
   ```
   {{% /tab %}}
   {{< /tabs >}}

   Example output:
   
   ```txt
   HTTP/1.1 200 OK
   access-control-allow-credentials: true
   access-control-allow-origin: *
   content-type: application/json; encoding=utf-8
   date: Thu, 13 Feb 2025 18:49:32 GMT
   content-length: 330
   x-envoy-upstream-service-time: 4
   server: envoy
   ```
   ```json
   {
     "headers": {
       "Accept": [
         "*/*"
       ],
       "Host": [
         "www.example.com"
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
         "26be0bcd-d941-48f4-ac3b-d5ac288ac46f"
       ]
     }
   }
   ```

## More resources

For more examples of weighted routes, review the following examples from the kgateway GitHub repository.

{{< cards >}}
  {{< card link="https://github.com/kgateway-dev/kgateway/blob/main/internal/kgateway/translator/gateway/testutils/inputs/route-sort-weighted.yaml" title="Weighted route input" icon="external-link" >}}
  {{< card link="https://github.com/kgateway-dev/kgateway/blob/main/internal/kgateway/translator/gateway/testutils/outputs/route-sort-weighted.yaml" title="Weighted route output" icon="external-link" >}}
{{< /cards >}}

## Cleanup {#cleanup}

{{< reuse "docs/snippets/cleanup.md" >}}

1. Delete the extra hello-world app that you created for this tutorial.

   ```sh
   kubectl delete deployment -n httpbin hello-world
   kubectl delete service -n httpbin hello-world
   kubectl delete httproute -n httpbin hello-world-a
   ```

2. Restore the sample httpbin HTTPRoute.

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
         namespace: {{< reuse "docs/snippets/namespace.md" >}}
     hostnames:
       - "www.example.com"
     rules:
       - backendRefs:
           - name: httpbin
             port: 8000
   EOF
   ```