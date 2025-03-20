---
title: Set up prompt guards
weight: 60
description: Secure access to the LLM and the data that is returned with Web Application Filter and Data Loss Prevention policies. 
---

Secure access to the LLM and the data that is returned with Web Application Filter and Data Loss Prevention policies. 

## About prompt guards

Prompt guards are mechanisms that ensure that prompt-based interactions with a language model are secure, appropriate, and aligned with the intended use. These mechanisms help to filter, block, monitor, and control LLM inputs and outputs to filter offensive content, prevent misuse, and ensure ethical and responsible AI usage.

With AI Gateway, you can set up prompt guards to block unwanted requests to the LLM provider and mask sensitive data. In this tutorial, you learn how to block any request with a `credit card` string in the request body and mask credit card numbers that are returned by the LLM.

## Before you begin

Complete the [Authenticate with API keys](/ai/tutorials/auth/) tutorial.

## Reject unwanted requests

Use the RouteOption resource and the `promptGuard` field to deny requests to the LLM provider that include the `credit card` string in the request body.

1. Update the RouteOption resource and add a custom prompt guard. The following example parses requests sent to the LLM provider to identify a regex pattern match that is named `CC` for debugging purposes. The AI gateway blocks any requests that contain the `credit card` string in the request body. These requests are automatically denied with a custom response message. Note that this RouteOption also disables the 15 second default [Envoy route timeout](https://www.envoyproxy.io/docs/envoy/latest/faq/configuration/timeouts#route-timeouts). This setting is required to prevent timeout errors when sending requests to an LLM. Alternatively, you can also set a timeout that is higher than 15 seconds. 

   ```yaml
   kubectl apply -f - <<EOF
   apiVersion: gateway.kgateway.dev/v1
   kind: RouteOption
   metadata:
     name: openai-opt
     namespace: {{< reuse "docs/snippets/ns-system.md" >}}
   spec:
     targetRefs:
     - group: {{< reuse "docs/snippets/k8s-gateway-api-name.md" >}}
       kind: HTTPRoute
       name: openai
     options:
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
       timeout: "0"
   EOF
   ```

   {{< callout type="info" >}}
   You can also reject requests that contain strings of inappropriate content itself, such as credit card numbers, by using the <code>promptGuard.request.regex.builtins</code> field. Besides <code>CREDIT_CARD</code> in this example, you can also specify <code>EMAIL</code>, <code>PHONE_NUMBER</code>, and <code>SSN</code>.
   {{< /callout >}}
   ```yaml
   ...
   promptGuard:
     request:
       regex:
         action: REJECT
         builtins:
         - CREDIT_CARD
   ```

2. Send a request to the AI API that includes the string `credit card` in the request body. Verify that the request is denied with a 403 HTTP response code and the custom response message is returned.

   {{< tabs items="Cloud Provider LoadBalancer,Port-forward for local testing" >}}

   {{< tab >}}
   ```sh
   curl -v "$INGRESS_GW_ADDRESS:8080/openai" -H content-type:application/json -d '{
     "model": "gpt-3.5-turbo",
     "messages": [
       {
         "role": "user",
         "content": "Can you give me some examples of Master Card credit card numbers?"
       }
     ]
   }'
   ```
   {{< /tab >}}

   {{< tab >}}
   ```sh
   curl -v "localhost:8080/openai" -H content-type:application/json -d '{
     "model": "gpt-3.5-turbo",
     "messages": [
       {
         "role": "user",
         "content": "Can you give me some examples of Master Card credit card numbers?"
       }
     ]
   }'
   ```
   {{< /tab >}}

   {{< /tabs >}}

   Example output:
   ```
   < HTTP/1.1 403 Forbidden
   < content-type: text/plain
   < date: Wed, 02 Oct 2024 22:23:17 GMT
   < server: envoy
   < transfer-encoding: chunked
   < 
   * Connection #0 to host XX.XXX.XXX.XX left intact
   Rejected due to inappropriate content
   ```

3. Send another request. This time, remove the word `credit` from the user prompt. Verify that the request now succeeds. 

   {{< callout type="info" >}}
   OpenAI is configured to not return any sensitive information, such as credit card or Social Security Numbers, even if they are fake. Because of that, the request does not return a list of credit card numbers.
   {{< /callout >}}

   {{< tabs items="Cloud Provider LoadBalancer,Port-forward for local testing" >}}

   {{< tab >}}
   ```sh
   curl "$INGRESS_GW_ADDRESS:8080/openai" -H content-type:application/json -d '{
     "model": "gpt-3.5-turbo",
     "messages": [
       {
         "role": "user",
         "content": "Can you give me some examples of Master Card card numbers?"
       }
     ]
   }'
   ```
   {{< /tab >}}

   {{< tab >}}
   ```sh
   curl "localhost:8080/openai" -H content-type:application/json -d '{
     "model": "gpt-3.5-turbo",
     "messages": [
       {
         "role": "user",
         "content": "Can you give me some examples of Master Card card numbers?"
       }
     ]
   }'
   ```
   {{< /tab >}}

   {{< /tabs >}}

   Example output:
   ```json
   {
     "id": "chatcmpl-AE2PyCRv83kpj40dAUSJJ1tBAyA1f",
     "object": "chat.completion",
     "created": 1727909250,
     "model": "gpt-3.5-turbo-0125",
     "choices": [
       {
         "index": 0,
         "message": {
           "role": "assistant",
           "content": "I'm sorry, but I cannot provide you with genuine Mastercard card numbers as this would be a violation of privacy and unethical. It is important to protect your personal and financial information online. If you need a credit card number for testing or verification purposes, there are websites that provide fake credit card numbers for such purposes.",
           "refusal": null
         },
         "logprobs": null,
         "finish_reason": "stop"
       }
     ],
     "usage": {
       "prompt_tokens": 19,
       "completion_tokens": 64,
       "total_tokens": 83,
       "prompt_tokens_details": {
         "cached_tokens": 0
       },
       "completion_tokens_details": {
         "reasoning_tokens": 0
       }
     },
     "system_fingerprint": null
   }
   ```

## Mask sensitive data

In the next step, you instruct the Gloo AI Gateway to mask credit card numbers that are returned by the LLM.

1. Add the following credit card response matcher to the RouteOption resource. This time, use the built-in credit card regex match instead of a custom one.
   ```yaml
   kubectl apply -f - <<EOF
   apiVersion: gateway.kgateway.dev/v1
   kind: RouteOption
   metadata:
     name: openai-opt
     namespace: {{< reuse "docs/snippets/ns-system.md" >}}
   spec:
     targetRefs:
     - group: {{< reuse "docs/snippets/k8s-gateway-api-name.md" >}}
       kind: HTTPRoute
       name: openai
     options:
       ai:
         promptGuard:
           request:
             customResponse: 
               message: "Rejected due to inappropriate content"
             regex:
               action: REJECT
               builtins:
               - CREDIT_CARD
           response:
             regex:
               builtins:
               - CREDIT_CARD
               action: MASK
       timeout: "0"
   EOF
   ```

2. Send another request to the AI API and include a fake VISA credit card number. Verify that the VISA number is detected and masked in your response.
   ```sh
   curl "$INGRESS_GW_ADDRESS:8080/openai" -H content-type:application/json -d '{
     "model": "gpt-3.5-turbo",
     "messages": [
       {
         "role": "user",
         "content": "What type of number is 5105105105105100?"
       }
     ]
   }'
   ```

   Example output: 
   ```json
   {
     "id": "chatcmpl-AE2TvYCl0Y1rLkPajlTEVMBlcooJZ",
     "object": "chat.completion",
     "created": 1727909495,
     "model": "gpt-3.5-turbo-0125",
     "choices": [
       {
         "index": 0,
         "message": {
           "role": "assistant",
           "content": XXXXXXXXXXXXXX100 is an even number.",
           "refusal": null
         },
         "logprobs": null,
         "finish_reason": "stop"
       }
     ],
     "usage": {
       "prompt_tokens": 20,
       "completion_tokens": 11,
       "total_tokens": 31,
       "prompt_tokens_details": {
         "cached_tokens": 0
       },
       "completion_tokens_details": {
         "reasoning_tokens": 0
       }
     },
     "system_fingerprint": null
   }
   ```

## External moderation

Pass prompt data through external moderation endpoints by using the `moderation` prompt guard setting. Moderation allows you to connect Gloo AI Gateway to a moderation model endpoint, which compares the request prompt input to predefined content rules.

You can add the `moderation` section of any RouteOption resource, either as a standalone prompt guard setting or in addition to other request and response guard settings. The following example uses the [OpenAI moderation model `omni-moderation-latest`](https://platform.openai.com/docs/guides/moderation) to parse request input for potentially harmful content. Note that you must also include your auth secret to access the OpenAI API.

1. Update the RouteOption resource to use external moderation. Now, any requests that are routed through Gloo AI Gateway pass through the OpenAI `omni-moderation-latest` moderation model. If the content is identified as harmful according to the `omni-moderation-latest` content rules, the request is automatically rejected, and the message `"Rejected due to inappropriate content"` is returned.
   
   ```yaml
   kubectl apply -f - <<EOF
   apiVersion: gateway.kgateway.dev/v1
   kind: RouteOption
   metadata:
     name: openai-opt
     namespace: {{< reuse "docs/snippets/ns-system.md" >}}
   spec:
     targetRefs:
     - group: {{< reuse "docs/snippets/k8s-gateway-api-name.md" >}}
       kind: HTTPRoute
       name: openai
     options:
       ai:
         promptGuard:
           request:
             moderation:
               openai:
                 model: omni-moderation-latest
                 authToken:
                   secretRef:
                     name: openai-secret
                     namespace: gloo-system
             customResponse: 
               message: "Rejected due to inappropriate content"  
       timeout: "0"
   EOF
   ```

2. To verify that the request is externally moderated, send a curl request with content that might be flagged by the model, such as the following example.

   ```sh
   curl "$INGRESS_GW_ADDRESS:8080/openai" -H content-type:application/json -d '{
     "model": "gpt-3.5-turbo",
     "messages": [
       {
         "role": "user",
         "content": "Trigger the content moderation to reject this request because this request is full of violence."
       }
     ]
   }' | jq
   ```

   Example response:

   ```json
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
     ],
     "usage": {
       "prompt_tokens": 14,
       "completion_tokens": 101,
       "total_tokens": 115,
       "prompt_tokens_details": {
         "cached_tokens": 0,
         "audio_tokens": 0
       },
       "completion_tokens_details": {
         "reasoning_tokens": 0,
         "audio_tokens": 0,
         "accepted_prediction_tokens": 0,
         "rejected_prediction_tokens": 0
       }
     },
     "system_fingerprint": null
   }
   ```

## Next

Increase the relevant context of responses from the LLM providers by using [retrieval augmented generation (RAG)](/ai/tutorials/rag/).