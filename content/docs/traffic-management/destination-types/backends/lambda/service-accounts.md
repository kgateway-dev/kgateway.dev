---
title: Access AWS Lambda with a service account
weight: 20
---

Associate an IAM role with a gateway proxy service account, and configure {{% reuse "docs/snippets/product-name.md" %}} to use that service account to access AWS Lambda.

## About

Amazon Web Services (AWS) offers the ability to associate an IAM role with a Kubernetes service account, also known as creating an IRSA. {{% reuse "docs/snippets/product-name.md" %}} supports discovering and invoking AWS Lambda functions by using an IRSA. For more information, see the [AWS documentation](https://docs.aws.amazon.com/eks/latest/userguide/iam-roles-for-service-accounts.html).

In this guide, you follow these steps:

**AWS resources**:
* Associate your EKS cluster with an IAM OIDC provider
* Create an IAM policy that allows interactions with Lambda functions
* Create an IAM role that associates the IAM policy with the gateway proxy service account (an IRSA)
* Deploy the Amazon EKS Pod Identity Webhook to your cluster
* Create a Lambda function for testing

**{{% reuse "docs/snippets/product-name.md" %}} resources**:
* Install {{% reuse "docs/snippets/product-name.md" %}}, including settings to annotate the gateway proxy service account with the IRSA
* Set up routing to your function by creating `Upstream` and `HTTPRoute` resources

{{% callout type="warning" %}}
This guide requires you to enable IAM settings in your EKS cluster, such as the AWS Pod Identity Webhook, **before** you deploy {{% reuse "docs/snippets/product-name.md" %}} components that are created during installation, such as the Gateway CRD and the gateway proxy service account. You might use this guide with a fresh EKS test cluster to try out Lambda function invocation with {{% reuse "docs/snippets/product-name.md" %}} service accounts.
{{% /callout %}}

## Configure AWS IAM resources {#iam}

Save your AWS details, and create an IRSA for the gateway proxy pod to use.

1. Save the region where your Lambda functions exist, the region where your EKS cluster exists, your cluster name, and the ID of the AWS account.
   ```sh
   export AWS_LAMBDA_REGION=<lambda_function_region>
   export AWS_CLUSTER_REGION=<cluster_region>
   export CLUSTER_NAME=<cluster_name>
   export ACCOUNT_ID=<account_id>
   ```

2. Check whether your EKS cluster has an OIDC provider.
   ```sh
   export OIDC_PROVIDER=$(aws eks describe-cluster --name ${CLUSTER_NAME} --region ${AWS_CLUSTER_REGION} --query "cluster.identity.oidc.issuer" --output text | sed -e "s/^https:\/\///")
   echo $OIDC_PROVIDER
   ```
   * If an OIDC provider in the format `oidc.eks.<region>.amazonaws.com/id/<cluster_id>` is returned, continue to the next step. 
   * If an OIDC provider is not returned, follow the AWS documentation to [Create an IAM OIDC provider for your cluster](https://docs.aws.amazon.com/eks/latest/userguide/enable-iam-roles-for-service-accounts.html), and then run this command again to save the OIDC provider in an environment variable.

3. Create an IAM policy to allow access to the following four Lambda actions. Note that the permissions to discover and invoke functions are listed in the same policy. In a more advanced setup, you might separate discovery and invocation permissions into two IAM policies.
   ```sh
   cat >policy.json <<EOF
   {
      "Version": "2012-10-17",
      "Statement": [
          {
              "Effect": "Allow",
              "Action": [
                  "lambda:ListFunctions",
                  "lambda:InvokeFunction",
                  "lambda:GetFunction",
                  "lambda:InvokeAsync"
              ],
              "Resource": "*"
          }
      ]
   }
   EOF

   aws iam create-policy --policy-name {{% reuse "docs/snippets/product-name.md" %}}-lambda-policy --policy-document file://policy.json 
   ```

4. Use an IAM role to associate the policy with the Kubernetes service account for the HTTP gateway proxy, which assumes this role to invoke Lambda functions. For more information about these steps, see the [AWS documentation](https://docs.aws.amazon.com/eks/latest/userguide/associate-service-account-role.html).
   1. Create the following IAM role. Note that the service account name `http` in the `{{% reuse "docs/snippets/ns-system.md" %}}` namespace is specified, because in later steps you create an HTTP gateway named `http`.
      ```sh
      cat >role.json <<EOF
      {
        "Version": "2012-10-17",
        "Statement": [
          {
            "Effect": "Allow",
            "Principal": {
              "Federated": "arn:aws:iam::${ACCOUNT_ID}:oidc-provider/${OIDC_PROVIDER}"
            },
            "Action": "sts:AssumeRoleWithWebIdentity",
            "Condition": {
              "StringEquals": {
                "${OIDC_PROVIDER}:sub": [
                  "system:serviceaccount:{{% reuse "docs/snippets/ns-system.md" %}}:http"
                ]
              }
            }
          }
        ]
      }
      EOF

      aws iam create-role --role-name {{% reuse "docs/snippets/product-name.md" %}}-lambda-role --assume-role-policy-document file://role.json
      ```
   2. Attach the IAM role to the IAM policy. This IAM role for the service account is known as an IRSA.
      ```sh
      aws iam attach-role-policy --role-name {{% reuse "docs/snippets/product-name.md" %}}-lambda-role --policy-arn=arn:aws:iam::${ACCOUNT_ID}:policy/{{% reuse "docs/snippets/product-name.md" %}}-lambda-policy
      ```
   3. Verify that the policy is attached to the role.
      ```sh
      aws iam list-attached-role-policies --role-name {{% reuse "docs/snippets/product-name.md" %}}-lambda-role
      ```
      Example output:
      ```json
      {
          "AttachedPolicies": [
              {
                  "PolicyName": "{{% reuse "docs/snippets/product-name.md" %}}-lambda-policy",
                  "PolicyArn": "arn:aws:iam::111122223333:policy/{{% reuse "docs/snippets/product-name.md" %}}-lambda-policy"
              }
          ]
      }
      ```

## Deploy the Amazon EKS Pod Identity Webhook {#webhook}

**Before you install {{% reuse "docs/snippets/product-name.md" %}}**, deploy the [Amazon EKS Pod Identity Webhook](https://github.com/aws/amazon-eks-pod-identity-webhook/), which allows pods' service accounts to use AWS IAM roles. When you create the {{% reuse "docs/snippets/product-name.md" %}} proxy in the next section, this webhook mutates the proxy's service account so that it can assume your IAM role to invoke Lambda functions.

1. In your EKS cluster, install [cert-manager](https://cert-manager.io/docs/), which is a prerequisite for the webhook.
   ```sh
   wget https://github.com/cert-manager/cert-manager/releases/download/v1.12.4/cert-manager.yaml
   kubectl apply -f cert-manager.yaml
   ```

2. Verify that all cert-manager pods are running.
   ```sh
   kubectl get pods -n cert-manager
   ```

3. Deploy the Amazon EKS Pod Identity Webhook.
   ```sh
   kubectl apply -f https://raw.githubusercontent.com/solo-io/workshops/refs/heads/master/gloo-gateway/1-18/enterprise/lambda/data/steps/deploy-amazon-pod-identity-webhook/auth.yaml
   kubectl apply -f https://raw.githubusercontent.com/solo-io/workshops/refs/heads/master/gloo-gateway/1-18/enterprise/lambda/data/steps/deploy-amazon-pod-identity-webhook/deployment-base.yaml
   kubectl apply -f https://raw.githubusercontent.com/solo-io/workshops/refs/heads/master/gloo-gateway/1-18/enterprise/lambda/data/steps/deploy-amazon-pod-identity-webhook/mutatingwebhook.yaml
   kubectl apply -f https://raw.githubusercontent.com/solo-io/workshops/refs/heads/master/gloo-gateway/1-18/enterprise/lambda/data/steps/deploy-amazon-pod-identity-webhook/service.yaml
   ```

4. Verify that the webhook deployment completes.
   ```sh
   kubectl rollout status deploy/pod-identity-webhook
   ```

## Install {{% reuse "docs/snippets/product-name.md" %}} with service account authentication {#kgateway}

Install {{% reuse "docs/snippets/product-name.md" %}}, including settings to support gateway proxy service account authentication with your AWS account.

1. Deploy the Kubernetes Gateway API CRDs.

   ```sh
   kubectl apply -f https://github.com/kubernetes-sigs/gateway-api/releases/download/v{{< reuse "docs/versions/k8s-gw-version.md" >}}/standard-install.yaml
   ```

2. Deploy the {{% reuse "docs/snippets/product-name.md" %}} CRDs by using Helm.

   ```sh
   helm upgrade -i --create-namespace --namespace {{% reuse "docs/snippets/ns-system.md" %}} --version v{{< reuse "docs/versions/n-patch.md" >}} kgateway-crds oci://cr.kgateway.dev/kgateway-dev/charts/kgateway-crds
   ```
   
3. Install {{% reuse "docs/snippets/product-name.md" %}} by using Helm. The following settings enable {{% reuse "docs/snippets/product-name.md" %}} to use an AWS IRSA and annotate the `http` service account.
   ```yaml
   helm install -n {{% reuse "docs/snippets/ns-system.md" %}} \
   --create-namespace \
   --version v{{< reuse "docs/versions/n-patch.md" >}} \
   kgateway oci://cr.kgateway.dev/kgateway-dev/charts/kgateway \
   -f -<<EOF
   # Annotate the gateway proxy service account
   kubeGateway:
     gatewayParameters:
       glooGateway:
         serviceAccount:
           extraAnnotations:
             eks.amazonaws.com/role-arn: arn:aws:iam::${ACCOUNT_ID}:role/{{% reuse "docs/snippets/product-name.md" %}}-lambda-role
   # Enable AWS account authentication with IRSA
   settings:
     aws:
       enableServiceAccountCredentials: true
       stsCredentialsRegion: ${AWS_LAMBDA_REGION}
   EOF
   ```

4. Make sure that `kgateway` is running.

   ```sh
   kubectl get pods -n {{% reuse "docs/snippets/ns-system.md" %}}
   ```

   Example output:

   ```
   NAME                        READY   STATUS    RESTARTS   AGE
   kgateway-5495d98459-46dpk   1/1     Running   0          19s
   ```

## Create a gateway proxy and annotate its service account {#annotate}

Create an HTTP gateway, and verify that its service account is annotated.

1. Create a Gateway resource with an HTTP listener. 
   ```yaml
   kubectl apply -f- <<EOF
   kind: Gateway
   apiVersion: gateway.networking.k8s.io/v1
   metadata:
     name: http
     namespace: {{% reuse "docs/snippets/ns-system.md" %}}
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

2. Check the status of the gateway to make sure that your configuration is accepted and no conflicts exist in your cluster. 
   ```sh
   kubectl get gateway http -n {{% reuse "docs/snippets/ns-system.md" %}} -o yaml
   ```

3. Get the external address of the gateway and save it in an environment variable.
   {{< tabs items="Cloud Provider LoadBalancer,Port-forward for local testing" >}}
   {{% tab %}}
   ```sh
   export INGRESS_GW_ADDRESS=$(kubectl get svc -n {{% reuse "docs/snippets/ns-system.md" %}} http -o jsonpath="{.status.loadBalancer.ingress[0]['hostname','ip']}")
   echo $INGRESS_GW_ADDRESS   
   ```
   {{% /tab %}}
   {{% tab %}}
   ```sh
   kubectl port-forward deployment/http -n {{% reuse "docs/snippets/ns-system.md" %}} 8080:8080
   ```
   {{% /tab %}}
   {{< /tabs >}}

4. Verify that the `http` service account has the `eks.amazonaws.com/role-arn: arn:aws:iam::${ACCOUNT_ID}:role/{{% reuse "docs/snippets/product-name.md" %}}-lambda-role` annotation.
   ```sh
   kubectl describe serviceaccount http -n {{% reuse "docs/snippets/ns-system.md" %}}
   ```

## Create a Lambda function

Create an AWS Lambda function to test {{% reuse "docs/snippets/product-name.md" %}} routing.

1. Log in to the AWS console and navigate to the Lambda page.

2. Click the **Create Function** button.

3. Name the function `echo` and click **Create function**.

4. Replace the default contents of `index.mjs` with the following Node.js function, which returns a response body that contains exactly what was sent to the function in the request body.
   
   ```js
   export const handler = async(event) => {
       const response = {
           statusCode: 200,
           body: `Response from AWS Lambda. Here's the request you just sent me: ${JSON.stringify(event)}`
       };
       return response;
   };
   ```

5. Click **Deploy**.

## Set up routing to your function {#routing}

Create {{% reuse "docs/snippets/product-name.md" %}} `Backend` and `HTTPRoute` resources to route requests to the Lambda function.

1. Create a Backend resource that references the AWS region, IAM role, and `echo` function that you created.
   ```yaml
   kubectl apply -f - <<EOF
   apiVersion: gateway.kgateway.dev/v1alpha1
   kind: Backend
   metadata:
     name: lambda
     namespace: {{% reuse "docs/snippets/ns-system.md" %}}
   spec:
     type: AWS
     aws:
       region: ${AWS_LAMBDA_REGION}
       accountId: ${ACCOUNT_ID}
       auth:
         type: IRSA
       lambda:
         functionName: echo
   EOF
   ```

2. Create an HTTPRoute resource that references the `lambda` Backend.
   
   ```yaml
   kubectl apply -f - <<EOF
   apiVersion: gateway.networking.k8s.io/v1
   kind: HTTPRoute
   metadata:
     name: lambda
     namespace: {{% reuse "docs/snippets/ns-system.md" %}}
   spec:
     parentRefs:
       - name: http
         namespace: {{% reuse "docs/snippets/ns-system.md" %}}
     rules:
     - matches:
       - path:
           type: PathPrefix
           value: /echo
       backendRefs:
       - name: lambda
         namespace: {{% reuse "docs/snippets/ns-system.md" %}}
         group: gateway.kgateway.dev
         kind: Backend
         filters:
           - type: ExtensionRef
             extensionRef:
               group: gateway.kgateway.dev
               kind: Parameter
               name: echo
   EOF
   ```

3. Confirm that {{% reuse "docs/snippets/product-name.md" %}} correctly routes requests to Lambda by sending a curl request to the `echo` function. Note that the first request might take a few seconds to process, because the AWS Security Token Service (STS) credential request must be performed first. However, after the credentials are cached, subsequent requests are processed more quickly.

   {{< tabs items="Cloud Provider LoadBalancer,Port-forward for local testing" >}}
   {{% tab %}}
   ```sh
   curl $INGRESS_GW_ADDRESS:8080/echo -d '{"key1":"value1", "key2":"value2"}' -X POST
   ```
   {{% /tab %}}
   {{% tab %}}
   ```sh
   curl localhost:8080/echo -d '{"key1":"value1", "key2":"value2"}' -X POST
   ```
   {{% /tab %}}
   {{< /tabs >}}

   Example response:
   ```json
   {"statusCode":200,"body":"Response from AWS Lambda. Here's the request you just sent me: {\"key1\":\"value1\",\"key2\":\"value2\"}"}% 
   ```

At this point, {{% reuse "docs/snippets/product-name.md" %}} is routing directly to the `echo` Lambda function using an IRSA!

## Cleanup

{{% reuse "docs/snippets/cleanup.md" %}}

### Resources for the `echo` function

1. Delete the `lambda` HTTPRoute and `lambda` Backend.
   ```sh
   kubectl delete HTTPRoute lambda -n {{% reuse "docs/snippets/ns-system.md" %}}
   kubectl delete Backend lambda -n {{% reuse "docs/snippets/ns-system.md" %}}
   ```

2. Use the AWS Lambda console to delete the `echo` test function.

### IRSA authorization (optional)

If you no longer need to access Lambda functions from {{% reuse "docs/snippets/product-name.md" %}}:

1. Upgrade your {{% reuse "docs/snippets/product-name.md" %}} Helm installation to remove the added settings and annotation.
   1. Get the Helm values for your current installation, and save them in a file.
      ```sh
      helm get values kgateway -n {{% reuse "docs/snippets/ns-system.md" %}} -o yaml > kgateway.yaml
      open kgateway.yaml
      ```
   2. Delete the following settings, and save the file.
      * `kubeGateway.gatewayParameters.glooGateway.serviceAccount.extraAnnotations`
      * `settings.aws.enableServiceAccountCredentials`
      * `settings.aws.stsCredentialsRegion`
   3. Upgrade the Helm release. Replace the example {{% reuse "docs/snippets/product-name.md" %}} version with the version that you run.
     ```sh
     helm upgrade -i -n {{% reuse "docs/snippets/ns-system.md" %}} kgateway oci://cr.kgateway.dev/kgateway-dev/charts/kgateway \
     -f kgateway.yaml \
     --version v{{< reuse "docs/versions/n-patch.md" >}}
     ```

2. Delete the pod identity webhook.
   ```sh
   kubectl delete deploy pod-identity-webhook
   ```

3. Remove cert-manager.
   ```sh
   kubectl delete -f cert-manager.yaml -n cert-manager
   kubectl delete ns cert-manager
   ```

4. Delete the AWS IAM resources that you created.
   ```sh
   aws iam detach-role-policy --role-name {{% reuse "docs/snippets/product-name.md" %}}-lambda-role --policy-arn=arn:aws:iam::${ACCOUNT_ID}:policy/{{% reuse "docs/snippets/product-name.md" %}}-lambda-policy
   aws iam delete-role --role-name {{% reuse "docs/snippets/product-name.md" %}}-lambda-role
   aws iam delete-policy --policy-arn=arn:aws:iam::${ACCOUNT_ID}:policy/{{% reuse "docs/snippets/product-name.md" %}}-lambda-policy
   ```