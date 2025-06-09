---
title: HTTP listeners
weight: 10
---

Create an HTTP listener on your API gateway. Then, your API gateway listens for HTTP traffic on the specified port and hostname that you configure. This gateway can be used as the main ingress for the apps in your cluster. You can also create multiple gateways to listen for traffic on different ports and hostnames. 

Next, you set up an HTTPRoute resource to route requests through the gateway to backing services in your cluster. HTTPRoutes can refer to any gateway independent of the namespace they are in.

## Before you begin

1. Follow the [Get started guide](/docs/quickstart/) to install kgateway.

2. Deploy a [sample httpbin app](/docs/operations/sample-app/#deploy-app).

3. {{% reuse "docs/snippets/prereq-listenerset.md" %}}

   **ListenerSets**: {{< reuse "docs/versions/warn-2-1-only.md" >}} Also, you must install the experimental channel of the Kubernetes Gateway API at version 1.3 or later.
   
## Set up an HTTP listener {#setup-http}

1. Create a gateway resource with an HTTP listener. 
   
   {{< tabs items="Gateway listeners,ListenerSets" >}}
   {{% tab %}}
   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.networking.k8s.io/v1
   kind: Gateway
   metadata:
     name: my-http-gateway
     namespace: kgateway-system
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
   
   {{< reuse "docs/snippets/review-table.md" >}}
   
   |Setting|Description|
   |---|---|
   |`spec.gatewayClassName`|The name of the Kubernetes gateway class that you want to use to configure the gateway. When you set up kgateway, a default gateway class is set up for you.  |
   |`spec.listeners`|Configure the listeners for this gateway. In this example, you configure an HTTP gateway that listens for incoming traffic for the `mydomain.com` domain on port 8080. The gateway can serve HTTP routes from any namespace. |

   {{% /tab %}}
   {{% tab %}}
   
   {{% callout type="warning" %}}
   {{< reuse "docs/versions/warn-2-1-only.md" >}} Also, you must install the experimental channel of the Kubernetes Gateway API at version 1.3 or later.
   {{% /callout %}}

   1. Create a Gateway that enables the attachment of ListenerSets.
      
      ```yaml
      kubectl apply -f- <<EOF
      apiVersion: gateway.networking.k8s.io/v1
      kind: Gateway
      metadata:
        name: my-http-gateway
        namespace: kgateway-system
        labels:
          example: httpbin-mydomain
      spec:
        gatewayClassName: kgateway
        allowedListeners:
          namespaces:
            from: All        
        listeners:
        - protocol: HTTP
          port: 80
          name: http
          allowedRoutes:
            namespaces:
              from: All
      EOF
      ```
   
      {{< reuse "docs/snippets/review-table.md" >}}
   
      |Setting|Description|
      |---|---|
      |`spec.gatewayClassName`|The name of the Kubernetes gateway class that you want to use to configure the gateway. When you set up kgateway, a default gateway class is set up for you.  |
      |`spec.allowedListeners`|Enable the attachment of ListenerSets to this Gateway. The example allows listeners from any namespace, which is helpful in multitenant environments. You can also limit the allowed listeners. To limit to listeners in the same namespace as the Gateway, set this value to `Same`. To limit to listeners with a particular label, set this value to `Selector`. |
      |`spec.listeners`| Optionally, you can configure a listener that is specific to the Gateway. Note that due to a [Gateway API limitation](https://gateway-api.sigs.k8s.io/geps/gep-1713/#gateway-changes), you must configure at least one listener on the Gateway resource, even if the listener is not used and is a "dummy" listener. This dummy listener cannot conflict with the listener that you configure in the ListenerSet, such as using the same port or name. In this example, the dummy listener is configured on port 80, which differs from port 8080 in the ListenerSet that you create later. |

   2. Create a ListenerSet that configures an HTTP listener for the Gateway.

      ```yaml
      kubectl apply -f- <<EOF
      apiVersion: gateway.networking.x-k8s.io/v1alpha1
      kind: XListenerSet
      metadata:
        name: my-http-listenerset
        namespace: httpbin
        labels:
          example: httpbin-mydomain
      spec:
        parentRef:
          name: my-http-gateway
          namespace: kgateway-system
          kind: Gateway
          group: gateway.networking.k8s.io
        listeners:
        - protocol: HTTP
          port: 8080
          hostname: mydomain.com
          name: http-listener-set
          allowedRoutes:
            namespaces:
              from: All
      EOF
      ```

      {{< reuse "docs/snippets/review-table.md" >}}

      |Setting|Description|
      |--|--|
      |`spec.parentRef`|The name of the Gateway to attach the ListenerSet to. |
      |`spec.listeners`|Configure the listeners for this ListenerSet. In this example, you configure an HTTP gateway that listens for incoming traffic for the `mydomain.com` domain on port 8080. The gateway can serve HTTP routes from any namespace. |

   {{% /tab %}}
   {{< /tabs >}}

2. Check the status of the gateway to make sure that your configuration is accepted. Note that in the output, a `NoConflicts` status of `False` indicates that the gateway is accepted and does not conflict with other gateway configuration. 
   ```sh
   kubectl get gateway my-http-gateway -n kgateway-system -o yaml
   ```

3. Create an HTTPRoute resource for the httpbin app that is served by the gateway that you created.
   
   {{< tabs items="Gateway listeners,ListenerSets" >}}
   {{% tab %}}
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
         namespace: kgateway-system
     rules:
       - backendRefs:
           - name: httpbin
             port: 8000
   EOF
   ```
   {{% /tab %}}
   {{% tab %}}
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
       - name: my-http-listenerset
         namespace: httpbin
         kind: XListenerSet
         group: gateway.networking.x-k8s.io
     rules:
       - backendRefs:
           - name: httpbin
             port: 8000
   EOF
   ```
   {{% /tab %}}
   {{< /tabs >}}

4. Verify that the HTTPRoute is applied successfully. 
   ```sh
   kubectl get httproute/httpbin-mydomain -n httpbin -o yaml
   ```

   Example output: Notice in the `status` section that the parentRef is either the Gateway or the ListenerSet, depending on how you attached the HTTPRoute.

   ```yaml
   ...
   status:
     parents:
     - conditions:
       - lastTransitionTime: "2025-04-29T20:48:51Z"
         message: ""
         observedGeneration: 3
         reason: Accepted
         status: "True"
         type: Accepted
       - lastTransitionTime: "2025-04-29T20:48:51Z"
         message: ""
         observedGeneration: 3
         reason: ResolvedRefs
         status: "True"
         type: ResolvedRefs
       controllerName: kgateway.dev/kgateway
     parentRef:
       group: gateway.networking.k8s.io
       kind: Gateway
       name: my-http-gateway
       namespace: kgateway-system
   ```

5. Verify that the listener now has a route attached.

   {{< tabs items="Gateway listeners,ListenerSet (experimental)" >}}
   {{% tab %}}   

   ```sh
   kubectl get gateway -n kgateway-system my-http-gateway -o yaml
   ```

   Example output:

   ```yaml
   ...
   listeners:
   - attachedRoutes: 1
   ```
   {{% /tab %}}
   {{% tab %}}

   ```sh
   kubectl get xlistenerset -n httpbin my-http-listenerset -o yaml
   ```

   Example output:

   ```yaml
   ...
   listeners:
   - attachedRoutes: 1
   ```

   Note that because the HTTPRoute is attached to the ListenerSet, the Gateway does not show the route in its status.

   ```sh
   kubectl get gateway -n kgateway-system my-http-gateway -o yaml
   ```

   Example output:

   ```yaml
   ...
   listeners:
   - attachedRoutes: 0
   ```

   If you create another HTTPRoute that attaches to the Gateway and uses the same listener as the ListenerSet, then the route is reported in the status of both the Gateway (attachedRoutes: 1) and the ListenerSet (attachedRoutes: 2).

   {{% /tab %}}
   {{< /tabs >}}

6. Get the external address of the gateway and save it in an environment variable.
   {{< tabs items="Cloud Provider LoadBalancer,Port-forward for local testing" >}}
   {{% tab %}}
   ```sh
   export INGRESS_GW_ADDRESS=$(kubectl get svc -n kgateway-system my-http-gateway -o jsonpath="{.status.loadBalancer.ingress[0]['hostname','ip']}")
   echo $INGRESS_GW_ADDRESS   
   ```
   {{% /tab %}}
   {{% tab %}}
   ```sh
   kubectl port-forward deployment/my-http-gateway -n kgateway-system 8080:8080
   ```
   {{% /tab %}}
   {{< /tabs >}}

7. Send a request to the httpbin app and verify that you get back a 200 HTTP response code. 
   {{< tabs items="Cloud Provider LoadBalancer,Port-forward for local testing" >}}
   {{% tab %}}
   ```sh
   curl -vi http://$INGRESS_GW_ADDRESS:8080/status/200 -H "host: mydomain.com:8080" 
   ```
   {{% /tab %}}
   {{% tab %}}
   ```sh
   curl -vi localhost:8080/status/200 -H "host: mydomain.com"
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

## Cleanup

{{< reuse "docs/snippets/cleanup.md" >}}

{{< tabs items="Gateway listeners,ListenerSet (experimental)" >}}
{{% tab %}}
```sh
kubectl delete -A gateways,httproutes -l example=httpbin-mydomain
```
{{% /tab %}}
{{% tab %}}
```sh
kubectl delete -A gateways,httproutes,xlistenersets -l example=httpbin-mydomain
```
{{% /tab %}}
{{< /tabs >}}
