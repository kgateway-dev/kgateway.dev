The httpbin app lets you test your API gateway by sending requests to it and receiving responses.

Review the following diagram to understand the setup.

```mermaid
flowchart LR
    A[client] -->|example.com| B[gateway proxy]
    B --> C[httpbin backend]
```

* The client calls the `www.example.com` hostname that you set up in the Gateway configuration.
* The gateway proxy receives the request. Based on the routing rules that you set up in the Gateway configuration, the gateway proxy forwards the traffic to the backend destination, which is the httpbin service. The gateway proxy is available from an external LoadBalancer service that is backed by an IP address that your cloud provider typically assigns. For testing in a local cluster where you do not have an external service, you can enable port-forwarding so that the gateway proxy listens on the localhost instead.
* The httpbin service receives and responds to the request. Note that the httpbin service does not have to be publicly exposed because the gateway proxy handles the external traffic. Instead, it can have an internal service type, such as ClusterIP.

## Before you begin

Set up {{< reuse "/docs/snippets/kgateway.md" >}} by following the [Quick start](../../quickstart/) or [Installation]({{< link-hextra path="/install" >}}) guides.

## Deploy a sample app {#deploy-app}

The following configuration file creates the httpbin app. To review the source file, see [the kgateway project](https://github.com/kgateway-dev/kgateway/blob/{{< reuse "docs/versions/github-branch.md" >}}/examples/httpbin.yaml).

1. Create the httpbin app.

   ```shell
   kubectl apply -f https://raw.githubusercontent.com/kgateway-dev/kgateway/refs/heads/{{< reuse "docs/versions/github-branch.md" >}}/examples/httpbin.yaml
   ```

   Example output:
   
   ```txt
   namespace/httpbin created
   serviceaccount/httpbin created
   service/httpbin created
   deployment.apps/httpbin created
   ```

2. Verify that the httpbin app is running.
   
   ```sh
   kubectl -n httpbin get pods
   ```

   Example output: 
   
   ```txt
   NAME                      READY   STATUS    RESTARTS   AGE
   httpbin-d57c95548-nz98t   2/2     Running   0          18s
   ```

## Set up an API gateway {#api-gateway}

{{< reuse "docs/snippets/setup-gateway.md" >}}

## Expose the app on the gateway {#expose-app}

Now that you have an app and a gateway proxy, you can create a route to access the app.

1. Create an HTTPRoute resource to expose the httpbin app on the Gateway. The following example exposes the app on the `wwww.example.com` domain. 
   
   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.networking.k8s.io/v1
   kind: HTTPRoute
   metadata:
     name: httpbin
     namespace: httpbin
   spec:
     parentRefs:
       - name: http
         namespace: {{< reuse "docs/snippets/namespace.md" >}}
     hostnames:
       - "www.example.com"
     rules:
       - backendRefs:
           - name: httpbin
             port: 8000
   EOF
   ```

   |Setting|Description|
   |--|--|
   |`spec.parentRefs`|The name and namespace of the Gateway resource that serves the route. In this example, you use the `http` Gateway that you created earlier.  |
   |`spec.hostnames`|A list of hostnames that the route is exposed on. In the example, the route is exposed on `www.example.com`. |
   |`spec.rules.backendRefs`| The Kubernetes service that serves the incoming request. In this example, requests to `www.example.com` are forwarded to the httpbin app on port 8000. Note that you must create the HTTPRoute in the same namespace as the service that serves that route. To create the HTTPRoute resource in a different namespace, you must create a ReferenceGrant resource to allow the HTTPRoute to forward requests to a service in a different namespace. For more information, see the [Kubernetes API Gateway documentation](https://gateway-api.sigs.k8s.io/api-types/referencegrant/). |

2. Verify that the HTTPRoute is applied successfully. 
   
   ```sh
   kubectl get -n httpbin httproute/httpbin -o yaml
   ```

   Example output: Note the status of the HTTPRoute resource. Check for `Accepted` and `ResolvedRefs` messages. The `parentRef` refers to the Gateway that the HTTPRoute is exposed on.

   ```yaml
   status:
     parents:
     - conditions:
       - lastTransitionTime: "2025-02-13T18:41:06Z"
         message: ""
         observedGeneration: 1
         reason: Accepted
         status: "True"
         type: Accepted
       - lastTransitionTime: "2025-02-13T18:41:06Z"
         message: ""
         observedGeneration: 1
         reason: ResolvedRefs
         status: "True"
         type: ResolvedRefs
       controllerName: kgateway.dev/kgateway
       parentRef:
         group: gateway.networking.k8s.io
         kind: Gateway
         name: http
         namespace: {{< reuse "docs/snippets/namespace.md" >}}
   ```

## Send a request {#send-request}

Now that your httpbin app is running and exposed on the gateway proxy, you can send a request to the app. The steps vary depending on your load balancer setup.

{{< tabs items="Cloud Provider LoadBalancer,Port-forward for local testing" tabTotal="2" >}}
{{% tab tabName="Cloud Provider LoadBalancer" %}}
1. Get the external address of the gateway proxy and save it in an environment variable.
   
   ```sh
   export INGRESS_GW_ADDRESS=$(kubectl get svc -n {{< reuse "docs/snippets/namespace.md" >}} http -o=jsonpath="{.status.loadBalancer.ingress[0]['hostname','ip']}")
   echo $INGRESS_GW_ADDRESS
   ```

2. Send a request to the httpbin app and verify that you get back a 200 HTTP response code. Note that it might take a few seconds for the load balancer service to become fully ready and accept traffic.
   
   ```sh
   curl -i http://$INGRESS_GW_ADDRESS:8080/headers -H "host: www.example.com:8080"
   ```
   
   Example output: 
   
   ```txt
   HTTP/1.1 200 OK
   access-control-allow-credentials: true
   access-control-allow-origin: *
   content-type: application/json; encoding=utf-8
   date: Thu, 13 Feb 2025 18:49:32 GMT
   content-length: 330
   x-envoy-upstream-service-time: 4
   server: envoy
   ```
   ```json
   {
     "headers": {
       "Accept": [
         "*/*"
       ],
       "Host": [
         "www.example.com"
       ],
       "User-Agent": [
         "curl/8.7.1"
       ],
       "X-Envoy-Expected-Rq-Timeout-Ms": [
         "15000"
       ],
       "X-Forwarded-Proto": [
         "http"
       ],
       "X-Request-Id": [
         "26be0bcd-d941-48f4-ac3b-d5ac288ac46f"
       ]
     }
   }
   ```
{{% /tab %}}
{{% tab tabName="Port-forward for local testing"%}}
1. Port-forward the gateway proxy `http` pod on port 8080. 
   
   ```sh
   kubectl port-forward deployment/http -n {{< reuse "docs/snippets/namespace.md" >}} 8080:8080
   ```

2. Send a request to the httpbin app and verify that you get back a 200 HTTP response code. 
   
   ```sh
   curl -i localhost:8080/headers -H "host: www.example.com"
   ```
   
   Example output: 
   
   ```txt
   HTTP/1.1 200 OK
   access-control-allow-credentials: true
   access-control-allow-origin: *
   content-type: application/json; encoding=utf-8
   date: Thu, 13 Feb 2025 18:49:32 GMT
   content-length: 330
   x-envoy-upstream-service-time: 4
   server: envoy
   ```
   ```json
   {
     "headers": {
       "Accept": [
         "*/*"
       ],
       "Host": [
         "www.example.com"
       ],
       "User-Agent": [
         "curl/8.7.1"
       ],
       "X-Envoy-Expected-Rq-Timeout-Ms": [
         "15000"
       ],
       "X-Forwarded-Proto": [
         "http"
       ],
       "X-Request-Id": [
         "26be0bcd-d941-48f4-ac3b-d5ac288ac46f"
       ]
     }
   }
   ```
{{% /tab %}}
{{< /tabs >}}

## Next steps

Now that you have {{< reuse "/docs/snippets/kgateway.md" >}} set up and running, check out the following guides to expand your API gateway capabilities.

- Add routing capabilities to your httpbin route by using the [Traffic management](../../traffic-management) guides. 
- Explore ways to make your routes more resilient by using the [Resiliency](../../resiliency) guides. 
- Secure your routes with external authentication and rate limiting policies by using the [Security](../../security) guides.

## Cleanup

{{< reuse "docs/snippets/cleanup.md" >}}


1. Delete the httpbin app.

   ```sh
   kubectl delete -f https://raw.githubusercontent.com/kgateway-dev/kgateway/refs/heads/{{< reuse "docs/versions/github-branch.md" >}}/examples/httpbin.yaml
   ```

2. Delete the HTTPRoute.

   ```sh
   kubectl delete httproute httpbin -n httpbin
   ```

3. Delete the Gateway.

   ```sh
   kubectl delete gateway http -n {{< reuse "docs/snippets/namespace.md" >}}
   ```

