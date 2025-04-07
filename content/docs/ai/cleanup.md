---
title: Cleanup
weight: 100
description: Remove the AI Gateway resources that you created as part of the guides. 
---

Remove the AI Gateway resources that you created as part of the guides.

1. Remove the Backend resource for the LLM provider.

   ```sh
   kubectl delete backend openai -n kgateway-system
   ```

1. Delete any LLM provider credentials, model failover, TrafficPolicy, and other AI Gateway resources that you created.

   ```sh
   kubectl delete secret -n kgateway-system openai-secret
   kubectl delete backend,deployment,httproute,service -n kgateway-system -l app=model-failover
   kubectl delete TrafficPolicy -n kgateway-system -l app=ai-kgateway
   ```

1. Remove the AI Gateway.

   ```sh
   kubectl delete gateway ai-gateway -n kgateway-system
   kubectl delete gatewayparameters ai-gateway -n kgateway-system
   ```

1. Disable the AI extension in your kgateway Helm chart.

   {{< callout type="warning" >}}
   If you use a different version or extra Helm settings, update the following command accordingly.
   {{< /callout >}}

   ```shell
   helm upgrade -i -n kgateway-system kgateway oci://cr.kgateway.dev/kgateway-dev/charts/kgateway \
        --set gateway.aiExtension.enabled=false \
        --version v{{< reuse "docs/versions/n-patch.md" >}}
   ```

