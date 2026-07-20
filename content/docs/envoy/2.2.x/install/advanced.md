---
title: Advanced settings
weight: 70
description: Install kgateway and related components.
---

{{< reuse "kgw-docs/pages/install/advanced.md" >}}

## xDS first-connect grace period

By default, the control plane waits 1 second after a new proxy connects before sending its first xDS snapshot. This gives per-client translation time to converge and prevents newly started gateway pods from receiving incomplete configuration after a controller restart.

You can adjust the grace period by using the `KGW_XDS_FIRST_CONNECT_DELAY` environment variable on the controller. The value is a Go duration string, for example `2s`. Set it to `0` to disable the grace period entirely.

```yaml
controller:
  extraEnv:
    KGW_XDS_FIRST_CONNECT_DELAY: "2s"
```

