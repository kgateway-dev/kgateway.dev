1. Follow the [Get started guide](/docs/quickstart/) to install {{< reuse "docs/snippets/product-name.md" >}}, if it's not already installed.

2. Create a Gateway resource and configure an HTTP listener. The following Gateway can serve HTTPRoute resources from all namespaces.

   ```yaml
   kubectl apply -f- <<EOF
   kind: Gateway
   apiVersion: gateway.networking.k8s.io/v1
   metadata:
     name: http
     namespace: {{< reuse "docs/snippets/ns-system.md" >}}
   spec:
     gatewayClassName: kgateway
     listeners:
     - protocol: HTTP
       port: 8080
       name: http
       allowedRoutes:
         namespaces:
           from: All
   EOF
   ```

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

4. Create the namespaces for `team1` and `team2`.
   ```sh
   kubectl create namespace team1
   kubectl create namespace team2
   ```

5. Deploy the httpbin app into both namespaces.
   ```sh
   kubectl -n team1 apply -f https://raw.githubusercontent.com/kgateway-dev/kgateway.dev/main/assets/docs/examples/httpbin.yaml
   kubectl -n team2 apply -f https://raw.githubusercontent.com/kgateway-dev/kgateway.dev/main/assets/docs/examples/httpbin.yaml
   ```

6. Verify that the httpbin apps are up and running.
   ```sh
   kubectl get pods -n team1
   kubectl get pods -n team2
   ```
   
   Example output: 
   ```
   NAME                      READY   STATUS    RESTARTS   AGE
   httpbin-f46cc8b9b-bzl9z   3/3     Running   0          7s
   NAME                      READY   STATUS    RESTARTS   AGE
   httpbin-f46cc8b9b-nhtmg   3/3     Running   0          6s
   ```