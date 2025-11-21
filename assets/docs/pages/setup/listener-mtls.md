In this guide, you learn how to set up an mTLS Gateway. Before the client application and the Gateway establish a connection, both parties must exchange certificates to verify their identities. After a TLS connection is established, the TLS connection is terminated at the Gateway and the unencrypted HTTP traffic is forwarded to the backend destination. 

## Before you begin

{{< reuse "docs/snippets/cert-prereqs.md" >}}

## Create self-signed TLS certificates 

Create self-signed TLS certificates that you use for the mutual TLS connection between your client application (`curl`) and the gateway proxy. 

{{< callout type="warning" >}}
Self-signed certificates are used for demonstration purposes. Do not use self-signed certificates in production environments. Instead, use certificates that are issued from a trust Certificate Authority. 
{{< /callout >}}

<!-- >
When generating your Envoy certificates, make sure to use encryption algorithms that are supported in Envoy. To learn more about supported algorithms that you can use for your certificates and keys, see the <a href="https://www.envoyproxy.io/docs/envoy/latest/intro/arch_overview/security/ssl#certificate-selection">Envoy documentation</a>. 
-->

1. Create a root certificate for the `example.com` domain. You use this certificate to sign the certificate for your client and gateway later. 
   ```shell
   mkdir example_certs
   openssl req -x509 -sha256 -nodes -days 365 -newkey rsa:2048 -subj '/O=example Inc./CN=example.com' -keyout example_certs/example.com.key -out example_certs/example.com.crt
   ```
   
2. Create a gateway certificate that is signed by the root CA certificate that you created in the previous step. 
   ```sh
   openssl req -out example_certs/gateway.csr -newkey rsa:2048 -nodes -keyout example_certs/gateway.key -subj "/CN=*/O=any domain"
   openssl x509 -req -sha256 -days 365 -CA example_certs/example.com.crt -CAkey example_certs/example.com.key -set_serial 0 -in example_certs/gateway.csr -out example_certs/gateway.crt
   ```

3. Create a Kubernetes secret to store your gateway TLS certificate. You create the secret in the same cluster and namespace that the gateway is deployed to. By including a `rootca` certificate, Gloo Gateway is automatically configured for mutual TLS with the downstream application. 
   ```sh
   export TLS_CERT="$(< example_certs/gateway.crt)"  
   export TLS_KEY="$(< example_certs/gateway.key)"  
   export CA_CERT="$(< example_certs/example.com.crt)"
   
   cat <<EOF | kubectl apply -f -
   apiVersion: v1
   kind: Secret
   metadata:
     name: https
     namespace: {{< reuse "docs/snippets/namespace.md" >}}
     labels: 
       gateway: https
   type: kubernetes.io/tls
   stringData:
     tls.crt: |
   $(echo "$TLS_CERT" | sed 's/^/    /')
     tls.key: |
   $(echo "$TLS_KEY" | sed 's/^/    /')
     ca.crt: | 
   $(echo "$CA_CERT" | sed 's/^/    /')
   EOF
   ```

4. Create a client certificate and private key. You use these credentials later when sending a request to the gateway proxy. The client certificate is signed with the same root CA certificate that you used for the gateway proxy. 
   ```sh
   openssl req -out example_certs/client.example.com.csr -newkey rsa:2048 -nodes -keyout example_certs/client.example.com.key -subj "/CN=client.example.com/O=client organization"
   openssl x509 -req -sha256 -days 365 -CA example_certs/example.com.crt -CAkey example_certs/example.com.key -set_serial 1 -in example_certs/client.example.com.csr -out example_certs/client.example.com.crt
   ```
   
## Set up an mTLS listener

1. Create a mTLS Gateway that is configured with the TLS certificates that you set up earlier. To use the default Envoy-based kgateway proxy, set the gatewayClassName to `{{< reuse "docs/snippets/gatewayclass.md" >}}`. To use agentgateway, set the gatewayClassName to `{{< reuse "docs/snippets/agw-gatewayclass.md" >}}`.

   {{< tabs tabTotal="2" items="Gateway listeners,ListenerSet (experimental)">}}
   {{% tab tabName="Gateway listeners" %}}

   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.networking.k8s.io/v1
   kind: Gateway
   metadata:
     name: https
     namespace: {{< reuse "docs/snippets/namespace.md" >}}
     labels:
       gateway: https
   spec:
     gatewayClassName: {{< reuse "docs/snippets/gatewayclass.md" >}}
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
   |`spec.gatewayClassName`|The name of the Kubernetes gateway class that you want to use to configure the gateway. |
   |`spec.listeners`|Configure the listeners for this gateway. In this example, you configure an HTTPS gateway that listens for incoming traffic on port 443. |
   |`spec.listeners.tls.mode`|The TLS mode that you want to use for incoming requests. In this example, HTTPS requests are terminated at the gateway and the unencrypted request is forwarded to the service in the cluster. |
   |`spec.listeners.tls.certificateRefs`|The Kubernetes secret that holds the TLS certificate and key for the gateway. The gateway uses these credentials to establish the TLS connection with a client, and to decrypt incoming HTTPS requests.|

   {{% /tab %}}
   {{% tab tabName="ListenerSet (experimental)" %}}
   
   1. Create a Gateway that enables the attachment of ListenerSets.

      ```yaml
      kubectl apply -f- <<EOF
      apiVersion: gateway.networking.k8s.io/v1
      kind: Gateway
      metadata:
        name: https
        namespace: {{< reuse "docs/snippets/namespace.md" >}}
        labels:
          gateway: https
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
      
      
      |Setting|Description|
      |--|--|
      |`spec.gatewayClassName`|The name of the Kubernetes gateway class that you want to use to configure the gateway.  |
      |`spec.allowedListeners`|Enable the attachment of ListenerSets to this Gateway. The example allows listeners from any namespace, which is helpful in multitenant environments. You can also limit the allowed listeners. To limit to listeners in the same namespace as the Gateway, set this value to `Same`. To limit to listeners with a particular label, set this value to `Selector`. |
      | `spec.listeners` | Optionally, you can configure a listener that is specific to the Gateway. Note that due to a [Gateway API limitation](https://gateway-api.sigs.k8s.io/geps/gep-1713/#gateway-changes), you must configure at least one listener on the Gateway resource, even if the listener is not used and is a "dummy" listener. This dummy listener cannot conflict with the listener that you configure in the ListenerSet, such as using the same port or name. In this example, the dummy listener is configured on HTTP port 80, which differs from HTTPS port 443 in the ListenerSet that you create later. |
   
   2. Create a ListenerSet that configures an HTTPS listener for the Gateway.

      ```yaml
      kubectl apply -f- <<EOF
      apiVersion: gateway.networking.x-k8s.io/v1alpha1
      kind: XListenerSet
      metadata:
        name: https-listenerset
        namespace: {{< reuse "docs/snippets/namespace.md" >}}
        labels:
          gateway: https
      spec:
        parentRef:
          name: https
          namespace: {{< reuse "docs/snippets/namespace.md" >}}
          kind: Gateway
          group: gateway.networking.k8s.io
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
      |`spec.parentRef`|The name of the Gateway to attach the ListenerSet to. |
      |`spec.listeners`|Configure the listeners for this gateway. In this example, you configure an HTTPS gateway that listens for incoming traffic on port 443. |
      |`spec.listeners.tls.mode`|The TLS mode that you want to use for incoming requests. In this example, HTTPS requests are terminated at the gateway and the unencrypted request is forwarded to the service in the cluster. |
      |`spec.listeners.tls.certificateRefs`|The Kubernetes secret that holds the TLS certificate and key for the gateway. The gateway uses these credentials to establish the TLS connection with a client, and to decrypt incoming HTTPS requests.|

   {{% /tab %}}
   {{< /tabs >}}

2. Create an HTTPRoute for the httpbin app and add it to the HTTPS gateway that you created. 

   {{< tabs tabTotal="2" items="Gateway listeners,ListenerSet (experimental)" >}}
   {{% tab tabName="Gateway listeners" %}}   

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
         namespace: {{< reuse "docs/snippets/namespace.md" >}}
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
     labels:
       example: httpbin-route
       gateway: https
   spec:
     parentRefs:
       - name: https-listenerset
         namespace: {{< reuse "docs/snippets/namespace.md" >}}
         kind: XListenerSet
         group: gateway.networking.x-k8s.io
     rules:
       - backendRefs:
           - name: httpbin
             port: 8000
   EOF
   ```
   {{% /tab %}}
   {{< /tabs >}}

3. Verify that the HTTPRoute is applied successfully. 
   
   ```sh
   kubectl get httproute/httpbin-https -n httpbin -o yaml
   ```

   Example output: Notice in the `status` section that the parentRef is either the Gateway or the ListenerSet, depending on how you attached the HTTPRoute.

   ```yaml
   ...
   status:
     parents:
     - conditions:
       - lastTransitionTime: "2025-04-29T20:48:51Z"
         message: ""
         observedGeneration: 3
         reason: Accepted
         status: "True"
         type: Accepted
       - lastTransitionTime: "2025-04-29T20:48:51Z"
         message: ""
         observedGeneration: 3
         reason: ResolvedRefs
         status: "True"
         type: ResolvedRefs
       controllerName: solo.io/gloo-gateway
     parentRef:
       group: gateway.networking.x-k8s.io
       kind: XListenerSet
       name: https-listenerset
       namespace: {{< reuse "docs/snippets/namespace.md" >}}
   ```

4. Verify that the listener now has a route attached.

   {{< tabs tabTotal="2" items="Gateway listeners,ListenerSet (experimental)" >}}
   {{% tab tabName="Gateway listeners" %}}   

   ```sh
   kubectl get gateway -n {{< reuse "docs/snippets/namespace.md" >}} https -o yaml
   ```

   Example output:

   ```yaml
   ...
   listeners:
   - attachedRoutes: 1
   ```
   {{% /tab %}}
   {{% tab tabName="ListenerSet (experimental)" %}}

   ```sh
   kubectl get xlistenerset -n {{< reuse "docs/snippets/namespace.md" >}} https-listenerset -o yaml
   ```

   Example output:

   ```yaml
   ...
   listeners:
   - attachedRoutes: 1
   ```

   Note that because the HTTPRoute is attached to the ListenerSet, the Gateway does not show the route in its status.

   ```sh
   kubectl get gateway -n {{< reuse "docs/snippets/namespace.md" >}} https -o yaml
   ```

   Example output:

   ```yaml
   ...
   listeners:
   - attachedRoutes: 0
   ```

   If you create another HTTPRoute that attaches to the Gateway and uses the same listener as the ListenerSet, then the route is reported in the status of both the Gateway (attachedRoutes: 1) and the ListenerSet (attachedRoutes: 2).
   {{% /tab %}}
   {{< /tabs >}}

5. Get the external address of the gateway and save it in an environment variable. Note that it might take a few seconds for the gateway address to become available. 
   {{< tabs tabTotal="2" items="Cloud Provider LoadBalancer,Port-forward for local testing">}}
   {{% tab tabName="Cloud Provider LoadBalancer" %}}
   ```sh
   export INGRESS_GW_ADDRESS=$(kubectl get svc -n {{< reuse "docs/snippets/namespace.md" >}} https -o jsonpath="{.status.loadBalancer.ingress[0]['hostname','ip']}")
   echo $INGRESS_GW_ADDRESS   
   ```
   {{% /tab %}}
   {{% tab tabName="Port-forward for local testing" %}}
   ```sh
   kubectl port-forward svc/https -n {{< reuse "docs/snippets/namespace.md" >}} 8443:443
   ```
   {{% /tab %}}
   {{< /tabs >}}

6. Send a request to the httpbin app. Verify that you see the TLS handshake and that you get back a 200 HTTP response code. 
   {{< tabs tabTotal="3" items="LoadBalancer IP address,LoadBalancer hostname,Port-forward for local testing" >}}
   {{% tab tabName="LoadBalancer IP address" %}}
   ```sh
   curl -vik --resolve "https.example.com:443:${INGRESS_GW_ADDRESS}"  https://https.example.com:443/anything \
     --cert example_certs/client.example.com.crt \
     --key example_certs/client.example.com.key \
     --cacert example_certs/example.com.crt 
   ```
   {{% /tab %}}
   {{% tab tabName="LoadBalancer hostname" %}}
   ```sh
   curl -vik --resolve "https.example.com:443:$(dig +short $INGRESS_GW_ADDRESS | head -n1)"  https://https.example.com:443/anything \
     --cert example_certs/client.example.com.crt \
     --key example_certs/client.example.com.key \
     --cacert example_certs/example.com.crt 
   ```
   {{% /tab %}}
   {{% tab tabName="Port-forward for local testing" %}}
   ```sh
   curl -vik --connect-to https.example.com:443:localhost:8443 https://https.example.com:443/anything \
     --cert example_certs/client.example.com.crt \
     --key example_certs/client.example.com.key \
     --cacert example_certs/example.com.crt 
   ```
   {{% /tab %}}
   {{< /tabs >}} 
   
   Example output: 
   ```
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
   *  subject: CN=*; O=any domain
   *  issuer: O=any domain; CN=*
   *  SSL certificate verify result: unable to get local issuer certificate (20), continuing   anyway.
   * using HTTP/2
   * [HTTP/2] [1] OPENED stream for https://https.example.com:443/anything
   * [HTTP/2] [1] [:method: GET]
   * [HTTP/2] [1] [:scheme: https]
   * [HTTP/2] [1] [:authority: https.example.com]
   * [HTTP/2] [1] [:path: /anything]
   * [HTTP/2] [1] [user-agent: curl/8.7.1]
   * [HTTP/2] [1] [accept: */*]
   > GET /anything HTTP/2
   > Host: https.example.com
   > User-Agent: curl/8.7.1
   > Accept: */*
   > 
   * Request completely sent off
   < HTTP/2 200 
   HTTP/2 200 
   ...
   {
     "args": {},
     "headers": {
       "Accept": [
         "*/*"
       ],
       "Host": [
         "https.example.com"
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
         "01ef350c-4587-4350-aa0e-0712fee757b9"
       ]
     },
     "url": "https://https.example.com/anything",
     ...
   }
   ```
   
## Cleanup
   
1. Remove the routing resources for the HTTPS route, including the Kubernetes secret that holds the TLS certificate and key.

   {{< tabs tabTotal="2" items="Gateway listeners,ListenerSet (experimental)"  >}}
   {{% tab tabName="Gateway listeners" %}}

   ```sh
   kubectl delete httproute,gateway,secret -A -l gateway=https
   ```
   {{% /tab %}}
   {{% tab tabName="ListenerSet (experimental)" %}}
   ```sh
   kubectl delete httproute,xlistenerset,gateway,secret -A -l gateway=https
   ```
   {{% /tab %}}
   {{< /tabs >}}

2. Remove the `example_certs` directory that stores your TLS credentials. 
   ```sh
   rm -rf example_certs
   ```