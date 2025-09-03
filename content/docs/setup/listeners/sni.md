---
title: SNI
weight: 10
description: 
---

Serve multiple hosts on the same HTTPS listener.

## About SNI 

Each host comes with its own TLS certificates that the Gateway uses to authenticate and authorize client requests.

Serving multiple hosts on a single listener is also referred to as Server Name Indication (SNI) routing. SNI is an extension to the TLS protocol and allows clients to indicate which hostname they want to connect to at the start of the TLS handshake. After the HTTPS/TLS traffic is accepted at the gateway, the TLS connection is terminated, and the unencrypted HTTP/TCP request is forwarded to the destination.

## About this guide

In this guide, you learn how to set up an HTTPS Gateway that serves two different domains, `httpbin.example.com` and `petstore.example.com` on the same port 443. When sending a request to the Gateway, you indicate the hostname you want to connect to. Based on the selected hostname, the Gateway presents the hostname-specific certificate. 

{{< reuse-image src="img/sni-listener.svg" width="700px">}}
{{< reuse-image-dark srcDark="img/sni-listener-dark.svg" width="700px" >}}

## Before you begin

{{< reuse "docs/snippets/cert-prereqs.md" >}}

## Deploy sample apps 

Deploy the Petstore sample app. This app is used alongside the httpbin app from the [Get started](/docs/quickstart) guide to demonstrate the SNI routing capabilities.

1. Deploy the Petstore app.
   ```sh
   kubectl apply -f https://raw.githubusercontent.com/solo-io/gloo/v1.16.x/example/petstore/petstore.yaml
   ```
   
   Example output:
   ```console
   deployment.apps/petstore created
   service/petstore created
   ```
   
2. Verify that the Petstore app is up and running.
   ```sh
   kubectl get pods
   ```
   
   Example output:
   ```
   NAME                        READY   STATUS    RESTARTS   AGE
   petstore-66cddd5bb4-x7vdd   1/1     Running   0          26s
   ```
   
## Set up TLS certificates for multiple domains 

Create TLS certificates for the `httpbin.example.com` and `petstore.example.com` domains that are signed by a self-signed root CA.

{{< callout type="warning" >}}
Self-signed certificates are used for demonstration purposes. Do not use self-signed certificates in production environments. Instead, use certificates that are issued from a trusted Certificate Authority.
{{< /callout >}}

{{< callout type="info" >}}
When generating your Envoy certificates, make sure to use encryption algorithms that are supported in Envoy. To learn more about supported algorithms that you can use for your certificates and keys, see the <a href="https://www.envoyproxy.io/docs/envoy/latest/intro/arch_overview/security/ssl#certificate-selection">Envoy documentation</a>. 
{{< /callout >}}
   
1. Create a root certificate and private key to sign the certificates for your services. 
   ```shell
   mkdir example_certs
   openssl req -x509 -sha256 -nodes -days 365 -newkey rsa:2048 -subj '/O=example Inc./CN=example.com' -keyout example_certs/example.com.key -out example_certs/example.com.crt
   ```
   
2. Generate a TLS certificate and key for the `httpbin.example.com` domain. 
   ```shell
   openssl req -out example_certs/httpbin.example.com.csr -newkey rsa:2048 -nodes -keyout example_certs/httpbin.example.com.key -subj "/CN=httpbin.example.com/O=httpbin organization"
   openssl x509 -req -sha256 -days 365 -CA example_certs/example.com.crt -CAkey example_certs/example.com.key -set_serial 0 -in example_certs/httpbin.example.com.csr -out example_certs/httpbin.example.com.crt
   ```

3. Generate a TLS certificate and key for the `petstore.example.com` domain. 
   ```shell
   openssl req -out example_certs/petstore.example.com.csr -newkey rsa:2048 -nodes -keyout example_certs/petstore.example.com.key -subj "/CN=petstore.example.com/O=petstore organization"
   openssl x509 -req -sha256 -days 365 -CA example_certs/example.com.crt -CAkey example_certs/example.com.key -set_serial 1 -in example_certs/petstore.example.com.csr -out example_certs/petstore.example.com.crt
   ```

4. Verify that you have the required certificates and keys. 
   ```shell
   ls example_cert*
   ```
   
   Example output: 
   ```
   petstore.example.com.crt petstore.example.com.key  example.com.crt          httpbin.example.com.crt  httpbin.example.com.key
   petstore.example.com.csr example.com.key          httpbin.example.com.csr
   ```
    
6. Store the credentials for the `httpbin.example.com` domain in a Kubernetes secret. 
   ```shell
   kubectl create -n {{< reuse "docs/snippets/namespace.md" >}} secret tls httpbin-credential \
     --key=example_certs/httpbin.example.com.key \
     --cert=example_certs/httpbin.example.com.crt
   ```

7. Store the credentials for the `petstore.example.com` domain in a Kubernetes secret. 
   ```shell
   kubectl create -n {{< reuse "docs/snippets/namespace.md" >}} secret tls petstore-credential \
     --key=example_certs/petstore.example.com.key \
     --cert=example_certs/petstore.example.com.crt
   ```
    
## Set up SNI routing

Set up an SNI Gateway that serves multiple hosts on the same port. 

If you plan to set up your listener as part of a ListenerSet, keep the following considerations in mind. For more information, see [ListenerSets (experimental)](/docs/setup/listeners/overview/#listenersets).
* {{< reuse "docs/versions/warn-2-1-only.md" >}} 
* You must install the experimental channel of the Kubernetes Gateway API at version 1.3 or later.

1. Create an SNI Gateway. The Gateway defines two hosts on the same HTTPS listener. Each host is configured with the host-specific TLS certificate that you set up earlier. {{< reuse "docs/snippets/agw-gatewayclass-choice.md" >}}

   {{< tabs items="Gateway listeners,ListenerSet (experimental)" tabTotal="2" >}}
   {{% tab tabName="Gateway listeners" %}}

   ```yaml
   kubectl apply -f- <<EOF
   kind: Gateway
   apiVersion: gateway.networking.k8s.io/v1
   metadata:
     name: sni
     namespace: {{< reuse "docs/snippets/namespace.md" >}}
   spec:
     gatewayClassName: {{< reuse "docs/snippets/gatewayclass.md" >}}
     listeners:
       - protocol: HTTPS
         port: 443
         name: httpbin
         hostname: "httpbin.example.com"
         tls:
           mode: Terminate
           certificateRefs:
             - name: httpbin-credential
               kind: Secret
         allowedRoutes:
           namespaces:
             from: All
       - protocol: HTTPS
         port: 443
         name: petstore
         hostname: "petstore.example.com"
         tls:
           mode: Terminate
           certificateRefs:
             - name: petstore-credential
               kind: Secret
         allowedRoutes:
           namespaces:
             from: All
   EOF
   ```

   {{< reuse "docs/snippets/review-table.md" >}}

   |Setting|Description|
   |--|--|
   |`spec.gatewayClassName`| The name of the Kubernetes GatewayClass that you want to use to configure the Gateway. When you set up {{< reuse "docs/snippets/kgateway.md" >}}, a default GatewayClass is set up for you. {{< reuse "docs/snippets/agw-gatewayclass-choice.md" >}}|
   |`spec.listeners`|Configure the listeners for this Gateway. In this example, you configure two HTTPS listeners. One listener is for the httpbin app and the other is for the petstore app. Each listener refers to a secret that holds the TLS certificate and key for the hostname that the listener is configured for. |
   |`spec.listeners.tls.mode`|The TLS mode that you want to use for incoming requests. In this example, HTTPS requests are terminated at the Gateway and the unencrypted request is forwarded to the service in the cluster. |
   |`spec.listeners.tls.certificateRefs`|The Kubernetes secret that holds the TLS certificate and key for the Gateway. The Gateway uses these credentials to establish the TLS connection with a client, and to decrypt incoming HTTPS requests.|

   {{% /tab %}}
   {{% tab tabName="ListenerSet (experimental)" %}}
   
   1. Create a Gateway that enables the attachment of ListenerSets.

      ```yaml
      kubectl apply -f- <<EOF
      apiVersion: gateway.networking.k8s.io/v1
      kind: Gateway
      metadata:
        name: sni
        namespace: {{< reuse "docs/snippets/namespace.md" >}}
      spec:
        gatewayClassName: {{< reuse "docs/snippets/gatewayclass.md" >}}
        allowedListeners:
          namespaces:
            from: All
        listeners:
        - protocol: HTTP
          port: 80
          name: http
          allowedRoutes:
            namespaces:
              from: All     
      EOF
      ```
      
      {{< reuse "docs/snippets/review-table.md" >}}
      
      |Setting|Description|
      |--|--|
      |`spec.gatewayClassName`| The name of the Kubernetes GatewayClass that you want to use to configure the Gateway. When you set up {{< reuse "docs/snippets/kgateway.md" >}}, a default GatewayClass is set up for you. {{< reuse "docs/snippets/agw-gatewayclass-choice.md" >}}|
      |`spec.allowedListeners`|Enable the attachment of ListenerSets to this Gateway. The example allows listeners from any namespace, which is helpful in multitenant environments. You can also limit the allowed listeners. To limit to listeners in the same namespace as the Gateway, set this value to `Same`. To limit to listeners with a particular label, set this value to `Selector`. |
      | `spec.listeners` | {{< reuse "docs/snippets/generic-listener.md" >}} In this example, the generic listener is configured on HTTP port 80, which differs from the HTTPS port 443 in the ListenerSet that you create later. |
   
   2. Create a ListenerSet that configures an HTTPS listener for each app that the Gateway serves.

      ```yaml
      kubectl apply -f- <<EOF
      apiVersion: gateway.networking.x-k8s.io/v1alpha1
      kind: XListenerSet
      metadata:
        name: sni-listenerset
        namespace: {{< reuse "docs/snippets/namespace.md" >}}
      spec:
        parentRef:
          name: sni
          namespace: {{< reuse "docs/snippets/namespace.md" >}}
          kind: Gateway
          group: gateway.networking.k8s.io
        listeners:
          - protocol: HTTPS
            port: 443
            name: httpbin
            hostname: "httpbin.example.com"
            tls:
              mode: Terminate
              certificateRefs:
                - name: httpbin-credential
                  kind: Secret
            allowedRoutes:
              namespaces:
                from: All
          - protocol: HTTPS
            port: 443
            name: petstore
            hostname: "petstore.example.com"
            tls:
              mode: Terminate
              certificateRefs:
                - name: petstore-credential
                  kind: Secret
            allowedRoutes:
              namespaces:
                from: All
      EOF
      ```

      {{< reuse "docs/snippets/review-table.md" >}}
      
      |Setting|Description|
      |--|--|
      |`spec.parentRef`|The name of the Gateway to attach the ListenerSet to. |
      |`spec.listeners`|Configure the listeners for this gateway. In this example, you configure two HTTPS listeners. One listener is for the httpbin app and the other is for the petstore app. Each listener refers to a secret that holds the TLS certificate and key for the hostname that the listener is configured for. |
      |`spec.listeners.tls.mode`|The TLS mode that you want to use for incoming requests. In this example, HTTPS requests are terminated at the gateway and the unencrypted request is forwarded to the service in the cluster. |
      |`spec.listeners.tls.certificateRefs`|The Kubernetes secret that holds the TLS certificate and key for the gateway. The gateway uses these credentials to establish the TLS connection with a client, and to decrypt incoming HTTPS requests.|

   {{% /tab %}}
   {{< /tabs >}}

2. Create an HTTPRoute that routes incoming requests on the `httpbin.example.com` domain to the httpbin app. 

   {{< tabs items="Gateway listeners,ListenerSet (experimental)" tabTotal="2" >}}
   {{% tab tabName="Gateway listeners" %}}   
   
   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.networking.k8s.io/v1
   kind: HTTPRoute
   metadata:
     name: httpbin-https
     namespace: httpbin
       gateway: sni
   spec:
     parentRefs:
       - name: sni
         namespace: {{< reuse "docs/snippets/namespace.md" >}}
     hostnames:
       - "httpbin.example.com"
     rules:
       - backendRefs:
           - name: httpbin
             port: 8000
   EOF
   ```

   {{% /tab %}}
   {{% tab tabName="ListenerSet (experimental)" %}}

   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.networking.k8s.io/v1
   kind: HTTPRoute
   metadata:
     name: httpbin-https
     namespace: httpbin
       gateway: sni
   spec:
     parentRefs:
       - name: sni-listenerset
         namespace: {{< reuse "docs/snippets/namespace.md" >}}
         kind: XListenerSet
         group: gateway.networking.x-k8s.io
     hostnames:
       - "httpbin.example.com"
     rules:
       - backendRefs:
           - name: httpbin
             port: 8000
   EOF
   ```
   {{% /tab %}}
   {{< /tabs >}}

3. Create an HTTPRoute that routes incoming requests on the `petstore.example.com` domain to the petstore app. 

   {{< tabs items="Gateway listeners,ListenerSet (experimental)" tabTotal="2" >}}
   {{% tab tabName="Gateway listeners" %}}   
   
   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.networking.k8s.io/v1
   kind: HTTPRoute
   metadata:
     name: petstore-https
     namespace: default
   spec:
     parentRefs:
       - name: sni
         namespace: {{< reuse "docs/snippets/namespace.md" >}}
     hostnames:
       - "petstore.example.com"
     rules:
       - backendRefs:
           - name: petstore
             port: 8080
   EOF
   ```

   {{% /tab %}}
   {{% tab tabName="ListenerSet (experimental)" %}}

   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.networking.k8s.io/v1
   kind: HTTPRoute
   metadata:
     name: petstore-https
     namespace: default
   spec:
     parentRefs:
       - name: sni-listenerset
         namespace: {{< reuse "docs/snippets/namespace.md" >}}
         kind: XListenerSet
         group: gateway.networking.x-k8s.io
     hostnames:
       - "petstore.example.com"
     rules:
       - backendRefs:
           - name: petstore
             port: 8080
   EOF
   ```
   {{% /tab %}}
   {{< /tabs >}}

4. Get the external address of the Gateway and save it in an environment variable. Note that it might take a few seconds for the Gateway address to become available. 
   {{< tabs items="Cloud Provider LoadBalancer,Port-forward for local testing" tabTotal="2" >}}
   {{% tab tabName="Cloud Provider LoadBalancer" %}}
   ```sh
   export INGRESS_GW_ADDRESS=$(kubectl get svc -n {{< reuse "docs/snippets/namespace.md" >}} sni -o jsonpath="{.status.loadBalancer.ingress[0]['hostname','ip']}")
   echo $INGRESS_GW_ADDRESS   
   ```
   {{% /tab %}}
   {{% tab tabName="Port-forward for local testing" %}}
   ```sh
   kubectl port-forward svc/sni -n {{< reuse "docs/snippets/namespace.md" >}} 8443:443
   ```
   {{% /tab %}}
   {{< /tabs >}}

5. Send a request to the `httpbin.example.com` domain with the client certificate that you created earlier. Verify that the gateway presents the TLS certificate for the `httpbin.example.com` domain during the TLS handshake. 
   {{< tabs items="LoadBalancer IP address,LoadBalancer hostname,Port-forward for local testing" tabTotal="3" >}}
   {{% tab tabName="LoadBalancer IP address" %}}
   ```sh
   curl -vik --resolve "httpbin.example.com:443:${INGRESS_GW_ADDRESS}"  https://httpbin.example.com:443/anything  
   ```
   {{% /tab %}}
   {{% tab tabName="LoadBalancer hostname" %}}
   ```sh
   curl -vik --resolve "httpbin.example.com:443:$(dig +short $INGRESS_GW_ADDRESS | head -n1)"  https://httpbin.example.com:443/anything 
   ```
   {{% /tab %}}
   {{% tab tabName="Port-forward for local testing" %}}
   ```sh
   curl -vik --connect-to httpbin.example.com:443:localhost:8443 https://httpbin.example.com:443/anything
   ```
   {{% /tab %}}
   {{< /tabs >}}

   Example output: 
   ```
   * Added httpbin.example.com:443:3.XXX.XXX.XX to DNS cache
   * Hostname httpbin.example.com was found in DNS cache
   *   Trying 3.128.214.17:443...
   * Connected to httpbin.example.com (3.XXX.XXX.XX) port 443
   * ALPN: curl offers h2,http/1.1
   * (304) (OUT), TLS handshake, Client hello (1):
   * (304) (IN), TLS handshake, Server hello (2):
   * (304) (IN), TLS handshake, Unknown (8):
   * (304) (IN), TLS handshake, Certificate (11):
   * (304) (IN), TLS handshake, CERT verify (15):
   * (304) (IN), TLS handshake, Finished (20):
   * (304) (OUT), TLS handshake, Finished (20):
   * SSL connection using TLSv1.3 / AEAD-CHACHA20-POLY1305-SHA256 / [blank] / UNDEF
   * ALPN: server accepted h2
   * Server certificate:
   *  subject: CN=httpbin.example.com; O=httpbin organization
   *  issuer: O=example Inc.; CN=example.com
   *  SSL certificate verify result: unable to get local issuer certificate (20), continuing   anyway.
   * using HTTP/2
   * [HTTP/2] [1] OPENED stream for https://httpbin.example.com:443/headers
   * [HTTP/2] [1] [:method: GET]
   * [HTTP/2] [1] [:scheme: https]
   * [HTTP/2] [1] [:authority: httpbin.example.com]
   * [HTTP/2] [1] [:path: /headers]
   * [HTTP/2] [1] [user-agent: curl/8.7.1]
   * [HTTP/2] [1] [accept: */*]
   > GET /headers HTTP/2
   > Host: httpbin.example.com
   > User-Agent: curl/8.7.1
   > Accept: */*
   > 
   * Request completely sent off
   < HTTP/2 200 
   HTTP/2 200 
   ...
       "Accept": [
         "*/*"
       ],
       "Host": [
         "httpbin.example.com"
       ],
       "User-Agent": [
         "curl/8.7.1"
       ],
       "X-Envoy-Expected-Rq-Timeout-Ms": [
         "15000"
       ],
       "X-Forwarded-Proto": [
         "https"
       ],
       "X-Request-Id": [
         "33654cba-7198-4b7c-a850-8629fd230145"
       ]
     }
   }
   ```

6. Send a request to the `petstore.example.com` domain with the client certificate that you created earlier. Verify that the gateway presents the TLS certificate for the `petstore.example.com` domain during the TLS handshake. 
   {{< tabs items="LoadBalancer IP address,LoadBalancer hostname,Port-forward for local testing" tabTotal="3" >}}
   {{% tab tabName="LoadBalancer IP address" %}}
   ```sh
   curl -vik --resolve "petstore.example.com:443:${INGRESS_GW_ADDRESS}" https://petstore.example.com:443/api/pets
   ```
   {{% /tab %}}
   {{% tab tabName="LoadBalancer hostname" %}}
   ```sh
   curl -vik --resolve "petstore.example.com:443:$(dig +short $INGRESS_GW_ADDRESS | head -n1)" https://petstore.example.com:443/api/pets 
   ```
   {{% /tab %}}
   {{% tab tabName="Port-forward for local testing" %}}
   ```sh
   curl -vik --connect-to petstore.example.com:443:localhost:8443 https://petstore.example.com:443/api/pets 
   ```
   {{% /tab %}}
   {{< /tabs >}}
    
   Example output: 
   ```
   * Added petstore.example.com:443:3.XXX.XXX.XX to DNS cache
   * Hostname petstore.example.com was found in DNS cache
   *   Trying 3.128.214.17:443...
   * Connected to petstore.example.com (3.XXX.XXX.XX) port 443
   * ALPN: curl offers h2,http/1.1
   * (304) (OUT), TLS handshake, Client hello (1):
   * (304) (IN), TLS handshake, Server hello (2):
   * (304) (IN), TLS handshake, Unknown (8):
   * (304) (IN), TLS handshake, Certificate (11):
   * (304) (IN), TLS handshake, CERT verify (15):
   * (304) (IN), TLS handshake, Finished (20):
   * (304) (OUT), TLS handshake, Finished (20):
   *  SSL connection using TLSv1.3 / AEAD-CHACHA20-POLY1305-SHA256 / [blank] / UNDEF
   * ALPN: server accepted h2
   * Server certificate:
   *  subject: CN=petstore.example.com; O=petstore organization
   *  issuer: O=example Inc.; CN=example.com
   *  SSL certificate verify result: unable to get local issuer certificate (20), continuing anyway.
   * using HTTP/2
   * [HTTP/2] [1] OPENED stream for https://petstore.example.com:443/api/pets
   * [HTTP/2] [1] [:method: GET]
   * [HTTP/2] [1] [:scheme: https]
   * [HTTP/2] [1] [:authority: petstore.example.com]
   * [HTTP/2] [1] [:path: /api/pets]
   * [HTTP/2] [1] [user-agent: curl/8.7.1]
   * [HTTP/2] [1] [accept: */*]
   > GET /api/pets HTTP/2
   > Host: petstore.example.com
   > User-Agent: curl/8.7.1
   > Accept: */*
   > 
   * Request completely sent off
   < HTTP/2 200 
   HTTP/2 200 
   ...

   [{"id":1,"name":"Dog","status":"available"},{"id":2,"name":"Cat","status":"pending"}]
   ```
    
## Cleanup

{{< reuse "docs/snippets/cleanup.md" >}}

1. Remove the routing resources for the HTTPS route, including the Kubernetes secret that holds the TLS certificate and key.

   {{< tabs items="Gateway listeners,ListenerSet (experimental)" tabTotal="2" >}}
   {{% tab tabName="Gateway listeners" %}}

   ```sh
   kubectl delete secret httpbin-credential -n {{< reuse "docs/snippets/namespace.md" >}}
   kubectl delete secret petstore-credential -n {{< reuse "docs/snippets/namespace.md" >}}
   kubectl delete gateway sni -n {{< reuse "docs/snippets/namespace.md" >}}
   kubectl delete httproute httpbin-https -n httpbin
   kubectl delete httproute petstore-https -n default
   kubectl delete deployment petstore
   kubectl delete service petstore
   ```
   {{% /tab %}}
   {{% tab tabName="ListenerSet (experimental)" %}}
   ```sh
   kubectl delete secret httpbin-credential -n {{< reuse "docs/snippets/namespace.md" >}}
   kubectl delete secret petstore-credential -n {{< reuse "docs/snippets/namespace.md" >}}
   kubectl delete gateway sni -n {{< reuse "docs/snippets/namespace.md" >}}
   kubectl delete xlistenerset sni-listenerset -n {{< reuse "docs/snippets/namespace.md" >}}
   kubectl delete httproute httpbin-https -n httpbin
   kubectl delete httproute petstore-https -n default
   kubectl delete deployment petstore
   kubectl delete service petstore
   ```
   {{% /tab %}}
   {{< /tabs >}}

2. Remove the `example_certs` directory that stores your TLS credentials. 
   ```sh
   rm -rf example_certs
   ```
