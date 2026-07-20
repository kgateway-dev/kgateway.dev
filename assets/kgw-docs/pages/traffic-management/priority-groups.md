Route traffic to a primary backend and automatically fail over to a secondary backend when the primary becomes unhealthy by using a `priorityGroups` Backend.

A `priorityGroups` Backend holds an ordered list of target groups that you can route traffic to. Each group references one or more static Backend resources in the same namespace. The gateway proxy sends traffic to the highest-priority group (group 0) by default. When all endpoints in that group fail their active health checks, traffic automatically shifts to the next group. Recovery happens automatically when the primary endpoints become healthy again.

>[!WARNING]
> The `priorityGroups` Backend field is an experimental API and subject to breaking changes in future releases.


## Limitations

- **Static backends only**: Each group can only reference Backends of type `static`. Other Backends, such as AWS Lambda, GCP, and Dynamic Forward Proxy are not supported.
- **Same namespace only**: All referenced static Backends must be in the same namespace as the `priorityGroups` Backend. Cross-namespace references are not supported.
- **Shared health check configuration**: A `BackendConfigPolicy` that targets the `priorityGroups` Backend applies its health check settings uniformly to all endpoints across all target groups. You cannot configure different health check settings per group or per referenced static backend.

## Before you begin

{{< reuse "kgw-docs/snippets/prereq.md" >}}

## Set up failover

1. Deploy a hello-world app to use as the failover backend.

   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: apps/v1
   kind: Deployment
   metadata:
     name: hello-world
     namespace: httpbin
   spec:
     replicas: 1
     selector:
       matchLabels:
         app: hello-world
     template:
       metadata:
         labels:
           app: hello-world
       spec:
         containers:
         - name: hello-world
           image: nginxdemos/hello:plain-text
           ports:
           - containerPort: 80
   ---
   apiVersion: v1
   kind: Service
   metadata:
     name: hello-world
     namespace: httpbin
   spec:
     selector:
       app: hello-world
     ports:
     - port: 80
       targetPort: 80
   EOF
   ```

2. Verify that the service is up and running. 
   ```sh
   kubectl get pods -n httpbin | grep hello-world
   ```

   Example output: 
   ```console
   hello-world-747c66d5b6-js8rd   1/1     Running   0             38s
   ```

3. Create two static Backend resources, one for the httpbin app that serves as your primary target and one for the hello-world that you use as a failover target when the httpbin app is unavailable.

   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.kgateway.dev/v1alpha1
   kind: Backend
   metadata:
     name: httpbin-backend
     namespace: httpbin
   spec:
     static:
       hosts:
         - host: httpbin.httpbin.svc.cluster.local
           port: 8000
   ---
   apiVersion: gateway.kgateway.dev/v1alpha1
   kind: Backend
   metadata:
     name: hello-world-backend
     namespace: httpbin
   spec:
     static:
       hosts:
         - host: hello-world.httpbin.svc.cluster.local
           port: 80
   EOF
   ```

4. Create a `priorityGroups` Backend that references both static Backends. The first group (priority 0) receives all traffic by default. The second group (priority 1) is the failover target and only receives traffic when all endpoints in the first group are unhealthy.

   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.kgateway.dev/v1alpha1
   kind: Backend
   metadata:
     name: failover-backend
     namespace: httpbin
   spec:
     priorityGroups:
       - backendRefs:
           - name: httpbin-backend
       - backendRefs:
           - name: hello-world-backend
   EOF
   ```

5. Create a BackendConfigPolicy resource to define the health checks for all target groups in the `priorityGroups` Backend. The proxy uses the health check results to determine when to trigger failover to the next priority group. 

   Note that this example also disables the Envoy panic threshold by setting `healthyPanicThreshold` to `0`. By default, Envoy requires 50% of endpoints to be healthy before the health status is considered for routing. When the healthy endpoints drop below this threshold, Envoy enters panic mode and routes to all endpoints regardless of their health. Because this guide only uses two endpoints, when one becomes unavailable, Envoy panic mode is automatically entered. Disabling the panic threshold allows you to test the failover to the lower priority target group. 

   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.kgateway.dev/v1alpha1
   kind: BackendConfigPolicy
   metadata:
     name: failover-healthcheck
     namespace: httpbin
   spec:
     targetRefs:
       - group: gateway.kgateway.dev
         kind: Backend
         name: failover-backend
     healthCheck:
       healthyThreshold: 1
       http:
         path: /
       interval: 5s
       timeout: 2s
       unhealthyThreshold: 1
     loadBalancer:
       healthyPanicThreshold: 0
       roundRobin: {}
   EOF
   ```

5. Create an HTTPRoute that routes traffic to the `priorityGroups` Backend.

   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.networking.k8s.io/v1
   kind: HTTPRoute
   metadata:
     name: failover-route
     namespace: httpbin
   spec:
     parentRefs:
     - name: http
       namespace: {{< reuse "kgw-docs/snippets/namespace.md" >}}
     hostnames:
       - failover.example
     rules:
       - backendRefs:
         - name: failover-backend
           kind: Backend
           group: gateway.kgateway.dev
   EOF
   ```

6. Send a request to the gateway proxy and verify that you get back a response from the httpbin app that is set as the primary target in your `priorityGroup` Backend. 

   {{< tabs >}}
   {{% tab name="Cloud Provider LoadBalancer" %}}
   ```sh
   curl -vi http://$INGRESS_GW_ADDRESS:8080/ -H "host: failover.example:8080"
   ```
   {{% /tab %}}
   {{% tab name="Port-forward for local testing" %}}
   ```sh
   curl -vi localhost:8080/ -H "host: failover.example:8080"
   ```
   {{% /tab %}}
   {{< /tabs >}}

   Example output:
   ```console
   * Connected to <host> port 8080
   > GET / HTTP/1.1
   > Host: failover.example:8080
   ...
   < HTTP/1.1 200 OK
   HTTP/1.1 200 OK
   < server: envoy
   ...
   <p>A golang port of the venerable <a href="https://httpbin.org/">httpbin.org</a> HTTP request &amp; response testing service.</p>
   ```

## Simulate a failover {#simulate}

Scale the primary httpbin deployment to zero replicas to simulate a Backend failure. The gateway proxy detects that the primary endpoints no longer pass health checks and automatically routes traffic to the hello-world failover Backend.

1. Scale the httpbin deployment to zero replicas.

   ```sh
   kubectl scale deployment/httpbin -n httpbin --replicas=0
   ```

2. Wait for the health check interval to pass (about 5–10 seconds), then send a request. Verify that you now see responses from the hello-world failover backend.

   {{< tabs >}}
   {{% tab name="Cloud Provider LoadBalancer" %}}
   ```sh
   curl -vi http://$INGRESS_GW_ADDRESS:8080/ -H "host: failover.example:8080"
   ```
   {{% /tab %}}
   {{% tab name="Port-forward for local testing" %}}
   ```sh
   curl -vi localhost:8080/ -H "host: failover.example:8080"
   ```
   {{% /tab %}}
   {{< /tabs >}}

   Example output: The response comes from the hello-world nginx service, showing a different server name than httpbin.
   ```console
   < HTTP/1.1 200 OK
   HTTP/1.1 200 OK
   < server: envoy
   ...
   Server address: 10.XXX.X.X:80
   Server name: hello-world-669dfbd799-g4jkg
   URI: /
   Request ID: 796644ce8bda8ae5ecc36c5f4117a590
   ```

3. Restore the httpbin deployment.

   ```sh
   kubectl scale deployment/httpbin -n httpbin --replicas=1
   ```

4. Wait a few seconds for httpbin to pass health checks, then verify that traffic automatically returns to the primary Backend.

   {{< tabs >}}
   {{% tab name="Cloud Provider LoadBalancer" %}}
   ```sh
   curl -vi http://$INGRESS_GW_ADDRESS:8080/ -H "host: failover.example:8080"
   ```
   {{% /tab %}}
   {{% tab name="Port-forward for local testing" %}}
   ```sh
   curl -vi localhost:8080/ -H "host: failover.example:8080"
   ```
   {{% /tab %}}
   {{< /tabs >}}

   Example output:
   ```console
   * Connected to <host> port 8080
   > GET / HTTP/1.1
   > Host: failover.example:8080
   ...
   < HTTP/1.1 200 OK
   HTTP/1.1 200 OK
   < server: envoy
   ...
   <p>A golang port of the venerable <a href="https://httpbin.org/">httpbin.org</a> HTTP request &amp; response testing service.</p>
   ```

## Cleanup

{{< reuse "kgw-docs/snippets/cleanup.md" >}}

```sh
kubectl delete httproute failover-route -n httpbin
kubectl delete backendconfigpolicy failover-healthcheck -n httpbin
kubectl delete backend failover-backend httpbin-backend hello-world-backend -n httpbin
kubectl delete deployment hello-world -n httpbin
kubectl delete service hello-world -n httpbin
```
