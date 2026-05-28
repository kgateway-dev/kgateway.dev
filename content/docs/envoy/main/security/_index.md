---
title: Security
icon: security
weight: 450
description: Secure your gateway to prevent unauthenticated and unauthorized access to your apps. 
---
Secure your gateway to prevent unauthenticated and unauthorized access to your apps. 

Securing your API gateway involves multiple layers of protection to safeguard traffic, enforce encryption, and maintain observability. These security features work best in combination. 

For example, you might use HTTPS listeners for external client connections, enforce backend TLS for internal workload security, use Istio for mutual TLS across workloads within your cluster environment, and automate certificate management of the DNS for your gateway's hostname with ExternalDNS and Cert-Manager. Access logging provides visibility into all these layers, ensuring a comprehensive security posture for your API gateway deployment.

{{< cards >}}
  {{< card link="access-logging" title="Access logging" subtitle="Capture an access log for all the requests that enter the gateway." >}}
  {{< card link="acl" title="IP-based access control (ACL)" subtitle="Allow or deny HTTP requests based on the client's source IP address using an ACL policy." >}}
  {{< card link="cors" title="CORS" subtitle="Enforce client-site access controls with cross-origin resource sharing (CORS)." >}}
  {{< card link="jwt" title="JWT" subtitle="Control access or route traffic based on verified claims in a JSON web token (JWT)." >}}
  {{< card link="csrf" title="CSRF" subtitle="Apply a CSRF filter to the gateway to help prevent cross-site request forgery attacks." >}}
  {{< card link="extauth" title="Bring your own external auth" subtitle="Authenticate requests with API keys, basic auth, or your own external auth service." >}}
  {{< card link="ratelimit" title="Rate limiting" subtitle="Throttle requests with local rate limiting or a global rate limit service." >}}
  {{< card link="backend-tls" title="Backend TLS" subtitle="Originate a one-way TLS connection from the Gateway to a backend." >}}
  {{< card path="/setup/listeners/https/" title="HTTPS listener" icon="bookmark" subtitle="Add an HTTPS listener that terminates TLS at the gateway.">}}
  {{< card path="/setup/listeners/sni/" title="SNI listener" icon="bookmark" subtitle="Serve multiple hostnames from one HTTPS listener by selecting certificates with SNI.">}}
  {{< card path="/setup/listeners/tls-passthrough/" title="TLS passthrough" icon="bookmark" subtitle="Set up a TLS listener on the Gateway that serves one or more hosts and passes TLS traffic through to a destination.">}}
  {{< card path="/integrations/external-dns-cert-manager/" title="ExternalDNS and Cert-Manager" icon="bookmark" subtitle="Automate DNS record creation and TLS certificate provisioning with ExternalDNS and cert-manager.">}}
  {{< card path="/integrations/istio/" title="Istio for mTLS" icon="bookmark" subtitle="Use kgateway as the ingress gateway for an Istio ambient or sidecar service mesh.">}}
{{< /cards >}}

<!--{{< card path="/integrations/istio/" title="Istio service mesh for mTLS" icon="bookmark" subtitle="Use kgateway as the ingress gateway for an Istio ambient or sidecar service mesh.">}}-->
