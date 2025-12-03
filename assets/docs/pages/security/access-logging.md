Capture an access log for all the requests that enter the gateway. 

{{< callout >}}
{{< reuse "docs/snippets/proxy-kgateway.md" >}}
{{< /callout >}}

## About access logging

Access logs, sometimes referred to as audit logs, represent all traffic requests that pass through the gateway proxy. The access log entries can be customized to include data from the request, the routing destination, and the response. 

Access logs can be written to a file, the `stdout` stream of the gateway proxy container, or exported to a gRPC server for custom handling. The access logs capture information from requests that the Envoy HttpConnectionManager in your gateway proxy handles.

### Envoy data that can be logged

Envoy exposes a lot of data that can be used when customizing access logs. The following data properties are available for both TCP and HTTP access logging:

* The downstream (client) address, connection information, TLS configuration, and timing
* The backend (service) address, connection information, TLS configuration, timing, and Envoy routing information
* Relevant Envoy configuration, such as rate of sampling (if used)
* Filter-specific context that is published to Envoy's dynamic metadata during the filter chain

### Additional HTTP properties 

When Envoy is used as an HTTP proxy, additional HTTP information is available for access logging, including:

* Request data, including the method, path, scheme, port, user agent, headers, body, and more
* Response data, including the response code, headers, body, and trailers, as well as a string representation of the response code
* Protocol version

## Before you begin

{{< reuse "docs/snippets/prereq.md" >}}

## Access logs to `stdout` {#access-log-stdout-filesink}

You can set up access logs to write to a standard (stdout/stderr) stream. The following example writes access logs to a stdout in the pod of the selected `http` gateway.

1. Create an HTTPListenerPolicy resource to define your access logging rules. The following example writes access logs to the `stdout` stream of the gateway proxy container by using a custom string format that is defined in the `jsonFormat` field. 
   
   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.kgateway.dev/v1alpha1
   kind: HTTPListenerPolicy
   metadata:
     name: access-logs
     namespace: {{< reuse "docs/snippets/namespace.md" >}}
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
             method: "%REQ(X-ENVOY-ORIGINAL-METHOD?:METHOD)%"
             path: "%REQ(X-ENVOY-ORIGINAL-PATH?:PATH)%"
             protocol: "%PROTOCOL%"
             response_code: "%RESPONSE_CODE%"
             response_flags: "%RESPONSE_FLAGS%"
             bytes_received: "%BYTES_RECEIVED%"
             bytes_sent: "%BYTES_SENT%"
             total_duration: "%DURATION%"
             resp_backend_service_time: "%RESP(X-ENVOY-UPSTREAM-SERVICE-TIME)%"
             req_x_forwarded_for: "%REQ(X-FORWARDED-FOR)%"
             user_agent: "%REQ(USER-AGENT)%"
             request_id: "%REQ(X-REQUEST-ID)%"
             authority: "%REQ(:AUTHORITY)%"
             backendHost: "%UPSTREAM_HOST%"
             backendCluster: "%UPSTREAM_CLUSTER%"
   EOF
   ```

   | Setting | Description |
   | ------- | ----------- |
   | `targetRefs`| Select the Gateway to enable access logging for. The example selects the `http` gateway that you created from the sample app guide. |
   | `accessLog` | Configure the details for access logging. You can use multiple `fileSink` configurations for multiple outputs. The example sets up a `fileSink` for standard logging (stdout) in JSON format at `/dev/stdout`. You can also send the access logs to a `grpcService` instead of `fileSink`. |
   | `path` | The path in the gateway proxy to write access logs to, such as `/dev/stdout`. |
   | `jsonFormat` | The structured JSON format to write logs in. For more information about the JSON format dictionaries and command operators you can use, see the [Envoy docs](https://www.envoyproxy.io/docs/envoy/latest/configuration/observability/access_log/usage#format-dictionaries). To format as a string, use the `stringFormat` setting instead. If you omit or leave this setting blank, the [Envoy default format string](https://www.envoyproxy.io/docs/envoy/latest/configuration/observability/access_log/usage#default-format-string) is used. |
   | `stringFormat` | The string format to write logs in. For more information about the string format and command operators you can use, see the [Envoy docs](https://www.envoyproxy.io/docs/envoy/latest/configuration/observability/access_log/usage#config-access-log-format-strings). To format as JSON, use the `jsonFormat` setting instead. If you omit or leave this setting blank, the [Envoy default format string](https://www.envoyproxy.io/docs/envoy/latest/configuration/observability/access_log/usage#default-format-string) is used. |

2. Send a request to the httpbin app on the `www.example.com` domain. Verify that your request succeeds and that you get back a 200 HTTP response code.  
   
   {{< tabs tabTotal="2" items="Cloud Provider LoadBalancer,Port-forward for local testing" >}}
   {{% tab tabName="Cloud Provider LoadBalancer" %}}
   ```sh
   curl -i http://$INGRESS_GW_ADDRESS:8080/status/200 -H "host: www.example.com:8080"
   ```
   {{% /tab %}}
   {{% tab tabName="Port-forward for local testing" %}}
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
   
3. Get the logs for the gateway pod and verify that you see a stdout JSON entry for each request that you sent to the httpbin app. 
   
   ```sh
   kubectl -n {{< reuse "docs/snippets/namespace.md" >}} logs deployments/http | tail -1 | jq --sort-keys
   ```
   
   Example output: 
   ```json
   {
     "authority": "www.example.com:8080",
     "bytes_received": 0,
     "bytes_sent": 0,
     "method": "GET",
     "path": "/status/200",
     "protocol": "HTTP/1.1",
     "req_x_forwarded_for": null,
     "request_id": "a6758866-0f26-4c95-95d9-4032c365c498",
     "resp_backend_service_time": "0",
     "response_code": 200,
     "response_flags": "-",
     "start_time": "2024-08-19T20:57:57.511Z",
     "total_duration": 1,
     "backendCluster": "kube-svc:httpbin-httpbin-8000_httpbin",
     "backendHost": "10.36.0.14:8080",
     "user_agent": "curl/7.77.0"
   }
   ```
<!-- TODO

Need to figure out how to mount a volume for file-based

## Access logs to a file {#access-log-file-filesink}

You can set up access logs to write to a file. The following example writes access logs to a text file in a volume that is mounted to the selected `http` gateway.

1. Create a GatewayParameters resource to set up a special `access-logs` volume for your gateway proxy.

   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.kgateway.dev/v1alpha1
   kind: GatewayParameters
   metadata:
     name: gateway-config-access-logs
     namespace: {{< reuse "docs/snippets/namespace.md" >}}
   spec:
     kube:
       envoyContainer:
         volumeMounts:
           - mountPath: /dev/
             name: access-logs
       podTemplate:
         volumes:
           - name: access-logs
             emptyDir: {}  # Creates a writable volume for the logs
   EOF
   ```

2. Update the `http` Gateway to use the GatewayParameters that you created.

   ```yaml
   kubectl apply -f- <<EOF
   kind: Gateway
   apiVersion: gateway.networking.k8s.io/v1
   metadata:
     name: http
     namespace: {{< reuse "docs/snippets/namespace.md" >}}
   spec:
     gatewayClassName: kgateway
     infrastructure:
       parametersRef:
         name: gateway-config-access-logs
         group: gateway.kgateway.dev
         kind: GatewayParameters        
     listeners:
     - protocol: HTTP
       port: 8080
       name: http
       allowedRoutes:
         namespaces:
           from: All
   EOF
   ```

3. Create an HTTPListenerPolicy resource to define your access logging rules. The following example writes access logs in string format to the `/dev/default-access-logs.txt` file in the volume of the gateway proxy. 
   
   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.kgateway.dev/v1alpha1
   kind: HTTPListenerPolicy
   metadata:
     name: access-logs
     namespace: {{< reuse "docs/snippets/namespace.md" >}}
   spec:
     targetRefs:
     - group: gateway.networking.k8s.io
       kind: Gateway
       name: http
     accessLog:
     - fileSink:
         path: /dev/default-access-logs.txt
         stringFormat: ""
   EOF
   ```

   | Setting | Description |
   | ------- | ----------- |
   | `targetRefs`| Select the Gateway to enable access logging for. The example selects the `http` gateway that you created from the sample app guide. |
   | `accessLog` | Configure the details for access logging. You can use multiple `fileSink` configurations for multiple outputs. The example sets up a `fileSink` for string access logs to a text file. You can also send the access logs to a `grpcService` instead of `fileSink`. |
   | `path` | The path in the gateway proxy to write access logs to, such as `/dev/default-access-logs.txt`. Because this value is a file, make sure that the gateway you select mounts a volume with this path. |
   | `jsonFormat` | The structured JSON format to write logs in. For more information about the JSON format dictionaries and command operators you can use, see the [Envoy docs](https://www.envoyproxy.io/docs/envoy/latest/configuration/observability/access_log/usage#format-dictionaries). To format as a string, use the `stringFormat` setting instead. If you omit or leave this setting blank, the [Envoy default format string](https://www.envoyproxy.io/docs/envoy/latest/configuration/observability/access_log/usage#default-format-string) is used. |
   | `stringFormat` | The string format to write logs in. For more information about the string format and command operators you can use, see the [Envoy docs](https://www.envoyproxy.io/docs/envoy/latest/configuration/observability/access_log/usage#config-access-log-format-strings). To format as JSON, use the `jsonFormat` setting instead. If you omit or leave this setting blank, the [Envoy default format string](https://www.envoyproxy.io/docs/envoy/latest/configuration/observability/access_log/usage#default-format-string) is used. |

4. Send a request to the httpbin app on the `www.example.com` domain. Verify that your request succeeds and that you get back a 200 HTTP response code.  
   
   {{< tabs tabTotal="2" items="Cloud Provider LoadBalancer,Port-forward for local testing" >}}
   {{% tab tabName="Cloud Provider LoadBalancer" %}}
   ```sh
   curl -i http://$INGRESS_GW_ADDRESS:8080/status/200 -H "host: www.example.com:8080"
   ```
   {{% /tab %}}
   {{% tab tabName="Port-forward for local testing" %}}
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
   
5. Check the access log file in the gateway pod and verify that you see a string entry for each request that you sent to the httpbin app. 
   
   ```sh
   kubectl -n {{< reuse "docs/snippets/namespace.md" >}} exec -it deploy/http -- cat /dev/default-access-logs.txt
   ```
   
   Example output: 
   ```txt
   
   ```
-->
<!-- TODO updated for gRPC service

## Set up access logging to a gRPC service {#access-log-grpc}

You send access logs to a gRPC service. This way, you can collect logs from several gateways in a central location that is integrated with an existing log collecting service that you might already use, such as OpenTelemetry. This option performs better than writing to stdout for scalable, high traffic scenarios.

1. Create or get the details of the gRPC service. The following example creates a simple `log-test` service in the {{< reuse "docs/snippets/namespace.md" >}} namespace that listens on port 50051.

2. Create an HTTPListenerPolicy resource to define your access logging rules. The following example writes access logs to gRPC service that you created in the previous step. It logs requests that use the `x-my-cool-test-filter` header when the value is `test`. For more Envoy filters, see the [Envoy access log docs](https://www.envoyproxy.io/docs/envoy/latest/api-v3/config/accesslog/v3/accesslog.proto).  
   
   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.kgateway.dev/v1alpha1
   kind: HTTPListenerPolicy
   metadata:
     name: access-logs
     namespace: {{< reuse "docs/snippets/namespace.md" >}}
   spec:
     targetRefs:
     - group: gateway.networking.k8s.io
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
   
   {{< tabs tabTotal="2" items="Cloud Provider LoadBalancer,Port-forward for local testing" >}}
   {{% tab tabName="Cloud Provider LoadBalancer" %}}
   ```sh
   curl -i http://$INGRESS_GW_ADDRESS:8080/status/200 -H "host: www.example.com:8080" -H "x-my-cool-test-filter:test"
   ```
   {{% /tab %}}
   {{% tab tabName="Port-forward for local testing" %}}
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
   
   {{< tabs tabTotal="2" items="Cloud Provider LoadBalancer,Port-forward for local testing" >}}
   {{% tab tabName="Cloud Provider LoadBalancer" %}}
   ```sh
   curl -i http://$INGRESS_GW_ADDRESS:8080/status/200 -H "host: www.example.com:8080" -H "x-my-cool-test-filter:test"
   ```
   {{% /tab %}}
   {{% tab tabName="Port-forward for local testing" %}}
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
   kubectl -n {{< reuse "docs/snippets/namespace.md" >}} logs deployments/log-test | tail -1 | jq --sort-keys
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
     "resp_backend_service_time": "0",
     "response_code": 200,
     "response_flags": "-",
     "start_time": "2024-08-19T20:57:57.511Z",
     "total_duration": 1,
     "backendCluster": "kube-svc:httpbin-httpbin-8000_httpbin",
     "backendHost": "10.36.0.14:8080",
     "user_agent": "curl/7.77.0"
   }
   ```

-->

## Cleanup

{{< reuse "docs/snippets/cleanup.md" >}}

```sh
kubectl delete HTTPListenerPolicy access-logs -n {{< reuse "docs/snippets/namespace.md" >}}
```

