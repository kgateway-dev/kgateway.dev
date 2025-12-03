Apply a CSRF filter to the gateway to help prevent cross-site request forgery attacks.

{{< callout >}}
{{< reuse "docs/snippets/proxy-kgateway.md" >}}
{{< /callout >}}

## About CSRF

According to [OWASP](https://owasp.org/www-community/attacks/csrf), CSRF is defined as follows:

> Cross-Site Request Forgery (CSRF) is an attack that forces an end user to execute unwanted actions on a web application in which they're currently authenticated. With a little help of social engineering (such as sending a link via email or chat), an attacker may trick the users of a web application into executing actions of the attacker's choosing. If the victim is a normal user, a successful CSRF attack can force the user to perform state changing requests like transferring funds, changing their email address, and so forth. If the victim is an administrative account, CSRF can compromise the entire web application.

To help prevent CSRF attacks, you can enable the CSRF filter on your gateway or a specific route. For each route that you apply the CSRF policy to, the filter checks to make sure that a request's origin matches its destination. If the origin and destination do not match, a 403 Forbidden error code is returned. 

{{< callout type="info" >}}
Note that because CSRF attacks specifically target state-changing requests, the filter only acts on HTTP requests that have a state-changing method such as `POST` or `PUT`.
{{< /callout >}}

{{< callout type="info" >}}
To learn more about CSRF, you can try out the [CSRF sandbox](https://www.envoyproxy.io/docs/envoy/latest/start/sandboxes/csrf) in Envoy. 
{{< /callout >}}

## Before you begin

{{< reuse "docs/snippets/prereq.md" >}}

## Set up CSRF 

Use a {{< reuse "docs/snippets/trafficpolicy.md" >}} resource to define your CSRF rules. 

1. Create a {{< reuse "docs/snippets/trafficpolicy.md" >}} resource to define your CSRF rules. The following example allows request from only the `allowThisOne.example.com` origin.
   
   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: {{< reuse "docs/snippets/trafficpolicy-apiversion.md" >}}
   kind: {{< reuse "docs/snippets/trafficpolicy.md" >}}
   metadata:
     name: csrf
     namespace: httpbin
   spec:
     targetRefs:
     - group: gateway.networking.k8s.io
       kind: HTTPRoute
       name: httpbin
     csrf:
       percentageEnabled: 100
       additionalOrigins:
       - exact: allowThisOne.example.com
         ignoreCase: false
   EOF
   ```

   {{< reuse "docs/snippets/review-table.md" >}} For more information, see the [API docs](/docs/reference/api/#csrfpolicy).

   | Field | Description |
   |-------|-------------|
   | `targetRefs` | The policy targets the `httpbin` HTTPRoute resource that you created before you began. |
   | `percentageEnabled` | The percentage of requests for which the CSRF policy is enabled. A value of `100` means that all requests are enforced by the CSRF rules. |
   | `additionalOrigins` | Additional origins that the CSRF policy allows, besides the destination origin. Possible values include `exact`, `prefix`, `suffix`, `contains`, `safeRegex`, and an `ignoreCase` boolean. At least one of `exact`, `prefix`, `suffix`, `contains`, or `safeRegex` must be set. The example allows requests from the `allowThisOne.example.com` exact origin. |
   
2. Send a request to the httpbin app on the `www.example.com` domain. Verify that you get back a 403 HTTP response code because no origin is set in your request. 

   {{< tabs tabTotal="2" items="Cloud Provider LoadBalancer,Port-forward for local testing" >}}
   {{% tab tabName="Cloud Provider LoadBalancer" %}}
   ```sh
   curl -vi -X POST http://$INGRESS_GW_ADDRESS:8080/post -H "host: www.example.com:8080"
   ```
   {{% /tab %}}
   {{% tab tabName="Port-forward for local testing" %}}
   ```sh
   curl -vi -X POST localhost:8080/post -H "host: www.example.com"
   ```
   {{% /tab %}}
   {{< /tabs >}}
   
   Example output: 
   
   ```console
   HTTP/1.1 403 Forbidden
   ...
   Invalid origin
   ```

3. Send another request to the httpbin app. This time, you include the `allowThisOne.example.com` origin header. Verify that you get back a 200 HTTP response code, because the origin matches the origin that you specified in the {{< reuse "docs/snippets/trafficpolicy.md" >}} resource.
   
   {{< tabs tabTotal="2" items="Cloud Provider LoadBalancer,Port-forward for local testing" >}}
   {{% tab tabName="Cloud Provider LoadBalancer" %}}
   ```sh
   curl -vi -X POST http://$INGRESS_GW_ADDRESS:8080/post -H "host: www.example.com:8080" -H "origin: allowThisOne.example.com"
   ```
   {{% /tab %}}
   {{% tab tabName="Port-forward for local testing" %}}
   ```sh
   curl -vi -X POST localhost:8080/post -H "host: www.example.com" -H "origin: allowThisOne.example.com"
   ```
   {{% /tab %}}
   {{< /tabs >}}   
     
   Example output: 
   ```console
   HTTP/1.1 200 OK
   ...
   {
     "args": {},
     "headers": {
       "Accept": [
         "*/*"
       ],
       "Content-Length": [
         "0"
       ],
       "Host": [
         "csrf.example:8080"
       ],
       "Origin": [
         "allowThisOne.example.com"
       ],
       "User-Agent": [
         "curl/7.77.0"
       ],
       "X-Envoy-Expected-Rq-Timeout-Ms": [
         "15000"
       ],
       "X-Forwarded-Proto": [
         "http"
      ],
       "X-Request-Id": [
         "b1b53950-f7b3-47e6-8b7b-45a44196f1c4"
       ]
     },
     "origin": "10.X.X.XX:33896",
     "url": "http://csrf.example:8080/post",
     "data": "",
     "files": null,
     "form": null,
     "json": null
   }
   ```

## Monitor CSRF metrics

1. Port-forward the gateway proxy. 
   ```sh
   kubectl port-forward -n {{< reuse "docs/snippets/namespace.md" >}} deploy/http 19000
   ```

2. Open the [`/stats`](http://localhost:19000/stats) endpoint. 

3. Find the statistics for `csrf`.
   
   Example output:

   ```console
   http.http.csrf.missing_source_origin: 1
   http.http.csrf.request_invalid: 0
   http.http.csrf.request_valid: 1
   ...
   ```

   * `missing_source_origin`: The number of requests that were sent without an origin. The number is `1` because you sent the first request without an origin.
   * `request_invalid`: The number of requests that were sent with an origin that did not match the destination origin. The number is `0` because you did not send an invalid request.
   * `request_valid`: The number of requests that were sent with an origin that matched the destination origin. The number is `1` because you sent a valid request in your second request.

## Cleanup

{{< reuse "docs/snippets/cleanup.md" >}}

```sh
kubectl delete {{< reuse "docs/snippets/trafficpolicy.md" >}} csrf -n httpbin
```
