Originate a one-way TLS connection from the Gateway to a backend. 

{{< version include-if="2.0.x,2.1.x,2.2.x,2.3.x,2.4.x" >}}
> [!WARNING]
> {{< reuse "kgw-docs/versions/warn-experimental.md" >}}
{{< /version >}}

## About one-way TLS

When you configure a TLS listener on your Gateway, the Gateway typically terminates incoming TLS traffic and forwards the unencrypted traffic to the backend service. However, you might have a service that only accepts TLS connections, or you want to forward traffic to a secured Backend service that is external to the cluster.

You can use the [{{< reuse "kgw-docs/snippets/k8s-gateway-api-name.md" >}} BackendTLSPolicy](https://gateway-api.sigs.k8s.io/reference/api-types/policy/backendtlspolicy/) to configure TLS origination from the Gateway to a service in the cluster. This policy supports simple, one-way TLS use cases. 

However, to additionally set up different hostnames on the Backend that you want to route to via SNI, or to originate TLS connections to an external backend, use the {{< reuse "kgw-docs/snippets/kgateway.md" >}} BackendConfigPolicy instead. 

## About this guide

In this guide, you learn how to use the BackendTLSPolicy and BackendConfigPolicy resources originate one-way TLS connections for the following services: 
* [**In-cluster service**](#in-cluster-service): An NGINX server that is configured with a self-signed TLS certificate and deployed to the same cluster as the Gateway. You use a BackendTLSPolicy to originate TLS connections to NGINX. 
* [**External service**](#external-service): The `httpbin.org` hostname, which represents an external service that you want to originate a TLS connection to. You use a BackendConfigPolicy resource to originate TLS connections to that hostname. 

## Before you begin

{{< version include-if="2.0.x,2.1.x,2.2.x,2.3.x,2.4.x" >}}
{{< reuse "kgw-docs/snippets/prereq-x-channel.md" >}}
{{< /version >}}
{{< version exclude-if="2.0.x,2.1.x,2.2.x,2.3.x,2.4.x" >}}
{{< reuse "kgw-docs/snippets/prereq.md" >}}
{{< /version >}}

## In-cluster service

Deploy an NGINX server in your cluster that is configured for TLS traffic. Then, instruct the gateway proxy to terminate TLS traffic at the gateway and originate a new TLS connection from the gateway proxy to the NGINX server.

### Deploy the sample app

The following example uses an NGINX server with a self-signed TLS certificate. For the configuration, see the [test directory in the kgateway GitHub repository](https://raw.githubusercontent.com/kgateway-dev/kgateway/refs/heads/main/test/e2e/features/backendtls/testdata/nginx.yaml).


1. Create the namespace.

   ```shell
   kubectl create namespace kgateway-base
   ```

2. Deploy the NGINX server with a self-signed TLS certificate.

   ```shell
   kubectl apply -f https://raw.githubusercontent.com/kgateway-dev/kgateway/refs/heads/main/test/e2e/features/backendtls/testdata/nginx.yaml
   ```

3. Verify that the NGINX server is running.

   ```shell
   kubectl -n kgateway-base get pods -l app.kubernetes.io/name=nginx
   ```

   Example output:

   ```
   NAME    READY   STATUS    RESTARTS   AGE
   nginx   1/1     Running   0          9s
   ```
   
### Create a TLS policy {#create-backend-tls-policy}

Create a TLS policy for the NGINX workload. You can use the Gateway API BackendTLSPolicy for simple, one-way TLS connections. For more advanced TLS connections or simply to reduce the number of resources if you use other backend connections, create a BackendConfigPolicy instead.

{{< tabs >}}
{{% tab name="BackendConfigPolicy" %}}

1. Create a Kubernetes Secret that has the public CA certificate for the NGINX server.

   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: v1
   kind: Secret
   metadata:
     namespace: kgateway-base
     name: ca
     labels:
       app: nginx
   type: Opaque
   stringData:
     ca.crt: |
       -----BEGIN CERTIFICATE-----
       MIIDFTCCAf2gAwIBAgIUG9Mdv3nOQ2i7v68OgjArU4lhBikwDQYJKoZIhvcNAQEL
       BQAwFjEUMBIGA1UEAwwLZXhhbXBsZS5jb20wHhcNMjUwNzA3MTA0MDQwWhcNMjYw
       NzA3MTA0MDQwWjAWMRQwEgYDVQQDDAtleGFtcGxlLmNvbTCCASIwDQYJKoZIhvcN
       AQEBBQADggEPADCCAQoCggEBANueqwfAApjTfg+nxIoKVK4sK/YlNICvdoEq1UEL
       StE9wfTv0J27uNIsfpMqCx0Ni9Rjt1hzjunc8HUJDeobMNxGaZmryQofrdJWJ7Uu
       t5jeLW/w0MelPOfFLsDiM5REy4WuPm2X6v1Z1N3N5GR3UNDOtDtsbjS1momvooLO
       9WxPIr2cfmPqr81fyyD2ReZsMC/8lVs0PkA9XBplMzpSU53DWl5/Nyh2d1W5ENK0
       Zw1l5Ze4UGUeohQMa5cD5hmZcBjOeJF8MuSTi3167KSopoqfgHTvC5IsBeWXAyZF
       81ihFYAq+SbhUZeUlsxc1wveuAdBRzafcYkK47gYmbq1K60CAwEAAaNbMFkwFgYD
       VR0RBA8wDYILZXhhbXBsZS5jb20wCwYDVR0PBAQDAgeAMBMGA1UdJQQMMAoGCCsG
       AQUFBwMBMB0GA1UdDgQWBBSoa1Zu2o+pQ6sq2HcOjAglZkp01zANBgkqhkiG9w0B
       AQsFAAOCAQEADZq1EMw/jMl0z2LpPh8cXbP09BnfXhoFbpL4cFrcBNEyig0oPO0j
       YN1e4bfURNduFVnC/FDnZhR3FlAt8a6ozJAwmJp+nQCYFoDQwotSx12y5Bc9IXwd
       BRZaLgHYy2NjGp2UgAya2z23BkUnwOJwJNMCzuGw3pOsmDQY0diR8ZWmEYYEPheW
       6BVkrikzUNXv3tB8LmWzxV9V3eN71fnP5u39IM/UQsOZGRUow/8tvN2/d0W4dHky
       t/kdgLKhf4gU2wXq/WbeqxlDSpjo7q/emNl59v1FHeR3eITSSjESU+dQgRsYaGEn
       SWP+58ApfCcURLpMxUmxkO1ayfecNJbmSQ==
       -----END CERTIFICATE-----
   EOF
   ```

2. Create the TLS policy.

   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.kgateway.dev/v1alpha1
   kind: BackendConfigPolicy
   metadata:
     namespace: kgateway-base
     name: nginx-tls-policy
     labels:
       app: nginx
   spec:
     targetRefs:
     - group: ""
       kind: Service
       name: nginx
     tls:
       sni: "example.com"
       secretRef:
         name: ca
   EOF
   ```

   {{< reuse "kgw-docs/snippets/review-table.md" >}} For more information, see the [BackendConfigPolicy API docs]({{< link-hextra path="/reference/api/#backendconfigpolicy" >}}).

   | Setting | Description |
   |---------|-------------|
   | `targetRefs` | The service that you want the Gateway to originate a TLS connection to, such as the NGINX server. <br><br>**Agentgateway proxies**: Even if you use a Backend for selector-based destinations, you still need to target the backing Service and the `sectionName` of the port that you want the policy to apply to.  |
   | `tls.sni` | The Server Name Indication (SNI) hostname that matches the NGINX server certificate. The SNI is used during the TLS handshake to specify which certificate the server should present. |
   | `tls.secretRef` | The Kubernetes Secret that has the public CA certificate for the NGINX server. |

{{% /tab %}}

{{% tab name="BackendTLSPolicy" %}}

1. Create a Kubernetes ConfigMap that has the public CA certificate for the NGINX server.

   ```shell
   kubectl apply -f https://raw.githubusercontent.com/kgateway-dev/kgateway/refs/heads/main/test/e2e/features/backendtls/testdata/configmap.yaml
   ```

2. Create the TLS policy.{{< version include-if="2.0.x,2.1.x,2.2.x,2.3.x,2.4.x" >}} Note that to use the BackendTLSPolicy, you must have the experimental channel of the Kubernetes Gateway API version 1.4 or later.{{< /version >}}
   ```yaml
   kubectl apply -f - <<EOF
   apiVersion: gateway.networking.k8s.io/v1
   kind: BackendTLSPolicy
   metadata:
     namespace: kgateway-base
     name: nginx-tls-policy
     labels:
       app: nginx
   spec:
     targetRefs:
     - group: ""
       kind: Service
       name: nginx
     validation:
       hostname: "example.com"
       caCertificateRefs:
       - group: ""
         kind: ConfigMap
         name: ca
   EOF
   ```

   {{< reuse "kgw-docs/snippets/review-table.md" >}} For more information, see the [{{< reuse "kgw-docs/snippets/k8s-gateway-api-name.md" >}} docs](https://gateway-api.sigs.k8s.io/reference/api-types/policy/backendtlspolicy/).

   | Setting | Description |
   |---------|-------------|
   | `targetRefs` | The service that you want the Gateway to originate a TLS connection to, such as the NGINX server. <br><br>**Agentgateway proxies**: Even if you use a Backend for selector-based destinations, you still need to target the backing Service and the `sectionName` of the port that you want the policy to apply to.  |
   | `validation.hostname` | The hostname that matches the NGINX server certificate. |
   | `validation.caCertificateRefs` | The ConfigMap that has the public CA certificate for the NGINX server. |
{{% /tab %}}

{{< /tabs >}}

### Create an HTTPRoute {#create-http-route}

Create an HTTPRoute that routes traffic to the NGINX server on the `example.com` hostname and HTTPS port 8443. Note that the parent Gateway is the sample `http` Gateway resource that you created [before you began](#before-you-begin).

```yaml
kubectl apply -f - <<EOF
apiVersion: gateway.networking.k8s.io/v1beta1
kind: HTTPRoute
metadata:
  namespace: kgateway-base
  name: nginx-route
  labels:
    app: nginx
spec:
  parentRefs:
  - name: http
    namespace: {{< reuse "kgw-docs/snippets/namespace.md" >}}
  hostnames:
  - "example.com"
  rules:
  - backendRefs:
    - name: nginx
      port: 8443
EOF
```

### Verify the TLS connection {#verify-tls-connection}

Now that your TLS backend and routing resources are configured, verify the TLS connection.

1. Send a request to the NGINX server and verify that you get back a 200 HTTP response code. 
   
   {{< tabs >}}
   {{% tab name="Cloud Provider LoadBalancer" %}}
   ```sh
   curl -vi http://$INGRESS_GW_ADDRESS:8080/ -H "host: example.com:8080"
   ```
   {{% /tab %}}
   {{% tab name="Port-forward for local testing" %}}
   ```sh
   curl -vi http://localhost:8080/ -H "host: example.com:8080"
   ```
   {{% /tab %}}
   {{< /tabs >}}

   Example output: 
   ```
   * Host localhost:8080 was resolved.
   * IPv6: ::1
   * IPv4: 127.0.0.1
   *   Trying [::1]:8080...
   * Connected to localhost (::1) port 8080
   > GET / HTTP/1.1
   > Host: example.com:8080
   > User-Agent: curl/8.7.1
   > Accept: */*
   > 
   * Request completely sent off
   < HTTP/1.1 200 OK
   HTTP/1.1 200 OK
   ```

2. Enable port-forwarding on the Gateway.

   ```sh
   kubectl port-forward deploy/http -n kgateway-system 19000
   ```

3. In your browser, open the Envoy stats page at [http://127.0.0.1:19000/stats](http://127.0.0.1:19000/stats).

4. Search for the following stats that indicate the TLS connection is working. The count increases each time that the Gateway sends a request to the NGINX server.

   * `cluster.kube_default_nginx_8443.ssl.versions.TLSv1.2`: The number of TLSv1.2 connections from the Envoy gateway proxy to the NGINX server.
   * `cluster.kube_default_nginx_8443.ssl.handshake`: The number of successful TLS handshakes between the Envoy gateway proxy and the NGINX server.
   
## External service

Set up a Backend resource that represents your external service. Then, use a BackendTLSPolicy to instruct the gateway proxy to originate a TLS connection from the gateway proxy to the external service. 

> [!NOTE]
> If your gateway proxy runs inside an Istio service mesh, Istio's automatic mTLS can override the TLS settings from your BackendTLSPolicy or BackendConfigPolicy, causing backend TLS connections to fail. To prevent this failure, add the `kgateway.dev/disable-istio-auto-mtls: "true"` annotation to the Backend resource. For more information, see [Istio ingress]({{< link-hextra path="/integrations/istio/sidecar/ingress/" >}}).

1. Create a Backend resource that represents your external service. In this example, you use a static Backend that routes traffic to the `httpbin.org` site. Make sure to include the HTTPS port 443 so that traffic is routed to this port. 
   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.kgateway.dev/v1alpha1
   kind: Backend
   metadata:
     name: httpbin-org
     namespace: default
   spec:
     type: Static
     static:
       hosts:
       - host: httpbin.org
         port: 443
   EOF
   ```
   
2. Create a TLS policy that originates a TLS connection to the Backend that you created in the previous step. To originate the TLS connection, you use known trusted CA certificates. You can use the Gateway API BackendTLSPolicy for simple, one-way TLS connections. For more advanced TLS connections or simply to reduce the number of resources if you use other backend connections, create a BackendConfigPolicy instead. Note that the BackendConfigPolicy is only supported for Envoy-based kgateway proxies.
   
   {{< tabs >}}
   {{% tab name="BackendConfigPolicy" %}}
   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.kgateway.dev/v1alpha1
   kind: BackendConfigPolicy
   metadata:
     name: httpbin-org
     namespace: default
   spec:
     targetRefs:
       - name: httpbin-org
         kind: Backend
         group: gateway.kgateway.dev
     tls:
       sni: httpbin.org
       wellKnownCACertificates: System
   EOF
   ```
   {{% /tab %}}
   {{% tab name="BackendTLSPolicy" %}}
   {{< version include-if="2.0.x,2.1.x,2.2.x,2.3.x,2.4.x" >}}Note that to use the BackendTLSPolicy, you must have the experimental channel of the Kubernetes Gateway API version 1.4 or later.{{< /version >}}
   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.networking.k8s.io/v1
   kind: BackendTLSPolicy
   metadata:
     name: httpbin-org
     namespace: default
   spec:
     targetRefs:
       - name: httpbin-org
         kind: Backend
         group: gateway.kgateway.dev
     validation:
       hostname: httpbin.org
       wellKnownCACertificates: System
   EOF
   ```
   {{% /tab %}}
   {{< /tabs >}}

3. Create an HTTPRoute that rewrites traffic on the `httpbin-external.example` domain to the `httpbin.org` hostname and routes traffic to your Backend.  
   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.networking.k8s.io/v1
   kind: HTTPRoute
   metadata:
     name: httpbin-org
     namespace: default
   spec:
     parentRefs:
     - name: http
       namespace: {{< reuse "kgw-docs/snippets/namespace.md" >}}
     hostnames:
     - "httpbin-external.example"
     rules:
       - matches:
         - path:
             type: PathPrefix
             value: /anything
         backendRefs:
         - name: httpbin-org
           kind: Backend
           group: gateway.kgateway.dev
         filters:
         - type: URLRewrite
           urlRewrite:
             hostname: httpbin.org
   EOF
   ```

4. Send a request to the `httpbin-external.example` domain. Verify that the host is rewritten to `https://httpbin.org/anything` and that you get back a 200 HTTP response code.  
   
   {{< tabs >}}
   {{% tab name="Cloud Provider LoadBalancer" %}}
   ```sh
   curl -vi http://$INGRESS_GW_ADDRESS:8080/anything -H "host: httpbin-external.example" 
   ```
   {{% /tab %}}
   {{% tab name="Port-forward for local testing" %}}
   ```sh
   curl -vi http://localhost:8080/anything -H "host: httpbin-external.example" 
   ```
   {{% /tab %}}
   {{< /tabs >}}

   Example output: 
   ```console {hl_lines=[1,2,20]}
   < HTTP/1.1 200 OK
   HTTP/1.1 200 OK
   ...
   {
     "args": {}, 
     "data": "", 
     "files": {}, 
     "form": {}, 
     "headers": {
       "Accept": "*/*", 
       "Host": "httpbin.org", 
       "User-Agent": "curl/8.7.1", 
       "X-Amzn-Trace-Id": "Root=1-6881126a-03bfc90450805b9703e66e78", 
       "X-Envoy-Expected-Rq-Timeout-Ms": "15000", 
       "X-Envoy-External-Address": "10.0.15.215"
     }, 
     "json": null, 
     "method": "GET", 
     "origin": "10.0.X.XXX, 3.XXX.XXX.XXX", 
     "url": "https://httpbin.org/anything"
   }
   ```


{{< version exclude-if="2.0.x,2.1.x,2.2.x,2.3.x" >}}
## Other configurations {#other}

Review other configurations.

### TLS settings {#tls-settings}

Restrict the TLS settings that the gateway proxy uses when it originates the upstream TLS connection, such as the key exchange curves, the TLS version range, and the signature algorithms. These settings are useful when your backend requires specific parameters for compliance or security reasons, such as a P-384 ECDSA server certificate that the Envoy default ECDH curve list rejects. If you do not set a parameter, the Envoy default applies.

Set the parameters in the same policy that you created for the TLS connection in this guide. When a backend has both a BackendTLSPolicy and a BackendConfigPolicy, the BackendTLSPolicy takes precedence for TLS and the BackendConfigPolicy TLS settings are ignored.

{{< version exclude-if="2.0.x,2.1.x,2.2.x,2.3.x,2.4.x" >}}
The following table compares what each policy supports for TLS settings.

| Capability | BackendTLSPolicy | BackendConfigPolicy |
|------------|------------------|---------------------|
| ECDH curves, cipher suites, TLS version range, signature algorithms, and ALPN protocols | Supported through `spec.options` | Supported through `tls.parameters` and `tls.alpnProtocols` |
| Certificate hash verification | Supported through `kgateway.dev/verify-certificate-hash` | Not supported |
| Additional Subject Alternative Name verification | Not supported. The `kgateway.dev/verify-subject-alt-names` option is rejected because `spec.validation.hostname` already sets the required check. | Supported through `tls.verifySubjectAltNames` |
| SNI, skipping verification, client certificates from files, and renegotiation | Not supported | Supported through `tls.sni`, `tls.insecureSkipVerify`, `tls.files`, and `tls.allowRenegotiation` |
{{< /version >}}

The following examples update the `nginx-tls-policy` that you created earlier. The values in the examples are illustrative. Adjust them to match what your backend supports.

{{< version include-if="2.4.x" >}}
{{< reuse "kgw-docs/snippets/backend-tls-bcp-parameters.md" >}}
{{< /version >}}

{{< version exclude-if="2.0.x,2.1.x,2.2.x,2.3.x,2.4.x" >}}
{{< tabs >}}
{{% tab name="BackendConfigPolicy" %}}

{{< reuse "kgw-docs/snippets/backend-tls-bcp-parameters.md" >}}

{{% /tab %}}
{{% tab name="BackendTLSPolicy" %}}

Use `spec.options` in a BackendTLSPolicy resource to set the TLS settings. The options use the same `kgateway.dev/*` keys as Gateway listener TLS options. Each option takes a single string value, with list values separated by commas.

```yaml
kubectl apply -f- <<EOF
apiVersion: gateway.networking.k8s.io/v1
kind: BackendTLSPolicy
metadata:
  namespace: kgateway-base
  name: nginx-tls-policy
  labels:
    app: nginx
spec:
  targetRefs:
  - group: ""
    kind: Service
    name: nginx
  validation:
    hostname: "example.com"
    caCertificateRefs:
    - group: ""
      kind: ConfigMap
      name: ca
  options:
    kgateway.dev/ecdh-curves: "P-384,P-256"
    kgateway.dev/cipher-suites: "TLS_ECDHE_ECDSA_WITH_AES_256_GCM_SHA384,TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384"
    kgateway.dev/min-tls-version: "1.2"
    kgateway.dev/max-tls-version: "1.3"
    kgateway.dev/signature-algorithms: "ecdsa_secp256r1_sha256,rsa_pss_rsae_sha256"
    kgateway.dev/alpn-protocols: "http/1.1"
    kgateway.dev/verify-certificate-hash: "<SHA256_CERTIFICATE_HASH>"
EOF
```

{{< reuse "kgw-docs/snippets/review-table.md" >}} For the full list of TLS options, see [TLS listener settings]({{< link-hextra path="/setup/listeners/tls-settings/" >}}).

| Setting | Description |
|---------|-------------|
| `kgateway.dev/ecdh-curves` | A comma-delimited list of key exchange curves for the upstream TLS handshake. If the backend uses a P-384 ECDSA certificate, include `P-384` in this list. |
| `kgateway.dev/cipher-suites` | A comma-delimited list of cipher suites for the upstream TLS handshake. Cipher suites apply to TLS 1.2 and earlier. |
| `kgateway.dev/min-tls-version` | The minimum TLS version for the upstream TLS handshake. If you set this option to `1.3` and omit `kgateway.dev/max-tls-version`, the generated Envoy configuration also uses TLS 1.3 as the maximum. |
| `kgateway.dev/max-tls-version` | The maximum TLS version for the upstream TLS handshake. |
| `kgateway.dev/signature-algorithms` | A comma-delimited list of TLS signature algorithms that the gateway proxy advertises during the upstream TLS handshake. |
| `kgateway.dev/alpn-protocols` | A comma-delimited list of Application-Layer Protocol Negotiation (ALPN) protocols that the gateway proxy offers to the backend. If you do not set this option and the Service port has no `appProtocol`, the proxy negotiates HTTP/2 or HTTP/1.1 through ALPN. For more information, see [HTTP version](#http-version). |
| `kgateway.dev/verify-certificate-hash` | The SHA-256 hash of the backend certificate, in hex format. The backend certificate must match this hash. Replace `<SHA256_CERTIFICATE_HASH>` with the hash of your backend certificate. |

{{% /tab %}}
{{< /tabs >}}

### HTTP version {#http-version}

If you attach a BackendTLSPolicy to a Service and the Service port has no `appProtocol`, the gateway proxy offers HTTP/2 and HTTP/1.1 during the TLS handshake (ALPN) and uses the version that the backend selects. The proxy uses HTTP/2 if the backend supports it. For example, a backend such as an NGINX server that has HTTP/2 enabled on its TLS port is reached over HTTP/2. Previously, the gateway proxy always used HTTP/1.1 for these backends.

To always use HTTP/1.1, set the `appProtocol` of the Service port to `http`. The following example sets the `appProtocol` for the HTTPS port of the NGINX service from this guide, which is the second port of the Service.

```sh
kubectl patch service nginx -n kgateway-base --type='json' \
  -p='[{"op":"add","path":"/spec/ports/1/appProtocol","value":"http"}]'
```

For more information about the `appProtocol` setting, see [HTTP/2 upstream]({{< link-hextra path="/traffic-management/http2/" >}}).
{{< /version >}}

{{< /version >}}

## Cleanup

{{< reuse "kgw-docs/snippets/cleanup.md" >}}

### In-cluster service

{{< tabs >}}
{{% tab name="BackendConfigPolicy" %}}
1. Delete the NGINX server.

   ```yaml
   kubectl delete -f https://raw.githubusercontent.com/kgateway-dev/kgateway/refs/heads/main/test/e2e/features/backendtls/testdata/nginx.yaml
   ```
   
2. Delete the routing resources that you created for the NGINX server.
   
   ```sh
   kubectl -n kgateway-base delete backendconfigpolicy,secret,httproute -A -l app=nginx
   ```
{{% /tab %}}
{{% tab name="BackendTLSPolicy" %}}
1. Delete the NGINX server.

   ```yaml
   kubectl delete -f https://raw.githubusercontent.com/kgateway-dev/kgateway/refs/heads/main/test/e2e/features/backendtls/testdata/nginx.yaml
   ```
   
2. Delete the routing resources that you created for the NGINX server.
   
   ```sh
   kubectl -n kgateway-base delete backendtlspolicy,configmap,httproute -A -l app=nginx
   ```

3. If you want to re-create a BackendTLSPolicy after deleting one, restart the control plane.

   **Note**: Due to a [known issue](https://github.com/kgateway-dev/kgateway/issues/11146), if you don't restart the control plane, you might notice requests that fail with a `HTTP/1.1 400 Bad Request` error after creating the new BackendTLSPolicy.

   ```sh
   kubectl rollout restart -n kgateway-system deployment/{{< reuse "kgw-docs/snippets/pod-name.md" >}}
   ```
{{% /tab %}}
{{< /tabs >}}


### External service

Delete the resources that you created. 

{{< tabs >}}
{{% tab name="BackendConfigPolicy" %}}
```sh
kubectl delete httproute httpbin-org
kubectl delete backendconfigpolicy httpbin-org
kubectl delete backend httpbin-org
```
{{% /tab %}}
{{% tab name="BackendTLSPolicy" %}}
```sh
kubectl delete httproute httpbin-org
kubectl delete backendtlspolicy httpbin-org
kubectl delete backend httpbin-org
```
{{% /tab %}}
{{< /tabs >}}



