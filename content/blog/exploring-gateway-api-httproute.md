---
title: Exploring the Gateway API's HTTPRoute
toc: false
publishDate: 2025-03-28T00:00:00-00:00
author: Nadine Spies
excludeSearch: true
---

An [HTTPRoute](https://gateway-api.sigs.k8s.io/api-types/httproute/) resource is the main resource in the Kubernetes Gateway API to define HTTP routing rules for one or more services in your cluster. Its configuration is simple and easy to comprehend.

Take the following example route:

```yaml
apiVersion: gateway.networking.k8s.io/v1
kind: HTTPRoute
metadata:
  name: httpbin
spec:
  parentRefs:
  - name: my-gateway
  hostnames:
  - httpbin.example.com
  rules:
  - backendRefs:
    - name: httpbin
      port: 8000
```
The above routes all requests for the hostname `httpbin.example.com` to the backend service named `httpbin` listening on port 8000.

We "dial up" the complexity slightly in this next example:

```yaml
apiVersion: gateway.networking.k8s.io/v1
kind: HTTPRoute
metadata:
  name: httpbin
  namespace: httpbin
spec:
  parentRefs:
  - name: my-gateway
    namespace: kgateway-system
    sectionName: http
  rules:
  - matches:
    - path:
        type: PathPrefix
        value: /status/200
    backendRefs:
    - name: httpbin
      port: 8000
```
This route binds to a specific listener named `http` on the `my-gateway` gateway. No host matching is specified on the route, the hostname is specified on the listener of the Gateway resource, which is not shown in this example.

Another difference is the presence of a `matches` field on the single routing rule. This rule only allows requests with a path prefix of `/status/200` to be forwarded to httpbin.

Now that you know about the components of an HTTPRoute, let’s dive deeper into some of them. This blog explores three main fields that are part of any HTTP routing rule:  `matches`, `filters`, and `backendRefs`. We will also look at optional resiliency settings for your routes. 

## Matches

With `matches`, you can define the criteria for when traffic should be routed to your backend services. Matching traffic is a crucial concept in networking as it allows you to control which requests you want to accept and how you want to route them to your backends. 

Assuming the HTTP protocol, you can match on many different aspects of a request, including: 

- **Paths** (e.g., `/headers`, `/status/*`)
- **Headers** (e.g., `User-Agent: Mobile`)
- **Query Parameters** (e.g., `?version=beta`)
- **Methods** (e.g., `GET`, `POST`)

You can also define multiple matching criteria and even combine them with an *AND* or *OR* operator. This unlocks even more powerful capabilities, such as the ability to perform A/B testing where users are directed to different versions of your app depending on the properties that are provided in the request.

To understand how this works, let’s take a look at the following HTTPRoute, which defines three different sets of matching rules. Each matching rule set allows traffic to a particular version of the httpbin app.  

- Requests to `/status/*` that also include the `-H “user: me”` header are routed to httpbin-v1
- `POST` requests that also include the `?version=2` query parameter are routed to httpbin-v2
- Requests to `/headers` OR requests with the `-H “version: 3”` header are routed to httpbin-v3

```yaml
apiVersion: gateway.networking.k8s.io/v1
kind: HTTPRoute
metadata:
  name: httpbin
spec:
  parentRefs:
  - name: my-gateway
  rules:
  - matches:
      - path: 
          type: PathPrefix
          value: /status
        headers:
        - type: Exact
          name: user
          value: me
      backendRefs:
        - name: httpbin-v1
          port: 8000
    - matches:
      - queryParams: 
        - type: Exact
          name: version
          value: 2
        method: "POST"
      backendRefs:
        - name: httpbin-v2
          port: 8000
    - matches:
      - path:
          type: Exact
          value: /headers
      - headers: 
        - type: Exact
          name: version
          value: "3"
      backendRefs:
        - name: httpbin-v3
          port: 8000
```
Here is another example of an HTTPRoute, a more realistic scenario from the bookinfo sample application, which exposes specific endpoints via a combination of exact and prefix path matches:

```yaml
apiVersion: gateway.networking.k8s.io/v1
kind: HTTPRoute
metadata:
  name: bookinfo
spec:
  parentRefs:
  - name: bookinfo-gateway
  rules:
  - matches:
    - path:
        type: Exact
        value: /productpage
    - path:
        type: PathPrefix
        value: /static
    - path:
        type: Exact
        value: /login
    - path:
        type: Exact
        value: /logout
    - path:
        type: PathPrefix
        value: /api/v1/products
    backendRefs:
    - name: productpage
      port: 9080
```
Matches can be a powerful tool.  We can use header-based matching to support capabilities such as A/B testing where some users are directed to a different version of the application.  Header-based matching has other uses, for example: testing in production.  

I vividly recall how Netflix years ago [presented a talk](https://youtu.be/mHHHpxJuTAo) on how they used their edge gateway "Zuul" to diagnose and troubleshoot issues in production. They would spin up a version of the workload in debug mode and route requests to it only when testers accessed the system in production, allowing them to better understand what was going on with that particular workload, all without disrupting production traffic.

Think about what else you can achieve with matchers. Another powerful capability is to segment traffic based on the user’s geolocation, which can improve performance and the overall user experience, but also help meet compliance standards. 

## Filters
If you are excited about matches, wait until you explore what filters can do for you. With filters, you have another powerful tool at hand that allows you to modify, inspect, and manipulate matched requests. The Kubernetes Gateway API specifies several [types of filters](https://gateway-api.sigs.k8s.io/reference/spec/#gateway.networking.k8s.io/v1.HTTPRouteFilterType) including:

- **RequestRedirect** which is great to redirect HTTP traffic to HTTPS.
- **URLRewrite** which is a useful tool when dealing with API evolution so that you can continue to support deprecated routes while removing newer versions of an API.  
- **RequestHeaderModifier** and **ResponseHeaderModifier** which help to augment requests or responses with additional metadata before they are routed to their destination. For example, you can inject JWT tokens or telemetry data like tracing IDs, change the format of headers to comply with new standards, or strip insecure headers. 
- **RequestMirror** which can be used to capture or replay streams of requests against another version of the application, and can be useful for testing purposes.
- **CORS** (Cross-Origin Resource Sharing) which controls how web pages in one domain can request and interact with resources that are hosted on a different domain. 

Below is an example for redirecting traffic to HTTPS. 

```yaml
apiVersion: gateway.networking.k8s.io/v1
kind: HTTPRoute
metadata:
  name: httpbin-redirect-to-https
spec:
  hostnames:
  - httpbin.example.com
  parentRefs:
  - name: my-gateway
    sectionName: http
  rules:
  - filters:
    - type: RequestRedirect
      requestRedirect:
        scheme: https
        statusCode: 301
```

## Extend core capabilities with the ExtensionRef filter
The `ExtensionRef` filter allows implementers of the Kubernetes Gateway API to plug in their custom filters which opens up an exciting world of new opportunities. One example of such a custom filter is kgateway’s [DirectResponse API](https://kgateway.dev/docs/traffic-management/direct-response/). This API allows you to directly respond to incoming requests with a pre-defined body and HTTP status code. Requests are therefore not forwarded to the backend service. Direct responses can be useful in cases where you want to simulate responses from a backend service for testing purposes or in cases where sending back a static response is sufficient. 

Below is a DirectResponse resource that sends back a 404 HTTP response code with a custom message indicating that using the `/direct-response` path is not allowed. 

```yaml
apiVersion: gateway.kgateway.dev/v1alpha1
kind: DirectResponse
metadata:
 name: direct-response
 namespace: httpbin
spec:
 status: 404
 body: "User-agent: *\nDisallow: /direct-response\n"
```
To apply the DirectResponse to a route, you now reference it with the `extensionRef` filter in your HTTPRoute as shown in the following configuration. The example routes all incoming traffic along the / path prefix to the httpbin app. 

However, when traffic comes in on the `/direct-response` path, the gateway will not forward the request to the httpbin app. Instead, it will send back the DirectResponse’s body and HTTP status code.

```yaml
apiVersion: gateway.networking.k8s.io/v1
kind: HTTPRoute
metadata:
  name: httpbin-direct-resonse
  namespace: httpbin
spec:
  parentRefs:
  - name: http
  rules:
  - matches:
    - path:
        type: PathPrefix
        value: /
    backendRefs:
    - name: httpbin
      port: 8000
  - matches:
    - path:
        type: Exact
        value: /direct-response
    filters:
    - type: ExtensionRef
      extensionRef:
       name: direct-response
       group: gateway.kgateway.dev
       kind: DirectResponse
```
As you can see, by combining `matches` and `filters` in an HTTPRoute, you have a great way of customizing and fine-tuning traffic routing, traffic control, and traffic processing for your services.

## BackendRefs
The `backendRefs` section is a simple list of backends that you want to route traffic to. The most common backend type is a Kubernetes Service. In the example below, all traffic is routed to the httpbin service on port 8000.

```yaml
apiVersion: gateway.networking.k8s.io/v1
kind: HTTPRoute
metadata:
  name: httpbin
  namespace: httpbin
  labels:
    example: httpbin-route
spec:
  parentRefs:
    - name: http
      namespace: kgateway-system
  rules:
    - backendRefs:
        - name: httpbin
          port: 8000
```
## Splitting traffic between different backends
Another powerful tool with `backendRefs` is to use weights to split traffic between two or more backends, also known as “traffic splitting”. Traffic splitting is crucial when performing canary releases and A/B testing, but it can also be used to load balance requests across backends to optimize costs. 

If unspecified, the weight defaults to “1”. If only one backend is defined, 100% of the traffic is forwarded to that destination. If we have “n” `backendRefs` however, each with an equal weight, requests will be load balanced evenly across all destinations as shown in the following example. 

```yaml
apiVersion: gateway.networking.k8s.io/v1
kind: HTTPRoute
metadata:
  name: httpbin
  namespace: httpbin
spec:
  parentRefs:
  - name: infra-gateway
  rules:
  - matches:
    - path:
        type: PathPrefix
        value: /status/200
    backendRefs:
    - name: httpbin-v1
      port: 8000
      weight: 1
    - name: httpbin-v2
      port: 8000
      weight: 1
```
To progressively shift traffic onto a new version of the backend, you simply adjust the weights for each backend destination. 

In the example below, 10% of traffic is sent to helloworld-v1 and helloworld-v2, and 80% of the traffic is sent to helloworld-v3. 

```yaml
apiVersion: gateway.networking.k8s.io/v1
kind: HTTPRoute
metadata:
  name: traffic-split
  namespace: helloworld
spec:
  parentRefs:
  - name: http
    namespace: gloo-system
  hostnames:
  - traffic.split.example
  rules:
  - matches:
    - path:
        type: PathPrefix
        value: /
    backendRefs:
    - name: helloworld-v1
      port: 5000
      weight: 10
    - name: helloworld-v2
      port: 5000
      weight: 10
    - name: helloworld-v3
      port: 5000
      weight: 80
```
## Explore kgateway’s Backend API
As we saw earlier, a backend is typically represented by a Kubernetes service in your cluster. However, you can also leverage [kgateway’s Backend API](https://kgateway.dev/docs/traffic-management/destination-types/backends/) to route traffic to an external endpoint, such as an AWS Lambda function or a static hostname.

Each Backend must define a type, which describes the endpoint you want to send traffic to. Below you find an example for an `aws` Backend that configures an AWS Lambda function. As you can see, you simply specify the region, name of the function, and credentials to access it. 

```yaml
apiVersion: gateway.kgateway.dev/v1alpha1
kind: Backend
metadata:
  name: lambda
  namespace: kgateway-system
spec:
  aws:
    region: us-east-1
    secretRef:
      name: aws-creds
      namespace: kgateway-system
    lambdaFunctions:
    - lambdaFunctionName: echo
      logicalName: echo
      qualifier: $LATEST
```
With your Backend all set up, you now just need to reference it from your HTTPRoute. You do this in the same way you reference a Kubernetes service. 

```yaml
apiVersion: gateway.networking.k8s.io/v1
kind: HTTPRoute
metadata:
  name: lambda
  namespace: kgateway-system
spec:
  parentRefs:
    - name: http
  rules:
  - matches:
    - path:
        type: PathPrefix
        value: /echo
    backendRefs:
    - name: lambda
      namespace: kgateway-system
      group: gateway.kgateway.dev
      kind: Backend
      filters:
        - type: ExtensionRef
          extensionRef:
            group: "gateway.kgateway.dev"
            kind: Parameter
            name: echo
```
## Resilience
Apart from `matches`, `filters`, and `backendRefs`, the Kubernetes Gateway API comes with additional settings (still experimental) that can improve the resilience of your services, including `timeouts`, `retry` , and `sessionPersistence`.

`Timeouts` and `retries` are crucial in modern distributed systems as they help to improve service reliability, protect resources, and enhance user experience. Just imagine how a slow or unresponsive backend can cause requests to hang indefinitely, which then leads to a poor user experience. Requests that are stuck can also consume excessive resources and cause cascading failures. 

Combining `timeouts` and `retries` lets you identify non-responsive backends so that you can gracefully failover to other backends and protect your environment. I recommend the book [Understanding Distributed Systems](https://understandingdistributed.systems/) for more information on this subject.

HTTPRoutes also support `sessionPersistence`, also known as session affinity or “sticky” sessions. Session persistence ensures that traffic is always routed to the same backend instance for the duration of the session, which can improve request latency and the user experience.

## Summary
HTTPRoutes provide powerful tools to control, process, and manipulate traffic for your services, all coupled with common extension points to enhance the core capabilities of the Kubernetes Gateway API. We invite you to try these exciting tools yourself hands-on by visiting the kgateway project's [labs](https://kgateway.dev/resources/labs/) section.  The companion hands-on lab for this blog is titled [Exploring HTTPRoute resource configurations with kgateway](https://www.solo.io/resources/lab/exploring-httproute-resource-configurations-with-kgateway?web&utm_source=organic&utm_medium=FY26&utm_campaign=WW_GEN_LAB_kgateway.dev&utm_content=community).

