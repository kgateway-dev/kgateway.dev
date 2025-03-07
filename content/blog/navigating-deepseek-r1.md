---
title: Navigating DeepSeek R1, Security Concerns, and Guardrails
toc: false
publishDate: 2025-01-29T00:00:00-00:00
author: Christian Posta
---

DeepSeek R1 is a new model from Chinese startup DeepSeek released on January 20th with impressive reasoning ability which rivals (or beats) the existing leading reasoning models (ie, o1 from OpenAI). It is available from a few different providers but from my perspective, the most interesting thing is that it's open source and is available in distilled form with similar performance (ie, distilled to Qwen or Llama models, which can be self-hosted).

One question we see (from our users as well as the broader public) is "is DeepSeek safe?". Sure, DeepSeek is hosted by a Chinese company, so most organizations (and the country) may have some questions about that, but the real concern is about your data, what happens to it, what should be sent or not sent. And in that case, it doesn't matter if it's DeepSeek or any other public LLM provider. As an enterprise organization, you have to be careful what you do with your sensitive data. You need tight control and audit trails for your data or risk significant harm to your company with slip ups.

This blog covers some ways to enable tighter control and audit for your interactions with DeepSeek.

## Establishing Control

Application developers building apps that leverage LLMs are the first line of defense when establishing control over LLM usage. These developers must be responsible for what data they send or receive in terms of detecting, scrubbing, or outright limiting it. They can adopt content safety or guardrail systems to help with that. They must also be responsible for securely connecting to any LLMs they use. This includes keeping client IDs, secrets, and authorization tokens safe. Code reviews and responsible coding can help here, but this is just one line of defense.

{{< reuse-image src="blog/navigating-deepseek-1.png" >}}

Whenever you consider security and compliance, you must think in terms of "defense in depth" as organizations now require having more options to control these LLM interactions.

Establishing an intermediary that acts as an out-of-application way to observe, audit, and control these interactions is crucial. This can be done with a piece of middleware like an API gateway or a more dedicated AI gateway. These AI gateways can implement security, WAF (IP-based controls), and further apply policy around what LLMs can be used, securing their connections, and most importantly, placing a second line of defense for [guardrails](https://towardsdatascience.com/safeguarding-llms-with-guardrails-4f5d9f57cff2). These guardrails can inspect the request and do an analysis to determine whether or not they should be allowed (or conversely, inspect a response from an LLM and determine whether it should be allowed). 

This intermediary allows an organization to implement a ["kill-switch"](https://en.wikipedia.org/wiki/Internet_kill_switch) type architecture should a vulnerability be discovered. That is, it would be easier to apply new guardrails quickly at this intermediary than it would be to go to all respective application teams and ask them to update their code.

{{< reuse-image src="blog/navigating-deepseek-2.png" >}}

In the case of DeepSeek R1, we also have the option to take the open source model ([or one of it's distilled variants](https://ollama.com/library/deepseek-r1)) and run it ourselves, that is, in our datacenters/VPC, and under our control. We will still want guardrails in place, but running it ourselves means the data being sent to/from will be under our control. We see some of our larger enterprise customers doing this by building out their own GPU infrastructure to run these types of models.

{{< reuse-image src="blog/navigating-deepseek-3.png" width="1000px" >}}

## Putting this into Practice

We can use an AI Gateway like [kgateway](https://github.com/kgateway-dev/kgateway/pull/10495/files) to help implement these intermediary controls for security, prompt guarding, and routing/failover to either the public DeepSeek R1 or to our own self-hosted R1 model. KGateway is a powerful, mature AI gateway built on top of the CNCF Envoy Proxy project. 

{{< reuse-image src="blog/navigating-deepseek-4.png" width="1000px" >}}

To demonstrate this, we will deploy the AI gateway on GKE along with a locally hosted deepseek-r1:7b model. We will use the NVIDIA GPU operator to configure the GPUs and `containerd` so that GPU enabled workloads can take advantage of the accelerators. 

We will see how we can use powerful security and guardrail capabilities from kgateway to implement control and observability when calling Deepseek models whether they are publicly hosted or locally/self hosted. 

Check out this 5 minute demo to see the following details ([source code available](https://github.com/christian-posta/scripted-solo-demos/tree/master/deepseek-blog)):

* Running a self hosted deepseek-r1 7B model on GKE with [NVIDIA L4 GPUs](https://cloud.google.com/compute/docs/gpus#l4-gpus) and NVIDIA [GPU Operator](https://github.com/NVIDIA/gpu-operator)
* Running a mature, powerful [OSS AI gateway](https://github.com/kgateway-dev/kgateway/pull/10495/files) capable of applying guardrails as an intermediary
* Securing traffic to Deepseek using your own security mechanisms instead of provider API keys
* Routing/splitting traffic to local Deepseek instead of public one without clients knowing

## Conclusion

Deepseek is a powerful model, but just like with any model hosted by a provider, you should be very wary of what data and information you're sending to it. Deepseek may be safe, but who knows? Who knows about any LLM model provider? You should implement strict security, observability, and guardrail systems before you use any LLM provider. An [AI Gateway like kgateway](https://www.solo.io/products/gloo-ai-gateway) helps implement a safe "kill-switch" style architecture which gives you defense in depth. 
