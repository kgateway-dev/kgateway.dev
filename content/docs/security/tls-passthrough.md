---
title: TLS passthrough
weight: 10
description: Set up a TLS listener on the gateway that serves one or more hosts and passes TLS traffic through to a destination.
---

Set up a TLS listener on the gateway that serves one or more hosts and passes TLS traffic through to a destination. Because TLS traffic is not terminated at the gateway, the destination must be capable of handling incoming TLS traffic.

## Before you begin

{{< reuse "docs/snippets/cert-prereqs.md" >}}

## Deploy an NGINX server that is configured for HTTPS traffic

Deploy a sample NGINX server and configure the server for HTTPS traffic. You use this server to try out the client TLS policy later.

1. Create a root certificate for the `example.com` domain. You use this certificate to sign the certificate for your NGINX service later. 
   ```shell
   mkdir example_certs
   openssl req -x509 -sha256 -nodes -days 365 -newkey rsa:2048 -subj '/O=example Inc./CN=example.com' -keyout example_certs/example.com.key -out example_certs/example.com.crt
   ```
   
2. Create a server certificate and private key for the `nginx.example.com` domain. 
   ```
   openssl req -out example_certs/nginx.example.com.csr -newkey rsa:2048 -nodes -keyout example_certs/nginx.example.com.key -subj "/CN=nginx.example.com/O=some organization"
   openssl x509 -req -sha256 -days 365 -CA example_certs/example.com.crt -CAkey example_certs/example.com.key -set_serial 0 -in example_certs/nginx.example.com.csr -out example_certs/nginx.example.com.crt
   ```

3. Create a secret that stores the certificate and key for the NGINX server. 
   ```shell
   kubectl create secret tls nginx-server-certs \
    --key example_certs/nginx.example.com.key \
    --cert example_certs/nginx.example.com.crt
   ```
   
5. Prepare your NGINX configuration. The following example configures NGINX for HTTPS traffic with the certificate that you created earlier.
   ```shell
   cat <<\EOF > ./nginx.conf
   events {
   }

   http {
     log_format main '$remote_addr - $remote_user [$time_local]  $status '
     '"$request" $body_bytes_sent "$http_referer" '
     '"$http_user_agent" "$http_x_forwarded_for"';
     access_log /var/log/nginx/access.log main;
     error_log  /var/log/nginx/error.log;

     server {
       listen 443 ssl;

       root /usr/share/nginx/html;
       index index.html;

       server_name nginx.example.com;
       ssl_certificate /etc/nginx-server-certs/tls.crt;
       ssl_certificate_key /etc/nginx-server-certs/tls.key;
     }
   }
   EOF
   ```
   
6. Store the NGINX configuration in a configmap. 
   ```shell
   kubectl create configmap nginx-configmap --from-file=nginx.conf=./nginx.conf
   ```

7. Deploy the NGINX server. 
   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: v1
   kind: Service
   metadata:
     name: my-nginx
     labels:
       run: my-nginx
   spec:
     ports:
     - port: 443
       protocol: TCP
     selector:
       run: my-nginx
   ---
   apiVersion: apps/v1
   kind: Deployment
   metadata:
     name: my-nginx
   spec:
     selector:
       matchLabels:
         run: my-nginx
     replicas: 1
     template:
       metadata:
         labels:
           run: my-nginx
           sidecar.istio.io/inject: "true"
       spec:
         containers:
         - name: my-nginx
           image: nginx
           ports:
           - containerPort: 443
           volumeMounts:
           - name: nginx-config
             mountPath: /etc/nginx
             readOnly: true
           - name: nginx-server-certs
             mountPath: /etc/nginx-server-certs
             readOnly: true
         volumes:
         - name: nginx-config
           configMap:
             name: nginx-configmap
         - name: nginx-server-certs
           secret:
             secretName: nginx-server-certs
   EOF
   ```

## Set up TLS passthrough 

To route TLS traffic to the NGINX server directly without terminating the TLS connection at the gateway, you create a Gateway and configure it for TLS passthrough.

1. Install the experimental channel of the Kubernetes Gateway API so that you can use TLSRoutes.
   ```sh
   kubectl apply -f https://github.com/kubernetes-sigs/gateway-api/releases/download/v1.2.1/experimental-install.yaml
   ```

1. Create a Gateway that passes through incoming TLS requests for the `nginx.example.com` domain. 
   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.networking.k8s.io/v1
   kind: Gateway
   metadata:
     name: tls-passthrough
     namespace: {{< reuse "docs/snippets/ns-system.md" >}}
   spec:
     gatewayClassName: {{< reuse "docs/snippets/product-name.md" >}}
     listeners:
     - name: tls
       protocol: TLS
       hostname: "nginx.example.com"
       tls:
         mode: Passthrough
       port: 8443
       allowedRoutes:
         namespaces:
           from: All
   EOF
   ```

2. Create a TLSRoute resource that forwards incoming TLS traffic to the nginx server. 
   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.networking.k8s.io/v1alpha2
   kind: TLSRoute
   metadata:
     name: tlsroute
     namespace: default
   spec:
     parentRefs:
       - name: tls-passthrough
     rules:
       - backendRefs:
           - group: ""
             kind: Service
             name: my-nginx
             port: 443
   EOF
   ```

3. Get the IP address of your ingress gateway. 
   ```
   export INGRESS_GW_ADDRESS=$(kubectl get svc -n kgateway-system tls-passthrough -o jsonpath="{.status.loadBalancer.ingress[0]['hostname','ip']}")
   echo $INGRESS_GW_ADDRESS  
   ```
   
4. Send a request to the `nginx.example.com` domain and verify that you get back a 200 HTTP response code from your NGINX server. Because NGINX accepts incoming TLS traffic only, the 200 HTTP response code proves that TLS traffic was not terminated at the gateway. In addition, you can verify that you get back the server certificate that you configured your NGINX server with in the beginning. 
   ```shell
   curl -vik --resolve "nginx.example.com:443:${INGRESS_GW_ADDRESS}" --cacert example_certs/example.com.crt https://nginx.example.com:443/
   ```
   
   Example output: 
   ```
   Added nginx.example.com:443:34.XXX.XXX.XXX to DNS cache
   * Hostname nginx.example.com was found in DNS cache
   *   Trying 34.XXX.XXX.XXX:443...
   * Connected to nginx.example.com (34.XXX.XXX.XXX) port 443 (#0)
   * ALPN, offering h2
   * ALPN, offering http/1.1
   * successfully set certificate verify locations:
   *  CAfile: example_certs/example.com.crt
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
   * ALPN, server accepted to use http/1.1
   * Server certificate:
   *  subject: CN=nginx.example.com; O=some organization
   *  start date: Apr  3 17:54:04 2023 GMT
   *  expire date: Apr  2 17:54:04 2024 GMT
   *  common name: nginx.example.com (matched)
   *  issuer: O=example Inc.; CN=example.com
   *  SSL certificate verify ok.
   > GET / HTTP/1.1
   > Host: nginx.example.com
   > User-Agent: curl/7.77.0
   > Accept: */*
   > 
   * Mark bundle as not supporting multiuse
   < HTTP/1.1 200 OK
   HTTP/1.1 200 OK
   < Server: nginx/1.23.4
   Server: nginx/1.23.4
   < Date: Mon, 03 Apr 2023 18:14:42 GMT
   Date: Mon, 03 Apr 2023 18:14:42 GMT
   < Content-Type: text/html
   Content-Type: text/html
   < Content-Length: 615
   Content-Length: 615
   < Last-Modified: Tue, 28 Mar 2023 15:01:54 GMT
   Last-Modified: Tue, 28 Mar 2023 15:01:54 GMT
   < Connection: keep-alive
   Connection: keep-alive
   < ETag: "64230162-267"
   ETag: "64230162-267"
   < Accept-Ranges: bytes
   Accept-Ranges: bytes

   < 
   <!DOCTYPE html>
   <html>
   <head>
   <title>Welcome to nginx!</title>
   ...
   ```

## Cleanup

{{< reuse "docs/snippets/cleanup.md" >}}

```shell
rm -r example_certs
rm nginx.conf
kubectl delete configmap nginx-configmap
kubectl delete routetable tls-route
kubectl delete virtualgateway istio-ingressgateway
kubectl delete deployment my-nginx
kubectl delete service my-nginx
kubectl delete secret nginx-server-certs
```




