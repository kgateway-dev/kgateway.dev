---
title: Configuring HTTPS routes with the Gateway API
toc: false
publishDate: 2025-03-14T00:00:00-00:00
author: Eitan Suez & Brian Jimerson
excludeSearch: true
---

In the [previous blog](https://kgateway.dev/blog/introduction-to-kubernetes-gateway-api/), we explored a straightforward example of configuring an ingress route for a workload running in Kubernetes. That example focused on simplicity by utilizing a single Gateway listener with the HTTP protocol. 

In this blog, we will expand on that foundation by demonstrating how to configure an HTTPs route. 

## Configuring TLS Certificates

To service HTTPS traffic, a TLS certificate must be associated with the hostname for the application. There are various methods to generate TLS certificates, ranging from simple tools such as `openssl` and the [step CLI](https://smallstep.com/docs/step-cli/) to more automated solutions such as 'cert-manager' in Kubernetes. 

[Cert-manager](https://cert-manager.io/) simplifies certificate management by introducing Custom Resource Definitions (CRDs) to configure certificate issuers and the certificates to be created. The project automates the process of certificate generation by contacting the issuer and minting the certificates, subsequently generating the Kubernetes TLS secrets that contain the certificates.

A key advantage of `cert-manager` is its ability to automate certificate rotation at a specified duration before expiration. The only remaining task is to reference the secret in the listener configuration.

Let us study an example gateway configuration.

## Defining the Gateway

The following example demonstrates how to configure a Gateway with an HTTPS listener:
```yaml
kind: Gateway
apiVersion: gateway.networking.k8s.io/v1
metadata:
  name: my-gateway
spec:
  gatewayClassName: kgateway
  listeners:
  - name: http
    protocol: HTTP
    port: 80
  - name: https
    protocol: HTTPS
    port: 443
    hostname: httpbin.example.com
    tls:
      mode: Terminate
      certificateRefs:
      - name: httpbin-cert
```
Above, we define a gateway with an HTTPS listener on port 443, serving traffic for `httpbin.example.com.` The `tls` configuration references a secret named `httpbin-cert` which we should have previously created.

We can choose between two modes: `Terminate` or `Passthrough`.

In cases where the backing workload is designed to handle the TLS request directly, the Gateway can be configured to pass the traffic through, encrypted. Best practice is to terminate TLS at the Gateway, and to use a service mesh for internal communication inside the cluster, including for the traffic from the Gateway to the backing workload. 

With service meshes we can then take advantage of the automatic mutual TLS communication which not only encrypts the internal traffic, but also provides workload identity information to the parties involved in the communication. We will discuss the service mesh scenario in a future writeup.

The configuration we show above is sufficient to provision a gateway and to have the HTTPS listener serve the certificate in question to any clients that request endpoints associated with the host named `httpbin.example.com`.

Next, let us study a route definition.

### Defining Routes 

The following example illustrates an HTTPRoute resource that directs traffic to a backend service:
```yaml
apiVersion: gateway.networking.k8s.io/v1
kind: HTTPRoute
metadata:
  name: httpbin
spec:
  parentRefs:
  - name: my-gateway
    sectionName: https
  hostnames:
  - httpbin.example.com
  rules:
  - backendRefs:
    - name: httpbin
      port: 8000
```
Above is an example of a simple route configuration that directs any request destined for the hostname in question to a backing service named `httpbin` running in our Kubernetes cluster.

The `sectionName` specification above provides a way to bind a route not to the gateway as a whole, but to a specific listener. This guarantees that plain-text requests over HTTP have no routing rules in place and the call must be made over HTTPS.

It is best practice to redirect clients who erroneously attempt to call the service via HTTP and to redirect the request to the correct HTTPS scheme

### Redirecting HTTP to HTTPS

Below is a second route configuration, this route binds to the HTTP listener on port 80:
```yaml
apiVersion: gateway.networking.k8s.io/v1
kind: HTTPRoute
metadata:
  name: httpbin-redirect-to-https
spec:
  hostnames:
  - httpbin.example.com
  parentRefs:
  - name: my-gateway
    sectionName: http
  rules:
  - filters:
    - type: RequestRedirect
      requestRedirect:
        scheme: https
        statusCode: 301
```
Above we see a first example of the use of a filter in the context of defining routing rules.

As its name implies, the `RequestRedirect` filter can be used to respond with a `location` header to redirect the request.

For HTTP to HTTPS redirects it's customary to return a 301 "Moved Permanently" response code.

A great feature here is that the full URL of the request is preserved, and only the scheme is altered. For example, a request to `http://httpbin.example.com/json` ends up being redirected to `https://httpbin.example.com/json`.

### Automating Certification Creation and Management

The `cert-manager` project supports the [Gateway API](https://cert-manager.io/docs/usage/gateway/). This support is enabled with the feature flag `config.enableGatewayAPI`. 

By adding a `cert-manager` specific annotation associating the certificate issuer with the Gateway, we're instructing `cert-manager` to call out to the issuer and generate a certificate for the host names associated with its listeners, and to create the TLS secret whose name is referenced in the `tls` configuration for that listener.

Here is an example:
```yaml
kind: Gateway
apiVersion: gateway.networking.k8s.io/v1
metadata:
  name: my-gateway
  annotations:
    cert-manager.io/cluster-issuer: my-ca-issuer
spec:
  gatewayClassName: gloo-gateway
  listeners:
  - name: http
    protocol: HTTP
    port: 80
  - name: https
    protocol: HTTPS
    port: 443
    hostname: httpbin.example.com
    tls:
      mode: Terminate
      certificateRefs:
      - name: httpbin-cert
```
Above, `cert-manager` will be responsible for creating the secret `httpbin-cert` containing the certificate for the hostname `httpbin.example.com`, using a predefined certificate issuer by the name of `my-ca-issuer`.

### Summary

The Kubernetes Gateway API offers a simple and streamlined approach to configuring gateways incorporating HTTPS listeners. From the examples provided, adapting this configuration to an enterprise environment is easily achievable by incorporating listeners for supplementary hostnames that have routing rules directing traffic towards other backend APIs or applications. You can get [hands-on experience](https://www.solo.io/resources/lab/configure-https-with-the-gateway-api-and-kgateway) on HTTP route configuration with Gateway API in our free technical labs or watch the [quick demo video below](https://youtu.be/cOnL9vjVRvQ) for more information.

<br>
{{< youtube cOnL9vjVRvQ >}}
