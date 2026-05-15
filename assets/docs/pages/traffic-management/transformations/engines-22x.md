{{< reuse "docs/snippets/kgateway-capital.md" >}} can transform requests and responses by using one of two transformation engines:

* **Rustformation** (default in 2.2.x): A Rust filter that is loaded into Envoy at runtime as a [dynamic module](https://www.envoyproxy.io/docs/envoy/latest/configuration/http/http_filters/dynamic_modules_filter). Templates are powered by the [MiniJinja](https://github.com/mitsuhiko/minijinja) template engine.
* **Classic transformation** (opt-out fallback): A C++ filter that is statically linked into a custom Envoy build. Templates are powered by version 3.4 of the [Inja](https://github.com/pantor/inja/tree/v3.4.0) template engine.

In 2.2.x, rustformation is the default. Classic transformation is still available as a fallback so that you can switch back if you hit a missing feature or a regression. Classic transformation is removed in 2.3.x, so plan to migrate any classic-only templates before you upgrade.

## Switch back to classic transformation {#switch-back-to-classic-transformation}

To fall back to classic transformation, set `useRustFormations: false` in the kgateway Helm values, or set the `USE_RUST_FORMATIONS` environment variable on the kgateway controller to `false`. After kgateway restarts, any TrafficPolicy with a `transformation` field is processed by the classic filter instead of the rustformation filter.

Helm values:

```yaml
useRustFormations: false
```

Controller environment variable:

```yaml
controller:
  env:
    USE_RUST_FORMATIONS: "false"
```

Classic transformation requires the custom envoy-wrapper image, which is only published for `x86_64` (amd64). If you run kgateway on `arm64`, you cannot switch back to classic transformation. For more information, see [Architecture support](#architecture-support).

## Behavior differences {#behavior-differences}

Inja and MiniJinja are syntactically similar but not identical. If you have classic transformation templates that worked in 2.1.x or earlier, review the following differences before you upgrade to 2.2.x.

{{< reuse "docs/pages/traffic-management/transformations/migrating-classic.md" >}}

## Architecture support {#architecture-support}

Starting in v2.2.0, kgateway supports both `x86_64` (amd64) and `arm64` builds. The two builds use different Envoy images:

* `x86_64` uses a custom envoy-wrapper image that includes both the classic transformation filter and the rustformation dynamic module. You can run either engine.
* `arm64` uses the upstream Envoy image with the rustformation dynamic module loaded at runtime. The classic transformation filter is not available on `arm64`.


## Strict validation compatibility {#strict-validation-compatibility}

Strict validation runs an Envoy preflight against the generated xDS snapshot to block configuration that would be rejected at the data plane. In 2.2.x, strict validation works with both transformation engines. The kgateway control plane image is built from the envoy-wrapper image, which bundles the rustformation dynamic module, and the validator loads the module from `/usr/local/lib` before running the preflight. You can run strict validation with rustformation (the default) or with classic transformation. For configuration steps, see [Strict validation]({{< link-hextra path="/install/advanced/#strict-validation" >}}).

## Limitations {#limitations}

* The transformation `add` operation is currently not supported on `arm64` builds. Use `set` instead, or run kgateway on `x86_64` if you need to append header values without replacing existing ones.
* Classic transformation is deprecated. If you fall back to classic in 2.2.x, plan to file issues for any rustformation gaps so that you can move back to the default before upgrading.
