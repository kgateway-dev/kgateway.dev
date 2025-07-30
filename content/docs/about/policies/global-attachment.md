---
title: Global policy attachment
weight: 20
---

By default, you must attach policies to resources that are in the same namespace. However, you might have policies that you want to reuse across teams, such as to standardize security protections across your organization.

To do so, you can create policies in a "global" namespace. Then, the policies can attach to resources in any namespace in your cluster through label selectors.

{{< callout type="warning" >}}
Because it increases the number of policy attachments to calculate, the global policy namespace feature can impact performance at scale. It also changes the standard policy attachment behavior, which can make debugging more difficult. As such, make sure to establish clear guidelines for using this feature, such as how many global policies are available for teams to use.
{{< /callout >}}

## Before you begin

{{< reuse "docs/snippets/prereq.md" >}}

## Step 1: Review default policy behavior {#default-policy}

By default, policies are attached to resources in the same namespace. This way, each team manages their own apps, routing resources, and policies.

1. Send a request to the httpbin service on the `/anything` path and note the expected 200 response.
   
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

   Example output:
   
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

2. Create a {{< reuse "docs/snippets/trafficpolicy.md" >}} that rewrites the path to `/status/418` if it has the `transform:status` header. Note that the policy is in the same namespace as the HTTPRoute.

   ```yaml
   kubectl apply -f- <<EOF  
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
       request:
         set:
         - name: ":path"
           value: '{% if request_header("transform") == "status" %}/status/418{% else %}{{ header(":path") }}{% endif %}'
   EOF
   ```

3. Repeat the request with the `transform:status` header. The request is now transformed from the `/anything` path to the `/status/418` path.

   {{< tabs items="Cloud Provider LoadBalancer,Port-forward for local testing" tabTotal="2" >}}
   {{% tab tabName="Cloud Provider LoadBalancer" %}}
   ```sh
   curl -i http://$INGRESS_GW_ADDRESS:8080/anything -H "host: www.example.com:8080" -H "transform: status"
   ```
   {{% /tab %}}
   {{% tab tabName="Port-forward for local testing"%}}
   ```sh
   curl -i localhost:8080/anything -H "host: www.example.com" -H "transform: status"
   ```
   {{% /tab %}}
   {{< /tabs >}}

   Example output: Notice that the response is now `418 I'm a teapot!` instead of the initial 200 response.
   
   ```txt
   HTTP/1.1 418 Unknown
   access-control-allow-credentials: true
   access-control-allow-origin: *
   x-more-info: http://tools.ietf.org/html/rfc2324
   date: Wed, 30 Jul 2025 15:45:07 GMT
   content-length: 13
   content-type: text/plain; charset=utf-8
   x-envoy-upstream-service-time: 1
   server: envoy
   
   I'm a teapot!
   ```

4. Delete the {{< reuse "docs/snippets/trafficpolicy.md" >}}.

   ```sh
   kubectl delete {{< reuse "docs/snippets/trafficpolicy.md" >}} -n httpbin transformation
   ```

5. Create the same {{< reuse "docs/snippets/trafficpolicy.md" >}} but in a different namespace, such as the `{{< reuse "docs/snippets/namespace.md" >}}` namespace.

   ```yaml
   kubectl apply -f- <<EOF  
   apiVersion: {{< reuse "docs/snippets/trafficpolicy-apiversion.md" >}}
   kind: {{< reuse "docs/snippets/trafficpolicy.md" >}}
   metadata:
     name: transformation
     namespace: {{< reuse "docs/snippets/namespace.md" >}}
   spec:
     targetRefs:
     - group: gateway.networking.k8s.io
       kind: HTTPRoute
       name: httpbin
     transformation:
       request:
         set:
         - name: ":path"
           value: '{% if request_header("transform") == "status" %}/status/418{% else %}{{ header(":path") }}{% endif %}'
   EOF
   ```

6. Repeat the request. This time, the request is not transformed. The policy cannot be attached because the resource is in a different namespace. Instead, you get the initial 200 response.

   {{< tabs items="Cloud Provider LoadBalancer,Port-forward for local testing" tabTotal="2" >}}
   {{% tab tabName="Cloud Provider LoadBalancer" %}}
   ```sh
   curl -i http://$INGRESS_GW_ADDRESS:8080/anything -H "host: www.example.com:8080" -H "transform: status"
   ```
   {{% /tab %}}
   {{% tab tabName="Port-forward for local testing"%}}
   ```sh
   curl -i localhost:8080/anything -H "host: www.example.com" -H "transform: status"
   ```
   {{% /tab %}}
   {{< /tabs >}}

   Example output:
   
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

## Step 2: Enable global policy attachment {#enable-global-policy-attachment}

To enable the global policy attachment feature, upgrade your {{< reuse "/docs/snippets/kgateway.md" >}} Helm installation.

1. Get the Helm values for your current Helm installation. 
   ```sh
   helm get values {{< reuse "/docs/snippets/helm-kgateway.md" >}} -n {{< reuse "docs/snippets/namespace.md" >}} -o yaml > {{< reuse "/docs/snippets/helm-kgateway.md" >}}.yaml
   open {{< reuse "/docs/snippets/helm-kgateway.md" >}}.yaml
   ```
   
2. Add the following values to the Helm values file to enable the global policy namespace feature. The example uses the `{{< reuse "docs/snippets/namespace.md" >}}` namespace as the "global" namespace, but you can use any existing namespace that you want.
   ```yaml
   
   controller:
     extraEnv:
       KGW_GLOBAL_POLICY_NAMESPACE: {{< reuse "docs/snippets/namespace.md" >}}
   ```
   
3. Upgrade your Helm installation. Replace the `--version {{< reuse "/docs/versions/helm-version-flag.md" >}}` option to match your current version.
   
   ```sh
   helm upgrade -i --namespace {{< reuse "docs/snippets/namespace.md" >}} --version {{< reuse "/docs/versions/helm-version-flag.md" >}} {{< reuse "/docs/snippets/helm-kgateway.md" >}} oci://{{< reuse "/docs/snippets/helm-path.md" >}}/charts/{{< reuse "/docs/snippets/helm-kgateway.md" >}} -f {{< reuse "/docs/snippets/helm-kgateway.md" >}}.yaml
   ```

## Step 3: Create a global policy {#create-global-policy}

Create a global policy in the `{{< reuse "docs/snippets/namespace.md" >}}` namespace. Then, use a `global-policy` label selector to attach the policy to resources in any namespace.

1. Update the HTTPRoute for the httpbin service to add a label selector. The label selector can be any value that you want, but it must match the label selector that you add in the {{< reuse "docs/snippets/trafficpolicy.md" >}}.

   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.networking.k8s.io/v1
   kind: HTTPRoute
   metadata:
     name: httpbin
     namespace: httpbin
     labels:
       global-policy: transformation
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

2. Update the {{< reuse "docs/snippets/trafficpolicy.md" >}} to target the HTTPRoute by using the `global-policy` label in the `targetSelectors` field (instead of the `targetRefs` field).

   ```yaml
   kubectl apply -f- <<EOF  
   apiVersion: {{< reuse "docs/snippets/trafficpolicy-apiversion.md" >}}
   kind: {{< reuse "docs/snippets/trafficpolicy.md" >}}
   metadata:
     name: transformation
     namespace: {{< reuse "docs/snippets/namespace.md" >}}
   spec:
     targetSelectors:
     - group: gateway.networking.k8s.io
       kind: HTTPRoute
       matchLabels:
         global-policy: transformation
     transformation:
       request:
         set:
         - name: ":path"
           value: '{% if request_header("transform") == "status" %}/status/418{% else %}{{ header(":path") }}{% endif %}'
   EOF
   ```

3. Send a request with the `transform:status` header. This time, the request is transformed even though the HTTPRoute and transformation policy are in different namespaces.

   {{< tabs items="Cloud Provider LoadBalancer,Port-forward for local testing" tabTotal="2" >}}
   {{% tab tabName="Cloud Provider LoadBalancer" %}}
   ```sh
   curl -i http://$INGRESS_GW_ADDRESS:8080/anything -H "host: www.example.com:8080" -H "transform: status"
   ```
   {{% /tab %}}
   {{% tab tabName="Port-forward for local testing"%}}
   ```sh
   curl -i localhost:8080/anything -H "host: www.example.com" -H "transform: status"
   ```
   {{% /tab %}}
   {{< /tabs >}}

   Example output:

   ```txt
   HTTP/1.1 418 Unknown
   access-control-allow-credentials: true
   access-control-allow-origin: *
   x-more-info: http://tools.ietf.org/html/rfc2324
   date: Wed, 30 Jul 2025 15:49:17 GMT
   content-length: 13
   content-type: text/plain; charset=utf-8
   x-envoy-upstream-service-time: 0
   server: envoy
   
   I'm a teapot!%
   ```


## More resources

For more examples of attaching policies to different resources, review each policy's docs.

{{< cards >}}
  {{< card link="../../policies/backendconfigpolicy/#policy-attachment-backendconfigpolicy" title="BackendConfigPolicy" >}}
  {{< card link="../../policies/httplistenerpolicy/#policy-attachment-listeneroption" title="HTTPListenerPolicy" >}}
  {{< card link="../../policies/trafficpolicy/#policy-attachment-trafficpolicy" title="TrafficPolicy" >}}
{{< /cards >}}

## Cleanup {#cleanup}

{{< reuse "docs/snippets/cleanup.md" >}}

1. Delete the transformation policy.

   ```sh
   kubectl delete {{< reuse "docs/snippets/trafficpolicy.md" >}} -n {{< reuse "docs/snippets/namespace.md" >}} transformation
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
