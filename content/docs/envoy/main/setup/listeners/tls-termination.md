---
title: TLS termination for TLSRoutes
weight: 10
description: Set up a TLS listener on the Gateway that terminates TLS traffic and forwards plain traffic to a backend service using a TLSRoute.
---

Set up a TLS listener on the Gateway that terminates incoming TLS traffic. Unlike [TLS passthrough]({{< link-hextra path="/setup/listeners/tls-passthrough" >}}), the Gateway decrypts the traffic and forwards plain TCP traffic to the backend service. The backend service does not need to handle TLS.

## Before you begin

{{< reuse "docs/snippets/cert-prereqs.md" >}}

## Create a TLS certificate

1. Create a directory to store your TLS credentials in.
   ```sh
   mkdir example_certs
   ```

2. Create a self-signed root certificate.
   ```sh
   openssl req -x509 -sha256 -nodes -days 365 -newkey rsa:2048 \
     -subj '/O=any domain/CN=*' \
     -keyout example_certs/root.key -out example_certs/root.crt
   ```

3. Create an OpenSSL configuration for the `app.example.com` hostname.
   ```sh
   cat <<'EOF' > example_certs/gateway.cnf
   [ req ]
   default_bits = 2048
   prompt = no
   default_md = sha256
   distinguished_name = dn
   req_extensions = req_ext
   [ dn ]
   CN = *.example.com
   O = any domain
   [ req_ext ]
   subjectAltName = @alt_names
   [ alt_names ]
   DNS.1 = *.example.com
   DNS.2 = example.com
   EOF
   ```

4. Create and sign the gateway certificate.
   ```sh
   openssl req -new -nodes \
     -keyout example_certs/gateway.key \
     -out example_certs/gateway.csr \
     -config example_certs/gateway.cnf
   openssl x509 -req -sha256 -days 365 \
     -CA example_certs/root.crt -CAkey example_certs/root.key -set_serial 0 \
     -in example_certs/gateway.csr -out example_certs/gateway.crt \
     -extfile example_certs/gateway.cnf -extensions req_ext
   ```

5. Create a Kubernetes secret to store the gateway TLS certificate.
   ```sh
   kubectl create secret tls tls-terminate \
     -n {{< reuse "docs/snippets/namespace.md" >}} \
     --key example_certs/gateway.key \
     --cert example_certs/gateway.crt
   ```

## Set up TLS termination {#setup-tls-terminate}

Set up a TLS listener on the Gateway with `tls.mode: Terminate`. The Gateway decrypts incoming TLS traffic using the certificate you created and forwards the plain traffic to the backend service.

1. Create a Gateway with a TLS termination listener. {{< reuse "docs/snippets/agw-gatewayclass-choice.md" >}}

   {{< tabs items="Gateway listeners,ListenerSets" tabTotal="2" >}}
   {{% tab tabName="Gateway listeners" %}}
   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.networking.k8s.io/v1
   kind: Gateway
   metadata:
     name: tls-terminate
     namespace: {{< reuse "docs/snippets/namespace.md" >}}
     labels:
       example: tls-terminate
   spec:
     gatewayClassName: {{< reuse "docs/snippets/gatewayclass.md" >}}
     listeners:
     - name: tls
       protocol: TLS
       port: 8443
       hostname: app.example.com
       tls:
         mode: Terminate
         certificateRefs:
           - name: tls-terminate
             kind: Secret
       allowedRoutes:
         namespaces:
           from: All
   EOF
   ```

   {{< reuse "docs/snippets/review-table.md" >}}

   |Setting|Description|
   |---|---|
   |`spec.gatewayClassName`|The name of the Kubernetes GatewayClass that you want to use to configure the Gateway. When you set up {{< reuse "docs/snippets/kgateway.md" >}}, a default GatewayClass is set up for you. {{< reuse "docs/snippets/agw-gatewayclass-choice.md" >}}|
   |`spec.listeners`|Configure the listeners for this Gateway. In this example, you configure a TLS listener that terminates incoming TLS traffic for the `app.example.com` hostname on port 8443. The Gateway can serve TLS routes from any namespace.|
   |`spec.listeners.tls.mode`|The TLS mode for incoming requests. In this example, TLS requests are terminated at the Gateway and the decrypted traffic is forwarded to the backend service.|
   |`spec.listeners.tls.certificateRefs`|The Kubernetes secret that holds the TLS certificate and key. The Gateway uses these to terminate the TLS connection.|

   {{% /tab %}}
   {{% tab tabName="ListenerSets" %}}

   1. Create a Gateway that enables the attachment of ListenerSets.

      ```yaml
      kubectl apply -f- <<EOF
      apiVersion: gateway.networking.k8s.io/v1
      kind: Gateway
      metadata:
        name: tls-terminate
        namespace: {{< reuse "docs/snippets/namespace.md" >}}
        labels:
          example: tls-terminate
      spec:
        gatewayClassName: {{< reuse "docs/snippets/gatewayclass.md" >}}
        allowedListeners:
          namespaces:
            from: All
        listeners:
        - protocol: TLS
          port: 80
          name: generic-tls
          tls:
            mode: Terminate
            certificateRefs:
              - name: tls-terminate
                kind: Secret
          allowedRoutes:
            namespaces:
              from: All
      EOF
      ```

      {{< reuse "docs/snippets/review-table.md" >}}

      |Setting|Description|
      |---|---|
      |`spec.gatewayClassName`|The name of the Kubernetes GatewayClass that you want to use to configure the Gateway. When you set up {{< reuse "docs/snippets/kgateway.md" >}}, a default GatewayClass is set up for you. {{< reuse "docs/snippets/agw-gatewayclass-choice.md" >}}|
      |`spec.allowedListeners`|Enable the attachment of ListenerSets to this Gateway. The example allows listeners from any namespace.|
      |`spec.listeners`|{{< reuse "docs/snippets/generic-listener.md" >}} In this example, the generic listener is configured on port 80, which differs from port 8443 in the ListenerSet that you create later.|

   2. Create a ListenerSet that configures a TLS termination listener for the Gateway.

      ```yaml
      kubectl apply -f- <<EOF
      apiVersion: gateway.networking.k8s.io/v1
      kind: ListenerSet
      metadata:
        name: my-tls-terminate-listenerset
        namespace: {{< reuse "docs/snippets/namespace.md" >}}
        labels:
          example: tls-terminate
      spec:
        parentRef:
          name: tls-terminate
          namespace: {{< reuse "docs/snippets/namespace.md" >}}
          kind: Gateway
          group: gateway.networking.k8s.io
        listeners:
        - protocol: TLS
          port: 8443
          hostname: app.example.com
          name: tls-listener-set
          tls:
            mode: Terminate
            certificateRefs:
              - name: tls-terminate
                kind: Secret
          allowedRoutes:
            namespaces:
              from: All
      EOF
      ```

      {{< reuse "docs/snippets/review-table.md" >}}

      |Setting|Description|
      |---|---|
      |`spec.parentRef`|The name of the Gateway to attach the ListenerSet to.|
      |`spec.listeners`|Configure the listeners for this ListenerSet. In this example, you configure a TLS termination listener for the `app.example.com` hostname on port 8443.|
      |`spec.listeners.tls.mode`|The TLS mode for incoming requests. TLS requests are terminated at the Gateway and the decrypted traffic is forwarded to the backend service.|
      |`spec.listeners.tls.certificateRefs`|The Kubernetes secret that holds the TLS certificate and key for TLS termination.|

   {{% /tab %}}
   {{< /tabs >}}

2. Check the status of the Gateway to make sure that your configuration is accepted.
   ```sh
   kubectl get gateway tls-terminate -n {{< reuse "docs/snippets/namespace.md" >}} -o yaml
   ```

## Create a TLSRoute

Create a TLSRoute that routes SNI traffic for `app.example.com` to the httpbin app.

{{< tabs items="Gateway listeners,ListenerSets" tabTotal="2" >}}
{{% tab tabName="Gateway listeners" %}}
```yaml
kubectl apply -f- <<EOF
apiVersion: gateway.networking.k8s.io/v1
kind: TLSRoute
metadata:
  name: tls-terminate-route
  namespace: httpbin
  labels:
    example: tls-terminate
spec:
  hostnames:
    - app.example.com
  parentRefs:
    - name: tls-terminate
      namespace: {{< reuse "docs/snippets/namespace.md" >}}
      sectionName: tls
  rules:
    - backendRefs:
        - name: httpbin
          port: 8000
EOF
```
{{% /tab %}}
{{% tab tabName="ListenerSets" %}}
```yaml
kubectl apply -f- <<EOF
apiVersion: gateway.networking.k8s.io/v1
kind: TLSRoute
metadata:
  name: tls-terminate-route
  namespace: httpbin
  labels:
    example: tls-terminate
spec:
  hostnames:
    - app.example.com
  parentRefs:
    - name: my-tls-terminate-listenerset
      namespace: {{< reuse "docs/snippets/namespace.md" >}}
      kind: ListenerSet
      group: gateway.networking.k8s.io
      sectionName: tls-listener-set
  rules:
    - backendRefs:
        - name: httpbin
          port: 8000
EOF
```
{{% /tab %}}
{{< /tabs >}}

## Verify TLS termination traffic {#verify-tls-terminate}

{{< tabs items="Cloud Provider LoadBalancer,Port-forward for local testing" tabTotal="2" >}}
{{% tab tabName="Cloud Provider LoadBalancer" %}}
1. Get the external address of the gateway and save it in an environment variable.
   ```sh
   export INGRESS_GW_ADDRESS=$(kubectl get svc -n {{< reuse "docs/snippets/namespace.md" >}} tls-terminate -o jsonpath="{.status.loadBalancer.ingress[0]['hostname','ip']}")
   echo $INGRESS_GW_ADDRESS
   ```

2. Send a request to the `app.example.com` domain and verify that you get back a 200 HTTP response code. The TLS connection is terminated at the Gateway and the plain traffic is forwarded to the httpbin app.

   * **Load balancer IP**:
     ```sh
     curl -vik --resolve "app.example.com:8443:${INGRESS_GW_ADDRESS}" \
       --cacert example_certs/root.crt \
       https://app.example.com:8443/status/200
     ```

   * **Load balancer hostname**:
     ```sh
     curl -vik --resolve "app.example.com:8443:$(dig +short $INGRESS_GW_ADDRESS | head -n1)" \
       --cacert example_certs/root.crt \
       https://app.example.com:8443/status/200
     ```

   Example output:
   ```console
   * Request completely sent off
   < HTTP/1.1 200 OK
   HTTP/1.1 200 OK
   ...
   ```

{{% /tab %}}
{{% tab tabName="Port-forward for local testing" %}}
1. Port-forward the gateway service to your local machine.
   ```sh
   kubectl port-forward svc/tls-terminate -n {{< reuse "docs/snippets/namespace.md" >}} 8443:8443
   ```

2. Send a request to the `app.example.com` domain and verify that you get back a 200 HTTP response code.
   ```sh
   curl -vik --connect-to app.example.com:8443:localhost:8443 \
     --cacert example_certs/root.crt \
     https://app.example.com:8443/status/200
   ```

   Example output:
   ```console
   * Request completely sent off
   < HTTP/1.1 200 OK
   HTTP/1.1 200 OK
   ...
   ```

{{% /tab %}}
{{< /tabs >}}

## Cleanup

{{< reuse "docs/snippets/cleanup.md" >}}

{{< tabs items="Gateway listeners,ListenerSet" tabTotal="2" >}}
{{% tab tabName="Gateway listeners" %}}
```sh
kubectl delete -A gateways,tlsroutes,secret -l example=tls-terminate
rm -rf example_certs
```
{{% /tab %}}
{{% tab tabName="ListenerSet" %}}
```sh
kubectl delete -A gateways,tlsroutes,listenersets,secret -l example=tls-terminate
rm -rf example_certs
```
{{% /tab %}}
{{< /tabs >}}
