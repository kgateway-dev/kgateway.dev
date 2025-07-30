---
title: Traffic splitting
weight: 20
---

Set up weight-based routing between multiple apps. 

## Before you begin

{{< reuse "docs/snippets/prereq.md" >}}

## Deploy the Helloworld sample app

To demonstrate weighted routing for multiple apps, deploy 3 versions of the Helloworld sample app. 

1. Create the helloworld namespace.  
   ```sh
   kubectl create namespace helloworld
   ```

2. Deploy the Hellworld sample apps. 
   ```sh
   kubectl -n helloworld apply -f https://raw.githubusercontent.com/solo-io/gloo-edge-use-cases/main/docs/sample-apps/helloworld.yaml
   ```

   Example output: 
   ```
   service/helloworld-v1 created
   service/helloworld-v2 created
   service/helloworld-v3 created
   deployment.apps/helloworld-v1 created
   deployment.apps/helloworld-v2 created
   deployment.apps/helloworld-v3 created
   ```

3. Verify that the Helloworld pods are up and running. 
   ```sh
   kubectl -n default get pods -n helloworld
   ```

   Example output: 
   ```
   NAME                             READY   STATUS    RESTARTS   AGE
   helloworld-v1-5c457458f-rfkc7    3/3     Running   0          30s
   helloworld-v2-6594c54f6b-8dvjp   3/3     Running   0          29s
   helloworld-v3-8576f76d87-czdll   3/3     Running   0          29s
   ```

## Set up weighted routing 

1. Create an HTTPRoute resource for the `traffic.split.example` domain that routes 10% of the traffic to `helloworld-v1`, 10% to `helloworld-v2`, and 80% to `helloworld-v3`.
   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.networking.k8s.io/v1
   kind: HTTPRoute
   metadata:
     name: traffic-split
     namespace: helloworld
   spec:
     parentRefs:
     - name: http
       namespace: {{< reuse "docs/snippets/namespace.md" >}}
     hostnames:
     - traffic.split.example
     rules:
     - matches:
       - path:
           type: PathPrefix
           value: /
       backendRefs:
       - name: helloworld-v1
         port: 5000
         weight: 10
       - name: helloworld-v2
         port: 5000
         weight: 10
       - name: helloworld-v3
         port: 5000
         weight: 80
   EOF
   ```

   |Setting|Description|
   |--|--|
   |`spec.parentRefs.name`|The name and namespace of the gateway resource that serves the route. In this example, you use the gateway that you created when you set up the [Sample app](/docs/operations/sample-app/). |
   |`spec.hostnames`| The hostname for which you want to apply traffic splitting.|
   |`spec.rules.matches.path`|The path prefix to match on. In this example, `/` is used. |
   |`spec.rules.backendRefs`| A list of services you want to forward traffic to. Use the `weight` option to define the amount of traffic that you want to forward to each service. |

2. Verify that the HTTPRoute is applied successfully. 
   ```sh
   kubectl get httproute/traffic-split -n helloworld -o yaml
   ```

3. Send a few requests to the `/hello` path. Verify that you see responses from all 3 Helloworld apps, and that most responses are returned from `helloworld-v3`. 
   {{< tabs items="Cloud Provider LoadBalancer,Port-forward for local testing" tabTotal="2" >}}
   {{% tab tabName="Cloud Provider LoadBalancer" %}}
   ```sh
   for i in {1..20}; do curl -i http://$INGRESS_GW_ADDRESS:8080/hello \
   -H "host: traffic.split.example:8080"; done
   ```
   {{% /tab %}}
   {{% tab tabName="Port-forward for local testing" %}}
   ```sh
   for i in {1..20}; do curl -i localhost:8080/hello \
   -H "host: traffic.split.example"; done
   ```
   {{% /tab %}}
   {{< /tabs >}}
   
   Example output: 
   ```
   HTTP/1.1 200 OK
   server: envoy
   date: Wed, 12 Mar 2025 20:59:35 GMT
   content-type: text/html; charset=utf-8
   content-length: 60
   x-envoy-upstream-service-time: 110

   Hello version: v3, instance: helloworld-v3-55bfdf76cf-nv545
   ```

   
## Cleanup

{{< reuse "docs/snippets/cleanup.md" >}}

1. Remove the HTTP route resource. 
   ```sh
   kubectl delete httproute traffic-split -n helloworld
   ```

2. Remove the Helloworld apps. 
   ```sh
   kubectl delete -n helloworld -f https://raw.githubusercontent.com/solo-io/gloo-edge-use-cases/main/docs/sample-apps/helloworld.yaml
   ```
