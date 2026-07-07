Route traffic directly to AWS EC2 instances that the gateway proxy discovers dynamically by using tag-based filters. Endpoints are refreshed periodically and served to Envoy through EDS (Endpoint Discovery Service), so your routing stays up to date as instances start and stop.

## Before you begin

{{< reuse "kgw-docs/snippets/prereq.md" >}}

## Step 1: Enable EC2 discovery

Enable EC2 discovery by setting the `controller.enableAwsEc2Discovery` Helm value to `true` in your {{< reuse "kgw-docs/snippets/kgateway.md" >}} Helm chart. 

1. Optional: Get the values of your current installation. 
   ```sh
   helm get values {{< reuse "/kgw-docs/snippets/helm-kgateway.md" >}} -n {{< reuse "kgw-docs/snippets/namespace.md" >}} -o yaml > values.yaml
   open values.yaml
   ```

2. Enable EC2 discovery by setting the `controller.enableAwsEc2Discovery` Helm value to `true`. The `--reuse-values` setting re-applies any Helm values that you previously set.

   ```sh
   helm upgrade -i {{< reuse "/kgw-docs/snippets/helm-kgateway.md" >}} oci://{{< reuse "/kgw-docs/snippets/helm-path.md" >}}/charts/{{< reuse "/kgw-docs/snippets/helm-kgateway.md" >}} \
     --namespace {{< reuse "kgw-docs/snippets/namespace.md" >}} \
     --reuse-values \
     --version {{< reuse "kgw-docs/versions/helm-version-flag.md" >}} \
     --set controller.enableAwsEc2Discovery=true
   ```

3. Verify that the control plane pods are up and running. 
   ```sh
   kubectl get pods -n {{< reuse "kgw-docs/snippets/namespace.md" >}}
   ```


## Step 2: Create an AWS EC2 instance {#ec2-instance}

1. Follow the AWS documentation to [launch an EC2 instance](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/EC2_GetStarted.html) with the following settings:
   - Use an Amazon Linux image.
   - Allow inbound HTTP traffic on port 80 in the instance's security group.
   - Add at least one tag that you later use to discover the instance, for example `app: payments`.
   - Create a key file so that you can later connect to your instance by using SSH. 

2. Save the AWS region that your EC2 instance is created in as an environment variable. Make sure to use the region name (for example, `us-east-1`), not an availability zone (for example, `us-east-1b`).
   ```sh
   export AWS_REGION=<aws-region>
   ```

3. [Connect to your EC2 instance](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/EC2_GetStarted.html#ec2-connect-to-instance). 

4. Start an HTTP server on the EC2 instance. You can use the HTTP server that is built into Python by default. 
   ```sh
   sudo python3 -m http.server 80 &
   ```

5. Verify that you can send requests to the local HTTP server. 
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

## Step 3: Configure AWS credentials {#credentials}

For the gateway proxy to discover and route traffic to the EC2 instance, you must configure the proxy with the required AWS credentials. You can choose between the following authentication methods:
* **Static AWS credentials**: Store your AWS access key ID and secret access key in a Kubernetes secret.
* **Role assumption**: Configure an IAM role that the gateway proxy assumes to get temporary credentials.

For static credentials, the IAM user must have at least `ec2:DescribeInstances` permissions. For role assumption, the IAM user must have `sts:AssumeRole` permissions and the role must have at least `ec2:DescribeInstances` permissions.

{{< tabs >}}
{{% tab name="Static AWS credentials" %}}

Use this method when your IAM user and EC2 instances are in the same AWS account and you want a simple setup. The `ec2:DescribeInstances` permission is attached directly to your IAM user, and the gateway proxy uses those credentials as-is to discover EC2 instances.

{{< callout type="info" >}}
The steps in this example require a permanent IAM user with long-lived credentials. If you authenticate through AWS SSO (IAM Identity Center), `aws sts get-caller-identity` returns a role ARN rather than an IAM user ARN, and `aws iam create-access-key` fails with a `NoSuchEntity` error. In this case, create a dedicated IAM user first:
```sh
aws iam create-user --user-name kgateway-ec2-user
export IAM_USERNAME=kgateway-ec2-user
```
Then, skip step 1 to export your `IAM_USERNAME` and continue with the remaining steps.
{{< /callout >}}

1. Get your IAM username. If you are using AWS SSO, skip this command and use the `IAM_USERNAME` value you set earlier.
   ```sh
   export IAM_USERNAME=$(aws sts get-caller-identity --query 'Arn' --output text | cut -d'/' -f2)
   ```

2. Create the policy document and save the ARN in an environment variable. At a minimum, you must assign the `ec2:DescribeInstances` permission. 
   ```sh
   aws iam create-policy \
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
     }'

   export AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
   export POLICY_ARN="arn:aws:iam::${AWS_ACCOUNT_ID}:policy/kgateway-ec2-discovery"
   echo $POLICY_ARN
   ```

3. Attach the policy directly to your IAM user.
   ```sh
   aws iam attach-user-policy \
     --user-name ${IAM_USERNAME} \
     --policy-arn $POLICY_ARN
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

5. Create a Kubernetes secret that holds the credentials.
   ```yaml
   kubectl apply -n {{< reuse "kgw-docs/snippets/namespace.md" >}} -f - <<EOF
   apiVersion: v1
   kind: Secret
   metadata:
     name: aws-creds
   type: Opaque
   stringData:
     accessKey: "${AWS_ACCESS_KEY_ID}"
     secretKey: "${AWS_SECRET_ACCESS_KEY}"
   EOF
   ```

{{% /tab %}}
{{% tab name="Role assumption" %}}

Use this method when you want EC2 discovery to use a least-privilege IAM role rather than long-lived user credentials. The kgateway controller uses its own ambient IAM identity (configured via [IRSA](https://docs.aws.amazon.com/eks/latest/userguide/iam-roles-for-service-accounts.html)) to call `sts:AssumeRole` and obtain temporary credentials for the role. No Kubernetes secret is required. The `ec2:DescribeInstances` permission is attached to the role, not the controller's identity directly.

{{< callout type="warning" >}}
This method requires an EKS cluster with an OIDC provider. It does not work on local clusters such as Kind or minikube. If you are using a local cluster, use the **Static AWS credentials** method instead.
{{< /callout >}}

1. Verify that your EKS cluster has an OIDC provider associated with it, and save the provider ID in an environment variable.
   ```sh
   export OIDC_PROVIDER=$(aws eks describe-cluster --name <cluster-name> \
     --query "cluster.identity.oidc.issuer" --output text | sed 's|https://||')
   echo $OIDC_PROVIDER
   ```

   If this command returns nothing, [associate an OIDC provider with your cluster](https://docs.aws.amazon.com/eks/latest/userguide/enable-iam-roles-for-service-accounts.html) before continuing.

2. Get your AWS account ID.
   ```sh
   export AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
   ```

3. Create an IAM role for the kgateway controller with an IRSA trust policy. This lets the controller's ServiceAccount use the role.
   ```sh
   aws iam create-role \
     --role-name kgateway-controller-role \
     --assume-role-policy-document "{
       \"Version\": \"2012-10-17\",
       \"Statement\": [{
         \"Effect\": \"Allow\",
         \"Principal\": {\"Federated\": \"arn:aws:iam::${AWS_ACCOUNT_ID}:oidc-provider/${OIDC_PROVIDER}\"},
         \"Action\": \"sts:AssumeRoleWithWebIdentity\",
         \"Condition\": {\"StringEquals\": {
           \"${OIDC_PROVIDER}:sub\": \"system:serviceaccount:kgateway-system:kgateway\"
         }}
       }]
     }"
   ```

4. Create the EC2 discovery policy and save the ARN.
   ```sh
   aws iam create-policy \
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
     }'

   export POLICY_ARN="arn:aws:iam::${AWS_ACCOUNT_ID}:policy/kgateway-ec2-discovery"
   echo $POLICY_ARN
   ```

5. Create the EC2 discovery role and attach the policy to it. The controller role assumes this role to list EC2 instances.
   ```sh
   aws iam create-role \
     --role-name kgateway-ec2-role \
     --assume-role-policy-document "{
       \"Version\": \"2012-10-17\",
       \"Statement\": [{
         \"Effect\": \"Allow\",
         \"Principal\": {\"AWS\": \"arn:aws:iam::${AWS_ACCOUNT_ID}:role/kgateway-controller-role\"},
         \"Action\": \"sts:AssumeRole\"
       }]
     }"

   aws iam attach-role-policy \
     --role-name kgateway-ec2-role \
     --policy-arn $POLICY_ARN

   export ROLE_ARN=$(aws iam get-role --role-name kgateway-ec2-role --query 'Role.Arn' --output text)
   echo $ROLE_ARN
   ```

6. Allow the controller role to assume the EC2 discovery role.
   ```sh
   aws iam put-role-policy \
     --role-name kgateway-controller-role \
     --policy-name assume-ec2-role \
     --policy-document "{
       \"Version\": \"2012-10-17\",
       \"Statement\": [{
         \"Effect\": \"Allow\",
         \"Action\": \"sts:AssumeRole\",
         \"Resource\": \"${ROLE_ARN}\"
       }]
     }"
   ```

7. Annotate the kgateway controller's ServiceAccount with the controller role ARN and restart the controller.
   ```sh
   export CONTROLLER_ROLE_ARN=$(aws iam get-role --role-name kgateway-controller-role --query 'Role.Arn' --output text)

   kubectl annotate serviceaccount {{< reuse "kgw-docs/snippets/pod-name.md" >}} -n {{< reuse "kgw-docs/snippets/namespace.md" >}}  \
     eks.amazonaws.com/role-arn=${CONTROLLER_ROLE_ARN}

   kubectl rollout restart deployment/{{< reuse "kgw-docs/snippets/pod-name.md" >}} -n {{< reuse "kgw-docs/snippets/pod-name.md" >}} -n {{< reuse "kgw-docs/snippets/namespace.md" >}}
   kubectl rollout status deployment/{{< reuse "kgw-docs/snippets/pod-name.md" >}} -n {{< reuse "kgw-docs/snippets/pod-name.md" >}} -n {{< reuse "kgw-docs/snippets/namespace.md" >}}
   ```

{{% /tab %}}
{{< /tabs >}}

## Step 4: Set up EC2 routing {#routing}

Create a Backend resource that represents your EC2 instance and an HTTPRoute to route requests to it.

1. Create a Backend resource that represents the EC2 instance. Set the tag that you added to your EC2 instance earlier in the `ec2.filters` field so that the gateway proxy can discover the instance. You can also choose to route traffic to the instance's public or private IP address by using the `addressType` field. Note that if you choose a private address, your cluster must be in the same private network as the EC2 instance, such as in the same VPC.

   {{< tabs >}}
   {{% tab name="Static AWS credentials" %}}
   ```yaml
   kubectl apply -n {{< reuse "kgw-docs/snippets/namespace.md" >}} -f - <<EOF
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
   {{% /tab %}}
   {{% tab name="Role assumption" %}}
   ```yaml
   kubectl apply -n {{< reuse "kgw-docs/snippets/namespace.md" >}} -f - <<EOF
   apiVersion: gateway.kgateway.dev/v1alpha1
   kind: Backend
   metadata:
     name: ec2-backend
   spec:
     type: AWS
     aws:
       region: ${AWS_REGION}
       auth:
         type: AssumeRole
         assumeRole:
           roleArn: "${ROLE_ARN}"
       ec2:
         port: 80
         addressType: PublicIP
         filters:
         - keyValue:
             key: app
             value: payments
   EOF
   ```
   {{% /tab %}}
   {{< /tabs >}}

   | Field | Description |
   |---|---|
   | `ec2.port` | The port on the EC2 instance to route to. |
   | `ec2.addressType` | `PublicIP` to route to the public IP address; `PrivateIP` to route to the private IP address. |
   | `ec2.filters` | Tag-based filters to select EC2 instances. Only running instances that match all filters are included as endpoints. |
   | `auth.type` | The authentication method. Use `Secret` for static credentials stored in a Kubernetes secret, or `AssumeRole` to have the controller assume an IAM role using its ambient identity. |
   | `auth.assumeRole.roleArn` | The ARN of the IAM role to assume. Required when `auth.type` is `AssumeRole`. |

2. Create an HTTPRoute resource that references the `ec2-backend` Backend.
   ```yaml
   kubectl apply -n {{< reuse "kgw-docs/snippets/namespace.md" >}} -f - <<EOF
   apiVersion: gateway.networking.k8s.io/v1
   kind: HTTPRoute
   metadata:
     name: ec2-route
   spec:
     parentRefs:
     - name: http
       namespace: {{< reuse "kgw-docs/snippets/namespace.md" >}}
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

3. Verify that the Backend endpoint is discovered. The gateway proxy periodically calls `ec2:DescribeInstances` to refresh the list of running instances that match your filters.
   ```sh
   kubectl get backend ec2-backend -n {{< reuse "kgw-docs/snippets/namespace.md" >}} -o yaml
   ```

4. Send a request to the EC2 instance through the gateway proxy. Verify that the output equals the output that you saw earlier when you sent a request to the EC2 directly. 
   {{< tabs >}}
   {{% tab name="Cloud Provider LoadBalancer" %}}
   ```sh
   curl http://$INGRESS_GW_ADDRESS:8080/ -H "host: ec2.example"
   ```
   {{% /tab %}}
   {{% tab name="Port-forward for local testing" %}}
   ```sh
   curl http://localhost:8080/ -H "host: ec2.example"
   ```
   {{% /tab %}}
   {{< /tabs >}}

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

## Cleanup

{{% reuse "kgw-docs/snippets/cleanup.md" %}}

1. Delete the HTTPRoute and Backend.
   ```sh
   kubectl delete httproute ec2-route -n {{< reuse "kgw-docs/snippets/namespace.md" >}}
   kubectl delete backend ec2-backend -n {{< reuse "kgw-docs/snippets/namespace.md" >}}
   ```

2. Delete the AWS credentials secret.
   ```sh
   kubectl delete secret aws-creds -n {{< reuse "kgw-docs/snippets/namespace.md" >}}
   ```

3. Clean up the AWS IAM resources.

   {{< tabs >}}
   {{% tab name="Static AWS credentials" %}}
   ```sh
   aws iam detach-user-policy --user-name ${IAM_USERNAME} --policy-arn ${POLICY_ARN}
   aws iam delete-policy --policy-arn ${POLICY_ARN}
   ```
   {{% /tab %}}
   {{% tab name="Role assumption" %}}
   ```sh
   aws iam detach-role-policy --role-name kgateway-ec2-role --policy-arn ${POLICY_ARN}
   aws iam delete-role --role-name kgateway-ec2-role
   aws iam delete-policy --policy-arn ${POLICY_ARN}
   ```
   {{% /tab %}}
   {{< /tabs >}}

4. Terminate the EC2 instance from the AWS console.
