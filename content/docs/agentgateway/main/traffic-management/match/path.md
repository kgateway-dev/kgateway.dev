---
title: Path 
weight: 10
---

Match the targeted path of an incoming request against specific path criteria. 

For more information, see the [{{< reuse "docs/snippets/k8s-gateway-api-name.md" >}} documentation](https://gateway-api.sigs.k8s.io/api-types/httproute/#matches).

## Before you begin

1. [Set up an agentgateway proxy]({{< link-hextra path="/setup/" >}}). 
2. [Install the httpbin sample app]({{< link-hextra path="/operations/sample-app/" >}}).

## Set up exact matching

1. Create an HTTPRoute resource for the `match.example` domain that matches incoming requests on the `/status/200` exact path. 
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
         - path:
             type: Exact
             value: /status/200
         backendRefs:
           - name: httpbin
             port: 8000
   EOF
   ```
   
2. Send a request to the `/status/200` path of the httpbin app on the `match.example` domain. Verify that you get back a 200 HTTP response code.  
   {{< tabs items="Cloud Provider LoadBalancer,Port-forward for local testing" tabTotal="2" >}}
   {{% tab tabName="Cloud Provider LoadBalancer" %}}
   ```sh
   curl -vi http://$INGRESS_GW_ADDRESS:80/status/200 -H "host: match.example"
   ```
   {{% /tab %}}
   {{% tab tabName="Port-forward for local testing"  %}}
   ```sh
   curl -vi localhost:8080/status/200 -H "host: match.example"
   ```
   {{% /tab %}}
   {{< /tabs >}}

   Example output: 
   ```
   * Request completely sent off
   < HTTP/1.1 200 OK
   HTTP/1.1 200 OK
    access-control-allow-credentials: true
   access-control-allow-credentials: true
   < access-control-allow-origin: *
   access-control-allow-origin: *
   < content-length: 0
   content-length: 0
   ```

3. Send another request to the httpbin app. This time, use the `/headers` path. Because this path is not specified in the HTTPRoute, the request fails and a 404 HTTP response code is returned. 
   {{< tabs items="Cloud Provider LoadBalancer,Port-forward for local testing" tabTotal="2" >}}
   {{% tab tabName="Cloud Provider LoadBalancer" %}}
   ```sh
   curl -vi http://$INGRESS_GW_ADDRESS:80/headers -H "host: match.example"
   ```
   {{% /tab %}}
   {{% tab tabName="Port-forward for local testing" %}}
   ```sh
   curl -vi localhost:8080/headers -H "host: match.example"
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
   
## Set up prefix path matching

1. Create an HTTPRoute resource for the `match.example` domain that matches incoming requests on the `/anything` prefix path. 
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
         - path:
             type: PathPrefix
             value: /anything
         backendRefs:
           - name: httpbin
             port: 8000
   EOF
   ```
   
2. Send a request to the `/anything/team1` path of the httpbin app on the `match.example` domain. Verify that you get back a 200 HTTP response code.  
   {{< tabs items="Cloud Provider LoadBalancer,Port-forward for local testing" tabTotal="2" >}}
   {{% tab tabName="Cloud Provider LoadBalancer" %}}
   ```sh
   curl -vi http://$INGRESS_GW_ADDRESS:80/anything/team1 -H "host: match.example"
   ```
   {{% /tab %}}
   {{% tab tabName="Port-forward for local testing" %}}
   ```sh
   curl -vi localhost:8080/anything/team1 -H "host: match.example"
   ```
   {{% /tab %}}
   {{< /tabs >}}

   Example output: 
   ```
   < HTTP/1.1 200 OK
   HTTP/1.1 200 OK
   < access-control-allow-credentials: true
   access-control-allow-credentials: true
   < access-control-allow-origin: *
   access-control-allow-origin: *
   < content-type: application/json; encoding=utf-8
   content-type: application/json; encoding=utf-8
   < content-length: 304
   content-length: 304
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
       "User-Agent": [
         "curl/8.7.1"
       ]
     },
     "origin": "10.xxx.x.xx:35204",
     "url": "http://match.example/anything/team1",
     "data": "",
     "files": null,
     "form": null,
     "json": null
   }
   ```

3. Send another request to the httpbin app. This time, use the `/headers` path. Because this path is not specified in the HTTPRoute, the request fails and a 404 HTTP response code is returned. 
   {{< tabs items="Cloud Provider LoadBalancer,Port-forward for local testing" tabTotal="2" >}}
   {{% tab tabName="Cloud Provider LoadBalancer" %}}
   ```sh
   curl -vi http://$INGRESS_GW_ADDRESS:80/headers -H "host: match.example"
   ```
   {{% /tab %}}
   {{% tab tabName="Port-forward for local testing" %}}
   ```sh
   curl -vi localhost:8080/headers -H "host: match.example"
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
   
## Set up regex matching

Use [RE2 syntax](https://github.com/google/re2/wiki/Syntax) for regular expressions to match incoming requests.

1. Create an HTTPRoute resource for the `match.example` domain that uses a regular expression (regex) to match incoming requests. The following regex patterns are defined in the example: 
   * **`/.*my-path.*`**: 
     * The request path must start with `/`.
     * The expression `.*` means that any character before and after the `my-path` string is allowed. 
     * Allowed pattern: `/anything/this-is-my-path-1`, not allowed: `/anything`. 
   * **`/anything/stores/[^/]+?/entities`**: 
     * The request path must start with `/anything/stores/`. 
     * `[^/]+?` matches any character except `/`.
     * The request path must end with `/entities`.
     * Allowed pattern: `/anything/stores/us/entities`, not allowed: `/anything/stores/us/south/entities`. 
   * **`/anything/(dogs|cats)/\\d[.]\\d.*`**
     * The request path must start with `/anything/`, followed by either `dogs/` or `cats/`.
     * `\\d` matches a single digit.
     * `[.]` matches a literal period.
     * `\\d.*` matches a single digit followed by zero or any character.
     * Allowed pattern: `/anything/dogs/3.0-game`, not allowed: `/anything/birds`
   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.networking.k8s.io/v1beta1
   kind: HTTPRoute
   metadata:
     name: httpbin-match
     namespace: httpbin
   spec:
     parentRefs:
       - name: agentgateway-proxy
         namespace: {{< reuse "docs/snippets/namespace.md" >}}
     hostnames:
       - "match.example"
     rules:
       - matches:  
         - path:
             type: RegularExpression
             value: /.*my-path.*
         - path:
             type: RegularExpression
             value: /anything/stores/[^/]+?/entities
         - path:
             type: RegularExpression
             value: /anything/(dogs|cats)/\\d[.]\\d.*
         backendRefs:
         - name: httpbin
           namespace: httpbin
           port: 8000
   EOF
   ```
   
2. Send multiple requests to the httpbin app on the `match.example` domain. 
   * `/anything/this-is-my-path-1` matches the regex pattern `\/.*my-path.*` 
   * `/anything/stores/us/entities` matches the regex pattern `/anything/stores/[^/]+?/entities` 
   * `/anything/dogs/3.0-game` matches the regex pattern `/anything/(dogs|cats)/\\d[.]\\d.*`
   
   Verify that the requests succeed and that you get back a 200 HTTP response code.  
   {{< tabs items="Cloud Provider LoadBalancer,Port-forward for local testing" tabTotal="2" >}}
   {{% tab tabName="Cloud Provider LoadBalancer" %}}
   ```sh
   curl -vi http://$INGRESS_GW_ADDRESS:80/anything/this-is-my-path-1 -H "host: match.example"
   curl -vi http://$INGRESS_GW_ADDRESS:80/anything/stores/us/entities -H "host: match.example"
   curl -vi http://$INGRESS_GW_ADDRESS:80/anything/dogs/3.0-game -H "host: match.example"
   ```
   {{% /tab %}}
   {{% tab tabName="Port-forward for local testing" %}}
   ```sh
   curl -vi localhost:8080/anything/this-is-my-path-1 -H "host: match.example"
   curl -vi localhost:8080/anything/stores/us/entities -H "host: match.example"
   curl -vi localhost:8080/anything/dogs/3.0-game -H "host: match.example"
   ```
   {{% /tab %}}
   {{< /tabs >}}

   Example output: 
   ```
   < HTTP/1.1 200 OK
   HTTP/1.1 200 OK
   < access-control-allow-credentials: true
   access-control-allow-credentials: true
   < access-control-allow-origin: *
   access-control-allow-origin: *
   < content-type: application/json; encoding=utf-8
   content-type: application/json; encoding=utf-8
   < content-length: 317
   content-length: 317
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
       "User-Agent": [
         "curl/8.7.1"
       ]
     },
     "origin": "10.xxx.x.xx:43182",
     "url": "http://match.example/anything/stores/us/entities",
     "data": "",
     "files": null,
     "form": null,
     "json": null
   }
   ```

3. Send requests to the httpbin app that do not meet the defined regex patterns.
   * `/anything` does not match the regex pattern `\/.*my-path.*` 
   * `/anything/stores/us/south/entities` does not match the regex pattern `/anything/stores/[^/]+?/
   * `/anything/birds/1.1-game` does not match the regex pattern `/anything/(dogs|cats)/\\d[.]\\d.*`
   
   Verify that all requests fail with a 404 HTTP response code, because the path does not match the regex pattern that you defined. 
   {{< tabs items="Cloud Provider LoadBalancer,Port-forward for local testing" tabTotal="2" >}}
   {{% tab tabName="Cloud Provider LoadBalancer" %}}
   ```sh
   curl -vi http://$INGRESS_GW_ADDRESS:80/anything -H "host: match.example"
   curl -vi http://$INGRESS_GW_ADDRESS:80/anything/stores/us/south/entities -H "host: match.example"
   curl -vi http://$INGRESS_GW_ADDRESS:80/anything/birds/1.1-game -H "host: match.example"
   ```
   {{% /tab %}}
   {{% tab tabName="Port-forward for local testing" %}}
   ```sh
   curl -vi localhost:8080/anything -H "host: match.example"
   curl -vi localhost:8080/anything/stores/us/south/entities -H "host: match.example"
   curl -vi localhost:8080/anything/birds/1.1-game -H "host: match.example"
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



