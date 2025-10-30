You can update several installation settings in your Helm values file. For example, you can update the namespace, set resource limits and requests, or enable extensions such as for AI.

* **Show all values**: 
      
  ```sh
  helm show values oci://{{< reuse "/docs/snippets/helm-path.md" >}}/charts/{{< reuse "/docs/snippets/helm-kgateway.md" >}} --version {{< reuse "docs/versions/helm-version-upgrade.md" >}}
  ```

* **Get a file with all values**: You can get a `{{< reuse "/docs/snippets/helm-kgateway.md" >}}/values.yaml` file for the upgrade version by pulling and inspecting the Helm chart locally.
      
  ```sh
  helm pull oci://{{< reuse "/docs/snippets/helm-path.md" >}}/charts/{{< reuse "/docs/snippets/helm-kgateway.md" >}} --version {{< reuse "docs/versions/helm-version-upgrade.md" >}}
  tar -xvf {{< reuse "/docs/snippets/helm-kgateway.md" >}}-{{< reuse "docs/versions/helm-version-upgrade.md" >}}.tgz
  open {{< reuse "/docs/snippets/helm-kgateway.md" >}}/values.yaml
  ```

For more information, see the [Helm reference docs]({{< link-hextra path="/reference/helm/" >}}).

{{< version include-if="2.2.x,2.1.x" >}}

## Agentgateway and AI extensions {#agentgateway-ai-extensions}

To enable the [agentgateway]({{< link-hextra path="/agentgateway/" >}}) integration, set the following values in your Helm values file.

```yaml

agentgateway:
  enabled: true
```

{{< /version >}}

## Development builds

When using the development build {{< reuse "docs/versions/patch-dev.md" >}}, add `--set controller.image.pullPolicy=Always` to ensure you get the latest image. For production environments, this setting is not recommended as it might impact performance.

{{< version include-if="2.2.x,2.1.x" >}}

## Leader election

Leader election is enabled by default to ensure that you can run {{< reuse "docs/snippets/kgateway.md" >}} in a multi-control plane replica setup for high availability. 

You can disable leader election by setting the `controller.disableLeaderElection` to `true` in your Helm chart. 

```yaml

controller:
  disableLeaderElection: true
```

{{< /version >}}

## Namespace discovery {#namespace-discovery}

You can limit the namespaces that {{< reuse "/docs/snippets/kgateway.md" >}} watches for gateway configuration. For example, you might have a multi-tenant cluster with different namespaces for different tenants. You can limit {{< reuse "/docs/snippets/kgateway.md" >}} to only watch a specific namespace for gateway configuration.

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

{{< version include-if="2.2.x,2.1.x" >}}

## TLS encryption {#tls-encryption}

You can enable TLS encryption for the xDS gRPC server in the {{< reuse "docs/snippets/kgateway.md" >}} control plane. For more information, see the [TLS encryption]({{< link-hextra path="/install/tls" >}}) docs.

{{< /version >}}
