### Cloud providers {#cloud-providers}

Kgateway supports the following AI cloud providers:

* [Anthropic](https://docs.anthropic.com/en/release-notes/api)
* [Azure OpenAI](https://learn.microsoft.com/en-us/azure/ai-services/openai/)
* [Gemini](https://ai.google.dev/gemini-api/docs)
* [OpenAI](https://platform.openai.com/docs/overview). You can also use `openai` support for LLM providers that use the OpenAI API, such as [DeepSeek](https://api-docs.deepseek.com/) and [Mistral](https://docs.mistral.ai/getting-started/quickstart/).
* [Vertex AI](https://cloud.google.com/vertex-ai/docs)

### Local providers {#local-providers}

You can use kgateway with a local LLM provider, such as the following common options:

* [Ollama](/docs/ai/ollama/) for local LLM development.
* [Gateway API Inference Extension project](/docs/integrations/inference-extension/) to route requests to local LLM workloads that run in your cluster.