---
title: Overview
weight: 10
---

Learn more about {{< reuse "docs/snippets/product-name.md" >}}, its architecture, and benefits. 

## About kgateway

{{< reuse "docs/snippets/product-name-caps.md" >}} is a feature-rich, fast, and flexible Kubernetes-native ingress controller and next-generation API gateway that is built on top of [Envoy proxy](https://www.envoyproxy.io/) and the {{< reuse "docs/snippets/k8s-gateway-api-name.md" >}}. An API Gateway is a reverse proxy that serves as a security barrier between your clients and the microservices that make up your app. In order to access a microservice, all clients must send a request to the API Gateway. The API Gateway then verifies and routes the request to the microservice.

{{< reuse "docs/snippets/product-name-caps.md" >}} is fully conformant with the {{< reuse "docs/snippets/k8s-gateway-api-name.md" >}} and extends its functionality with custom Gateway APIs, such as RouteOption, VirtualHostOption, or Backends. These resources help to centrally configure advanced traffic management, security, and resiliency rules for a specific component, such as a host, route, or gateway listener.

## Extensions

The {{< reuse "docs/snippets/product-name.md" >}} project provides the following extensions on top of the {{< reuse "docs/snippets/k8s-gateway-api-name.md" >}} to configure advanced routing, security, and resiliency capabilities.

{{< cards >}}
  {{< card link="/docs/security/access-logging/" title="Access logging" tag="Security" >}}
  {{< card link="/docs/setup/customize/aws-elb/" title="AWS ALB and NLB" tag="Traffic" >}}
  {{< card link="/docs/traffic-management/destination-types/backends/lambda" title="AWS Lambda" tag="Traffic" >}}
  {{< card link="/docs/traffic-management/buffering/" title="Buffering" tag="Traffic" >}}
  {{< card link="/docs/security/cors/" title="Cross-Origin Resource Sharing (CORS)" tag="Security" >}}
  {{< card link="/docs/security/csrf/" title="Cross-Site Request Forgery (CSRF)" tag="Security" >}}
  {{< card link="/docs/traffic-management/route-delegation/" title="Delegation" tag="Traffic" >}}
  {{< card link="/docs/traffic-management/direct-response/" title="Direct responses" tag="Traffic" >}}
  {{< card link="/docs/resiliency/fault-injection/" title="Fault injection" tag="Resiliency" >}}
  {{< card link="/docs/setup/customize/" title="Gateway customization" tag="Setup" >}}
  {{< card link="/docs/traffic-management/header-control/" title="Header control" tag="Traffic" >}}
  {{< card link="/docs/traffic-management/health-checks/" title="Health checks" tag="Traffic" >}}
  {{< card link="/docs/integrations/" title="Integrations" tag="Setup" >}}
  {{< card link="/docs/security/local/" title="Local rate limiting" tag="Security" >}}
  {{< card link="/docs/traffic-management/proxy-protocol/" title="Proxy protocol" tag="Traffic" >}}
  {{< card link="/docs/traffic-management/redirect/" title="Redirects" tag="Traffic" >}}
  {{< card link="/docs/traffic-management/match/" title="Request matching" tag="Traffic" >}}
  {{< card link="/docs/about/resource-validation/" title="Resource validation" tag="Setup" >}}
  {{< card link="/docs/resiliency/retry/" title="Retries" tag="Resiliency" >}}
  {{< card link="/docs/traffic-management/rewrite/" title="Rewrites" tag="Traffic" >}}
  {{< card link="/docs/resiliency/shadowing/" title="Shadowing" tag="Resiliency" >}}
  {{< card link="/docs/traffic-management/tcp_keepalive/" title="TCP keepalive" tag="Traffic" >}}
  {{< card link="/docs/resiliency/timeouts/" title="Timeouts" tag="Resiliency" >}}
  {{< card link="/docs/traffic-management/transformations/" title="Transformations" tag="Traffic" >}}
{{< /cards >}}

## Default gateway proxy setup

{{< reuse "docs/snippets/product-name-caps.md" >}} automatically spins up, bootstraps, and manages gateway proxy deployments when you create a Kubernetes Gateway resource. To do that, a combination of {{< reuse "docs/snippets/product-name.md" >}} and Kubernetes resources are used, such as GatewayClass, GatewayParameters, Settings, and a gateway proxy template that includes the Envoy configuration that each proxy is bootstrapped with. 

To learn more about the default setup and how these resources interact with each other, see the [Default gateway proxy setup](/docs/setup/default/).