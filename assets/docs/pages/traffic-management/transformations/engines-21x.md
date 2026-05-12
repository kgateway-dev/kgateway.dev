{{< reuse "docs/snippets/kgateway-capital.md" >}} can transform requests and responses by using one of two transformation engines:

* **Classic transformation** (default in 2.1.x): A C++ filter that is statically linked into a custom Envoy build. Templates are powered by version 3.4 of the [Inja](https://github.com/pantor/inja/tree/v3.4.0) template engine.
* **Rustformation** (opt-in in 2.1.x): A Rust filter that is loaded into Envoy at runtime as a [dynamic module](https://www.envoyproxy.io/docs/envoy/latest/configuration/http/http_filters/dynamic_modules_filter). Templates are powered by the [MiniJinja](https://github.com/mitsuhiko/minijinja) template engine.

In 2.1.x, rustformation is still under active development and the classic engine is the recommended default. Rustformation becomes the default in 2.2.x. For long-term planning, see the [v2.2 transformation engine release note]({{< link-hextra path="/reference/release-notes/#v22-rustformation" >}}).

## Enable rustformation

To enable rustformation in 2.1.x, set the `USE_RUST_FORMATIONS` environment variable on the kgateway controller to `true`, or set `useRustFormations: true` in the kgateway Helm values. After kgateway restarts, any TrafficPolicy with a `transformation` field is processed by the rustformation filter instead of the classic filter.

```yaml
controller:
  env:
    USE_RUST_FORMATIONS: "true"
```

When the toggle is enabled, all transformation policies are handled by rustformation. You cannot run both engines side by side.

## Custom function availability in 2.1.x rustformation

The rustformation engine in 2.1.x is still a preview implementation. Only three custom template functions are registered:

* `substring(input, start, len)`
* `header(header_name)`
* `request_header(header_name)`

The other custom functions documented in [Templating language]({{< link-hextra path="/traffic-management/transformations/templating-language/#custom-inja-functions" >}}) (such as `body()`, `context()`, `env()`, `base64_encode`, `base64_decode`, `base64url_encode`, `base64url_decode`, `replace_with_random`, `replace_with_string`, and `raw_string`) are not available with rustformation in 2.1.x. Templates that call any of those functions fail to render. The full function set is registered in 2.2.x.

If you need any of the unregistered functions, run on the classic engine (which is the 2.1.x default) until you upgrade to 2.2.x.

## Behavior differences

Inja and MiniJinja are syntactically similar but not identical. If you opt in to rustformation in 2.1.x, review the following differences so that your existing templates continue to behave as you expect.

| Area | Classic (Inja) | Rustformation (MiniJinja) |
| --- | --- | --- |
| Whitespace | Whitespace is preserved as-is. | Trailing whitespace is right-trimmed by default. |
| `replace_with_random` | The same input string produces the same random replacement within a single request. For example, `replace_with_random("abc", "a")` and `replace_with_random("cba", "a")` replace `"a"` with the same generated value. | A new random value is generated on every call, so the two example calls produce different replacements. |
| Default body parsing | The body is automatically parsed as JSON whenever any transformation is configured, even if the template never reads from the body. | The body is treated as a string by default. To access JSON fields directly, set `transformation.<request\|response>.body.parseAs: AsJson`. |
| JSON body field access for headers with non-identifier characters | Classic requires the `.0` accessor and dot notation: `{{ headers.X-Incoming-Stuff.0 }}`. Bracket notation is rejected. | MiniJinja requires bracket notation: `{{ headers["X-Incoming-Stuff"][0] }}`. The `.0` accessor is not supported. |
| JSON field name collisions with custom Inja functions | No conflict. | If a JSON body field shares a name with a built-in template function (for example, `context`), the field value shadows the function and rendering fails because the value is not callable. Rename the field or avoid `parseAs: AsJson` for that template. |
| Body buffering | The classic filter buffers the body in its own internal structure and tracks buffer limits independently. | Rustformation relies on Envoy to buffer the body before the filter processes it. |
| Adding multiple headers with the same name | Not supported. | Not supported. The kgateway transformation API models headers as a map keyed by name, so each header can appear only once in `add`, `set`, or `remove`. |

For details about each behavior change, see the [v2.2 rustformation release note]({{< link-hextra path="/reference/release-notes/#v22-rustformation" >}}) and the upstream [MiniJinja documentation](https://docs.rs/minijinja/latest/minijinja/).

## Strict validation

Strict validation runs an Envoy preflight against the generated xDS snapshot to block configuration that would be rejected at the data plane. Strict validation works with classic transformation in 2.1.x. It does not work with rustformation because the control plane image does not bundle the rustformation dynamic module. If you need strict validation, leave `USE_RUST_FORMATIONS` set to `false`. For configuration steps, see [Strict validation]({{< link-hextra path="/operations/strict-validation/" >}}).

## Limitations

* In 2.1.x, the rustformation engine is opt-in and is intended for early evaluation. Solo recommends running the classic engine in production environments.
* Strict validation is not available when rustformation is enabled.
* You cannot mix classic and rustformation TrafficPolicies on the same controller. The `USE_RUST_FORMATIONS` setting is a global toggle.
