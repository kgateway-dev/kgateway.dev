1. Create a Gateway that uses the `{{< reuse "docs/snippets/agw-gatewayclass.md" >}}` GatewayClass. The following example sets up a Gateway that uses the [default agentgateway proxy template](https://github.com/kgateway-dev/kgateway/blob/main/internal/kgateway/helm/agentgateway/templates/deployment.yaml). 
   ```yaml
   kubectl apply -f- <<EOF
   kind: Gateway
   apiVersion: gateway.networking.k8s.io/v1
   metadata:
     name: agentgateway
     namespace: {{< reuse "docs/snippets/namespace.md" >}}
     labels:
       app: agentgateway
   spec:
     gatewayClassName: {{< reuse "docs/snippets/agw-gatewayclass.md" >}}
     listeners:
     - protocol: HTTP
       port: 8080
       name: http
       allowedRoutes:
         namespaces:
           from: All
   EOF
   ```
   
2. Verify that the agentgateway proxy is created. 

   * Gateway: Note that it might take a few minutes for an address to be assigned.
   * Pod for `agentgateway` proxy: The pod has one container: `agent-gateway`.

   ```sh
   kubectl get gateway agentgateway -n {{< reuse "docs/snippets/namespace.md" >}}
   kubectl get deployment agentgateway -n {{< reuse "docs/snippets/namespace.md" >}}
   ```
   
   Example output: 
   ```
   NAME           CLASS          ADDRESS                                                                  PROGRAMMED   AGE
   agentgateway   {{< reuse "docs/snippets/agw-gatewayclass.md" >}}   a1cff4bd974a34d8b882b2fa01d357f0-119963959.us-east-2.elb.amazonaws.com   True         6m9s
   NAME           READY   UP-TO-DATE   AVAILABLE   AGE
   agentgateway   1/1     1            1           6m11s
   ```

3. Get the external address of the agentgateway proxy and save it in an environment variable.
   {{< tabs tabTotal="2" items="Cloud Provider LoadBalancer,Port-forward for local testing" >}}
   {{% tab tabName="Cloud Provider LoadBalancer" %}}
   ```sh
   export INGRESS_GW_ADDRESS=$(kubectl get svc -n {{< reuse "docs/snippets/namespace.md" >}} agentgateway -o jsonpath="{.status.loadBalancer.ingress[0]['hostname','ip']}")
   echo $INGRESS_GW_ADDRESS  
   ```
   {{% /tab %}}
   {{% tab tabName="Port-forward for local testing" %}}
   ```sh
   kubectl port-forward deployment/agentgateway -n {{< reuse "docs/snippets/namespace.md" >}} 8080:8080
   ```
   {{% /tab %}}
   {{< /tabs >}}