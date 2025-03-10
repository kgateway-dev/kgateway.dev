---
title: AWS EC2
weight: 30
---

Route traffic directly to an AWS EC2 instance. 

## Before you begin 

{{< reuse "docs/snippets/prereq.md" >}}

## Set up an AWS EC2 instance

1. Follow the AWS documentation to [launch an AWS EC2 instance](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/EC2_GetStarted.html#ec2-launch-instance) with the following configuration: 
   * Use an `amazon linux` image. 
   * Configure the EC2 instance's security group to allow HTTP traffic on port 80. 
   * Add the following tags: 
     - `gateway-id: abcde123`
     - `gateway-tag: group1`
     - `version: v1.2.3`. 

2. [Connect to your EC2 instance](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/EC2_GetStarted.html#ec2-connect-to-instance). 

3. Use the following script to set up a demo echo app that returns specific HTTP response codes. For example, a request to `http://$INSTANCE_IP/?code=404` returns a 404 HTTP response. 
   ```sh
   wget https://mitch-solo-public.s3.amazonaws.com/echoapp2
   chmod +x echoapp2
   sudo ./echoapp2 --port 81 &
   ```
   
4. Verify that you can reach the echo app. The following curl request returns the app's help menu. 
   ```sh
   curl http://$INSTANCE_IP/
   ```
   
## Create AWS credentials

Create AWS credentials for the EC2 instance so that Gloo Gateway can connect to it. 

{{% callout type="info" %}}
The following example shows how to use a user's AWS access key ID and secret key to authenticate with AWS, and an AWS role to authorize access to the EC2 instance. This approach is recommended. However, you can also assign the required permissions to your AWS user directly and only use an AWS access key ID and secret key. 
{{% /callout %}}

1. Get the AWS access key ID and secret key of the user that you want to use to authenticate with AWS. For more information, see the [AWS documentation](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_credentials_access-keys.html). 

2. Create a Kubernetes secret that holds your AWS access key ID and secret key. 
   ```sh
   glooctl create secret aws \
    --name gateway-tag-group1 \
    --namespace default \
    --access-key <aws_access_key_ID> \
    --secret-key <aws_secret_key>
    ```

3. Create an AWS role. 
   1. From the AWS console, navigate to **IAM** > **Roles**. 
   2. Click **Create Role**.
   3. Select **AWS account** as the type of trusted entity.
   4. Enter the 12-digit account ID of the account that has the EC2 instances that you want to route to.
   5. Assign the required permission. At a minimum, you must be able to describe EC2 instances. The following example shows a sample policy configuration. 
      ```json
      {
        "Version": "2012-10-17",
        "Statement": [
           {
               "Sid": "VisualEditor0",
               "Effect": "Allow",
               "Action": "ec2:DescribeInstances",
               "Resource": "*"
           }
        ]
      }
      ```

4. Add your AWS user as a trusted entity to your role. 
   1. Open the AWS role that you created. 
   2. Navigate to the **Trust relationship** tab. 
   3. Edit the **Trusted entities** to allow your AWS user to assume this role. 
      ```json
      {
       "Version": "2012-10-17",
       "Statement": [
           {
               "Effect": "Allow",
               "Principal": {
                   "AWS": "arn:aws:iam::<account-ID>:user/<user_ID>"
               },
               "Action": "sts:AssumeRole",
               "Condition": {}
           }
       ]
      }
      ``` 
 
## Set up routing to your EC2 instance


1. Create an Backend that represents your EC2 instance. Replace the AWS region with the region that your instance is in. Also make sure to add the ARN of the AWS role that you created earlier. If you assigned the permissions directly to your AWS user, the AWS access key ID and secret key are sufficient to authenticate with AWS and access the EC2 instance. In this case, remove the `spec.awsEc2.roleArn` from your Backend configuration. 
   ```yaml
   kubectl apply -f- <<EOF              
   apiVersion: gloo.solo.io/v1
   kind: Backend
   metadata:
     annotations:
     name: my-ec2-backend
     namespace: {{< reuse "docs/snippets/ns-system.md" >}}
   spec:
     awsEc2:
       filters:
       - key: gateway-id
       - kvPair:
           key: gateway-tag
           value: group1
       - kvPair:
           key: version
           value: v1.2.3
       region: <region>
       publicIp: true
       port: 81
       secretRef:
         name: gateway-tag-group1
         namespace: default
       roleArn: <role-arn>
   EOF
   ```

2. Create an HTTPRoute that routes traffic to the EC2 Backend. 
   ```yaml
   kubectl apply -f- <<EOF   
   apiVersion: gateway.networking.k8s.io/v1
   kind: HTTPRoute
   metadata:
     name: ec2-route
     namespace: {{< reuse "docs/snippets/ns-system.md" >}}
   spec:
     hostnames:
     - ec2.example
     parentRefs:
     - group: gateway.networking.k8s.io
       kind: Gateway
       name: http
       namespace: {{< reuse "docs/snippets/ns-system.md" >}}
     rules:
     - backendRefs:
       - group: gloo.solo.io
         kind: Backend
         name: ec2
       matches:
       - path:
           type: PathPrefix
           value: /
   EOF
   ```

3. Send a request to your EC2 instance. 
   {{< tabs items="Cloud Provider LoadBalancer,Port-forward for local testing"  >}}
   {{% tab %}}
   ```sh
   curl -vik http://$INGRESS_GW_ADDRESS:8080/\?code\=500 -H "host: ec2.example:8080"
   ```
   {{% /tab %}}
   {{% tab  %}}
   ```sh
   curl localhost:8080/\?code\=500 -H "host: ec2.example"
   ```
   {{% /tab %}}
   {{< /tabs >}}
   
   Example output: 
   ```
   * Mark bundle as not supporting multiuse
   < HTTP/1.1 500 Internal Server Error
   HTTP/1.1 500 Internal Server Error
   < date: Thu, 14 Nov 2024 20:01:57 GMT
   date: Thu, 14 Nov 2024 20:01:57 GMT
   < content-length: 0
   content-length: 0
   < x-envoy-upstream-service-time: 206
   x-envoy-upstream-service-time: 206
   < server: envoy
   server: envoy
   ```


## Cleanup

1. Remove the Backend and HTTProute.
   ```sh
   kubectl delete httproute ec2-route -n {{< reuse "docs/snippets/ns-system.md" >}}
   kubectl delete backend ec2 -n {{< reuse "docs/snippets/ns-system.md" >}}
   ```

2. Delete the AWS role or revoke permissions for your user.  

3. Delete the AWS EC2 instance. 
