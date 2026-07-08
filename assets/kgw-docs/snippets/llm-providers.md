### Cloud providers {#cloud-providers}

Kgateway supports the following AI cloud providers:

* [Anthropic](https://platform.claude.com/docs/en/release-notes/overview)
* [Azure OpenAI](https://learn.microsoft.com/en-us/azure/foundry/)
* [Gemini](https://ai.google.dev/gemini-api/docs)
* [OpenAI](https://platform.openai.com/). You can also use `openai` support for LLM providers that use the OpenAI API, such as [DeepSeek](https://api-docs.deepseek.com) and [Mistral](https://docs.mistral.ai/).
* [Vertex AI](https://docs.cloud.google.com/gemini-enterprise-agent-platform)

### Local providers {#local-providers}

You can use kgateway with a local LLM provider, such as the following common options:

* [Ollama]({{< link-hextra path="/ai/ollama/" >}}) for local LLM development.
* [Gateway API Inference Extension project](https://gateway-api-inference-extension.sigs.k8s.io/) to route requests to local LLM workloads that run in your cluster.
