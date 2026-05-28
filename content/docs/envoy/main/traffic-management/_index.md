---
title: Traffic management
icon: traffic
description: Match, redirect, rewrite, split, and transform requests as they flow through your gateway.
weight: 400
---
{{< cards >}}
  {{< card link="destination-types" title="Destination types" subtitle="Configure routing to different types of service destinations." >}}
  {{< card link="direct-response" title="Direct response" subtitle="Return a fixed status code and body straight from the gateway without forwarding to a backend." >}}
  {{< card link="grpc" title="gRPC routing" subtitle="Route traffic to gRPC services by using the GRPCRoute resource for protocol-aware routing." >}}
  {{< card link="dfp" title="Dynamic Forward Proxy (DFP)" subtitle="Resolve upstream hosts dynamically at request time with a Dynamic Forward Proxy." >}}
  {{< card link="extproc" title="External processing (ExtProc)" subtitle="Modify aspects of an HTTP request or response with an external processing server." >}}
  {{< card link="match" title="Request matching" subtitle="Match requests by path, method, header, query parameter, or regular expression." >}}
  {{< card link="redirect" title="Redirects" subtitle="Redirect requests to a different host, path, scheme, or status code." >}}
  {{< card link="rewrite" title="Rewrites" subtitle="Rewrite the request host or path prefix before forwarding to a backend." >}}
  {{< card link="route-delegation" title="Route delegation" subtitle="Compose routing across teams by delegating subpaths to child HTTPRoute resources." >}}
  {{< card link="buffering" title="Buffering" subtitle="Buffer request and response bodies so that filters can inspect and transform them safely." >}}
  {{< card link="header-control" title="Header control" subtitle="Add, remove, or rewrite request and response headers on routes and listeners." >}}
  {{< card link="http2" title="HTTP/2" subtitle="Configure a service to use HTTP/2." >}}
  {{< card link="health-checks" title="Health checks" subtitle="Probe backend and gateway health to remove unhealthy endpoints from rotation." >}}
  {{< card link="proxy-protocol" title="Proxy protocol" subtitle="Preserve the original client IP and port by accepting PROXY protocol on a listener." >}}
  {{< card link="session-affinity" title="Session affinity" subtitle="Choose how the gateway selects a backend, from load balancing strategies to sticky sessions." >}}
  {{< card link="transformations" title="Transformations" subtitle="Transform request and response headers and bodies with templated expressions." >}}
  {{< card link="traffic-split" title="Traffic splitting" subtitle="Split traffic across multiple backends by weight for canary and blue/green rollouts." >}}
  {{< card link="weighted-routes" title="Route weighting" subtitle="Distribute traffic across multiple HTTPRoutes by weight for traffic shaping." >}}
{{< /cards >}}
