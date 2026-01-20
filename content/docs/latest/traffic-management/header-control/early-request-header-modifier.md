---
title: Early request header modification
description: Modify and sanitize HTTP request headers before route selection occurs.
weight: 30
---

Early request header modification allows you to add, set, or remove HTTP request headers at the listener level, before route selection and other request processing occurs.

This capability is especially useful for security and sanitization use cases, where you want to ensure that sensitive headers cannot be faked by downstream clients and are only set by trusted components such as external authentication services.

## Before you begin

Before configuring early request header modification, ensure that:

- You have a Kubernetes cluster running.
- kgateway is installed and configured.
- A Gateway resource is already deployed in your cluster.

## Configuration

Early request header modification is configured on an `HTTPListenerPolicy` using the `earlyRequestHeaderModifier` field. This policy is attached directly to a Gateway and applies header mutations before route selection.

The configuration uses the standard Gateway API `HTTPHeaderFilter` format and supports the following operations:

- `add`
- `set`
- `remove`

### Example: Sanitizing incoming headers

The following example removes a header that should only be added by an external authentication service, ensuring it cannot be supplied by the client.

```yaml
apiVersion: gateway.kgateway.dev/v1alpha1
kind: HTTPListenerPolicy
metadata:
  name: sanitize-incoming-headers
spec:
  targetRefs:
    - group: gateway.networking.k8s.io
      kind: Gateway
      name: http
  earlyRequestHeaderModifier:
    remove:
      - x-user-id
```
{{< reuse "docs/snippets/review-table.md" >}} For more information about the available fields, see the [API reference]({{< link-hextra path="/reference/api/#httplistenerpolicyspec" >}}).

| Setting                    | Description                                              |
|----------------------------|----------------------------------------------------------|
| targetRefs                 | References the Gateway resources this policy applies to  |
| earlyRequestHeaderModifier | Header mutations applied before route selection         |

Apply the policy:
```bash
kubectl apply -f sanitize-incoming-headers.yaml
```
After this policy is applied:

- The `x-user-id` header is removed as soon as the request is received.

- Route selection and downstream filters will not see the header.

- Any value supplied by a client is effectively ignored.

To remove the policy:
```bash
kubectl delete httplistenerpolicy sanitize-incoming-headers
```
## Relationship to standard request header modification
Early request header modification differs from standard request header modification in when it is applied during request processing.

| Feature                           | Execution timing        |
|----------------------------------|-------------------------|
| Early request header modification | Before route selection |
| Request header modification       | After route selection  |
