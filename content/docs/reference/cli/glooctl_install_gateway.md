---
title: "glooctl install gateway"
weight: 5
---

Reference docs for the `{{< reuse "docs/snippets/cli-name.md" >}} install gateway` command.

## glooctl install gateway

Install {{< reuse "docs/snippets/product-name.md" >}} on Kubernetes.

### Synopsis

requires kubectl to be installed

```
{{< reuse "docs/snippets/cli-name.md" >}} install gateway [flags]
```

### Options

```
      --create-namespace      Create the namespace to install {{< reuse "docs/snippets/product-name.md" >}} into (default true)
  -d, --dry-run               Dump the raw installation yaml instead of applying it to kubernetes
  -f, --file string           Install {{< reuse "docs/snippets/product-name.md" >}} from this Helm chart archive file rather than from a release
  -h, --help                  help for gateway
  -n, --namespace string      namespace to install {{< reuse "docs/snippets/product-name.md" >}} into (default "{{< reuse "docs/snippets/ns-system.md" >}}")
      --release-name string   helm release name (default "gloo")
      --values strings        List of files with value overrides for the {{< reuse "docs/snippets/product-name.md" >}}  Helm chart, (e.g. --values file1,file2 or --values file1 --values file2)
      --version string        version to install (e.g. 1.4.0, defaults to latest)
```

### Options inherited from parent commands

```
  -c, --config string              set the path to the {{< reuse "docs/snippets/cli-name.md" >}} config file (default "<home_directory>/.gloo/glooctl-config.yaml")
  -i, --interactive                use interactive mode
      --kube-context string        kube context to use when interacting with kubernetes
      --kubeconfig string          kubeconfig to use, if not standard one
  -v, --verbose                    If true, output from kubectl commands will print to stdout/stderr
```

