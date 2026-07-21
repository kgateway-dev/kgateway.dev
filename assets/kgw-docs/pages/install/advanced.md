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

{{< version exclude-if="2.2.x,2.1.x">}}

## ReferenceGrant enforcement modes

In multi-tenant clusters, different teams typically own separate namespaces and share a gateway. The Gateway API [ReferenceGrant](https://gateway-api.sigs.k8s.io/reference/api-types/referencegrant/) mechanism controls which cross-namespace references are permitted, ensuring that one team cannot silently access another team's resources. Without a ReferenceGrant in the target namespace, the reference is denied.

In {{< reuse "kgw-docs/snippets/kgateway.md" >}}, you can configure how strictly you want ReferenceGrant requirements to be enforced by using the `KGW_REFERENCE_GRANT_MODE` environment variable on the control plane. You can choose between the following modes: 

- **`STRICT`**: Enforce ReferenceGrants for all cross-namespace references. This mode provides the strongest namespace isolation and is recommended for new clusters.
- **`PERMISSIVE`** (default): Enforce ReferenceGrants for `BackendRef` and `SecretRef` references, but not for cross-namespace `ExtensionRef` references. Before reference grant modes were introduced, {{< reuse "kgw-docs/snippets/trafficpolicy.md" >}} resources were able to reference and access a GatewayExtension resource in another namespace without a ReferenceGrant. `PERMISSIVE` mode allows these setups to function as before. Over time, you can add the missing ReferenceGrant resources in the required namespaces and migrate your cluster to `STRICT` ReferenceGrant validation. 
- **`OFF`**: Disable all ReferenceGrant validation. Not recommended for multi-tenant or production environments.
  > [!CAUTION]
  > Do not use `OFF` in multi-tenant or production environments. It breaks Gateway API compliance, bypasses namespace isolation, and lets any namespace access backends, secrets, and GatewayExtensions in other namespaces without restriction.

### Reference validation by mode {#referencegrant-modes}

The following table shows which cross-namespace references are checked in each mode. Same-namespace references always pass, regardless of the mode. 

| Source resource | Field | Referenced resource | `STRICT` | `PERMISSIVE` (default) | `OFF` |
|---|---|---|---|---|---|
| HTTPRoute / <br>GRPCRoute / <br>TCPRoute / <br>TLSRoute | `spec.rules[].backendRefs` | Service / Backend | checked | checked | allowed |
| Gateway / <br>ListenerSet | `spec.listeners[].tls.certificateRefs` | Secret | checked | checked | allowed |
| TrafficPolicy | `spec.basicAuth.secretRef` / `spec.apiKeyAuth.secretRef` | Secret | checked | checked | allowed |
| GatewayExtension (ExtAuth, ExtProc, RateLimit, OAuth2) | `spec.<type>.grpcService.backendRef` | Service | checked | checked | allowed |
| {{< reuse "kgw-docs/snippets/trafficpolicy.md" >}} | `spec.<plugin>.extensionRef` | GatewayExtension (same namespace) | allowed | allowed | allowed |
| {{< reuse "kgw-docs/snippets/trafficpolicy.md" >}} | `spec.<plugin>.extensionRef` | GatewayExtension (different namespace) | checked | allowed | allowed |

### Enable STRICT mode {#set-referencegrant-mode}

1. Check which mode is currently active by inspecting the `KGW_REFERENCE_GRANT_MODE` environment variable on the controller deployment. If the variable is not set, the active mode is `PERMISSIVE`.
   ```sh
   kubectl -n {{< reuse "kgw-docs/snippets/namespace.md" >}} get deployment {{< reuse "kgw-docs/snippets/pod-name.md" >}} \
     -o jsonpath='{.spec.template.spec.containers[*].env[?(@.name=="KGW_REFERENCE_GRANT_MODE")].value}'
   ```

2. Make sure that any existing cross-namespace {{< reuse "kgw-docs/snippets/trafficpolicy.md" >}} → GatewayExtension references have a corresponding ReferenceGrant. 

3. Get the current Helm values for your {{< reuse "kgw-docs/snippets/kgateway.md" >}} release and save them to a file.

   ```sh
   helm get values {{< reuse "/kgw-docs/snippets/helm-kgateway.md" >}} -n {{< reuse "kgw-docs/snippets/namespace.md" >}} -o yaml > values.yaml
   open values.yaml
   ```

4. Add the following values to enable `STRICT` ReferenceGrant validation. 

   ```yaml
   controller:
     extraEnv:
       KGW_REFERENCE_GRANT_MODE: "STRICT"
   ```

5. Apply the change by upgrading the Helm release.

   ```sh
   helm upgrade -i -n {{< reuse "kgw-docs/snippets/namespace.md" >}} {{< reuse "/kgw-docs/snippets/helm-kgateway.md" >}} \
     oci://{{< reuse "/kgw-docs/snippets/helm-path.md" >}}/charts/{{< reuse "/kgw-docs/snippets/helm-kgateway.md" >}} \
     --version {{< reuse "kgw-docs/versions/n-patch.md" >}} \
     -f values.yaml
   ```

6. Confirm that the {{< reuse "kgw-docs/snippets/kgateway.md" >}} control plane restarted and is running.

   ```sh
   kubectl get pods -n {{< reuse "kgw-docs/snippets/namespace.md" >}}
   ```

7. Verify the active mode.

   ```sh
   kubectl -n {{< reuse "kgw-docs/snippets/namespace.md" >}} get deployment {{< reuse "kgw-docs/snippets/kgateway.md" >}}  \
     -o jsonpath='{.spec.template.spec.containers[*].env[?(@.name=="KGW_REFERENCE_GRANT_MODE")].value}'
   ```

{{< /version >}}

{{< version include-if="2.4.x,2.5.x" >}}

## Disable automatic RBAC creation {#disable-rbac}

By default, the {{< reuse "kgw-docs/snippets/kgateway.md" >}} Helm chart creates a `ClusterRole` and `ClusterRoleBinding` that grant the controller's service account the permissions it needs to watch and manage Kubernetes resources. In environments where RBAC resources are managed externally, such as by a platform or security team that controls all cluster-scoped permissions, you can disable the creation of these resources by setting `rbac.create: false`.

> [!CAUTION]
> If you disable the creation of ClusterRole and ClusterRoleBinding resources, you must create equivalent resources yourself before or alongside the {{< reuse "kgw-docs/snippets/kgateway.md" >}} installation. Without these resources, the controller cannot watch and manage Gateways, HTTPRoutes, Secrets, or other resources. 

To skip RBAC resource creation, set `rbac.create: false` in your Helm values:

```yaml
rbac:
  create: false
```

{{< /version >}}
