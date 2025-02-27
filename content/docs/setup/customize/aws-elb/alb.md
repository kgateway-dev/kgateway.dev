---
title: AWS ALB
weight: 10
---

In this guide you explore how to expose the {{< reuse "docs/snippets/product-name.md" >}} proxy with an AWS application load balancer (ALB). 

{{< callout type="warning" >}}
Keep in mind the following considerations when working with an ALB: 
* The AWS Load Balancer Controller only supports creation of an ALB through an Ingress Controller and not through the {{< reuse "docs/snippets/k8s-gateway-api-name.md" >}}. Because of this, you must create the ALB separately and later connect it to the service that exposes your gateway proxy.
* {{< reuse "docs/snippets/product-name-caps.md" >}} does not open any proxy ports until at least one HTTPRoute resource is created that references the gateway. However, AWS ELB health checks are automatically created and run after you create the gateway. Because of this, registered targets might appear unhealthy until an HTTPRoute resource is created. 
{{< /callout >}}

## Before you begin

1. Create or use an existing AWS account. 
2. Follow the [Get started guide](/docs/quickstart/) to install {{< reuse "docs/snippets/product-name.md" >}} and deploy the httpbin sample app. You do not need to set up a Gateway as you create a custom Gateway as part of this guide. 

## Step 1: Deploy the AWS Load Balancer controller

{{< reuse "docs/snippets/aws-elb-controller-install.md" >}}
   
## Step 2: Deploy your gateway proxy

1. Create a Gateway resource with an HTTP listener. 
   ```yaml
   kubectl apply -n {{< reuse "docs/snippets/ns-system.md" >}} -f- <<EOF
   kind: Gateway
   apiVersion: gateway.networking.k8s.io/v1
   metadata:
     name: alb
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
   
2. Create an HttpListenerPolicy resource to change the default health check path for the gateway proxy. This step is required to ensure that the ALB health checks pass successfully. 
   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.kgateway.dev/v1alpha1
   kind: HttpListenerPolicy
   metadata:
     name: alb-healthcheck
     namespace: {{< reuse "docs/snippets/ns-system.md" >}}
   spec:
     targetRefs:
     - group: gateway.networking.k8s.io
       kind: Gateway
       name: alb
     options:
       healthCheck:
         path: "/healthz"
   EOF
   ```
   
3. Use an Ingress resource to create your ALB. Make sure to include the health check path that you set up earlier. 
   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: networking.k8s.io/v1
   kind: Ingress
   metadata:
     namespace: {{< reuse "docs/snippets/ns-system.md" >}}
     name: alb
     annotations:
       alb.ingress.kubernetes.io/scheme: internet-facing
       alb.ingress.kubernetes.io/target-type: instance
       alb.ingress.kubernetes.io/healthcheck-protocol: HTTP #--HTTPS by default
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

4. Review the load balancer in the AWS EC2 dashboard. 
   1. Go to the [AWS EC2 dashboard](https://console.aws.amazon.com/ec2). 
   2. Go to **Load Balancing > Load Balancers**. Find and open the ALB that was created for you. 
   3. On the **Resource map** tab, verify that the load balancer points to targets in your cluster. 

   {{< callout type="info" >}}
   {{< reuse "docs/snippets/product-name-caps.md" >}} does not open any proxy ports until at least one HTTPRoute is associated with the gateway. The AWS ELB health checks are automatically created when you create the Gateway resource and might report that the gateway proxy is unhealthy. Continue with this guide to create an HTTPRoute resource to open up a port in the ALB.
   {{< /callout >}}
 
5. Create an HTTPRoute resource to open up a port on the gateway proxy. This step is required for AWS ELB health checks to pass. 
   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.networking.k8s.io/v1
   kind: HTTPRoute
   metadata:
     name: httpbin-alb
     namespace: httpbin
     labels:
       example: httpbin-route
   spec:
     parentRefs:
       - name: alb
         namespace: {{< reuse "docs/snippets/ns-system.md" >}}
     hostnames:
       - "albtest.com"
     rules:
       - backendRefs:
           - name: httpbin
             port: 8000
   EOF
   ```

6. Go back to the AWS EC2 console to verify that the AWS ELB checks now pass. 
   {{< reuse-image src="img/alb.png" >}}

## Test the ALB

1. From the AWS EC2 console, get the DNS name that was assigned to your ALB and save it as an environment variable. 
   ```sh
   export INGRESS_GW_ADDRESS=<alb-dns-name>
   ```

2. Send a request to the httpbin app. Verify that you get back a 200 HTTP response code. 
   ```sh
   curl -vik http://$INGRESS_GW_ADDRESS:80/headers -H "host: albtest.com:80"
   ```
   
   Example output: 
   ```
   ...
   < HTTP/1.1 200 OK
   HTTP/1.1 200 OK
   ```


## Cleanup

{{< reuse "docs/snippets/cleanup.md" >}}

```sh
kubectl delete ingress alb -n {{< reuse "docs/snippets/ns-system.md" >}}
kubectl delete httproute httpbin-alb -n httpbin
kubectl delete gateway alb -n {{< reuse "docs/snippets/ns-system.md" >}} 
kubectl delete httplisteneroption alb-healthcheck -n {{< reuse "docs/snippets/ns-system.md" >}} 
```
