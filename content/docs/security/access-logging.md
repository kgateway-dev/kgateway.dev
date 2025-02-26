---
title: Access logging
weight: 10
description: Capture an access log for all the requests that enter the gateway. 
---

Capture an access log for all the requests that enter the gateway. 

## About access logging

Access logs, sometimes referred to as audit logs, represent all traffic requests that pass through the gateway proxy. The access log entries can be customized to include data from the request, the routing destination, and the response. 

Access logs can be written to a file, the `stdout` stream of the gateway proxy container, or exported to a gRPC server for custom handling. 

### Envoy data that can be logged

Envoy exposes a lot of data that can be used when customizing access logs. The following data properties are available for both TCP and HTTP access logging:

* The downstream (client) address, connection information, TLS configuration, and timing
* The upstream (service) address, connection information, TLS configuration, timing, and Envoy routing information
* Relevant Envoy configuration, such as rate of sampling (if used)
* Filter-specific context that is published to Envoy’s dynamic metadata during the filter chain

#### Additional HTTP properties 

When Envoy is used as an HTTP proxy, additional HTTP information is available for access logging, including:

* Request data, including the method, path, scheme, port, user agent, headers, body, and more
* Response data, including the response code, headers, body, and trailers, as well as a string representation of the response code
* Protocol version

## Before you begin

{{< reuse "docs/snippets/prereq.md" >}}

## Set up access logging for `stdout` {#access-log-stdout-filesink}

You can set up access logging for requests that the Envoy HttpConnectionManager handles. The following example writes access logs to the `/dev/stdout` path in the pod of the selected `http` gateway.

1. Create an HTTPListenerPolicy resource to define your access logging rules. The following example writes access logs to the `stdout` stream of the gateway proxy container by using a custom string format that is defined in the `jsonFormat` field. If no custom string format is defined, the [default Envoy format](https://www.envoyproxy.io/docs/envoy/v1.14.1/configuration/observability/access_log#config-access-log-format-strings) is used.  
   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.kgateway.dev/v1alpha1
   kind: HTTPListenerPolicy
   metadata:
     name: access-logs
     namespace: {{< reuse "docs/snippets/ns-system.md" >}}
   spec:
     targetRef:
       group: gateway.networking.k8s.io
       kind: Gateway
       name: http
     accessLog:
     - fileSink:
         path: /dev/stdout
         jsonFormat:
             start_time: "%START_TIME%"
             method: "%REQ(X-ENVOY-ORIGINAL-METHOD?:METHOD)%"
             path: "%REQ(X-ENVOY-ORIGINAL-PATH?:PATH)%"
             protocol: "%PROTOCOL%"
             response_code: "%RESPONSE_CODE%"
             response_flags: "%RESPONSE_FLAGS%"
             bytes_received: "%BYTES_RECEIVED%"
             bytes_sent: "%BYTES_SENT%"
             total_duration: "%DURATION%"
             resp_upstream_service_time: "%RESP(X-ENVOY-UPSTREAM-SERVICE-TIME)%"
             req_x_forwarded_for: "%REQ(X-FORWARDED-FOR)%"
             user_agent: "%REQ(USER-AGENT)%"
             request_id: "%REQ(X-REQUEST-ID)%"
             authority: "%REQ(:AUTHORITY)%"
             upstreamHost: "%UPSTREAM_HOST%"
             upstreamCluster: "%UPSTREAM_CLUSTER%"
   EOF
   ```

2. Send a request to the httpbin app on the `www.example.com` domain. Verify that your request succeeds and that you get back a 200 HTTP response code.  
   
   {{< tabs items="LoadBalancer IP address or hostname,Port-forward for local testing" >}}
   {{% tab  %}}
   ```sh
   curl -i http://$INGRESS_GW_ADDRESS:8080/status/200 -H "host: www.example.com:8080"
   ```
   {{% /tab %}}
   {{% tab %}}
   ```sh
   curl -i localhost:8080/status/200 -H "host: www.example.com:8080"
   ```
   {{% /tab %}}
   {{< /tabs >}}
   
   Example output: 
   ```
   HTTP/1.1 200 OK
   access-control-allow-credentials: true
   access-control-allow-origin: *
   date: Fri, 07 Jun 2024 21:10:03 GMT
   x-envoy-upstream-service-time: 2
   server: envoy
   transfer-encoding: chunked
   ```
   
3. Get the logs for the gateway pod and verify that you see an entry for each request that you sent to the httpbin app. 
   
   ```sh
   kubectl -n {{< reuse "docs/snippets/ns-system.md" >}} logs deployments/http | tail -1 | jq --sort-keys
   ```
   
   Example output: 
   ```
   {
     "authority": "www.example.com:8080",
     "bytes_received": 0,
     "bytes_sent": 0,
     "method": "GET",
     "path": "/status/200",
     "protocol": "HTTP/1.1",
     "req_x_forwarded_for": null,
     "request_id": "a6758866-0f26-4c95-95d9-4032c365c498",
     "resp_upstream_service_time": "0",
     "response_code": 200,
     "response_flags": "-",
     "start_time": "2024-08-19T20:57:57.511Z",
     "total_duration": 1,
     "upstreamCluster": "kube-svc:httpbin-httpbin-8000_httpbin",
     "upstreamHost": "10.36.0.14:8080",
     "user_agent": "curl/7.77.0"
   }
   ```

<!-- TODO updated for gRPC service

## Set up access logging to a gRPC service {#access-log-grpc}

You send access logs to a gRPC service. This way, you can collect logs from several gateways in a central location that is integrated with an existing log collecting service that you might already use, such as OpenTelemetry. This option performs better than writing to stdout for scalable, high traffic scenarios.

1. Create or get the details of the gRPC service. The following example creates a simple `log-test` service in the {{< reuse "docs/snippets/ns-system.md" >}} namespace that listens on port 50051.

2. Create an HTTPListenerPolicy resource to define your access logging rules. The following example writes access logs to gRPC service that you created in the previous step. It logs requests that use the `x-my-cool-test-filter` header when the value is `test`. For more Envoy filters, see the [Envoy access log docs](https://www.envoyproxy.io/docs/envoy/latest/api-v3/config/accesslog/v3/accesslog.proto).  
   
   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.kgateway.dev/v1alpha1
   kind: HTTPListenerPolicy
   metadata:
     name: access-logs
     namespace: {{< reuse "docs/snippets/ns-system.md" >}}
   spec:
     targetRef:
       group: gateway.networking.k8s.io
       kind: Gateway
       name: http
     accessLog:
     - grpcService:
         logName: "test-accesslog-service"
         backendRef:
           name: log-test
           port: 50051
       filter:
           headerFilter:
               header:
                 value: "test"
                 name: "x-my-cool-test-filter"
                 type: "Exact"
   EOF
   ```

3. Send a request to the httpbin app on the `www.example.com` domain. Verify that your request succeeds and that you get back a 200 HTTP response code.  
   
   {{< tabs items="LoadBalancer IP address or hostname,Port-forward for local testing" >}}
   {{% tab  %}}
   ```sh
   curl -i http://$INGRESS_GW_ADDRESS:8080/status/200 -H "host: www.example.com:8080" -H "x-my-cool-test-filter:test"
   ```
   {{% /tab %}}
   {{% tab %}}
   ```sh
   curl -i localhost:8080/status/200 -H "host: www.example.com:8080" -H "x-my-cool-test-filter:test"
   ```
   {{% /tab %}}
   {{< /tabs >}}
   
   Example output: 
   ```
   HTTP/1.1 200 OK
   access-control-allow-credentials: true
   access-control-allow-origin: *
   date: Fri, 07 Jun 2024 21:10:03 GMT
   x-envoy-upstream-service-time: 2
   server: envoy
   transfer-encoding: chunked
   ```

4. Send another request, this time with the header that you configured in the HTTPListenerPolicy. Verify that your request succeeds and that you get back a 200 HTTP response code.  
   
   {{< tabs items="LoadBalancer IP address or hostname,Port-forward for local testing" >}}
   {{% tab  %}}
   ```sh
   curl -i http://$INGRESS_GW_ADDRESS:8080/status/200 -H "host: www.example.com:8080" -H "x-my-cool-test-filter:test"
   ```
   {{% /tab %}}
   {{% tab %}}
   ```sh
   curl -i localhost:8080/status/200 -H "host: www.example.com:8080" -H "x-my-cool-test-filter:test"
   ```
   {{% /tab %}}
   {{< /tabs >}}
   
   Example output: 
   ```
   HTTP/1.1 200 OK
   access-control-allow-credentials: true
   access-control-allow-origin: *
   date: Fri, 07 Jun 2024 21:10:03 GMT
   x-envoy-upstream-service-time: 2
   server: envoy
   transfer-encoding: chunked
   ```

5. Get the logs of the gRPC service and verify that you see an entry for the matching requests that you sent to the httpbin app. 
   
   ```sh
   kubectl -n {{< reuse "docs/snippets/ns-system.md" >}} logs deployments/log-test | tail -1 | jq --sort-keys
   ```
   
   Example output: 
   ```
   {
     "authority": "www.example.com:8080",
     "bytes_received": 0,
     "bytes_sent": 0,
     "method": "GET",
     "path": "/status/200",
     "protocol": "HTTP/1.1",
     "req_x_forwarded_for": null,
     "request_id": "a6758866-0f26-4c95-95d9-4032c365c498",
     "resp_upstream_service_time": "0",
     "response_code": 200,
     "response_flags": "-",
     "start_time": "2024-08-19T20:57:57.511Z",
     "total_duration": 1,
     "upstreamCluster": "kube-svc:httpbin-httpbin-8000_httpbin",
     "upstreamHost": "10.36.0.14:8080",
     "user_agent": "curl/7.77.0"
   }
   ```

-->

## Cleanup

{{< reuse "docs/snippets/cleanup.md" >}}

```sh
kubectl delete HTTPListenerPolicy access-logs -n {{< reuse "docs/snippets/ns-system.md" >}}
```
