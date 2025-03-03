---
title: VirtualHostOptions
weight: 5
description: 
---



**Package**: `gloo.solo.io` 

**Types:** 

- [VirtualHostOptions](#virtualhostoptions)




**Source File:**
[github.com/solo-io/gloo/projects/gloo/api/v1/virtual_host_options.proto](https://github.com/solo-io/gloo/blob/main/projects/gloo/api/v1/virtual_host_options.proto)





---
### VirtualHostOptions


Optional, feature-specific configuration that lives on virtual hosts.
Each VirtualHostOptions object contains configuration for a specific feature.
Note to developers: new Virtual Host plugins must be added to this struct
to be usable by {{< reuse "docs/snippets/product-name.md" >}}. 

```yaml
"extensions": .gloo.solo.io.Extensions
"retries": .retries.options.gloo.solo.io.RetryPolicy
"stats": .stats.options.gloo.solo.io.Stats
"headerManipulation": .headers.options.gloo.solo.io.HeaderManipulation
"cors": .cors.options.gloo.solo.io.CorsPolicy
"bufferPerRoute": .solo.io.envoy.extensions.filters.http.buffer.v3.BufferPerRoute
"csrf": .solo.io.envoy.extensions.filters.http.csrf.v3.CsrfPolicy
"includeRequestAttemptCount": .google.protobuf.BoolValue
"includeAttemptCountInResponse": .google.protobuf.BoolValue
"stagedTransformations": .transformation.options.gloo.solo.io.TransformationStages
"corsPolicyMergeSettings": .cors.options.gloo.solo.io.CorsPolicyMergeSettings

```
| Field | Type | Description |
| ----- | ---- | ----------- | 
| `extensions` | [.gloo.solo.io.Extensions](../../components/extensions.proto.sk/#extensions) | Extensions will be passed along from Listeners, Gateways, VirtualServices, Routes, and Route tables to the underlying Proxy, making them useful for controllers, validation tools, etc. which interact with kubernetes yaml. Some sample use cases: * controllers, deployment pipelines, helm charts, etc. which wish to use extensions as a kind of opaque metadata.  |
| `retries` | [.retries.options.gloo.solo.io.RetryPolicy](../../components/retries.proto.sk/#retrypolicy) |  |
| `stats` | [.stats.options.gloo.solo.io.Stats](../../components/stats.proto.sk/#stats) |  |
| `headerManipulation` | [.headers.options.gloo.solo.io.HeaderManipulation](../../components/headers.proto.sk/#headermanipulation) | Append/Remove headers on Requests or Responses on all routes contained in this Virtual Host. |
| `cors` | [.cors.options.gloo.solo.io.CorsPolicy](../../components/cors.proto.sk/#corspolicy) | Defines a CORS policy for the virtual host. If a CORS policy is also defined on the route matched by the request, the route policy overrides the virtual host policy for any configured field unless CorsPolicyMergeSettings are specified that define an alternate behavior. |
| `transformations` | [.transformation.options.gloo.solo.io.Transformations](../../components/transformation.proto.sk/#transformations) | Transformations to apply. Note: this field is superseded by `staged_transformations`. If `staged_transformations.regular` is set, this field will be ignored. |
| `bufferPerRoute` | [.solo.io.envoy.extensions.filters.http.buffer.v3.BufferPerRoute](../../components/buffer.proto.sk/#bufferperroute) | BufferPerRoute can be used to set the maximum request size that the filter will buffer before the connection manager will stop buffering and return a 413 response. Note: If you have not set a global config (at the gateway level), this override will not do anything by itself. |
| `csrf` | [.solo.io.envoy.extensions.filters.http.csrf.v3.CsrfPolicy](../../components/csrf.proto.sk/#csrfpolicy) | Csrf can be used to set percent of requests for which the CSRF filter is enabled, enable shadow-only mode where policies will be evaluated and tracked, but not enforced and add additional source origins that will be allowed in addition to the destination origin. For more, see https://www.envoyproxy.io/docs/envoy/latest/api-v3/extensions/filters/http/csrf/v3/csrf.proto#envoy-v3-api-msg-extensions-filters-http-csrf-v3-csrfpolicy. |
| `includeRequestAttemptCount` | [.google.protobuf.BoolValue](https://developers.google.com/protocol-buffers/docs/reference/csharp/class/google/protobuf/well-known-types/bool-value) | IncludeRequestAttemptCount decides whether the x-envoy-attempt-count header should be included in the backend request. Setting this option will cause it to override any existing header value, so in the case of two Envoys on the request path with this option enabled, the backend will see the attempt count as perceived by the second Envoy. Defaults to false. |
| `includeAttemptCountInResponse` | [.google.protobuf.BoolValue](https://developers.google.com/protocol-buffers/docs/reference/csharp/class/google/protobuf/well-known-types/bool-value) | IncludeAttemptCountInResponse decides whether the x-envoy-attempt-count header should be included in the downstream response. Setting this option will cause the router to override any existing header value, so in the case of two Envoys on the request path with this option enabled, the downstream will see the attempt count as perceived by the Envoy closest backend from itself. Defaults to false. |
| `stagedTransformations` | [.transformation.options.gloo.solo.io.TransformationStages](../../components/transformation.proto.sk/#transformationstages) | Early transformations stage. These transformations run before most other options are processed. If the `regular` field is set in here, the `transformations` field is ignored. |
| `corsPolicyMergeSettings` | [.cors.options.gloo.solo.io.CorsPolicyMergeSettings](../../components/cors.proto.sk/#corspolicymergesettings) | Settings for determining merge strategy for CORS settings when present at both Route and VirtualHost levels. |



<!-- Start of HubSpot Embed Code -->
<script type="text/javascript" id="hs-script-loader" async defer src="//js.hs-scripts.com/5130874.js"></script>
<!-- End of HubSpot Embed Code -->