1. Follow the [Get started guide](/docs/quickstart/) to install {{< reuse "docs/snippets/product-name.md" >}}, set up a gateway resource, and deploy the httpbin sample app.

2. Get the external address of the gateway and save it in an environment variable.
   {{< tabs items="Cloud Provider LoadBalancer,Port-forward for local testing" >}}
   {{% tab %}}
   ```sh
   export INGRESS_GW_ADDRESS=$(kubectl get svc -n {{< reuse "docs/snippets/ns-system.md" >}} http -o jsonpath="{.status.loadBalancer.ingress[0]['hostname','ip']}")
   echo $INGRESS_GW_ADDRESS  
   ```
   {{% /tab %}}
   {{% tab  %}}
   ```sh
   kubectl port-forward deployment/http -n {{< reuse "docs/snippets/ns-system.md" >}} 8080:8080
   ```
   {{% /tab %}}
   {{< /tabs >}}