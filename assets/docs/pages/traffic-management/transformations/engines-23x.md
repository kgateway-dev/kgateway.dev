{{< reuse "docs/snippets/kgateway.md" >}} uses a single transformation engine: **rustformation**. Rustformation is a Rust filter that is loaded into Envoy at runtime as a [dynamic module](https://www.envoyproxy.io/docs/envoy/latest/configuration/http/http_filters/dynamic_modules_filter). Templates are powered by the [MiniJinja](https://github.com/mitsuhiko/minijinja) template engine.

{{< callout type="warning" >}}
The classic C++ transformation filter that was the default in 2.1.x and the fallback in 2.2.x is removed in 2.3.x and later. The `USE_RUST_FORMATIONS` setting and the `useRustFormations` Helm value have no effect.

If you upgrade from 2.2.x with `USE_RUST_FORMATIONS=false`, plan to migrate your templates to rustformation syntax before you upgrade to 2.3.x. For migration help, see [Migrating from classic transformation](#migrating-from-classic-transformation).
{{< /callout >}}

## Migrating from classic transformation

If you migrate templates that previously ran on the classic engine, review the following differences:

| Area | Classic (Inja) | Rustformation (MiniJinja) |
| --- | --- | --- |
| Whitespace | Whitespace is preserved as-is. | Trailing whitespace is right-trimmed by default. |
| `replace_with_random` | The same input string produces the same random replacement within a single request. | A new random value is generated on every call. |
| Default body parsing | The body is automatically parsed as JSON whenever any transformation is configured. | The body is treated as a string by default. Set `transformation.<request\|response>.body.parseAs: AsJson` to access JSON fields directly. |
| JSON body field access for headers with non-identifier characters | Classic requires the `.0` accessor and dot notation: `{{ headers.X-Incoming-Stuff.0 }}`. | MiniJinja requires bracket notation: `{{ headers["X-Incoming-Stuff"][0] }}`. |
| JSON field name collisions with custom Inja functions | No conflict. | If a JSON body field shares a name with a built-in template function (for example, `context`), the field value shadows the function and rendering fails. Rename the field or avoid `parseAs: AsJson` for that template. |
| Body buffering | The classic filter buffers the body in its own internal structure and tracks buffer limits independently. | Rustformation relies on Envoy to buffer the body. Tunnel upgrades, such as `CONNECT` and WebSocket, automatically bypass buffering. |
| Adding multiple headers with the same name | Not supported. | Not supported. The kgateway transformation API models headers as a map keyed by name. |

For more details about syntax, see the upstream [MiniJinja documentation](https://docs.rs/minijinja/latest/minijinja/).

## Body parsing modes

The `body.parseAs` field controls how rustformation buffers and interprets the request or response body. Three modes are available:

* `AsString` (default): The body is buffered and made available to templates as a raw string. Use this mode when you want to read or rewrite the body with [`body()`]({{< link-hextra path="/traffic-management/transformations/templating-language/#custom-inja-functions" >}}) but do not need field-level access.
* `AsJson`: The body is buffered and parsed as JSON. Top-level JSON fields are exposed to the template context, so you can read them with dot or bracket notation. If the body is not valid JSON, the filter falls back to skipping the transformation.
* `None`: The body is not buffered. All body processing is skipped, and the [`body()`]({{< link-hextra path="/traffic-management/transformations/templating-language/#custom-inja-functions" >}}) and [`context()`]({{< link-hextra path="/traffic-management/transformations/templating-language/#custom-inja-functions" >}}) functions return an empty string. Attempts to read JSON variables from a header template return a 400 response.

Rustformation also auto-detects `CONNECT` requests and WebSocket upgrade requests and bypasses buffering for those connections, even if `parseAs` is not `None`. This prevents long-lived tunnels from stalling on body buffering.

## Dynamic metadata

You can populate Envoy dynamic metadata from a transformation by using the `dynamicMetadata` field. Values you set are available to downstream filters and to access log formatters.

```yaml
transformation:
  request:
    dynamicMetadata:
    - namespace: my.team.namespace
      key: user_id
      value:
        stringValue: '{{ request_header("x-user-id") }}'
```

The `value.stringValue` field accepts a MiniJinja template. The rendered output is stored as a string in the named dynamic metadata namespace and key. For details about the available filter chain placement, see the [Envoy dynamic metadata documentation](https://www.envoyproxy.io/docs/envoy/latest/configuration/advanced/well_known_dynamic_metadata).

## Strict validation

Strict validation runs an Envoy preflight against the generated xDS snapshot to block configuration that would be rejected at the data plane. In 2.3.x, strict validation works with rustformation. The kgateway control plane image is built from the envoy-wrapper image, which bundles the rustformation dynamic module, and the validator loads the module from `/usr/local/lib` before running the preflight. You can safely run TrafficPolicies with `transformation` on Gateways that have strict validation enabled. For configuration steps, see [Strict validation]({{< link-hextra path="/operations/strict-validation/" >}}).

## Limitations

* `replace_with_random` caches its random output per input string within a policy and reuses the cached value across requests. For details and a workaround, see the known-issue callout in [Templating language]({{< link-hextra path="/traffic-management/transformations/templating-language/#custom-inja-functions" >}}). Tracked in [kgateway-dev/kgateway#13634](https://github.com/kgateway-dev/kgateway/issues/13634).
