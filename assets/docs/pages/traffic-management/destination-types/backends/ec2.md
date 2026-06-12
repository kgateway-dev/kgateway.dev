Route traffic directly to AWS EC2 instances that the gateway proxy discovers dynamically by using tag-based filters. Endpoints are refreshed periodically and served to Envoy through EDS (Endpoint Discovery Service), so your routing stays up to date as instances start and stop.

## Before you begin

{{< reuse "docs/snippets/prereq.md" >}}

2. Enable EC2 discovery when you install or upgrade {{< reuse "/docs/snippets/kgateway.md" >}} by setting the `controller.enableAwsEc2Discovery` Helm value to `true`.

   ```sh
   helm upgrade --install kgateway oci://ghcr.io/kgateway-dev/charts/kgateway \
     --namespace {{< reuse "docs/snippets/namespace.md" >}} \
     --reuse-values \
     --set controller.enableAwsEc2Discovery=true
   ```

## Create an AWS EC2 instance {#ec2-instance}

1. Follow the AWS documentation to [launch an EC2 instance](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/EC2_GetStarted.html#ec2-launch-instance) with the following settings:
   - Use an Amazon Linux image.
   - Allow inbound HTTP traffic on port 80 in the instance's security group.
   - Add at least one tag that you later use to discover the instance, for example `app: payments`.
   - Create a key file so that you can later connect to your instance by using SSH. 

2. Save the AWS region that your EC2 instance is created in as an environment variable.
   ```sh
   export AWS_REGION=<aws-region>
   ```

3. Get the public IP address of your EC2 instance and save it in an environment variable. 
   ```sh
   export INSTANCE_IP=<public-ec2-IP>
   ```

4. [Connect to your EC2 instance](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/EC2_GetStarted.html#ec2-connect-to-instance). 

5. Start an HTTP server on the EC2 instance. You can use the HTTP server that is built into Python by default. 
   ```sh
   sudo python3 -m http.server 80 &
   ```

6. Verify that you can send requests to the local HTTP server. 
   ```sh
   curl http://localhost/
   ```

   Example output: 
   ```console
   <!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd">
   <html>
   <head>
   <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
   <title>Directory listing for /</title>
   </head>
   <body>
   <h1>Directory listing for /</h1>
   <hr>
   <ul>
   <li><a href=".bash_logout">.bash_logout</a></li>
   <li><a href=".bash_profile">.bash_profile</a></li>
   <li><a href=".bashrc">.bashrc</a></li>
   <li><a href=".ssh/">.ssh/</a></li>
   </ul>
   <hr>
   </body>
   </html>
   ```

## Configure AWS credentials {#credentials}

For the gateway proxy to discover and route traffic to the EC2 instance, you must configure the proxy with the required AWS credentials. You can choose between the following authentication methods: 
* **Static AWS credentials**: Store your AWS secret key and access key ID in a Kubernetes secret. Then, 
* Role assumption: 

The credentials must have at least `ec2:DescribeInstances` permissions. 

{{< tabs items="Static AWS credentials,Role assumption" >}}
{{% tab tabName="Static AWS credentials" %}}

1. Create the policy document and save the ARN in an environment variable. At a minimum, you must assign the `ec2:DescribeInstances` permission. 
   ```sh
   export POLICY_ARN=$(aws iam create-policy \
     --policy-name kgateway-ec2-discovery \
     --policy-document '{
       "Version": "2012-10-17",
       "Statement": [
         {
           "Effect": "Allow",
           "Action": "ec2:DescribeInstances",
           "Resource": "*"
         }
       ]
     }' \
     --query 'Policy.Arn' \
     --output text)

   echo $POLICY_ARN
   ```

2. Create a role and configure your IAM user to assume this role. 
   ```sh
   export AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
   export IAM_USERNAME=$(aws sts get-caller-identity --query 'Arn' --output text | cut -d'/' -f2)

   aws iam create-role \
     --role-name kgateway-ec2-role \
     --assume-role-policy-document "{
       \"Version\": \"2012-10-17\",
       \"Statement\": [{
         \"Effect\": \"Allow\",
         \"Principal\": {\"AWS\": \"arn:aws:iam::${AWS_ACCOUNT_ID}:user/${IAM_USERNAME}\"},
         \"Action\": \"sts:AssumeRole\"
       }]
     }"
   ```

3. Attach the policy to the role. 
   ```sh
   aws iam attach-role-policy \
    --role-name kgateway-ec2-role \
    olicy-arn $POLICY_ARN     
   ```

4. Create permanent AWS credentials for your user. 
   ```sh
   eval $(aws iam create-access-key --user-name ${IAM_USERNAME} \
     --query 'AccessKey.[AccessKeyId,SecretAccessKey]' \
     --output text | \
     awk '{print "export AWS_ACCESS_KEY_ID="$1"\nexport AWS_SECRET_ACCESS_KEY="$2}')

   echo "AWS_ACCESS_KEY_ID $AWS_ACCESS_KEY_ID"
   echo "AWS_SECRET_ACCESS_KEY $AWS_SECRET_ACCESS_KEY"
   ```

5. Create a Kubernetes secret that holds the credentials. Note that if you don't use long-lived AWS credentials, you must also provide an AWS session token in the `sessionToken` field.
   ```yaml
   kubectl apply -n {{< reuse "docs/snippets/namespace.md" >}} -f - <<EOF
   apiVersion: v1
   kind: Secret
   metadata:
     name: aws-creds
   type: Opaque
   stringData:
     accessKey: "${AWS_ACCESS_KEY_ID}"
     secretKey: "${AWS_SECRET_ACCESS_KEY}"
     # sessionToken: "${AWS_SESSION_TOKEN}"
   EOF
   ```

{{% /tab %}}
{{% tab tabName="Role assumption" %}}
{{% /tab %}}
{{< /tabs >}}

## Set up EC2 routing {#routing}

Create `Backend` and `HTTPRoute` resources to route requests to your EC2 instances.

1. Create a Backend resource that represents the EC2 instance. Set the tag that you added to your EC2 instance earlier in the `ec2.filters` field so that the gateway proxy can discover the instance. You can also choose to route traffic to the instance's public or private IP address by using the `addressType` field. Note that if you choose a private address, your cluster must be in the same private network as the EC2 instance, such as in the same VPC.  
   ```yaml
   kubectl apply -n {{< reuse "docs/snippets/namespace.md" >}} -f - <<EOF
   apiVersion: gateway.kgateway.dev/v1alpha1
   kind: Backend
   metadata:
     name: ec2-backend
   spec:
     type: AWS
     aws:
       region: ${AWS_REGION}
       auth:
         type: Secret
         secretRef:
           name: aws-creds
       ec2:
         port: 80
         addressType: PublicIP
         filters:
         - keyValue:
             key: app
             value: payments
   EOF
   ```

   | Field | Description |
   |---|---|
   | `ec2.port` | The port on the EC2 instance to route to. |
   | `ec2.addressType` | `PublicIP` to route to the public IP address; `PrivateIP` to route to the private IP address. |
   | `ec2.filters` | Tag-based filters to select EC2 instances. Only running instances that match all filters are included as endpoints. |

2. Create an HTTPRoute resource that references the `ec2-backend` Backend.
   ```yaml
   kubectl apply -n {{< reuse "docs/snippets/namespace.md" >}} -f - <<EOF
   apiVersion: gateway.networking.k8s.io/v1
   kind: HTTPRoute
   metadata:
     name: ec2-route
   spec:
     parentRefs:
     - name: http
       namespace: {{< reuse "docs/snippets/namespace.md" >}}
     hostnames:
     - ec2.example
     rules:
     - matches:
       - path:
           type: PathPrefix
           value: /
       backendRefs:
       - name: ec2-backend
         group: gateway.kgateway.dev
         kind: Backend
   EOF
   ```

3. Verify that the Backend endpoint is discovered. {{< reuse "/docs/snippets/kgateway.md" >}} periodically calls `ec2:DescribeInstances` to refresh the list of running instances that match your filters.
   ```sh
   kubectl get backend ec2-backend -n {{< reuse "docs/snippets/namespace.md" >}} -o yaml
   ```

4. Send a request to the EC2 instance through the gateway.
   {{< tabs items="Cloud Provider LoadBalancer,Port-forward for local testing" tabTotal="2" >}}
   {{% tab tabName="Cloud Provider LoadBalancer" %}}
   ```sh
   curl http://$INGRESS_GW_ADDRESS:8080/help -H "host: ec2.example"
   ```
   {{% /tab %}}
   {{% tab tabName="Port-forward for local testing" %}}
   ```sh
   curl http://localhost:8080/help -H "host: ec2.example"
   ```
   {{% /tab %}}
   {{< /tabs >}}

   Example output:
   ```
   usage:
     curl -v http://localhost:8080/?code=<httpCode>
       where httpCode is a http response code such as 200, 404, or 500
   ```

## Cleanup

{{% reuse "docs/snippets/cleanup.md" %}}

1. Delete the HTTPRoute and Backend.
   ```sh
   kubectl delete httproute ec2-route -n {{< reuse "docs/snippets/namespace.md" >}}
   kubectl delete backend ec2-backend -n {{< reuse "docs/snippets/namespace.md" >}}
   ```

2. Delete the AWS credentials secret.
   ```sh
   kubectl delete secret aws-creds -n {{< reuse "docs/snippets/namespace.md" >}}
   ```

3. Terminate the EC2 instance from the AWS console.
