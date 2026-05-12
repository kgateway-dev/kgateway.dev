{{< reuse "docs/snippets/kgateway-capital.md" >}} supports two validation modes for routes and policies in the control plane: `standard` and `strict`. The validation mode controls how the control plane handles invalid configuration before it is sent to Envoy.

## Validation modes

{{< reuse "docs/snippets/kgateway-capital.md" >}} supports the following validation modes. The mode is set globally on the controller through a single Helm value.

| Mode | Behavior |
| --- | --- |
| `standard` (default) | The control plane translates all valid resources and replaces invalid routes with a direct response (typically `HTTP 500`). Valid routes that are unrelated to the invalid resource are unaffected. This mode protects multi-tenant clusters from individual misconfiguration without dropping the entire snapshot. |
| `strict` | In addition to the `standard` behavior, the control plane runs an Envoy preflight validation against the generated xDS snapshot. If Envoy would reject the snapshot, the entire snapshot is blocked and the previous good config remains in place. This mode prevents misconfigurations that would otherwise cause Envoy to NACK an xDS update from reaching the data plane. |

`standard` mode is the default and is appropriate for most production environments. `strict` mode is recommended when you cannot tolerate a NACKed xDS update reaching the data plane, for example because you have downstream automation that depends on every accepted change being safe.

## Enable strict validation

Set the `validation.level` Helm value to `strict` when you install or upgrade kgateway. Restart the control plane to apply the change.

```yaml
validation:
  level: strict
```

Internally, the Helm chart passes the value to the control plane through the `KGW_VALIDATION_MODE` environment variable. If you manage the control plane deployment manually, set `KGW_VALIDATION_MODE=STRICT` on the kgateway container.

The accepted values for `validation.level` are `standard` and `strict` (case-insensitive). Any other value causes the Helm install to fail.

## Verify the validation mode

To check which mode is active, inspect the `KGW_VALIDATION_MODE` env var on the kgateway controller deployment. The expected output is `standard` or `strict`.

```sh
kubectl -n {{< reuse "docs/snippets/namespace.md" >}} get deployment kgateway \
  -o jsonpath='{.spec.template.spec.containers[*].env[?(@.name=="KGW_VALIDATION_MODE")].value}'
```



## Transformation policies and strict validation

Strict validation runs the preflight against an Envoy binary that is bundled in the kgateway control plane image. The control plane image is built from the envoy-wrapper image, which bundles the rustformation dynamic module, and the validator sets `ENVOY_DYNAMIC_MODULES_SEARCH_PATH=/usr/local/lib` before invoking the preflight. As a result, the preflight understands rustformation per-route config and can validate TrafficPolicies that use `transformation`.

Behavior by version:

* **2.1.x:** Strict validation works with classic transformation (the 2.1.x default). It does not work with rustformation, because the 2.1.x validator was not yet wired to load dynamic modules during the preflight. If you opted in to rustformation by setting `useRustFormations: true`, switch the setting back to `false` before you enable strict mode.
* **2.2.x and 2.3.x:** Strict validation works with both transformation engines (2.2.x) and with rustformation (2.3.x, where rustformation is the only engine). No additional configuration is required.

For more information about the engines, see [Transformation engines]({{< link-hextra path="/traffic-management/transformations/engines/" >}}).
