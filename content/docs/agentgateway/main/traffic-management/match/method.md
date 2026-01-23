---
title: HTTP method 
weight: 10
---

Specify an HTTP method, such as POST, GET, PUT, PATCH, or DELETE, to match requests against.

For more information, see the [{{< reuse "docs/snippets/k8s-gateway-api-name.md" >}} documentation](https://gateway-api.sigs.k8s.io/api-types/httproute/#matches).

## Before you begin

1. [Set up an agentgateway proxy]({{< link-hextra path="/setup/" >}}). 
2. [Install the httpbin sample app]({{< link-hextra path="/operations/sample-app/" >}}).

## Set up HTTP method matching

1. Create an HTTPRoute resource for the `match.example` domain that serves incoming GET requests for the httpbin app. 
   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.networking.k8s.io/v1
   kind: HTTPRoute
   metadata:
     name: httpbin-match
     namespace: httpbin
   spec:
     parentRefs:
       - name: agentgateway-proxy
         namespace: {{< reuse "docs/snippets/namespace.md" >}}
     hostnames:
       - match.example
     rules:
       - matches:
         - method: "GET"
         backendRefs:
           - name: httpbin
             port: 8000
   EOF
   ```

2. Send a GET request to the httpbin app on the `match.example` domain. Verify that you get back a 200 HTTP response code. 
   {{< tabs items="Cloud Provider LoadBalancer,Port-forward for local testing" tabTotal="2" >}}
   {{% tab tabName="Cloud Provider LoadBalancer" %}}
   ```sh
   curl -vi http://$INGRESS_GW_ADDRESS:80/get -H "host: match.example"
   ```
   {{% /tab %}}
   {{% tab tabName="Port-forward for local testing" %}}
   ```sh
   curl -vi localhost:8080/get -H "host: match.example"
   ```
   {{% /tab %}}
   {{< /tabs >}}

   Example output: 
   ```
   HTTP/1.1 200 OK
   < access-control-allow-credentials: true
   access-control-allow-credentials: true
   < access-control-allow-origin: *
   access-control-allow-origin: *
   < content-type: application/json; encoding=utf-8
   content-type: application/json; encoding=utf-8
   < content-length: 322
   content-length: 322
   < 

   {
     "args": {},
     "headers": {
       "Accept": [
         "*/*"
      ],
       "Host": [
         "match.example"
       ],
       "Traceparent": [
         "00-30f560cded924883c1eebfecfd8a8367-3eedcde5b0a6924f-01"
       ],
       "User-Agent": [
         "curl/8.7.1"
       ]
     },
     "origin": "10.xxx.x.xx:55304",
     "url": "http://match.example/get"
   }
   ```

3. Send another request to the httpbin app on the `match.example` domain. This time, you use the `POST` method. Verify that your request is not forwarded to the httpbin app and that you get back a 404 HTTP response code. 
   {{< tabs items="Cloud Provider LoadBalancer,Port-forward for local testing" tabTotal="2" >}}
   {{% tab tabName="Cloud Provider LoadBalancer" %}}
   ```sh
   curl -vi -X POST http://$INGRESS_GW_ADDRESS:80/post -H "host: match.example" 
   ```
   {{% /tab %}}
   {{% tab tabName="Port-forward for local testing" %}}
   ```sh
   curl -vi -X POST localhost:8080/post -H "host: match.example"
   ```
   {{% /tab %}}
   {{< /tabs >}}

   Example output: 
    ```
   < HTTP/1.1 404 Not Found
   HTTP/1.1 404 Not Found
   < content-length: 9
   content-length: 9
   < content-type: text/plain; charset=utf-8
   content-type: text/plain; charset=utf-8
   ```

## Cleanup

{{< reuse "docs/snippets/cleanup.md" >}}

```sh
kubectl delete httproute httpbin-match -n httpbin
```



