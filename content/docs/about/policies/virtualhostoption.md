---
title: VirtualHostOption
weight: 40
description: Use a VirtualHostOption resource to attach policies to the hosts on one, multiple, or all gateway listeners.
next: /docs/about/resource-validation 
---

Use a VirtualHostOption resource to attach policies to the hosts on one, multiple, or all gateway listeners. 

## Policy attachment {#policy-attachment-virtualhostoption}

Learn more about how you can attach policies to gateway listeners. 

### Option 1: Attach policies to the hosts on all gateway listeners (`targetRefs`)

You can use the `spec.targetRefs` section in the VirtualHostOption resource to attach policies to the hosts on all gateway listeners. 

The following VirtualHostOption resource defines a CSRF policy that is attached to the `http` Gateway resource. Because no gateway listener is defined, the policy is attached to all the hosts on all the listeners that are set up on the gateway. 

```yaml {hl_lines=[15,16,17,18,19]}
apiVersion: gateway.kgateway.dev/v1alpha1
kind: VirtualHostOption
metadata:
  name: csrf
  namespace: {{< reuse "docs/snippets/ns-system.md" >}}
spec:
  options:
    csrf:
      filterEnabled: 
        defaultValue: 
          numerator: 100
          denominator: HUNDRED
      additionalOrigins:
      - exact: allowThisOne.solo.io
  targetRefs:
  - group: gateway.networking.k8s.io
    kind: Gateway
    name: http
    namespace: {{< reuse "docs/snippets/ns-system.md" >}}
```

### Option 2: Attach the policy to a specific listener (`targetRefs.sectionName`)

Instead of applying a policy to all the hosts on all the listeners that are defined on the gateway, you can target a particular listener by using the `spec.targetRefs.sectionName` field in the VirtualHostOption resource. 

The following Gateway resource defines two listeners, an HTTP (`http`) and HTTPS (`https`) listener. Each listener defines a set of hostnames. 

```yaml {hl_lines=[8,15,16,17,18,21]}
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
    hostname: 
    - www.example.com
    - www.example.org
    - www.example.net
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

To attach the policy to only the hosts on the `https` listener, you specify the listener name in the `spec.targetRefs.sectionName` field of the VirtualHostOption resource as shown in the following example. 

```yaml {hl_lines=[20]}
apiVersion: gateway.kgateway.dev/v1alpha1
kind: VirtualHostOption
metadata:
  name: csrf
  namespace: {{< reuse "docs/snippets/ns-system.md" >}}
spec:
  options:
    csrf:
      filterEnabled: 
        defaultValue: 
          numerator: 100
          denominator: HUNDRED
      additionalOrigins:
      - exact: allowThisOne.solo.io
  targetRefs:
  - group: gateway.networking.k8s.io
    kind: Gateway
    name: http
    namespace: {{< reuse "docs/snippets/ns-system.md" >}}
    sectionName: https
```

{{% callout type="info" %}}
You can attach a VirtualHostOption resource to only an entire gateway listener. Because of that, the policy is automatically applied to all the hosts that this listener serves. You currently cannot address a particular hostname if multiple hostnames are defined on a listener. 
{{% /callout %}}

## Conflicting policies

Review the following rules to learn how multiple VirtualHostOptions are applied to the gateway or a specific gateway listener. 

* VirtualHostOptions that define the same top-level policy, such as two CORS policies, and that are attached to the gateway by using the `targetRefs` option without targeting a specific gateway listener, are not merged. Instead, the VirtualHostOption resource that was created first is applied. When specified in subsequent VirtualHostOptions, the same top-level policies are ignored.
* VirtualHostOptions that define the same top-level policy, such as two CORS policies, and that are attached to the same gateway listener by using the `targetRefs.sectionName` option are not merged. Instead, the VirtualHostOption resource that was created first is applied. When specified in subsequent VirtualHostOptions, the same top-level policies are ignored.
* If you apply two VirtualHostOptions that define the same top-level policy, such as two CORS policies, and you apply one to the entire gateway by using the `targetRefs` option and one to a specific gateway listener by using the `targetRefs.sectionName` option, the CORS policy that targets a specific listener takes precedence over the one that is applied to the entire gateway. 
* VirtualHostOptions that define different top-level policies, such as a CORS and a CSRF policy, are merged and applied to the gateway or gateway listeners. 

### Example 1: Gateway vs. listener-level policies

In the following image, you have two VirtualHostOption resources that define the same top-level CORS policy. CORS policy 1 is attached to a specific gateway listener by using the `targetRefs.sectionName` option. CORS policy 2 is attached to the entire gateway. Because listener-level policies take precedence over gateway-level policies, CORS policy 1 is attached to the http listener. However, CORS policy 2 is attached to the https listener, because no other listener-level policy exists that targets the https listener. 

In addition, another VirtualHostOption resource that defines a different top-level policy (CSRF policy 3) is attached to the entire gateway by using the `targetRef` option. Because the CSRF policy does not conflict with any of the CORS policies, it is applied to both the http and https listeners. 

{{< reuse-image src="img/policy-ov-multiple-virtualhostoptions.svg" width="800" >}}

### Example 2: Gateway vs. listener-level policies with conflict

In the following image, you have 4 VirtualHostOption resources that all define the same top-level CORS policy. CORS policies 1 and 2 are attached to the http gateway listener by using the `targetRefs.sectionName` option. CORS policies 3 and 4 are attached to the entire gateway by using the `targetRefs` option. 

Because you cannot apply two VirtualHostOption resources with the same top-level policy to the same gateway listener, only the VirtualHostOption resource that was created first is applied. Consequently, only CORS policy 1 is attached to the http listener. CORS policy 2 is ignored. CORS policies 3 and 4 are also ignored and not applied to the http listener, because policies that target a specific gateway listener take precedence over policies that target an entire gateway. 

CORS policies 3 and 4 can only be attached to the https listener. However, because you cannot apply two VirtualHostOption resources with the same top-level policy to the entire gateway, only the VirtualHostOption resource that was created first is applied. Consequently, only CORS policy 3 is attached to the https listener. 

{{< reuse-image src="img/policy-ov-multiple-virtualhostoption-conflict.svg" width="800" >}}
