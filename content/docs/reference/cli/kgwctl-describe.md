---
title: kgwctl describe
weight: 20
description: kgwctl describe command reference
---

Get the details of one or more kgateway resources. 

## Usage
  
```sh
kgwctl describe TYPE [RESOURCE_NAME] [flags]
```

## Command-specific flags

```yaml
-A, --all-namespaces    If present, list the requested object(s) across all namespaces. Namespace in current context is ignored even if specified with --namespace.
-h, --help              Help for the command
-l, --selector string   The selector label to filter on. Supported operations include '=', '==', and '!='. For example, to describe all resources with the `key1=value1` and `key2=value2` labels, use `-l key1=value1,key2=value2`. 
```


{{< reuse "docs/snippets/kgwctl-global-flags.md" >}}