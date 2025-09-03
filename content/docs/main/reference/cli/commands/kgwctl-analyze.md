---
title: kgwctl analyze
weight: 20
description: kgwctl analyze command reference
---

Analyze kgateway resource manifests by file names or directory to find configuration issues and impacts on other resources. 

## Usage

```sh
kgwctl analyze -f FILENAME|DIRECTORY [flags]
```

## Command-specific flags

```yaml
-f, --filename strings   The file name or directory that contains the kgateway manifests that you want to analyze.
-h, --help               Help for the command.
-R, --recursive          Process the directory that you reference in -f or --filename recursively. This option is useful for when you want to analyze related manifests that are stored in the same directory. (default true)
```

{{< reuse "docs/snippets/kgwctl-global-flags.md" >}}
