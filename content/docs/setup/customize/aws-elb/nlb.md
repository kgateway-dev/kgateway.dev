---
title: AWS NLB
weight: 20
---

In this guide you explore how to expose the {{< reuse "docs/snippets/product-name.md" >}} proxy with an AWS network load balancer (NLB). The following use cases are covered:

* **NLB HTTP**: Create an HTTP listener on the NLB that exposes an HTTP endpoint on your gateway proxy. Traffic from the NLB to the proxy is not secured. 
* **TLS passthrough**: Expose an HTTPS endpoint of your gateway with an NLB. The NLB passes through HTTPS traffic to the gateway proxy where the traffic is terminated. 

{{< callout type="warning" >}}
Keep in mind the following considerations when working with an NLB:
* An AWS NLB has an idle timeout of 350 seconds that you cannot change. This limitation can increase the number of reset TCP connections.
<!-- TODO HTTPListenerPolicy healthcheck
* {{< reuse "docs/snippets/product-name-caps.md" >}} does not open any proxy ports until at least one HTTPRoute resource is created that references the gateway. However, AWS ELB health checks are automatically created and run after you create the gateway. Because of this, registered targets might appear unhealthy until an HTTPRoute resource is created. 
-->
{{< /callout >}}

## Before you begin

1. Create or use an existing AWS account. 
2. Follow the [Get started guide](/docs/quickstart/) to install {{< reuse "docs/snippets/product-name.md" >}}, set up a gateway resource, and deploy the httpbin sample app.

## Step 1: Deploy the AWS Load Balancer controller

{{< reuse "docs/snippets/aws-elb-controller-install.md" >}}
   
## Step 2: Deploy your gateway proxy

1. Create a GatewayParameters resource with custom AWS annotations. These annotations instruct the AWS load balancer controller to expose the gateway proxy with a public-facing AWS NLB. 
   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.kgateway.dev/v1alpha1
   kind: GatewayParameters
   metadata:
     name: custom-gw-params
     namespace: {{< reuse "docs/snippets/ns-system.md" >}}
   spec:
     kube: 
       service:
         extraAnnotations:
           service.beta.kubernetes.io/aws-load-balancer-type: "external" 
           service.beta.kubernetes.io/aws-load-balancer-scheme: internet-facing 
           service.beta.kubernetes.io/aws-load-balancer-nlb-target-type: "instance"
   EOF
   ```
   
   | Setting | Description | 
   | -- | -- | 
   | `aws-load-balancer-type: "external"` | Instruct Kubernetes to pass the Gateway's service configuration to the AWS load balancer controller that you created earlier instead of using the built-in capabilities in Kubernetes. For more information, see the [AWS documentation](https://kubernetes-sigs.github.io/aws-load-balancer-controller/v2.2/guide/service/nlb/#configuration). | 
   | `aws-load-balancer-scheme: internet-facing ` | Create the NLB with a public IP addresses that is accessible from the internet. For more information, see the [AWS documentation](https://kubernetes-sigs.github.io/aws-load-balancer-controller/v2.2/guide/service/nlb/#prerequisites).  | 
   | `aws-load-balancer-nlb-target-type: "instance"` | Use the Gateway's instance ID to register it as a target with the NLB. For more information, see the [AWS documentation](https://kubernetes-sigs.github.io/aws-load-balancer-controller/v2.2/guide/service/nlb/#instance-mode_1).  | 
   
2. Depending on the annotations that you use on your gateway proxy, you can configure the NLB in different ways. 

   {{< tabs items="Simple HTTP NLB,TLS passthrough" >}}
   {{% tab %}}

   Create a simple NLB that accepts HTTP traffic on port 80 and forwards this traffic to the HTTP listener on your gateway proxy. 

   {{< reuse-image src="/img/elb-http.svg" >}}

   This Gateway resource references the custom GatewayParameters resource that you created.
   ```yaml
   kubectl apply -f- <<EOF
   kind: Gateway
   apiVersion: gateway.networking.k8s.io/v1
   metadata:
     name: aws-cloud
     namespace: {{% reuse "docs/snippets/ns-system.md" %}}
     annotations:
       gateway.kgateway.dev/gateway-parameters-name: custom-gw-params
   spec:
     gatewayClassName: kgateway
     listeners:
     - protocol: HTTP
       port: 80
       name: http
       allowedRoutes:
         namespaces:
           from: All
   EOF
   ```

   {{% /tab %}}
   {{% tab %}}
   Pass through HTTPS requests from the AWS NLB to your gateway proxy, and terminate TLS traffic at the gateway proxy for added security. 

   {{< reuse-image src="/img/elb-tls-passthrough.svg" >}}

   1. Create a self-signed TLS certificate to configure your gateway proxy with an HTTPS listener. 
      {{< reuse "docs/snippets/listeners-https-create-cert.md" >}}

   2. Create a Gateway with an HTTPS listener that terminates incoming TLS traffic. Make sure to reference the custom GatewayParameters resource and the Kubernetes secret that contains the TLS certificate information. 
      ```yaml
      kubectl apply -f- <<EOF
      apiVersion: gateway.networking.k8s.io/v1
      kind: Gateway
      metadata:
        name: aws-cloud
        namespace: {{< reuse "docs/snippets/ns-system.md" >}}
        labels:
          gateway: aws-cloud
        annotations:
          gateway.kgateway.dev/gateway-parameters-name: "custom-gw-params"
      spec:
        gatewayClassName: kgateway
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
   {{% /tab %}}
   {{< /tabs >}}

3. Verify that your gateway is created. 
   ```sh
   kubectl get gateway aws-cloud -n {{< reuse "docs/snippets/ns-system.md" >}}
   ```
   
4. Verify that the gateway service is exposed with an AWS NLB and assigned an AWS hostname. 
   ```sh
   kubectl get services aws-cloud -n {{< reuse "docs/snippets/ns-system.md" >}}
   ```
   
   Example output: 
   ```console
   NAME        TYPE           CLUSTER-IP      EXTERNAL-IP                                                                     PORT(S)        AGE
   aws-cloud   LoadBalancer   172.20.39.233   k8s-kgateway-awscloud-edaaecf0c5-2d48d93624e3a4bf.elb.us-east-2.amazonaws.com   80:30565/TCP   12s
   ```

5. Review the NLB in the AWS EC2 dashboard. 
   1. Go to the [AWS EC2 dashboard](https://console.aws.amazon.com/ec2). 
   2. In the left navigation, go to **Load Balancing > Load Balancers**.
   3. Find and open the ALB that was created for you, with a name such as `k8s-kgateway-awscloud-<hash>`.
   4. On the **Resource map** tab, verify that the load balancer points to EC2 targets in your cluster. For example, you can click on the target EC2 name to verify that the instance summary lists your cluster name.

<!-- TODO HTTPListenerPolicy healthcheck
{{< callout type="info" >}}
{{< reuse "docs/snippets/product-name-caps.md" >}} does not open any proxy ports until at least one HTTPRoute is associated with the gateway. The AWS ELB health checks are automatically created when you create the Gateway resource and might report that the gateway proxy is unhealthy. Continue with this guide to create an HTTPRoute resource and send traffic through the NLB.
{{< /callout >}}-->

## Step 3: Test traffic to the NLB {#test-traffic}

{{< tabs items="Simple HTTP NLB,TLS passthrough" >}}
{{% tab %}}
   
1. Create an HTTPRoute resource and associate it with the gateway that you created. 
   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.networking.k8s.io/v1
   kind: HTTPRoute
   metadata:
     name: httpbin-elb
     namespace: httpbin
     labels:
       example: httpbin-route
   spec:
     parentRefs:
       - name: aws-cloud
         namespace: {{< reuse "docs/snippets/ns-system.md" >}}
     hostnames:
       - "www.nlb.com"
     rules:
       - backendRefs:
           - name: httpbin
             port: 8000
   EOF
   ```

2. Get the AWS hostname of the NLB. 
   ```sh
   export INGRESS_GW_ADDRESS=$(kubectl get svc -n {{< reuse "docs/snippets/ns-system.md" >}} aws-cloud -o jsonpath='{.status.loadBalancer.ingress[0].hostname}')
   echo $INGRESS_GW_ADDRESS
   ```

3. Send a request to the httpbin app. 
   ```sh
   curl -vik http://$INGRESS_GW_ADDRESS:80/headers -H "host: www.nlb.com:80"
   ```
   
   Example output: 
   ```console
   ...
   < HTTP/1.1 200 OK
   HTTP/1.1 200 OK
   ```

{{% /tab %}}
{{% tab %}}

1. Create an HTTPRoute resource and associate it with the gateway that you created. 
   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.networking.k8s.io/v1
   kind: HTTPRoute
   metadata:
     name: httpbin-elb
     namespace: httpbin
     labels:
       example: httpbin-route
   spec:
     parentRefs:
       - name: aws-cloud
         namespace: {{< reuse "docs/snippets/ns-system.md" >}}
     hostnames:
       - "https.example.com"
     rules:
       - backendRefs:
           - name: httpbin
             port: 8000
   EOF
   ```

2. Get the IP address that is associated with the NLB's AWS hostname. 
   ```sh
   export INGRESS_GW_HOSTNAME=$(kubectl get svc -n {{< reuse "docs/snippets/ns-system.md" >}} aws-cloud -o jsonpath='{.status.loadBalancer.ingress[0].hostname}')
   echo $INGRESS_GW_HOSTNAME
   export INGRESS_GW_ADDRESS=$(dig +short ${INGRESS_GW_HOSTNAME} | head -1)
   echo $INGRESS_GW_ADDRESS
   ```

3. Send a request to the httpbin app. Verify that you see a successful TLS handshake and that you get back a 200 HTTP response code from the httpbin app. 
   ```sh
   curl -vik --resolve "https.example.com:443:${INGRESS_GW_ADDRESS}" https://https.example.com:443/status/200
   ```
   
   Example output: 
   ```console
   * Hostname https.example.com was found in DNS cache
   *   Trying 3.XX.XXX.XX:443...
   * Connected to https.example.com (3.XX.XXX.XX) port 443 (#0)
   * ALPN, offering h2
   * ALPN, offering http/1.1
   * successfully set certificate verify locations:
   *  CAfile: /etc/ssl/cert.pem
   *  CApath: none
   * TLSv1.2 (OUT), TLS handshake, Client hello (1):
   * TLSv1.2 (IN), TLS handshake, Server hello (2):
   * TLSv1.2 (IN), TLS handshake, Certificate (11):
   * TLSv1.2 (IN), TLS handshake, Server key exchange (12):
   * TLSv1.2 (IN), TLS handshake, Server finished (14):
   * TLSv1.2 (OUT), TLS handshake, Client key exchange (16):
   * TLSv1.2 (OUT), TLS change cipher, Change cipher spec (1):
   * TLSv1.2 (OUT), TLS handshake, Finished (20):
   * TLSv1.2 (IN), TLS change cipher, Change cipher spec (1):
   * TLSv1.2 (IN), TLS handshake, Finished (20):
   * SSL connection using TLSv1.2 / ECDHE-RSA-CHACHA20-POLY1305
   * ALPN, server accepted to use h2
   * Server certificate:
   *  subject: CN=*; O=any domain
   *  start date: Jul 23 20:03:48 2024 GMT
   *  expire date: Jul 23 20:03:48 2025 GMT
   *  issuer: O=any domain; CN=*
   *  SSL certificate verify result: unable to get local issuer certificate (20), continuing anyway.
   * Using HTTP2, server supports multi-use
   * Connection state changed (HTTP/2 confirmed)
   * Copying HTTP/2 data in stream buffer to connection buffer after upgrade: len=0
   * Using Stream ID: 1 (easy handle 0x14200fe00)
   ...
   < HTTP/2 200 
   HTTP/2 200 
   ```
   
{{% /tab %}}
{{< /tabs >}}

<!--TODO HTTPListenerPolicy healthcheck
4. Go back to the AWS EC2 dashboard and verify that the NLB health checks now show a `Healthy` status. 
   {{< reuse-image src="/img/elb-resource-map.png" >}}-->

## Cleanup

{{< reuse "docs/snippets/cleanup.md" >}}

1. Delete the Ingress and Gateway resources.
   ```sh
   kubectl delete gatewayparameters custom-gw-params -n {{< reuse "docs/snippets/ns-system.md" >}}
   kubectl delete gateway aws-cloud -n {{< reuse "docs/snippets/ns-system.md" >}}
   kubectl delete httproute httpbin-elb -n {{< reuse "docs/snippets/ns-system.md" >}}
   kubectl delete secret tls -n {{< reuse "docs/snippets/ns-system.md" >}}
   ```

2. Delete the AWS IAM resources that you created.
   ```sh
   aws iam delete-policy --policy-arn=arn:aws:iam::${AWS_ACCOUNT_ID}:policy/${IAM_POLICY_NAME}
   eksctl delete iamserviceaccount --name=${IAM_SA} --cluster=${CLUSTER_NAME}
   ```

3. Uninstall the Helm release for the `aws-load-balancer-controller`.
   ```sh
   helm uninstall aws-load-balancer-controller -n kube-system
   ```