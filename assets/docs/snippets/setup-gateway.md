Create an API gateway with an HTTP listener by using the {{< reuse "docs/snippets/k8s-gateway-api-name.md" >}}.

1. Create a Gateway resource and configure an HTTP listener. The following Gateway can serve HTTPRoute resources from all namespaces.
   
   ```yaml
   kubectl apply -f- <<EOF
   kind: Gateway
   apiVersion: gateway.networking.k8s.io/v1
   metadata:
     name: http
     namespace: {{< reuse "docs/snippets/namespace.md" >}}
   spec:
     gatewayClassName: {{< reuse "/docs/snippets/gatewayclass.md" >}}
     listeners:
     - protocol: HTTP
       port: 8080
       name: http
       allowedRoutes:
         namespaces:
           from: All
   EOF
   ```

2. Verify that the Gateway is created successfully. You can also review the external address that is assigned to the Gateway. Note that depending on your environment it might take a few minutes for the load balancer service to be assigned an external address. If you are using a local Kind cluster without a load balancer such as `metallb`, you might not have an external address.
   
   ```sh
   kubectl get gateway http -n {{< reuse "docs/snippets/namespace.md" >}}
   ```

   Example output: 
   
   ```txt
   NAME   CLASS      ADDRESS                                  PROGRAMMED   AGE
   http   {{< reuse "/docs/snippets/gatewayclass.md" >}}   1234567890.us-east-2.elb.amazonaws.com   True         93s
   ```

3. Verify that the gateway proxy pod is running.

   ```sh
   kubectl get po -n {{< reuse "docs/snippets/namespace.md" >}} -l gateway.networking.k8s.io/gateway-name=http
   ```

   Example output:
   
   ```txt
   NAME                  READY   STATUS    RESTARTS   AGE
   http-7dd94b74-k26j6   1/1     Running   0          18s
   ```

   {{< callout type="info" >}}
   Using Kind and getting a `CrashLoopBackOff` error with a `Failed to create temporary file` message in the logs? You might have a multi-arch platform issue on macOS. In your Docker Desktop settings, uncheck **Use Rosetta**, restart Docker, re-create your Kind cluster, and try again.
   {{< /callout >}}