
{{< reuse "docs/snippets/ai-rate-limiting.md" >}}

For more details about how rate limiting works in agentgateway enterprise or request-based rate limiting, see the [Rate limiting docs]({{< link-hextra path="/security/ratelimit/about/" >}}).


## Before you begin

{{< reuse "docs/snippets/agentgateway-prereq.md" >}}


## Agentgateway rate limit {#global}

Set up a global rate limit for the number of requests to any route through agentgateway.

1. Create a RateLimitConfig with your rate limit rules. To indicate that the rate limit counts requests and not tokens, include the `type: REQUEST"` field. The following example sets a global limit of 5 requests per minute.
   
   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: ratelimit.solo.io/v1alpha1
   kind: RateLimitConfig
   metadata:
     name: global-rate-limit
     namespace: {{< reuse "docs/snippets/namespace.md" >}}
   spec:
     raw:
       descriptors:
       - key: generic_key
         value: counter
         rateLimit:
           requestsPerUnit: 5
           unit: MINUTE
       rateLimits:
       - actions:
         - genericKey:
             descriptorValue: counter
         type: REQUEST
   EOF
   ```

2. Apply the rate limit by using a {{< reuse "docs/snippets/trafficpolicy.md" >}} resource. To indicate that the rate limit counts requests and not tokens, include the `type: REQUEST"` field. The following example targets the `agentgateway` HTTPRoute that you set up before you began.
   
   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: {{< reuse "docs/snippets/trafficpolicy-apiversion.md" >}}
   kind: {{< reuse "docs/snippets/trafficpolicy.md" >}}
   metadata:
     name: global-rate-limit
     namespace: {{< reuse "docs/snippets/namespace.md" >}}
   spec:
     targetRefs:
       - group: gateway.networking.k8s.io
         kind: Gateway
         name: agentgateway-proxy
     traffic: 
       entRateLimit:
         global:
           rateLimitConfigRefs:
           - name: global-rate-limit
   EOF
   ```

3. Send a simple request to a route on agentgateway. Verify that the request succeeds.
   
   {{< tabs tabTotal= "2" >}}
   {{% tab tabName="Cloud Provider LoadBalancer" %}}
   ```sh
   curl -v "${INGRESS_GW_ADDRESS}:8080/openai" -H content-type:application/json -d '{
    "model": "gpt-3.5-turbo",
    "messages": [
      {
        "role": "system",
        "content": "You are a poetic assistant, skilled in explaining complex programming concepts with creative flair."
      },
      {
        "role": "user",
        "content": "Compose a poem that explains the concept of recursion in programming."
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
        "role": "system",
        "content": "You are a poetic assistant, skilled in explaining complex programming concepts with creative flair."
      },
      {
        "role": "user",
        "content": "Compose a poem that explains the concept of recursion in programming."
      }
    ]
   }'
   ```
   {{% /tab %}}
   {{< /tabs >}}

4. Repeat the request. On the sixth time, verify that the request is now rate limited and that you get back a 429 HTTP response code, because only 5 requests per minute are allowed through your agentgateway.

   To test the rate limit by running the request multiple times, you can use a loop:

   {{< tabs tabTotal= "2" >}}
   {{% tab tabName="Cloud Provider LoadBalancer" %}}
   ```sh
   for i in {1..6}; do
     curl -v "${INGRESS_GW_ADDRESS}:8080/openai" -H content-type:application/json -d '{
      "model": "gpt-3.5-turbo",
      "messages": [
        {
          "role": "system",
          "content": "You are a poetic assistant, skilled in explaining complex programming concepts with creative flair."
        },
        {
          "role": "user",
          "content": "Make it a shorter haiku."
        }
      ]
     }'
     echo "--- Request $i completed ---"
   done
   ```
   {{% /tab %}}
   {{% tab tabName="Port-forward for local testing" %}}
   ```sh
   for i in {1..6}; do
     curl -v "localhost:8080/openai" -H content-type:application/json -d '{
      "model": "gpt-3.5-turbo",
      "messages": [
        {
          "role": "system",
          "content": "You are a poetic assistant, skilled in explaining complex programming concepts with creative flair."
        },
        {
          "role": "user",
          "content": "Make it a shorter haiku."
        }
      ]
     }'
     echo "--- Request $i completed ---"
   done
   ```
   {{% /tab %}}
   {{< /tabs >}}

   Example output: 
   ```
   < HTTP/1.1 429 Too Many Requests
   < x-envoy-ratelimited: true
   < date: Tue, 18 Jun 2024 05:15:13 GMT
   < server: envoy
   < content-length: 0
   ```


## LLM provider rate limit {#request}

If you have routes to multiple LLM providers, you can enforce a rate limit for each provider.

1. Create a RateLimitConfig with the rate limit rules for the LLM provider. To indicate that the rate limit counts requests and not tokens, include the `type: REQUEST"` field. The following example sets a limit of 2 requests per minute.
   
   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: ratelimit.solo.io/v1alpha1
   kind: RateLimitConfig
   metadata:
     name: openai-rate-limit
     namespace: {{< reuse "docs/snippets/namespace.md" >}}
   spec:
     raw:
       descriptors:
       - key: generic_key
         value: counter
         rateLimit:
           requestsPerUnit: 2
           unit: MINUTE
       rateLimits:
       - actions:
         - genericKey:
             descriptorValue: counter
         type: REQUEST
   EOF
   ```

2. Apply the rate limit by using a {{< reuse "docs/snippets/trafficpolicy.md" >}} resource. The following example targets the `openai` HTTPRoute that you set up before you began.
   
   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: {{< reuse "docs/snippets/trafficpolicy-apiversion.md" >}}
   kind: {{< reuse "docs/snippets/trafficpolicy.md" >}}
   metadata:
     name: openai-rate-limit
     namespace: {{< reuse "docs/snippets/namespace.md" >}}
   spec:
     targetRefs:
       - group: gateway.networking.k8s.io
         kind: HTTPRoute
         name: openai
     traffic: 
       entRateLimit:
         global:
           rateLimitConfigRefs:
           - name: openai-rate-limit
   EOF
   ```

3. Send a simple request to the OpenAI API. Verify that the request succeeds.
   
   {{< tabs tabTotal= "2" >}}
   {{% tab tabName="Cloud Provider LoadBalancer" %}}
   ```sh
   curl -v "${INGRESS_GW_ADDRESS}:8080/openai" -H content-type:application/json -d '{
    "model": "gpt-3.5-turbo",
    "messages": [
      {
        "role": "system",
        "content": "You are a poetic assistant, skilled in explaining complex programming concepts with creative flair."
      },
      {
        "role": "user",
        "content": "Compose a poem that explains the concept of recursion in programming."
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
        "role": "system",
        "content": "You are a poetic assistant, skilled in explaining complex programming concepts with creative flair."
      },
      {
        "role": "user",
        "content": "Compose a poem that explains the concept of recursion in programming."
      }
    ]
   }'
   ```
   {{% /tab %}}
   {{< /tabs >}}

   Example output:
   ```json
   {
     "id": "chatcmpl-9bLT1ofadlXEMpo53LcGjHsv3S5Ry",
     "object": "chat.completion",
     "created": 1718687683,
     "model": "gpt-3.5-turbo-0125",
     "choices": [
       {
         "index": 0,
         "message": {
           "role": "assistant",
           "content": "In the realm of code, a concept so divine,\nRecursion weaves patterns, like nature's design.\nA function that calls itself, with purpose and grace,\nIt solves problems complex, with elegance and pace.\n\nLike a mirror reflecting its own reflection,\nRecursion repeats with boundless affection.\nEach iteration holds a story untold,\nUnraveling mysteries, a journey unfold.\n\nInfinite loops, a dangerous abyss,\nRecursion beckons with a siren's sweet kiss.\nBase case in"
         },
         "logprobs": null,
         "finish_reason": "length"
       }
     ],
     "usage": {
       "prompt_tokens": 39,
       "completion_tokens": 100,
       "total_tokens": 139
     },
     "system_fingerprint": null
   }
   ```

4. Repeat the request two more times. Verify that the request is now rate limited and that you get back a 429 HTTP response code, because only 2 requests per minute are allowed for OpenAI.
   {{< tabs tabTotal= "2" >}}
   {{% tab tabName="Cloud Provider LoadBalancer" %}}
   ```sh
   curl -v "${INGRESS_GW_ADDRESS}:8080/openai" -H content-type:application/json -d '{
    "model": "gpt-3.5-turbo",
    "messages": [
      {
        "role": "system",
        "content": "You are a poetic assistant, skilled in explaining complex programming concepts with creative flair."
      },
      {
        "role": "user",
        "content": "Make it a shorter haiku."
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
        "role": "system",
        "content": "You are a poetic assistant, skilled in explaining complex programming concepts with creative flair."
      },
      {
        "role": "user",
        "content": "Make it a shorter haiku."
      }
    ]
   }'
   ```
   {{% /tab %}}
   {{< /tabs >}}
   Example output: 
   ```
   < HTTP/1.1 429 Too Many Requests
   < x-envoy-ratelimited: true
   < date: Tue, 18 Jun 2024 05:15:13 GMT
   < server: envoy
   < content-length: 0
   ```


## Token-based rate limit {#token}

Instead of request-based rate limiting, you can apply a rate limit based on the number of tokens used. This approach helps make your costs and AI usage more predictable.

1. Update your OpenAI RateLimitConfig with your rate limit for tokens. Add a rate limit descriptor and action pair that set `type: TOKEN`. The following example adds a user limit of 100 tokens per minute.

   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: ratelimit.solo.io/v1alpha1
   kind: RateLimitConfig
   metadata:
     name: openai-rate-limit
     namespace: {{< reuse "docs/snippets/namespace.md" >}}
   spec:
     raw:
       descriptors:
       - key: X-User-ID
         rateLimit:
           unit: MINUTE
           requestsPerUnit: 100
       rateLimits:
       - actions:
         - requestHeaders:
             descriptorKey: "X-User-ID"
             headerName: "X-User-ID"
         type: TOKEN
   EOF
   ```

2. Check that the rate limit is still applied by the {{< reuse "docs/snippets/trafficpolicy.md" >}} that selects your updated RateLimitConfig.
   
   ```sh
   kubectl get {{< reuse "docs/snippets/trafficpolicy.md" >}} openai-rate-limit -n {{< reuse "docs/snippets/namespace.md" >}} -o yaml
   ```

   Example output:

   ```yaml
   status:
       ancestors:
       - ancestorRef:
           group: gateway.networking.k8s.io
           kind: HTTPRoute
           name: openai
           namespace: {{< reuse "docs/snippets/namespace.md" >}}
         conditions:
         - lastTransitionTime: "2025-09-29T16:58:37Z"
           message: Policy accepted
           reason: Valid
           status: "True"
           type: Accepted
         - lastTransitionTime: "2025-09-29T16:58:37Z"
           message: Attached to all targets
           reason: Attached
           status: "True"
           type: Attached
         controllerName: solo.io/agentgateway
       - ancestorRef:
           group: gateway.networking.k8s.io
           kind: HTTPRoute
           name: openai
           namespace: {{< reuse "docs/snippets/namespace.md" >}}
         conditions:
         - lastTransitionTime: "2025-09-29T16:58:37Z"
           message: Policy accepted
           reason: Accepted
           status: "True"
           type: Accepted
         controllerName: solo.io/agentgateway
   ```

3. Send a simple request to the OpenAI API. Verify that the request succeeds. Include the `X-User-ID` request header with the value `user123`.
   
   {{< tabs tabTotal= "2" >}}
   {{% tab tabName="Cloud Provider LoadBalancer" %}}
   ```sh
   curl -v "${INGRESS_GW_ADDRESS}:8080/openai" -H content-type:application/json -H "X-User-ID: user123" -d '{
    "model": "gpt-3.5-turbo",
    "messages": [
      {
        "role": "system",
        "content": "You are a poetic assistant, skilled in explaining complex programming concepts with creative flair."
      },
      {
        "role": "user",
        "content": "In the style of Shakespeare, write a series of sonnets that explain the concept of recursion in programming."
      }
    ]
   }'
   ```
   {{% /tab %}}
   {{% tab tabName="Port-forward for local testing" %}}
   ```sh
   curl -v "localhost:8080/openai" -H content-type:application/json -H "X-User-ID: user123" -d '{
    "model": "gpt-3.5-turbo",
    "messages": [
      {
        "role": "system",
        "content": "You are a poetic assistant, skilled in explaining complex programming concepts with creative flair."
      },
      {
        "role": "user",
        "content": "In the style of Shakespeare, write a series of sonnets that explain the concept of recursion in programming."
      }
    ]
   }'
   ```
   {{% /tab %}}
   {{< /tabs >}}

   In the output, note that the `usage` section shows how many total tokens the request uses, such as 256. Because this is the first request, the limit was not yet exceeded and so the request succeeds even though it exceeds the limit of 100 tokens per minute.
   ```json
   {
     "id": "chatcmpl-9bLT1ofadlXEMpo53LcGjHsv3S5Ry",
     "object": "chat.completion",
     "created": 1718687683,
     "model": "gpt-3.5-turbo-0125",
     "choices": [
       {
         "index": 0,
         "message": {
           "role": "assistant",
           "content": "In the realm of code, a concept so divine,\nRecursion weaves patterns, like nature's design.\nA function that calls itself, with purpose and grace,\nIt solves problems complex, with elegance and pace.\n\nLike a mirror reflecting its own reflection,\nRecursion repeats with boundless affection.\nEach iteration holds a story untold,\nUnraveling mysteries, a journey unfold.\n\nInfinite loops, a dangerous abyss,\nRecursion beckons with a siren's sweet kiss.\nBase case in"
         },
         "logprobs": null,
         "finish_reason": "length"
       }
     ],
     "usage": {
       "prompt_tokens": 48,
       "completion_tokens": 208,
       "total_tokens": 256
     },
     "system_fingerprint": null
   }
   ```

4. Repeat the request. Verify that the request is now rate limited and that you get back a 429 HTTP response code. <!--TODO multiple RLCs Even though you only sent 2 requests to your OpenAI provider, which is allowed per the request rate limit, you exceeded the token rate limit.-->
   {{< tabs tabTotal= "2" >}}
   {{% tab tabName="Cloud Provider LoadBalancer" %}}
   ```sh
   curl -v "${INGRESS_GW_ADDRESS}:8080/openai" -H content-type:application/json -H "X-User-ID: user123" -d '{
    "model": "gpt-3.5-turbo",
    "messages": [
      {
        "role": "system",
        "content": "You are a poetic assistant, skilled in explaining complex programming concepts with creative flair."
      },
      {
        "role": "user",
        "content": "Make it a shorter haiku."
      }
    ]
   }'
   ```
   {{% /tab %}}
   {{% tab tabName="Port-forward for local testing" %}}
   ```sh
   curl -v "localhost:8080/openai" -H content-type:application/json -H "X-User-ID: user123" -d '{
    "model": "gpt-3.5-turbo",
    "messages": [
      {
        "role": "system",
        "content": "You are a poetic assistant, skilled in explaining complex programming concepts with creative flair."
      },
      {
        "role": "user",
        "content": "Make it a shorter haiku."
      }
    ]
   }'
   ```
   {{% /tab %}}
   {{< /tabs >}}
   
   Example output: 
   ```
   < HTTP/1.1 429 Too Many Requests
   < x-envoy-ratelimited: true
   < date: Tue, 18 Jun 2024 05:15:13 GMT
   < server: envoy
   < content-length: 0
   ```


## CEL-based rate limit {#cel}

CEL (Common Expression Language) transformations allows you to use dynamic expressions to extract and transform values from requests and responses. 

For an overview of supported CEL expressions, see the [agentgateway docs](https://agentgateway.dev/docs/reference/cel/).

1. Create a RateLimitConfig with the rate limit rules for the CEL transformation. The following example sets a limit of 1 request per minute.
   
   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: ratelimit.solo.io/v1alpha1
   kind: RateLimitConfig
   metadata:
     name: cel-rate-limit-config
     namespace: {{< reuse "docs/snippets/namespace.md" >}}
   spec:
     raw:
       domain: "solo.io"
       descriptors:
       - key: "me"
         rateLimit:
           requestsPerUnit: 1
           unit: MINUTE
       rateLimits:
       - actions:
         - cel:
           expression: 'request.headers["x-user"]'
           key: "me"
   EOF
   ```

   Example output:
   ```txt
   ratelimitconfig.ratelimit.solo.io/mcp-cel-rate-limit-config created
   ```

2. Apply the rate limit by using a {{< reuse "docs/snippets/trafficpolicy.md" >}} resource. The following example targets the HTTPRoute that you set up before you began.
   
   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: {{< reuse "docs/snippets/trafficpolicy-apiversion.md" >}}
   kind: {{< reuse "docs/snippets/trafficpolicy.md" >}}
   metadata:
     name: mcp-echo-cel-rate-limit
     namespace: {{< reuse "docs/snippets/namespace.md" >}}
   spec:
     targetRefs:
       - group: gateway.networking.k8s.io
         kind: HTTPRoute
         name: openai
     traffic:
       entRateLimit:
         global:
           rateLimitConfigRefs:
           - name: cel-rate-limit-config
             namespace: {{< reuse "docs/snippets/namespace.md" >}}
   EOF
   ```
   
   Example output:
   ```txt
   enterpriseagentgatewaypolicy.enterpriseagentgateway.solo.io/mcp-echo-cel-rate-limit created
   ```

3. Send a simple request to the OpenAI API. Include the `x-user` request header with the value `me`. Verify that the request succeeds. 
   
   {{< tabs tabTotal= "2" >}}
   {{% tab tabName="Cloud Provider LoadBalancer" %}}
   ```sh
   curl -v "${INGRESS_GW_ADDRESS}:8080/openai" -H content-type:application/json -H "x-user: me" -d '{
    "model": "gpt-3.5-turbo",
    "messages": [
      {
        "role": "system",
        "content": "You are a poetic assistant, skilled in explaining complex programming concepts with creative flair."
      },
      {
        "role": "user",
        "content": "Compose a poem that explains the concept of recursion in programming."
      }
    ]
   }'
   ```
   {{% /tab %}}
   {{% tab tabName="Port-forward for local testing" %}}
   ```sh
   curl -v "localhost:8080/openai" -H content-type:application/json -H "x-user: me" -d '{
    "model": "gpt-3.5-turbo",
    "messages": [
      {
        "role": "system",
        "content": "You are a poetic assistant, skilled in explaining complex programming concepts with creative flair."
      },
      {
        "role": "user",
        "content": "Compose a poem that explains the concept of recursion in programming."
      }
    ]
   }'
   ```
   {{% /tab %}}
   {{< /tabs >}}

   Example output:
   ```json
   {
     "id": "chatcmpl-9bLT1ofadlXEMpo53LcGjHsv3S5Ry",
     "object": "chat.completion",
     "created": 1718687683,
     "model": "gpt-3.5-turbo-0125",
     "choices": [
       {
         "index": 0,
         "message": {
           "role": "assistant",
           "content": "In the realm of code, a concept so divine,\nRecursion weaves patterns, like nature's design.\nA function that calls itself, with purpose and grace,\nIt solves problems complex, with elegance and pace.\n\nLike a mirror reflecting its own reflection,\nRecursion repeats with boundless affection.\nEach iteration holds a story untold,\nUnraveling mysteries, a journey unfold.\n\nInfinite loops, a dangerous abyss,\nRecursion beckons with a siren's sweet kiss.\nBase case in"
         },
         "logprobs": null,
         "finish_reason": "length"
       }
     ],
     "usage": {
       "prompt_tokens": 39,
       "completion_tokens": 100,
       "total_tokens": 139
     },
     "system_fingerprint": null
   }
   ```

4. Repeat the request. Verify that the request is now rate limited and that you get back a 429 HTTP response code, because only 1 request per minute is allowed for OpenAI.
   {{< tabs tabTotal= "2" >}}
   {{% tab tabName="Cloud Provider LoadBalancer" %}}
   ```sh
   curl -v "${INGRESS_GW_ADDRESS}:8080/openai" -H content-type:application/json -H "x-user: me" -d '{
    "model": "gpt-3.5-turbo",
    "messages": [
      {
        "role": "system",
        "content": "You are a poetic assistant, skilled in explaining complex programming concepts with creative flair."
      },
      {
        "role": "user",
        "content": "Make it a shorter haiku."
      }
    ]
   }'
   ```
   {{% /tab %}}
   {{% tab tabName="Port-forward for local testing" %}}
   ```sh
   curl -v "localhost:8080/openai" -H content-type:application/json -H "x-user: me" -d '{
    "model": "gpt-3.5-turbo",
    "messages": [
      {
        "role": "system",
        "content": "You are a poetic assistant, skilled in explaining complex programming concepts with creative flair."
      },
      {
        "role": "user",
        "content": "Make it a shorter haiku."
      }
    ]
   }'
   ```
   {{% /tab %}}
   {{< /tabs >}}
   Example output: 
   ```
   < HTTP/1.1 429 Too Many Requests
   < x-envoy-ratelimited: true
   < date: Fri, 16 Jan 2026 05:15:13 GMT
   < server: envoy
   < content-length: 0
   ```


## Cleanup

{{< reuse "docs/snippets/cleanup.md" >}}

```sh
kubectl delete RateLimitConfig global-rate-limit -n {{< reuse "docs/snippets/namespace.md" >}}
kubectl delete RateLimitConfig openai-rate-limit -n {{< reuse "docs/snippets/namespace.md" >}}
kubectl delete {{< reuse "docs/snippets/trafficpolicy.md" >}} global-rate-limit -n {{< reuse "docs/snippets/namespace.md" >}}
kubectl delete {{< reuse "docs/snippets/trafficpolicy.md" >}} openai-rate-limit -n {{< reuse "docs/snippets/namespace.md" >}}
```
