---
title: Transformations in kgateway 
toc: false
publishDate: 2025-04-17T00:00:00-00:00
author: Eitan Suez
excludeSearch: true
---

Transformations are a feature in kgateway that allows for the transformation of an incoming request or outgoing response. It offers the addition, removal, or replacement of HTTP headers and the manipulation of request or response body.

While the Kubernetes Gateway API provides [filters for request and response header modifiers](https://gateway-api.sigs.k8s.io/guides/http-header-modifier/), those filters are scoped to the manipulation of headers only, and provide only rudimentary capabilities such as adding, removing or updating headers with static values supplied as strings.

Transformations are more powerful in that the value of the body or header is an [inja template](https://github.com/pantor/inja), which loosely adheres to the [jinja2 template engine syntax](https://jinja.palletsprojects.com/en/stable/).

Through transformations, kgateway gives us access to an expression language, which includes conditional statements, and access to a number of functions.

## How it works

Transformations are configured with the [TrafficPolicy](https://kgateway.dev/docs/reference/api/#trafficpolicy) resource and can be applied to either the request or the response, or both.

The TrafficPolicy resource in turn is associated to select HTTP requests through the `targetRefs` field, which can point to an [HTTPRoute](https://gateway-api.sigs.k8s.io/reference/spec/#httproute). The HTTPRoute routing rule's [matches field](https://gateway-api.sigs.k8s.io/reference/spec/#httproutematch) can target specific requests based on various request attributes including path, headers, query parameters, and the HTTP method.

Let's study some examples.

## Examples

If you wish to try out any of the below examples yourself, you'll need:

- A Kubernetes cluster with kgateway deployed
- A backing workload, such as [httpbin](https://httpbin.org/)
- A provisioned Gateway and HTTPRoute with a rule to send requests to the workload

You can find the details in the blog posts [Guide to installing kgateway](https://kgateway.dev/blog/guide-to-installing-kgateway/) and [Understanding Gateway API basics](https://kgateway.dev/blog/understanding-gateway-api-basics/).

### Example 1: Decode a header value in a request

This example configures a TrafficPolicy to add a request header named `x-decoded-message` containing the value of a base64-decoded header named "message".

```yaml
apiVersion: gateway.kgateway.dev/v1alpha1
kind: TrafficPolicy
metadata:
  name: transformation
spec:
  targetRefs:
  - name: httpbin
    kind: HTTPRoute
    group: gateway.networking.k8s.io
  transformation:
    request:
      add:
      - name: x-decoded-message
        value: '{{ base64_decode(request_header("message")) }}'
```

Set the environment variable MESSAGE to the base64-encoded value of "hello world":

```yaml
export MESSAGE=$(echo -n "hello world" | base64)
```

Send a request through the ingress gateway with the "message" header:

```yaml
curl -H "message: $MESSAGE" http://httpbin.example.com/headers --resolve httpbin.example.com:80:$GW_IP
```

In the response, note how the encoded message was decoded (and placed in the new header) by the gateway prior to forwarding the request on to `httpbin`:

```yaml
{
  "headers": {
    ...
    "Message": [
      "aGVsbG8gd29ybGQ="
    ],
    "X-Decoded-Message": [
      "hello world"
    ],
    ...
  }
}
```

### Example 2: Add a response header conditionally

This example configures a TrafficPolicy to set the response header named `x-host-match` to "yes" if the request was sent to the hostname "httpbin.example.com":

```yaml
apiVersion: gateway.kgateway.dev/v1alpha1
kind: TrafficPolicy
metadata:
  name: transformation
spec:
  targetRefs:
  - name: httpbin
    kind: HTTPRoute
    group: gateway.networking.k8s.io
  transformation:
    response:
      add:
      - name: x-host-match
        value: '{%- if "httpbin.example.com" in request_header("Host") -%}yes{% else %}nope{% endif %}'
```

The value of the `Host` request header is an array, and so condition uses the `in` operator to check for the presence of the host name in the list.

Send a request through the ingress gateway using the host name `httpbin.example.com`:

```yaml
curl --verbose http://httpbin.example.com/get --resolve httpbin.example.com:80:$GW_IP
```

Note the presence and value of the header `x-host-match` in the response:

```yaml
* Connected to httpbin.example.com (127.0.0.1) port 80
* using HTTP/1.x
> GET /get HTTP/1.1
> Host: httpbin.example.com
> User-Agent: curl/8.12.1
> Accept: */*
>
* Request completely sent off
< HTTP/1.1 200 OK
< access-control-allow-credentials: true
< access-control-allow-origin: *
< content-type: application/json; charset=utf-8
< date: Thu, 03 Apr 2025 18:08:45 GMT
< content-length: 545
< x-envoy-upstream-service-time: 1
< x-host-match: yes
< server: envoy
...
```

### Example 3: Response body transformation

The `httpbin` sample application contains a `/json` endpoint that returns some "canned" response about a slideshow:

```yaml
curl http://httpbin.example.com/json --resolve httpbin.example.com:80:$GW_IP | jq
```

Here is the default response:

```yaml
{
  "slideshow": {
    "author": "Yours Truly",
    "date": "date of publication",
    "slides": [
      {
        "title": "Wake up to WonderWidgets!",
        "type": "all"
      },
      {
        "items": [
          "Why <em>WonderWidgets</em> are great",
          "Who <em>buys</em> WonderWidgets"
        ],
        "title": "Overview",
        "type": "all"
      }
    ],
    "title": "Sample Slide Show"
  }
}
```

Say that we wish to transform the response as follows:

- Wrap the response in a field named `response`,
- Rename `title` to `description`,
- Include only the `slides` section from the original response.

Here is a TrafficPolicy that applies the transformation:

```yaml
apiVersion: gateway.kgateway.dev/v1alpha1
kind: TrafficPolicy
metadata:
  name: transformation
spec:
  targetRefs:
  - name: httpbin
    kind: HTTPRoute
    group: gateway.networking.k8s.io
  transformation:
    response:
      body:
        parseAs: AsJson
        value: |
          {
            "response": {
              "description": "{{slideshow.title}}",
              "slides": {{slideshow.slides}}
            }
          }
```

Apply the traffic policy, then send in another request:

```yaml
curl http://httpbin.example.com/json --resolve httpbin.example.com:80:$GW_IP | jq
```

Review the transformed response:

```yaml
{
  "response": {
    "description": "Sample Slide Show",
    "slides": [
      {
        "title": "Wake up to WonderWidgets!",
        "type": "all"
      },
      {
        "items": [
          "Why <em>WonderWidgets</em> are great",
          "Who <em>buys</em> WonderWidgets"
        ],
        "title": "Overview",
        "type": "all"
      }
    ]
  }
}
```

## Summary

Transformations is a powerful feature that provides access to an expression language to transform requests and (or) responses in a number of ways. This can be very useful in a number of use cases, providing a way to adapt incoming requests to the expectations of the running service, or to adapt the server's responses to the expectations of a client.

Transformations is but one of a number of features that the kgateway project provides.