---
title: Local rate limiting
weight: 10
next: /docs/security/local/http
---

Local rate limiting is a coarse-grained rate limiting capability that is primarily used as a first line of defense mechanism to limit the number of requests that are forwarded to your rate limit servers. 

Without local rate limiting, all requests are directly forwarded to a rate limit server where the request is either denied or allowed based on the global rate limiting settings that you configured. However, during an attack, too many requests might be forwarded to your rate limit servers and can cause overload or even failure.

To protect your rate limit servers from being overloaded and to optimize their resource utilization, you can set up local rate limiting in conjunction with global rate limiting. Because local rate limiting is enforced in each Envoy instance that makes up your gateway, no rate limit server is required in this setup. For example, if you have 5 Envoy instances that together represent your gateway, each instance is configured with the limit that you set. In a global rate limiting setup, this limit is shared across all Envoy instances. 

For more information about local rate limiting, see the [Envoy documentation](https://www.envoyproxy.io/docs/envoy/latest/configuration/http/http_filters/local_rate_limit_filter). 

## Architecture

The following image shows how local rate limiting works in {{< reuse "docs/snippets/product-name.md" >}}. As clients send requests to a backend destination, they first reach the Envoy instance that represents your gateway. Local rate limiting settings are applied to an Envoy pod or process. Note that limits are applied to each pod or process. For example, if you have 5 Envoy instances that are configured with a local rate limit of 10 requests per second, the total number of allowed requests per second is 50 (5*10). In a global rate limiting setup, this limit is shared between all Envoy instances, so the total number of allowed requests per second is 10. 

Depending on your setup, each Envoy instance or pod is configured with a number of tokens in a token bucket. To allow a request, a token must be available in the bucket so that it can be assigned to a downstream connection. Token buckets are refilled occasionally as defined in the refill setting of the local rate limiting configuration. If no token is available, the connection is closed immediately, and a 429 HTTP response code is returned to the client. 

When a token is available in the token bucket it can be assigned to an incoming connection. The request is then forwarded to your rate limit server to enforce any global rate limiting settings. For example, the request might be further rate limited based on headers or query parameters. Only requests that are within the local and global rate limits are forwarded to the backend destination in the cluster. 

{{< reuse-image src="/img/local-rate-limiting.svg" caption="Local rate limiting" width="600px" >}}

