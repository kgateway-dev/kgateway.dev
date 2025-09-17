---
title: kgwctl get
weight: 20
description: kgwctl get command reference
---

List one or more kgateway resources. 

## Usage

```sh
kgwctl get TYPE [RESOURCE_NAME] [flags]
```

## Command-specific flags

```sh
-A, --all-namespaces    If present, list the requested object(s) across all namespaces. Note that any namespace context that you specified with -n or --namespace is ignored. 
--for string            Only show the resources that match the filter. To filter the results, use the `TYPE[/NAMESPACE]/NAME` format. If no `NAMESPACE` is set, the `default` namespace is automatically assumed. Examples: `gateway/ns2/foo-gateway`, `httproute/bar-httproute`, and `service/ns1/my-svc`.
-h, --help              Help for the command.
-l, --selector string   The selector label to filter on. Supported operations include '=', '==', and '!='. For example, to get all resources with the `key1=value1` and `key2=value2` labels, use `-l key1=value1,key2=value2`. 
-o, --output string     Define the output format. Supported values are wide, json, yaml, and graph.
```

{{< reuse "docs/snippets/kgwctl-global-flags.md" >}}

