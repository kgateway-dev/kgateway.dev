In 2.1.x, {{< reuse "docs/snippets/kgateway.md" >}} uses the **classic transformation** engine. Classic transformation is a C++ filter that is statically linked into a custom Envoy build, and templates are powered by version 3.4 of the [Inja template engine](https://github.com/pantor/inja/tree/v3.4.0).

For the template syntax and the list of supported functions, see [Templating language]({{< link-hextra path="/traffic-management/transformations/templating-language/" >}}).

## Strict validation compatibility {#strict-validation-compatibility}

Strict validation runs an Envoy preflight against the generated xDS snapshot to block configuration that would be rejected at the data plane. In 2.1.x, strict validation works with classic transformation. For configuration steps, see [Strict validation]({{< link-hextra path="/install/advanced/#strict-validation" >}}).
