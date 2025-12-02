Change the default route-level timeout of 15 seconds with an HTTPRoute or {{< reuse "docs/snippets/kgateway.md" >}} {{< reuse "docs/snippets/trafficpolicy.md" >}}. To ensure that your apps are available even if they are temporarily unavailable, you can use timeouts alongside [Retries]({{< link-hextra path="/resiliency/retry/" >}}).

{{< callout >}}
{{< reuse "docs/snippets/proxy-kgateway.md" >}}
{{< /callout >}}

## Before you begin

{{< reuse "docs/snippets/prereq.md" >}}

## Set up timeouts {#timeouts}
   
Specify timeouts for a specific route. 

1. Configure a timeout for a specific route by using the Kubernetes Gateway API-native configuration in an HTTPRoute or by using {{< reuse "docs/snippets/kgateway.md" >}}'s {{< reuse "docs/snippets/trafficpolicy.md" >}}. In the following example, you set a timeout of 20 seconds for httpbin's `/headers` path. However, no timeout is set along the `/anything` path. 
   {{< tabs tabTotal="2" items="Option 1: HTTPRoute (Kubernetes GW API),Option 2: TrafficPolicy" >}}
   {{% tab tabName="Option 1: HTTPRoute (Kubernetes GW API)" %}}
   ```yaml
   kubectl apply -n httpbin -f- <<EOF
   apiVersion: gateway.networking.k8s.io/v1
   kind: HTTPRoute
   metadata:
     name: httpbin-timeout
   spec:
     hostnames:
     - timeout.example
     parentRefs:
     - group: gateway.networking.k8s.io
       kind: Gateway
       name: http
       namespace: {{< reuse "docs/snippets/namespace.md" >}}
     rules:
     - matches: 
       - path:
           type: PathPrefix
           value: /headers
       backendRefs:
       - group: ""
         kind: Service
         name: httpbin
         port: 8000
       timeouts:
         request: "20s"
     - matches: 
       - path:
           type: PathPrefix
           value: /anything
       backendRefs:
       - group: ""
         kind: Service
         name: httpbin
         port: 8000
   EOF
   ```
   {{% /tab %}}
   {{% tab tabName="Option 2: GlooTrafficPolicy"  %}}
   1.  Install the experimental channel of the Kubernetes Gateway API to use this feature.
       ```sh
       kubectl apply -f https://github.com/kubernetes-sigs/gateway-api/releases/download/v1.3.0/experimental-install.yaml
       ```
   
   2. Create the HTTPRoute with two routes, `/headers` and `/anything`, and add an HTTPRoute rule name to each path. You use the rule name later to apply the timeout to a particular route. 
      ```yaml
      kubectl apply -n httpbin -f- <<EOF
      apiVersion: gateway.networking.k8s.io/v1
      kind: HTTPRoute
      metadata:
        name: httpbin-timeout
      spec:
        hostnames:
        - timeout.example
        parentRefs:
        - group: gateway.networking.k8s.io
          kind: Gateway
          name: http
          namespace: {{< reuse "docs/snippets/namespace.md" >}}
        rules:
        - matches: 
          - path:
              type: PathPrefix
              value: /headers
          backendRefs:
          - group: ""
            kind: Service
            name: httpbin
            port: 8000
          name: timeout
        - matches: 
          - path:
              type: PathPrefix
              value: /anything
          backendRefs:
          - group: ""
            kind: Service
            name: httpbin
            port: 8000
          name: no-timeout
      EOF
      ```
   
   3. Create a {{< reuse "docs/snippets/trafficpolicy.md" >}} with your timeout settings and use the `targetRefs.sectionName` to apply the timeout to a specific HTTPRoute rule. In this example, you apply the policy to the `timeout` rule that points to the `/headers` path in your HTTPRoute resource.
      ```yaml
      kubectl apply -f- <<EOF
      apiVersion: {{< reuse "docs/snippets/trafficpolicy-apiversion.md" >}}
      kind: {{< reuse "docs/snippets/trafficpolicy.md" >}}
      metadata:
        name: timeout
        namespace: httpbin
      spec:
        targetRefs:
        - kind: HTTPRoute
          group: gateway.networking.k8s.io
          name: httpbin-timeout
          sectionName: timeout
        timeouts:
          request: 20s
      EOF
      ```
   
   {{% /tab %}}
   {{< /tabs >}}

2. Send a request to the httpbin app along the `/headers` path that you configured a custom timeout for. Verify that the request succeeds and that you see a `X-Envoy-Expected-Rq-Timeout-Ms` header with the custom timeout of 20 seconds (20000).
   {{< tabs items="Cloud Provider LoadBalancer,Port-forward for local testing" tabTotal="2" >}}
   {{% tab tabName="Cloud Provider LoadBalancer" %}}
   ```sh
   curl -vi http://$INGRESS_GW_ADDRESS:8080/headers -H "host: timeout.example:8080"
   ```
   {{% /tab %}}
   {{% tab tabName="Port-forward for local testing" %}}
   ```sh
   curl -vi localhost:8080/headers -H "host: timeout.example"
   ```
   {{% /tab %}}
   {{< /tabs >}}

   Example output for a successful response: 
   ```console {hl_lines=[12,13]}
   {
    "headers": {
      "Accept": [
        "*/*"
      ],
      "Host": [
        "www.example.com:8080"
      ],
      "User-Agent": [
        "curl/7.77.0"
      ],
      "X-Envoy-Expected-Rq-Timeout-Ms": [
        "20000"
      ],
      "X-Forwarded-Proto": [
        "http"
      ],
      "X-Request-Id": [
        "0ae53bc3-2644-44f2-8603-158d2ccf9f78"
      ]
    }
   }
   ```
  
3. Send a request to the httpbin app along the `anything` path that does not have a custom timeout. Verify that the request succeeds and that you see a `X-Envoy-Expected-Rq-Timeout-Ms` header with the default timeout of 15 seconds (15000). 
   {{< tabs items="Cloud Provider LoadBalancer,Port-forward for local testing" tabTotal="2" >}}
   {{% tab tabName="Cloud Provider LoadBalancer" %}}
   ```sh
   curl -vi http://$INGRESS_GW_ADDRESS:8080/anything -H "host: timeout.example:8080"
   ```
   {{% /tab %}}
   {{% tab tabName="Port-forward for local testing" %}}
   ```sh
   curl -vi localhost:8080/anything -H "host: timeout.example"
   ```
   {{% /tab %}}
   {{< /tabs >}}

   Example output for a successful response: 
   ```console {hl_lines=[12,13]}
   {
    "headers": {
      "Accept": [
        "*/*"
      ],
      "Host": [
        "www.example.com:8080"
      ],
      "User-Agent": [
        "curl/7.77.0"
      ],
      "X-Envoy-Expected-Rq-Timeout-Ms": [
        "15000"
      ],
      "X-Forwarded-Proto": [
        "http"
      ],
      "X-Request-Id": [
        "0ae53bc3-2644-44f2-8603-158d2ccf9f78"
      ]
    }
   }
   ```

## Cleanup

{{< reuse "docs/snippets/cleanup.md" >}}
   
```sh
kubectl delete httproute httpbin-timeout -n httpbin
kubectl delete {{< reuse "docs/snippets/trafficpolicy.md" >}} timeout -n httpbin
```


