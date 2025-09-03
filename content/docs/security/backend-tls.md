---
title: Backend TLS
weight: 10
description: Originate a one-way TLS connection from the Gateway to a backend. 
---

Originate a one-way TLS connection from the Gateway to a backend. 

{{< callout type="warning" >}}
{{< reuse "docs/versions/warn-experimental.md" >}}
{{< /callout >}}

## About one-way TLS

When you configure a TLS listener on your Gateway, the Gateway typically terminates incoming TLS traffic and forwards the unencrypted traffic to the backend service. However, you might have a service that only accepts TLS connections, or you want to forward traffic a secured Backend service that is external to the cluster.

You can use the [{{< reuse "docs/snippets/k8s-gateway-api-name.md" >}} BackendTLSPolicy](https://gateway-api.sigs.k8s.io/api-types/backendtlspolicy/) to configure TLS origination from the Gateway to a service in the cluster. This policy supports simple, one-way TLS use cases. 

However, to additionally set up different hostnames on the Backend that you want to route to via SNI, or to originate TLS connections to an external backend, use the {{< reuse "docs/snippets/kgateway.md" >}} BackendConfigPolicy instead. 

## About this guide

In this guide, you learn how to use the BackendTLSPolicy and BackendConfigPolicy resources originate one-way TLS connections for the following services: 
* [**In-cluster service**](#in-cluster-service): An NGINX server that is configured with a self-signed TLS certificate and deployed to the same cluster as the Gateway. You use a BackendTLSPolicy to originate TLS connections to NGINX. 
* [**External service**](#external-service): The `httpbin.org` hostname, which represents an external service that you want to originate a TLS connection to. You use a BackendConfigPolicy resource to originate TLS connections to that hostname. 

## Before you begin

{{< reuse "docs/snippets/prereq-x-channel.md" >}}

## In-cluster service

Deploy an NGINX server in your cluster that is configured for TLS traffic. Then, instruct the gateway proxy to terminate TLS traffic at the gateway and originate a new TLS connection from the gateway proxy to the NGINX server. 

### Deploy the sample app

The following example uses an NGINX server with a self-signed TLS certificate. For the configuration, see the [test directory in the kgateway GitHub repository](https://github.com/kgateway-dev/kgateway/tree/{{< reuse "docs/versions/github-branch.md" >}}/test/kubernetes/e2e/features/backendtls/inputs).


1. Deploy the NGINX server with a self-signed TLS certificate.

   ```shell
   kubectl apply -f https://raw.githubusercontent.com/kgateway-dev/kgateway/refs/heads/main/test/kubernetes/e2e/features/backendtls/testdata/nginx.yaml
   ```

2. Verify that the NGINX server is running.

   ```shell
   kubectl get pods -l app.kubernetes.io/name=nginx
   ```

   Example output:

   ```
   NAME    READY   STATUS    RESTARTS   AGE
   nginx   1/1     Running   0          9s
   ```
   
### Create a BackendTLSPolicy {#create-backend-tls-policy}

Create the BackendTLSPolicy for the NGINX workload. For more information, see the [{{< reuse "docs/snippets/k8s-gateway-api-name.md" >}} docs](https://gateway-api.sigs.k8s.io/api-types/backendtlspolicy/).

1. Create a Kubernetes ConfigMap that has the public CA certificate for the NGINX server.

   ```shell
   kubectl apply -f- <<EOF
   {{< github url="https://raw.githubusercontent.com/kgateway-dev/kgateway/refs/heads/main/test/kubernetes/e2e/features/backendtls/testdata/configmap.yaml" >}}
   EOF
   ```

2. Create the BackendTLSPolicy.

   ```yaml
   kubectl apply -f - <<EOF
   apiVersion: gateway.networking.k8s.io/v1alpha3
   kind: BackendTLSPolicy
   metadata:
     name: nginx-tls-policy
     labels:
       app: nginx
   spec:
     targetRefs:
     - group: ""
       kind: Service
       name: nginx
       sectionName: "8443"
     validation:
       hostname: "example.com"
       caCertificateRefs:
       - group: ""
         kind: ConfigMap
         name: ca
   EOF
   ```

   {{< reuse "docs/snippets/review-table.md" >}}

   | Setting | Description |
   |---------|-------------|
   | `targetRefs` | The service that you want the Gateway to originate a TLS connection to, such as the NGINX server. <br><br>{{< icon name="agentgateway" >}}**Agentgateway proxies**: Even if you use a Backend for selector-based destinations, you still need to target the backing Service and the `sectionName` of the port that you want the policy to apply to.  |
   | `validation.hostname` | The hostname that matches the NGINX server certificate. |
   | `validation.caCertificateRefs` | The ConfigMap that has the public CA certificate for the NGINX server. |

3. Create an HTTPRoute that routes traffic to the NGINX server on the `example.com` hostname and HTTPS port 8443. Note that the parent Gateway is the sample `http` Gateway resource that you created [before you began](#before-you-begin).

   ```yaml
   kubectl apply -f - <<EOF
   apiVersion: gateway.networking.k8s.io/v1beta1
   kind: HTTPRoute
   metadata:
     name: nginx-route
     labels:
       app: nginx
   spec:
     parentRefs:
     - name: http
       namespace: {{< reuse "docs/snippets/namespace.md" >}}
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
   
   {{< tabs items="Cloud Provider LoadBalancer,Port-forward for local testing" tabTotal="2" >}}
   {{% tab tabName="Cloud Provider LoadBalancer" %}}
   ```sh
   curl -vi http://$INGRESS_GW_ADDRESS:8080/ -H "host: example.com:8080"
   ```
   {{% /tab %}}
   {{% tab tabName="Port-forward for local testing" %}}
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
   
2. Create a BackendTLSPolicy resource that originates a TLS connection to the Backend that you created in the previous step. To originate the TLS connection, you use known trusted CA certificates. 
   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.networking.k8s.io/v1alpha3	
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
       namespace: {{< reuse "docs/snippets/namespace.md" >}}
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
   
   {{< tabs items="Cloud Provider LoadBalancer,Port-forward for local testing" tabTotal="2">}}
   {{% tab tabName="Cloud Provider LoadBalancer" %}}
   ```sh
   curl -vi http://$INGRESS_GW_ADDRESS:8080/anything -H "host: httpbin-external.example" 
   ```
   {{% /tab %}}
   {{% tab tabName="Port-forward for local testing" %}}
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


## Cleanup

{{< reuse "docs/snippets/cleanup.md" >}}

### In-cluster service

1. Delete the NGINX server.

   ```yaml
   kubectl delete -f https://raw.githubusercontent.com/kgateway-dev/kgateway/refs/heads/main/test/kubernetes/e2e/features/backendtls/inputs/nginx.yaml
   ```
   
2. Delete the routing resources that you created for the NGINX server.
   
   ```sh
   kubectl delete backendtlspolicy,configmap,httproute -A -l app=nginx
   ```

3. If you want to re-create a BackendTLSPolicy after deleting one, restart the control plane.

   {{< callout type="warning" >}}
   Due to a [known issue](https://github.com/kgateway-dev/kgateway/issues/11146), if you don't restart the control plane, you might notice requests that fail with a `HTTP/1.1 400 Bad Request` error after creating the new BackendTLSPolicy.
   {{< /callout >}}

   ```sh
   kubectl rollout restart -n kgateway-system deployment/kgateway
   ```
   
### External service

Delete the resources that you created. 

```sh
kubectl delete httproute httpbin-org
kubectl delete backendtlspolicy httpbin-org
kubectl delete backed httpbin-org
```