---
title: AWS Lambda
weight: 30
---

Use {{< reuse "docs/snippets/product-name.md" >}} to route traffic requests directly to an [Amazon Web Services (AWS) Lambda](https://aws.amazon.com/lambda/resources/) function.

## About

Serverless functions, such as Lambda functions, provide an alternative to traditional applications or services. The functions run on servers that you do not have to manage yourself, and you pay for only for the compute time you use.

However, you might want to invoke your serverless functions from other services or apps, such as the Kubernetes workloads that run in your cluster. By abstracting a Lambda as a type of destination in your {{< reuse "docs/snippets/product-name.md" >}} environment, your workloads can send requests to the Lambda destination in the same way that you set up routing through {{< reuse "docs/snippets/product-name.md" >}} to other types of destinations. {{< reuse "docs/snippets/product-name.md" >}} does the work of assuming an AWS IAM role to invoke the actual Lambda function in your AWS account.

For more information, see the AWS Lambda documentation on [configuring Lambda functions as targets](https://docs.aws.amazon.com/elasticloadbalancing/latest/application/lambda-functions.html).

## Before you begin

{{< reuse "docs/snippets/prereq.md" >}}

## Create an AWS credentials secret

Create a Kubernetes secret that contains your AWS access key and secret key. {{< reuse "docs/snippets/product-name.md" >}} uses this secret to connect to AWS Lambda for authentication and function invocation.

1. Get the access key, secret key, and session token for your AWS account. If your AWS account setup does not require a session token, you can remove the session token parameter from the Kubernetes secret. Note that your [AWS credentials](https://docs.aws.amazon.com/general/latest/gr/aws-sec-cred-types.html) must have the appropriate permissions to interact with AWS Lambda.

2. Create a Kubernetes secret that contains the AWS access key and secret key.
   ```sh
   {{< reuse "docs/snippets/cli-name.md" >}} create secret aws \
       --name 'aws-creds' \
       --namespace {{< reuse "docs/snippets/ns-system.md" >}} \
       --access-key ${AWS_ACCESS_KEY_ID} \
       --secret-key ${AWS_SECRET_ACCESS_KEY} \
       --session-token ${AWS_SESSION_TOKEN}
   ```

## Create a Lambda function

Create an AWS Lambda function to test {{< reuse "docs/snippets/product-name.md" >}} routing.

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

## Create a Backend and HTTPRoute

Create {{< reuse "docs/snippets/product-name.md" >}} `Backend` and `HTTPRoute` resources to route requests to the Lambda function.

1. In your terminal, create a Backend resource that references the Lambda secret. Update the region with your AWS account region, such as `us-east-1`.
   
   ```yaml
   kubectl apply -f - <<EOF
   apiVersion: gateway.kgateway.dev/v1alpha1
   kind: Backend
   metadata:
     name: lambda
     namespace: {{< reuse "docs/snippets/ns-system.md" >}}
   spec:
     aws:
       region: <region>
       secretRef:
         name: aws-creds
         namespace: {{< reuse "docs/snippets/ns-system.md" >}}
       lambdaFunctions:
       - lambdaFunctionName: echo
         logicalName: echo
         qualifier: $LATEST
   EOF
   ```

2. Create an HTTPRoute resource that references the `lambda` Backend.
   
   ```yaml
   kubectl apply -f - <<EOF
   apiVersion: gateway.networking.k8s.io/v1
   kind: HTTPRoute
   metadata:
     name: lambda
     namespace: {{< reuse "docs/snippets/ns-system.md" >}}
   spec:
     parentRefs:
       - name: http
         namespace: {{< reuse "docs/snippets/ns-system.md" >}}
     rules:
     - matches:
       - path:
           type: PathPrefix
           value: /echo
       backendRefs:
       - name: lambda
         namespace: {{< reuse "docs/snippets/ns-system.md" >}}
         group: gateway.kgateway.dev
         kind: Backend
         filters:
           - type: ExtensionRef
             extensionRef:
               group: "gateway.kgateway.dev"
               kind: Parameter
               name: echo
   EOF
   ```

3. Confirm that {{< reuse "docs/snippets/product-name.md" >}} correctly routes requests to Lambda by sending a curl request to the `echo` function.
   
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

At this point, {{< reuse "docs/snippets/product-name.md" >}} is routing directly to the `echo` Lambda function!

## Cleanup

{{% reuse "docs/snippets/cleanup.md" %}}

1. Delete the `lambda` HTTPRoute and `lambda` Backend.
   
   ```sh
   kubectl delete HTTPRoute lambda -n {{< reuse "docs/snippets/ns-system.md" >}}
   kubectl delete Backend lambda -n {{< reuse "docs/snippets/ns-system.md" >}}
   ```

2. Delete the `aws-creds` secret.
   
   ```sh
   kubectl delete secret aws-creds -n {{< reuse "docs/snippets/ns-system.md" >}}
   ```

3. Use the AWS Lambda console to delete the `echo` test function.

## Known limitations

- Currently, the only parameter that is supported for the `backendRefs.filters.extensionRef` field in the HTTPRoute resource is the name of the Lambda function. Additional parameters, such as `wrapAsApiGateway`, `unwrapAsApiGateway`, or `invocationStyle`, are not supported.
- Authenticating with your AWS account by using IAM Roles for Service Accounts (IRSA) is currently unsupported.
