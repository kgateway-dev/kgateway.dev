### How security context settings merge {#security-context-merge}

When both the GatewayClass and the Gateway reference {{< reuse "kgw-docs/snippets/gatewayparameters.md" >}} resources, the security context settings are merged field by field. The Gateway does not replace the whole block. This merge applies to the pod security context in `podTemplate.securityContext` and to container security contexts, such as `envoyContainer.securityContext`. The following general merging rules apply: 

* If the Gateway sets a field, the Gateway value is used.
* If the Gateway does not set a field, the GatewayClass value is kept.

Lists are merged differently:

* **`supplementalGroups`, `capabilities.add`, and `capabilities.drop`**: The Gateway entries are appended to the GatewayClass entries.
* **`sysctls`**: Entries are merged by name. A Gateway sysctl replaces the GatewayClass `sysctl` with the same name. If the names are different, both `sysctl` values are kept.
* **Empty lists**: For all of these lists, a Gateway list that is set to empty (`[]`) clears the GatewayClass entries. A list that the Gateway does not set keeps them.

Nested settings, such as `windowsOptions`, also merge field by field. For example, a Gateway can set `windowsOptions.gmsaCredentialSpecName` to name a GMSA credential spec, and the inline `windowsOptions.gmsaCredentialSpec` contents from the GatewayClass are kept.

Consider the following GatewayClass configuration:

```yaml
spec:
  kube:
    podTemplate:
      securityContext:
        runAsUser: 1000
        fsGroup: 3000
        supplementalGroups:
          - 2000
        sysctls:
          - name: net.core.somaxconn
            value: "1024"
        windowsOptions:
          gmsaCredentialSpec: '{"CmsPlugins":["ActiveDirectory"]}'
```

Consider the following Gateway configuration:

```yaml
spec:
  kube:
    podTemplate:
      securityContext:
        runAsUser: 2000
        supplementalGroups:
          - 4000
        sysctls:
          - name: net.core.somaxconn
            value: "2048"
          - name: net.ipv4.ip_unprivileged_port_start
            value: "0"
        windowsOptions:
          gmsaCredentialSpecName: gmsa-webapp
```

The resulting security context merges both configurations as follows:

```yaml
securityContext:
  runAsUser: 2000                      # Gateway value is used
  fsGroup: 3000                        # GatewayClass value is kept
  supplementalGroups:                  # Gateway entries are appended
    - 2000
    - 4000
  sysctls:
    - name: net.core.somaxconn         # Gateway value replaces the same name
      value: "2048"
    - name: net.ipv4.ip_unprivileged_port_start  # New name is added
      value: "0"
  windowsOptions:
    gmsaCredentialSpec: '{"CmsPlugins":["ActiveDirectory"]}' # GatewayClass value is kept
    gmsaCredentialSpecName: gmsa-webapp                      # Gateway value is added
```

For the full order in which built-in fields and overlays are applied, see [Configuration priority and precedence]({{< link-hextra path="/setup/customize/options/#configuration-priority-and-precedence" >}}).
