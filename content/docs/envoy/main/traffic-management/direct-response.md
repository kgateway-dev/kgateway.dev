---
title: Direct responses
weight: 20
prev: /docs/traffic-management/destination-types
next: /docs/traffic-management/match
---

{{< reuse "docs/pages/traffic-management/direct-response.md" >}}

## Other configurations

Review other common direct response configurations.

### Dynamic text body {#dynamic-text-body}

Use the `bodyFormat.text` field to return a dynamic response body by using [Envoy format strings](https://www.envoyproxy.io/docs/envoy/latest/api-v3/config/core/v3/substitution_format_string.proto#envoy-v3-api-field-config-core-v3-substitutionformatstring-text-format). Format strings use `%VARIABLE%` placeholders that [Envoy substitutes](https://www.envoyproxy.io/docs/envoy/latest/configuration/observability/access_log/usage#format-strings) at request time, such as request headers or dynamic metadata.

In this example, you use the `%REQ(:path)%` expression to inject the request path into the direct response. This setting is mutually exclusive with `spec.bodyFormat.json` and `spec.body`. 

```yaml
kubectl apply -f- <<EOF
apiVersion: gateway.kgateway.dev/v1alpha1
kind: DirectResponse
metadata:
  name: robots-txt
  namespace: httpbin
spec:
  status: 200
  bodyFormat:
    text: |
      User-agent: *
      Disallow: %REQ(:path)%
EOF
```

### Dynamic JSON body {#dynamic-json-body}

Use the `bodyFormat.json` field to return a JSON response body for [Envoy format strings](https://www.envoyproxy.io/docs/envoy/latest/api-v3/config/core/v3/substitution_format_string.proto#envoy-v3-api-field-config-core-v3-substitutionformatstring-json-format). Envoy substitutes the format string values at request time and returns the result as a JSON object with a default `Content-Type` of `application/json`.

The following example returns the request path as a JSON body. This setting is mutually exclusive with `spec.bodyFormat.text` and `spec.body`. 

```yaml
kubectl apply --server-side -f- <<EOF
apiVersion: gateway.kgateway.dev/v1alpha1
kind: DirectResponse
metadata:
  name: data-json
  namespace: httpbin
spec:
  status: 200
  bodyFormat:
    json:
      path: "%REQ(:path)%"
EOF
```


