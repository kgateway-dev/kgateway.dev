---
title: "glooctl check"
weight: 5
---

Reference docs for the `{{< reuse "docs/snippets/cli-name.md" >}} check` command.

## glooctl check

Checks {{< reuse "docs/snippets/product-name.md" >}} resources for errors.

### Synopsis

usage: {{< reuse "docs/snippets/cli-name.md" >}} check [-o FORMAT]

```
{{< reuse "docs/snippets/cli-name.md" >}} check [flags]
```

### Options

```
  -x, --exclude strings                   check to exclude: (deployments, pods, backends, backendgroup, auth-configs, rate-limit-configs, virtual-host-options, route-options, secrets, virtual-services, gateways, proxies, xds-metrics, kube-gateway-classes, kube-gateways, kube-http-routes)
  -h, --help                              help for check
  -n, --namespace string                  namespace for reading or writing resources (default "{{< reuse "docs/snippets/ns-system.md" >}}")
  -o, --output OutputType                 output format: (json, table) (default table)
  -p, --pod-selector string               Label selector for pod scanning (default "gloo")
      --read-only                         only do checks that dont require creating resources (i.e. port forwards)
  -r, --resource-namespaces stringArray   Namespaces in which to scan {{< reuse "docs/snippets/product-name.md" >}} custom resources. If not provided, all watched namespaces (as specified in settings) will be scanned.
```

### Options inherited from parent commands

```
  -c, --config string              set the path to the {{< reuse "docs/snippets/cli-name.md" >}} config file (default "<home_directory>/.gloo/glooctl-config.yaml")
  -i, --interactive                use interactive mode
      --kube-context string        kube context to use when interacting with kubernetes
      --kubeconfig string          kubeconfig to use, if not standard one
```



