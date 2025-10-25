## Cleanup

{{< reuse "docs/snippets/cleanup.md" >}}

1. Delete the {{< reuse "/docs/snippets/trafficpolicy.md" >}} resources.
   ```sh
   kubectl delete {{< reuse "/docs/snippets/trafficpolicy.md" >}} transformation-buffer-body -n httpbin 
   {{< version include-if="2.2.x,2.1.x" >}}
   kubectl delete {{< reuse "/docs/snippets/trafficpolicy.md" >}} transformation-buffer-limit -n httpbin {{< /version >}}
   ```

2. Remove the buffer limit annotation from the http Gateway resource.
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