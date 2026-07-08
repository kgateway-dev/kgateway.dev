You can update several installation settings in your Helm values file. For example, you can update the namespace, set resource limits and requests, or enable extensions such as for AI. 

Set the version you want to configure in an environment variable, such as the latest patch version (`{{< reuse "kgw-docs/versions/n-patch.md" >}}`).
   ```sh
   export NEW_VERSION={{< reuse "kgw-docs/versions/n-patch.md" >}}
   ```
* **Show all values**: 
      
  ```sh
  helm show values oci://{{< reuse "/kgw-docs/snippets/helm-path.md" >}}/charts/{{< reuse "/kgw-docs/snippets/helm-kgateway.md" >}} --version {{< reuse "kgw-docs/versions/helm-version-upgrade.md" >}}
  ```

* **Get a file with all values**: You can get a `{{< reuse "/kgw-docs/snippets/helm-kgateway.md" >}}/values.yaml` file for the upgrade version by pulling and inspecting the Helm chart locally.
      
  ```sh
  helm pull oci://{{< reuse "/kgw-docs/snippets/helm-path.md" >}}/charts/{{< reuse "/kgw-docs/snippets/helm-kgateway.md" >}} --version {{< reuse "kgw-docs/versions/helm-version-upgrade.md" >}}
  tar -xvf {{< reuse "/kgw-docs/snippets/helm-kgateway.md" >}}-{{< reuse "kgw-docs/versions/helm-version-upgrade.md" >}}.tgz
  open {{< reuse "/kgw-docs/snippets/helm-kgateway.md" >}}/values.yaml
  ```

For more information, see the [Helm reference docs]({{< link-hextra path="/reference/helm/" >}}).

## Development builds

When using the development build {{< reuse "kgw-docs/versions/patch-dev.md" >}}, add `--set controller.image.pullPolicy=Always` to ensure you get the latest image. For production environments, this setting is not recommended as it might impact performance.

### Experimental Gateway API features {#experimental-gateway-api-features}

The `KGW_ENABLE_EXPERIMENTAL_GATEWAY_API_FEATURES` feature gate controls support for experimental Gateway API features such as the following:

- TCPRoutes
- TLSRoutes
- ListenerSets
- CORS policies
- Retries
- Session persistence

{{< version include-if="2.0.x,2.1.x" >}}This setting defaults to `false` and must be explicitly enabled. To enable these features, set the environment variable in your kgateway controller deployment in your Helm values file.

```yaml
controller:
  extraEnv:
    KGW_ENABLE_EXPERIMENTAL_GATEWAY_API_FEATURES: "true"
```{{< /version >}}{{< version exclude-if="2.0.x,2.1.x" >}}In kgateway version 2.2 and later, this setting defaults to `true`, so experimental features are enabled by default and no additional configuration is required. To disable these features, set the environment variable to `false` in your kgateway controller deployment in your Helm values file.

```yaml
controller:
  extraEnv:
    KGW_ENABLE_EXPERIMENTAL_GATEWAY_API_FEATURES: "false"
```{{< /version >}}

## Leader election

Leader election is enabled by default to ensure that you can run {{< reuse "kgw-docs/snippets/kgateway.md" >}} in a multi-control plane replica setup for high availability. 

You can disable leader election by setting the `KGW_DISABLE_LEADER_ELECTION` environment variable to `"true"` through the `controller.extraEnv` Helm value.

```yaml
controller:
  extraEnv:
    KGW_DISABLE_LEADER_ELECTION: "true"
```


## Namespace discovery {#namespace-discovery}

You can limit the namespaces that {{< reuse "/kgw-docs/snippets/kgateway.md" >}} watches for gateway configuration. For example, you might have a multi-tenant cluster with different namespaces for different tenants. You can limit {{< reuse "/kgw-docs/snippets/kgateway.md" >}} to only watch a specific namespace for gateway configuration.

Namespace selectors are a list of matched expressions or labels.

* `matchExpressions`: Use this field for more complex selectors where you want to specify an operator such as `In` or `NotIn`.
* `matchLabels`: Use this field for simple selectors where you want to specify a label key-value pair.

Each entry in the list is disjunctive (OR semantics). This means that a namespace is selected if it matches any selector.

You can also use matched expressions and labels together in the same entry, which is conjunctive (AND semantics).

The following example selects namespaces for discovery that meet either of the following conditions:

* The namespace has the label `environment=prod` and the label `version=v2`, or
* The namespace has the label `version=v3`

```yaml

discoveryNamespaceSelectors:
- matchExpressions:
  - key: environment
    operator: In
    values:
    - prod
  matchLabels:
    version: v2
- matchLabels:
    version: v3
```

{{< conditional-text include-if="envoy" >}}
## TLS encryption {#tls-encryption}

You can enable TLS encryption for the xDS gRPC server in the {{< reuse "kgw-docs/snippets/kgateway.md" >}} control plane. For more information, see the [TLS encryption]({{< link-hextra path="/install/tls" >}}) docs.
{{< /conditional-text >}}

## Strict validation

{{< reuse "kgw-docs/snippets/kgateway-capital.md" >}} supports two validation modes for routes and policies in the control plane: `standard` and `strict`. The validation mode controls how the control plane handles invalid configuration before it is sent to Envoy.

### Validation modes

{{< reuse "kgw-docs/snippets/kgateway-capital.md" >}} supports the following validation modes. The mode is set globally on the controller through a single Helm value.

| Mode | Behavior |
| --- | --- |
| `standard` (default) | The control plane translates all valid resources and replaces invalid routes with a direct response (typically `HTTP 500`). Valid routes that are unrelated to the invalid resource are unaffected. This mode protects multi-tenant clusters from individual misconfiguration without dropping the entire snapshot. |
| `strict` | In addition to the `standard` behavior, the control plane runs an Envoy preflight validation against the generated xDS snapshot. If Envoy would reject the snapshot, the entire snapshot is blocked and the previous valid configuration remains in place. This mode prevents misconfigurations that would otherwise cause Envoy to NACK an xDS update from reaching the data plane. |

`standard` mode is the default and is appropriate for most production environments. `strict` mode is recommended when you cannot tolerate a NACKed xDS update reaching the data plane; for example, you might have downstream automation that depends on every accepted change being safe.

### Enable strict validation

Set the `validation.level` Helm value to `strict` when you install or upgrade kgateway. Restart the control plane to apply the change.

```yaml
validation:
  level: strict
```

Internally, the Helm chart passes the value to the control plane through the `KGW_VALIDATION_MODE` environment variable. If you manage the control plane deployment manually, set `KGW_VALIDATION_MODE=STRICT` on the kgateway container.

The accepted values for `validation.level` are `standard` and `strict` (case-insensitive). Any other value causes the Helm install to fail.

### Verify the validation mode

To check which mode is active, inspect the `KGW_VALIDATION_MODE` environment variable on the kgateway controller deployment. The expected output is `standard` or `strict`.

```sh
kubectl -n {{< reuse "kgw-docs/snippets/namespace.md" >}} get deployment kgateway \
  -o jsonpath='{.spec.template.spec.containers[*].env[?(@.name=="KGW_VALIDATION_MODE")].value}'
```


### Transformation policies and strict validation

Strict validation runs the preflight against an Envoy binary that is bundled in the kgateway control plane image. The control plane image is built from the envoy-wrapper image, which bundles the rustformation dynamic module, and the validator sets `ENVOY_DYNAMIC_MODULES_SEARCH_PATH=/usr/local/lib` before invoking the preflight. As a result, the preflight understands rustformation per-route config and can validate TrafficPolicies that use `transformation`.

For more information about transformation engines, see [Transformation engines]({{< link-hextra path="/traffic-management/transformations/engines/" >}}).

{{< version exclude-if="2.2.x,2.1.x,2.0.x">}}

## ReferenceGrant enforcement modes

The Gateway API [ReferenceGrant](https://gateway-api.sigs.k8s.io/reference/api-types/referencegrant/) mechanism controls which cross-namespace references are permitted. {{< reuse "kgw-docs/snippets/kgateway.md" >}} supports three enforcement modes that you set with the `KGW_REFERENCE_GRANT_MODE` environment variable on the control plane, such as with the following example.

```yaml

controller:
  extraEnv:
    KGW_REFERENCE_GRANT_MODE: "PERMISSIVE"
```

The default mode is `PERMISSIVE` so that GatewayExtensions such as for external auth are permitted out of the box. The following table describes the three modes.

| Mode | Behavior |
|------|----------|
| `OFF` | Disables all ReferenceGrant validation and permits unrestricted cross-namespace references. |
| `PERMISSIVE` (default) | Enforces ReferenceGrant for `BackendRef` and `SecretRef` cross-namespace references. Cross-namespace `ExtensionRef` references (such as a TrafficPolicy that references a GatewayExtension) are not checked and are always permitted. |
| `STRICT` | Enforces ReferenceGrant for all cross-namespace references, including `ExtensionRef`. References that are missing a grant are rejected, and the referencing policy reports a `RouteRuleReplaced` condition. |

The following table shows which reference types are checked in each mode. Same-namespace references always pass, regardless of the mode.

| Reference | From | To | `OFF` | `PERMISSIVE` | `STRICT` |
|-----------|------|----|-------|--------------|----------|
| `BackendRef` | HTTPRoute / GRPCRoute | Service / Backend | allowed | checked | checked |
| `SecretRef` | TrafficPolicy (BasicAuth, APIKeyAuth) | Secret | allowed | checked | checked |
| `BackendRef` | GatewayExtension (ExtAuth, ExtProc, RateLimit, OAuth2) | Service | allowed | checked | checked |
| `ExtensionRef` | TrafficPolicy | GatewayExtension (same namespace) | allowed | allowed | allowed |
| `ExtensionRef` | TrafficPolicy | GatewayExtension (cross namespace) | allowed | allowed | checked |

{{< callout type="warning" >}}
Avoid `OFF` mode in multi-tenant or production environments. It breaks Gateway API compliance, bypasses namespace isolation, and can allow any namespace to access backends, secrets, and GatewayExtensions in other namespaces, which introduces secret exfiltration risks.
{{< /callout >}}

`STRICT` mode closes a transitive exposure gap: a TrafficPolicy that references a GatewayExtension gains indirect access to that extension's secrets. To allow a cross-namespace `ExtensionRef` in `STRICT` mode, create a ReferenceGrant in the target namespace. For example, the following ReferenceGrant permits a TrafficPolicy in the `app` namespace to reference a GatewayExtension in the `{{< reuse "kgw-docs/snippets/namespace.md" >}}` namespace.

```yaml
apiVersion: gateway.networking.k8s.io/v1beta1
kind: ReferenceGrant
metadata:
  name: allow-trafficpolicy-to-gwext
  namespace: {{< reuse "kgw-docs/snippets/namespace.md" >}}
spec:
  from:
    - group: gateway.kgateway.dev
      kind: TrafficPolicy
      namespace: app
  to:
    - group: gateway.kgateway.dev
      kind: GatewayExtension
```

{{< /version >}}
