---
title: AWS Lambda
weight: 30
---

Use kgateway to route traffic requests directly to an [Amazon Web Services (AWS) Lambda] (https://aws.amazon.com/lambda/resources/) function.

{{< callout >}}
{{< reuse "docs/snippets/proxy-kgateway.md" >}}
{{< /callout >}}

## About

Serverless functions, such as Lambda functions, provide an alternative to traditional applications or services. The functions run on servers that you do not have to manage yourself, and you pay for only for the compute time you use.

However, you might want to invoke your serverless functions from other services or apps, such as the Kubernetes workloads that run in your cluster. By abstracting a {{< gloss "Lambda" >}}Lambda{{< /gloss >}} as a type of destination in your kgateway environment, your workloads can send requests to the Lambda destination in the same way that you set up routing through kgateway to other types of destinations. kgateway does the work of assuming an AWS IAM role to invoke the actual Lambda function in your AWS account.

For more information, see the AWS Lambda documentation on [configuring Lambda functions as targets](https://docs.aws.amazon.com/elasticloadbalancing/latest/application/lambda-functions.html).

## Lambda access type

Check out the following guides for examples on how to invoke Lambda functions with kgateway, depending on the type of authentication that you want to use.

{{< cards >}}
  {{< card link="creds-secret" title="Access AWS Lambda with a credentials secret" >}}
  {{< card link="service-accounts" title="Access AWS Lambda with a service account" >}}
{{< /cards >}}