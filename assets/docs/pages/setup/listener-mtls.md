Add a [FrontendTLSConfig](https://gateway-api.sigs.k8s.io/reference/1.4/spec/#frontendtlsconfig) to a Gateway to create a mutual TLS (mTLS) listener. 

## About FrontendTLS

When configuring an mTLS listener on a Gateway, the client application and the Gateway must exchange certificates to verify their identities before a connection can be established. After a TLS connection is established, the TLS connection is terminated at the Gateway and the unencrypted HTTP traffic is forwarded to the backend destination. 

FrontendTLS supports the following configurations: 

* **Default (required)**: Create the default client certificate validation configuration for all Gateway listeners that handle HTTPS traffic. For an example, see the [Default configuration for all listeners](#default) guide. 
* **perPort (optional)**: Override the default configuration with port-specific configuration. The configuration is applied only to matching ports that handle HTTPS traffic. For all other ports that handle HTTPS traffic, the default configuration continues to apply. For an example, see the [Per port configuration](#perport) guide.

In addition, you can choose between the following validation modes: 
* **AllowValidOnly**: A connection between a client and the gateway proxy can only be established if the gateway can validate the client's TLS certificate successfully. For an example, see the [Default configuration for all listeners](#default) guide.
* **AllowInsecureFallback**: The gateway proxy can establish a TLS connection, even if the client TLS certificate could not be validated successfully. For an example, see the [Per port configuration](#perport) guide.

## About this guide

In this guide, you learn how to apply default certificate validation configuration for all HTTPS listeners on a Gateway and how to override this configuration for a specific port. You further explore secure and insecure certificate validation modes, and use TLS annotations to limit connections to clients that present certificates with a specific Subject Alt Name and certificate hash. 

Throughout this guide, you use self-signed TLS certificates for the Certificate Authority. These certificates are used to sign the TLS certificates for the gateway proxy (server) and httpbin client. 

{{< callout type="warning" >}}
Self-signed certificates are used for demonstration purposes. Do not use self-signed certificates in production environments. Instead, use certificates that are issued from a trust Certificate Authority. 
{{< /callout >}}

## Before you begin

{{< reuse "docs/snippets/cert-prereqs.md" >}}

5. Install the experimental channel of the Kubernetes Gateway API. This API is required to use the FrontendTLS configuration on a Gateway.   
   ```sh
   kubectl apply -f https://github.com/kubernetes-sigs/gateway-api/releases/download/v1.4.0/experimental-install.yaml
   ```


## Create TLS certificates 

Create self-signed TLS certificates that you use for the mutual TLS connection between your client application (`curl`) and the gateway proxy. 

{{< callout type="warning" >}}
Self-signed certificates are used for demonstration purposes. Do not use self-signed certificates in production environments. Instead, use certificates that are issued from a trust Certificate Authority. 
{{< /callout >}}

<!-- >
When generating your Envoy certificates, make sure to use encryption algorithms that are supported in Envoy. To learn more about supported algorithms that you can use for your certificates and keys, see the <a href="https://www.envoyproxy.io/docs/envoy/latest/intro/arch_overview/security/ssl#certificate-selection">Envoy documentation</a>. 
-->

1. Create the `example_certs` directory and navigate into this directory. 
   ```sh
   mkdir example_certs && cd example_certs
   ```

2. Create self-signed certificates for the Certificate Authority (CA) that you later use to sign the server and client certificates. 
   ```sh
   # Create CA private key
   openssl genrsa -out ca-key.pem 2048

   # Create CA certificate (valid for 1 year)
   openssl req -new -x509 -days 365 -key ca-key.pem -out ca-cert.pem \
     -subj "/CN=Test CA/O=Test Org"
   ```

3. Create the server certificates for the Gateway that is signed by the CA that you created in the previous step. The Gateway uses these certificates to terminate incoming TLS connections. 
   ```sh
   # Create server private key
   openssl genrsa -out server-key.pem 2048

   # Create server certificate signing request
   openssl req -new -key server-key.pem -out server.csr \
     -subj "/CN=example.com/O=Test Org"

   # Create server certificate signed by CA (valid for 1 year)
   openssl x509 -req -days 365 -in server.csr -CA ca-cert.pem -CAkey ca-key.pem \
     -CAcreateserial -out server-cert.pem \
     -extensions v3_req -extfile <(echo "[v3_req]"; echo "subjectAltName=DNS:example.com,DNS:*.example.com")
   ```

4. Store the server certificate and key in a Kubernetes secret. 
   ```yaml
   # Base64 encode server certificate and key
   SERVER_CERT=$(cat server-cert.pem | base64 -w 0)
   SERVER_KEY=$(cat server-key.pem | base64 -w 0)

   # Create the secret
   kubectl create secret tls https-cert \
     --cert=server-cert.pem \
     --key=server-key.pem \
     -n {{< reuse "docs/snippets/namespace.md" >}}
   ```

5. Store the CA certificates in a configmap. The gateway proxy later uses these certificates to validate the client certificate that is presented during the TLS handshake. 
   ```sh
   kubectl create configmap ca-cert \
     --from-file=ca.crt=ca-cert.pem \
     -n {{< reuse "docs/snippets/namespace.md" >}}
   ```

6. Create a client certificate and private key. You use these credentials later when sending a request to the gateway proxy. The client certificate is signed by the same CA that you used for the gateway proxy.
   ```sh
   # Create client private key
   openssl genrsa -out client-key.pem 2048

   # Create client certificate signing request
   openssl req -new -key client-key.pem -out client.csr \
     -subj "/CN=client.example.com/O=Test Org"

   # Create client certificate signed by CA (valid for 1 year)
   openssl x509 -req -days 365 -in client.csr -CA ca-cert.pem -CAkey ca-key.pem \
     -CAcreateserial -out client-cert.pem \
     -extensions v3_req -extfile <(echo "[v3_req]"; echo "subjectAltName=DNS:example.com,DNS:*.example.com")
   ```

## Default configuration for all listeners {#default}

1. Create a Gateway with a default frontend TLS configuration that applies to all listeners that handle HTTPS traffic. The following example configures two HTTPS listeners on the Gateway. Both listeners use the same server TLS credentials to terminate incoming HTTPS connections. The validation mode is set to `AllowValidOnly` to allow connection only if a valid certificate is presented during the TLS handshake. 
   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.networking.k8s.io/v1
   kind: Gateway
   metadata:
     name: mtls
     namespace: {{< reuse "docs/snippets/namespace.md" >}}
   spec:
     gatewayClassName: {{< reuse "docs/snippets/gatewayclass.md" >}}
     tls:
       frontend:
         default:
           validation:
             mode: AllowValidOnly
             caCertificateRefs:
               - name: ca-cert
                 kind: ConfigMap
                 group: ""
     listeners:
     - name: https-8443
       protocol: HTTPS
       port: 8443
       tls:
         mode: Terminate
         certificateRefs:
           - name: https-cert
             kind: Secret
       allowedRoutes:
         namespaces:
           from: All
     - name: https-8444
       protocol: HTTPS
       port: 8444
       tls:
         mode: Terminate
         certificateRefs:
           - name: https-cert
             kind: Secret
       allowedRoutes:
         namespaces:
           from: All
   EOF
   ```

2. Create an HTTPRoute that routes incoming traffic on the `example.com` domain to the mTLS Gateway that you created. 
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
     hostnames:
     - "example.com"
     parentRefs:
       - name: mtls
         namespace: {{< reuse "docs/snippets/namespace.md" >}}
     rules:
       - backendRefs:
           - name: httpbin
             port: 8000
   EOF
   ```

5. Get the external address of the gateway and save it in an environment variable. Note that it might take a few seconds for the gateway address to become available. 
   {{< tabs tabTotal="2" items="Cloud Provider LoadBalancer,Port-forward for local testing">}}
   {{% tab tabName="Cloud Provider LoadBalancer" %}}
   ```sh
   export INGRESS_GW_ADDRESS=$(kubectl get svc -n {{< reuse "docs/snippets/namespace.md" >}} mtls -o jsonpath="{.status.loadBalancer.ingress[0]['hostname','ip']}")
   echo $INGRESS_GW_ADDRESS   
   ```
   {{% /tab %}}
   {{% tab tabName="Port-forward for local testing" %}}
   ```sh
   kubectl port-forward deploy/mtls -n {{< reuse "docs/snippets/namespace.md" >}} 8443:8443 8444:8444
   ```
   {{% /tab %}}
   {{< /tabs >}}

6. Send a request to the httpbin app without a client certificate. Verify that the TLS handshake fails, because a TLS certificate is required to establish the connection. 
   {{< tabs tabTotal="3" items="LoadBalancer IP address,LoadBalancer hostname,Port-forward for local testing" >}}
   {{% tab tabName="LoadBalancer IP address" %}}
   ```sh
   curl -v -k --resolve "example.com:8443:${INGRESS_GW_ADDRESS}"  https://example.com:8443/get

   curl -v -k --resolve "example.com:8444:${INGRESS_GW_ADDRESS}"  https://example.com:8444/get
   ```
   {{% /tab %}}
   {{% tab tabName="LoadBalancer hostname" %}}
   ```sh
   curl -v -k --resolve "example.com:8443:$(dig +short $INGRESS_GW_ADDRESS | head -n1)"  https://example.com:8443/get

   curl -v -k --resolve "example.com:8444:$(dig +short $INGRESS_GW_ADDRESS | head -n1)"  https://example.com:8444/get
   ```

   {{% /tab %}}
   {{% tab tabName="Port-forward for local testing" %}}
   ```sh
   curl -v -k https://localhost:8443/get \
     --resolve example.com:8443:127.0.0.1 \
     -H "Host: example.com"
  
   curl -v -k https://localhost:8444/get \
     --resolve example.com:8444:127.0.0.1 \
     -H "Host: example.com"
   ```
   {{% /tab %}}
   {{< /tabs >}} 
   

   Example output: 
   ```
   * LibreSSL SSL_read: LibreSSL/3.3.6: error:1404C45C:SSL routines:ST_OK:reason(1116), errno 0
   * Failed receiving HTTP2 data: 56(Failure when receiving data from the peer)
   * Connection #0 to host localhost left intact
   curl: (56) LibreSSL SSL_read: LibreSSL/3.3.6: error:1404C45C:SSL routines:ST_OK:reason(1116), errno 0
   ```

7. Repeat the request. This time, you include the client certificate that you created earlier. 
   {{< tabs tabTotal="3" items="LoadBalancer IP address,LoadBalancer hostname,Port-forward for local testing" >}}
   {{% tab tabName="LoadBalancer IP address" %}}
   ```sh
   curl -v -k --resolve "example.com:8443:${INGRESS_GW_ADDRESS}"  https://example.com:8443/get \
     --cert client-cert.pem \
     --key client-key.pem \
     --cacert ca-cert.pem

   curl -v -k --resolve "example.com:8444:${INGRESS_GW_ADDRESS}"  https://example.com:8444/get \
     --cert client-cert.pem \
     --key client-key.pem \
     --cacert ca-cert.pem
   ```
   {{% /tab %}}
   {{% tab tabName="LoadBalancer hostname" %}}
   ```sh
   curl -v -k --resolve "example.com:8443:$(dig +short $INGRESS_GW_ADDRESS | head -n1)"  https://example.com:8443/get \
     --cert client-cert.pem \
     --key client-key.pem \
     --cacert ca-cert.pem

   curl -v -k --resolve "example.com:8444:$(dig +short $INGRESS_GW_ADDRESS | head -n1)"  https://example.com:8444/get \
     --cert client-cert.pem \
     --key client-key.pem \
     --cacert ca-cert.pem
   ```

   {{% /tab %}}
   {{% tab tabName="Port-forward for local testing" %}}
   ```sh
   curl -v -k https://localhost:8443/get \
     --resolve example.com:8443:127.0.0.1 \
     -H "Host: example.com" \
     --cert client-cert.pem \
     --key client-key.pem \
     --cacert ca-cert.pem

   curl -v -k https://localhost:8444/get \
     --resolve example.com:8444:127.0.0.1 \
     -H "Host: example.com" \
     --cert client-cert.pem \
     --key client-key.pem \
     --cacert ca-cert.pem
   ```
   {{% /tab %}}
   {{< /tabs >}} 

   Example output for port 8444: 
   ```
   * Connection #0 to host localhost left intact
   * Added example.com:8444:127.0.0.1 to DNS cache
   * Host localhost:8444 was resolved.
   * IPv6: ::1
   * IPv4: 127.0.0.1
   *   Trying [::1]:8444...
   * Connected to localhost (::1) port 8444
   * ALPN: curl offers h2,http/1.1
   * (304) (OUT), TLS handshake, Client hello (1):
   * (304) (IN), TLS handshake, Server hello (2):
   * (304) (IN), TLS handshake, Unknown (8):
   * (304) (IN), TLS handshake, Request CERT (13):
   * (304) (IN), TLS handshake, Certificate (11):
   * (304) (IN), TLS handshake, CERT verify (15):
   * (304) (IN), TLS handshake, Finished (20):
   * (304) (OUT), TLS handshake, Certificate (11):
   * (304) (OUT), TLS handshake, CERT verify (15):
   * (304) (OUT), TLS handshake, Finished (20):
   * SSL connection using TLSv1.3 / AEAD-CHACHA20-POLY1305-SHA256 / [blank] / UNDEF
   * ALPN: server accepted h2
   * Server certificate:
   *  subject: CN=example.com; O=Test Org
   *  start date: Jan 13 20:19:17 2026 GMT
   *  expire date: Jan 13 20:19:17 2027 GMT
   *  issuer: CN=Test CA; O=Test Org
   *  SSL certificate verify result: unable to get local issuer certificate (20), continuing anyway.
   * using HTTP/2
   * [HTTP/2] [1] OPENED stream for https://localhost:8444/get
   * [HTTP/2] [1] [:method: GET]
   * [HTTP/2] [1] [:scheme: https]
   * [HTTP/2] [1] [:authority: example.com]
   * [HTTP/2] [1] [:path: /get]
   * [HTTP/2] [1] [user-agent: curl/8.7.1]
   * [HTTP/2] [1] [accept: */*]
   > GET /get HTTP/2
   > Host: example.com
   > User-Agent: curl/8.7.1
   > Accept: */*

   * Request completely sent off
   < HTTP/2 200 
   < access-control-allow-credentials: true
   < access-control-allow-origin: *
   < content-type: application/json; encoding=utf-8
   < date: Tue, 13 Jan 2026 21:59:07 GMT
   < content-length: 515
   < x-envoy-upstream-service-time: 1
   < server: envoy
   ...
   ```
  

## Per port configuration {#perport}

In this example, you override the default certificate validation configuration for port 8444. 

1. Update your Gateway to add in port-specific validation configuration for port 8444. In the following example, you override the default certificate validation for port 8444. This configuration allows requests, even if an invalid certificate was presented during the TLS handshake. Port 8443 continues to only allow connections if a valid certificate is presented. 
   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.networking.k8s.io/v1
   kind: Gateway
   metadata:
     name: mtls
     namespace: {{< reuse "docs/snippets/namespace.md" >}}
   spec:
     gatewayClassName: {{< reuse "docs/snippets/gatewayclass.md" >}}
     tls:
       frontend:
         default:
           validation:
             mode: AllowValidOnly
             caCertificateRefs:
               - name: ca-cert
                 kind: ConfigMap
                 group: ""
         perPort:
           - port: 8444
             tls:
               validation:
                 mode: AllowInsecureFallback
                 caCertificateRefs:
                   - name: ca-cert
                     kind: ConfigMap
                     group: ""
     listeners:
     - name: https-8443
       protocol: HTTPS
       port: 8443
       tls:
         mode: Terminate
         certificateRefs:
           - name: https-cert
             kind: Secret
       allowedRoutes:
         namespaces:
           from: All
     - name: https-8444
       protocol: HTTPS
       port: 8444
       tls:
         mode: Terminate
         certificateRefs:
           - name: https-cert
             kind: Secret
       allowedRoutes:
         namespaces:
           from: All
   EOF
   ```

2. If you have not done so yet, get the external address of the gateway and save it in an environment variable. Note that it might take a few seconds for the gateway address to become available. 
   {{< tabs tabTotal="2" items="Cloud Provider LoadBalancer,Port-forward for local testing">}}
   {{% tab tabName="Cloud Provider LoadBalancer" %}}
   ```sh
   export INGRESS_GW_ADDRESS=$(kubectl get svc -n {{< reuse "docs/snippets/namespace.md" >}} mtls -o jsonpath="{.status.loadBalancer.ingress[0]['hostname','ip']}")
   echo $INGRESS_GW_ADDRESS   
   ```
   {{% /tab %}}
   {{% tab tabName="Port-forward for local testing" %}}
   ```sh
   kubectl port-forward deploy/mtls -n {{< reuse "docs/snippets/namespace.md" >}} 8443:8443 8444:8444
   ```
   {{% /tab %}}
   {{< /tabs >}}

3. Send a request to the httpbin app on both ports without a valid certificate. Verify that the request on port 8443 fails, because the default validation configuration does not allow to establish a connection without a valid certificate. The connection on port 8444 however is established as the port-specific validation configuration mode is set to `AllowInsecureFallback`.
   {{< tabs tabTotal="3" items="LoadBalancer IP address,LoadBalancer hostname,Port-forward for local testing" >}}
   {{% tab tabName="LoadBalancer IP address" %}}
   ```sh
   curl -v -k --resolve "example.com:8443:${INGRESS_GW_ADDRESS}"  https://example.com:8443/get

   curl -v -k --resolve "example.com:8444:${INGRESS_GW_ADDRESS}"  https://example.com:8444/get
   ```
   {{% /tab %}}
   {{% tab tabName="LoadBalancer hostname" %}}
   ```sh
   curl -v -k --resolve "example.com:8443:$(dig +short $INGRESS_GW_ADDRESS | head -n1)"  https://example.com:8443/get

   curl -v -k --resolve "example.com:8444:$(dig +short $INGRESS_GW_ADDRESS | head -n1)"  https://example.com:8444/get
   ```

   {{% /tab %}}
   {{% tab tabName="Port-forward for local testing" %}}
   ```sh
   curl -v -k https://localhost:8443/get \
     --resolve example.com:8443:127.0.0.1 \
     -H "Host: example.com"
  
   curl -v -k https://localhost:8444/get \
     --resolve example.com:8444:127.0.0.1 \
     -H "Host: example.com"
   ```
   {{% /tab %}}
   {{< /tabs >}} 

   Example output for port 8443:
   ```
   * LibreSSL SSL_read: LibreSSL/3.3.6: error:1404C45C:SSL routines:ST_OK:reason(1116), errno 0
   * Failed receiving HTTP2 data: 56(Failure when receiving data from the peer)
   * Connection #0 to host localhost left intact
   curl: (56) LibreSSL SSL_read: LibreSSL/3.3.6: error:1404C45C:SSL routines:ST_OK:reason(1116), errno 0
   ```

   Example output for port 8444: 
   ```
   ...
   * Request completely sent off
   < HTTP/2 200 
   ...
   ```

4. Repeat the request with a valid certificate. Verify that both requests succeed. 
   {{< tabs tabTotal="3" items="LoadBalancer IP address,LoadBalancer hostname,Port-forward for local testing" >}}
   {{% tab tabName="LoadBalancer IP address" %}}
   ```sh
   curl -v -k --resolve "example.com:8443:${INGRESS_GW_ADDRESS}"  https://example.com:8443/get \
     --cert client-cert.pem \
     --key client-key.pem \
     --cacert ca-cert.pem

   curl -v -k --resolve "example.com:8444:${INGRESS_GW_ADDRESS}"  https://example.com:8444/get \
     --cert client-cert.pem \
     --key client-key.pem \
     --cacert ca-cert.pem
   ```
   {{% /tab %}}
   {{% tab tabName="LoadBalancer hostname" %}}
   ```sh
   curl -v -k --resolve "example.com:8443:$(dig +short $INGRESS_GW_ADDRESS | head -n1)"  https://example.com:8443/get \
     --cert client-cert.pem \
     --key client-key.pem \
     --cacert ca-cert.pem

   curl -v -k --resolve "example.com:8444:$(dig +short $INGRESS_GW_ADDRESS | head -n1)"  https://example.com:8444/get \
     --cert client-cert.pem \
     --key client-key.pem \
     --cacert ca-cert.pem
   ```

   {{% /tab %}}
   {{% tab tabName="Port-forward for local testing" %}}
   ```sh
   curl -v -k https://localhost:8443/get \
     --resolve example.com:8443:127.0.0.1 \
     -H "Host: example.com" \
     --cert client-cert.pem \
     --key client-key.pem \
     --cacert ca-cert.pem

   curl -v -k https://localhost:8444/get \
     --resolve example.com:8444:127.0.0.1 \
     -H "Host: example.com" \
     --cert client-cert.pem \
     --key client-key.pem \
     --cacert ca-cert.pem
   ```
   {{% /tab %}}
   {{< /tabs >}}

## Additional TLS settings

You can configure your mTLS listener to limit connections to clients that present a certificate with a specific certificate hash and Subject Alternative Names. Alternatively, you can configure your listeners to enforce other TLS settings, such as a minimum or maximum TLS version, specific cipher suites, or CSDH curves. For more information, see [Additional TLS settings]({{< link-hextra path="/setup/listeners/tls-settings/" >}}). 


1. Get the certificate hash of the client certificate. 
   ```sh
   openssl x509 -in client-cert.pem -noout -fingerprint -sha256
   ```
  
   Example output: 
   ```
   sha256 Fingerprint=46:DB:0D:C2:E1:4F:0A:05:8C:4F:05:8D:77:B1:8D:7C:1A:BE:18:4F:AF:81:BF:E2:B1:CD:03:43:7F:D8:65:4B
   ```
   
2. Update port 8443 on the Gateway to allow connections only if the client certificate includes a specific hash and Subject Alt Name. 
   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.networking.k8s.io/v1
   kind: Gateway
   metadata:
     name: mtls
     namespace: {{< reuse "docs/snippets/namespace.md" >}}
   spec:
     gatewayClassName: {{< reuse "docs/snippets/gatewayclass.md" >}}
     tls:
       frontend:
         default:
           validation:
             mode: AllowValidOnly
             caCertificateRefs:
               - name: ca-cert
                 kind: ConfigMap
                 group: ""
     listeners:
     - name: https-8443
       protocol: HTTPS
       port: 8443
       tls:
         mode: Terminate
         certificateRefs:
           - name: https-cert
             kind: Secret
         options:
           kgateway.dev/verify-subject-alt-names: "example.com"
           kgateway.dev/verify-certificate-hash: "46:DB:0D:C2:E1:4F:0A:05:8C:4F:05:8D:77:B1:8D:7C:1A:BE:18:4F:AF:81:BF:E2:B1:CD:03:43:7F:D8:65:4B"
       allowedRoutes:
         namespaces:
           from: All
   EOF
   ```

   | Setting | Description | 
   | -- | -- | 
   | `kgateway.dev/verify-certificate-hash` | A comma-delimited list of the certificate hash (fingerprint) that must be present in the peer certificate that is presented during the TLS handshake.  | 
   | `kgateway.dev/verify-subject-alt-names` | A comma-delimited list of the Subject Alternative Names that must be present in the peer certificate that is presented during the TLS handshake.  |

3. Send a request to the httpbin app with your client certificate. Verify that the request succeeds. 
   {{< tabs tabTotal="3" items="LoadBalancer IP address,LoadBalancer hostname,Port-forward for local testing" >}}
   {{% tab tabName="LoadBalancer IP address" %}}
   ```sh
   curl -v -k --resolve "example.com:8443:${INGRESS_GW_ADDRESS}"  https://example.com:8443/get \
     --cert client-cert.pem \
     --key client-key.pem \
     --cacert ca-cert.pem
   ```
   {{% /tab %}}
   {{% tab tabName="LoadBalancer hostname" %}}
   ```sh
   curl -v -k --resolve "example.com:8443:$(dig +short $INGRESS_GW_ADDRESS | head -n1)"  https://example.com:8443/get \
     --cert client-cert.pem \
     --key client-key.pem \
     --cacert ca-cert.pem

   ```

   {{% /tab %}}
   {{% tab tabName="Port-forward for local testing" %}}
   ```sh
   curl -v -k https://localhost:8443/get \
     --resolve example.com:8443:127.0.0.1 \
     -H "Host: example.com" \
     --cert client-cert.pem \
     --key client-key.pem \
     --cacert ca-cert.pem
   ```
   {{% /tab %}}
   {{< /tabs >}}

   Example output: 
   ```
   * Added example.com:8443:172.18.0.10 to DNS cache
   * Hostname example.com was found in DNS cache
   *   Trying 172.18.0.10:8443...
   * Connected to example.com (172.18.0.10) port 8443
   * ALPN: curl offers h2,http/1.1
   * (304) (OUT), TLS handshake, Client hello (1):
   * (304) (IN), TLS handshake, Server hello (2):
   * (304) (IN), TLS handshake, Unknown (8):
   * (304) (IN), TLS handshake, Request CERT (13):
   * (304) (IN), TLS handshake, Certificate (11):
   * (304) (IN), TLS handshake, CERT verify (15):
   * (304) (IN), TLS handshake, Finished (20):
   * (304) (OUT), TLS handshake, Certificate (11):
   * (304) (OUT), TLS handshake, CERT verify (15):
   * (304) (OUT), TLS handshake, Finished (20):
   * SSL connection using TLSv1.3 / AEAD-CHACHA20-POLY1305-SHA256 / [blank] / UNDEF
   * ALPN: server accepted h2
   * Server certificate:
   *  subject: CN=example.com; O=Test Org
   *  start date: Jan 14 16:29:20 2026 GMT
   *  expire date: Jan 14 16:29:20 2027 GMT
   *  issuer: CN=Test CA; O=Test Org
   *  SSL certificate verify result: unable to get local issuer certificate (20), continuing anyway.
   * using HTTP/2
   * [HTTP/2] [1] OPENED stream for https://example.com:8443/get
   * [HTTP/2] [1] [:method: GET]
   * [HTTP/2] [1] [:scheme: https]
   * [HTTP/2] [1] [:authority: example.com:8443]
   * [HTTP/2] [1] [:path: /get]
   * [HTTP/2] [1] [user-agent: curl/8.7.1]
   * [HTTP/2] [1] [accept: */*]
   > GET /get HTTP/2
   > Host: example.com:8443
   > User-Agent: curl/8.7.1
   > Accept: */*
   > 
   * Request completely sent off
   < HTTP/2 200 
   ...
   ```

4. Change the annotation values in the Gateway to a value that does not exist in the client certificate. For example, you can change the Subject Alt Name to `mtls.com`.
   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.networking.k8s.io/v1
   kind: Gateway
   metadata:
     name: mtls
     namespace: {{< reuse "docs/snippets/namespace.md" >}}
   spec:
     gatewayClassName: {{< reuse "docs/snippets/gatewayclass.md" >}}
     tls:
       frontend:
         default:
           validation:
             mode: AllowValidOnly
             caCertificateRefs:
               - name: ca-cert
                 kind: ConfigMap
                 group: ""
     listeners:
     - name: https-8443
       protocol: HTTPS
       port: 8443
       tls:
         mode: Terminate
         certificateRefs:
           - name: https-cert
             kind: Secret
         options:
           kgateway.dev/verify-subject-alt-names: "mtls.com"
           kgateway.dev/verify-certificate-hash: "46:DB:0D:C2:E1:4F:0A:05:8C:4F:05:8D:77:B1:8D:7C:1A:BE:18:4F:AF:81:BF:E2:B1:CD:03:43:7F:D8:65:4B"
       allowedRoutes:
         namespaces:
           from: All
   EOF
   ```

5. Repeat the request to the httpbin app with your client certificate. Verify that the request now succeeds.
   {{< tabs tabTotal="3" items="LoadBalancer IP address,LoadBalancer hostname,Port-forward for local testing" >}}
   {{% tab tabName="LoadBalancer IP address" %}}
   ```sh
   curl -v -k --resolve "example.com:8443:${INGRESS_GW_ADDRESS}"  https://example.com:8443/get \
     --cert client-cert.pem \
     --key client-key.pem \
     --cacert ca-cert.pem
   ```
   {{% /tab %}}
   {{% tab tabName="LoadBalancer hostname" %}}
   ```sh
   curl -v -k --resolve "example.com:8443:$(dig +short $INGRESS_GW_ADDRESS | head -n1)"  https://example.com:8443/get \
     --cert client-cert.pem \
     --key client-key.pem \
     --cacert ca-cert.pem

   ```

   {{% /tab %}}
   {{% tab tabName="Port-forward for local testing" %}}
   ```sh
   curl -v -k https://localhost:8443/get \
     --resolve example.com:8443:127.0.0.1 \
     -H "Host: example.com" \
     --cert client-cert.pem \
     --key client-key.pem \
     --cacert ca-cert.pem
   ```
   {{% /tab %}}
   {{< /tabs >}}

   Example output:
   ```
   * LibreSSL SSL_read: LibreSSL/3.3.6: error:1404C45C:SSL routines:ST_OK:reason(1116), errno 0
   * Failed receiving HTTP2 data: 56(Failure when receiving data from the peer)
   * Connection #0 to host localhost left intact
   curl: (56) LibreSSL SSL_read: LibreSSL/3.3.6: error:1404C45C:SSL routines:ST_OK:reason(1116), errno 0
   ```


   
## Cleanup

{{< reuse "docs/snippets/cleanup.md" >}}

```sh
kubectl delete httproute httpbin-https -n httpbin
kubectl delete gateway mtls -n {{< reuse "docs/snippets/namespace.md" >}}
kubectl delete secret https-cert -n {{< reuse "docs/snippets/namespace.md" >}}
kubectl delete configmap ca-cert -n {{< reuse "docs/snippets/namespace.md" >}}
rm -rf ../example_certs
```
   