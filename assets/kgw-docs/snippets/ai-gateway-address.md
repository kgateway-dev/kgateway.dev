Get the external address of the gateway and save it in an environment variable.
   
   {{< tabs >}}
   {{< tab name="Cloud Provider LoadBalancer" >}}
   ```sh
   export INGRESS_GW_ADDRESS=$(kubectl get svc -n {{< reuse "kgw-docs/snippets/namespace.md" >}} ai-gateway -o jsonpath="{.status.loadBalancer.ingress[0]['hostname','ip']}")
   echo $INGRESS_GW_ADDRESS  
   ```
   {{< /tab >}}
   {{< tab name="Port-forward for local testing" >}}
   ```sh
   kubectl port-forward deployment/ai-gateway -n {{< reuse "kgw-docs/snippets/namespace.md" >}} 8080:8080
   ```
   {{< /tab >}}
   {{< /tabs >}}