---
title: AWS ALB
weight: 20
---

In this guide you explore how to expose the {{< reuse "docs/snippets/kgateway.md" >}} proxy with an AWS application load balancer (ALB). 

{{< callout type="warning" >}}
The AWS Load Balancer Controller only supports the creation of an ALB through an Ingress Controller and not through the {{< reuse "docs/snippets/k8s-gateway-api-name.md" >}}. Because of this, you must create the ALB separately through an Ingress resource that connects it to the service that exposes your gateway proxy.
{{< /callout >}}

## Before you begin

1. Create or use an existing AWS account. 
2. Follow the [Get started guide]({{< link-hextra path="/quickstart/" >}}) to install {{< reuse "docs/snippets/kgateway.md" >}}.
3. Deploy the httpbin sample app. For more information, see the [sample app guide]({{< link-hextra path="/install/sample-app#deploy-app/" >}}).
   1. Create the httpbin app.
      ```shell
      kubectl apply -f https://raw.githubusercontent.com/kgateway-dev/kgateway/refs/heads/{{< reuse "docs/versions/github-branch.md" >}}/examples/httpbin.yaml
      ```

      Example output:
      ```txt
      namespace/httpbin created
      serviceaccount/httpbin created
      service/httpbin created
      deployment.apps/httpbin created
      ```
   2. Verify that the httpbin app is running.
      ```sh
      kubectl -n httpbin get pods
      ```

      Example output: 
      ```txt
      NAME                      READY   STATUS    RESTARTS   AGE
      httpbin-d57c95548-nz98t   2/2     Running   0          18s
      ```
   
## Step 1: Deploy gateway proxy resources
 
1. Create a Gateway resource with an HTTP listener. You later pair this Gateway with an AWS ALB. 
   ```yaml
   kubectl apply -n {{< reuse "docs/snippets/namespace.md" >}} -f- <<EOF
   kind: Gateway
   apiVersion: gateway.networking.k8s.io/v1
   metadata:
     name: alb
   spec:
     gatewayClassName: {{< reuse "docs/snippets/gatewayclass.md" >}}
     listeners:
     - protocol: HTTP
       port: 8080
       name: http
       allowedRoutes:
         namespaces:
           from: All
   EOF
   ```

2. Create DirectResponse and HTTPRoute resources to configure a custom healthcheck path on the gateway. In this example, you expose the `/healthz` path and configure it to always return a 200 HTTP response code by using the DirectResponse. Later, you configure the ALB to perform the health check against the `/healthz` path to determine if the Gateway is healthy. 
   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.kgateway.dev/v1alpha1
   kind: DirectResponse
   metadata:
     name: httpbin-healthcheck-dr
     namespace: httpbin
   spec:
     status: 200
   ---
   apiVersion: gateway.networking.k8s.io/v1
   kind: HTTPRoute
   metadata:
     name: httpbin-healthcheck
     namespace: httpbin
   spec:
     parentRefs:
       - name: alb
         namespace: {{< reuse "docs/snippets/namespace.md" >}}
     rules:
     - matches:
       - path:
           type: Exact
           value: /healthz
       filters:
       - type: ExtensionRef
         extensionRef:
          name: httpbin-healthcheck-dr
          group: gateway.kgateway.dev
          kind: DirectResponse
   EOF
   ```

3. Create another HTTPRoute resource to expose the httpbin app on the `albtest.com` domain. 
   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.networking.k8s.io/v1
   kind: HTTPRoute
   metadata:
     name: httpbin-alb
     namespace: httpbin
   spec:
     parentRefs:
       - name: alb
         namespace: {{< reuse "docs/snippets/namespace.md" >}}
     hostnames:
       - "albtest.com"
     rules:
     - matches:
       - path:
           type: PathPrefix
           value: /
       backendRefs:
       - name: httpbin
         port: 8000
   EOF
   ```

## Step 2: Create an ALB with the AWS Load Balancer controller

{{< reuse "docs/snippets/aws-elb-controller-install.md" >}}

5. Use an Ingress resource to define your ALB. When you apply this resource, the AWS Load Balancer Controller creates the ALB in your account.
   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: networking.k8s.io/v1
   kind: Ingress
   metadata:
     namespace: {{< reuse "docs/snippets/namespace.md" >}}
     name: alb
     annotations:
       alb.ingress.kubernetes.io/scheme: internet-facing
       alb.ingress.kubernetes.io/target-type: instance
       alb.ingress.kubernetes.io/healthcheck-protocol: HTTP
       alb.ingress.kubernetes.io/healthcheck-path: "/healthz"
   spec:
     ingressClassName: alb
     rules:
       - http:
           paths:
           - path: /
             pathType: Prefix
             backend:
               service:
                 name: alb
                 port:
                   number: 8080
   EOF
   ```
   
   {{< callout type="info" >}}
   If you later change your Ingress resource configuration, you might need to delete and re-create your Ingress resource for AWS to pick up the changes.
   {{< /callout >}}

6. Review the load balancer in the AWS EC2 dashboard. 
   1. Go to the [AWS EC2 dashboard](https://console.aws.amazon.com/ec2). 
   2. In the left navigation, go to **Load Balancing > Load Balancers**.
   3. Find and open the ALB that was created for you, with a name such as `k8s-{{< reuse "docs/snippets/alb-elb-name.md" >}}-alb-<hash>`. Note that it might take a few minutes for the ALB to provision.
   4. On the **Resource map** tab, verify that the load balancer points to healthy EC2 targets in your cluster. For example, you can click on the target EC2 name to verify that the instance summary lists your cluster name.
      {{< reuse-image src="img/alb.png" >}}
      {{< reuse-image-dark srcDark="img/alb.png" >}}

## Step 3: Test the ALB

1. In the **Details** pane of the ALB, get the **DNS name** that was assigned to your ALB and save it as an environment variable. 
   ```sh
   export INGRESS_GW_ADDRESS=<alb-dns-name>
   ```

2. Send a request to the httpbin app. Verify that you get back a 200 HTTP response code. 
   ```sh
   curl -vi http://$INGRESS_GW_ADDRESS:80/headers -H "host: albtest.com:80"
   ```
   
   Example output: 
   ```console
   ...
   < HTTP/1.1 200 OK
   HTTP/1.1 200 OK
   ```

## Cleanup

{{< reuse "docs/snippets/cleanup.md" >}}

1. Delete the Ingress, HTTPRoute, DirectResponse, and Gateway resources.
   ```sh
   kubectl delete ingress alb -n {{< reuse "docs/snippets/namespace.md" >}}
   kubectl delete httproute httpbin-alb -n httpbin
   kubectl delete httproute httpbin-healthcheck -n httpbin
   kubectl delete directresponse httpbin-healthcheck-dr -n httpbin
   kubectl delete gateway alb -n {{< reuse "docs/snippets/namespace.md" >}}
   ```

2. Delete the AWS IAM resources that you created.
   ```sh
   eksctl delete iamserviceaccount --name=${IAM_SA} --cluster=${CLUSTER_NAME}
   aws iam delete-policy --policy-arn=arn:aws:iam::${AWS_ACCOUNT_ID}:policy/${IAM_POLICY_NAME}
   ```

3. Uninstall the Helm release for the `aws-load-balancer-controller`.
   ```sh
   helm uninstall aws-load-balancer-controller -n kube-system
   ```