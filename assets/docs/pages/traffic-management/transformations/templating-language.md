The data plane proxy of your Gateway determines the templating language that you use to express transformations.

{{< icon "kgateway" >}} Transformation templates for Envoy-based kgateway proxies

## Transformation templates for Envoy-based kgateway proxies {#inja}

{{< reuse "docs/snippets/kgateway-capital.md" >}} transformation templates use a template syntax that lets you transform headers and body information of a request or response based on the header and body properties themselves.

{{< version include-if="2.1.x" >}}
The engine is the classic transformation filter, which is powered by version 3.4 of the [Inja template engine](https://github.com/pantor/inja/tree/v3.4.0).
{{< /version >}}
{{< version include-if="2.2.x" >}}
The default engine is rustformation, which is powered by the [MiniJinja template engine](https://github.com/mitsuhiko/minijinja). On `x86_64`, classic transformation (powered by version 3.4 of the [Inja template engine](https://github.com/pantor/inja/tree/v3.4.0)) is available as an opt-out fallback. For a comparison of the two engines, see [Transformation engines]({{< link-hextra path="/traffic-management/transformations/engines/" >}}).
{{< /version >}}
{{< version exclude-if="2.0.x,2.1.x,2.2.x" >}}
The only supported engine is rustformation, which is powered by the [MiniJinja template engine](https://github.com/mitsuhiko/minijinja). For details, see [Transformation engine]({{< link-hextra path="/traffic-management/transformations/engines/" >}}).
{{< /version >}}

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

When writing your templates, you can take advantage of all the core template features, such as loops, conditional logic, and functions. In addition, you can use [custom transformation functions](#custom-inja-functions) to transform request and response metadata more easily.

### Custom transformation functions {#custom-functions}

When specifying your transformation template, you can leverage custom functions that can help to transform headers and bodies more easily.

| Function | Description |
| -- | -- |
| `base64_encode(string)` | Encodes the input string to standard base64. |
| `base64_decode(string)` | Decodes the input string from standard base64. For an example, see [Decode base64 headers]({{< link-hextra path="/traffic-management/transformations/simple/decode-base64-headers/" >}}). |
| `base64url_encode(string)` | Encodes the input string to URL-safe base64. URL-safe base64 replaces the standard `+` and `/` characters with `-` and `_` so the result can be used in URLs and HTTP headers without further escaping. |
| `base64url_decode(string)` | Decodes the input string from URL-safe base64. |
| `body()` | Returns the request or response body. For an example, see [Update response body]({{< link-hextra path="/traffic-management/transformations/simple/update-response-body" >}}). |
| `context()` | Returns the base JSON context. You can use this context to parse a JSON body that is an array. |
| `env(env_var_name)` | Returns the value of the environment variable with the given name. Because the transformation filter is processed in the gateway proxy, the environment variables are returned in the context of the gateway proxy. For an example, see [Inject response headers]({{< link-hextra path="/traffic-management/transformations/simple/inject-response-headers/" >}}). |
| `header(header_name)` | Returns the value of the response header with the given name. For an example, see [Change response status]({{< link-hextra path="/traffic-management/transformations/simple/change-response-status/" >}}). |
| `raw_string(string)` | Returns the input string with escaped characters intact. This function is useful for constructing JSON request or response bodies. For an example, see [Inject response headers]({{< link-hextra path="/traffic-management/transformations/simple/inject-response-headers" >}}). |
| `replace_with_random(string, pattern)` | Finds the pattern in the input string and replaces this pattern with a random value. {{< version exclude-if="2.0.x,2.1.x" >}}See the known-issue note below this table about constant-folding behavior in rustformation.{{< /version >}} For an example, see [Inject response headers]({{< link-hextra path="/traffic-management/transformations/simple/inject-response-headers/" >}}). |{{< version exclude-if="2.0.x,2.1.x" >}}
| `replace_with_string(input, pattern, replacement)` | Finds the pattern in the input string and replaces every occurrence with `replacement`. Useful for redacting tokens or normalizing values before they are forwarded. |{{< /version >}}
| `request_header(header_name)` | Returns the value of the request header with the given name. This function is useful to add the request header values in response transformations. For an example for how to extract a request header value and inject it into a response header, see [Inject response headers]({{< link-hextra path="/traffic-management/transformations/simple/inject-response-headers/" >}}). |
| `substring(string, start_pos, substring_len)` | Returns a substring of the input string, starting at `start_pos` and extending for `substring_len` characters. If `substring_len` is omitted or `<= 0`, the substring extends to the end of the input string. For an example, see [Decode base64 headers]({{< link-hextra path="/traffic-management/transformations/simple/decode-base64-headers/" >}}). |

{{< version exclude-if="2.0.x,2.1.x" >}}
{{< callout type="warning" >}}
**Known issue: `replace_with_random` returns the same value across requests in rustformation.** With rustformation, MiniJinja evaluates `replace_with_random` at template compile time when its arguments are constants and stores the result in the compiled template, so every request returns the same generated value. To get a fresh random per request, pass a per-request input such as `request_header("x-request-id")` — a non-constant argument can't be folded at compile time, so MiniJinja re-evaluates the function on every render. Tracked in [kgateway-dev/kgateway#13634](https://github.com/kgateway-dev/kgateway/issues/13634).
{{< /callout >}}
{{< /version >}}

**Other common functions**

You might use built-in template functions such as `if else` or `if exists`. For an example, see [Change response status]({{< link-hextra path="/traffic-management/transformations/simple/change-response-status/" >}}).

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

#### Template functions in headers  {#functions-headers}

You can use transformation functions in your templates to modify request and response headers.

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

The `parseAs` field controls how the body is buffered and interpreted.

{{< version include-if="2.1.x" >}}
* `AsJson` (default): The body is buffered and parsed as JSON. Top-level fields are available to the template by name. If the body is not valid JSON, a 400 Bad Request response is returned.
* `AsString`: The body is buffered and exposed to the template as a raw string. Set `parseAs: AsString` explicitly when your body is not valid JSON.
{{< /version >}}
{{< version include-if="2.2.x" >}}
The default and the available modes depend on the [transformation engine]({{< link-hextra path="/traffic-management/transformations/engines/" >}}) that is enabled.

* `AsString`: The body is buffered and exposed to the template as a raw string. This is the rustformation default. With the classic engine, you must set `parseAs: AsString` explicitly if your body is not valid JSON.
* `AsJson`: The body is buffered and parsed as JSON. Top-level fields are available to the template by name. This is the classic default. With the rustformation engine, you must set `parseAs: AsJson` explicitly to access JSON fields directly. If the body is not valid JSON, the classic engine returns a 400 Bad Request response, and the rustformation engine skips the transformation.
{{< /version >}}
{{< version exclude-if="2.0.x,2.1.x,2.2.x" >}}
* `AsString` (default): The body is buffered and exposed to the template as a raw string. Use this mode when you want to read or rewrite the body with [`body()`](#custom-functions) but do not need field-level access.
* `AsJson`: The body is buffered and parsed as JSON. Top-level fields are exposed to the template context, so you can read them with dot or bracket notation. If the body is not valid JSON, the filter falls back to skipping the transformation.
* `None`: The body is not buffered and all body processing is skipped. The [`body()`](#custom-functions) and [`context()`](#custom-inja-functions) functions return an empty string. Attempts to read JSON variables from a header template return a 400 response.
{{< /version >}}

The following example explicitly parses the body as a string.

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

#### Template function in the body
The following example uses a transformation function to get the `POD_NAME` environment variable from the gateway proxy and returns that value in a custom body string.

```yaml 

transformation: 
  response: 
    body: 
      value: 'This is the value of the POD_NAME environment variable: {{env("POD_NAME")}}'
```

This template results in a body similar to `This is the value of the POD_NAME environment variable: http-844ff8bc4d-dh4pn`. 

#### Header to body
To extract header information and add this information to the body, you can take multiple different approaches. The approach that is right for you depends on how you want to transform the body. 

**Template functions**:

The following example uses a transformation function to access the value of a request header. This value is added to a custom body string.
```yaml

transformation: 
  response: 
    body: 
      value: 'This is the value of the :path pseudo header: {{request_header(":path")}}.'
```

This template results in a body similar to `This is the value of the :path pseudo header: /json`. 


#### Body to body

{{< version include-if="2.1.x" >}}
{{< reuse "docs/snippets/kgateway.md" >}} automatically parses the body as JSON whenever a transformation is configured, so you can directly access top-level body fields to inject into your custom body.
{{< /version >}}
{{< version exclude-if="2.0.x,2.1.x" >}}
With rustformation, set `body.parseAs: AsJson` on the transformation. With `parseAs: AsJson`, the body is parsed and the top-level JSON fields are exposed to the template, so you can access them directly to inject into your custom body.
{{< /version >}}

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
      parseAs: AsJson
      value: '{"author": "{{ slideshow.author }}", "title": "{{ slideshow.title }}", "slides": "{{ slideshow.slides }}}'
```

The following body is returned after transformation: 
```
{"author": "Yours Truly", "title": "Sample Slide Show", "slides": "[{"title":"Wake up to WonderWidgets!","type":"all"},{"items":["Why <em>WonderWidgets</em> are great","Who <em>buys</em> WonderWidgets"],"title":"Overview","type":"all"}]}% 
```
