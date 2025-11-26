{{< reuse "docs/snippets/agentgateway-capital.md" >}} provides seamless integration with various Large Language Model (LLM) providers. This way, you can consume AI services through a unified interface while still maintain flexibility in the providers that you use.

## What is an LLM?

Large Language Model (LLMs) are very large, deep learning models that are pre-trained on massive amounts of unlabeled and self-supervised data, often containing billions of words. LLMs extract meanings from a sequence of text and can understand the relationship between words and phrases in it. Based on this understanding, the LLM can then predict and generate natural language, and perform related tasks, such as answering questions, summarizing text, translating between languages, or writing content. LLMs can be fine-tuned on a smaller, more specific data set so that it can perform a more specific task more accurately. 

While LLMs were originally designed to be trained on text and natural language, they are now becoming multimodal, supporting different media types, such as images and videos. 

## Common problems with LLM consumption

When adopting an LLM on an enterprise-level, you typically run into the following issues: 

* **Data leakage and privacy**: When interacting with LLMs, it is essential to comply with federal laws and to not leak any PII (personally identifiable information) or other sensitive information in prompts. For example, users might enter personal credit card or customer related information, such as account numbers and names. Attackers might also trick the model into revealing previous user data that is still stored in the context. To prevent sensitive information from leaking to the LLM provider, prompt guards must be in place that help to fitler, block, monitor, and control LLM inputs and outputs to find offensive content, prevent misuse, and ensure ethical and responsible AI usage.

* **Cost controls**: Compared to traditional APIs, LLM queries are long-running, meaning the LLM must parse through its large data set iteratively to compute one token at a time. All tokens must then be summarized to generate a prediction. Given the large amounts of data that the LLM parses, GPUs are required to run LLMs efficently, which are costly to run and maintain. Limiting the amount of tokens that can be used and monitoring token consumption are critical to keep costs to a minimum. 

* **Fan-out patterns**: LLMs are limited by static training data. This limitation can make seemingly simple questions difficult to answer. For example, answering a simple question, such as `What is the weather today?` requires the LLM to have access to several real-time information, such as the location, time, and weather forecast. Integrating LLMs with other MCP servers and agents to perform these tasks becomes essential to accurately answer questions of this nature. 

* **Security**: To protect your LLM from being consumed by unauthorized users, you typically want to authenticate with the LLM before you start sending requests. Managing credentials, such as API keys, and monitoring the traffic to the LLM becomes essential to protect access to the LLM . 

* **Scalability and reliability**: When relying on an LLM to perform specific tasks in your environment, you must put measures in place that prevent your applications from failing, being overwhelmed, or performing inefficiently. This includes retries and timeouts, request rate limiting, and multi-model failovers. 



## Supported providers

Review the following table for a list of supported LLM providers.


| Provider                  | Chat Completions | Streaming |
|---------------------------|:---------------:|:---------:|
| [OpenAI](../providers/openai)          | ✅           | ✅         |
| [Vertex AI](../providers/vertex)      | ✅           | ✅         |
| [Gemini](../providers/gemini)          | ✅           | ✅         |
| [Amazon Bedrock](../providers/bedrock) | ✅           | ✅         |
| [Anthropic](../providers/anthropic)    | ✅           | ✅         |
| [OpenAI compatible](../providers/openai-compatible)    | ✅           | ✅         |
| [Azue OpenAI](../providers/azureopenai)    | ✅           | ✅         |

* Chat Completions: support for the `/v1/chat/completions` API.
* Streaming: support for streaming (`"stream": true` in the completions request)

