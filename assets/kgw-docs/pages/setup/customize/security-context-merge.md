### How security context settings merge {#security-context-merge}

When both the GatewayClass and the Gateway reference {{< reuse "kgw-docs/snippets/gatewayparameters.md" >}} resources, the security context settings are merged field by field. The Gateway does not replace the whole block. If the Gateway sets a field, the Gateway value is used. If the Gateway does not set a field, the GatewayClass value is kept. This merge applies to the pod security context in `podTemplate.securityContext` and to container security contexts, such as `envoyContainer.securityContext`.

Nested settings, such as `windowsOptions`, merge the same way. For example, a Gateway can set `windowsOptions.gmsaCredentialSpecName` to name a GMSA credential spec, and the inline `windowsOptions.gmsaCredentialSpec` contents from the GatewayClass are kept.

Consider the following GatewayClass configuration:

```yaml
spec:
  kube:
    podTemplate:
      securityContext:
        runAsUser: 1000
        fsGroup: 3000
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
        windowsOptions:
          gmsaCredentialSpecName: gmsa-webapp
```

The resulting security context merges both configurations as follows:

```yaml
securityContext:
  runAsUser: 2000                                            # Gateway value is used
  fsGroup: 3000                                              # GatewayClass value is kept
  windowsOptions:
    gmsaCredentialSpec: '{"CmsPlugins":["ActiveDirectory"]}' # GatewayClass value is kept
    gmsaCredentialSpecName: gmsa-webapp                      # Gateway value is added
```

For the full order in which built-in fields and overlays are applied, see [Configuration priority and precedence]({{< link-hextra path="/setup/customize/options/#configuration-priority-and-precedence" >}}).
