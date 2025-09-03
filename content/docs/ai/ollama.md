---
title: Ollama for local LLMs
weight: 15
description: Set up Ollama as a local LLM provider with AI Gateway.
---

Instead of a cloud LLM provider, you might want to use a local LLM provider such as [Ollama](https://ollama.com/) for local development. 

## Before you begin

1. [Set up AI Gateway](../setup/).

2. As part of the AI Gateway setup, make sure that you set up the GatewayParameters resource to use a NodePort service.
   
   ```sh
   kubectl get GatewayParameters ai-gateway -n {{< reuse "docs/snippets/namespace.md" >}} -o jsonpath='{.items[*].spec.kube.service.type}'
   ```

   Example output:

   ```
   NodePort
   ```

## Start Ollama locally {#ollama-setup}

Start running an Ollama server as a local LLM provider.

1. Find your local IP address.

   {{< tabs items="macOS, Unix-based systems, Windows" tabTotal="3" >}}
   {{% tab tabName="macOS" %}}
   ```sh
   ipconfig getifaddr en0
   ```
   {{% /tab %}}
   {{% tab tabName="Unix-based systems" %}}
   ```sh
   ifconfig
   ```
   {{% /tab %}}
   {{% tab tabName="Windows" %}}
   ```sh
   ipconfig
   ```
   {{% /tab %}}
   {{< /tabs >}}
   
   Example output: Note the `inet 192.168.1.100` address.

   ```
   inet 192.168.1.100 netmask 255.255.255.0 broadcast 192.168.1.255
   ```

2. Set the IP address as an environment variable.

   ```sh
   export OLLAMA_HOST=192.168.1.100
   ```

3. Start your local LLM provider.

   ```sh
   ollama serve
   ```

   Example output:

   ```text
   time=2025-05-21T12:33:42.433+08:00 level=INFO source=routes.go:1205 msg="server config"
   env="map[HTTPS_PROXY: HTTP_PROXY: NO_PROXY: OLLAMA_CONTEXT_LENGTH:4096
   OLLAMA_DEBUG:INFO OLLAMA_FLASH_ATTENTION:false OLLAMA_GPU_OVERHEAD:0
   OLLAMA_HOST:http://192.168.181.210:11434 OLLAMA_KEEP_ALIVE:5m0s OLLAMA_KV_CACHE_TYPE:
   OLLAMA_LLM_LIBRARY: OLLAMA_LOAD_TIMEOUT:5m0s OLLAMA_MAX_LOADED_MODELS:0
   OLLAMA_MAX_QUEUE:512 OLLAMA_MODELS:/Users/zhengkezhou/.ollama/models
   OLLAMA_MULTIUSER_CACHE:false OLLAMA_NEW_ENGINE:false OLLAMA_NOHISTORY:false
   OLLAMA_NOPRUNE:false OLLAMA_NUM_PARALLEL:0 OLLAMA_ORIGINS:[http://localhost https://localhost
   http://localhost:* https://localhost:* http://127.0.0.1 https://127.0.0.1 http://127.0.0.1:* https://127.0.0.1:*
   http://0.0.0.0 https://0.0.0.0 http://0.0.0.0:* https://0.0.0.0:* app://* file://* tauri://* vscode-webview://*
   vscode-file://*] OLLAMA_SCHED_SPREAD:false http_proxy: https_proxy: no_proxy:]"
   time=2025-05-21T12:33:42.436+08:00 level=INFO source=images.go:463 msg="total blobs: 12"
   time=2025-05-21T12:33:42.437+08:00 level=INFO source=images.go:470 msg="total unused blobs removed: 0"
   time=2025-05-21T12:33:42.437+08:00 level=INFO source=routes.go:1258 msg="Listening on 192.168.181.210:11434 (version 0.7.0)"
   time=2025-05-21T12:33:42.478+08:00 level=INFO source=types.go:130 msg="inference compute" id=0 library=metal variant="" compute="" driver=0.0 name="" total="16.0 GiB" available="16.0 GiB"
   ```

## Set up Ollama with AI Gateway {#ollama-ai-gateway}

To use Ollama with AI Gateway, create Backend and HTTPRoute resources.

1. Create the Backend resource so that you can route requests to the Ollama server.

   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.kgateway.dev/v1alpha1
   kind: Backend
   metadata:
     labels:
       app: ai-gateway
     name: ollama
     namespace: {{< reuse "docs/snippets/namespace.md" >}}
   spec:
     type: AI
     ai:
       llm:
         hostOverride:
           host: $OLLAMA_HOST # replace with your IP address
           port: 11434
         provider:
           openai:
             model: "llama3.2" # replace with your model
             authToken:
               kind: Inline
               inline: "$TOKEN"
   EOF
   ```
   
   {{< reuse "docs/snippets/review-table.md" >}}

   | Setting | Description |
   |---------|-------------|
   | `host` | Your local IP address from the previous step (`$OLLAMA_HOST`). |
   | `port` | The port of your local LLM provider (default port 11434 for Ollama). |
   | `authToken` | Although authentication is not required for your local Ollama server, the `authToken` field is required to create an AI Backend in kgateway. You can provide any placeholder value for the inline token. |
   | `model` | The Ollama model you want to use, such as `llama3.2`. |

2. Create an HTTPRoute resource that routes incoming traffic to the Backend. The following example sets up a route on the `ollama` path to the Backend you previously created. The `URLRewrite` filter rewrites the path from `ollama` to the API path you want to use in the LLM provider, `/v1/models`.

   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.networking.k8s.io/v1
   kind: HTTPRoute
   metadata:
     name: ollama
     namespace: {{< reuse "docs/snippets/namespace.md" >}}
     labels:
       app: ai-gateway
   spec:
     parentRefs:
       - name: ai-gateway
         namespace: {{< reuse "docs/snippets/namespace.md" >}}
     rules:
     - matches:
       - path:
           type: PathPrefix
           value: /ollama
       filters:
       - type: URLRewrite
         urlRewrite:
           path:
             type: ReplaceFullPath
             replaceFullPath: /v1/models
       backendRefs:
       - name: ollama
         namespace: {{< reuse "docs/snippets/namespace.md" >}}
         group: gateway.kgateway.dev
         kind: Backend
   EOF
   ```

3. For local testing: Port forward the AI Gateway service.

   ```sh
   kubectl port-forward svc/ai-gateway 8080:8080 -n {{< reuse "docs/snippets/namespace.md" >}}
   ``` 

4. Send a request to the Ollama server that you started in the previous section. Verify that the request succeeds and that you get back a response from the chat completion API.

    ```bash
    curl -v "localhost:8080/ollama" \
        -H "Content-Type: application/json" \
        -d '{
            "model": "llama3.2",
            "messages": [
                {
                    "role": "system",
                    "content": "You are a helpful assistant."
                },
                {
                    "role": "user",
                    "content": "Hello!"
                }
            ]
        }' | jq
    ```

    Example output:

    ```json
    {
      "id": "chatcmpl-534",
      "object": "chat.completion",
      "created": 1747805667,
      "model": "llama3.2",
      "system_fingerprint": "fp_ollama",
      "choices": [
        {
          "index": 0,
          "message": {
            "role": "assistant",
            "content": "It's nice to meet you. Is there something I can help you with, or would you like to chat?"
          },
          "finish_reason": "stop"
        }
      ],
      "usage": {
        "prompt_tokens": 33,
        "completion_tokens": 24,
        "total_tokens": 57
      }
    }
    ```

## Next

Now that you can send requests to an LLM provider, explore the other AI Gateway features.

{{< cards >}}
  {{< card link="../failover" title="Model failover" >}}
  {{< card link="../functions" title="Function calling" >}}
  {{< card link="../prompt-enrichment" title="Prompt enrichment" >}}
  {{< card link="../prompt-guards" title="Prompt guards" >}}
  {{< card link="../observability" title="AI Gateway metrics" >}}
{{< /cards >}}