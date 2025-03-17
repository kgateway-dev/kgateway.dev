---
title: Backend TLS
weight: 10
description: Configure TLS to terminate for a specific backend workload. 
---

When you configure an [HTTPS listener](/docs/setup/listeners/https), the Gateway terminates the TLS connection and decrypts the traffic. The Gateway then routes the decrypted traffic to the backend service.

However, you might have a specific backend workload that uses its own TLS certificate. In this case, you can terminate the TLS connection at the backend service by using the {{< reuse "docs/snippets/k8s-gateway-api-name.md" >}} BackendTLSPolicy. For more information, see the [{{< reuse "docs/snippets/k8s-gateway-api-name.md" >}} docs](https://gateway-api.sigs.k8s.io/api-types/backendtlspolicy/).

## Before you begin

{{< reuse "docs/snippets/prereq.md" >}}

## Create a TLS certificate {#tls-certs}

The following steps create a TLS certificate for the sample httpbin workload.

1. Create a directory to store your TLS credentials in. 
   
   ```sh
   mkdir example_certs
   ```

2. Create a self-signed root certificate. The following command creates a root certificate that is valid for a year and can serve any hostname. You use this certificate to sign the server certificate for the httpbin workload later. For other command options, see the [OpenSSL docs](https://www.openssl.org/docs/manmaster/man1/openssl-req.html).
   
   ```sh
   # root cert
   openssl req -x509 -sha256 -nodes -days 365 -newkey rsa:2048 -subj '/O=any domain/CN=*' -keyout example_certs/root.key -out example_certs/root.crt
   ```

3. Use the root certificate to sign the httpbin workload certificate.
   
   ```sh
   openssl req -out example_certs/httpbin.csr -newkey rsa:2048 -nodes -keyout example_certs/httpbin.key -subj "/CN=*/O=any domain"
   openssl x509 -req -sha256 -days 365 -CA example_certs/root.crt -CAkey example_certs/root.key -set_serial 0 -in example_certs/httpbin.csr -out example_certs/httpbin.crt
   ```

4. Create a Kubernetes Secret to store your server TLS certificate. You create the secret in the same cluster and namespace that the httpbin workload is deployed to.
   
   ```sh
   kubectl create secret tls -n httpbin httpbin \
     --key example_certs/httpbin.key \
     --cert example_certs/httpbin.crt
   kubectl label secret httpbin app=httpbin --namespace httpbin
   ```

5. Create a Kubernetes ConfigMap to store the root certificate. Later, you refer to this ConfigMap to validate the BackendTLSPolicy.

   ConfigMap:

   ```sh
   kubectl create configmap -n httpbin httpbin-root-ca \
     --from-file=ca.crt=example_certs/root.crt
   kubectl label configmap httpbin-root-ca app=httpbin --namespace httpbin
   ```

   Secret:
   ```
   kubectl create secret generic httpbin-root-ca \
     --from-file=ca.crt=example_certs/root.crt \
     -n httpbin
   kubectl label secret httpbin-root-ca app=httpbin --namespace httpbin
   ```

## Add the TLS certificate to your backend workload {#add-tls-cert}

1. Get the configuration of the `httpbin` sample app.

   ```shell
   wget -0 httpbin-tls.yaml https://raw.githubusercontent.com/kgateway-dev/kgateway/refs/heads/main/examples/httpbin.yaml
   ```

2. Open the `httpbin-tls.yaml` file and update the Deployment container spec to mount the TLS certificate, such as with the following example:

   ```yaml
   spec:
     serviceAccountName: httpbin
     containers:
       - image: docker.io/mccutchen/go-httpbin:v2.6.0
         imagePullPolicy: IfNotPresent
         name: httpbin
         command: [ go-httpbin ]
         args:
           - "-port"
           - "8080"
           - "-max-duration"
           - "600s" # override default 10s
         ports:
           - containerPort: 8080
         volumeMounts:
           - name: tls-cert
             mountPath: "/etc/tls"
             readOnly: true
       - name: curl
         image: curlimages/curl:7.83.1
         resources:
           requests:
             cpu: "100m"
           limits:
             cpu: "200m"
         imagePullPolicy: IfNotPresent
         command:
           - "tail"
           - "-f"
           - "/dev/null"
     volumes:
       - name: tls-cert
         secret:
           secretName: httpbin
           optional: false
   ```

3. Apply the updated configuration to your cluster.

   ```shell
   kubectl apply -f httpbin-tls.yaml
   ```

4. Verify that the `httpbin` sample app is running.

   ```shell
   kubectl get pods -n httpbin
   ```

   Example output:

   ```
   NAME                     READY   STATUS    RESTARTS   AGE
   httpbin-569d948984-42424   2/2     Running   0          10s
   ```
   
## Create a BackendTLSPolicy {#create-backend-tls-policy}

Create the BackendTLSPolicy for the httpbin workload. For more information, see the [{{< reuse "docs/snippets/k8s-gateway-api-name.md" >}} docs](https://gateway-api.sigs.k8s.io/api-types/backendtlspolicy/).

1. Create the BackendTLSPolicy.

   ```yaml
   kubectl apply -f - <<EOF
   apiVersion: gateway.networking.k8s.io/v1alpha3
   kind: BackendTLSPolicy
   metadata:
     name: httpbin-backend-tls
     namespace: httpbin
     labels:
       app: httpbin
   spec:
     targetRefs:
     - group: ''
       kind: Service
       name: httpbin
     validation:
       caCertificateRefs:
       - name: httpbin-root-ca
         group: ''
         kind: Secret
       hostname: www.example.com
   EOF
   ```

2. Get the external address of the gateway and save it in an environment variable. Note that it might take a few seconds for the gateway address to become available. 
   {{< tabs items="Cloud Provider LoadBalancer,Port-forward for local testing" >}}
   {{% tab %}}
   ```sh
   export INGRESS_GW_ADDRESS=$(kubectl get svc -n {{< reuse "docs/snippets/ns-system.md" >}} https -o jsonpath="{.status.loadBalancer.ingress[0]['hostname','ip']}")
   echo $INGRESS_GW_ADDRESS   
   ```
   {{% /tab %}}
   {{% tab %}}
   ```sh
   kubectl port-forward svc/https -n {{< reuse "docs/snippets/ns-system.md" >}} 8080:8080
   ```
   {{% /tab %}}
   {{< /tabs >}}

3. Send a request to the httpbin app and verify that you see the TLS handshake and you get back a 200 HTTP response code. 
   {{< tabs items="Cloud Provider LoadBalancer,Port-forward for local testing" >}}
   {{% tab %}}
   ```sh
   curl -vik https://$INGRESS_GW_ADDRESS:8080/headers -H "host: www.example.com:8080"
   ```
   {{% /tab %}}
   {{% tab %}}
   ```sh
   curl -vik https://localhost:8080/headers -H "host: www.example.com"
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

{{< reuse "docs/snippets/cleanup.md" >}}

1. Update the httpbin Deployment to remove the TLS certificate.

   ```yaml
   kubectl apply -f https://raw.githubusercontent.com/kgateway-dev/kgateway/refs/heads/main/examples/httpbin.yaml
   ```
   
2. Remove the HTTP route for the httpbin app, the HTTPS gateway, and the Kubernetes secret that holds the TLS certificate and key.
   ```sh
   kubectl delete backendtlspolicy,secret,configmap -A -l app=httpbin
   ```

3. Remove the `example_certs` directory that stores your TLS credentials. 
   ```sh
   rm -rf example_certs
   ```