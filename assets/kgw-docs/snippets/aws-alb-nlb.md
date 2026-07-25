## About AWS Elastic Load Balancers (ELBs)

{{< reuse "kgw-docs/snippets/kgateway-capital.md" >}} is an application (L7) proxy based on Envoy and the {{< reuse "kgw-docs/snippets/k8s-gateway-api-name.md" >}} that can act as both a secure edge router and as a developer-friendly Kubernetes ingress/egress (north-south traffic) gateway. You can get many benefits by pairing {{< reuse "kgw-docs/snippets/kgateway.md" >}} with an AWS Elastic Load Balancer (ELB), including better cross availability zone failover and deeper integration with AWS services like AWS Certificate Manager, AWS CLI & CloudFormation, and Route 53 (DNS).

AWS provides the following types of ELBs:

* **Network Load Balancer (NLB)**: An optimized L4 TCP/UDP load balancer that can handle very high throughput (millions of requests per second) while maintaining low latency. This load balancer also has deep integration with other AWS services like Route 53 (DNS).
* **Application Load Balancer (ALB)**: An L7 HTTP-only load balancer that is focused on providing HTTP request routing capabilities.

### AWS NLB vs. ALB

In general, using a {{< reuse "kgw-docs/snippets/kgateway.md" >}} proxy with an AWS NLB is recommended, as NLBs provide more transport (L4) capabilities than AWS ALBs but no application (L7) capabilities. For example, you can configure the NLB for TLS passthrough and terminate TLS traffic on the gateway. You can also terminate traffic at the NLB and configure the NLB with a certificate that is used to secure the connection from the NLB to the gateway proxy.

ALBs can be useful if you want to use AWS Web Application Firewall (WAF) policies. Because TLS traffic is terminated at the ALB, you are responsible for securing the connection from the ALB to the {{< reuse "kgw-docs/snippets/kgateway.md" >}} proxy. The AWS Load Balancer Controller supports the [creation of an ALB through the Kubernetes Gateway API](https://kubernetes-sigs.github.io/aws-load-balancer-controller/latest/guide/gateway/l7gateway/).
