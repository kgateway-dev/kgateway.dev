---
title: Set up AI Gateway 
weight: 10
description: Use a custom GatewayParameters resource to set up AI Gateway. 
---

{{< reuse "docs/snippets/ai-deprecation-note.md" >}}

Configure your Helm chart installation to use AI Gateway. Then, use a custom GatewayParameters resource to set up AI Gateway.

## Before you begin

[Get started](/docs/quickstart/) to install the {{< reuse "docs/snippets/k8s-gateway-api-name.md">}} CRDs and {{< reuse "/docs/snippets/kgateway.md" >}}.

## Enable the AI extension {#ai-extension}

Configure your {{< reuse "/docs/snippets/kgateway.md" >}} Helm chart installation to use AI Gateway.

1. [Upgrade](/docs/envoy/main/operations/upgrade/) {{< reuse "/docs/snippets/kgateway.md" >}} with the AI Gateway extension enabled. **Note**: To use AI Gateway with [agentgateway](../../agentgateway/main/), see the [agentgateway docs]({{< link-hextra path="/agentgateway" >}}).

   {{< callout type="warning" >}}
   If you use a different version or extra Helm settings such as in a `-f values.yaml` file, update the following command accordingly.
   {{< /callout >}}

   ```shell
   helm upgrade -i -n {{< reuse "docs/snippets/namespace.md" >}} {{< reuse "/docs/snippets/helm-kgateway.md" >}} oci://{{< reuse "/docs/snippets/helm-path.md" >}}/charts/{{< reuse "/docs/snippets/helm-kgateway.md" >}} \
        --set gateway.aiExtension.enabled=true \
        --version {{< reuse "docs/versions/helm-version-upgrade.md" >}}
   ```

2. Verify that your Helm installation is updated.

   ```shell
   helm get values {{< reuse "/docs/snippets/helm-kgateway.md" >}} -n {{< reuse "docs/snippets/namespace.md" >}} -o yaml
   ```

   Example output:
   ```yaml
   gateway:
     aiExtension:
       enabled: true
   ```
  
## Create an AI Gateway {#gateway}

1. Create a GatewayParameters resource which enables an AI extension for the Gateway.
   
   {{< tabs tabTotal="2" items="Cloud Provider,Local Environment" >}}
   {{% tab tabName="Cloud Provider" %}}
   For AI services in a cloud provider, use a LoadBalancer service. This way, the AI Gateway can be accessed from outside the cluster.
   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.kgateway.dev/v1alpha1
   kind: GatewayParameters
   metadata:
     name: ai-gateway
     namespace: {{< reuse "docs/snippets/namespace.md" >}}
     labels:
       app: ai-gateway
   spec:
     kube:
       aiExtension:
         enabled: true
         ports:
         - name: ai-monitoring
           containerPort: 9092
         image:
           registry: cr.kgateway.dev/kgateway-dev
           repository: kgateway-ai-extension
           tag: v2.1.0-main
       service:
         type: LoadBalancer
   EOF
   ```
   {{% /tab %}}
   {{% tab tabName="Local Environment" %}}
   For local environments such as Ollama, use a NodePort service. This way, the AI Gateway can be accessed locally.
   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.kgateway.dev/v1alpha1
   kind: GatewayParameters
   metadata:
     name: ai-gateway
     namespace: {{< reuse "docs/snippets/namespace.md" >}}
     labels:
       app: ai-gateway
   spec:
     kube:
       aiExtension:
         enabled: true
         ports:
         - name: ai-monitoring
           containerPort: 9092
         image:
           registry: cr.kgateway.dev/kgateway-dev
           repository: kgateway-ai-extension
           tag: v2.1.0-main
       service:
         type: NodePort
   EOF
   ```
   {{% /tab %}}
   {{< /tabs >}}

2. Create a Gateway that uses the default GatewayClass and the AI-enabled GatewayParameters resource you created in the previous step. {{< reuse "docs/snippets/agw-gatewayclass-choice.md" >}}

   ```yaml
   kubectl apply -f- <<EOF
   kind: Gateway
   apiVersion: gateway.networking.k8s.io/v1
   metadata:
     name: ai-gateway
     namespace: {{< reuse "docs/snippets/namespace.md" >}}
     labels:
       app: ai-gateway
   spec:
     gatewayClassName: {{< reuse "/docs/snippets/gatewayclass.md" >}}
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
   * Pod for `kgateway` proxy: The pod has two containers: `kgateway-proxy` and `kgateway-ai-extension`. 

   ```sh
   kubectl get gateway,pods -l app.kubernetes.io/name=ai-gateway -A
   ```
   
   Example output: 
   ```
   NAMESPACE         NAME                                           CLASS      ADDRESS       PROGRAMMED   AGE
   {{< reuse "docs/snippets/namespace.md" >}}   gateway.gateway.networking.k8s.io/ai-gateway   kgateway   xx.xx.xx.xx   True         13s
   
   NAMESPACE         NAME                              READY   STATUS             RESTARTS   AGE
   {{< reuse "docs/snippets/namespace.md" >}}   pod/ai-gateway-6f4786fcb6-gqhlm   2/2     Running   0          13s
   ```

   If you see an error, check the logs of the `kgateway-ai-extension` container.

   ```sh
   kubectl logs -l app.kubernetes.io/app=ai-gateway -n {{< reuse "docs/snippets/namespace.md" >}} -c kgateway-ai-extension
   ```

## Next

* For OpenAI: Continue with the [Authenticate to the LLM](../auth/) guide.
* For other cloud LLM providers such as Gemini: [Review the Cloud LLM providers guide](../cloud-providers/) for provider-specific setup examples.
* For local LLM providers such as Ollama: [Set up Ollama as a local LLM provider](../ollama/).
