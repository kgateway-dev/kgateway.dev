---
title: Cleanup
weight: 100
description: Remove the AI Gateway resources that you created as part of the guides. 
---

{{< reuse "docs/snippets/ai-deprecation-note.md" >}}

Remove the AI Gateway resources that you created as part of the guides.

1. Remove the Backend resource for the LLM provider.

   ```sh
   kubectl delete backend openai -n {{< reuse "docs/snippets/namespace.md" >}}
   ```

1. Delete any LLM provider credentials, model failover, TrafficPolicy, and other AI Gateway resources that you created.

   ```sh
   kubectl delete secret -n {{< reuse "docs/snippets/namespace.md" >}} openai-secret
   kubectl delete backend,deployment,httproute,service -n {{< reuse "docs/snippets/namespace.md" >}} -l app=model-failover
   kubectl delete TrafficPolicy -n {{< reuse "docs/snippets/namespace.md" >}} -l app=ai-gateway
   ```

1. Remove the AI Gateway.

   ```sh
   kubectl delete gateway ai-gateway -n {{< reuse "docs/snippets/namespace.md" >}}
   kubectl delete gatewayparameters ai-gateway -n {{< reuse "docs/snippets/namespace.md" >}}
   ```

1. Disable the AI extension in your kgateway Helm chart.

   {{< callout type="warning" >}}
   If you use a different version or extra Helm settings such as in a `-f values.yaml` file, update the following command accordingly.
   {{< /callout >}}

   ```shell
   helm upgrade -i -n {{< reuse "docs/snippets/namespace.md" >}} {{< reuse "/docs/snippets/helm-kgateway.md" >}} oci://{{< reuse "/docs/snippets/helm-path.md" >}}/charts/{{< reuse "/docs/snippets/helm-kgateway.md" >}} \
     --set gateway.aiExtension.enabled=false \
     --version {{< reuse "docs/versions/helm-version-upgrade.md" >}}
   ```
 