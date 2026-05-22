---
title: Security
icon: security
weight: 450
description: Secure your gateway to prevent unauthenticated and unauthorized access to your apps. 
---

Secure your gateway to prevent unauthenticated and unauthorized access to your apps. 

Securing your API gateway involves multiple layers of protection to safeguard traffic, enforce encryption, and maintain observability. These security features work best in combination. 

For example, you might use HTTPS listeners for external client connections, enforce backend TLS for internal workload security, use Istio for mutual TLS across workloads within your cluster environment, and automate certificate management of the DNS for your gateway's hostname with ExternalDNS and Cert-Manager. Access logging provides visibility into all these layers, ensuring a comprehensive security posture for your API gateway deployment.
<!--{{< card path="/integrations/istio/" title="Istio service mesh for mTLS" icon="bookmark">}}-->
