---
title: HTTP connection settings
weight: 10 
description: Configure and manage HTTP connections to an upstream service. 
---

Configure and manage HTTP connections to an upstream service. 

{{< callout >}}
{{< reuse "docs/snippets/proxy-kgateway.md" >}}
{{< /callout >}}

## Supported HTTP connection settings

You can use a BackendConfigPolicy to apply HTTP connection settings to a service in your cluster. These settings include general settings, such as connection timeouts or the maximum number of connections that an upstream service can receive. You can also configure settings for HTTP/2 and HTTP/1 requests. 

* [General connection settings](#general-settings)
* [HTTP protocol options](#http)
* [Additional HTTP 1.0 protocol options](#http1)

### General connection settings {#general-settings}

Configure the timeout and read/write buffer limits for a connection. 

```yaml 
kind: BackendConfigPolicy
apiVersion: gateway.kgateway.dev/v1alpha1
metadata:
  name: httpbin-policy
  namespace: gwtest
spec:
  targetRefs:
    - name: httpbin
      group: ""
      kind: Service
  connectTimeout: 5s
  perConnectionBufferLimitBytes: 1024
```

| Setting | Description | 
| -- | -- | 
| `connectTimeout` | The timeout for new network connections to an upstream service. | 
| `perConnectionBufferLimitBytes` | Set the size of the read and write buffer per connection. By default, the gateway has a maximum of 1MiB for the read and write buffer for each connection. For large requests that must be buffered and that exceed the default buffer limit, the gateway proxy either disconnects the connection to the downstream service if headers were already sent, or returns a 500 HTTP response code. To make sure that large requests can be sent and received, you can specify the maximum number of bytes that you want to allow to be buffered between the gateway and the downstream service. | 

### HTTP protocol options {#http}

You can use a BackendConfigPolicy to configure additional connection options when handling upstream HTTP requests. Note that these options are applied to HTTP/1 and HTTP/2 requests. 

```yaml
kind: BackendConfigPolicy
apiVersion: gateway.kgateway.dev/v1alpha1
metadata:
  name: httpbin-policy
  namespace: gwtest
spec:
  targetRefs:
    - name: httpbin
      group: ""
      kind: Service
  commonHttpProtocolOptions:
    idleTimeout: 10s  
    maxHeadersCount: 15
    maxStreamDuration: 30s
    maxRequestsPerConnection: 100 
```

| Setting | Description | 
| -- | -- | 
| `idleTimeout` | The idle timeout for connections. The idle timeout is defined as the period in which there are no active requests. When the idle timeout is reached, the connection is closed. Note that request-based timeouts mean that HTTP/2 PINGs do not keep the connection alive. If not specified, the idle timeout defaults to 1 hour. To disable idle timeouts, explicitly set this field to 0. **Warning**: Disabling the timeout has a highly likelihood of yielding connection leaks, such as due to lost TCP FIN packets.| 
| `maxHeadersCount` | The maximum number of headers that can be sent in a connection. If not specified, the number defaults to 100. Requests that exceed this limit receive a 431 response for HTTP/1 and cause a stream reset for HTTP/2. | 
| `maxStreamDuration` | The total duration to keep alive an HTTP request/response stream. If the time limit is reached, the stream is reset independent of any other timeouts. If not specified, this value is not set. | 
| `maxRequestsPerConnection` | The maximum number of requests that can be sent per connection. | 
 

#### Additional HTTP 1.0 protocol options {#http1}

The BackendConfigPolicy allows you to apply additional configuration to HTTP/1 connections. 

```yaml
kind: BackendConfigPolicy
apiVersion: gateway.kgateway.dev/v1alpha1
metadata:
  name: httpbin-policy
  namespace: gwtest
spec:
  targetRefs:
    - name: httpbin
      group: ""
      kind: Service
  http1ProtocolOptions:
    enableTrailers: true
    overrideStreamErrorOnInvalidHttpMessage: true
    headerFormat: PreserveCaseHeaderKeyFormat
```

| Setting | Description | 
| -- | -- | 
| `enableTrailers` | Enables trailers for HTTP/1 requests. Trailers are headers that are sent after the request body is sent. By default, the HTTP/1 codec drops proxied trailers. | 
| `overrideStreamErrorOnInvalidHttpMessage` | When set to false, the proxy terminates HTTP/1.1 connections when an invalid HTTP message is received, such as malformatted headers. When set to true, the proxy leaves the HTTP/1.1 connection open where possible. | 
| `headerFormat` | By default, the proxy normalizes header keys to lowercase. Set to `PreserveCaseHeaderKeyFormat` to preserve the original casing after the request is proxied. Set to `properCaseHeaderKeyFormat` to capitalize the first character and any character following a special character if it’s an alpha character. For example, `content-type` becomes `Content-Type`, and `foo$b#$are` becomes `Foo$B#$Are`. |


## Before you begin

{{< reuse "docs/snippets/prereq.md" >}}

## Configure backend connections

1. Create a BackendConfigPolicy that applies connection configuration to the httpbin app. 
   ```yaml 
   kubectl apply -f- <<EOF
   kind: BackendConfigPolicy
   apiVersion: gateway.kgateway.dev/v1alpha1
   metadata:
     name: httpbin-connection
     namespace: httpbin   
   spec:
     targetRefs:
       - name: httpbin
         group: ""
         kind: Service
     connectTimeout: 5s
     perConnectionBufferLimitBytes: 1024
     commonHttpProtocolOptions:
       idleTimeout: 10s  
       maxHeadersCount: 15
       maxStreamDuration: 30s
       maxRequestsPerConnection: 100 
     http1ProtocolOptions:
       enableTrailers: true
       overrideStreamErrorOnInvalidHttpMessage: true
       headerFormat: PreserveCaseHeaderKeyFormat
   EOF
   ```   

2. Port-forward the gateway proxy on port 19000. 
   ```sh
   kubectl port-forward deployment/http -n {{< reuse "docs/snippets/namespace.md" >}} 19000
   ```
   
3. Get the configuration of your gateway proxy as a config dump. 
   ```sh
   curl -X POST 127.0.0.1:19000/config_dump\?include_eds > gateway-config.json
   ```
   
4. Open the config dump and find the `kube_httpbin_httpbin_8000` cluster. Verify that you see all the connection settings that you enabled in your BackendConfigPolicy. 
   
   Example output
   ```console
   ...
   "connect_timeout": "5s",
      "per_connection_buffer_limit_bytes": 1024,
      "metadata": {},
      "upstream_connection_options": {
      },
      "typed_extension_protocol_options": {
       "envoy.extensions.upstreams.http.v3.HttpProtocolOptions": {
        "@type": "type.googleapis.com/envoy.extensions.upstreams.http.v3.HttpProtocolOptions",
        "common_http_protocol_options": {
         "idle_timeout": "10s",
         "max_headers_count": 15,
         "max_stream_duration": "30s",
         "headers_with_underscores_action": "REJECT_REQUEST",
         "max_requests_per_connection": 100
        },
        "explicit_http_config": {
         "http_protocol_options": {
          "header_key_format": {
           "stateful_formatter": {
            "name": "envoy.http.stateful_header_formatters.preserve_case",
            "typed_config": {
             "@type": "type.googleapis.com/envoy.extensions.http.header_formatters.preserve_case.v3.PreserveCaseFormatterConfig"
            }
           }
          },
          "enable_trailers": true,
          "override_stream_error_on_invalid_http_message": true
         }
        }
       }
      }
   ...
   ```
    
## Cleanup

{{< reuse "docs/snippets/cleanup.md" >}}

```sh
kubectl delete backendconfigpolicy httpbin-connection -n httpbin
```
   