---
title: ExternalDNS & Cert Manager
weight: 520
description: Use kgateway with External DNS and Cert Manager. 
---

[ExternalDNS](https://github.com/kubernetes-sigs/external-dns) and [Cert Manager](https://github.com/cert-manager/cert-manager) are two well known integrations within the Kubernetes ecosystem that can be used in conjunction to automate the creation of TLS certificates. 

## Before you begin 

{{< reuse "docs/snippets/prereq.md" >}}

## Set up ExternalDNS
ExternalDNS is used to dynamically set up and control DNS records for discovered gateway and HTTP resources. When you create a gateway or HTTP resource, and you define a hostname, External DNS uses the external address that is assigned to the gateway's load balancer service that serves this hostname, and uses this information to create a DNS record in the DNS provider that you configured. 

You can later use Cert Manager to create TLS certificates for this hostname so that you can serve HTTPS traffic on your gateway. 

1. Create an HTTP route resource to expose httpbin on your domain. Replace `<my-domain.com>` with your domain. Note that you must own the domain to enable ExternalDNS to create DNS records on your behalf. 
   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.networking.k8s.io/v1
   kind: HTTPRoute
   metadata:
     name: httpbin
     namespace: httpbin
     labels:
       example: httpbin-route
   spec:
     parentRefs:
       - name: http
         namespace: {{< reuse "docs/snippets/ns-system.md" >}}
     hostnames:
       - "<my-domain.com>"
     rules:
       - backendRefs:
           - name: httpbin
             port: 8000
   EOF
   ```

2. Deploy the ExternalDNS components. The following example configures ExternalDNS to monitor gateway and HTTP route resources to determine the list of DNS records that must be created or changed. DNS records are set up in DigitalOcean. To find the ExternalDNS configuration for your DNS provider, see the  [Kubernetes documentation](https://kubernetes-sigs.github.io/external-dns/v0.14.0/#deploying-to-a-cluster).
   ```yaml
   cat <<EOF | kubectl apply -f -
   apiVersion: v1
   kind: ServiceAccount
   metadata:
     name: external-dns
     namespace: default
   ---
   apiVersion: rbac.authorization.k8s.io/v1
   kind: ClusterRole
   metadata:
     name: external-dns
   rules:
   - apiGroups: [""]
     resources: ["namespaces"]
     verbs: ["get","watch","list"]
   - apiGroups: ["gateway.networking.k8s.io"]
     resources: ["gateways","httproutes","grpcroutes","tlsroutes","tcproutes","udproutes"] 
     verbs: ["get","watch","list"]
   ---
   apiVersion: rbac.authorization.k8s.io/v1
   kind: ClusterRoleBinding
   metadata:
     name: external-dns
   roleRef:
     apiGroup: rbac.authorization.k8s.io
     kind: ClusterRole
     name: external-dns
   subjects:
   - kind: ServiceAccount
     name: external-dns
     namespace: default
   ---
   apiVersion: apps/v1
   kind: Deployment
   metadata:
     name: external-dns
   spec:
     replicas: 1
     selector:
       matchLabels:
         app: external-dns
     strategy:
       type: Recreate
     template:
       metadata:
         labels:
           app: external-dns
       spec:
         serviceAccountName: external-dns
         containers:
         - name: external-dns
           image: registry.k8s.io/external-dns/external-dns:v0.13.5
           args:
           - --source=gateway-httproute
           - --provider=digitalocean
           - --log-level=debug
           env:
           - name: DO_TOKEN
             value: "<my-token>"
   EOF
   ```

3. Wait for the DNS entry to get created. Note that depending on the DNS provider that you use, this process can take some time to complete. To verify that the DNS record is created, use the `dig` command as shown in the following example. 
   ```sh
   dig <my-domain.com>
   ```

   Example output for a successfully created DNS record: 
   ```console
   ;; ANSWER SECTION:
   <my-domain.com>	300	IN	A	164.90.241.80
   ```

## Set up Cert Manager
Cert Manager is a Kubernetes controller that helps you automate the process of obtaining and renewing certificates from various PKI providers, such as AWS Private CA, Google Cloud CA, or Vault. In this example, you learn how to install Cert Manager by using Helm and how to configure it to obtain TLS certificates for your domain from Let's Encrypt.

{{% callout type="info" %}}
To allow Cert Manager to use the {{< reuse "docs/snippets/k8s-gateway-api-name.md" >}}, you must set `--feature-gates=ExperimentalGatewayAPISupport=true` during the Helm installation.
{{% /callout %}}

1. Install Cert Manager.
   1. Add the Jetstack Helm repository.
      ```sh
      helm repo add jetstack https://charts.jetstack.io --force-update
      ```
   2. Install Cert Manager in your cluster.
      ```sh
      helm upgrade --install cert-manager jetstack/cert-manager --namespace cert-manager --create-namespace \
      --set "extraArgs={--feature-gates=ExperimentalGatewayAPISupport=true}" --set installCRDs=true
      ```
      
2. Create an issuer resource that represents the Certificate Authority (CA) that you want to use to issue the TLS certificates for your domain. In this example, you configure Cert Manager to obtain a Let's Encrypt certificate by using the ACME protocol. To automate domain validation and certificate issuance, you use the `http01` challenge. The `http01` challenge is designed to prove that you have control over your domain by requiring you to store a challenge token in your cluster so that Let's Encrypt can validate it. For more information about this challenge, see the [Let's Encrypt documentation](https://letsencrypt.org/docs/challenge-types/#http-01-challenge).
   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: cert-manager.io/v1
   kind: Issuer
   metadata:
     name: letsencrypt-http
     namespace: {{< reuse "docs/snippets/ns-system.md" >}}
   spec:
     acme:
       email: hello@world.com
       #You can switch to live URL if you are brave
       #server: https://acme-v02.api.letsencrypt.org/directory
       server: https://acme-staging-v02.api.letsencrypt.org/directory
       privateKeySecretRef:
         name: letsencrypt-http-issuer-account-key
       solvers:
         - http01:
             gatewayHTTPRoute:
               parentRefs:
                 - name: http
                   namespace: {{< reuse "docs/snippets/ns-system.md" >}}
                   kind: Gateway
   EOF
   ```  

3. Verify that your TLS certificates are created successfully. Note that depending on the CA that you use, this process might take a while to complete. 
   ```sh
   kubectl get issuer letsencrypt-http -n {{< reuse "docs/snippets/ns-system.md" >}}
   ```

   Example output for successfully issued TLS certificates: 
   ```console
    Status:
    Acme:
    Conditions:
        Last Transition Time:  2023-11-09T16:03:58Z
        Message:               The ACME account was registered with the ACME server
        Observed Generation:   1
        Reason:                ACMEAccountRegistered
        Status:                True
        Type:                  Ready
   ```
   
4. Verify that the TLS certificate was added to the secret that you configured in the Cert Manager issuer resource. 
    ```sh
    kubectl get secret letsencrypt-http-issuer-account-key -n {{< reuse "docs/snippets/ns-system.md" >}} -o yaml
    ```

## Configure an HTTPS listener on your gateway

1. Add an HTTPS listener to the gateway that you set up as part of the [Get started guide](/docs/quickstart/). Replace `<my-domain.com>` with your domain.
   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.networking.k8s.io/v1
   kind: Gateway
   metadata:
     name: http
     annotations:
       cert-manager.io/issuer: letsencrypt-http
     namespace: {{< reuse "docs/snippets/ns-system.md" >}}
   spec:
     gatewayClassName: kgateway
     listeners:
     - allowedRoutes:
         namespaces:
           from: All
       name: http
       port: 80
       protocol: HTTP
     - allowedRoutes:
         namespaces:
           from: All
       hostname: <my-hostname.com>
       name: https
       port: 443
       protocol: HTTPS
       tls:
         mode: Terminate
         certificateRefs:
           - name: letsencrypt-http-issuer-account-key
             kind: Secret
   EOF
   ```
   
2. Verify that the gateway is configured successfully. You can also review the external address that is assigned to the gateway. 
   ```sh
   kubectl get gateway http -n {{< reuse "docs/snippets/ns-system.md" >}}
   ```

   Example output for an AWS EKS cluster: 
   ```console
   NAME   CLASS          ADDRESS                                                                  PROGRAMMED   AGE
   http   kgateway  a3a6c06e2f4154185bf3f8af46abf22e-139567718.us-east-2.elb.amazonaws.com   True         93s
   ```

## Test your HTTPS listener

With the TLS certificate in place, you can now test your HTTPS listener. 

Send a curl request to the httpbin app on the domain that you configured. 

```sh
curl -vik https://<my-domain.com>/status/200
```

Example output:
```console
*   Trying 164.90.241.80:443...
* Connected to <my-domain.com> (164.90.241.80) port 443 (#0)
* ALPN: offers h2,http/1.1
* (304) (OUT), TLS handshake, Client hello (1):
* (304) (IN), TLS handshake, Server hello (2):
* (304) (IN), TLS handshake, Unknown (8):
* (304) (IN), TLS handshake, Certificate (11):
* (304) (IN), TLS handshake, CERT verify (15):
* (304) (IN), TLS handshake, Finished (20):
* (304) (OUT), TLS handshake, Finished (20):
* SSL connection using TLSv1.3 / AEAD-CHACHA20-POLY1305-SHA256
* ALPN: server accepted h2
* Server certificate:
*  subject: CN=<my-domain.com>
*  start date: Nov  9 15:32:59 2023 GMT
*  expire date: Feb  7 15:32:58 2024 GMT
*  issuer: C=US; O=Let's Encrypt; CN=R3
*  SSL certificate verify ok.
* using HTTP/2
* h2h3 [:method: GET]
* h2h3 [:path: /status/200]
* h2h3 [:scheme: https]
* h2h3 [:authority: <my-domain.com>]
* h2h3 [user-agent: curl/7.88.1]
* h2h3 [accept: */*]
* Using Stream ID: 1 (easy handle 0x12c812800)
> GET /status/200 HTTP/2
> Host: <my-domain.com>
> user-agent: curl/7.88.1
> accept: */*
>
< HTTP/2 200
HTTP/2 200
< access-control-allow-credentials: true
access-control-allow-credentials: true
< access-control-allow-origin: *
access-control-allow-origin: *
< date: Thu, 09 Nov 2023 17:28:17 GMT
date: Thu, 09 Nov 2023 17:28:17 GMT
< content-length: 0
content-length: 0
< x-envoy-upstream-service-time: 2
x-envoy-upstream-service-time: 2
< server: envoy
server: envoy

<
* Connection #0 to host <my-domain.com> left intact
```
