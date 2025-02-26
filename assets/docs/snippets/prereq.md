1. Follow the [Get started guide](/docs/quickstart/) to install {{< reuse "docs/snippets/product-name.md" >}}.

2. Follow the [Sample app guide](/docs/operations/sample-app/) to create an API gateway proxy with an HTTP listener and deploy the httpbin sample app.

3. Get the external address of the gateway and save it in an environment variable.
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