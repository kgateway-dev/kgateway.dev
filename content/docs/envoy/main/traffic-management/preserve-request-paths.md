---
title: Preserve request paths
weight: 20
description: Disable Envoy's default path normalization and slash merging so that backends that depend on the original request path, such as S3-compatible object stores, receive it unmodified.
---
{{< reuse "kgw-docs/pages/traffic-management/preserve-request-paths.md" >}}