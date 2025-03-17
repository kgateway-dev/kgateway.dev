---
title: HTTP listeners
weight: 10
---

Create an HTTP listener on your API gateway. Then, your API gateway listens for HTTP traffic on the specified port and hostname that you configure. This gateway can be used as the main ingress for the apps in your cluster. You can also create multiple gateways to listen for traffic on different ports and hostnames. 

Next, you set up an HTTPRoute resource to route requests through the gateway to backing services in your cluster. HTTPRoutes can refer to any gateway independent of the namespace they are in.

1. Create a gateway resource with an HTTP listener. 
   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.networking.k8s.io/v1
   kind: Gateway
   metadata:
     name: my-http-gateway
     namespace: {{< reuse "docs/snippets/ns-system.md" >}}
     labels:
       example: httpbin-mydomain
   spec:
     gatewayClassName: kgateway
     listeners:
     - protocol: HTTP
       port: 8080
       hostname: mydomain.com
       name: http
       allowedRoutes:
         namespaces:
           from: All
   EOF
   ```

   |Setting|Description|
   |--|--|
   |`spec.gatewayClassName`|The name of the Kubernetes gateway class that you want to use to configure the gateway. When you set up {{< reuse "docs/snippets/product-name.md" >}}, a default gateway class is set up for you.  |
   |`spec.listeners`|Configure the listeners for this gateway. In this example, you configure an HTTP gateway that listens for incoming traffic for the `mydomain.com` domain on port 8080. The gateway can serve HTTP routes from any namespace. |

2. Check the status of the gateway to make sure that your configuration is accepted. Note that in the output, a `NoConflicts` status of `False` indicates that the gateway is accepted and does not conflict with other gateway configuration. 
   ```sh
   kubectl get gateway my-http-gateway -n {{< reuse "docs/snippets/ns-system.md" >}} -o yaml
   ```

3. Create an HTTPRoute resource for the httpbin app that is served by the gateway that you created.
   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.networking.k8s.io/v1
   kind: HTTPRoute
   metadata:
     name: httpbin-mydomain
     namespace: httpbin
     labels:
       example: httpbin-mydomain
   spec:
     parentRefs:
       - name: my-http-gateway
         namespace: {{< reuse "docs/snippets/ns-system.md" >}}
     rules:
       - backendRefs:
           - name: httpbin
             port: 8000
   EOF
   ```

4. Verify that the HTTPRoute is applied successfully. 
   ```sh
   kubectl get httproute/httpbin-mydomain -n httpbin -o yaml
   ```

5. Get the external address of the gateway and save it in an environment variable.
   {{< tabs items="Cloud Provider LoadBalancer,Port-forward for local testing" >}}
   {{% tab %}}
   ```sh
   export INGRESS_GW_ADDRESS=$(kubectl get svc -n {{< reuse "docs/snippets/ns-system.md" >}} my-http-gateway -o jsonpath="{.status.loadBalancer.ingress[0]['hostname','ip']}")
   echo $INGRESS_GW_ADDRESS   
   ```
   {{% /tab %}}
   {{% tab %}}
   ```sh
   kubectl port-forward deployment/my-http-gateway -n {{< reuse "docs/snippets/ns-system.md" >}} 8080:8080
   ```
   {{% /tab %}}
   {{< /tabs >}}

6. Send a request to the httpbin app and verify that you get back a 200 HTTP response code. 
   {{< tabs items="Cloud Provider LoadBalancer,Port-forward for local testing" >}}
   {{% tab %}}
   ```sh
   curl -vik http://$INGRESS_GW_ADDRESS:8080/status/200 -H "host: mydomain.com:8080" 
   ```
   {{% /tab %}}
   {{% tab %}}
   ```sh
   curl -vik localhost:8080/status/200 -H "host: mydomain.com"
   ```
   {{% /tab %}}
   {{< /tabs >}}
   

   Example output: 
   ```console
   * Mark bundle as not supporting multiuse
   < HTTP/1.1 200 OK
   HTTP/1.1 200 OK
   < access-control-allow-credentials: true
   access-control-allow-credentials: true
   < access-control-allow-origin: *
   access-control-allow-origin: *
   < date: Fri, 03 Nov 2023 20:02:48 GMT
   date: Fri, 03 Nov 2023 20:02:48 GMT
   < content-length: 0
   content-length: 0
   < x-envoy-upstream-service-time: 1
   x-envoy-upstream-service-time: 1
   < server: envoy
   server: envoy
   ```

7. Optional: If you no longer need the HTTP listener, clean up the resources that you created.

   ```shell
   kubectl delete -A gateways,httproutes -l example=httpbin-mydomain
   ```