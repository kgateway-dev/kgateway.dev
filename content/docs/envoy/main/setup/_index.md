---
title: Gateway setup
icon: dns
description: Configure gateway proxies, listeners, and gateway-level options.
weight: 300
---
Review your options for configuring gateway proxies and the HTTP or HTTPS listeners on the gateway proxies.

{{< cards >}}
  {{< card link="gateway" title="Set up a gateway" subtitle="Set up your first gateway proxy and explore how to use it to route traffic to a sample app." >}}
  {{< card link="default" title="Default gateway proxy setup" subtitle="Walk through the default GatewayClass, GatewayParameters, and proxy resources that kgateway creates." >}}
  {{< card link="customize" title="Gateway customization" subtitle="Customize the proxy deployment, service, and pod settings with GatewayParameters." >}}
  {{< card link="listeners" title="Listeners" subtitle="Add HTTP, HTTPS, TCP, TLS, mTLS, and SNI listeners to your gateway." >}}
  {{< card link="customize/selfmanaged" title="Self-managed gateways (BYO)" subtitle="Run your own bring-your-own gateway proxy alongside the kgateway control plane." >}}
  {{< card link="http10" title="HTTP/1.0 and HTTP/0.9" subtitle="Allow HTTP/1.0 and HTTP/0.9 traffic on a listener for legacy clients." >}}
{{< /cards >}}
