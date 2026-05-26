---
title: "CLI"
weight: 10
---
This page focuses on the commands you’ll use most often.

## `print`

Translates input manifests and prints generated resources.

Typical usage:

```bash
ingress2gateway print   --providers=ingress-nginx   --emitter=kgateway   --input-file ./ingress.yaml
```

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
