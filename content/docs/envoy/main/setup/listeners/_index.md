---
title: Listeners
description: Add HTTP, HTTPS, TCP, TLS, mTLS, and SNI listeners to your gateway.
weight: 20
---

{{< cards >}}
  {{< card link="overview" title="Listener overview" subtitle="Compare inline Gateway listeners and ListenerSet listeners and learn how to configure each." >}}
  {{< card link="http" title="HTTP listener" subtitle="Add an HTTP listener for plaintext traffic on a gateway." >}}
  {{< card link="https" title="HTTPS listener" subtitle="Add an HTTPS listener that terminates TLS at the gateway." >}}
  {{< card link="mtls" title="mTLS listener" subtitle="Create a FrontendTLSConfig on a Gateway to enforce mutual TLS between clients and listeners." >}}
  {{< card link="sni" title="SNI listener" subtitle="Serve multiple hostnames from one HTTPS listener by selecting certificates with SNI." >}}
  {{< card link="tcp" title="TCP listener" subtitle="Add a TCP listener to route non-HTTP traffic through the gateway." >}}
  {{< card link="tls-passthrough" title="TLS passthrough" subtitle="Set up a TLS listener on the Gateway that serves one or more hosts and passes TLS traffic through to a destination." >}}
  {{< card link="tls-termination" title="TLS termination for TLSRoutes" subtitle="Set up a TLS listener on the Gateway that terminates TLS traffic and forwards plain traffic to a backend service using a TLSRoute." >}}
  {{< card link="tls-termination-tcproute" title="TLS termination for TCPRoutes" subtitle="Set up a TLS listener on the Gateway that terminates TLS traffic and forwards plain traffic to a backend service using a TCPRoute." >}}
  {{< card link="tls-settings" title="Additional TLS settings" subtitle="Tune TLS settings such as minimum version and cipher suites on a listener." >}}
{{< /cards >}}

