Route traffic directly to AWS EC2 instances that the gateway proxy discovers dynamically by using tag-based filters. Endpoints are refreshed periodically and served to Envoy through EDS (Endpoint Discovery Service), so your routing stays up to date as instances start and stop.

## Before you begin

{{< reuse "docs/snippets/prereq.md" >}}

2. Enable EC2 discovery when you install or upgrade {{< reuse "/docs/snippets/kgateway.md" >}} by setting the `controller.enableAwsEc2Discovery` Helm value to `true`.

   ```sh
   helm upgrade --install kgateway oci://ghcr.io/kgateway-dev/charts/kgateway \
     --namespace {{< reuse "docs/snippets/namespace.md" >}} \
     --set controller.enableAwsEc2Discovery=true
   ```

## Create an AWS EC2 instance {#ec2-instance}

1. Follow the AWS documentation to [launch an EC2 instance](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/EC2_GetStarted.html#ec2-launch-instance) with the following settings:
   - Use an Amazon Linux image.
   - Allow inbound HTTP traffic on port 80 in the instance's security group.
   - Add at least one tag that you later use to discover the instance, for example `app: payments`.

2. Save the AWS region as an environment variable.
   ```sh
   export AWS_REGION=<region, such as us-east-2>
   ```

3. [Connect to your EC2 instance](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/EC2_GetStarted.html#ec2-connect-to-instance) and start a simple HTTP echo server to use for testing.
   ```sh
   wget https://mitch-solo-public.s3.amazonaws.com/echoapp2
   chmod +x echoapp2
   sudo ./echoapp2 --port 80 &
   ```

4. Verify that the echo server is reachable. Replace `$INSTANCE_IP` with the public or private IP of your instance.
   ```sh
   curl http://$INSTANCE_IP/help
   ```

   Example output:
   ```
   usage:
     curl -v http://localhost:8080/?code=<httpCode>
       where httpCode is a http response code such as 200, 404, or 500

     /metrics - returns http response code metrics
     /help    - prints this message
   ```

## Create AWS credentials {#credentials}

Your gateway proxy needs AWS credentials with `ec2:DescribeInstances` permission to discover EC2 instances.

1. Get the AWS access key ID and secret access key for the IAM user or role that you want to use. For more information, see the [AWS documentation](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_credentials_access-keys.html).

2. Verify that the credentials have at least the following IAM permission.
   ```json
   {
     "Version": "2012-10-17",
     "Statement": [
       {
         "Effect": "Allow",
         "Action": "ec2:DescribeInstances",
         "Resource": "*"
       }
     ]
   }
   ```

3. Save the credentials as environment variables.
   ```sh
   export AWS_ACCESS_KEY_ID=<your-access-key-id>
   export AWS_SECRET_ACCESS_KEY=<your-secret-access-key>
   export AWS_SESSION_TOKEN=<your-session-token-or-empty>
   ```

4. Create a Kubernetes secret that holds the credentials. Leave `sessionToken` empty if you are using long-lived IAM user keys.
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
     sessionToken: "${AWS_SESSION_TOKEN}"
   EOF
   ```

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
