---
title: Retries and timeouts
weight: 10
description: Set a maximum time for the gateway to handle a request, including error retries.
---

Set a maximum time for the gateway to handle a request, including error retries.

## About

The Kubernetes Gateway API provides a way to configure timeouts and retries on your HTTPRoutes.

### Timeouts {#about-timeouts}

A timeout is the amount of time ([duration](https://protobuf.dev/reference/protobuf/google.protobuf/#duration)) that kgateway waits for replies from a backend service before the service is considered unavailable. This setting can be useful to avoid your apps from hanging or fail if no response is returned in a specific timeframe. With timeouts, calls either succeed or fail within a predicatble timeframe.

The time an app needs to process a request can vary a lot which is why applying the same timeout across services can cause a variety of issues. For example, a timeout that is too long can result in excessive latency from waiting for replies from failing services. On the other hand, a timeout that is too short can result in calls failing unnecessarily while waiting for an operation that needs responses from multiple services.

### Retries {#about-retries}

A retry is the number of times a request is retried if it fails. This setting can be useful to avoid your apps from failing if they are temporarily unavailable. With retries, calls are retried a certain number of times before they are considered failed. Retries can enhance your app's availability by making sure that calls don’t fail permanently because of transient problems, such as a temporarily overloaded service or network.

For more information, see the [Gateway API docs](https://gateway-api.sigs.k8s.io/geps/gep-1731/).

## Before you begin

{{< reuse "docs/snippets/prereq.md" >}}

## Set up timeouts {#timeouts}
   
Specify timeouts for a specific route. 

1. Create an HTTPRoute resource to specify your timeout rules. In the following example, the request must be completed within 20 seconds.  
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
       namespace: kgateway-system
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
       timeouts:
         request: "20s"
   EOF
   ```

2. Send a request to the httpbin app. Verify that the request succeeds and that you see a `X-Envoy-Expected-Rq-Timeout-Ms` header. If the header is present, kgateway expects requests to the httpbin app to succeed within the set timeout. 
   {{< tabs items="LoadBalancer IP address or hostname,Port-forward for local testing" >}}
   {{% tab  %}}
   ```sh
   curl -vi http://$INGRESS_GW_ADDRESS:8080/headers -H "host: timeout.example:8080"
   ```
   {{% /tab %}}
   {{% tab %}}
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

### Cleanup

{{< reuse "docs/snippets/cleanup.md" >}}

1. Delete the HTTPRoute resource.
   
   ```sh
   kubectl delete httproute httpbin-timeout -n httpbin
   ```

## Set up retries {#retries}

Specify retries for a specific route.

{{% callout type="warning" %}} 
{{< reuse "docs/versions/warn-experimental.md" >}}
{{% /callout %}}

### Retry prereqs {#before-you-begin-retries}

1. Install the experimental CRDs
   
   ```sh
   kubectl apply -f https://github.com/kubernetes-sigs/gateway-api/releases/download/v{{< reuse "docs/versions/k8s-gw-version.md" >}}/experimental-install.yaml
   ```

2. Install a sample app that you can mimic a failure for, such as adding a `sleep` command to the [Bookinfo reviews app](https://istio.io/latest/docs/examples/bookinfo/).

   ```sh
   kubectl apply -f- <<EOF
   ---
   apiVersion: v1
   kind: Service
   metadata:
     name: reviews
     namespace: default
     labels:
       app: reviews
       service: reviews
   spec:
     ports:
     - port: 9080
       name: http
     selector:
       app: reviews
   ---
   apiVersion: v1
   kind: ServiceAccount
   metadata:
     name: bookinfo-reviews
     namespace: default
     labels:
       account: reviews
   ---
   apiVersion: apps/v1
   kind: Deployment
   metadata:
     name: reviews-v1
     namespace: default
     labels:
       app: reviews
       version: v1
   spec:
     replicas: 1
     selector:
       matchLabels:
         app: reviews
         version: v1
     template:
       metadata:
         labels:
           app: reviews
           version: v1
       spec:
         serviceAccountName: bookinfo-reviews
         containers:
         - name: reviews
           image: docker.io/istio/examples-bookinfo-reviews-v1:1.20.3
           imagePullPolicy: IfNotPresent
           env:
           - name: LOG_DIR
             value: "/tmp/logs"
           ports:
           - containerPort: 9080
           volumeMounts:
           - name: tmp
             mountPath: /tmp
           - name: wlp-output
             mountPath: /opt/ibm/wlp/output
         volumes:
         - name: wlp-output
           emptyDir: {}
         - name: tmp
           emptyDir: {}   
   EOF
   ```

3. Apply an access log policy to the gateway that tracks the number of retries. The key log in the following example is `response_flags`, which is used to verify that the request was retried. For more information, see the [Access logging guide](/docs/security/access-logging/) and the [Envoy access logs response flags docs](https://www.envoyproxy.io/docs/envoy/latest/configuration/observability/access_log/usage#response-flags).

   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.kgateway.dev/v1alpha1
   kind: HTTPListenerPolicy
   metadata:
     name: access-logs
     namespace: kgateway-system
   spec:
     targetRefs:
     - group: gateway.networking.k8s.io
       kind: Gateway
       name: http
     accessLog:
     - fileSink:
         path: /dev/stdout
         jsonFormat:
           start_time: "%START_TIME%"
           method: "%REQ(:METHOD)%"
           path: "%REQ(:PATH)%"
           response_code: "%RESPONSE_CODE%"
           response_flags: "%RESPONSE_FLAGS%"
           upstream_host: "%UPSTREAM_HOST%"
           upstream_cluster: "%UPSTREAM_CLUSTER%"
   EOF
   ```

### Test retries {#test-retries}

1. Update the HTTPRoute resource to specify your retry rules. In the following example, the request is retried 3 times if it fails (`attempts: 3`). The retry will be attempted every 10 seconds (`backoff: 10s`).

   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.networking.k8s.io/v1
   kind: HTTPRoute
   metadata:
     name: retry
     namespace: default
   spec:
     hostnames:
     - retry.example
     parentRefs:
     - group: gateway.networking.k8s.io
       kind: Gateway
       name: http
       namespace: kgateway-system
     rules:
     - matches: 
       - path:
           type: PathPrefix
           value: /
       backendRefs:
       - group: ""
         kind: Service
         name: reviews
         port: 9080
       timeouts:
         request: "20s"       
       retry:
         attempts: 3
         backoff: 1s
   EOF
   ```

2. Send a request to the reviews app. Verify that the request succeeds.
 
   {{< tabs items="LoadBalancer IP address or hostname,Port-forward for local testing" >}}
   {{% tab  %}}
   ```sh
   curl -vi http://$INGRESS_GW_ADDRESS:8080/reviews/1 -H "host: retry.example:8080"
   ```
   {{% /tab %}}
   {{% tab %}}
   ```sh
   curl -vi localhost:8080/reviews/1 -H "host: retry.example"
   ```
   {{% /tab %}}
   {{< /tabs >}}

   Example output for a successful response:

   ```
   HTTP/1.1 200 OK
   ...
   {"id": "1","podname": "reviews-v1-598b896c9d-l7d8l","clustername": "null","reviews": [{  "reviewer": "Reviewer1",  "text": "An extremely entertaining play by Shakespeare. The slapstick humour is refreshing!"},{  "reviewer": "Reviewer2",  "text": "Absolutely fun and entertaining. The play lacks thematic depth when compared to other plays by Shakespeare."}]}
   ```

3. Check the gateway logs to verify that the request was not retried.
   
   ```sh
   kubectl logs -n kgateway-system -l gateway.networking.k8s.io/gateway-name=http | tail -1 | jq
   ```

   Example output: Note that the `response_flags` field is `-`, which means that the request was not retried.

   ```json
   {
     "method": "GET",
     "path": "/reviews/1",
     "response_code": 200,
     "response_flags": "-",
     "start_time": "2025-06-16T17:24:04.268Z",
     "upstream_cluster": "kube_default_reviews_9080",
     "upstream_host": "10.244.0.24:9080"
   }
   ```

3. Send the reviews app to sleep, to mimic an app failure.

   ```sh
   kubectl -n default patch deploy reviews-v1 --patch '{"spec":{"template":{"spec":{"containers":[{"name":"reviews","command":["sleep","20h"]}]}}}}'
   ```

4. Send another request to the reviews app. This time, the request fails.
   
   {{< tabs items="LoadBalancer IP address or hostname,Port-forward for local testing" >}}
   {{% tab  %}}
   ```sh
   curl -vi http://$INGRESS_GW_ADDRESS:8080/reviews/1 -H "host: retry.example:80"
   ```
   {{% /tab %}}
   {{% tab %}}
   ```sh
   curl -vi localhost:8080/reviews/1 -H "host: retry.example"
   ```
   {{% /tab %}}
   {{< /tabs >}}

   Example output:

   ```
   HTTP/1.1 503 Service Unavailable
   ...
   upstream connect error or disconnect/reset before headers. retried and the latest reset reason: remote connection failure, transport failure reason: delayed connect error: Connection refused
   ```

5. Check the gateway logs to verify that the request was retried.
   
   ```sh
   kubectl logs -n kgateway-system -l gateway.networking.k8s.io/gateway-name=http | tail -1 | jq
   ```

   Example output: Note that the `response_flags` field now has values as follows:

   * `URX` means `UpstreamRetryLimitExceeded`, which verifies that the request was retried.
   * `UF` means `UpstreamOverflow`, which verifies that the request failed.
   
   ```json
   {
     "method": "GET",
     "path": "/reviews/1",
     "response_code": 503,
     "response_flags": "URX,UF",
     "start_time": "2025-06-16T17:26:07.287Z",
     "upstream_cluster": "kube_default_reviews_9080",
     "upstream_host": "10.244.0.25:9080"
   }
   ```

### Cleanup

{{< reuse "docs/snippets/cleanup.md" >}}

1. Delete the HTTPRoute resource.
   
   ```sh
   kubectl delete httproute httpbin-retry -n httpbin
   ```

2. Delete the reviews app.

   ```sh
   kubectl delete deploy reviews-v1 -n default
   kubectl delete svc reviews -n default
   kubectl delete sa bookinfo-reviews -n default
   ```

3. Delete the access log policy.

   ```sh
   kubectl delete httplistenerpolicy access-logs -n kgateway-system
   ```
