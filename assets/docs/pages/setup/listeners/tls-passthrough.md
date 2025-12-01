Set up a TLS listener on the Gateway that serves one or more hosts and passes TLS traffic through to a destination. Because TLS traffic is not terminated at the Gateway, the destination must be capable of handling incoming TLS traffic.

## Before you begin

{{< reuse "docs/snippets/cert-prereqs.md" >}}

## Deploy an nginx server that is configured for HTTPS traffic

Deploy a sample nginx server and configure the server for HTTPS traffic. 

1. Create a root certificate for the `example.com` domain. You use this certificate to sign the certificate for your nginx service later. 
   ```shell
   mkdir example_certs
   openssl req -x509 -sha256 -nodes -days 365 -newkey rsa:2048 -subj '/O=example Inc./CN=example.com' -keyout example_certs/example.com.key -out example_certs/example.com.crt
   ```
   
2. Create a server certificate and private key for the `nginx.example.com` domain. 
   ```
   openssl req -out example_certs/nginx.example.com.csr -newkey rsa:2048 -nodes -keyout example_certs/nginx.example.com.key -subj "/CN=nginx.example.com/O=some organization"
   openssl x509 -req -sha256 -days 365 -CA example_certs/example.com.crt -CAkey example_certs/example.com.key -set_serial 0 -in example_certs/nginx.example.com.csr -out example_certs/nginx.example.com.crt
   ```

3. Create a secret that stores the certificate and key for the nginx server. 
   ```shell
   kubectl create secret tls nginx-server-certs \
    --key example_certs/nginx.example.com.key \
    --cert example_certs/nginx.example.com.crt
   ```
   
5. Prepare your nginx configuration. The following example configures nginx for HTTPS traffic with the certificate that you created earlier.
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
   
6. Store the nginx configuration in a configmap. 
   ```shell
   kubectl create configmap nginx-configmap --from-file=nginx.conf=./nginx.conf
   ```

7. Deploy the nginx server. 
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

8. Verify that the server is up and running. 
   ```sh
   kubectl get pods | grep nginx
   ```
   
   Example output: 
   ```
   my-nginx-c4c49df8f-2bkws    1/1     Running   0          34s
   ```

## Set up TLS passthrough

To route TLS traffic to the nginx server directly without terminating the TLS connection at the Gateway, you can use either an inline Gateway listener or a ListenerSet. Then, you create a TLSRoute that represents the route to your nginx server and attach it to the Gateway or ListenerSet.

If you plan to set up your listener as part of a ListenerSet, keep the following considerations in mind. For more information, see [ListenerSets (experimental)]({{< link-hextra path="/setup/listeners/overview/#listenersets" >}}).
* {{< reuse "docs/versions/warn-2-1-only.md" >}} 
* You must install the experimental channel of the Kubernetes Gateway API at version 1.3 or later.

{{< tabs items="Gateway listeners,ListenerSets (experimental)" tabTotal="2" >}}
{{% tab tabName="Gateway listeners" %}}
1. Create a Gateway that passes through incoming TLS requests for the `nginx.example.com` domain.

   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.networking.k8s.io/v1
   kind: Gateway
   metadata:
     name: tls-passthrough
     namespace: {{< reuse "docs/snippets/namespace.md" >}}
   spec:
     gatewayClassName: {{< reuse "docs/snippets/gatewayclass.md" >}}
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

   {{< reuse "docs/snippets/review-table.md" >}}

   |Setting|Description|
   |---|---|
   |`spec.gatewayClassName`|The name of the Kubernetes GatewayClass that you want to use to configure the Gateway. When you set up {{< reuse "docs/snippets/kgateway.md" >}}, a default GatewayClass is set up for you. {{< reuse "docs/snippets/agw-gatewayclass-choice.md" >}}|
   |`spec.listeners`|Configure the listeners for this Gateway. In this example, you configure a TLS passthrough Gateway that listens for incoming traffic for the `nginx.example.com` domain on port 8443. The Gateway can serve TLS routes from any namespace.|
   |`spec.listeners.tls.mode`|The TLS mode for incoming requests. In this example, TLS requests are passed through to the backend service without being terminated at the Gateway.|

{{% /tab %}}
{{% tab tabName="ListenerSets (experimental)" %}}

1. Create a Gateway that enables the attachment of ListenerSets.

   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.networking.k8s.io/v1
   kind: Gateway
   metadata:
     name: tls-passthrough
     namespace: {{< reuse "docs/snippets/namespace.md" >}}
   spec:
     gatewayClassName: {{< reuse "docs/snippets/gatewayclass.md" >}}
     allowedListeners:
       namespaces:
         from: All
     listeners:
     - protocol: TLS
       port: 80
       name: generic-tls
       allowedRoutes:
         namespaces:
           from: All
   EOF
   ```

   {{< reuse "docs/snippets/review-table.md" >}}

   |Setting|Description|
   |---|---|
   |`spec.gatewayClassName`|The name of the Kubernetes GatewayClass that you want to use to configure the Gateway. When you set up {{< reuse "docs/snippets/kgateway.md" >}}, a default GatewayClass is set up for you. {{< reuse "docs/snippets/agw-gatewayclass-choice.md" >}} |
   |`spec.allowedListeners`|Enable the attachment of ListenerSets to this Gateway. The example allows listeners from any namespace.|
   |`spec.listeners`|{{< reuse "docs/snippets/generic-listener.md" >}} In this example, the generic listener is configured on port 80, which differs from port 443 in the ListenerSet that you create later.|

2. Create a ListenerSet that configures a TLS passthrough listener for the Gateway.

   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.networking.x-k8s.io/v1alpha1
   kind: XListenerSet
   metadata:
     name: my-tls-listenerset
     namespace: {{< reuse "docs/snippets/namespace.md" >}}
   spec:
     parentRef:
       name: tls-passthrough
       namespace: {{< reuse "docs/snippets/namespace.md" >}}
       kind: Gateway
       group: gateway.networking.k8s.io
     listeners:
     - protocol: TLS
       port: 8443
       hostname: nginx.example.com
       name: tls-listener-set
       tls:
         mode: Passthrough
       allowedRoutes:
         namespaces:
           from: All
   EOF
   ```

   {{< reuse "docs/snippets/review-table.md" >}}

   |Setting|Description|
   |--|--|
   |`spec.parentRef`|The name of the Gateway to attach the ListenerSet to.|
   |`spec.listeners`|Configure the listeners for this ListenerSet. In this example, you configure a TLS passthrough listener for the `nginx.example.com` domain on port 8443.|
   |`spec.listeners.tls.mode`|The TLS mode for incoming requests. TLS requests are passed through to the backend service without being terminated at the Gateway.|

{{% /tab %}}
{{< /tabs >}}

## Create a TLSRoute

{{< tabs items="Gateway listeners,ListenerSets (experimental)" tabTotal="2" >}}
{{% tab tabName="Gateway listeners" %}}
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
      namespace: {{< reuse "docs/snippets/namespace.md" >}}
  rules:
    - backendRefs:
        - group: ""
          kind: Service
          name: my-nginx
          port: 443
EOF
```
{{% /tab %}}
{{% tab tabName="ListenerSets (experimental)" %}}
```yaml
kubectl apply -f- <<EOF
apiVersion: gateway.networking.k8s.io/v1alpha2
kind: TLSRoute
metadata:
  name: tlsroute
  namespace: default
spec:
  parentRefs:
    - name: my-tls-listenerset
      namespace: {{< reuse "docs/snippets/namespace.md" >}}
      kind: XListenerSet
      group: gateway.networking.x-k8s.io
  rules:
    - backendRefs:
        - group: ""
          kind: Service
          name: my-nginx
          port: 443
EOF
```
{{% /tab %}}
{{< /tabs >}}

## Verify TLS passthrough traffic for nginx

{{< tabs items="Cloud Provider LoadBalancer,Port-forward for local testing" tabTotal="2" >}}
{{% tab tabName="Cloud Provider LoadBalancer" %}}
1. Get the external address of the gateway proxy and save it in an environment variable.external address of the gateway proxy and save it in an environment variable.
   ```sh 
   export INGRESS_GW_ADDRESS=$(kubectl get svc -n {{< reuse "docs/snippets/namespace.md" >}} tls-passthrough -o jsonpath="{.status.loadBalancer.ingress[0]['hostname','ip']}")
   echo $INGRESS_GW_ADDRESS  
   ```
2. Send a request to the `nginx.example.com` domain and verify that you get back a 200 HTTP response code from your nginx server. Because nginx accepts incoming TLS traffic only, the 200 HTTP response code proves that TLS traffic was not terminated at the Gateway. In addition, you can verify that you get back the server certificate that you configured your nginx server with in the beginning. 

   * **Load balancer IP**: 
     ```shell
     curl -vik --resolve "nginx.example.com:8443:${INGRESS_GW_ADDRESS}" --cacert example_certs/example.com.crt https://nginx.example.com:8443/
     ```
   
   * **Load balancer hostname**: 
     ```shell
     curl -vik --resolve "nginx.example.com:8443:$(dig +short $INGRESS_GW_ADDRESS | head -n1)" --cacert example_certs/example.com.crt https://nginx.example.com:8443/
     ```
     
   Example output: 
   ```console
   * Request completely sent off
   < HTTP/1.1 200 OK
   HTTP/1.1 200 OK
   < Server: nginx/1.27.4
   Server: nginx/1.27.4
   ...
   < 

   <!DOCTYPE html>
   <html>
   <head>
   <title>Welcome to nginx!</title>
   <style>
   html { color-scheme: light dark; }
   body { width: 35em; margin: 0 auto;
   font-family: Tahoma, Verdana, Arial, sans-serif; }
   </style>
   </head>
   <body>
   <h1>Welcome to nginx!</h1>
   <p>If you see this page, the nginx web server is successfully installed and
   working. Further configuration is required.</p>

   <p>For online documentation and support please refer to
   <a href="http://nginx.org/">nginx.org</a>.<br/>
   Commercial support is available at
   <a href="http://nginx.com/">nginx.com</a>.</p>

   <p><em>Thank you for using nginx.</em></p>
   </body>
   </html>
   * Connection #0 to host nginx.example.com left intact
   ```
{{% /tab %}}
{{% tab tabName="Port-forward for local testing" %}}
1. Port-forward the tls-passthrough gateway proxy pod on port 8443.
   ```sh
   kubectl port-forward deployment/tls-passthrough -n {{< reuse "docs/snippets/namespace.md" >}} 8443:8443
   ```
2. Send a request to the `nginx.example.com` domain and verify that you get back a 200 HTTP response code from your nginx server. Because nginx accepts incoming TLS traffic only, the 200 HTTP response code proves that TLS traffic was not terminated at the Gateway. In addition, you can verify that you get back the server certificate that you configured your nginx server with in the beginning. 
   ```sh
   curl -vi --cacert example_certs/example.com.crt --resolve "nginx.example.com:8443:127.0.0.1" https://nginx.example.com:8443
   ```
   
   Example output: 
   ```console
   * Request completely sent off
   < HTTP/1.1 200 OK
   HTTP/1.1 200 OK
   < Server: nginx/1.27.4
   Server: nginx/1.27.4
   ...
   < 

   <!DOCTYPE html>
   <html>
   <head>
   <title>Welcome to nginx!</title>
   <style>
   html { color-scheme: light dark; }
   body { width: 35em; margin: 0 auto;
   font-family: Tahoma, Verdana, Arial, sans-serif; }
   </style>
   </head>
   <body>
   <h1>Welcome to nginx!</h1>
   <p>If you see this page, the nginx web server is successfully installed and
   working. Further configuration is required.</p>

   <p>For online documentation and support please refer to
   <a href="http://nginx.org/">nginx.org</a>.<br/>
   Commercial support is available at
   <a href="http://nginx.com/">nginx.com</a>.</p>

   <p><em>Thank you for using nginx.</em></p>
   </body>
   </html>
   * Connection #0 to host nginx.example.com left intact
   ```
   
{{% /tab %}}
{{< /tabs >}}

## Cleanup

{{< reuse "docs/snippets/cleanup.md" >}}

{{< tabs items="Gateway listeners,ListenerSet (experimental)" tabTotal="2" >}}
{{% tab tabName="Gateway listeners" %}}

```sh
rm -r example_certs
rm nginx.conf
kubectl delete configmap nginx-configmap
kubectl delete tlsroute tlsroute
kubectl delete gateway tls-passthrough -n {{< reuse "docs/snippets/namespace.md" >}}
kubectl delete deployment my-nginx
kubectl delete service my-nginx
kubectl delete secret nginx-server-certs   
```
{{% /tab %}}
{{% tab tabName="ListenerSet (experimental)" %}}
```sh
rm -r example_certs
rm nginx.conf
kubectl delete configmap nginx-configmap
kubectl delete tlsroute tlsroute
kubectl delete XListenerSet my-tls-listenerset -n {{< reuse "docs/snippets/namespace.md" >}}
kubectl delete gateway tls-passthrough -n {{< reuse "docs/snippets/namespace.md" >}}
kubectl delete deployment my-nginx
kubectl delete service my-nginx
kubectl delete secret nginx-server-certs   
```
{{% /tab %}}
{{< /tabs >}}



