Capture an access log for all the requests that enter the gateway. 

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

{{< reuse "kgw-docs/snippets/prereq.md" >}}

## Access logs to `stdout` {#access-log-stdout-filesink}

You can set up access logs to write to a standard (stdout/stderr) stream. The following example writes access logs to a stdout in the pod of the selected `http` gateway.

1. Create a ListenerPolicy resource to define your access logging rules. The following example writes access logs to the `stdout` stream of the gateway proxy container by using a custom string format that is defined in the `jsonFormat` field. 

   ```yaml 
   kubectl apply -f- <<EOF
   apiVersion: gateway.kgateway.dev/v1alpha1
   kind: ListenerPolicy
   metadata:
     name: access-logs
     namespace: kgateway-system
   spec:
     targetRefs:
     - group: gateway.networking.k8s.io
       kind: Gateway
       name: http
     default:
       httpSettings:
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
   
   {{< tabs >}}
   {{% tab name="Cloud Provider LoadBalancer" %}}
   ```sh
   curl -i http://$INGRESS_GW_ADDRESS:8080/status/200 -H "host: www.example.com:8080"
   ```
   {{% /tab %}}
   {{% tab name="Port-forward for local testing" %}}
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
   kubectl -n {{< reuse "kgw-docs/snippets/namespace.md" >}} logs deployments/http | tail -1 | jq
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
## Other configurations

Review other common configurations. 

### String format {#string-format}

Instead of a JSON format, you can write access logs as a plain string by using the `stringFormat` field. For longer format strings, a [YAML block scalar](https://yaml.org/spec/1.2-old/spec.html#id2794534) is easier to read and maintain than escaping special characters in a quoted string.

> [!NOTE]
> Do not use single-quoted strings in the `stringFormat` field. Single-quoted YAML strings do not interpret escape sequences. Because of that, `\n` is stored as the literal characters `\` and `n` instead of a newline. Note that Kubernetes also stores `stringFormat` values with single quotes by default, so adding `\n` via the `kubectl edit` command also does not add a newline. Instead, use a block scalar as shown in the following example, which automatically adds the trailing newline that Envoy requires.

The following example uses the folded block scalar (`>`) syntax. The `>` operator converts the line break between the two content lines into a space, so that it produces a single-line string. A trailing newline is also appended, which Envoy requires in the format string.

```yaml
kubectl apply -f- <<EOF
apiVersion: gateway.kgateway.dev/v1alpha1
kind: ListenerPolicy
metadata:
  name: access-logs
  namespace: kgateway-system
spec:
  targetRefs:
  - group: gateway.networking.k8s.io
    kind: Gateway
    name: http
  default:
    httpSettings:
      accessLog:
        - fileSink:
            path: /dev/stdout
            stringFormat: >
              [%START_TIME%] "%REQ(:METHOD)% %REQ(X-ENVOY-ORIGINAL-PATH?:PATH)%"
              "%PROTOCOL%" "%RESPONSE_CODE%" "%RESPONSE_FLAGS%"
EOF
```

| Setting | Description |
| ------- | ----------- |
| `stringFormat` | The string format to write logs in. For more information about the string format and command operators you can use, see the [Envoy docs](https://www.envoyproxy.io/docs/envoy/latest/configuration/observability/access_log/usage#config-access-log-format-strings). To format as JSON, use the `jsonFormat` setting instead. If you omit or leave this setting blank, the [Envoy default format string](https://www.envoyproxy.io/docs/envoy/latest/configuration/observability/access_log/usage#default-format-string) is used. |

After sending a request to your app, check the gateway logs to see an entry similar to the following:

```sh
kubectl -n {{< reuse "kgw-docs/snippets/namespace.md" >}} logs deployments/http | tail -1
```

Example output:
```console
[2024-08-19T20:57:57.511Z] "GET /headers" "HTTP/1.1" "200" "-"
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
     namespace: {{< reuse "kgw-docs/snippets/namespace.md" >}}
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
     namespace: {{< reuse "kgw-docs/snippets/namespace.md" >}}
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

3. Create a ListenerPolicy resource to define your access logging rules. The following example writes access logs in string format to the `/dev/default-access-logs.txt` file in the volume of the gateway proxy. 
   
   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.kgateway.dev/v1alpha1
   kind: ListenerPolicy
   metadata:
     name: access-logs
     namespace: {{< reuse "kgw-docs/snippets/namespace.md" >}}
   spec:
     targetRefs:
     - group: gateway.networking.k8s.io
       kind: Gateway
       name: http
     default:
       httpSettings:
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
   
   {{< tabs >}}
   {{% tab name="Cloud Provider LoadBalancer" %}}
   ```sh
   curl -i http://$INGRESS_GW_ADDRESS:8080/status/200 -H "host: www.example.com:8080"
   ```
   {{% /tab %}}
   {{% tab name="Port-forward for local testing" %}}
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
   kubectl -n {{< reuse "kgw-docs/snippets/namespace.md" >}} exec -it deploy/http -- cat /dev/default-access-logs.txt
   ```
   
   Example output: 
   ```txt
   
   ```
-->
<!-- TODO updated for gRPC service

## Set up access logging to a gRPC service {#access-log-grpc}

You send access logs to a gRPC service. This way, you can collect logs from several gateways in a central location that is integrated with an existing log collecting service that you might already use, such as OpenTelemetry. This option performs better than writing to stdout for scalable, high traffic scenarios.

1. Create or get the details of the gRPC service. The following example creates a simple `log-test` service in the {{< reuse "kgw-docs/snippets/namespace.md" >}} namespace that listens on port 50051.

2. Create a ListenerPolicy resource to define your access logging rules. The following example writes access logs to gRPC service that you created in the previous step. It logs requests that use the `x-my-cool-test-filter` header when the value is `test`. For more Envoy filters, see the [Envoy access log docs](https://www.envoyproxy.io/docs/envoy/latest/api-v3/config/accesslog/v3/accesslog.proto).  
   
   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.kgateway.dev/v1alpha1
   kind: ListenerPolicy
   metadata:
     name: access-logs
     namespace: {{< reuse "kgw-docs/snippets/namespace.md" >}}
   spec:
     targetRefs:
     - group: gateway.networking.k8s.io
       kind: Gateway
       name: http
     default:
       httpSettings:
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
   
   {{< tabs >}}
   {{% tab name="Cloud Provider LoadBalancer" %}}
   ```sh
   curl -i http://$INGRESS_GW_ADDRESS:8080/status/200 -H "host: www.example.com:8080" -H "x-my-cool-test-filter:test"
   ```
   {{% /tab %}}
   {{% tab name="Port-forward for local testing" %}}
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

4. Send another request, this time with the header that you configured in the ListenerPolicy. Verify that your request succeeds and that you get back a 200 HTTP response code.  
   
   {{< tabs >}}
   {{% tab name="Cloud Provider LoadBalancer" %}}
   ```sh
   curl -i http://$INGRESS_GW_ADDRESS:8080/status/200 -H "host: www.example.com:8080" -H "x-my-cool-test-filter:test"
   ```
   {{% /tab %}}
   {{% tab name="Port-forward for local testing" %}}
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
   kubectl -n {{< reuse "kgw-docs/snippets/namespace.md" >}} logs deployments/log-test | tail -1 | jq --sort-keys
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

{{< version exclude-if="2.0.x,2.1.x,2.2.x,2.3.x" >}}

### Route source metadata {#route-source-metadata}

> [!WARNING]
> This feature is an experimental API and subject to breaking changes in future releases.

You can optionally enable kgateway to attach route source metadata to every Envoy route. When enabled, each Envoy route carries a `dev.kgateway.route_source` filter metadata entry that identifies the originating Kubernetes route resource by `kind`, `group`, `name`, `namespace`, {{< version include-if="2.4.x" >}}and `rule`{{< /version >}}{{< version exclude-if="2.0.x,2.1.x,2.2.x,2.3.x,2.4.x" >}}`rule`, and `match`{{< /version >}}. You can reference these fields in your access log format strings by using the `%METADATA(ROUTE:dev.kgateway.route_source:<field>)%` command operator.

1. Get the Helm values file for your current installation and save the values to a local file. 
   ```sh
   helm get values {{< reuse "/kgw-docs/snippets/helm-kgateway.md" >}} -n kgateway-system -o yaml > values.yaml
   open values.yaml
   ```

2. Add the following setting to your values file to enable route source metadata.
   ```yaml
   enableRouteSourceMetadata: true
   ```

3. Upgrade your installation to enable the feature.
   ```sh
   helm upgrade -i -n {{< reuse "kgw-docs/snippets/namespace.md" >}} {{< reuse "/kgw-docs/snippets/helm-kgateway.md" >}} oci://{{< reuse "/kgw-docs/snippets/helm-path.md" >}}/charts/{{< reuse "/kgw-docs/snippets/helm-kgateway.md" >}} \
     -f values.yaml \
     --version {{< reuse "kgw-docs/versions/n-patch.md" >}} 
   ```

4. Update your ListenerPolicy to include route source metadata fields in your access log format. The following example adds the `kind`, `name`, `namespace`, {{< version include-if="2.4.x" >}}and `rule`{{< /version >}}{{< version exclude-if="2.0.x,2.1.x,2.2.x,2.3.x,2.4.x" >}}`rule`, and `match`{{< /version >}} of the originating route resource to the JSON access log output.
   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.kgateway.dev/v1alpha1
   kind: ListenerPolicy
   metadata:
     name: access-logs
     namespace: kgateway-system
   spec:
     targetRefs:
     - group: gateway.networking.k8s.io
       kind: Gateway
       name: http
     default:
       httpSettings:
         accessLog:
           - fileSink:
               path: /dev/stdout
               jsonFormat:
                 start_time: "%START_TIME%"
                 method: "%REQ(X-ENVOY-ORIGINAL-METHOD?:METHOD)%"
                 path: "%REQ(X-ENVOY-ORIGINAL-PATH?:PATH)%"
                 response_code: "%RESPONSE_CODE%"
                 route_kind: "%METADATA(ROUTE:dev.kgateway.route_source:kind)%"
                 route_name: "%METADATA(ROUTE:dev.kgateway.route_source:name)%"
                 route_namespace: "%METADATA(ROUTE:dev.kgateway.route_source:namespace)%"
                 route_rule: "%METADATA(ROUTE:dev.kgateway.route_source:rule)%"{{< version exclude-if="2.0.x,2.1.x,2.2.x,2.3.x,2.4.x" >}}
                 route_match: "%METADATA(ROUTE:dev.kgateway.route_source:match)%"{{< /version >}}
   EOF
   ```

   | Field | Description |
   | ----- | ----------- |
   | `%METADATA(ROUTE:dev.kgateway.route_source:kind)%` | The kind of the Kubernetes route resource, such as `HTTPRoute`. |
   | `%METADATA(ROUTE:dev.kgateway.route_source:name)%` | The name of the Kubernetes route resource. |
   | `%METADATA(ROUTE:dev.kgateway.route_source:namespace)%` | The namespace of the Kubernetes route resource. |
   | `%METADATA(ROUTE:dev.kgateway.route_source:group)%` | The API group of the Kubernetes route resource. |
   | `%METADATA(ROUTE:dev.kgateway.route_source:rule)%` | {{< version include-if="2.4.x" >}}The generated name of the Envoy route that the route rule translates into, in the format `<kind>-<name>-<namespace>-<rule_index>-<match_index>-<rule_name>`, such as `httproute-my-route-default-0-0-to-backend`. If the rule has no name, the `-<rule_name>` suffix is omitted.{{< /version >}}{{< version exclude-if="2.0.x,2.1.x,2.2.x,2.3.x,2.4.x" >}}The name of the rule in the route resource that matched the request, such as `to-backend`. If the rule has no name, the value is `_rule-<index>`, where `<index>` is the zero-based position of the rule in the `rules` list, such as `_rule-1`. The `_` prefix keeps generated values from colliding with rule names, because Gateway API rule names must start with a letter.{{< /version >}} |{{< version exclude-if="2.0.x,2.1.x,2.2.x,2.3.x,2.4.x" >}}
   | `%METADATA(ROUTE:dev.kgateway.route_source:match)%` | The match in the rule that the Envoy route was generated from, in the format `_match-<index>`, where `<index>` is the zero-based position of the match in the rule's `matches` list, such as `_match-0`. Together, `rule` and `match` identify the exact match that handled the request. |{{< /version >}}

{{< /version >}}

{{< version exclude-if="2.0.x,2.1.x,2.2.x,2.3.x,2.4.x" >}}

### Log ext-auth latency {#extauth-latency}

If you use an external auth service, you can write the time that the external auth check took for each request to your access logs. The data is emitted from the Envoy `ext_authz` filter and is available for every request that makes an external auth check, including requests that the service denies. For more information, see the [Envoy `ext_authz` filter documentation](https://www.envoyproxy.io/docs/envoy/latest/configuration/http/http_filters/ext_authz_filter#logging).

1. Set up external auth for your gateway or route. For more information, see [External auth]({{< link-hextra path="/security/extauth/" >}}).

2. Update your ListenerPolicy to include the extauth fields in your access log format. The following example adds the latency of the external auth check and the number of bytes that were sent and received to the JSON access log output.

   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.kgateway.dev/v1alpha1
   kind: ListenerPolicy
   metadata:
     name: access-logs
     namespace: kgateway-system
   spec:
     targetRefs:
     - group: gateway.networking.k8s.io
       kind: Gateway
       name: http
     default:
       httpSettings:
         accessLog:
           - fileSink:
               path: /dev/stdout
               jsonFormat:
                 response_code: "%RESPONSE_CODE%"
                 extauth_latency_us: "%FILTER_STATE(ext_auth/kgateway-system/basic-ext-auth:FIELD:latency_us)%"
                 extauth_bytes_sent: "%FILTER_STATE(ext_auth/kgateway-system/basic-ext-auth:FIELD:bytesSent)%"
                 extauth_bytes_received: "%FILTER_STATE(ext_auth/kgateway-system/basic-ext-auth:FIELD:bytesReceived)%"
   EOF
   ```

   Envoy uses the name of the filter as the filter state key. {{< reuse "kgw-docs/snippets/kgateway-capital.md" >}} names each ext-auth filter `ext_auth/<namespace>/<name>`, where `<namespace>` and `<name>` are the namespace and name of your GatewayExtension resource. In this example, the GatewayExtension is named `basic-ext-auth` and is in the `kgateway-system` namespace. Use this key instead of the `envoy.filters.http.ext_authz` key that is shown in the Envoy documentation.

   | Field | Description |
   | ----- | ----------- |
   | `latency_us` | The time in microseconds that the external auth check took. |
   | `bytesSent` | The number of bytes that the gateway proxy sent to the external auth service. Available only for gRPC external auth services. |
   | `bytesReceived` | The number of bytes that the gateway proxy received from the external auth service. Available only for gRPC external auth services. |

3. Send a request to a route that your external auth policy protects.

4. Get the logs for the gateway pod and verify that the entry includes the ext-auth fields.

   ```sh
   kubectl -n {{< reuse "kgw-docs/snippets/namespace.md" >}} logs deployments/http | tail -1 | jq
   ```

   Example output:
   ```json
   {
     "extauth_bytes_received": "1135",
     "extauth_bytes_sent": "638",
     "extauth_latency_us": "1643",
     "response_code": 200
   }
   ```

   The ext-auth values are written as strings. Envoy adds the ext-auth fields only for requests that make a check call to the external auth service.

> [!NOTE]
> The `%FILTER_STATE(<key>:TYPED)%` format is not supported for external auth. Use the `FIELD` format as shown in the example.

{{< /version >}}

{{< version exclude-if="2.0.x,2.1.x,2.2.x,2.3.x,2.4.x" >}}
## Access logs for TCP and TLS listeners {#tcp-access-log}

The `httpSettings.accessLog` field applies to HTTP and HTTPS listeners. To log connections on listeners that serve TCPRoutes or TLSRoutes, set the `tcpSettings.accessLog` field in a ListenerPolicy instead. This field applies to TCP listeners and to TLS listeners in both the `Terminate` and `Passthrough` modes. The proxy writes one log entry for each connection, and not for each request.

1. Set up a TCP listener and a TCPRoute, such as in the [TCP listener]({{< link-hextra path="/setup/listeners/tcp/" >}}) guide.

2. Create a ListenerPolicy that logs each connection to the `stdout` stream of the gateway proxy. In `targetRefs`, select the `tcp-gateway` Gateway from the TCP listener guide. Because TCP connections have no HTTP properties, the format uses only data that is available for TCP, such as the addresses, bytes, and duration of the connection.
   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.kgateway.dev/v1alpha1
   kind: ListenerPolicy
   metadata:
     name: tcp-access-logs
     namespace: {{< reuse "kgw-docs/snippets/namespace.md" >}}
   spec:
     targetRefs:
     - group: gateway.networking.k8s.io
       kind: Gateway
       name: tcp-gateway
     default:
       tcpSettings:
         accessLog:
         - fileSink:
             path: /dev/stdout
             jsonFormat:
               start_time: "%START_TIME%"
               downstream_remote_address: "%DOWNSTREAM_REMOTE_ADDRESS%"
               upstream_host: "%UPSTREAM_HOST%"
               bytes_received: "%BYTES_RECEIVED%"
               bytes_sent: "%BYTES_SENT%"
               duration: "%DURATION%"
               response_flags: "%RESPONSE_FLAGS%"
   EOF
   ```

3. Send a TCP request to the gateway, such as in the [verify steps]({{< link-hextra path="/setup/listeners/tcp/#verify-tcp-route" >}}) of the TCP listener guide.

4. Get the logs of the gateway proxy. The proxy writes the log entry when the connection closes.
   ```sh
   kubectl logs deploy/tcp-gateway -n {{< reuse "kgw-docs/snippets/namespace.md" >}} | tail -n 1
   ```

   Example output:
   ```json
   {"bytes_received":88,"bytes_sent":147,"downstream_remote_address":"127.0.0.1:49638","duration":1004,"response_flags":"-","start_time":"2026-10-27T20:56:15.708Z","upstream_host":"10.244.0.96:8080"}
   ```

The `tcpSettings.accessLog` field accepts the same sinks as `httpSettings.accessLog`, such as `fileSink`, `grpcService`, and `openTelemetry`, with the following differences:

* **HTTP-only settings are rejected**: The `statusCodeFilter`, `headerFilter`, `grpcStatusFilter`, and `traceableFilter` filters, and the `additional*ToLog` fields of `grpcService`, apply only to HTTP traffic. If you set them, the ListenerPolicy is not accepted. The status of the policy names the field that is not supported, such as `filter.statusCodeFilter is not supported for TCP access logs`.
* **gRPC sinks use the TCP gRPC access log service**: The proxy sends the entries to your service with Envoy's TCP gRPC access logger. Make sure that your access log service handles TCP log entries.
* **Section policies apply only to the listener with settings**: If you target a listener with `sectionName`, the policy reports a status for a TCP or TLS listener only when it sets `tcpSettings` or `transportSocketConnectTimeout`.
{{< /version >}}

## Cleanup

{{< reuse "kgw-docs/snippets/cleanup.md" >}}

```sh
kubectl delete ListenerPolicy access-logs -n {{< reuse "kgw-docs/snippets/namespace.md" >}}
```




