---
title: Policies
weight: 30
prev: /docs/about/proxies
next: /docs/about/policies/trafficpolicy
---

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
| [Backend connection config](../../resiliency/connection)| BackendConfigPolicy | 
| [Direct response](../../traffic-management/direct-response/) | DirectResponse | 
| [External authorization](../../security/external-auth) | GatewayExtension and {{< reuse "docs/snippets/trafficpolicy.md" >}} |
| [External processing (ExtProc)](../../traffic-management/extproc/) | {{< reuse "docs/snippets/trafficpolicy.md" >}} | 
| [Rate limiting](../../security/ratelimit/) | {{< reuse "docs/snippets/trafficpolicy.md" >}} | 
| [Transformations](../../traffic-management/transformations) | {{< reuse "docs/snippets/trafficpolicy.md" >}} | 
