---
title: HTTPListenerPolicy
weight: 10
description: You can use an HTTPListenerPolicy resource to attach policies to HTTP or HTTPS listeners on the gateway. 
---

You can use an HTTPListenerPolicy resource to attach policies to HTTP or HTTPS listeners on the gateway.

{{< callout type="info" >}}
{{< reuse "docs/snippets/global-policy.md" >}}
{{< /callout >}}

## Policy attachment {#policy-attachment-listeneroption}

<!--

Learn more about how you can attach policies to HTTP or HTTPS listeners. 

### Option 1: Attach the policy to all listeners on the gateway (`targetRefs`) -->

You can apply a policy to all HTTP and HTTPS listeners that are defined on the gateway by using the `spec.targetRefs` section in the HTTPListenerPolicy resource. 

The following HTTPListenerPolicy resource configures access logs on a Gateway that is named `http`. The policy applies to all the HTTP and HTTPS listeners that are defined on the gateway. 

```yaml {hl_lines=[7,8,9,10]} 
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
```

<!--

### Option 2: Attach the policy to a particular listener on the gateway (`targetRefs.sectionName`)

Instead of attaching a policy to all the HTTP and HTTPs listeners that are defined on the gateway, you can target a particular HTTP or HTTPS listener by using the `spec.targetRefs.sectionName` field in the HTTPListenerPolicy resource. 

The following Gateway resource defines two listeners, an HTTP (`http`) and HTTPS (`https`) listener. 

```console {hl_lines=[8,15]} 
kind: Gateway
apiVersion: gateway.networking.k8s.io/v1
metadata:
  name: http
spec:
  gatewayClassName: kgateway
  listeners:
  - name: http
    protocol: HTTP
    port: 8080
    allowedRoutes:
      namespaces:
        from: All
    hostname: www.example.com
  - name: https
    port: 443
    protocol: HTTPS
    hostname: https.example.com
    tls:
      mode: Terminate
      certificateRefs:
        - name: https
          kind: Secret
    allowedRoutes:
      namespaces:
        from: All
```

To apply the policy to only the `https` listener, you specify the listener name in the `spec.targetRefs.sectionName` field in the HTTPListenerPolicy resource as shown in the following example. 

```console {hl_lines=[11]} 
apiVersion: gateway.kgateway.dev/v1alpha1
kind: HTTPListenerPolicy
metadata:
  name: server-name
  namespace: kgateway-system
spec:
  targetRefs:
  - group: gateway.networking.k8s.io
    kind: Gateway
    name: http
    sectionName: https
  options:
    httpConnectionManagerSettings:
      serverName: "myserver"
```
-->

## Conflicting policies

If you create multiple HTTPListenerPolicy resources that define the same type of top-level policy, and attach them to the same gateway by using the `targetRefs` option, only the HTTPListenerPolicy that was last applied is enforced. 

<!--

{{< callout type="info" >}}
You cannot attach multiple HTTPListenerPolicy resources to the same listener, *even if* they define different top-level policies. To add multiple policies, define them in the same HTTPListenerPolicy resource.
{{< /callout >}}

In the following image, you want to attach two HTTPListenerPolicy resources to the HTTP listener. One configures local rate limiting and the other one configures a CSRF policy. Because only one HTTPListenerPolicy can be attached to a gateway listener via `targetRefs` at any given time, only the policy that is created first is enforced (policy 1). 

{{< reuse-image src="img/policy-ov-multiple-httplisteneroption.svg" width="800" >}}
-->