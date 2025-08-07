---
title: Supporting Service Mesh with kgateway and Gateway API
toc: false
publishDate: 2025-03-20T00:00:00-00:00
author: Nadine Spies & Eitan Suez
excludeSearch: true
---

A service mesh allows you to configure and control traffic between Kubernetes services that are deployed in a cluster. Service-to-service communication is also referred to as “east-west” traffic and does not involve ingress gateways.

When the Gateway API "SIG" (Special Interest Group) got together to design the service mesh integration, their goal was to accommodate service mesh use cases while keeping changes to the API at a minimum.

The Gateway API [refactors](https://refactoring.com/) the Ingress API by decoupling routing-specific concerns from gateway-specific ones. An advantage of this design choice is the ability to reuse routes in a service mesh context, without a gateway.

Typically we expect routes to have a Gateway `parentRef`, as implied by the following resource model:
{{< reuse-image src="blog/introduction-to-kubernetes-gateway-api-1.png" width="750px" >}}

However, in the context of a service mesh, you can simply associate a route with a Kubernetes Service.

The following example shows an HTTPRoute that configures routing to the `reviews` service. Irrespective of who calls the `reviews` service, it sends half of the traffic to `reviews-v1` and half of the traffic to `reviews-v2`.

```yaml
---
apiVersion: gateway.networking.k8s.io/v1
kind: HTTPRoute
metadata:
  name: bookinfo-reviews
  namespace: bookinfo
spec:
  parentRefs:
  - name: reviews
    kind: Service
    group: ""
  rules:
  - backendRefs:
    - name: reviews-v1
      port: 9080
      weight: 1
    - name: reviews-v2
      port: 9080
      weight: 1
```
So how does the Gateway API enforce these policies if no gateway is involved? This is where service mesh providers, such as [Istio](https://istio.io/), come into play.

The role of a service mesh provider is to recognize the east-west communication pattern and to enforce it accordingly within the service mesh by using a gateway-like component. In Istio, you typically have a sidecar proxy or a waypoint proxy that applies the policy to the east-west traffic before it is forwarded to the target destination. 

Check out the [implementations](https://gateway-api.sigs.k8s.io/implementations/#service-mesh-implementation-status) page of the Kubernetes Gateway API portal to find a list of other service mesh providers that also support this facet of the Gateway API.

## The power of extensibility

Now think about how powerful this capability is. Besides controlling how traffic enters your cluster by using the Gateway API's ingress capabilities, you can now control the traffic flow between services in the cluster. And the best thing about this is that you don’t have to learn a new API.

For example, you can extend the example above to support important capabilities:
- **Canary releases and A/B testing:** You can use header-based matching and traffic splitting to route requests to different versions of your app.  

- **Timeouts and retry (experimental) policies:** Applying timeouts and retry policies is crucial to improve the resilience, performance, and reliability of your service mesh.  

- **Extensions:** The Gateway API allows implementers to extend the core capabilities of the API with policy attachments, which opens up a world of new capabilities. For example, you could apply rate limits or external auth policies to your east-west traffic, ensuring your services are protected against potential attacks. We cover policy attachments and how they work in this [blog](https://kgateway.dev/blog/policy-attachments/). 

The "SIG" group is evaluating other mesh scenarios, through its enhancement proposal process. [Proposal 1324](https://gateway-api.sigs.k8s.io/geps/gep-1324/#use-cases) lists use cases for service mesh, and is an agreement for further work in this area.

## Summary

The work of the “SIG” group and its commitment to adding more service mesh use cases helps drive new standards for how to configure east-west traffic, irrespective of which service mesh implementation we choose to employ.

To see a service mesh implementation in action and try out applying policies to east-west traffic, we encourage you to check out the [free lab](https://www.solo.io/resources/lab/gatewayapi-support-for-service-mesh-with-kgateway?web&utm_source=organic) on Gateway API support for service mesh or watch the [demo](https://youtu.be/c5ZfIUOFb9I) video below.
 
<br>
{{< youtube c5ZfIUOFb9I >}}
