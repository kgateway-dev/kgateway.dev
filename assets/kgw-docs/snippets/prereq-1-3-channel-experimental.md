1. Follow the [Get started guide]({{< link-hextra path="/quickstart/" >}}) to install kgateway.

2. Follow the [Sample app guide]({{< link-hextra path="/install/sample-app/" >}}) to create a gateway proxy with an HTTP listener and deploy the httpbin sample app.

3. Get the external address of the gateway and save it in an environment variable.
   {{< tabs >}}
   {{% tab name="Cloud Provider LoadBalancer" %}}
   ```sh
   export INGRESS_GW_ADDRESS=$(kubectl get svc -n {{< reuse "kgw-docs/snippets/namespace.md" >}} http -o jsonpath="{.status.loadBalancer.ingress[0]['hostname','ip']}")
   echo $INGRESS_GW_ADDRESS  
   ```
   {{% /tab %}}
   {{% tab name="Port-forward for local testing" %}}
   ```sh
   kubectl port-forward deployment/http -n {{< reuse "kgw-docs/snippets/namespace.md" >}} 8080:8080
   ```
   {{% /tab %}}
   {{< /tabs >}}

4. **Important**: Install the experimental channel of version 1.3 of the Kubernetes Gateway API to use this feature.
   ```shell
   kubectl apply -f https://github.com/kubernetes-sigs/gateway-api/releases/download/v1.3.0/experimental-install.yaml
   ```{{< version include-if="2.2.x,2.3.x,2.4.x" >}}

5. In kgateway version 2.2 and later, experimental Gateway API features are enabled by default. The `KGW_ENABLE_EXPERIMENTAL_GATEWAY_API_FEATURES` environment variable on the kgateway controller deployment defaults to `true`, so no additional configuration is required. To disable these features, set the variable to `false` in your Helm values and upgrade your installation.

   ```yaml
   controller:
     extraEnv:
       KGW_ENABLE_EXPERIMENTAL_GATEWAY_API_FEATURES: "false"
   ```{{< /version >}}