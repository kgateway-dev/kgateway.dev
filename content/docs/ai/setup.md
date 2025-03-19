---
title: Set up AI Gateway 
weight: 10
description: Use a custom GatewayParameters resource to set up AI Gateway. 
---

Configure your Helm chart installation to use AI Gateway. Then, use a custom GatewayParameters resource to set up AI Gateway.

## Before you begin

[Get started](/docs/quickstart/) to install the {{< reuse "docs/snippets/k8s-gateway-api-name.md">}} CRDs and {{< reuse "docs/snippets/product-name.md" >}}.

## Enable the AI extension {#ai-extension}

Configure your {{< reuse "docs/snippets/product-name.md" >}} Helm chart installation to use AI Gateway.

1. [Upgrade](/docs/operations/upgrade/) {{< reuse "docs/snippets/product-name.md" >}} with the AI Gateway extension enabled.

   {{< callout type="warning" >}}
   If you use a different version or extra Helm settings, update the following command accordingly.
   {{< /callout >}}

   ```shell
   helm upgrade -i -n {{< reuse "docs/snippets/ns-system.md" >}} kgateway oci://cr.kgateway.dev/kgateway-dev/charts/kgateway \
        --set gateway.aiExtension.enabled=true \
        --version v{{< reuse "docs/versions/n-patch.md" >}}
   ```

2. Verify that your Helm installation is updated.

   ```shell
   helm get values kgateway -n kgateway-system -o yaml
   ```

   Example output:
   
   ```yaml
   gateway:
     aiExtension:
       enabled: true
   ```

## Create an AI Gateway {#gateway}

1. Create a GatewayParameters resource which enables an AI extension for the Gateway.
   
   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.kgateway.dev/v1alpha1
   kind: GatewayParameters
   metadata:
     name: ai-gateway
     namespace: kgateway-system
     labels:
       app.kubernetes.io/name: ai-gateway
   spec:
     kube:
       aiExtension:
         enabled: true
         ports:
         - name: ai-monitoring
           containerPort: 9092
       service:
         type: ClusterIP
   EOF
   ```

2. Create a Gateway that uses the default {{< reuse "docs/snippets/product-name.md" >}} GatewayClass and the AI-enabled GatewayParameters resource you created in the previous step.
   
   ```yaml
   kubectl apply -f- <<EOF
   kind: Gateway
   apiVersion: gateway.networking.k8s.io/v1
   metadata:
     name: ai-gateway
     namespace: {{< reuse "docs/snippets/ns-system.md" >}}
     labels:
       app.kubernetes.io/name: ai-gateway
   spec:
     gatewayClassName: kgateway
     infrastructure:
       parametersRef:
         name: ai-gateway
         group: gateway.kgateway.dev
         kind: GatewayParameters
     listeners:
     - protocol: HTTP
       port: 8080
       name: http
       allowedRoutes:
         namespaces:
           from: All
   EOF
   ```

3. Verify that the AI Gateway is created. 

   * Gateway: Note that it might take a few minutes for an address to be assigned.
   * Deployment: The pod has two containers: `kgateway-proxy` and `kgateway-ai-extension`. 

   ```sh
   kubectl get gateway,pods -l app.kubernetes.io/name=ai-gateway -A
   ```
   
   Example output: 
   ```
   NAMESPACE         NAME                                           CLASS      ADDRESS       PROGRAMMED   AGE
   kgateway-system   gateway.gateway.networking.k8s.io/ai-gateway   kgateway   xx.xx.xx.xx   True         13s
   
   NAMESPACE         NAME                              READY   STATUS             RESTARTS   AGE
   kgateway-system   pod/ai-gateway-6f4786fcb6-gqhlm   2/2     Running   0          13s
   ```

   If you see an error, check the logs of the `kgateway-ai-extension` container.

   ```sh
   kubectl logs -l app.kubernetes.io/name=ai-gateway -n kgateway-system -c kgateway-ai-extension
   ```

## Next

Explore how to [connect the gateway to an LLM provider and successfully authenticate](/docs/ai/auth/) so that you can use AI services.
