Get the external address of the gateway and save it in an environment variable.
   
   {{< tabs items="Cloud Provider LoadBalancer,Port-forward for local testing" >}}
   {{< tab >}}
   ```sh
   export INGRESS_GW_ADDRESS=$(kubectl get svc -n {{< reuse "docs/snippets/ns-system.md" >}} ai-gateway -o jsonpath="{.status.loadBalancer.ingress[0]['hostname','ip']}")
   echo $INGRESS_GW_ADDRESS  
   ```
   {{< /tab >}}
   {{< tab >}}
   ```sh
   kubectl port-forward deployment/ai-gateway -n {{< reuse "docs/snippets/ns-system.md" >}} 8080:8080
   ```
   {{< /tab >}}
   {{< /tabs >}}