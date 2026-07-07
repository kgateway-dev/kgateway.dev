1. Save the name and region of your AWS EKS cluster and your AWS account ID in environment variables.
   ```sh
   export CLUSTER_NAME="<cluster-name>"
   export REGION="<region>"
   export AWS_ACCOUNT_ID=<aws-account-ID>
   export IAM_POLICY_NAME=AWSLoadBalancerControllerIAMPolicyNew
   export IAM_SA=aws-load-balancer-controller
   ```

2. Create an AWS IAM policy and bind it to a Kubernetes service account. 
   ```sh
   # Set up an IAM OIDC provider for a cluster to enable IAM roles for pods
   eksctl utils associate-iam-oidc-provider \
    --region ${REGION} \
    --cluster ${CLUSTER_NAME} \
    --approve

   # Fetch the IAM policy that is required for the Kubernetes service account
   curl -o iam-policy.json https://raw.githubusercontent.com/kubernetes-sigs/aws-load-balancer-controller/v2.5.3/docs/install/iam_policy.json

   # Create the IAM policy
   aws iam create-policy \
    --policy-name ${IAM_POLICY_NAME} \
    --policy-document file://iam-policy.json

   # Create the Kubernetes service account
   eksctl create iamserviceaccount \
    --cluster=${CLUSTER_NAME} \
    --namespace=kube-system \
    --name=${IAM_SA} \
    --attach-policy-arn=arn:aws:iam::${AWS_ACCOUNT_ID}:policy/${IAM_POLICY_NAME} \
    --override-existing-serviceaccounts \
    --approve \
    --region ${REGION}
   ```

3. Verify that the service account is created in your cluster. 
   ```sh
   kubectl -n kube-system get sa aws-load-balancer-controller -o yaml
   ```

4. Deploy the AWS Load Balancer Controller. 
   ```sh
   kubectl apply -k "github.com/aws/eks-charts/stable/aws-load-balancer-controller/crds?ref=master"

   helm repo add eks https://aws.github.io/eks-charts
   helm repo update
   helm install aws-load-balancer-controller eks/aws-load-balancer-controller \
     -n kube-system \
     --set clusterName=${CLUSTER_NAME} \
     --set serviceAccount.create=false \
     --set serviceAccount.name=${IAM_SA}
   ```