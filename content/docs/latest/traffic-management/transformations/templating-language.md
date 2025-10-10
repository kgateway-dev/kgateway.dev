---
title: Templating language
weight: 10
---

The data plane proxy of your Gateway determines the templating language that you use to express transformations.

* {{< icon "agentgateway" >}} [Common Expression Language (CEL) for {{< reuse "docs/snippets/agentgateway.md" >}}](#cel)
* {{< icon "kgateway" >}} [Inja for Envoy-based kgateway proxies](#inja)

## CEL for Agentgateway {#cel}

{{< reuse "docs/snippets/agentgateway-capital.md" >}} transformation templates are written in Common Expression Language (CEL). CEL is a fast, portable, and safely executable language that goes beyond declarative configurations. CEL lets you develop more complex expressions in a readable, developer-friendly syntax.

To learn more about how to use CEL, refer to the following resources:

* [cel.dev tutorial](https://cel.dev/tutorials/cel-get-started-tutorial)
* [Agentgateway reference docs](https://agentgateway.dev/docs/reference/cel/)

### Log CEL variables in agentgateway {#cel-log}

You can log the full context of the CEL variables by [upgrading your Helm installation settings]({{< link-hextra path="/operations/upgrade/">}}), such as the following example:

```yaml
agentgateway:
  config:
    logging:
      fields:
        add:
          cel: variables()
  enabled: true
```

## Inja for Envoy-based kgateway proxies {#inja}

{{< reuse "docs/snippets/kgateway-capital.md" >}} transformation templates are powered by v3.4 of the [Inja template engine](https://github.com/pantor/inja/tree/v3.4.0), which is inspired by the popular Jinja templating language in Python. The template lets you transform headers and body information of a request or response based on the header and body properties themselves. 

The following TrafficPolicy shows the structure of the transformation template and all the attributes that you can configure. To learn more about each attribute, see [Template attributes](#template-attributes).

```yaml
apiVersion: gateway.kgateway.dev/v1alpha1
kind: TrafficPolicy
metadata:
  name: transformation
  namespace: httpbin
spec:
  transformation: 
    request:
      add: 
      - name: 
        value: 
      set: 
      - name: 
        value: 
      remove: []
      - name: 
        value: 
      body:
        value: 
        parseAs: 
    response: 
      add:
      - name: 
        value: 
      set: 
      - name: 
        value: 
      remove: []
      body: 
        value: 
        parseAs:
```

When writing your templates, you can take advantage of all the core Inja features, such as loops, conditional logic, and functions. In addition, you can use [custom Inja functions](#custom-inja-functions) to transform request and response metadata more easily.

### Custom Inja functions

When specifying your transformation template, you can leverage custom functions that can help to transform headers and bodies more easily. 

| Function | Description | 
| -- | -- |
| `base64_encode(string)` | Encodes the input string to base64. |
| `base64_decode(string)` | Decodes the input string from base64. For an example, see [Decode base64 headers](/docs/traffic-management/transformations/decode-base64-headers/). |
| `body()` | Returns the request/response body. For an example, see [Update response body](/docs/traffic-management/transformations/update-response-body).  | 
| `context()` | Returns the base JSON context. You can use this context to parse a JSON body that is an array. |
| `env(env_var_name)` | Returns the value of the environment variable with the given name. Note that because the transformation filter is processed in the gateway proxy, the environment variables are returned in the context of the gateway proxy. For an example, see [Inject response headers](/docs/traffic-management/transformations/inject-response-headers/). | 
| `header(header_name)` | Returns the value of the header with the given name. For an example, see [Change response status](/docs/traffic-management/transformations/change-response-status/). |
| `raw_string(string)` | Returns the input string with escaped characters intact. This function is useful for constructing JSON request or response bodies. For an example, see [Inject response headers](/docs/traffic-management/transformations/inject-response-headers). |
| `replace_with_random(string, pattern)` | Finds the pattern in the input string and replaces this pattern with a random string. For an example, see [Inject response headers](/docs/traffic-management/transformations/inject-response-headers/). |
| `request_header(header_name)` | Returns the value of the request header with the given name. This function is useful to add the request header values in response transformations. For an example for how to extract a request header value and inject it into a response header, see [Inject response headers](/docs/traffic-management/transformations/inject-response-headers/).|
| `substring(string, start_pos, substring_len)` | Returns a substring of the input string, starting at `start_pos` and extending for `substring_len` characters. If no `substring_len` is provided or `substring_len is <= 0`, the substring extends to the end of the input string. For an example, see [Decode base64 headers](/docs/traffic-management/transformations/decode-base64-headers/). |

**Other common functions**

You might use default Inja functions, such as `if else` or `if exists`. For an example, see [Change response status](/docs/traffic-management/transformations/change-response-status/). 

### Template attributes

Learn more about the template attributes that you can use to transform headers and bodies of requests and responses.

### `add`, `set`, `remove`

Apply transformation templates to add, set, or remode request or response headers. 

#### Static value

You can add request and response headers with static values. The following example adds the `my-header: static` request header and sets the `foo: bar` response header. 

```yaml

transformation: 
  request:
    add: 
    - name: my-header
      value: static
  response: 
    set: 
    - name: foo
      value: bar
```

#### Inja functions

You can use Inja functions in combination with Inja templates to modify request and response headers. 

In the following example, you set response headers in the following ways: 
* `x-gateway-response`: Use the value from the `x-gateway-request` request header and populate the value of that header into an `x-gateway-response` response header.
* `x-podname`: Retrieve the value of the `POD_NAME` environment variable and add the value to the x-podname response header. Because the transformation is processed in the gateway proxy, these environment variables refer to the variables that are set on the proxy. You can view supported environment variables when you run `kubectl get deployment http -n {{< reuse "docs/snippets/namespace.md" >}} -o yaml` and look at the `spec.containers.env` section.
* `x-response-raw`: Adds a static string hello value with all escape characters intact.
* `x-replace`: Replaces the pattern-to-replace text in the `baz` header with a random string.

```yaml

transformation:
  response:
    set:
    - name: x-gateway-response
      value: '{{ request_header("x-gateway-request") }}' 
    - name: x-podname
      value: '{{ env("POD_NAME") }}'
    - name: x-response-raw
      value: '{{ raw_string("hello") }}'
    - name: x-replace
      value: '{{ replace_with_random(request_header("baz"), "pattern-to-replace") }}'
```

### `body`

Apply transformation templates to request or response bodies. The `body` attribute allows you to specify the structure of the body that you want to return. For example, you can replace values in the body, extract values from headers and add them to the body, or return a static body. 

#### `parseAs`

By default, {{< reuse "docs/snippets/kgateway.md" >}} parses the body as JSON. If the body cannot be parsed as a JSON, a 400 Bad Request HTTP error is returned. 

If your body is not a JSON object, you can instead parse it as plain text, by setting the `parseAs` option to `AsString`. 

```yaml

transformation:
  response:
    body:
      value: 'This is my static body'
      parseAs: AsString
```

#### Static value

To add a static value to the body, you can use the following transformation template. 
```yaml

transformation:
  response:
    body:
      value: 'This is my static body'
```

This template results in a `This is my static body` body. 

#### Inja template
The following example uses an Inja function to get the `POD_NAME` environment variable from the gateway proxy and returns that value in a custom body string. 

```yaml 

transformation: 
  response: 
    body: 
      value: 'This is the value of the POD_NAME environment variable: {{env("POD_NAME")}}'
```

This template results in a body similar to `This is the value of the POD_NAME environment variable: http-844ff8bc4d-dh4pn`. 

#### Header to body
To extract header information and add this information to the body, you can take multiple different approaches. The approach that is right for you depends on how you want to transform the body. 

* **Inja functions**: 

The following example uses an Inja function to access the value of a request header. This value is added to a custom body string. 
```yaml

transformation: 
  response: 
    body: 
      value: 'This is the value of the :path pseudo header: {{request_header(":path")}}.'
```

This template results in a body similar to `This is the value of the :path pseudo header: /json`. 


#### Body to body
Because {{< reuse "docs/snippets/kgateway.md" >}} automatically parses a body as a JSON, you can directly access values from the body to inject into your custom body that you want to return. 

Assuming a body with the following format: 
```yaml
{
  "slideshow": {
    "editor": "Yours Truly",
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

You can use a transformation template similar to the following to extract the `author`, `title`, and `slides` attributes and add them to the response body.  
```yaml

transformation: 
  response: 
    body: 
      text: '{"author": "{{ slideshow.author }}", "title": "{{ slideshow.title }}", "slides": "{{ slideshow.slides }}}'
```

The following body is returned after transformation: 
```
{"author": "Yours Truly", "title": "Sample Slide Show", "slides": "[{"title":"Wake up to WonderWidgets!","type":"all"},{"items":["Why <em>WonderWidgets</em> are great","Who <em>buys</em> WonderWidgets"],"title":"Overview","type":"all"}]}% 
```

