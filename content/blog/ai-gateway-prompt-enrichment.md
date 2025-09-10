---
title: Get Better Results from your LLM with AI Gateway Prompt Enrichment
toc: false
publishDate: 2025-05-02T00:00:00-00:00
author: Art Berger
excludeSearch: true
---

Prompting is more than just typing something into a chat and hoping the AI understands you. If you're working with large language models (LLMs) through an API gateway—or managing a system that does—it pays to be deliberate about how prompts are structured and enriched.

## About prompting

In this blog post, we'll explore how managing system and user prompts with kgateway can improve the quality of responses you get from your LLM. Whether you're building a customer support assistant or enabling internal tools powered by AI, prompt enrichment is a practical tool for getting consistent, accurate, and helpful results.

### What is prompt enrichment?

Prompt enrichment is the process of improving the instructions given to a language model by managing and combining different types of input in two main ways:

- **System prompts**: These are hidden from the end user. Think of them as behind-the-scenes instructions that set the tone, personality, or policies the AI should follow in its response.

- **User prompts**: These come directly from the client that interacts with the system—an employee, a customer, or a tool making a request.

With kgateway, you can templatize rules for system and user prompts, or "enrich" the final prompt sent to the LLM.

### Why good prompts matter

LLMs are sensitive to phrasing, structure, and context. A good prompt can mean the difference between a vague response and a spot-on answer.

With AI Gateway prompt enrichment, you can enforce best practices for prompting automatically. Such best practices include:

- Stating the intended audience, purpose, subject, and other context of the prompt
- Structuring the response according to a template, genre expectations, or other instructions such as "format into a CSV table"
- Asking the model to qualify certainty or cite sources

Such prompt enrichment improves the user experience (UX) by helping your products:

- Maintain consistency across user sessions
- Follow brand voice, tone, and style guidelines
- Ensure compliance to organizational standards

## Example scenario

Let's take a look at how we can set up prompt enrichment with kgateway. As shown in Figure 1, kgateway lets you configure prompts such as by providing system instructions to a request before it reaches the LLM.

*Figure 1: Example of prompt enrichment. Source in [Excalidraw](https://app.excalidraw.com/s/AKnnsusvczX/9uvNK3rCBeK).*

{{< reuse-image src="blog/ai-gateway-prompt-enrichment-1.png" width="750px" >}}

### Before you begin

Make sure that you have a basic kgateway environment set up with AI Gateway and your LLM provider. If you don't, check out these docs:

- [Get started with kgateway](https://kgateway.dev/docs/quickstart/)
- [Set up AI Gateway](https://kgateway.dev/docs/ai/setup/)
- [Authenticate to the LLM provider](https://kgateway.dev/docs/ai/auth/)

### Step 1: Append a system prompt

Create a TrafficPolicy resource to enrich your prompts and configure additional settings. The following example prepends a system prompt of `Parse the unstructured text into CSV format` to each request that is sent to the `openai` HTTPRoute.

```yaml
kubectl apply -f- <<EOF
apiVersion: gateway.kgateway.dev/v1alpha1
kind: TrafficPolicy
metadata:
  name: openai-opt
  namespace: kgateway-system
  labels:
    app: ai-kgateway
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

### Step 2: Send a test request

As a client, send a request without a system prompt.

```yaml
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

Although the system prompt instructions are not in the request, the unstructured text in the user prompt is still transformed into structured CSV format. This is because the system prompt is automatically prepended by AI Gateway before it is sent to the LLM provider.

```
Item, Price
Eggs, $5
Flour, $3
Sugar, $2
```

## Conclusion

Good work! You played around with prepending system instructions to your prompts with a simple kgateway TrafficPolicy. Now you're ready to feed the TrafficPolicy CRD to your favorite LLM and have it help you craft the perfect prompts for your AI-powered apps! 😂

For more information, try out [AI Gateway](https://www.solo.io/resources/lab/kgateway-ai-lab-prompt-enrichment) in our free hands-on labs, get involved in the [community](https://github.com/kgateway-dev/kgateway), and let us know how it goes.