---
title: Prompt enrichment
weight: 40
description: Effectively manage system and user prompts to improve LLM outputs.
---

Effectively manage system and user prompts to improve LLM outputs.

## About prompt enrichment

Prompts are basic building blocks for guiding LLMs to produce relevant and accurate responses. By effectively managing both system prompts, which set initial guidelines, and user prompts, which provide specific context, you can significantly enhance the quality and coherence of the model's outputs.

**System prompts** include initialization instructions, behavior guidelines, and background information. You use system prompts to set the foundation for the model's behavior. For example, you might instruct your LLM to respond to users with a polite tone, or according to specific organizational policies, with a system prompt such as "You are a helpful customer service assistant. Always be polite, and conclude conversations by asking customers to rate their experience."

**User prompts** encompass direct queries, sequential inputs, and task-oriented instructions. They ensure that the model responds accurately to specific user needs. This includes all interactions that end users have with your LLM, such as "Summarize this article in 3 key points" or "What kind of dinner can I make with these ingredients?".

Note that system and user prompts are not mutually exclusive, and can be combined in a single request to an LLM. For example, in the following steps, the prompt `Parse the unstructured text into CSV format: Seattle, Los Angeles, and Chicago are cities in North America. London, Paris, and Berlin are cities in Europe.` contains both system prompt and user prompt components.

## Before you begin

1. [Set up AI Gateway](../setup/).
2. [Authenticate to the LLM](../auth/).
3. {{< reuse "docs/snippets/ai-gateway-address.md" >}}

## Refactor LLM prompts

In the following example, you explore how to refactor system and user prompts to parse and turn unstructured text into valid CSV format.

1. Send a request to the AI API with the following prompt: `Parse the unstructured text into CSV format: Seattle, Los Angeles, and Chicago are cities in North America. London, Paris, and Berlin are cities in Europe.` Note that in this prompt, the system prompt is not separated from the user prompt.

   {{< tabs tabTotal="2" items="Cloud Provider LoadBalancer,Port-forward for local testing" >}}

   {{% tab tabName="Cloud Provider LoadBalancer" %}}
   ```sh
   curl "$INGRESS_GW_ADDRESS:8080/openai" -H content-type:application/json -d '{
       "model": "gpt-3.5-turbo",
       "messages": [
         {
           "role": "user",
           "content": "Parse the unstructured text into CSV format: Seattle, Los Angeles, and Chicago are cities in North America. London, Paris, and Berlin are cities in Europe."
         }
      ]
     }' | jq -r '.choices[].message.content'
   ```
   {{% /tab %}}

   {{% tab tabName="Port-forward for local testing" %}}
   ```sh
   curl "localhost:8080/openai" -H content-type:application/json -d '{
       "model": "gpt-3.5-turbo",
       "messages": [
         {
           "role": "user",
           "content": "Parse the unstructured text into CSV format: Seattle, Los Angeles, and Chicago are cities in North America. London, Paris, and Berlin are cities in Europe."
         }
      ]
     }' | jq -r '.choices[].message.content'
   ```
   {{% /tab %}}

   {{< /tabs >}}

   Verify that the request succeeds and that you get back a structured CSV response.
   ```
   City,Continent
   Seattle,North America
   Los Angeles,North America
   Chicago,North America
   London,Europe
   Paris,Europe
   Berlin,Europe
   ```

2. Refactor the request to improve readability and management of the prompt. In the following example, the instructions are separated from the unstructured text. The instructions are added as a system prompt and the unstructured text is added as a user prompt.

   {{< tabs tabTotal="2" items="Cloud Provider LoadBalancer,Port-forward for local testing" >}}

   {{% tab tabName="Cloud Provider LoadBalancer" %}}
   ```sh
   curl "$INGRESS_GW_ADDRESS:8080/openai" -H content-type:application/json -d '{
      "model": "gpt-3.5-turbo",
      "messages": [
        {
          "role": "system",
          "content": "Parse the unstructured text into CSV format."
        },
        {
          "role": "user",
          "content": "Seattle, Los Angeles, and Chicago are cities in North America. London, Paris, and Berlin are cities in Europe."
        }
      ]
    }' | jq -r '.choices[].message.content'
   ```
   {{< /tab >}}

   {{% tab tabName="Port-forward for local testing" %}}
   ```sh
   curl "localhost:8080/openai" -H content-type:application/json -d '{
      "model": "gpt-3.5-turbo",
      "messages": [
        {
          "role": "system",
          "content": "Parse the unstructured text into CSV format."
        },
        {
          "role": "user",
          "content": "Seattle, Los Angeles, and Chicago are cities in North America. London, Paris, and Berlin are cities in Europe."
        }
      ]
    }' | jq -r '.choices[].message.content'
   ```
   {{< /tab >}}

   {{< /tabs >}}

   Verify that you get back the same output as in the previous step.
   ```
   City, Continent  
   Seattle, North America  
   Los Angeles, North America  
   Chicago, North America  
   London, Europe  
   Paris, Europe  
   Berlin, Europe
   ```

## Append or prepend prompts

Use a TrafficPolicy resource to enrich prompts by appending or prepending system and user prompts to each request. This way, you can centrally manage common prompts that you want to add to each request.

1. Create a TrafficPolicy resource to enrich your prompts and configure additional settings. The following example prepends a system prompt of `Parse the unstructured text into CSV format.` to each request that is sent to the `openai` HTTPRoute.

   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.kgateway.dev/v1alpha1
   kind: TrafficPolicy
   metadata:
     name: openai-opt
     namespace: {{< reuse "docs/snippets/namespace.md" >}}
     labels:
       app: ai-gateway
   spec:
     targetRefs:
     - group: gateway.networking.k8s.io
       kind: HTTPRoute
       name: openai
     ai:
       promptEnrichment:
         prepend:
         - role: SYSTEM
           content: "Parse the unstructured text into CSV format."
   EOF
   ```

2. Send a request without a system prompt. Although the system prompt instructions are missing in the request, the unstructured text in the user prompt is still transformed into structured CSV format. This is because the system prompt is automatically prepended from the TrafficPolicy resource before it is sent to the LLM provider.

   {{< tabs tabTotal="2" items="Cloud Provider LoadBalancer,Port-forward for local testing" >}}

   {{% tab tabName="Cloud Provider LoadBalancer" %}}
   ```sh
   curl "$INGRESS_GW_ADDRESS:8080/openai" -H content-type:application/json -d '{
      "model": "gpt-3.5-turbo",
      "messages": [
        {
          "role": "user",
          "content": "The recipe called for eggs, flour and sugar. The price was $5, $3, and $2."
        }
      ]
    }' | jq -r '.choices[].message.content'
   ```
   {{< /tab >}}

   {{% tab tabName="Port-forward for local testing" %}}
   ```sh
   curl "localhost:8080/openai" -H content-type:application/json -d '{
      "model": "gpt-3.5-turbo",
      "messages": [
        {
          "role": "user",
          "content": "The recipe called for eggs, flour and sugar. The price was $5, $3, and $2."
        }
      ]
    }' | jq -r '.choices[].message.content'
   ```
   {{< /tab >}}

   {{< /tabs >}}

   Example output:
   ```
   Item, Price
   Eggs, $5
   Flour, $3
   Sugar, $2
   ```

## Overwrite settings on the route level

To overwrite a setting that you added to a TrafficPolicy resource, you simply include that setting in your request.

1. Send a request to the AI API and include a custom system prompt that instructs the API to transform unstructured text into JSON format.

   {{< tabs tabTotal="2" items="Cloud Provider LoadBalancer,Port-forward for local testing" >}}

   {{% tab tabName="Cloud Provider LoadBalancer" %}}
   ```sh
   curl "$INGRESS_GW_ADDRESS:8080/openai" -H content-type:application/json -d '{
      "model": "gpt-3.5-turbo",
      "messages": [
        {
          "role": "system",
          "content": "Parse the unstructured content and give back a JSON format"
        },
        {
          "role": "user",
          "content": "The recipe called for eggs, flour and sugar. The price was $5, $3, and $2."
        }
      ]
    }' | jq -r '.choices[].message.content'
   ```
   {{< /tab >}}

   {{% tab tabName="Port-forward for local testing" %}}
   ```sh
   curl "localhost:8080/openai" -H content-type:application/json -d '{
      "model": "gpt-3.5-turbo",
      "messages": [
        {
          "role": "system",
          "content": "Parse the unstructured content and give back a JSON format"
        },
        {
          "role": "user",
          "content": "The recipe called for eggs, flour and sugar. The price was $5, $3, and $2."
        }
      ]
    }' | jq -r '.choices[].message.content'
   ```
   {{< /tab >}}

   {{< /tabs >}}

   Example output:
   ```json
   {
     "recipe": [
       {
         "ingredient": "eggs",
         "price": "$5"
       },
       {
         "ingredient": "flour",
         "price": "$3"
       },
       {
         "ingredient": "sugar",
         "price": "$2"
       }
     ]
   }
   ```

2. Send another request. This time, you do not include a system prompt. Because the default setting in the TrafficPolicy resource is applied, the unstructured text is returned in CSV format.

   {{< tabs tabTotal="2" items="Cloud Provider LoadBalancer,Port-forward for local testing" >}}

   {{% tab tabName="Cloud Provider LoadBalancer" %}}
   ```sh
   curl "$INGRESS_GW_ADDRESS:8080/openai" -H content-type:application/json -d '{
      "model": "gpt-3.5-turbo",
      "messages": [
        {
          "role": "user",
          "content": "The recipe called for eggs, flour and sugar. The price was $5, $3, and $2."
        }
      ]
    }' | jq -r '.choices[].message.content'
   ```
   {{< /tab >}}

   {{% tab tabName="Port-forward for local testing" %}}
   ```sh
   curl "localhost:8080/openai" -H content-type:application/json -d '{
      "model": "gpt-3.5-turbo",
      "messages": [
        {
          "role": "user",
          "content": "The recipe called for eggs, flour and sugar. The price was $5, $3, and $2."
        }
      ]
    }' | jq -r '.choices[].message.content'
   ```
   {{< /tab >}}

   {{< /tabs >}}

   Example output: 
   ```
   Item, Price
   Eggs, $5
   Flour, $3
   Sugar, $2
   ```


## Cleanup

{{< reuse "docs/snippets/cleanup.md" >}}

```shell
kubectl delete TrafficPolicy -n {{< reuse "docs/snippets/namespace.md" >}} -l app=ai-gateway
```

## Next

Explore how to set up [prompt guards](../prompt-guards/) to block unwanted requests and mask sensitive data.
