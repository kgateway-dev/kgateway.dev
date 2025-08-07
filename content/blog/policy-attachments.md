---
title: Policy attachments with kgateway and Gateway API
toc: false
publishDate: 2025-03-21T00:00:00-00:00
author: Nadine Spies
excludeSearch: true
---

One of the major shortcomings of the venerable Kubernetes Ingress API was in the area of extensibility. The API specification did not address how implementers should specify features that were outside the scope of the ingress scenarios covered by the Ingress API.

Implementers had to resort to Kubernetes resource annotations to expose additional features or capabilities such as timeouts, retries, or rate limiting.

## The power of extensions

The Kubernetes Gateway API aims to do its part to redress the situation in its API through [policy attachments](https://gateway-api.sigs.k8s.io/reference/policy-attachment/). Their purpose is defined as follows: 

> **"Gateway API also defines a pattern called Policy Attachment, which augments the behavior of an object to add additional settings that can't be described within the spec of that object."**

The Gateway API documentation proceeds by mentioning that two kinds of policy attachments may exist: direct and inherited, depending on whether the configuration affects a single, directly referenced object (direct) or whether it might affect a hierarchy of resources.

This pattern is marked experimental at the time of writing, and is further discussed in the Gateway Enhancement Proposal (GEP) [713](https://gateway-api.sigs.k8s.io/geps/gep-713/).

Some notable aspects of this pattern worth calling out include:

- **Policy naming convention:** A resource will typically configure some kind of policy, so we are encouraged to use the suffix `Policy` when naming the CRD. For example, the Gateway API defines a [BackendTLSPolicy](https://gateway-api.sigs.k8s.io/api-types/backendtlspolicy/), which allows us to quickly infer that this resource is designed to configure aspects of TLS communication for the connection between a gateway and a backend workload.  

- **Target reference (`targetRefs`) in policy attachments:** The resource that a policy attachment affects should be specified via a `targetRefs` field. The value of that target reference is contextual. 

For a BackendTLSPolicy it's a reference to a service.  But we can imagine other scenarios where the target reference is a route or a gateway, as illustrated below (the extension resources shown in the illustration are just examples):

{{< reuse-image src="blog/policy-attachments-1.png" width="750px" >}}

## Exploring policies in kgateway

The kgateway project comes with different policy types that aim to extend the core capabilities of the Kubernetes Gateway API with advanced traffic management, resiliency, security, and even AI capabilities. You can apply these policies to an HTTPRoute or Gateway. 

Let’s start exploring a simple [HTTPListenerPolicy](https://kgateway.dev/docs/reference/api/#httplistenerpolicy). You use the `targetRefs` section to attach this policy to a Gateway. A very common use case for an HttpListenerPolicy is to configure or customize access logs. 

In the below example resource, the policy attaches to the gateway named `infra-gateway` and specifies "standard output" as the access logging "file sink". It then proceeds to specify the fields that will constitute each log line:

```yaml
apiVersion: gateway.kgateway.dev/v1alpha1
kind: HTTPListenerPolicy
metadata:
  name: access-logging-json
  namespace: kgateway-system
spec:
  targetRefs:
  - group: gateway.networking.k8s.io
    kind: Gateway
    name: infra-gateway
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
```
Applying policies to a gateway is handy as it lets you configure all traffic and all the routes that the Gateway serves. What if in addition to configuring a gateway, you also want to extend a route configuration? Kgateway’s[TrafficPolicy](https://kgateway.dev/docs/reference/api/#trafficpolicy) API is designed to solve this use case for you.

The structure of a TrafficPolicy is very similar to the one of an HTTPListenerPolicy, but you use the `targetRefs` section to apply the policy to the routes in an HTTPRoute instead of a Gateway. 

Let’s explore the following example, in which you use an Inja template to extract the value of the x-kgateway-request request header and inject that value into the `x-kgateway-response` response header. 

```yaml
apiVersion: gateway.kgateway.dev/v1alpha1
kind: TrafficPolicy
metadata:
  name: transformation
  namespace: helloworld
spec:
  targetRefs: 
  - group: gateway.networking.k8s.io
    kind: HTTPRoute
    name: helloworld
  transformation:
    response:
      set:
      - name: x-kgateway-response
        value: '{{ request_header("x-kgateway-request") }}'
```
The above is just one example of kgateway's [transformations](https://kgateway.dev/docs/traffic-management/transformations/) feature, which provides more powerful request and response transformation capabilities than the Gateway API's *RequestHeaderModifier* and *ResponseHeaderModifier* filters.

## Creating new opportunities with policy extensions
Policy attachments open up an exciting new world of possibilities to extend the Gateway API’s core capabilities with advanced traffic management, resiliency, security, and AI features that you can configure on a gateway or route, all while ensuring a common experience and easy adoption amongst users.

You can get started and try out policies in kgateway in this free [hands-on lab](https://www.solo.io/resources/lab/understanding-kgateway-patterns-of-extensions). Alternatively check out this [demo video below](https://www.youtube.com/watch?v=NQSADVpcO8M) by Eitan Suez and follow along as he demostrates how kgateway extends the patterns within the Gateway API.

<br>
{{< youtube NQSADVpcO8M >}}



