Keep in mind that some variables are available only at certain times. For example, response codes (`%RESPONSE_CODE%`) are only available after the response has been sent to the client. If you set a response code in a request header, the value is empty. 

You might use some of the following common values in your request or response headers.

Request and response information:
- %REQ(:METHOD)% - HTTP method
- %REQ(:PATH)% - Request path
- %REQ(:AUTHORITY)% - Host header
- %REQ(HEADER_NAME)% - Any request header
- %RESP(HEADER_NAME)% - Any response header
- %RESPONSE_CODE% - HTTP response code
- %RESPONSE_FLAGS% - Response flags

Connection information:
- %DOWNSTREAM_REMOTE_ADDRESS% - Client IP address with port
- %DOWNSTREAM_REMOTE_ADDRESS_WITHOUT_PORT% - Client IP address without port
- %DOWNSTREAM_LOCAL_ADDRESS% - Local address
- %DOWNSTREAM_CONNECTION_ID% - Connection ID

Timing information:
- %START_TIME% - Request start time
- %DURATION% - Request duration

Upstream information:
- %UPSTREAM_HOST% - Upstream host
- %UPSTREAM_CLUSTER% - Upstream Envoy cluster
- %UPSTREAM_LOCAL_ADDRESS% - Upstream local address

Data transfer:
- %BYTES_RECEIVED% - Bytes received
- %BYTES_SENT% - Bytes sent

For more potential values, see [Command operators in the Envoy docs](https://www.envoyproxy.io/docs/envoy/latest/configuration/observability/access_log/usage.html#command-operators).