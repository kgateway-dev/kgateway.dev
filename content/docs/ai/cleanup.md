---
title: Cleanup
weight: 90
description: Remove the AI Gateway resources that you created as part of the guides. 
---

Remove the AI Gateway resources that you created as part of the guides.

1. Remove the Backend resource for the LLM provider.

   ```sh
   kubectl delete backend openai -n {{< reuse "docs/snippets/ns-system.md" >}}
   ```

1. Remove the AI Gateway.

   ```sh
   kubectl delete gateway ai-gateway -n {{< reuse "docs/snippets/ns-system.md" >}}
   kubectl delete gatewayparameters ai-gateway -n {{< reuse "docs/snippets/ns-system.md" >}}
   ```

1. Disable the AI extension in your {{< reuse "docs/snippets/product-name.md" >}} Helm chart.

   {{< callout type="warning" >}}
   If you use a different version or extra Helm settings, update the following command accordingly.
   {{< /callout >}}

   ```shell
   helm upgrade -i -n {{< reuse "docs/snippets/ns-system.md" >}} kgateway oci://cr.kgateway.dev/kgateway-dev/charts/kgateway \
        --set gateway.aiExtension.enabled=false \
        --version v{{< reuse "docs/versions/n-patch.md" >}}
   ```

