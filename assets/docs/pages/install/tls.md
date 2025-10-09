Enable server-side TLS encryption for the xDS gRPC server in the {{< reuse "docs/snippets/kgateway.md" >}} control plane. For more information about the server, see the [Architecture]({{< link-hextra path="/about/architecture" >}}) docs.

TLS encryption is disabled by default. When enabled, the control plane mounts a `kgateway-xds-cert` TLS secret that you create and propogates the CA bundle to any kgateway and agentgateway data plane proxies to establish a secure connection. You might integrate your secret with a provider such as [cert-manager](https://cert-manager.io/docs/) to automate certificate management and rotation.

## Before you begin

{{< reuse "docs/snippets/prereq.md" >}}

## Step 1: Set up cert-manager {#cert-manager}

cert-manager is a Kubernetes controller that helps you automate the process of obtaining and renewing certificates from various PKI providers, such as AWS Private CA, Google Cloud CA, or Vault. In this example, you set up cert-manager to provide self-signed certificates for the {{< reuse "docs/snippets/kgateway.md" >}} control plane.

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

3. Create a self-signed Certificate Authority (CA) that acts as the root of trust for the xDS gRPC server certificates. For production environments, replace the self-signed root issuer with your organization's CA issuer, such as Vault or a cloud CA service. For more information, see the [cert-manager CA issuer docs](https://cert-manager.io/docs/configuration/issuers/).

   ```yaml
   kubectl apply -f - <<EOF
   apiVersion: cert-manager.io/v1
   kind: Issuer
   metadata:
     name: kgateway-xds-root-issuer
     namespace: {{< reuse "docs/snippets/namespace.md" >}}
   spec:
     selfSigned: {}
   ---
   apiVersion: cert-manager.io/v1
   kind: Certificate
   metadata:
     name: kgateway-xds-ca
     namespace: {{< reuse "docs/snippets/namespace.md" >}}
   spec:
     secretName: kgateway-xds-ca-secret
     issuerRef:
       name: kgateway-xds-root-issuer
       kind: Issuer
     isCA: true
     commonName: kgateway-xds-ca
     duration: 10m
     renewBefore: 2m
     privateKey:
       algorithm: RSA
       size: 2048
   EOF
   ```

4. Use the CA to sign a TLS certificate for the xDS gRPC server. The certificate must be named `kgateway-xds-cert`. This two-tiered approach keeps the root CA separate from the server certificate, and lets the server certificate be rotated independently of the CA. 
   
   {{< callout type="note" >}}**Note**: The DNS names in the server certificate must match the service endpoints of the control plane. If you install the control plane in a different namespace, you must update the DNS names to match the actual service endpoints.{{< /callout >}}
   
   ```yaml
   kubectl apply -f - <<EOF
   apiVersion: cert-manager.io/v1
   kind: Issuer
   metadata:
     name: kgateway-xds-ca-issuer
     namespace: {{< reuse "docs/snippets/namespace.md" >}}
   spec:
     ca:
       secretName: kgateway-xds-ca-secret
   ---
   apiVersion: cert-manager.io/v1
   kind: Certificate
   metadata:
     name: kgateway-xds-cert
     namespace: {{< reuse "docs/snippets/namespace.md" >}}
   spec:
     secretName: kgateway-xds-tls
     issuerRef:
       name: kgateway-xds-ca-issuer
       kind: Issuer
     isCA: false
     dnsNames:
     - {{< reuse "/docs/snippets/helm-kgateway.md" >}}
     - {{< reuse "/docs/snippets/helm-kgateway.md" >}}.{{< reuse "docs/snippets/namespace.md" >}}
     - {{< reuse "/docs/snippets/helm-kgateway.md" >}}.{{< reuse "docs/snippets/namespace.md" >}}.svc
     - {{< reuse "/docs/snippets/helm-kgateway.md" >}}.{{< reuse "docs/snippets/namespace.md" >}}.svc.cluster.local
     duration: 5m
     renewBefore: 2m
     privateKey:
       algorithm: RSA
       size: 2048
   EOF
   ```

## Step 2: Update the control plane to use TLS {#control-plane}

Upgrade {{< reuse "docs/snippets/kgateway.md" >}} with TLS enabled for the controller. For complete steps, review the [Upgrade guide]({{< link-hextra path="/operations/upgrade" >}}).

1. Set your version of {{< reuse "/docs/snippets/kgateway.md" >}} in an environment variable, such as the latest patch version (`{{< reuse "docs/versions/n-patch.md" >}}`).
   
   ```sh
   export NEW_VERSION={{< reuse "docs/versions/n-patch.md" >}}
   ```

2. Get the Helm values file for your current version.
      
   ```sh
   helm get values {{< reuse "/docs/snippets/helm-kgateway.md" >}} -n {{< reuse "docs/snippets/namespace.md" >}} -o yaml > values.yaml
   open values.yaml
   ```

3. Add the following values to the Helm values file to enable TLS for the xDS gRPC server.
   ```yaml
   controller:
     xds:
       tls:
         enabled: true
   ```

4. Upgrade your Helm installation.

   ```sh
   helm upgrade -i -n {{< reuse "docs/snippets/namespace.md" >}} {{< reuse "/docs/snippets/helm-kgateway.md" >}} oci://{{< reuse "/docs/snippets/helm-path.md" >}}/charts/{{< reuse "/docs/snippets/helm-kgateway.md" >}} \
     -f values.yaml \
     --version {{< reuse "docs/versions/helm-version-upgrade.md" >}} 
   ```

5. Confirm that the {{< reuse "/docs/snippets/kgateway.md" >}} control plane is up and running. 
   
   ```sh
   kubectl get pods -n {{< reuse "docs/snippets/namespace.md" >}}
   ```

## Step 3: Verify the TLS connection {#verify-tls-connection}

Now that the control plane is up and running, verify the TLS connection.

1. Port-forward the control plane deployment.

   ```sh
   kubectl port-forward -n {{< reuse "docs/snippets/namespace.md" >}} svc/{{< reuse "/docs/snippets/helm-kgateway.md" >}} 9092
   ```

2. Send a request to the control plane. Because you do not have a valid JWT, you get back an `authentication failed` error.

   ```
   grpcurl -cacert ca.crt -servername {{< reuse "/docs/snippets/helm-kgateway.md" >}}.{{< reuse "docs/snippets/namespace.md" >}}.svc.cluster.local localhost:9977 list
   ```

3. Send a request to the metrics endpoint to check for `xds_auth` metrics.

   ```sh
   curl localhost:9092/metrics | grep xds_auth
   ```

   Example output:

   ```
   # HELP kgateway_xds_auth_rq_success_total Total number of successful xDS auth requests
   # TYPE kgateway_xds_auth_rq_success_total counter
   kgateway_xds_auth_rq_success_total 5
   # HELP kgateway_xds_auth_rq_total Total number of xDS auth requests
   # TYPE kgateway_xds_auth_rq_total counter
   kgateway_xds_auth_rq_total 5
   ```
