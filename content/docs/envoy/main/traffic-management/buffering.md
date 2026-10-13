---
title: Buffering
description: Buffer request and response bodies so that filters can inspect and transform them safely.
weight: 20
next: /docs/traffic-management/header-control
prev: /docs/traffic-management/route-delegation
---

{{< reuse "kgw-docs/pages/traffic-management/buffering2.2-body.md" >}}

## Move the buffer filter before body-reading filters

{{< reuse "kgw-docs/snippets/buffering-filter-stage.md" >}}

{{< reuse "kgw-docs/snippets/buffering-filter-stage-cleanup.md" >}}
