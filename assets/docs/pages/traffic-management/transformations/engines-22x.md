{{< reuse "docs/snippets/kgateway-capital.md" >}} can transform requests and responses by using one of two transformation engines:

* **Rustformation** (default in 2.2.x): A Rust filter that is loaded into Envoy at runtime as a [dynamic module](https://www.envoyproxy.io/docs/envoy/latest/configuration/http/http_filters/dynamic_modules_filter). Templates are powered by the [MiniJinja](https://github.com/mitsuhiko/minijinja) template engine.
* **Classic transformation** (opt-out fallback): A C++ filter that is statically linked into a custom Envoy build. Templates are powered by version 3.4 of the [Inja](https://github.com/pantor/inja/tree/v3.4.0) template engine.

In 2.2.x, rustformation is the default. Classic transformation is still available as a fallback so that you can switch back if you hit a missing feature or a regression. Classic transformation is removed in 2.3.x, so plan to migrate any classic-only templates before you upgrade.

## Switch back to classic transformation {#switch-back-to-classic-transformation}

Rustformation is enabled by default in 2.2.x. To fall back to classic transformation, set the `USE_RUST_FORMATIONS` environment variable on the kgateway controller to `false`, or set `useRustFormations: false` in the kgateway Helm values. After kgateway restarts, any TrafficPolicy with a `transformation` field is processed by the classic filter instead of the rustformation filter.

```yaml
controller:
  env:
    USE_RUST_FORMATIONS: "false"
```

Classic transformation requires the custom envoy-wrapper image, which is only published for `x86_64` (amd64). If you run kgateway on `arm64`, you cannot switch back to classic transformation. For more information, see [Architecture support](#architecture-support).

## Behavior differences {#behavior-differences}

Inja and MiniJinja are syntactically similar but not identical. If you have classic transformation templates that worked in 2.1.x or earlier, review the following differences before you upgrade to 2.2.x.

| Area | Classic (Inja) | Rustformation (MiniJinja) |
| --- | --- | --- |
| Whitespace | Whitespace is preserved as-is. | Trailing whitespace is right-trimmed by default. |
| `replace_with_random` | The same input string produces the same random replacement within a single request. For example, `replace_with_random("abc", "a")` and `replace_with_random("cba", "a")` replace `"a"` with the same generated value. | A new random value is generated on every call, so the two example calls produce different replacements. |
| Default body parsing | The body is automatically parsed as JSON whenever any transformation is configured, even if the template never reads from the body. | The body is treated as a string by default. To access JSON fields directly, set `transformation.<request\|response>.body.parseAs: AsJson`. |
| JSON body field access for headers with non-identifier characters | Classic requires the `.0` accessor and dot notation: `{{ headers.X-Incoming-Stuff.0 }}`. Bracket notation is rejected. | MiniJinja requires bracket notation: `{{ headers["X-Incoming-Stuff"][0] }}`. The `.0` accessor is not supported. |
| JSON field name collisions with custom Inja functions | No conflict. | If a JSON body field shares a name with a built-in template function (for example, `context`), the field value shadows the function and rendering fails because the value is not callable. Rename the field or avoid `parseAs: AsJson` for that template. |
| Body buffering | The classic filter buffers the body in its own internal structure and tracks buffer limits independently. | Rustformation relies on Envoy to buffer the body before the filter processes it. |
| Adding multiple headers with the same name | Not supported. | Not supported. The kgateway transformation API models headers as a map keyed by name, so each header can appear only once in `add`, `set`, or `remove`. |

For more details about syntax, see the upstream [MiniJinja documentation](https://docs.rs/minijinja/latest/minijinja/).

## Architecture support {#architecture-support}

Starting in v2.2.0, kgateway supports both `x86_64` (amd64) and `arm64` builds. The two builds use different Envoy images:

* `x86_64` uses a custom envoy-wrapper image that includes both the classic transformation filter and the rustformation dynamic module. You can run either engine.
* `arm64` uses the upstream Envoy image with the rustformation dynamic module loaded at runtime. The classic transformation filter is not available on `arm64`.

In addition, the transformation `add` operation is currently not supported on `arm64` builds. Use `set` instead, or run kgateway on `x86_64` if you need to append header values without replacing existing ones.

## Strict validation {#strict-validation}

Strict validation runs an Envoy preflight against the generated xDS snapshot to block configuration that would be rejected at the data plane. In 2.2.x, strict validation works with both transformation engines. The kgateway control plane image is built from the envoy-wrapper image, which bundles the rustformation dynamic module, and the validator loads the module from `/usr/local/lib` before running the preflight. You can run strict validation with rustformation (the default) or with classic transformation. For configuration steps, see [Strict validation]({{< link-hextra path="/operations/strict-validation/" >}}).

## Limitations {#limitations}

* On `arm64`, the rustformation `add` header operation is not supported. Use `set`.
* Classic transformation is deprecated and is removed in 2.3.x. If you fall back to classic in 2.2.x, plan to file issues for any rustformation gaps so that you can move back to the default before upgrading to 2.3.
