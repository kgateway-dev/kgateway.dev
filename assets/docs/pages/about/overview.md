{{< reuse "docs/snippets/kgateway-about.md" >}}

In this topic, you learn about the basics of API gateways for microservices, the extensions that {{< reuse "/docs/snippets/kgateway.md" >}} provides beyond typical API gateway functionality, and the default API gateway proxy setup.

{{< callout icon="agentgateway" >}}
Looking for an AI gateway to connect agents, MCP tools, and LLMs? Check out the [agentgateway data plane docs](../../agentgateway/).
{{< /callout >}}

## API gateway {#api-gateway}

The {{< reuse "/docs/snippets/kgateway.md" >}} data plane is a feature-rich, fast, and flexible Kubernetes-native [ingress controller](#what-is-an-ingress) and next-generation [API gateway](#what-is-an-api-gateway) that is built on top of [Envoy proxy](https://www.envoyproxy.io/) and the [{{< reuse "docs/snippets/k8s-gateway-api-name.md" >}}](#what-is-the-kubernetes-gateway-api). 

### What is an ingress?

An ingress, edge router, or application gateway, is a service that is accessible to the Internet, and routes traffic to services running inside a Kubernetes environment. Traditionally, this service was managed by a Kubernetes object also called an `Ingress`, and as such “ingress” in a Kubernetes context normally refers to an operator configuration where a control plane configures a hardware or software proxy server. The traffic can include API traffic, but can also include general traffic like web pages and images.

Examples of Kubernetes ingresses include ingress-nginx and Contour.

Kgateway includes full Kubernetes ingress functionality, providing its own control plane, using the [{{< reuse "docs/snippets/k8s-gateway-api-name.md" >}}](#what-is-the-kubernetes-gateway-api) as its configuration language and Envoy as its proxy server.

### What are the components of an ingress?

There are three major components that make up any ingress solution:

* control plane  
* data plane  
* configuration language

The [{{< reuse "docs/snippets/k8s-gateway-api-name.md" >}}](#what-is-the-kubernetes-gateway-api) is a project designed to standardize the configuration language, replacing the legacy `Ingress` API with an extensible API.

Ingress projects therefore differentiate on their data plane — there are solutions built on top of Envoy, HAProxy, NGINX, Traefik and more — and the performance, scalability and features of their control plane.

<!-- There are multiple ingress projects based on Envoy alone. [Learn how kgateway differs from the others](#TODO). -->

### What is an API?

An application programming interface (API) is a method to allow a machine to talk to a machine. Contrast APIs with user interfaces (UIs), which allow a human to talk to a machine.

Today, an API most commonly refers to a web API, a method using HTTP (or a derivative like gRPC) to provide access to machine readable data in a format like JSON or XML. Web APIs are sometimes referred to as web services, which is where Amazon Web Services (AWS) gets its name.

As an example, take a look at the API for NASA's popular [Astronomy Picture of the Day](https://apod.nasa.gov/apod/astropix.html) service. The most common way that humans access this service is through the UI that is the NASA website. However, if you want a machine to use this service, you can also use the API.

To start, you [generate an API key](https://api.nasa.gov/) that gives access to the API. Then, you set up your program to perform an HTTP GET request to the API endpoint: `https://api.nasa.gov/planetary/apod?api_key=$YOUR_API_KEY`. 

As with most APIs, the Astronomy Picture of the Day API also includes parameters that you can use in the request to get back more specific responses, such as the date. Typically, parameters have default values if you don't include them, such as today's date. To find out the available parameters and more, you use the [API documentation](https://github.com/nasa/apod-api?tab=readme-ov-file#docs-).

### What is an API gateway?

An API gateway is a service that provides centralized gateway functionality for API traffic. The concept that took off as microservices architectures were growing in popularity in the 2005-2015 era, with early vendors such as 3scale, WSO2 and Apigee targeting backends that were run on Java. As Kubernetes became popular, the need arose to offer API gateway functionality that integrated with it. This led to the launch of Gloo, which is the original name of kgateway.

In the NASA example, recall that you had to provide an API key to access the service. This is a way of identifying you to the API, which can then be used to enable decision-making.

Some functions an API gateway might perform include:

* **Routing and aggregation**: Similar to an ingress, make APIs from different backend services (including serverless functions) available at a single endpoint, behind a single API key.
* **Load balancing**: Send requests to backend services, based on their load.
* **Rate limiting:** Limit the number of users that can call certain APIs, based on parameters such as identity, load, or cost.
* **Security**: Provide authentication and authorization, and Web Application Firewall functionality.
* **Logging and monitoring**: Track and display usage in order to provide visibility into the system to help with use cases such as API management, debugging, and accurate billing data.

### Are ingresses API gateways?

Although a necessary component, ingress functionality by itself is not sufficient for a project to be considered an API gateway.

Traditionally an ingress primarily handles routing and aggregation, with Kubernetes providing load balancing. If you hear the phrase “application gateway,” it’s probably acting as a gateway for the website UI. Although APIs are web traffic and are often published through an ingress, you don’t have the full range of features in a UI-focused application gateway as you would in an API gateway.

### What is the Kubernetes Gateway API?

The {{< reuse "docs/snippets/k8s-gateway-api-name.md" >}} is a common, extensible standard for traffic management in Kubernetes. It has quickly becoming the standard interface for defining routing and policy for cloud native networking, addressing many shortcomings of its predecessor, the Ingress API, and unifying best practices that have evolved through real-world usage.

[Learn about the history of the Gateway API](/blog/introduction-to-kubernetes-gateway-api/), or [watch our in-depth video series](/resources/videos/).

Kgateway is fully conformant with the {{< reuse "docs/snippets/k8s-gateway-api-name.md" >}} and extends its functionality with custom extension APIs, such as TrafficPolicies, ListenerPolicies, and Backends. These custom resources help to centrally configure advanced traffic management, security, and resiliency rules for an HTTPRoute or Gateway listener.

### Is the Gateway API an API gateway?

No, but this demonstrates why [naming things](https://www.karlton.org/2017/12/naming-things-hard/) is hard!

The Gateway API is an API which can be used to program an ingress or an API gateway.

## Extensions

{{< reuse "/docs/snippets/kgateway-capital.md" >}} provides the following extensions on top of the {{< reuse "docs/snippets/k8s-gateway-api-name.md" >}} to configure advanced routing, security, and resiliency capabilities.

{{< cards >}}
  {{< card link="../../security/access-logging/" title="Access logging" tag="Security" >}}
  {{< card link="../../integrations/aws-elb/" title="AWS ALB and NLB" tag="Traffic" >}}
  {{< card link="../../traffic-management/destination-types/backends/lambda" title="AWS Lambda" tag="Traffic" >}}
  {{< card link="../../traffic-management/route-delegation/" title="Delegation" tag="Traffic" >}}
  {{< card link="../../traffic-management/direct-response/" title="Direct responses" tag="Traffic" >}}
  {{< card link="../../setup/customize/" title="Gateway customization" tag="Setup" >}}
  {{< card link="../../integrations/" title="Integrations" tag="Setup" >}}
  {{< card link="../../resiliency/mirroring/" title="Mirroring" tag="Resiliency" >}}
  {{< card link="../../traffic-management/transformations/" title="Transformations" tag="Traffic" >}}
  {{< card link="../../traffic-management/weighted-routes/" title="Weighted routing" tag="Traffic" >}}
{{< /cards >}}

## Default gateway proxy setup

{{< reuse "/docs/snippets/kgateway-capital.md" >}} automatically spins up, bootstraps, and manages gateway proxy deployments when you create a Kubernetes Gateway resource. To do that, a combination of kgateway and Kubernetes resources are used, such as GatewayClass, GatewayParameters, and a gateway proxy template that includes the Envoy configuration that each proxy is bootstrapped with. 

To learn more about the default setup and how these resources interact with each other, see the [Default gateway proxy setup](/docs/setup/default/).
