A timeout is the amount of time ([duration](https://protobuf.dev/reference/protobuf/google.protobuf/#duration)) that the gateway waits for replies from a backend service before the service is considered unavailable. This setting can be useful to avoid your apps from hanging or to fail if no response is returned in a specific timeframe. With timeouts, calls either succeed or fail within a predictable timeframe.

The time an app needs to process a request can vary a lot. For this reason, applying the same timeout across services can cause a variety of issues. For example, a timeout that is too long can result in excessive latency from waiting for replies from failing services. On the other hand, a timeout that is too short can result in calls failing unnecessarily while waiting for an operation that needs responses from multiple services.

## Configuration options

You can configure different types of timeouts by using a Kubernetes Gateway API-native configuration, HTTPListenerPolicy, or a {{< reuse "docs/snippets/trafficpolicy.md" >}} as shown in the following table.

| Type of timeout| Description | Configured via | Attach to | 
| -- | -- | -- | --- | 
| [Request timeout]({{< link-hextra path="/resiliency/timeouts/request/" >}}) | Request timeouts configure the time Envoy allows for the entire request stream to be received from the client. | <ul><li>HTTPRoute </li><li>{{< reuse "docs/snippets/trafficpolicy.md" >}} </li></ul>| <ul><li>HTTPRoute </li><li>HTTPRoute rule </li></ul> | 
| [Idle timeout]({{< link-hextra path="/resiliency/timeouts/idle/" >}})  | An idle timeout is the time when Envoy terminates the connection to a downstream or upstream service if there no active streams.| HTTPListenerPolicy | Gateway | 
| [Idle stream timeout]({{< link-hextra path="/resiliency/timeouts/idle-stream/" >}})  | An idle stream timeout is the time Envoy allows a stream to exist without activity before it is terminated. | {{< reuse "docs/snippets/trafficpolicy.md" >}} | <ul><li>HTTPRoute</li><li>HTTPRoute rule</li></ul> | 
| [Per-try timeout]({{< link-hextra path="/resiliency/retry/per-try-timeout" >}}) | Set a shorter timeout for retries than the overall request timeout.  | <ul><li>HTTPRoute</li><li>{{< reuse "docs/snippets/trafficpolicy.md" >}} </li></ul>| <ul><li>HTTPRoute </li><li>HTTPRoute rule</li><li>Gateway listener ({{< reuse "docs/snippets/trafficpolicy.md" >}} only)</li></ul> | 


