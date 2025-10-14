Learn more about the custom resources that you can use to apply policies in kgateway. 


While the {{< reuse "docs/snippets/k8s-gateway-api-name.md" >}} allows you to do simple routing, such as to match, redirect, or rewrite requests, you might want additional capabilities in your API gateway, such direct responses, local rate limiting, or request and response transformations. Policies allow you to apply intelligent traffic management, resiliency, and security standards to an HTTPRoute or Gateway. 

## Policy CRDs

Kgateway uses the following custom resources to attach policies to routes and gateway listeners. 

{{< cards >}}
  {{< card link="../policies/backendconfigpolicy/" title="BackendConfigPolicy" subtitle="Configure connection settings to an upstream service." >}}
  {{< card link="../../traffic-management/direct-response/" title="Direct response" subtitle="Directly respond to incoming requests with a custom HTTP response code and body." >}}
  {{< card link="../policies/httplistenerpolicy/" title="HTTPListenerPolicy" subtitle="Apply policies to all HTTP and HTTPS listeners." >}}
  {{< card link="../policies/trafficpolicy/" title="TrafficPolicy" subtitle="Attach policies to routes in an HTTPRoute or Gateway resource." >}}
{{< /cards >}}



## Supported policies {#supported-policies}

Review the policies that you can configure in kgateway and the level at which you can apply them.   

| Policy | Applied via |
| -- | -- | 
| [Access logging](../../security/access-logging) | HTTPListenerPolicy |
| [Buffering](../../traffic-management/buffering)| {{< reuse "docs/snippets/trafficpolicy.md" >}} | 
| [CSRF](../../security/csrf)| {{< reuse "docs/snippets/trafficpolicy.md" >}} | 
| [Direct response](../../traffic-management/direct-response/) | DirectResponse | 
| [Dynamic Forward Proxy (DFP)](../../traffic-management/dfp)| Backend and HTTPRoute | 
| [External authorization](../../security/external-auth) | GatewayExtension and {{< reuse "docs/snippets/trafficpolicy.md" >}} |
| [External processing (ExtProc)](../../traffic-management/extproc/) | {{< reuse "docs/snippets/trafficpolicy.md" >}} | 
| [Health checks for the Gateway](../../traffic-management/health-checks/gateway)| HTTPListenerPolicy | 
| [Health checks for the Backends](../../traffic-management/health-checks/backend)| BackendConfigPolicy |{{%  version include-if="2.1.x" %}} 
| [HTTP connection settings](../../resiliency/connection)| BackendConfigPolicy | 
| [Outlier detection](../../resiliency/outlier-detection)| BackendConfigPolicy | {{% /version %}}
| [Rate limiting](../../security/ratelimit/) | {{< reuse "docs/snippets/trafficpolicy.md" >}} | 
| [Session affinity - Simple load balancing](../../traffic-management/session-affinity/loadbalancing/) | BackendConfigPolicy  | 
| [Session affinity - Consistent hashing](../../traffic-management/session-affinity/consistent-hashing/) | BackendConfigPolicy  | {{%  version include-if="2.1.x" %}} 
| [TCP keepalive](../../resiliency/tcp-keepalive/) | BackendConfigPolicy | {{% /version %}}
| [Transformations](../../traffic-management/transformations) | {{< reuse "docs/snippets/trafficpolicy.md" >}} | 