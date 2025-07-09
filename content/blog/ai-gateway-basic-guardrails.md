---
title: Dive into Basic Prompt Guardrails with kgateway 
toc: false
publishDate: 2025-05-01T00:00:00-00:00
author: Alex Ly
excludeSearch: true
---

Earlier this year, Solo.io's Field CTO, Christian Posta, posted this article [Navigating DeepSeek R1, Security Concerns, and Guardrails](https://kgateway.dev/blog/navigating-deepseek-r1/) which provided the following diagram that depicts how an AI Gateway can play a part in a "defense in depth" strategy.

By implementing this intermediary layer outside of the application code, platform owners gain a new layer to enforce security and policy, act as an enforcement point for all traffic flow, and most importantly act as a "kill switch" to protect the system should a critical vulnerability be discovered (rather than ask all application teams to update their code, yuck!)

{{< reuse-image src="blog/ai-gateway-basic-guardrails-1.png" width="750px" >}}

Today, open-source users of kgateway v2.0.0 can easily configure simple guardrails for chat requests destined for a backend LLM. Kgateway can also be configured to pass prompt data through external moderation endpoints such as OpenAI's **omni-moderation-latest** models. In this blog post we will walk through the configuration of both scenarios to learn more about prompt guarding features available for our users.

## Basic Prompt Guarding

Built into kgatewayAI are several prompt guard options: **string, regex, and built-in** values that can be configured using a **TrafficPolicy** configured for prompt guard. Here is a diagram of what an example request flow would look like

{{< reuse-image src="blog/ai-gateway-basic-guardrails-2.png" width="750px" >}}

**String** allows the user to configure behavior to mask or reject requests that contain the literal string defined in the prompt guard. Here is a simple example that rejects any request with the specific string "credit card"

```yaml
apiVersion: gateway.kgateway.dev/v1alpha1
kind: TrafficPolicy
metadata:
  name: openai-prompt-guard
  namespace: kgateway-system
  labels:
    app: ai-kgateway
spec:
  targetRefs:
  - group: gateway.networking.k8s.io
    kind: HTTPRoute
    name: openai
  ai:
    promptGuard:
      request:
        customResponse:
          message: "Rejected due to inappropriate content"
        regex:
          action: REJECT
          matches:
          - pattern: "credit card"
            name: "CC"
```

If you try to send a request asking for customer credit card information, you will be met with a 403 error code and the custom response defined in the prompt guard configuration

```yaml
< HTTP/1.1 403 Forbidden
< content-type: text/plain
< date: Wed, 02 Oct 2024 22:23:17 GMT
< server: envoy
< transfer-encoding: chunked
<
* Connection #0 to host XX.XXX.XXX.XX left intact
Rejected due to inappropriate content
```

**Regex** improves granularity with pattern matching. Adding to the previous example, below we will add a prompt guard for the response this time which will **MASK** any responses that match a regex that is a known pattern for credit card numbers from Mastercard

```yaml
apiVersion: gateway.kgateway.dev/v1alpha1
kind: TrafficPolicy
metadata:
  name: openai-prompt-guard
  namespace: kgateway-system
  labels:
    app: ai-kgateway
spec:
  targetRefs:
  - group: gateway.networking.k8s.io
    kind: HTTPRoute
    name: openai
  ai:
    promptGuard:
      request:
        customResponse:
          message: "Rejected due to inappropriate content"
        regex:
          action: REJECT
          matches:
          - pattern: "credit card"
            name: "CC"
      response:
        regex:
          matches:
          # Mastercard
          - pattern: '(?:^|\D)(5[1-5][0-9]{2}(?:\ |\-|)[0-9]{4}(?:\ |\-|)[0-9]{4}(?:\ |\-|)[0-9]{4})(?:\D|$)'
            action: MASK
```

This time, if we attempted to ask for a list of Mastercard numbers, you would be met with a similar response to below

```yaml
{
  "id": "chatcmpl-BFSv1H8b9Y32mzjzlG1KQRfzkAE6n",
  "object": "chat.completion",
  "created": 1743025783,
  "model": "gpt-3.5-turbo-0125",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "Sure, here is an example of a Mastercard number. This is not valid for actual use, but follows the correct format and prefix range for Mastercard numbers.\n\n1. **<CUSTOM>**\n",
        "refusal": null,
        "annotations": []
      },
      "logprobs": null,
      "finish_reason": "stop"
    }
  ...
```

**Builtin** supports a few native patterns such as **CREDIT_CARD**, **EMAIL, PHONE_NUMBER,** and **SSN** that can be easily configured by the user. Instead of having to define every regex pattern for each credit card provider, we can use the builtin:

```yaml
apiVersion: gateway.kgateway.dev/v1alpha1
kind: TrafficPolicy
metadata:
  name: openai-prompt-guard
  namespace: kgateway-system
  labels:
    app: ai-kgateway
spec:
  targetRefs:
  - group: gateway.networking.k8s.io
    kind: HTTPRoute
    name: openai
  ai:
    promptGuard:
      response:
        regex:
          action: MASK
          builtins:
          - CREDIT_CARD
```

## External Moderation Endpoint

Moderation allows for the use of external moderation model endpoints, which compare the request prompt input to predefined content rules. This allows us to parse the request input for potentially harmful content and reject it with a custom response to the user if deemed malicious. Here is a diagram of what an example request flow would look like

{{< reuse-image src="blog/ai-gateway-basic-guardrails-3.png" width="750px" >}}

A simple example of this would be to use the **omni-moderation-latest** model endpoint from OpenAI. Here is what the `TrafficPolicy` would look like

```yaml
apiVersion: gateway.kgateway.dev/v1alpha1
kind: TrafficPolicy
metadata:
  name: openai-prompt-guard
  namespace: kgateway-system
  labels:
    app: ai-kgateway
spec:
  targetRefs:
  - group: gateway.networking.k8s.io
    kind: HTTPRoute
    name: openai
  ai:
    promptGuard:
      request:
        moderation:
          openAIModeration:
            model: omni-moderation-latest
            authToken:
              kind: SecretRef
              secretRef:
                name: openai-secret
```

Now, when a user sends a request that is rejected by the moderation endpoint, we should see a canned response back from the moderation model.

```yaml
{
  "id": "chatcmpl-ASnJRpzmWPR4MonNETccEqB6qAZCO",
  "object": "chat.completion",
  "created": 1731426105,
  "model": "gpt-3.5-turbo-0125",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "I'm sorry, I cannot fulfill your request as it goes against ethical guidelines and promotes violence. If you have any other inquiries or requests, please feel free to ask. Thank you for your understanding.",
        "refusal": null
      },
      "logprobs": null,
      "finish_reason": "stop"
    }
  ]
}
```

## Conclusion

Today we covered another example of how kgateway serves as one of the most mature and widely deployed Envoy-based gateway, now serving AI workloads and their unique requirements.

Why not try this feature out in kgateway with a free a hands-on technical lab on [prompt guards in kgateway](https://www.solo.io/resources/lab/kgateway-ai-lab-prompt-guards).
