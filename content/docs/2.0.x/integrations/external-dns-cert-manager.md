---
title: ExternalDNS and cert-manager
weight: 10
---

[ExternalDNS](https://github.com/kubernetes-sigs/external-dns) and [cert-manager](https://github.com/cert-manager/cert-manager) are two well-known integrations within the Kubernetes ecosystem that can be used in conjunction to automate the creation of TLS certificates. 

* **ExternalDNS**: Instead of manually editing your domain in your DNS provider to add load balancer IP addresses, you can use ExternalDNS to dynamically set up and control DNS records for discovered Gateway and HTTPRoute resources. When you define a hostname in an HTTPRoute resource, ExternalDNS uses the external address that is assigned to the Gateway's load balancer service that serves this hostname, and uses this information to create a DNS record in the DNS provider that you configured.
* **cert-manager**: You can then use cert-manager to quickly and programmatically generate certificates for your domain, and store them in a Kubernetes secret. By adding this certificates secret to the HTTPRoute on the Gateway for your domain, you can secure it for HTTPS traffic.

## Before you begin 

{{< reuse "docs/snippets/prereq.md" >}}

## Set up ExternalDNS

1. Save your domain in an environment variable. Note that you must own the domain to enable ExternalDNS to create DNS records on your behalf.
   ```sh
   export DOMAIN=<my-domain.com>

2. Create an HTTPRoute resource to expose httpbin on your domain.
   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.networking.k8s.io/v1
   kind: HTTPRoute
   metadata:
     name: httpbin
     namespace: httpbin
   spec:
     parentRefs:
       - name: http
         namespace: kgateway-system
     hostnames:
       - "${DOMAIN}"
     rules:
       - backendRefs:
           - name: httpbin
             port: 8000
   EOF
   ```

3. Deploy the following Kubernetes components required for ExternalDNS.
   ```yaml
   kubectl apply -f- <<EOF
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
   EOF
   ```
   
4. Create the deployment for ExternalDNS, which configures ExternalDNS to monitor Gateway and HTTPRoute resources to determine the list of DNS records that must be created or changed. Note that in the following example, DNS records are set up in DigitalOcean, in which you provide your token. If you use a different DNS provider, find the required ExternalDNS configuration settings in the [Kubernetes documentation](https://kubernetes-sigs.github.io/external-dns/v0.14.0/#deploying-to-a-cluster).
   ```yaml {linenos=table,hl_lines=[25,26,27,28,29],linenostart=1}
   kubectl apply -f- <<EOF
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
           - --log-level=debug
           # Change the following fields for your DNS provider details
           - --provider=digitalocean
           env:
           - name: DO_TOKEN
             value: "<digital-ocean-token>"
   EOF
   ```

5. Wait for the DNS entry to be created. Note that depending on the DNS provider you use, this process can take some time to complete. To verify that the DNS record is created, use the `dig` command as shown in the following example.
   ```sh
   dig ${DOMAIN}
   ```

   Example output for a successfully created DNS record: 
   ```console
   ;; ANSWER SECTION:
   ${DOMAIN}	300	IN	A	164.90.241.80
   ```

## Set up cert-manager

cert-manager is a Kubernetes controller that helps you automate the process of obtaining and renewing certificates from various PKI providers, such as AWS Private CA, Google Cloud CA, or Vault. In this example, you install cert-manager by using Helm and configure it to obtain TLS certificates for your domain from Let's Encrypt.

1. Install cert-manager.
   1. Add the Jetstack Helm repository.
      ```sh
      helm repo add jetstack https://charts.jetstack.io --force-update
      ```
   2. Install cert-manager in your cluster.
      ```sh
      helm upgrade --install cert-manager jetstack/cert-manager --namespace cert-manager --create-namespace \
      --set "extraArgs={--feature-gates=ExperimentalGatewayAPISupport=true}" --set installCRDs=true
      ```
      {{< callout type="info" >}}To allow cert-manager to use the {{< reuse "docs/snippets/k8s-gateway-api-name.md" >}}, you must set `--feature-gates=ExperimentalGatewayAPISupport=true` in the cert-manager Helm installation.{{< /callout >}}
      
2. Create an Issuer resource that represents the Certificate Authority (CA) that you want cert-manager to use to issue the TLS certificates for your domain.
   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: cert-manager.io/v1
   kind: Issuer
   metadata:
     name: letsencrypt-http
     namespace: kgateway-system
   spec:
     acme:
       email: <email_address>
       server: https://acme-staging-v02.api.letsencrypt.org/directory
       privateKeySecretRef:
         name: letsencrypt-http-issuer-account-key
       solvers:
         - http01:
             gatewayHTTPRoute:
               parentRefs:
                 - name: http
                   namespace: kgateway-system
                   kind: Gateway
   EOF
   ```  

   | Setting | Description |
   | -- | -- | 
   | `acme` | The protocol to use for issuing certificates. In this example, you configure cert-manager to obtain a Let's Encrypt certificate by using the ACME (Automated Certificate Management Environment) protocol. |
   | `email` | Provide an email address where you can receive Let's Encrypt notifications for certificate expiration and account recovery. |
   | `server` | The Let's Encrypt ACME server used for issuing certificates. The value `https://acme-staging-v02.api.letsencrypt.org/directory` uses the Let’s Encrypt staging environment to avoid hitting rate limits during testing. For production setups, use the `https://acme-v02.api.letsencrypt.org/directory` server instead. |
   | `privateKeySecretRef.name` | Using your email address, cert-manager automatically generates and stores an ACME private account key in a Kubernetes secret of this name. cert-manager then uses this key to authenticate with Let’s Encrypt. This example uses the name `letsencrypt-http-issuer-account-key` in the `kgateway-system` namespace. |
   | `solvers.http01` | To automate domain validation and certificate issuance, you use the HTTP-01 challenge. The HTTP-01 challenge is designed to prove that you have control over your domain by requiring you to store a challenge token in your cluster so that Let's Encrypt can validate it. For more information about this challenge, see the [Let's Encrypt documentation](https://letsencrypt.org/docs/challenge-types/#http-01-challenge). |
   | `gatewayHTTPRoute.parentRefs` | The reference to the Gateway resource to solve certificate challenges. This example uses the `http` Gateway that you created in the get started guide. |

3. Verify that your TLS certificates are created successfully. Note that depending on the CA that you use, this process might take a while to complete. 
   ```sh
   kubectl get issuer letsencrypt-http -n kgateway-system
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
   
4. Verify that the TLS certificate was added to the secret that you configured in the cert-manager issuer resource. 
   ```sh
   kubectl get secret letsencrypt-http-issuer-account-key -n kgateway-system -o yaml
   ```

## Configure an HTTPS listener on your gateway

1. Add the cert-manager annotation and an HTTPS listener to the `http` gateway that you set up as part of the [Get started guide](/docs/quickstart/).
   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.networking.k8s.io/v1
   kind: Gateway
   metadata:
     name: http
     annotations:
       cert-manager.io/issuer: letsencrypt-http
     namespace: kgateway-system
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
       hostname: ${DOMAIN}
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
   kubectl get gateway http -n kgateway-system
   ```

   Example output for an AWS EKS cluster: 
   ```console
   NAME   CLASS        ADDRESS                                                                  PROGRAMMED   AGE
   http   kgateway     a3a6c06e2f4154185bf3f8af46abf22e-139567718.us-east-2.elb.amazonaws.com   True         93s
   ```

## Test your HTTPS listener

With the TLS certificate in place, you can now test your HTTPS listener. 

Send an HTTPS curl request to the httpbin app on the domain that you configured. 

```sh
curl -vik https://${DOMAIN}/status/200
```

In the output, verify that the TLS handshake finishes, and that you get a 200 response code:
```console
*   Trying 164.90.241.80:443...
* Connected to ${DOMAIN} (164.90.241.80) port 443 (#0)
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
*  subject: CN=${DOMAIN}
*  start date: Nov  9 15:32:59 2023 GMT
*  expire date: Feb  7 15:32:58 2024 GMT
*  issuer: C=US; O=Let's Encrypt; CN=R3
*  SSL certificate verify ok.
* using HTTP/2
* h2h3 [:method: GET]
* h2h3 [:path: /status/200]
* h2h3 [:scheme: https]
* h2h3 [:authority: ${DOMAIN}]
* h2h3 [user-agent: curl/7.88.1]
* h2h3 [accept: */*]
* Using Stream ID: 1 (easy handle 0x12c812800)
> GET /status/200 HTTP/2
> Host: ${DOMAIN}
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
* Connection #0 to host ${DOMAIN} left intact
```

## Cleanup

{{< reuse "docs/snippets/cleanup.md" >}}

1. Remove the cert-manager annotation and HTTPS listener from the `http` Gateway.
   ```yaml
   kubectl apply -f- <<EOF
   kind: Gateway
   apiVersion: gateway.networking.k8s.io/v1
   metadata:
     name: http
     namespace: kgateway-system
   spec:
     gatewayClassName: kgateway
     listeners:
     - protocol: HTTP
       port: 8080
       name: http
       allowedRoutes:
         namespaces:
           from: All
   EOF
   ```

2. Delete the Issuer resource.
   ```sh
   kubectl delete Issuer letsencrypt-http -n kgateway-system
   ```

3. Delete the `letsencrypt-http-issuer-account-key` secret.
   ```sh
   kubectl delete secret letsencrypt-http-issuer-account-key -n kgateway-system
   ```

4. Remove cert-manager.
   ```sh
   kubectl uninstall cert-manager -n cert-manager
   kubectl delete ns cert-manager
   ```

5. Delete the ExternalDNS deployment and related resources.
   ```sh
   kubectl delete Deployment external-dns
   kubectl delete ClusterRoleBinding external-dns
   kubectl delete ClusterRole external-dns
   kubectl delete ServiceAccount external-dns
   ```

6. Optional: Delete the HTTPRoute that exposes httpbin on your domain.
   ```sh
   kubectl delete HTTPRoute httpbin -n httpbin
   ```