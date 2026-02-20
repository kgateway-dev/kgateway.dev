Use {{< reuse "/docs/snippets/kgateway.md" >}} to route traffic requests directly to an [Amazon Web Services (AWS) Lambda](https://aws.amazon.com/lambda/resources/) function.

Note that this guide uses a Kubernetes secret that contains **long-lived IAM user access keys** (prefixed `AKIA`), not temporary STS/SSO credentials, which can cause failures with signature errors. To use AWS IAM roles to control access instead, see [Access AWS Lambda with a service account]({{< link-hextra path="/traffic-management/destination-types/backends/lambda/service-accounts/" >}}).

## Before you begin

{{< reuse "docs/snippets/prereq.md" >}}

## Create an AWS credentials secret

Create a Kubernetes secret that contains your AWS access key and secret key. You must use a long-lived IAM user access keys (prefixed `AKIA`), not temporary STS/SSO credentials. {{< reuse "/docs/snippets/kgateway-capital.md" >}} uses this secret to connect to AWS Lambda for authentication and function invocation.

1. Save the AWS account and region that your Lambda instance exists in as environment variables.
   ```sh
   export REGION=<us-east-1>
   export ACCOUNT_ID=<account_id>
   ````

2. Save your IAM user access key (prefixed `AKIA...`) and secret key as environment variables. Make sure that the `AWS_SESSION_TOKEN` is **not** set.
   ```bash
   export AWS_ACCESS_KEY_ID="<AKIA-access-key>"
   export AWS_SECRET_ACCESS_KEY="<secret-key>"
   ```
   If you do not have a long-lived IAM user access key pair, you can create one for your IAM user.
   * AWS console:
     1. Navigate to **IAM → Users → (your user)**.
     2. In the **Security credentials** tab, scroll to the **Access keys** panel, and click **Create access key**.
     3. Select the CLI option, and create the access key.
     4. Copy the output access key ID (prefixed `AKIA...`) and secret access key.
   * `aws` CLI:
     ```bash
     aws iam create-access-key --user-name <iam-user-name>
     ```

3. Verify that these credentials have the appropriate permissions to interact with AWS Lambda.
   ```bash
   aws sts get-caller-identity --region ${REGION}
   aws lambda invoke --function-name echo2 --region ${REGION} /tmp/out.json
   ```
   If either command fails, grant the IAM user Lambda invocation permissions in one of the following ways, and re-run the test commands.
   * AWS console:
     1. Navigate to **IAM → Users → (your user)**.
     2. In the **Permissions** tab, click **Add permissions → Create inline policy**.
     3. Toggle to the **JSON** editor.
     4. Paste the following policy to allow Lambda function invocation.
        ```json
        {
        	"Version": "2012-10-17",
        	"Statement": [
        		{
        			"Effect": "Allow",
        			"Action": "lambda:InvokeFunction",
        			"Resource": "arn:aws:lambda:us-east-1:802411188784:function:echo2"
        		}
        	]
        }
        ```
   * `aws` CLI:
     ```bash
     aws iam put-user-policy \
       --user-name <iam-user-name> \
       --policy-name AllowInvokeEcho2 \
       --policy-document "{
         \"Version\": \"2012-10-17\",
         \"Statement\": [
           {\"Effect\": \"Allow\", \"Action\": \"lambda:InvokeFunction\", \"Resource\": \"arn:aws:lambda:${REGION}:${ACCOUNT_ID}:function:echo2\"}
         ]
       }"
     ```

4. Create a Kubernetes secret that contains the AWS access key and secret key. Leave `sessionToken` empty for long-lived keys.
   ```yaml
   kubectl apply -n {{< reuse "/docs/snippets/namespace.md" >}} -f - << EOF
   apiVersion: v1
   kind: Secret
   metadata:
     name: aws-creds
   stringData:
     accessKey: ${AWS_ACCESS_KEY_ID}
     secretKey: ${AWS_SECRET_ACCESS_KEY}
     sessionToken: ""
   type: Opaque
   EOF
   ```

## Create a Lambda function

Create an AWS Lambda function to test {{< reuse "/docs/snippets/kgateway.md" >}} routing.

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

Create `Backend` and `HTTPRoute` resources to route requests to the Lambda function.

1. In your terminal, create a Backend resource that references the Lambda secret. Update the `region` with your AWS account region, such as `us-east-1`, and update the `accountId`.
   
   ```yaml
   kubectl apply -f - <<EOF
   apiVersion: gateway.kgateway.dev/v1alpha1
   kind: Backend
   metadata:
     name: lambda
     namespace: {{< reuse "/docs/snippets/namespace.md" >}}
   spec:
     type: AWS
     aws:
       region: ${REGION}
       accountId: "${ACCOUNT_ID}"
       auth:
         type: Secret
         secretRef:
           name: aws-creds
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
     namespace: {{< reuse "/docs/snippets/namespace.md" >}}
   spec:
     parentRefs:
       - name: http
         namespace: {{< reuse "/docs/snippets/namespace.md" >}}
     rules:
     - matches:
       - path:
           type: PathPrefix
           value: /echo
       backendRefs:
       - name: lambda
         namespace: {{< reuse "/docs/snippets/namespace.md" >}}
         group: gateway.kgateway.dev
         kind: Backend
   EOF
   ```

3. Confirm that {{< reuse "/docs/snippets/kgateway.md" >}} correctly routes requests to Lambda by sending a curl request to the `echo` function.
   
   {{< tabs items="Cloud Provider LoadBalancer,Port-forward for local testing" tabTotal="2" >}}
   {{% tab tabName="Cloud Provider LoadBalancer" %}}
   ```sh
   curl -H "Host: lambda.${REGION}.amazonaws.com" \
     $INGRESS_GW_ADDRESS:8080/echo \
     -d '{"key1":"value1", "key2":"value2"}' -X POST
   ```
   {{% /tab %}}
   {{% tab tabName="Port-forward for local testing" %}}
   ```sh
   curl -H "Host: lambda.${REGION}.amazonaws.com" \
     localhost:8080/echo \
     -d '{"key1":"value1", "key2":"value2"}' -X POST
   ```
   {{% /tab %}}
   {{< /tabs >}}

   Example response:
   
   ```json
   {"statusCode":200,"body":"Response from AWS Lambda. Here's the request you just sent me: {\"key1\":\"value1\",\"key2\":\"value2\"}"}% 
   ```

At this point, {{< reuse "/docs/snippets/kgateway.md" >}} is routing directly to the `echo` Lambda function!

## Cleanup

{{% reuse "docs/snippets/cleanup.md" %}}

1. Delete the `lambda` HTTPRoute and `lambda` Backend.
   
   ```sh
   kubectl delete HTTPRoute lambda -n {{< reuse "/docs/snippets/namespace.md" >}}
   kubectl delete Backend lambda -n {{< reuse "/docs/snippets/namespace.md" >}}
   ```

2. Delete the `aws-creds` secret.
   
   ```sh
   kubectl delete secret aws-creds -n {{< reuse "/docs/snippets/namespace.md" >}}
   ```

3. Use the AWS Lambda console to delete the `echo` test function.

