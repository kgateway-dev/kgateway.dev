---
title: AI observability
weight: 90
---

Observability helps you understand how your system is performing, identify issues, and troubleshoot problems. AI Gateway provides a rich set of observability features that help you monitor and analyze the performance of your AI Gateway and the LLM providers that it interacts with. 

## Before you begin

1. [Set up AI Gateway](/ai/tutorials/setup-gw/).

2. [Authenticate to the LLM](/ai/guides/auth/).

3. Get the external address of the gateway and save it in an environment variable.
   
   {{< tabs items="Cloud Provider LoadBalancer,Port-forward for local testing" >}}
   {{% tab %}}
   ```sh
   export INGRESS_GW_ADDRESS=$(kubectl get svc -n kgateway-system ai-gateway -o jsonpath="{.status.loadBalancer.ingress[0]['hostname','ip']}")
   echo $INGRESS_GW_ADDRESS  
   ```
   {{% /tab %}}
   {{% tab %}}
   ```sh
   kubectl port-forward deployment/ai-gateway -n kgateway-system 8080:8080
   ```
   {{% /tab %}}
   {{< /tabs >}}

## Metrics

Metrics are helpful for understanding the overall health and performance of your system. AI Gateway provides a rich set of metrics for you to monitor and analyze the performance of your AI Gateway and the LLM providers that it interacts with.

### Dynamic metadata

Dynamic metadata is a powerful feature of Envoy that allows you to attach arbitrary key-value pairs to requests and responses as they flow through the Envoy proxy. AI Gateway uses dynamic metadata to expose key metrics related to LLM provider usage. These metrics can be used to monitor and analyze the performance of your AI Gateway and the LLM providers that it interacts with.

| Dynamic Metadata Field | Description |
|-----------------------|-------------|
| `ai.gateway.kgateway.dev:total_tokens` | The total number of tokens used in the request |
| `ai.gateway.kgateway.dev:prompt_tokens` | The number of tokens used in the prompt |
| `ai.gateway.kgateway.dev:completion_tokens` | The number of tokens used in the completion |
| `envoy.ratelimit:hits_addend` | The number of tokens that were calculated to be rate limited |
| `ai.gateway.kgateway.dev:model` | The model which was specified by the user in the request |
| `ai.gateway.kgateway.dev:provider_model` | The model which the LLM provider used and returned in the response |
| `ai.gateway.kgateway.dev:provider` | The LLM provider being used, such as `OpenAI`, `Anthropic`, etc. |
| `ai.gateway.kgateway.dev:streaming` | A boolean indicating whether the request was streamed |

### Default metrics

Take a look at the default metrics that the system outputs.

1. In another tab in your terminal, port-forward the `ai-gateway` container of the gateway proxy.
   ```sh
   kubectl port-forward -n {{< reuse "docs/snippets/ns-system.md" >}} deploy/ai-gateway 9092
   ```

2. In the previous tab, run the following command to view the metrics.
   ```sh
   curl localhost:9092/metrics
   ```

3. In the output, search for the `ai_completion_tokens_total` and `ai_prompt_tokens_total` metrics. These metrics total the number of tokens used in the prompt and completion for the `openai` model `gpt-3.5-turbo`. 
   ```
   # HELP ai_completion_tokens_total Completion tokens
   # TYPE ai_completion_tokens_total counter
   ai_completion_tokens_total{llm="openai",model="gpt-3.5-turbo"} 539.0
   ...
   # HELP ai_prompt_tokens_total Prompt tokens
   # TYPE ai_prompt_tokens_total counter
   ai_prompt_tokens_total{llm="openai",model="gpt-3.5-turbo"} 204.0
   ```

4. Stop port-forwarding the `ai-gateway` container.


<!-- TODO: These sections do not work until JWT support is added, because the access logs and custom metrics rely on pulling the JWT token from a processed request. 

In the following tutorial, you extract claims from the JSON Web Tokens (JWTs) for Alice and Bob that you create by using a sample JWT tool. Then, you learn how to gather and observe key metrics related to LLM provider usage. Note that all observability features in this tutorial are built on existing {{< reuse "docs/snippets/product-name.md" >}} monitoring capabilities. For more information, see the [Observability](/docs/observability/) guide.

## Get the JWTs {#get-jwts}

In the following example, you use sample JWTs for two different users, Alice and Bob.

{{% callout type="info" %}}
You can optionally create other JWT tokens by using the [JWT generator tool](https://github.com/solo-io/solo-cop/blob/main/tools/jwt-generator/README.md). 
{{% /callout %}}

{{% callout type="warning" %}}
Use self-signed certificates for testing purposes only. In a production environment, you typically use a trusted Certificate Authority to sign the JWT tokens.
{{% /callout %}}

1. Save the JWT token for Alice in an environment variable.
   
   ```sh
   export ALICE_TOKEN=eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyAiaXNzIjogInNvbG8uaW8iLCAib3JnIjogInNvbG8uaW8iLCAic3ViIjogImFsaWNlIiwgInRlYW0iOiAiZGV2IiwgImxsbXMiOiB7ICJvcGVuYWkiOiBbICJncHQtMy41LXR1cmJvIiBdIH0gfQ.I7whTti0aDKxlILc5uLK9oo6TljGS6JUrjPVd6z1PxzucUa_cnuKkY0qj_wrkzyVN5djy4t2ggE1uBO8Llpwi-Ygru9hM84-1m53aO07JYFya1VTDsI25tCRG8rYhShDdAP5L935SIARta2QtHhrVcd1Ae7yfTDZ8G1DXLtjR2QelszCd2R8PioCQmqJ8PeKg4sURhu05GlBCZoXES9-rtPVbe6j3YLBTodJAvLHhyy3LgV_QbN7IiZ5qEywdKHoEF4D4aCUf_LqPp4NoqHXnGT4jLzWJEtZXHQ4sgRy_5T93NOLzWLdIjgMjGO_F0aVLwBzU-phykOVfcBPaMvetg
   ```

   Alice works in the `dev` team, and this token gives her access to the `gpt-3.5-turbo` model of the AI API:
   ```json
   {
     "iss": "solo.io",
     "org": "solo.io",
     "sub": "alice",
     "team": "dev",
     "llms": {
       "openai": [
         "gpt-3.5-turbo"
       ]
     }
   }
   ```

2. Save the JWT token for Bob in an environment variable.
      
   ```sh
   export BOB_TOKEN=eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyAiaXNzIjogInNvbG8uaW8iLCAib3JnIjogInNvbG8uaW8iLCAic3ViIjogImJvYiIsICJ0ZWFtIjogIm9wcyIsICJsbG1zIjogeyAibWlzdHJhbGFpIjogWyAibWlzdHJhbC1sYXJnZS1sYXRlc3QiIF0gfSB9.p7J2UFwnUJ6C7eXsFCSKb5b7ecWZ75JO4TUJHafjLv8jJ7GzKfJVk7ney19PYUrWrO4ntwnnK5_sY7yaLUBCJ3fv9pcoKyRtJTw1VMMTQsKkWFgvy-jEwc9M-D5lrUfR1HXGEUm6NBaj_Ja78XScPZb_-APPqMIvzDZU04vd6hna3UMc4DZE0wcnTjOqoND0GllHLupYTfgX0v9_AYJiKRAcJvol1W14dI7szpY5GFZtPqq0kl1g0sJPg-HQKwf7Cfvr_JLjkepNJ6A1lsrG8QbuUvMUAdaHzwLvF3L_G6VRjEte6okZpaq0g2urWpZgdNmPVN71Q_0WhyrJTr6SyQ
   ```

   Bob works in the `ops` team and does not have access to any LLM in the OpenAI. Instead, he has access to an LLM (`mistral-large-latest`) from a different AI provider (Mistral AI):
   
   ```json
   {
     "iss": "solo.io",
     "org": "solo.io",
     "sub": "bob",
     "team": "ops",
     "llms": {
       "mistralai": [
         "mistral-large-latest"
       ]
     }
   }
   ```

Next, set up access logging.

## Access logging

Access logs, sometimes referred to as audit logs, represent all traffic requests that pass through the AI Gateway proxy. You can leverage the default Envoy access log collector to record logs for the AI Gateway. You can then review these logs to identify and troubleshoot issues as-needed, or scrape these logs to view them in your larger platform logging system. Auditors in your organization can use this information to better understand how users interact with your system, and to detect malicious activity or unusual amounts of requests to your gateway.

1. Define access logging configuration for the gateway in an `HTTPListenerPolicy` resource. This resource configures Envoy to log access logs to `stdout` in JSON format by using `DYNAMIC_METADATA` fields that are specifically exposed for the AI Gateway.
   
   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.kgateway.dev/v1alpha1
   kind: HTTPListenerPolicy
   metadata:
     name: log-provider
     namespace: kgateway-system
   spec:
     targetRefs:
     - group: gateway.networking.k8s.io
       kind: Gateway
       name: ai-gateway
     accessLog:
     - fileSink:
         path: /dev/stdout
         jsonFormat:
           http_method: '%REQ(:METHOD)%'
           path: '%REQ(X-ENVOY-ORIGINAL-PATH?:PATH)%'
           user: '%DYNAMIC_METADATA(envoy.filters.http.jwt_authn:principal:sub)%'
           team: '%DYNAMIC_METADATA(envoy.filters.http.jwt_authn:principal:team)%'
           request_id: '%REQ(X-REQUEST-ID)%'
           response_code: '%RESPONSE_CODE%'
           system_time: '%START_TIME%'
           target_duration: '%RESPONSE_DURATION%'
           upstream_name: '%UPSTREAM_CLUSTER%'
           total_tokens: '%DYNAMIC_METADATA(ai.gateway.kgateway.dev:total_tokens)%'
           prompt_tokens: '%DYNAMIC_METADATA(ai.gateway.kgateway.dev:prompt_tokens)%'
           completion_tokens: '%DYNAMIC_METADATA(ai.gateway.kgateway.dev:completion_tokens)%'
           rate_limited_tokens: '%DYNAMIC_METADATA(envoy.ratelimit:hits_addend)%'
           streaming: '%DYNAMIC_METADATA(ai.gateway.kgateway.dev:streaming)%'
   EOF
   ```

2. Send a curl request with the JWT token for Alice to review access logs in action.

   {{< tabs items="Cloud Provider LoadBalancer,Port-forward for local testing" >}}

   {{< tab >}}
   ```sh
   curl "$INGRESS_GW_ADDRESS:8080/openai" -H "Authorization: Bearer $ALICE_TOKEN" -H content-type:application/json -d '{
    "model": "gpt-3.5-turbo",
    "messages": [
      {
        "role": "user",
        "content": "Please explain the movie Dr. Strangelove in 1 sentence."
      }
    ]
   }'
   ```
   {{< /tab >}}

   {{< tab >}}
   ```sh
   curl "localhost:8080/openai" -H "Authorization: Bearer $ALICE_TOKEN" -H content-type:application/json -d '{
    "model": "gpt-3.5-turbo",
    "messages": [
      {
        "role": "user",
        "content": "Please explain the movie Dr. Strangelove in 1 sentence."
      }
    ]
   }'
   ```
   {{< /tab >}}

   {{< /tabs >}}

3. After the request completes, view the access log for this request by getting the logs from the AI Gateway pod.
   
   ```sh
   kubectl logs -n {{< reuse "docs/snippets/ns-system.md" >}} deploy/ai-gateway | tail -1 | jq --sort-keys
   ```

   Verify that a log for your request is returned and looks similar to the following. If a log with these fields doesn't show up immediately, run the `kubectl logs` command again, as the logs are flushed asynchronously.
   
   ```json
   {
     "completion_tokens":22,
     "http_method":"POST",
     "path":"/v1/chat/completions",
     "prompt_tokens":21,
     "rate_limited_tokens":23,
     "request_id":"ee53553a-ca2f-4e49-b426-325d0cfc05f5",
     "response_code":200,
     "streaming":false,
     "system_time":"2025-01-02T17:32:53.596Z",
     "target_duration":544,
     "team":"dev",
     "total_tokens":43,
     "upstream_name":"openai_{{< reuse "docs/snippets/ns-system.md" >}}",
     "user":"alice"
   }
   ```

4. To review a log for a streamed response, send a curl request that uses streaming with the JWT token for Bob.
   
   {{< tabs items="Cloud Provider LoadBalancer,Port-forward for local testing" >}}

   {{< tab >}}
   ```sh
   curl "$INGRESS_GW_ADDRESS:8080/openai" -H "Authorization: Bearer $BOB_TOKEN" -H content-type:application/json -d '{
    "model": "gpt-3.5-turbo",
    "messages": [
      {
        "role": "user",
        "content": "Please explain the movie Dr. Strangelove in 1 sentence."
      }
    ],
    "stream_options": {
      "include_usage": true
    },
    "stream": true
   }'
   ```
   {{< /tab >}}

   {{< tab >}}
   ```sh
   curl "localhost:8080/openai" -H "Authorization: Bearer $BOB_TOKEN" -H content-type:application/json -d '{
    "model": "gpt-3.5-turbo",
    "messages": [
      {
        "role": "user",
        "content": "Please explain the movie Dr. Strangelove in 1 sentence."
      }
    ],
    "stream_options": {
      "include_usage": true
    },
    "stream": true
   }'
   ```
   {{< /tab >}}

   {{< /tabs >}}

5. Check the most recent access log again.
   
   ```sh
   kubectl logs -n {{< reuse "docs/snippets/ns-system.md" >}} deploy/ai-gateway | tail -1 | jq --sort-keys
   ```
   
   This time, the `streaming` field is recorded as `true` and the `user` is `bob`, but all other token information is still available.
   
   ```json
   {
     "completion_tokens":40,
     "http_method":"POST",
     "path":"/v1/chat/completions",
     "prompt_tokens":21,
     "rate_limited_tokens":23,
     "request_id":"8fa7950a-e609-4e3b-83f1-2cd38cf3c591",
     "response_code":200,
     "streaming":true,
     "system_time":"2025-01-02T17:34:13.213Z",
     "target_duration":297,
     "team":"ops",
     "total_tokens":61,
     "upstream_name":"openai_{{< reuse "docs/snippets/ns-system.md" >}}",
     "user":"bob"
   }
   ```

## Metrics

While access logs are great for understanding individual requests, metrics are better for understanding the overall health and performance of your system. AI Gateway provides a rich set of metrics that help you monitor and analyze the performance of your AI Gateway and the LLM providers that it interacts with. In addition, you can add custom labels to these metrics to help you better understand the context of the requests.

### Default metrics

Before you modify the labels, first take a look at the default metrics that the system outputs.

1. In another tab in your terminal, port-forward the `ai-gateway` container of the gateway proxy.
   ```sh
   kubectl port-forward -n {{< reuse "docs/snippets/ns-system.md" >}} deploy/ai-gateway 9092
   ```

2. In the previous tab, run the following command to view the metrics.
   ```sh
   curl localhost:9092/metrics
   ```

3. In the output, search for the `ai_completion_tokens_total` and `ai_prompt_tokens_total` metrics. These metrics total the number of tokens used in the prompt and completion for the `openai` model `gpt-3.5-turbo`. 
   ```
   # HELP ai_completion_tokens_total Completion tokens
   # TYPE ai_completion_tokens_total counter
   ai_completion_tokens_total{llm="openai",model="gpt-3.5-turbo"} 539.0
   ...
   # HELP ai_prompt_tokens_total Prompt tokens
   # TYPE ai_prompt_tokens_total counter
   ai_prompt_tokens_total{llm="openai",model="gpt-3.5-turbo"} 204.0
   ```

4. Stop port-forwarding the `ai-gateway` container.

### Customized metrics

Default metrics are useful for gauging LLM usage overtime, but don't help you understand usage by each team. You can add that context by creating custom labels.

1. To add custom labels to the metrics, update the `GatewayParameters` resource. In the `stats.customLabels` section, add a list of labels that contain the name of the label and the dynamic metadata field to get the label from. In this resource, the `team` label sources from the `team` field of the JWT token. The metadata namespace defaults to the namespace where you defined the JWT provider, but you can specify a different namespace if you have a different source of metadata.
   
   {{% callout type="info" %}}
   When you apply this resource, the gateway proxy restarts to pick up the new stats configuration.
   {{% /callout %}}

   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.kgateway.dev/v1alpha1
   kind: GatewayParameters
   metadata:
     name: ai-gateway
     namespace: kgateway-system
     labels:
       app: ai-kgateway
   spec:
     kube:
       aiExtension:
         enabled: true
         ports:
         - name: ai-monitoring
           containerPort: 9092
         stats:
           customLabels:
             - name: "team"
               metadataKey: "principal:team"
       service:
         type: ClusterIP
   EOF
   ```

2. Send one request as Alice and one request as Bob to test out the metrics labels.

   {{< tabs items="Cloud Provider LoadBalancer,Port-forward for local testing" >}}

   {{< tab >}}
   ```sh
   curl "$INGRESS_GW_ADDRESS:8080/openai" -H "Authorization: Bearer $ALICE_TOKEN" -H content-type:application/json -d '{
    "model": "gpt-3.5-turbo",
    "messages": [
      {
        "role": "user",
        "content": "Please explain the movie Dr. Strangelove in 1 sentence."
      }
    ]
   }'
   curl "$INGRESS_GW_ADDRESS:8080/openai" -H "Authorization: Bearer $BOB_TOKEN" -H content-type:application/json -d '{
    "model": "gpt-3.5-turbo",
    "messages": [
      {
        "role": "user",
        "content": "Please explain the movie Dr. Strangelove in 1 sentence."
      }
    ]
   }'
   ```
   {{< /tab >}}

   {{< tab >}}
   ```sh
   curl "localhost:8080/openai" -H "Authorization: Bearer $ALICE_TOKEN" -H content-type:application/json -d '{
    "model": "gpt-3.5-turbo",
    "messages": [
      {
        "role": "user",
        "content": "Please explain the movie Dr. Strangelove in 1 sentence."
      }
    ]
   }'
   curl "localhost:8080/openai" -H "Authorization: Bearer $BOB_TOKEN" -H content-type:application/json -d '{
    "model": "gpt-3.5-turbo",
    "messages": [
      {
        "role": "user",
        "content": "Please explain the movie Dr. Strangelove in 1 sentence."
      }
    ]
   }'
   ```
   {{< /tab >}}

   {{< /tabs >}}

3. In the port-forwarding tab, run the port-forward command again for the `ai-gateway` container of the gateway proxy.
   
   ```sh
   kubectl port-forward -n {{< reuse "docs/snippets/ns-system.md" >}} deploy/ai-gateway 9092
   ```

4. In the previous tab, view the metrics again.
   
   ```sh
   curl localhost:9092/metrics
   ```

5. In the output, search for the `ai_completion_tokens_total` and `ai_prompt_tokens_total` metrics again, and verify that the token total metrics are now separated according to team.
   
   ```
   # HELP ai_completion_tokens_total Completion tokens
   # TYPE ai_completion_tokens_total counter
   ai_prompt_tokens_total{llm="openai",model="gpt-3.5-turbo",team="dev"} 21.0
   ai_prompt_tokens_total{llm="openai",model="gpt-3.5-turbo",team="ops"} 21.0
   ...
   # HELP ai_prompt_tokens_total Prompt tokens
   # TYPE ai_prompt_tokens_total counter
   ai_completion_tokens_total{llm="openai",model="gpt-3.5-turbo",team="dev"} 18.0
   ai_completion_tokens_total{llm="openai",model="gpt-3.5-turbo",team="ops"} 30.0
   ```

## Next

You can now explore how to add further protection to your LLM provider by setting up [rate limiting based on claims in a JWT token](/ai/tutorials/ratelimit/).

Note that if you do not want to complete the rate limiting tutorial and instead want to try a different tutorial, first clean up the JWT authentication resources that you created in the previous [tutorial](/ai/tutorials/access-control/). If you do not remove these resources, you must include JWT tokens with the correct access in all subsequent curl requests to the AI API.

1. Delete the `HTTPListenerPolicy` resource that configures access logging.

   ```sh
   kubectl delete HTTPListenerPolicy log-provider -n {{< reuse "docs/snippets/ns-system.md" >}}
   ```

2. Update the `GatewayParameters` resource to remove the `stats.customLabels` section.

   {{% callout type="info" %}}
   When you apply this resource, the gateway proxy restarts to pick up the new stats configuration.
   {{% /callout %}}

   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.kgateway.dev/v1alpha1
   kind: GatewayParameters
   metadata:
     name: ai-gateway
     namespace: kgateway-system
     labels:
       app: ai-kgateway
   spec:
     kube:
       aiExtension:
         enabled: true
         ports:
         - name: ai-monitoring
           containerPort: 9092
       service:
         type: ClusterIP
   EOF
   ```

-->