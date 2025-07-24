---
title: HTTPS redirect
weight: 441
description: Redirect HTTP traffic to HTTPS. 
---

Redirect HTTP traffic to HTTPS. 

For more information, see the [{{< reuse "docs/snippets/k8s-gateway-api-name.md" >}} documentation](https://gateway-api.sigs.k8s.io/reference/spec/#gateway.networking.k8s.io/v1.HTTPRequestRedirectFilter).

## Before you begin

{{< reuse "docs/snippets/prereq.md" >}}

## Set up an HTTPS listener

{{% reuse "docs/snippets/listeners-https-create-cert.md" %}}
5. Configure an HTTPS listener on the Gateway that you created earlier. Note that your Gateway now has two listeners, `http` and `https`. You reference these listeners later in this guide to configure the HTTP to HTTPS redirect. 
   ```yaml
   kubectl apply -f- <<EOF                                                          
   kind: Gateway
   apiVersion: gateway.networking.k8s.io/v1
   metadata:
     name: http
     namespace: {{< reuse "docs/snippets/namespace.md" >}}
   spec:
     gatewayClassName: {{< reuse "docs/snippets/gatewayclass.md" >}}
     listeners:
     - protocol: HTTP
       port: 8080
       name: http
       allowedRoutes:
         namespaces:
           from: All
     - name: https
       port: 443
       protocol: HTTPS
       tls:
         mode: Terminate
         certificateRefs:
           - name: https
             kind: Secret
       allowedRoutes:
         namespaces:
           from: All
   EOF
   ```

## Redirect HTTP traffic to HTTPS

1. Create an HTTPRoute for the httpbin app that sets up a `RequestRedirect` filter. By using the `https` scheme, you instruct the Gateway to redirect HTTP traffic to HTTPS and send back a 301 HTTP response code to the client. 
   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.networking.k8s.io/v1
   kind: HTTPRoute
   metadata:
     name: httpbin-https-redirect
     namespace: httpbin
     labels:
       gateway: https
   spec:
     parentRefs:
       - name: http
         namespace: {{< reuse "docs/snippets/namespace.md" >}}
         sectionName: http
     hostnames: 
       - redirect.example
     rules:
       - filters:
         - type: RequestRedirect
           requestRedirect:
             scheme: https
             statusCode: 301
   EOF
   ```

   |Setting|Description|
   |--|--|
   |`spec.parentRefs.name` </br> `spec.parentRefs.namespace` |The name and namespace of the Gateway resource that serves the route. In this example, you use the Gateway that you set up earlier. |
   |`spec.parentRefs.sectionName`|The Gateway listener to bind this route to. In this example, you want to apply the HTTPS redirect to all traffic that is sent to the HTTP listener on the Gateway. |
   |`spec.hostnames`| The hostname for which you want to apply the redirect.|
   |`spec.rules.filters.type`|The type of filter that you want to apply to incoming requests. In this example, the `RequestRedirect` is used.|
   |`spec.rules.filters.requestRedirect.scheme`|The type of redirect that you want to apply. The `https` scheme redirects all incoming HTTP traffic to HTTPS. |
   |`spec.rules.filters.requestRedirect.statusCode`|The HTTP status code that you want to return to the client in case of a redirect. For a permanent redirect, use the 301 HTTP status code.   |

2. Create another HTTPRoute for the httpbin app that routes incoming HTTPS traffic to the httpbin app. Note that you bind this HTTPRoute to the HTTPS listener on your gateway by using `sectionName: https`. 
   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.networking.k8s.io/v1
   kind: HTTPRoute
   metadata:
     name: httpbin-https
     namespace: httpbin
     labels:
       gateway: https
   spec:
     parentRefs:
       - name: http
         namespace: {{< reuse "docs/snippets/namespace.md" >}}
         sectionName: https
     hostnames: 
       - redirect.example
     rules:
       - backendRefs:
           - name: httpbin
             port: 8000
   EOF
   ```

3. Send an HTTP request to the httpbin app on the `redirect.example` domain. Verify that you get back a 301 HTTP response code and that your redirect location shows `https://redirect.example:8080/status/200`. 
   {{< tabs items="Cloud Provider LoadBalancer,Port-forward for local testing" tabTotal="2" >}}
   {{% tab tabName="Cloud Provider LoadBalancer" %}}
   ```sh
   curl -vik http://$INGRESS_GW_ADDRESS:8080/status/200 -H "host: redirect.example"
   ```
   {{% /tab %}}
   {{% tab tabName="Port-forward for local testing" %}}
   ```sh
   curl -vik localhost:8080/status/200 -H "host: redirect.example"
   ```
   {{% /tab %}}
   {{< /tabs >}}

   Example output: 
   ```
   * Mark bundle as not supporting multiuse
   < HTTP/1.1 301 Moved Permanently
   HTTP/1.1 301 Moved Permanently
   < location: https://redirect.example:8080/status/200
   location: https://redirect.example:8080/status/200
   < date: Mon, 06 Nov 2024 01:48:12 GMT
   date: Mon, 06 Nov 2024 01:48:12 GMT
   < server: envoy
   server: envoy
   < content-length: 0
   content-length: 0
   ```
  
4. Send an HTTPS request to the httpbin app on the `redirect.example` domain. Verify that you get back a 200 HTTP response code and that you can see a successful TLS handshake with the gateway. 
   {{< tabs items="Cloud Provider LoadBalancer,Port-forward for local testing" tabTotal="2" >}}
   {{% tab tabName="Cloud Provider LoadBalancer" %}}
   ```sh
   curl -vik https://$INGRESS_GW_ADDRESS:443/status/200 -H "host: redirect.example"
   ```
   {{% /tab %}}
   {{% tab tabName="Port-forward for local testing" %}}
   1. Port-forward the gateway proxy on port 8443. 
      ```sh
      kubectl port-forward deployment/http -n gloo-system 8443:8443
      ```
   
   2. Send an HTTPS request to the httpbin app. 
      ```sh
      curl -vik --connect-to redirect.example:443:localhost:8443 https://redirect.example/status/200
      ```
   {{% /tab %}}
   {{< /tabs >}}
   
   Example output: 
   ```
   * ALPN: curl offers h2,http/1.1
   * (304) (OUT), TLS handshake, Client hello (1):
   * (304) (IN), TLS handshake, Server hello (2):
   * (304) (IN), TLS handshake, Unknown (8):
   * (304) (IN), TLS handshake, Certificate (11):
   * (304) (IN), TLS handshake, CERT verify (15):
   * (304) (IN), TLS handshake, Finished (20):
   * (304) (OUT), TLS handshake, Finished (20):
   * SSL connection using TLSv1.3 / AEAD-CHACHA20-POLY1305-SHA256 / [blank] / UNDEF
   * ALPN: server did not agree on a protocol. Uses default.
   * Server certificate:
   *  subject: CN=*; O=any domain
   *  start date: Mar 14 13:37:22 2025 GMT
   *  expire date: Mar 14 13:37:22 2026 GMT
   *  issuer: O=any domain; CN=*
   *  SSL certificate verify result: unable to get local issuer certificate (20), continuing anyway.
   * using HTTP/1.x
   > GET /status/200 HTTP/1.1
   > Host: redirect.example
   > User-Agent: curl/8.7.1
   > Accept: */*
   > 
   * Request completely sent off
   < HTTP/1.1 200 OK
   HTTP/1.1 200 OK
   ...
   ```


## Cleanup

{{< reuse "docs/snippets/cleanup.md" >}}
  
1. Remove the HTTPRoutes for the httpbin app and the Kubernetes secret that holds the TLS certificate and key.
   ```sh
   kubectl delete httproute,secret -A -l gateway=https
   ```

2. Remove the example_certs directory that stores your TLS credentials.
   ```sh
   rm -rf example_certs
   ```
  
3. Remove the HTTPS listener from your Gateway. 
   ```yaml
   kubectl apply -f- <<EOF                                                          
   kind: Gateway
   apiVersion: gateway.networking.k8s.io/v1
   metadata:
     name: http
     namespace: {{< reuse "docs/snippets/namespace.md" >}}
   spec:
     gatewayClassName: {{< reuse "docs/snippets/gatewayclass.md" >}}
     listeners:
     - protocol: HTTP
       port: 8080
       name: http
       allowedRoutes:
         namespaces:
           from: All
   EOF
   ```