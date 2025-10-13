Route requests to services that listen for incoming traffic on a fixed IP address and port or hostname and port combination by using static Backends.

You simply add the list of static hosts or DNS names to your Backend resource and then reference the Backend in your HTTPRoute resource.

## Before you begin

{{< reuse "docs/snippets/prereq.md" >}}

## HTTP static backend {#http}

1. Create a static Backend resource that routes requests to the [JSON testing API](http://jsonplaceholder.typicode.com/).
   
   ```yaml
   kubectl apply -f- <<EOF 
   apiVersion: gateway.kgateway.dev/v1alpha1
   kind: Backend
   metadata:
     name: json-backend
   spec:
     type: Static
     static:
       hosts:
         - host: jsonplaceholder.typicode.com
           port: 80
   EOF
   ```
   
2. Create an HTTPRoute resource that routes traffic on the `static.example` domain and rewrites the traffic to the hostname of your Backend resource.
   
   {{< callout type="warning" >}}
   Do not specify a port in the `spec.backendRefs.port` field when referencing your Backend. The port is defined in your Backend resource and ignored if set on the HTTPRoute resource.
   {{< /callout >}}
   
   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.networking.k8s.io/v1
   kind: HTTPRoute
   metadata:
     name: static-backend
     namespace: default
   spec:
     parentRefs:
     - name: http
       namespace: {{< reuse "docs/snippets/namespace.md" >}}
     hostnames:
       - static.example
     rules:
       - backendRefs:
         - name: json-backend
           kind: Backend
           group: gateway.kgateway.dev
         filters:
         - type: URLRewrite
           urlRewrite:
             hostname: jsonplaceholder.typicode.com
   EOF
   ```

3. Send a request to your Backend and verify that you get back a 200 HTTP response code and a list of posts. 
   
   {{< tabs tabTotal="2" items="Cloud Provider LoadBalancer,Port-forward for local testing" >}}
   {{% tab tabName="Cloud Provider LoadBalancer" %}}
   ```sh
   curl -vi http://$INGRESS_GW_ADDRESS:8080/posts -H "host: static.example:8080" 
   ```
   {{% /tab %}}
   {{% tab tabName="Port-forward for local testing" %}}
   ```sh
   curl -vi localhost:8080/posts -H "host: static.example:8080" 
   ```
   {{% /tab %}}
   {{< /tabs >}}
   
   Example output: 
   
   ```console
   * Connected to <host> (::1) port 8080
   > GET /posts HTTP/1.1
   > Host: static.example:8080
   > User-Agent: curl/8.7.1
   > Accept: */*
   > 
   * Request completely sent off
   < HTTP/1.1 200 OK
   HTTP/1.1 200 OK
   ...
    < 
    [
      {  
        "userId": 1,
        "id": 1,
        "title": "sunt aut facere repellat provident occaecati excepturi optio reprehenderit",
        "body": "quia et suscipit\nsuscipit recusandae consequuntur expedita et cum\nreprehenderit molestiae ut ut quas totam\nnostrum rerum est autem sunt rem eveniet architecto"
      },
      {
        "userId": 1,
        "id": 2,
        "title": "qui est esse",
        "body": "est rerum tempore vitae\nsequi sint nihil reprehenderit dolor beatae ea dolores neque\nfugiat blanditiis voluptate porro vel nihil molestiae ut reiciendis\nqui aperiam non debitis possimus qui neque nisi nulla"
      },
      {
        "userId": 1,
        "id": 3,
        "title": "ea molestias quasi exercitationem repellat qui ipsa sit aut",
        "body": "et iusto sed quo iure\nvoluptatem occaecati omnis eligendi aut ad\nvoluptatem doloribus vel accusantium quis pariatur\nmolestiae porro eius odio et labore et velit aut"
      },
      {
        "userId": 1,
        "id": 4,
        "title": "eum et est occaecati",
        "body": "ullam et saepe reiciendis voluptatem adipisci\nsit amet autem assumenda provident rerum culpa\nquis hic commodi nesciunt rem tenetur doloremque ipsam iure\nquis sunt voluptatem rerum illo velit"
      },
   ...
   ```

## HTTPS static backend {#https}

1. [Create an HTTPS listener for your Gateway]({{< link-hextra path="/setup/listeners/https/" >}}).

2. Create a static Backend resource that routes requests to the [JSON testing API](https://jsonplaceholder.typicode.com/).
   
   ```yaml
   kubectl apply -f- <<EOF 
   apiVersion: gateway.kgateway.dev/v1alpha1
   kind: Backend
   metadata:
     name: json-backend
   spec:
     type: Static
     static:
       hosts:
         - host: jsonplaceholder.typicode.com
           port: 443
   EOF
   ```
   
3. Create an HTTPRoute resource that routes traffic on the `static.example` domain and rewrites the traffic to the hostname of your Backend resource.
   
   {{< callout type="warning" >}}
   Do not specify a port in the `spec.backendRefs.port` field when referencing your Backend. The port is defined in your Backend resource and ignored if set on the HTTPRoute resource.
   {{< /callout >}}
   
   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.networking.k8s.io/v1
   kind: HTTPRoute
   metadata:
     name: static-backend
     namespace: default
   spec:
     parentRefs:
     - name: https
       namespace: {{< reuse "docs/snippets/namespace.md" >}}
     hostnames:
       - static.example.com
     rules:
       - backendRefs:
         - name: json-backend
           kind: Backend
           group: gateway.kgateway.dev
         filters:
         - type: URLRewrite
           urlRewrite:
             hostname: jsonplaceholder.typicode.com
   EOF
   ```

4. Set up a BackendConfigPolicy or BackendTLSPolicy, such as the following examples. This way, the Gateway can initiate a TLS connection to the secured backend. For more information, see the [Backend TLS]({{< link-hextra path="/security/backend-tls/" >}}) guide.

   {{< callout type="info" >}}
   If you generated a self-signed certificate when setting up the HTTPS listener, make sure the certificate contains Subject Alternative Name (SAN) entries for the hostname you configured (for example, both `example.com` and `*.example.com` for wildcard coverage) and install the root certificate into your local trust store of your system or pass it to your client. For example, for a `curl` client, add the `--cacert example_certs/root.crt` option (update the path to match where you stored the certificate).
   {{< /callout >}}

   {{< tabs tabTotal="2" items="BackendConfigPolicy, BackendTLSPolicy" >}}
   {{% tab tabName="BackendConfigPolicy" %}}
   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.kgateway.dev/v1alpha1
   kind: BackendConfigPolicy
   metadata:
     name: static-tls-policy
   spec:
     targetRefs:
     - group: gateway.kgateway.dev
       kind: Backend
       name: json-backend
     tls:
       sni: "jsonplaceholder.typicode.com"
       wellKnownCACertificates: System
   EOF
   ```
   {{% /tab %}}
   {{% tab tabName="BackendTLSPolicy" %}}
   Note that to use the BackendTLSPolicy, you must have the experimental channel of the Kubernetes Gateway API version 1.4 or later.
   ```yaml
   kubectl apply -f - <<EOF
   apiVersion: gateway.networking.k8s.io/v1
   kind: BackendTLSPolicy
   metadata:
     name: static-tls-policy
   spec:
     targetRefs:
     - group: gateway.kgateway.dev
       kind: Backend
       name: json-backend
     validation:
       hostname: "jsonplaceholder.typicode.com"
       wellKnownCACertificates: System
   EOF
   ```
   {{% /tab %}}
   {{< /tabs >}}

5. Send a request to your Backend and verify that you get back a 200 HTTP response code and a list of posts. Note that you can remove the `--cacert example_certs/root.crt` if you stored the certificates in the local trust store of your system.
   
   {{< tabs tabTotal="2" items="Cloud Provider LoadBalancer,Port-forward for local testing" >}}
   {{% tab tabName="Cloud Provider LoadBalancer" %}}
   ```sh
   curl -vi --cacert example_certs/root.crt --resolve "static.example.com:443:${INGRESS_GW_ADDRESS}" https://static.example.com:443/posts
   ```
   {{% /tab %}}
   {{% tab tabName="Port-forward for local testing" %}}
   ```sh
   curl -vi --cacert example_certs/root.crt --connect-to static.example.com:443:localhost:8443 https://static.example.com:443/posts
   ```
   {{% /tab %}}
   {{< /tabs >}}
   
   Example output: 
   
   ```console
   * Connecting to hostname: localhost
   * Connecting to port: 8443
   * Host localhost:8443 was resolved.
   * IPv6: ::1
   * IPv4: 127.0.0.1
   *   Trying [::1]:8443...
   * Connected to localhost (::1) port 8443
   * ALPN: curl offers h2,http/1.1
   * (304) (OUT), TLS handshake, Client hello (1):
   *  CAfile: example_certs/root.crt
   *  CApath: none
   * (304) (IN), TLS handshake, Server hello (2):
   * (304) (IN), TLS handshake, Unknown (8):
   * (304) (IN), TLS handshake, Certificate (11):
   * (304) (IN), TLS handshake, CERT verify (15):
   * (304) (IN), TLS handshake, Finished (20):
   * (304) (OUT), TLS handshake, Finished (20):
   * SSL connection using TLSv1.3 / AEAD-CHACHA20-POLY1305-SHA256 / [blank] / UNDEF
   * ALPN: server did not agree on a protocol. Uses default.
   * Server certificate:
   *  subject: CN=*.example.com; O=any domain
   *  start date: Oct  3 20:00:29 2025 GMT
   *  expire date: Oct  3 20:00:29 2026 GMT
   *  subjectAltName: host "static.example.com" matched cert's "*.example.com"
   *  issuer: O=any domain; CN=*
   *  SSL certificate verify ok.
   * using HTTP/1.x
   > GET /posts HTTP/1.1
   > Host: static.example.com
   > User-Agent: curl/8.7.1
   > Accept: */*
   > 
   * Request completely sent off
   < HTTP/1.1 200 OK
   HTTP/1.1 200 OK
   < date: Fri, 03 Oct 2025 20:16:33 GMT
   date: Fri, 03 Oct 2025 20:16:33 GMT
   < content-type: application/json; charset=utf-8
   content-type: application/json; charset=utf-8
   < access-control-allow-credentials: true
   access-control-allow-credentials: true
   < cache-control: max-age=43200
   cache-control: max-age=43200
   < etag: W/"6b80-Ybsq/K6GwwqrYkAsFxqDXGC7DoM"
   etag: W/"6b80-Ybsq/K6GwwqrYkAsFxqDXGC7DoM"
   < expires: -1
   expires: -1
   < nel: {"report_to":"heroku-nel","response_headers":["Via"],"max_age":3600,"success_fraction":0.01,"failure_fraction":0.1}
   nel: {"report_to":"heroku-nel","response_headers":["Via"],"max_age":3600,"success_fraction":0.01,"failure_fraction":0.1}
   < pragma: no-cache
   pragma: no-cache
   < report-to: {"group":"heroku-nel","endpoints":[{"url":"https://nel.heroku.com/reports?s=ES57MFYpcItNxqncxNgHKfLc4wJs5mHsrj1ja3lxILk%3D\u0026sid=e11707d5-02a7-43ef-b45e-2cf4d2036f7d\u0026ts=1756406957"}],"max_age":3600}
   report-to: {"group":"heroku-nel","endpoints":[{"url":"https://nel.heroku.com/reports?s=ES57MFYpcItNxqncxNgHKfLc4wJs5mHsrj1ja3lxILk%3D\u0026sid=e11707d5-02a7-43ef-b45e-2cf4d2036f7d\u0026ts=1756406957"}],"max_age":3600}
   < reporting-endpoints: heroku-nel="https://nel.heroku.com/reports?s=ES57MFYpcItNxqncxNgHKfLc4wJs5mHsrj1ja3lxILk%3D&sid=e11707d5-02a7-43ef-b45e-2cf4d2036f7d&ts=1756406957"
   reporting-endpoints: heroku-nel="https://nel.heroku.com/reports?s=ES57MFYpcItNxqncxNgHKfLc4wJs5mHsrj1ja3lxILk%3D&sid=e11707d5-02a7-43ef-b45e-2cf4d2036f7d&ts=1756406957"
   < server: envoy
   server: envoy
   < vary: Origin, Accept-Encoding
   vary: Origin, Accept-Encoding
   < via: 2.0 heroku-router
   via: 2.0 heroku-router
   < x-content-type-options: nosniff
   x-content-type-options: nosniff
   < x-powered-by: Express
   x-powered-by: Express
   < x-ratelimit-limit: 1000
   x-ratelimit-limit: 1000
   < x-ratelimit-remaining: 999
   x-ratelimit-remaining: 999
   < x-ratelimit-reset: 1756406983
   x-ratelimit-reset: 1756406983
   < age: 24922
   age: 24922
   < cf-cache-status: HIT
   cf-cache-status: HIT
   < cf-ray: 988f1e308c9f0a91-IAD
   cf-ray: 988f1e308c9f0a91-IAD
   < alt-svc: h3=":443"; ma=86400
   alt-svc: h3=":443"; ma=86400
   < x-envoy-upstream-service-time: 107
   x-envoy-upstream-service-time: 107
   < transfer-encoding: chunked
   transfer-encoding: chunked
   < 
   
   [
     {
       "userId": 1,
       "id": 1,
       "title": "sunt aut facere repellat provident occaecati excepturi optio reprehenderit",
       "body": "quia et suscipit\nsuscipit recusandae consequuntur expedita et cum\nreprehenderit molestiae ut ut quas totam\nnostrum rerum est autem sunt rem eveniet architecto"
     },
   ...
   ```

## Cleanup

{{< reuse "docs/snippets/cleanup.md" >}}

{{< tabs tabTotal="2" items="HTTP,HTTPS">}}
{{% tab tabName="HTTP" %}}
```sh
kubectl delete httproute static-backend
kubectl delete backend json-backend
```
{{% /tab %}}
{{% tab tabName="HTTPS" %}}
```sh
kubectl delete httproute static-backend
kubectl delete backendconfigpolicy static-tls-policy
kubectl delete backendtlspolicy static-tls-policy
kubectl delete backend json-backend
```
{{% /tab %}}
{{< /tabs >}}