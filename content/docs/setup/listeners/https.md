---
title: HTTPS listeners
weight: 20
---

Create an HTTPS listener on your API gateway. Then, your API gateway listens for secured HTTPS traffic on the specified port and hostname that you configure. 

## Before you begin

1. Set up {{< reuse "docs/snippets/product-name.md" >}} by following the [Quick start](/docs/quickstart/) or [Installation](/docs/operations/install/) guides.

2. [Deploy the httpbin sample app](/docs/operations/sample-app/).

3. Make sure that you have the OpenSSL version of `openssl`, not LibreSSL. The `openssl` version must be at least 1.1.
   1. Check the `openssl` version that is installed. If you see LibreSSL in the output, continue to the next step.
      ```sh
      openssl version
      ```
   2. Install the OpenSSL version (not LibreSSL). For example, you might use Homebrew.
      ```sh
      brew install openssl
      ```
      
   3. Review the output of the OpenSSL installation for the path of the binary file. You can choose to export the binary to your path, or call the entire path whenever the following steps use an openssl command.
      - For example, openssl might be installed along the following path: `/usr/local/opt/openssl@3/bin/`
      - To run commands, you can append the path so that your terminal uses this installed version of OpenSSL, and not the default LibreSSL. `/usr/local/opt/openssl@3/bin/openssl req -new -newkey rsa:4096 -x509 -sha256 -days 3650...`

## Create a TLS certificate

{{< reuse "docs/snippets/listeners-https-create-cert.md" >}}

## Set up an HTTPS listener

1. Create a gateway resource and configure an HTTPS listener. 
   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.networking.k8s.io/v1
   kind: Gateway
   metadata:
     name: https
     namespace: {{< reuse "docs/snippets/ns-system.md" >}}
     labels:
       gateway: https
   spec:
     gatewayClassName: kgateway
     listeners:
       - name: https
         port: 443
         protocol: HTTPS
         hostname: https.example.com
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

   |Setting|Description|
   |--|--|
   |`spec.gatewayClassName`|The name of the Kubernetes gateway class that you want to use to configure the gateway. When you set up {{< reuse "docs/snippets/product-name.md" >}}, a default gateway class is set up for you. |
   |`spec.listeners`|Configure the listeners for this gateway. In this example, you configure an HTTPS gateway that listens for incoming traffic on port 443. |
   |`spec.listeners.tls.mode`|The TLS mode that you want to use for incoming requests. In this example, HTTPS requests are terminated at the gateway and the unecrypted request is forwarded to the service in the cluster. |
   |`spec.listeners.tls.certificateRefs`|The Kubernetes secret that holds the TLS certificate and key for the gateway. The gateway uses these credentials to establish the TLS connection with a client, and to decrypt incoming HTTPS requests.|

2. Verify that the status of the gateway shows `ACCEPTED`. 
   ```sh
   kubectl get gateway/https -n {{< reuse "docs/snippets/ns-system.md" >}} -o yaml
   ```

3. Create an HTTP route for the httpbin app and add it to the HTTPS gateway that you created. 
   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.networking.k8s.io/v1
   kind: HTTPRoute
   metadata:
     name: httpbin-https
     namespace: httpbin
     labels:
       example: httpbin-route
       gateway: https
   spec:
     parentRefs:
       - name: https
         namespace: {{< reuse "docs/snippets/ns-system.md" >}}
     rules:
       - backendRefs:
           - name: httpbin
             port: 8000
   EOF
   ```

4. Verify that the HTTP route is applied successfully. 
   ```sh
   kubectl get httproute/httpbin-https -n httpbin -o yaml
   ```

5. Get the external address of the gateway and save it in an environment variable. Note that it might take a few seconds for the gateway address to become available. 
   {{< tabs items="Cloud Provider LoadBalancer,Port-forward for local testing" >}}
   {{% tab %}}
   ```sh
   export INGRESS_GW_ADDRESS=$(kubectl get svc -n {{< reuse "docs/snippets/ns-system.md" >}} https -o jsonpath="{.status.loadBalancer.ingress[0]['hostname','ip']}")
   echo $INGRESS_GW_ADDRESS   
   ```
   {{% /tab %}}
   {{% tab %}}
   ```sh
   kubectl port-forward svc/https -n {{< reuse "docs/snippets/ns-system.md" >}} 8443:443
   ```
   {{% /tab %}}
   {{< /tabs >}}

6. Send a request to the httpbin app and verify that you see the TLS handshake and you get back a 200 HTTP response code. 
   {{< tabs items="Cloud Provider LoadBalancer,Port-forward for local testing" >}}
   {{% tab %}}
   ```sh
   curl -vik --resolve "https.example.com:443:${INGRESS_GW_ADDRESS}" https://https.example.com:443/status/200
   ```
   {{% /tab %}}
   {{% tab %}}
   ```sh
   curl -vik --connect-to https.example.com:443:localhost:8443 https://https.example.com:443/status/200
   ```
   {{% /tab %}}
   {{< /tabs >}}

   Example output: 
   ```
   * ALPN, offering h2
   * ALPN, offering http/1.1
   * successfully set certificate verify locations:
   *  CAfile: /etc/ssl/cert.pem
   *  CApath: none
   * TLSv1.2 (OUT), TLS handshake, Client hello (1):
   * TLSv1.2 (IN), TLS handshake, Server hello (2):
   * TLSv1.2 (IN), TLS handshake, Certificate (11):
   * TLSv1.2 (IN), TLS handshake, Server key exchange (12):
   * TLSv1.2 (IN), TLS handshake, Server finished (14):
   * TLSv1.2 (OUT), TLS handshake, Client key exchange (16):
   * TLSv1.2 (OUT), TLS change cipher, Change cipher spec (1):
   * TLSv1.2 (OUT), TLS handshake, Finished (20):
   * TLSv1.2 (IN), TLS change cipher, Change cipher spec (1):
   * TLSv1.2 (IN), TLS handshake, Finished (20):
   * SSL connection using TLSv1.2 / ECDHE-RSA-CHACHA20-POLY1305
   * ALPN, server accepted to use h2
   * Server certificate:
   *  subject: CN=*; O=gateway
   *  start date: Nov  5 01:54:04 2023 GMT
   *  expire date: Nov  2 01:54:04 2033 GMT
   *  issuer: CN=*; O=root
   *  SSL certificate verify result: unable to get local issuer certificate (20), continuing anyway.
   * Using HTTP2, server supports multi-use
   * Connection state changed (HTTP/2 confirmed)
   * Copying HTTP/2 data in stream buffer to connection buffer after upgrade: len=0
   * Using Stream ID: 1 (easy handle 0x15200e800)
   > GET /status/200 HTTP/2
   > Host: https.example.com
   > user-agent: curl/7.77.0
   > accept: */*
   > 
   *  Connection state changed (MAX_CONCURRENT_STREAMS == 2147483647)!
   < HTTP/2 200 
   HTTP/2 200 
   ...
   ```

## Cleanup

You can optionally remove the resources that you created as part of this guide. 

1. Remove the HTTP route for the httpbin app, the HTTPS gateway, and the Kubernetes secret that holds the TLS certificate and key.
   ```sh
   kubectl delete httproute,gateway,secret -A -l gateway=https
   ```

2. Remove the `example_certs` directory that stores your TLS credentials. 
   ```sh
   rm -rf example_certs
   ```