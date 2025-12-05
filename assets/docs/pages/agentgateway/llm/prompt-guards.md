Secure access to the LLM and the data that is returned with Web Application Filter and Data Loss Prevention policies. 

## About prompt guards {#about}

Prompt guards are mechanisms that ensure that prompt-based interactions with a language model are secure, appropriate, and aligned with the intended use. These mechanisms help to filter, block, monitor, and control LLM inputs and outputs to filter offensive content, prevent misuse, and ensure ethical and responsible AI usage.

You can set up prompt guards to block unwanted requests to the LLM provider and mask sensitive data. In this tutorial, you learn how to block any request with a `credit card` string in the request body and mask credit card numbers that are returned by the LLM.

{{% version include-if="2.2.x" %}}
Prompt guards can be configured directly in an {{< reuse "docs/snippets/backend.md" >}} resource or in a separate AgentgatewayPolicy resource. 
{{% /version %}}

## Before you begin

{{< reuse "docs/snippets/agw-prereq-llm.md" >}}

## Reject unwanted requests

Use the {{< reuse "docs/snippets/trafficpolicy.md" >}} resource and the `promptGuard` field to deny requests to the LLM provider that include the `credit card` string in the request body.

{{% version include-if="2.1.x" %}}

1. Update the {{< reuse "docs/snippets/trafficpolicy.md" >}} resource and add a custom prompt guard. The following example parses requests sent to the LLM provider to identify a regex pattern match that is named `CC` for debugging purposes. The proxy blocks any requests that contain the `credit card` string in the request body. These requests are automatically denied with a custom response message.


   ```yaml
   kubectl apply -f - <<EOF
   apiVersion: {{< reuse "docs/snippets/trafficpolicy-apiversion.md" >}}
   kind: {{< reuse "docs/snippets/trafficpolicy.md" >}}
   metadata:
     name: openai-prompt-guard
     namespace: {{< reuse "docs/snippets/namespace.md" >}}
     labels:
       app: agentgateway
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
   EOF
   ```

   {{% /version %}}{{% version include-if="2.2.x" %}}
1. Update the {{< reuse "docs/snippets/trafficpolicy.md" >}} resource and add a custom prompt guard. The proxy blocks any requests that contain the `credit card` string in the request body. These requests are automatically denied with a custom response message.

   ```yaml
   kubectl apply -f - <<EOF
   apiVersion: {{< reuse "docs/snippets/trafficpolicy-apiversion.md" >}}
   kind: {{< reuse "docs/snippets/trafficpolicy.md" >}}
   metadata:
     name: openai-prompt-guard
     namespace: {{< reuse "docs/snippets/namespace.md" >}}
     labels:
       app: agentgateway
   spec:
     targetRefs:
     - group: gateway.networking.k8s.io
       kind: HTTPRoute
       name: openai
     backend:
       ai:
         promptGuard:
           request:
           - response:
               message: "Rejected due to inappropriate content"
             regex:
               action: REJECT
               matches:
               - "credit card"
   EOF
   ```

   {{% /version %}}

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

   {{< tabs tabTotal="2" items="Cloud Provider LoadBalancer,Port-forward for local testing" >}}

   {{% tab tabName="Cloud Provider LoadBalancer" %}}
   ```sh
   curl -v "$INGRESS_GW_ADDRESS/openai" -H content-type:application/json -d '{
     "model": "gpt-3.5-turbo",
     "messages": [
       {
         "role": "user",
         "content": "Can you give me some examples of Master Card credit card numbers?"
       }
     ]
   }'
   ```
   {{% /tab %}}

   {{% tab tabName="Port-forward for local testing" %}}
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
   {{% /tab %}}
   
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

   {{< tabs tabTotal="2" items="Cloud Provider LoadBalancer,Port-forward for local testing" >}}

   {{% tab tabName="Cloud Provider LoadBalancer" %}}
   ```sh
   curl "$INGRESS_GW_ADDRESS/openai" -H content-type:application/json -d '{
     "model": "gpt-3.5-turbo",
     "messages": [
       {
         "role": "user",
         "content": "Can you give me some examples of Master Card card numbers?"
       }
     ]
   }'
   ```
   {{% /tab %}}

   {{% tab tabName="Port-forward for local testing" %}}
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
   {{% /tab %}}

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

In the next step, you instruct agentgateway to mask credit card numbers that are returned by the LLM.

{{% version include-if="2.1.x" %}}
1. Add the following credit card response matcher to the {{< reuse "docs/snippets/trafficpolicy.md" >}} resource. This time, use the built-in credit card regex match instead of a custom one.
   
   ```yaml
   kubectl apply -f - <<EOF
   apiVersion: {{< reuse "docs/snippets/trafficpolicy-apiversion.md" >}}
   kind: {{< reuse "docs/snippets/trafficpolicy.md" >}}
   metadata:
     name: openai-prompt-guard
     namespace: {{< reuse "docs/snippets/namespace.md" >}}
     labels:
       app: agentgateway
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
   EOF
   ```
   {{% /version %}}{{% version include-if="2.2.x" %}}
1. Add the following credit card response matcher to the {{< reuse "docs/snippets/trafficpolicy.md" >}} resource. This time, use the built-in credit card regex match instead of a custom one.
   
   ```yaml
   kubectl apply -f - <<EOF
   apiVersion: {{< reuse "docs/snippets/trafficpolicy-apiversion.md" >}}
   kind: {{< reuse "docs/snippets/trafficpolicy.md" >}}
   metadata:
     name: openai-prompt-guard
     namespace: {{< reuse "docs/snippets/namespace.md" >}}
     labels:
       app: agentgateway
   spec:
     targetRefs:
     - group: gateway.networking.k8s.io
       kind: HTTPRoute
       name: openai
     backend:
       ai:
         promptGuard:
           response:
           - regex:
               builtins: 
                 - CREDIT_CARD
               action: MASK
   EOF
   ```
   {{% /version %}}

2. Send another request to the AI API and include a fake VISA credit card number. Verify that the VISA number is detected and masked in your response.
   
   {{< tabs tabTotal="2" items="Cloud Provider LoadBalancer,Port-forward for local testing" >}}

   {{% tab tabName="Cloud Provider LoadBalancer" %}}
   ```sh
   curl "$INGRESS_GW_ADDRESS/openai" -H content-type:application/json -d '{
     "model": "gpt-3.5-turbo",
     "messages": [
       {
         "role": "user",
         "content": "What type of number is 5105105105105100?"
       }
     ]
   }' | jq
   ```
   {{% /tab %}}

   {{% tab tabName="Port-forward for local testing" %}}
   ```sh
   curl "localhost:8080/openai" -H content-type:application/json -d '{
     "model": "gpt-3.5-turbo",
     "messages": [
       {
         "role": "user",
         "content": "What type of number is 5105105105105100?"
       }
     ]
   }' | jq
   ```
   {{% /tab %}}

   {{< /tabs >}}

   Example output: 
   
   ```json {linenos=table,hl_lines=[11],linenostart=1,filename="model-response.json"}
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
           "content": "<CREDIT_CARD> is an even number.",
           "refusal": null,
           "annotations": []
         },
         "logprobs": null,
         "finish_reason": "stop"
       }
   ...
   ```



## Cleanup

{{< reuse "docs/snippets/cleanup.md" >}}

```shell
kubectl delete {{< reuse "docs/snippets/trafficpolicy.md" >}} -n {{< reuse "docs/snippets/namespace.md" >}} -l app=agentgateway
```

## Next

[Enrich your prompts](../prompt-enrichment/) with system prompts to improve LLM outputs.
