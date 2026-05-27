---
title: Helm value reference
weight: 20
description: 
---

## Download the Helm chart {#download}

You can download the Helm chart to review the Helm values that are supported. 

1. Download the Helm chart as an archive to your local machine. 
   ```sh
   helm pull oci://cr.kgateway.dev/kgateway-dev/charts/kgateway --version v{{< reuse "docs/versions/n-patch.md" >}}
   ```

2. Extract the files from the downloaded archive. 
   ```sh
   tar -xvf kgateway-v{{< reuse "docs/versions/n-patch.md" >}}.tgz
   ```

3. Open the Helm values file. 
   ```sh
   open kgateway/values.yaml
   ```

## Helm charts

Review the documentation for the following Helm charts.

{{< cards >}}
  {{< card link="kgateway-crds" title="kgateway-crds" >}}
  {{< card link="kgateway" title="kgateway" >}}
{{< /cards >}}
