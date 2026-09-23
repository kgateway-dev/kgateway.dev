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

- **`STRICT`**: Enforce ReferenceGrants for every cross-namespace reference in the [following table](#referencegrant-modes), including cross-namespace `ExtensionRef` references. This mode provides the strongest namespace isolation and is recommended for new clusters.
- **`PERMISSIVE`** (default): Enforce ReferenceGrants for every cross-namespace reference in the [following table](#referencegrant-modes) except cross-namespace `ExtensionRef` references. Before reference grant modes were introduced, {{< reuse "kgw-docs/snippets/trafficpolicy.md" >}} resources were able to reference and access a GatewayExtension resource in another namespace without a ReferenceGrant. `PERMISSIVE` mode allows these setups to function as before. Over time, you can add the missing ReferenceGrant resources in the required namespaces and migrate your cluster to `STRICT` ReferenceGrant validation. 
- **`OFF`**: Disable all ReferenceGrant validation. Not recommended for multi-tenant or production environments.
  > [!CAUTION]
  > Do not use `OFF` in multi-tenant or production environments. It breaks Gateway API compliance, bypasses namespace isolation, and lets any namespace access backends, secrets, and GatewayExtensions in other namespaces without restriction.

### Reference validation by mode {#referencegrant-modes}

The following table shows which cross-namespace references are checked in each mode. Same-namespace references always pass, regardless of the mode. 

| Source resource | Field | Referenced resource | `STRICT` | `PERMISSIVE` (default) | `OFF` |
|---|---|---|---|---|---|
| HTTPRoute / <br>GRPCRoute / <br>TCPRoute / <br>TLSRoute | `spec.rules[].backendRefs` | Service / Backend | checked | checked | allowed |
| HTTPRoute / <br>GRPCRoute | `spec.rules[].filters[].requestMirror.backendRef` | Service / Backend | checked | checked | allowed |
| Gateway / <br>ListenerSet | `spec.listeners[].tls.certificateRefs` | Secret | checked | checked | allowed |
| Gateway / <br>ListenerSet | `spec.listeners[].tls.frontendValidation.caCertificateRefs`, or `spec.default.clientCertificateValidation.caCertificateRefs` on a ListenerPolicy that targets the listener | Secret / ConfigMap | checked | checked | allowed |
| Gateway | `spec.backendTLS.clientCertificateRef` | Secret | checked | checked | allowed |
| GatewayExtension (ExtAuth, ExtProc, RateLimit) | `spec.<type>.grpcService.backendRef` | Service / Backend | checked | checked | allowed |
| GatewayExtension | `spec.extAuth.httpService.backendRef` | Service / Backend | checked | checked | allowed |
| GatewayExtension | `spec.oauth2.backendRef`{{< version exclude-if="2.0.x,2.1.x,2.2.x,2.3.x" >}} / <br>`spec.oauth2.jwt.jwksBackendRef`{{< /version >}} | Service / Backend | checked | checked | allowed |
| GatewayExtension | `spec.jwt.providers[].jwks.remote.backendRef` | Service / Backend | checked | checked | allowed |
| ListenerPolicy | `spec.default.httpSettings.accessLog[].grpcService.backendRef` / <br>`spec.default.httpSettings.accessLog[].openTelemetry.grpcService.backendRef` | Service / Backend | checked | checked | allowed |
| ListenerPolicy | `spec.default.httpSettings.tracing.provider.openTelemetry.grpcService.backendRef` | Service / Backend | checked | checked | allowed |{{% version exclude-if="2.0.x,2.1.x,2.2.x,2.3.x" %}}
| ListenerPolicy | `spec.default.httpSettings.localReplies.mappers[].headers.set[].secretRef` / <br>`spec.default.httpSettings.localReplies.mappers[].headers.add[].secretRef` | Secret | checked | checked | allowed |
| {{< reuse "kgw-docs/snippets/trafficpolicy.md" >}}{{% downstream %}}*{{% /downstream %}} | `spec.headerModifiers.request.set[].secretRef` / <br>`spec.headerModifiers.request.add[].secretRef` / <br>`spec.headerModifiers.response.set[].secretRef` / <br>`spec.headerModifiers.response.add[].secretRef` | Secret | checked | checked | allowed |{{% /version %}}
| {{< reuse "kgw-docs/snippets/trafficpolicy.md" >}}{{% downstream %}}*{{% /downstream %}} | `spec.basicAuth.secretRef` / <br>`spec.apiKeyAuth.secretRef` / <br>`spec.apiKeyAuth.secretSelector` | Secret | checked | checked | allowed |
| {{< reuse "kgw-docs/snippets/trafficpolicy.md" >}}{{% downstream %}}*{{% /downstream %}} | `spec.<plugin>.extensionRef` | GatewayExtension (same namespace) | allowed | allowed | allowed |
| {{< reuse "kgw-docs/snippets/trafficpolicy.md" >}}{{% downstream %}}*{{% /downstream %}} | `spec.<plugin>.extensionRef` | GatewayExtension (different namespace) | checked | allowed | allowed |
{{% downstream %}}| {{< reuse "kgw-docs/snippets/trafficpolicy.md" >}}† | `spec.entJWT.<stage>.providers.<name>.jwks.remote.backendRef` | Service / Backend | checked | checked | allowed |
| {{< reuse "kgw-docs/snippets/trafficpolicy.md" >}}† | `spec.entWAF.wafServerRef` | Service / Backend | checked | checked | allowed |
| {{< reuse "kgw-docs/snippets/trafficpolicy.md" >}}† | `spec.entGrpcJsonTranscoder.protoDescriptorConfigMap` | ConfigMap | checked | checked | allowed |
{{% /downstream %}}

> [!IMPORTANT]
> In most cases, the **Source resource** column is the resource that you name in the `from` section of your ReferenceGrant. If you configure a CA certificate reference on a ListenerPolicy by using the `spec.default.clientCertificateValidation.caCertificateRefs` field, you must use the Gateway or ListenerSet that owns that listener in the `from` section of your ReferenceGrant and not the ListenerPolicy.
> {{% downstream %}}
> 
> Cross-namespace references from an {{< reuse "kgw-docs/snippets/trafficpolicy.md" >}} are evaluated as the `TrafficPolicy` kind, including the `apiKeyAuth`, `basicAuth`, `headerModifiers`, and `extensionRef` fields, and the `extensionRef` fields in `entExtAuth` and `entRateLimit.global`. For these fields, you must use the `gateway.kgateway.dev` group and the `TrafficPolicy` kind in the `from` section of your ReferenceGrant. A grant that names the `enterprisekgateway.solo.io` group or the {{< reuse "kgw-docs/snippets/trafficpolicy.md" >}} kind is accepted by the API server, never matches, and the policy fails with `missing reference grant`.
> 
> The exceptions are the Backend references in `entJWT` and `entWAF`, and the ConfigMap reference in `entGrpcJsonTranscoder`. These references are evaluated as the {{< reuse "kgw-docs/snippets/trafficpolicy.md" >}} kind, so their grants must name the `enterprisekgateway.solo.io` group and the {{< reuse "kgw-docs/snippets/trafficpolicy.md" >}} kind.
> 
> References from an {{< reuse "kgw-docs/snippets/trafficpolicy.md" >}} to an AuthConfig, RateLimitConfig, or WAFPolicy resource are not validated in any mode, so `entExtAuth.authConfigRef`, `entRateLimit.global.rateLimitConfigRefs`, and `entWAF.wafPolicyRef` can select a resource in another namespace without a ReferenceGrant. Do not rely on `STRICT` mode to isolate these resources between namespaces. If you need to restrict them, use namespace discovery or RBAC instead.
> {{% /downstream %}}

### ReferenceGrant example {#referencegrant-example}

To reference resources across namespaces, create a ReferenceGrant in the namespace of the resource that you want to access, not in the namespace of the resource that makes the reference. The `from` section describes the resource that makes the reference, and the `to` section describes the resource it is allowed to reach. For more information about which resource to reference in each field, see [Reference validation by mode](#referencegrant-modes). 

The following example allows a policy in the `httpbin` namespace to read Secrets in the `team-secrets` namespace.

```yaml
kubectl apply -f- <<EOF
apiVersion: gateway.networking.k8s.io/v1beta1
kind: ReferenceGrant
metadata:
  name: allow-apikey-secrets
  # The namespace that holds the Secrets.
  namespace: team-secrets
spec:
  from:
  - group: gateway.kgateway.dev
    kind: TrafficPolicy
    # The namespace that holds the policy.
    namespace: httpbin
  to:
  - group: ""
    kind: Secret
EOF
```

To restrict the grant to a single Secret, add `name` to the `to` entry. When you omit `name`, every Secret in the namespace is allowed.

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

{{< version exclude-if="2.0.x,2.1.x,2.2.x,2.3.x" >}}

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
