---
title: AWS ALB
weight: 10
---

{{< reuse "kgw-docs/pages/integrations/aws-elb/alb.md" >}} 

## Before you begin

1. Create or use an existing AWS account. 
2. Follow the [Get started guide]({{< link-hextra path="/quickstart/" >}}) to install kgateway. You do not need to set up a Gateway as you create a custom Gateway as part of this guide.
3. Follow the [Sample app guide]({{< link-hextra path="/install/sample-app/#deploy-app" >}}) to deploy the httpbin sample app.
   
## Step 1: Deploy gateway proxy resources
 
1. Create a Gateway resource with an HTTP listener. You later pair this Gateway with an AWS ALB. 
   ```yaml
   kubectl apply -n kgateway-system -f- <<EOF
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
         namespace: kgateway-system
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
         namespace: kgateway-system
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

> [!NOTE]
> Creating an ALB with {{< reuse "kgw-docs/snippets/k8s-gateway-api-name.md" >}} resources requires AWS Load Balancer Controller version 2.14.0 or later. Earlier versions can create an ALB only through an Ingress resource.

{{< reuse "kgw-docs/snippets/aws-elb-controller-install.md" >}}

5. Use another Gateway resource to define your ALB. When you apply these resources, the AWS Load Balancer Controller creates the ALB in your account.
   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.networking.k8s.io/v1
   kind: GatewayClass
   metadata:
     name: aws-alb-gateway-class
   spec:
     controllerName: gateway.k8s.aws/alb
   ---
   apiVersion: gateway.k8s.aws/v1beta1
   kind: LoadBalancerConfiguration
   metadata:
     namespace: kgateway-system
     name: aws-alb-config
   spec:
     loadBalancerName: kgateway-alb
     scheme: internet-facing
   ---
   apiVersion: gateway.k8s.aws/v1beta1
   kind: TargetGroupConfiguration
   metadata:
     namespace: kgateway-system
     name: aws-alb-target-group-config
   spec:
     targetReference:
       kind: Service
       name: alb
     defaultConfiguration:
       targetType: instance
       healthCheckConfig:
         healthCheckProtocol: HTTP
         healthCheckPath: /healthz
   ---
   apiVersion: gateway.networking.k8s.io/v1
   kind: Gateway
   metadata:
     namespace: kgateway-system
     name: aws-alb
   spec:
     gatewayClassName: aws-alb-gateway-class
     infrastructure:
       parametersRef:
         group: gateway.k8s.aws
         kind: LoadBalancerConfiguration
         name: aws-alb-config
     listeners:
     - name: http
       protocol: HTTP
       port: 80
       allowedRoutes:
         namespaces:
           from: Same
   ---
   apiVersion: gateway.networking.k8s.io/v1
   kind: HTTPRoute
   metadata:
     namespace: kgateway-system
     name: aws-alb-to-proxy
   spec:
     parentRefs:
     - group: gateway.networking.k8s.io
       kind: Gateway
       name: aws-alb
       sectionName: http
     rules:
     - backendRefs:
       - name: alb
         port: 8080
   EOF
   ```
   
   | Setting | Description |
   | -- | -- |
   | `GatewayClass` with `controllerName: gateway.k8s.aws/alb` | Instruct the AWS Load Balancer Controller to provision an ALB for each Gateway in this GatewayClass. For more information, see the [AWS documentation](https://kubernetes-sigs.github.io/aws-load-balancer-controller/latest/guide/gateway/l7gateway/). |
   | `LoadBalancerConfiguration` with `loadBalancerName: kgateway-alb` | Give the ALB a predictable name in your AWS account. If you omit this field, the controller generates a name for you. |
   | `LoadBalancerConfiguration` with `scheme: internet-facing` | Create the ALB with public IP addresses that are accessible from the internet. Because the ALB uses the `internal` scheme by default, you must set this field and attach the LoadBalancerConfiguration to the Gateway with the `spec.infrastructure.parametersRef` field. For more information, see the [AWS documentation](https://kubernetes-sigs.github.io/aws-load-balancer-controller/latest/guide/gateway/loadbalancerconfig/). |
   | `TargetGroupConfiguration` with `targetType: instance` | Use the instance IDs of your cluster nodes to register the gateway proxy's node ports as targets with the ALB. For more information, see the [AWS documentation](https://kubernetes-sigs.github.io/aws-load-balancer-controller/latest/guide/gateway/targetgroupconfig/). |
   | `TargetGroupConfiguration` with `healthCheckPath: /healthz` | Perform the ALB health check against the `/healthz` path that you exposed on the gateway proxy earlier. Without this setting, the ALB checks the `/` path, which the gateway proxy does not serve, and the targets remain unhealthy. |

   > [!NOTE]
   > The `aws-alb` Gateway serves HTTP traffic on port 80 only. To serve HTTPS traffic, add an HTTPS listener to the Gateway and a matching `listenerConfigurations` entry with a `defaultCertificate` certificate ARN to the LoadBalancerConfiguration. The ALB does not support certificates in the Gateway's `spec.listeners.tls.certificateRefs` field.

6. Review the load balancer in the AWS EC2 dashboard. 
   1. Go to the [AWS EC2 dashboard](https://console.aws.amazon.com/ec2). 
   2. In the left navigation, go to **Load Balancing > Load Balancers**.
   3. Find and open the `kgateway-alb` ALB that was created for you. Note that it might take a few minutes for the ALB to provision.
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

{{< reuse "kgw-docs/snippets/cleanup.md" >}}

1. Delete the HTTPRoute, DirectResponse, Gateway, GatewayClass, and AWS Load Balancer Controller resources.
   ```sh
   kubectl delete httproute httpbin-alb -n httpbin
   kubectl delete httproute httpbin-healthcheck -n httpbin
   kubectl delete directresponse httpbin-healthcheck-dr -n httpbin
   kubectl delete httproute aws-alb-to-proxy -n kgateway-system
   kubectl delete gateway alb aws-alb -n kgateway-system
   kubectl delete gatewayclass aws-alb-gateway-class
   kubectl delete loadbalancerconfiguration aws-alb-config -n kgateway-system
   kubectl delete targetgroupconfiguration aws-alb-target-group-config -n kgateway-system
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
