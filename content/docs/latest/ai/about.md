---
title: About AI Gateway
weight: 5
description: Unleash developer productivity and accelerate AI innovation with AI Gateway.  
---

Unleash developer productivity and accelerate AI innovation with AI Gateway.

## About LLMs {#about-llms}

A Large Language Model (LLM) is a type of artificial intelligence (AI) model that is designed to understand, generate, and manipulate human language in a way that is both coherent and contextually relevant. In recent years, the number of LLM providers or open source LLM projects increased significantly, such as OpenAI, Llama2, and Mistral. These providers distribute LLMs in various ways, such as through APIs and cloud-based platforms.

Because the AI technology landscape is fragmented, access to LLMs can vary a lot. Developers must learn each AI API and AI platform, and implement provider-specific code so that the app can consume the AI services of each LLM provider. This redundancy can significantly decrease developer efficiency and make it difficult to scale and upgrade the app or integrate it with other platforms.

## About AI Gateway {#about-ai-gateway}

AI Gateway unleashes developer productivity and accelerates AI innovation by providing a unified API interface that developers can use to access and consume AI services from multiple LLM providers. Because the API is part of the gateway proxy, you can leverage and apply additional traffic management, security, and resiliency policies to the requests to your LLM provider. This set of policies allows you to centrally govern, secure, control, and audit access to your LLM providers.

Learn more about the key capabilities of AI Gateway.

### Self-contained deployment

The AI Gateway control plane and data plane can be provisioned inside your cluster network boundaries with no dependency on external resources such as a SaaS provider. This way, you can have isolated governance and control over your LLM usage.

### Multi-provider support

AI Gateway supports multiple LLM providers, including OpenAI, Anthropic, and Gemini. For the full list, see the [Supported LLM providers](#supported-llm-providers) section. 

### Model traffic management

With AI Gateway, you can manage traffic to different models across LLM providers. Traffic management includes features such as the following:

* **A/B model testing**: Perform controlled experiments between two or more model versions. This feature allows users to evaluate model quality and performance with selective cohorting and routing to determine which model performs better for specific use cases or prompts.
* **Canary model rollout**: Deploy a new model version to a subset of traffic while continuing to route the majority of traffic to an existing model. This rollout pattern helps ensure stability and correctness of a new model before a full rollout.
* **Model failover**: Failover is a way to keep services running smoothly by automatically switching to a backup system when the main one fails or becomes unavailable. With AI Gateway, you can set up failover for the models of the LLM providers that you want to prioritize. If the main model from one provider goes down, slows, or has any issue, the system quickly switches to a backup model from that same provider. This keeps the service running without interruptions.

### Prompt enrichment

Prompts are basic building blocks for guiding LLMs to produce relevant and accurate responses. By effectively managing both system prompts, which set initial guidelines, and user prompts, which provide specific context, you can significantly enhance the quality and coherence of the model's outputs. AI Gateway allows you to pre-configure and refactor system and user prompts, extract common AI provider settings so that you can reuse them across requests, dynamically append or prepend prompts to where you need them, and overwrite default settings on a per-route level.

### Prompt guards

Prompt guards are mechanisms that ensure that prompt-based interactions with a language model are secure, appropriate, and aligned with the intended use. These mechanisms help to filter, block, monitor, and control LLM inputs and outputs to filter offensive content, prevent misuse, and ensure ethical and responsible AI usage. With AI Gateway, you can set up prompt guards to block unwanted requests to the LLM provider and mask sensitive data.

### Chat streaming

AI Gateway supports chat streaming, which allows the LLM to stream out tokens as they are generated. The way that chat streaming is determined varies by AI provider.

* OpenAI and most AI providers: Most providers send the `is-streaming` boolean as part of the request to determine whether or not a request should receive a streamed response. 
* Google Gemini and Vertex AI: In contrast, the Gemini and Vertex AI providers change the path to determine streaming, such as the `streamGenerateContent` segment of the path in the Vertex AI streaming endpoint `https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:streamGenerateContent?key=<key>`. To prevent the path you defined in your HTTPRoute from being overwritten by this streaming path, you instead indicate chat streaming for Gemini and Vertex AI by setting `spec.options.ai.routeType=CHAT_STREAMING` in your TrafficPolicies resource.

## Supported LLM providers {#supported-llm-providers}

{{< reuse "/docs/snippets/kgateway-capital.md" >}} supports the following LLM providers. For more information, refer to the [LLM providers](../cloud-providers/) guide.

{{< reuse "docs/snippets/llm-providers.md" >}}
