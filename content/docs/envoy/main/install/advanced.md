---
title: Advanced settings
weight: 70
description: Install kgateway and related components.
---

{{< reuse "docs/pages/install/advanced.md" >}}

## Common labels

Add custom labels to all resources that are created by the Helm charts, including the Deployment, Service, ServiceAccount, and ClusterRoles. This allows you to better organize your resources or integrate with external tooling. 

The following snippet adds the `label-key` and `kgw-managed` labels to all resources. 

```yaml

commonLabels: 
  label-key: label-value
  kgw-managed: "true"
```

