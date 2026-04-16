---
title: "CLI"
weight: 10
---
This page focuses on the commands you’ll use most often.

## `print`

Translates Ingress resources and prints the generated Gateway API and kgateway resources.

If you do not specify `--input-file`, the command reads from the cluster using your current kubeconfig context.

Typical usage:

```bash
ingress2gateway print \
  --providers=ingress-nginx \
  --emitter=kgateway \
  --input-file ./ingress.yaml
```

Common flags:

| Flag | Description |
| --- | --- |
| `--providers=ingress-nginx` | Select the Ingress NGINX provider. |
| `--emitter=kgateway` | Emit Gateway API and kgateway-specific resources. |
| `--input-file ./ingress.yaml` | Read manifests from a file instead of the cluster. Repeat the flag to include multiple files. |
| `-n`, `--namespace` | Restrict cluster reads to a namespace. |
| `-A`, `--all-namespaces` | Read matching resources across all namespaces. |
| `-o`, `--output` | Set the output format to `yaml`, `json`, or `kyaml`. |
| `--allow-experimental-gw-api` | Include experimental Gateway API fields in the generated output. |
| `--no-color` | Disable ANSI color codes in CLI output. |
| `--ingress-nginx-ingress-class=internal-nginx` | Select a custom Ingress NGINX class. Defaults to `nginx`. |

## `version`

Prints version information.

```bash
ingress2gateway version
```

## Help

For the complete flag reference for your build:

```bash
ingress2gateway --help
ingress2gateway print --help
```
