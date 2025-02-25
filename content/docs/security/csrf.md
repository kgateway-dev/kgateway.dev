---
title: CSRF
weight: 10
description: Apply a CSRF filter to the gateway to help prevent cross-site request forgery attacks.
next: /docs/security/local
---

Apply a CSRF filter to the gateway to help prevent cross-site request forgery attacks.

## About CSRF

According to [OWASP](https://owasp.org/www-community/attacks/csrf), CSRF is defined as follows: 
> Cross-Site Request Forgery (CSRF) is an attack that forces an end user to execute unwanted actions on a web application in which they’re currently authenticated. With a little help of social engineering (such as sending a link via email or chat), an attacker may trick the users of a web application into executing actions of the attacker’s choosing. If the victim is a normal user, a successful CSRF attack can force the user to perform state changing requests like transferring funds, changing their email address, and so forth. If the victim is an administrative account, CSRF can compromise the entire web application.

To help prevent CSRF attacks, you can enable the CSRF filter on your gateway or a specific route. For each route that you apply the CSRF policy to, the filter checks to make sure that a request's origin matches its destination. If the origin and destination do not match, a 403 Forbidden error code is returned. 

{{% callout type="info" %}}
Note that because CSRF attacks specifically target state-changing requests, the filter only acts on HTTP requests that have a state-changing method such as `POST` or `PUT`.
{{% /callout %}}

{{% callout type="info"  %}}
To learn more about CSRF, you can try out the [CSRF sandbox](https://www.envoyproxy.io/docs/envoy/latest/start/sandboxes/csrf) in Envoy. 
{{% /callout%}}

{{% callout type="info"  %}}
If you use {{< reuse "docs/snippets/product-name.md" >}} Enterprise, you can also set up a Web Application Firewall that is based on Apache ModSecurity. The filter lets you define CSRF rules in the OWASP Core Rule Set.
{{% /callout %}}

## Set up CSRF 

{{< tabs items="Gateway-level configuration,Route-level config" >}}
{{% tab  %}}

Use a VirtualHostOption resource to define your CSRF rules. 

1. Create a VirtualHostOption resource to define your CSRF rules. 
   ```yaml
   kubectl apply -n {{< reuse "docs/snippets/ns-system.md" >}} -f- <<EOF
   apiVersion: gateway.solo.io/v1
   kind: VirtualHostOption
   metadata:
     name: csrf
     namespace: {{< reuse "docs/snippets/ns-system.md" >}}
   spec:
     options:
       csrf:
         filterEnabled: 
           defaultValue: 
             numerator: 100
             denominator: HUNDRED
         additionalOrigins:
         - exact: allowThisOne.solo.io
     targetRefs:
     - group: gateway.networking.k8s.io
       kind: Gateway
       name: http
       namespace: {{< reuse "docs/snippets/ns-system.md" >}}
   EOF
   ```

2. Send a request to the httpbin app. Verify that you get back a 403 HTTP response code because no origin is set in your request. 
   * **LoadBalancer IP address or hostname**
     ```sh
     curl -vik -X POST http://$INGRESS_GW_ADDRESS:8080/post -H "host: www.example.com:8080"
     ```
   * **Port-forward for local testing**
     ```sh
     curl -vik -X POST localhost:8080/post -H "host: www.example.com"
     ```
   
   Example output: 
   ```console
   * Mark bundle as not supporting multiuse
   < HTTP/1.1 403 Forbidden
   HTTP/1.1 403 Forbidden
   < content-length: 14
   content-length: 14
   < content-type: text/plain
   content-type: text/plain
   < date: Tue, 23 Apr 2024 20:40:46 GMT
   date: Tue, 23 Apr 2024 20:40:46 GMT
   < server: envoy
   server: envoy
   ```

3. Send another request to the httpbin app. This time, you include the `allowThisOne.solo.io` origin header. Verify that you get back a 200 HTTP response code, because the origin matches the origin that you specified in the RouteOption resource.
   * **LoadBalancer IP address or hostname**
     ```sh
     curl -vik -X POST http://$INGRESS_GW_ADDRESS:8080/post -H "host: www.example.com:8080" -H "origin: allowThisOne.solo.io"
     ```
   * **Port-forward for local testing**
     ```sh
     curl -vik -X POST localhost:8080/post -H "host: www.example.com" -H "origin: allowThisOne.solo.io"
     ```
     
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
         "allowThisOne.solo.io"
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

4. Optional: Remove the resources that you created. 
   ```sh
   kubectl delete virtualhostoption csrf -n {{< reuse "docs/snippets/ns-system.md" >}}
   ```
   

{{% /tab %}}
{{% tab  %}}

Use a RouteOption resource to define your CSRF rules. 

1. Create a RouteOption resource to define your CSRF rules. The following example allows request from only the `allowThisOne.solo.io` origin. 
   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.solo.io/v1
   kind: RouteOption
   metadata:
     name: csrf
     namespace: httpbin
   spec:
     options:
       csrf:
         filterEnabled: 
           defaultValue: 
             numerator: 100
             denominator: HUNDRED
         additionalOrigins:
         - exact: allowThisOne.solo.io
   EOF
   ```

2. Create an HTTPRoute resource for the httpbin app that applies the RouteOption resource that you just created. 
   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.networking.k8s.io/v1
   kind: HTTPRoute
   metadata:
     name: httpbin-csrf
     namespace: httpbin
   spec:
     parentRefs:
     - name: http
       namespace: {{< reuse "docs/snippets/ns-system.md" >}}
     hostnames:
       - csrf.example
     rules:
       - filters:
           - type: ExtensionRef
             extensionRef:
               group: gateway.solo.io
               kind: RouteOption
               name: csrf
         backendRefs:
           - name: httpbin
             port: 8000
   EOF
   ```
   
3. Send a request to the httpbin app on the `csrf.example` domain. Verify that you get back a 403 HTTP response code because no origin is set in your request. 
   * **LoadBalancer IP address or hostname**
     ```sh
     curl -vik -X POST http://$INGRESS_GW_ADDRESS:8080/post -H "host: csrf.example:8080"
     ```
   * **Port-forward for local testing**
     ```sh
     curl -vik -X POST localhost:8080/post -H "host: csrf.example"
     ```
   
   Example output: 
   ```console
   * Mark bundle as not supporting multiuse
   < HTTP/1.1 403 Forbidden
   HTTP/1.1 403 Forbidden
   < content-length: 14
   content-length: 14
   < content-type: text/plain
   content-type: text/plain
   < date: Tue, 23 Apr 2024 20:40:46 GMT
   date: Tue, 23 Apr 2024 20:40:46 GMT
   < server: envoy
   server: envoy
   ```

4. Send another request to the httpbin app. This time, you include the `allowThisOne.solo.io` origin header. Verify that you get back a 200 HTTP response code, because the origin matches the origin that you specified in the RouteOption resource.
   * **LoadBalancer IP address or hostname**
     ```sh
     curl -vik -X POST http://$INGRESS_GW_ADDRESS:8080/post -H "host: csrf.example:8080" -H "origin: allowThisOne.solo.io"
     ```
   * **Port-forward for local testing**
     ```sh
     curl -vik -X POST localhost:8080/post -H "host: csrf.example" -H "origin: allowThisOne.solo.io"
     ```
     
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
         "allowThisOne.solo.io"
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

5. Optional: Remove the resources that you created. 
   ```sh
   kubectl delete routeoption csrf -n httpbin
   kubectl delete httproute httpbin-csrf -n httpbin
   ```


{{% /tab %}}
{{< /tabs >}}

## Monitor CSRF metrics

1. Port-forward the gateway proxy. 
   ```sh
   kubectl port-forward -n {{< reuse "docs/snippets/ns-system.md" >}} deploy/http 19000
   ```

2. Open the [`/stats`](http://localhost:19000/stats) endpoint. 

3. Filter the statistics by `csrf` as shown in the following image and verify that you see metrics for failed and successful CSRF requests as well as requests that were sent without an origin. 

   {{< reuse-image src="img/envoy-stats-csrf.svg" >}}