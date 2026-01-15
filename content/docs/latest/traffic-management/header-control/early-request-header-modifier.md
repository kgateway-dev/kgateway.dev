---
title: Early request header modification
description: Modify and sanitize HTTP request headers before route selection occurs.
weight: 30
---

Early request header modification allows you to **add, set, or remove HTTP request headers at the listener level, before route selection and other request processing occurs**.

This capability is especially useful for **security and sanitization use cases**, where you want to ensure that sensitive headers cannot be faked by downstream clients and are only set by trusted components such as external authentication services.

## When to use early request header modification

Use `earlyRequestHeaderModifier` when you need to:

- Sanitize incoming request headers **before routing decisions are made**
- Remove headers that should only be added by trusted systems
- Enforce security boundaries when handling untrusted downstream traffic
- Apply header mutations earlier than standard request header modifiers

Unlike standard request header modification, early header modification runs **before route matching**, ensuring headers do not influence routing or policy decisions.

## Configuration overview

Early request header modification is configured on an `HTTPListenerPolicy` using the `earlyRequestHeaderModifier` field.

The configuration uses the standard Gateway API `HTTPHeaderFilter` format and supports the following operations:

- `add`
- `set`
- `remove`

## Example: Sanitizing incoming headers

The following example removes a header that should only be added by an external authentication service, ensuring it cannot be supplied by the client.

```yaml
apiVersion: gateway.kgateway.dev/v1alpha1
kind: HTTPListenerPolicy
metadata:
  name: sanitize-incoming-headers
spec:
  earlyRequestHeaderModifier:
    remove:
      - x-user-id
```
In this example:

- The `x-user-id` header is removed as soon as the request is received

- Route selection and downstream filters will not see the header

- Any value supplied by a client is effectively ignored

## Relationship to standard request header modification

| Feature                          | Execution timing        |
|----------------------------------|------------------------|
| Early request header modification | Before route selection |
| Request header modification       | After route selection  |

If your use case depends on preventing headers from affecting routing or policy evaluation, early request header modification is the correct choice.

## API reference

The `earlyRequestHeaderModifier` field is part of the [HTTPListenerPolicy API](../../../reference/api/#httplistenerpolicyspec). Refer to the API documentation for full field definitions and schema details.
