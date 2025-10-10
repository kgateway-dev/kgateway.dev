---
title: Per-try timeout
weight: 20
description:
---

Set separate timeouts for retries. 

## About per-try timeouts

The per-retry timeout allows you to set a timeout for retried requests. If the timeout expires, Envoy cancels the retry attempt and immediately retries on another upstream host. 

By default, Envoy has a default overall request timeout of 15 seconds. A request timeout represents the time Envoy waits for the entire request to complete, including retries. Without a per-try timeout, retries might take longer than the overall request timeout, and therefore might not be executed as the request times out before the retry attempts can be performed. You can configure a larger [request timeout]({{< link-hextra path="/resiliency/timeouts/request/" >}}) to account for this case. However, you can also define timeouts for each retry so that you can protect against slow retry attempts from consuming the entire request timeout.

<!--
When per-try timeouts are enabled, Envoy returns the `x-envoy-upstream-rq-per-try-timeout-ms` header in the response.  -->
Note that if you configured a global request timeout, the per-try timeout must be less than the global request timeout.

Per-try timeouts can be configured on an HTTPRoute directly. To enable per-try timeouts on a Gateway listener level, use a {{< reuse "docs/snippets/trafficpolicy.md" >}} instead. 

{{< callout type="warning" >}} 
{{< reuse "docs/versions/warn-experimental.md" >}}
{{< /callout >}}

{{< callout >}}
{{< reuse "docs/snippets/proxy-kgateway.md" >}}
{{< /callout >}}


## Before you begin

{{< reuse "docs/snippets/prereq.md" >}}

## Set up per-retry timeouts

1. Install the experimental Kubernetes Gateway API CRDs.
   
   ```sh
   kubectl apply -f https://github.com/kubernetes-sigs/gateway-api/releases/download/v{{< reuse "docs/versions/k8s-gw-version.md" >}}/experimental-install.yaml
   ```

2. Configure the per-retry timeout. You can apply the timeout to an HTTPRoute, or Gateway listener.
   {{< tabs tabTotal="3" items="HTTPRoute (Kubernetes GW API),HTTPRoute (TrafficPolicy),Gateway listener" >}}
   {{% tab tabName="HTTPRoute (Kubernetes GW API)" %}}
   Use the `timeouts.backendRequest` field to configure the per-try timeout. Note that you must set a retry policy also to configure a per-try timeout. 
   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.networking.k8s.io/v1
   kind: HTTPRoute
   metadata:
     name: retry
     namespace: httpbin
   spec:
     hostnames:
     - retry.example
     parentRefs:
     - group: gateway.networking.k8s.io
       kind: Gateway
       name: http
       namespace: {{< reuse "docs/snippets/namespace.md" >}}
     rules:
     - matches: 
       - path:
           type: PathPrefix
           value: /
       backendRefs:
       - group: ""
         kind: Service
         name: httpbin
         port: 8000
       retry:
         attempts: 3
         backoff: 1s  
       timeouts:
         backendRequest: 5s 
   EOF
   ```
   {{% /tab %}}
   {{% tab tabName="HTTPRoute (GlooTrafficPolicy)" %}}
   1. Create an HTTPRoute to route requests along the `retry.example` domain to the httpbin app. Note that you add a name `timeout` to your HTTPRoute rule so that you can configure the per-try timeout for that rule later. 
      ```yaml
      kubectl apply -f- <<EOF
      apiVersion: gateway.networking.k8s.io/v1
      kind: HTTPRoute
      metadata:
        name: retry
        namespace: httpbin
      spec:
        hostnames:
        - retry.example
        parentRefs:
        - group: gateway.networking.k8s.io
          kind: Gateway
          name: http
          namespace: {{< reuse "docs/snippets/namespace.md" >}}
        rules:
        - matches: 
          - path:
              type: PathPrefix
              value: /
          backendRefs:
          - group: ""
            kind: Service
            name: httpbin
            port: 8000
          name: timeout 
      EOF
      ```
   2. Create a {{< reuse "docs/snippets/trafficpolicy.md" >}} to configure the per-try timeout. In this example, the per-try timeout is set to 5 seconds and assigned to the `timeout` HTTPRoute rule. Note that you must set a retry policy also to apply a per-try timeout. 
      ```yaml
      kubectl apply -f- <<EOF
      apiVersion: {{< reuse "docs/snippets/trafficpolicy-apiversion.md" >}}
      kind: {{< reuse "docs/snippets/trafficpolicy.md" >}}
      metadata:
        name: retry
        namespace: httpbin
      spec:
        targetRefs:
        - kind: HTTPRoute
          group: gateway.networking.k8s.io
          name: retry
          sectionName: timeout
        retry:
          attempts: 3
          perTryTimeout: 5s
          statusCodes:
          - 517
      EOF
      ```
   
   {{% /tab %}}
   {{% tab tabName="Gateway listener" %}}
   1. Create an HTTPRoute to route requests along the `retry.example` domain to the httpbin app. 
      ```yaml
      kubectl apply -f- <<EOF
      apiVersion: gateway.networking.k8s.io/v1
      kind: HTTPRoute
      metadata:
        name: retry
        namespace: httpbin
      spec:
        hostnames:
        - retry.example
        parentRefs:
        - group: gateway.networking.k8s.io
          kind: Gateway
          name: http
          namespace: {{< reuse "docs/snippets/namespace.md" >}}
        rules:
        - matches: 
          - path:
              type: PathPrefix
              value: /
          backendRefs:
          - group: ""
            kind: Service
            name: httpbin
            port: 8000
      EOF
      ```
   2. Create {{< reuse "docs/snippets/trafficpolicy.md" >}} to configure the per-try timeout. In this example, the per-try timeout is set to 5 seconds and assigned to the `http` Gateway listener that you set up as part of the [before you begin](#before-you-begin) section. Note that you must set a retry policy also to apply a per-try timeout. 
      ```yaml
      kubectl apply -f- <<EOF
      apiVersion: {{< reuse "docs/snippets/trafficpolicy-apiversion.md" >}}
      kind: {{< reuse "docs/snippets/trafficpolicy.md" >}}
      metadata:
        name: retry
        namespace: {{< reuse "docs/snippets/namespace.md" >}}
      spec:
        targetRefs:
        - kind: Gateway
          group: gateway.networking.k8s.io
          name: http
          sectionName: http
        retry:
          attempts: 2
          perTryTimeout: 5s
          statusCodes:
          - 517
      EOF
      ```
   {{% /tab %}}
   {{< /tabs >}}

2. Send a request to the httpbin app along the `retry.example` domain. Verify that the `X-Envoy-Expected-Rq-Timeout-Ms` header is set to the 5 second timeout that you configured.
   {{< tabs items="Cloud Provider LoadBalancer,Port-forward for local testing" tabTotal="2" >}}
   {{% tab tabName="Cloud Provider LoadBalancer" %}}
   ```sh
   curl -vi http://$INGRESS_GW_ADDRESS:8080/anything -H "host: retry.example:8080"
   ```
   {{% /tab %}}
   {{% tab tabName="Port-forward for local testing" %}}
   ```sh
   curl -vi localhost:8080/anything -H "host: retry.example"
   ```
   {{% /tab %}}
   {{< /tabs >}}
   
   Example output: 
   ```console {hl_lines=[14,15]}
   ...
   {
    "args": {},
    "headers": {
      "Accept": [
        "*/*"
      ],
      "Host": [
        "retry.example"
      ],
      "User-Agent": [
        "curl/8.7.1"
      ],
      "X-Envoy-Expected-Rq-Timeout-Ms": [
        "5000"
      ],
      "X-Envoy-External-Address": [
        "127.0.0.1"
      ],
      "X-Forwarded-For": [
        "10.244.0.55"
      ],
      "X-Forwarded-Proto": [
        "http"
      ],
      "X-Request-Id": [
        "9178dc39-297f-438a-8bd9-4e8203c06b59"
      ]
   },
   ```

3. Verify that the gateway proxy is configured with the per-try timeout.
   1. Port-forward the gateway proxy on port 19000.

      ```sh
      kubectl port-forward deployment/http -n {{< reuse "docs/snippets/namespace.md" >}} 19000
      ```

   2. Get the configuration of your gateway proxy as a config dump.

      ```sh
      curl -X POST 127.0.0.1:19000/config_dump\?include_eds > gateway-config.json
      ```

   3. Open the config dump and find the route configuration for the `kube_default_reviews_9080` Envoy cluster on the `listener~8080~retry_example` virtual host. Verify that the retry policy is set as you configured it.
      
      Example `jq` command:
      ```sh
      jq '.configs[] | select(."@type" == "type.googleapis.com/envoy.admin.v3.RoutesConfigDump") | .dynamic_route_configs[].route_config.virtual_hosts[] | select(.routes[].route.cluster == "kube_httpbin_httpbin_8000")' gateway-config.json
      ```
      
      Example output: 
      ```console {hl_lines=[12]}
      "routes": [
        {
          "match": {
            "prefix": "/"
          },
          "route": {
            "cluster": "kube_httpbin_httpbin_8000",
            "timeout": "5s",
            "retry_policy": {
              "retry_on": "cancelled,connect-failure,refused-stream,retriable-headers,retriable-status-codes,unavailable",
              "num_retries": 3,
              "per_try_timeout": "5s",
              "retry_back_off": {
                "base_interval": "1s"
              }
            },
            "cluster_not_found_response_code": "INTERNAL_SERVER_ERROR"
          },
          "name": "listener~8080~retry_example-route-0-httproute-retry-httpbin-0-0-matcher-0"
        }
      ]
      ```



## Cleanup

{{< reuse "docs/snippets/cleanup.md" >}}
   
```sh
kubectl delete {{< reuse "docs/snippets/trafficpolicy.md" >}} retry -n httpbin
kubectl delete {{< reuse "docs/snippets/trafficpolicy.md" >}} retry -n {{< reuse "docs/snippets/namespace.md" >}}
kubectl delete httproute retry -n httpbin
```

