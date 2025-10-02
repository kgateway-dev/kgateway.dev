1. Follow the [Get started guide](/docs/quickstart/) to install kgateway.

2. Follow the [Sample app guide]({{< link-hextra path="/install/sample-app/" >}}) to create a gateway proxy with an HTTP listener and deploy the httpbin sample app.

3. Get the external address of the gateway and save it in an environment variable.
   {{< tabs items="Cloud Provider LoadBalancer,Port-forward for local testing" tabTotal="2"  >}}
   {{% tab tabName="Cloud Provider LoadBalancer" %}}
   ```sh
   export INGRESS_GW_ADDRESS=$(kubectl get svc -n {{< reuse "docs/snippets/namespace.md" >}} http -o jsonpath="{.status.loadBalancer.ingress[0]['hostname','ip']}")
   echo $INGRESS_GW_ADDRESS  
   ```
   {{% /tab %}}
   {{% tab tabName="Port-forward for local testing"  %}}
   ```sh
   kubectl port-forward deployment/http -n {{< reuse "docs/snippets/namespace.md" >}} 8080:8080
   ```
   {{% /tab %}}
   {{< /tabs >}}

4. **Important**: Install the standard channel of version 1.3 of the Kubernetes Gateway API to use this feature.

   ```shell
   kubectl apply -f https://github.com/kubernetes-sigs/gateway-api/releases/download/v1.3.0/standard-install.yaml
   ```