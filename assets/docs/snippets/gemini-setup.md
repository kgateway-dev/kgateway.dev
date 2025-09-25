1. Save your Gemini API key as an environment variable. To retrieve your API key, [log in to the Google AI Studio and select **API Keys**](https://aistudio.google.com/app/apikey).

   ```bash
   export GOOGLE_KEY=<your-api-key>
   ```

2. Create a secret to authenticate to Google. 

   ```yaml
   kubectl apply -f - <<EOF
   apiVersion: v1
   kind: Secret
   metadata:
     name: google-secret
     namespace: {{< reuse "docs/snippets/namespace.md" >}}
     labels:
       app: agentgateway
   type: Opaque
   stringData:
     Authorization: $GOOGLE_KEY
   EOF
   ```

3. Create a Backend resource to define the Gemini destination.

   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.kgateway.dev/v1alpha1
   kind: Backend
   metadata:
     labels:
       app: agentgateway
     name: google
     namespace: {{< reuse "docs/snippets/namespace.md" >}}
   spec:
     ai:
       llm:
        gemini:
             apiVersion: v1beta
             authToken:
               kind: SecretRef
               secretRef:
                 name: google-secret
             model: gemini-1.5-flash-latest
     type: AI
   EOF
   ```

   {{< reuse "docs/snippets/review-table.md" >}}

   | Setting      | Description                                                                                                                                                                                                                                                                                                           |
   | ------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
   | `gemini`     | The Gemini AI provider.                                                                                                                                                                                                                                                                                               |
   | `apiVersion` | The API version of Gemini that is compatible with the model that you plan to use. In this example, you must use `v1beta` because the `gemini-1.5-flash-latest` model is not compatible with the `v1` API version. For more information, see the [Google AI docs](https://ai.google.dev/gemini-api/docs/api-versions). |
   | `authToken`  | The authentication token to use to authenticate to the LLM provider. The example refers to the secret that you created in the previous step.                                                                                                                                                                          |
   | `model`      | The model to use to generate responses. In this example, you use the `gemini-1.5-flash-latest` model. For more models, see the [Google AI docs](https://ai.google.dev/gemini-api/docs/models).                                                                                                                        |

4. Create an HTTPRoute resource to route requests to the Gemini backend. Note that {{< reuse "/docs/snippets/kgateway.md" >}} automatically rewrites the endpoint that you set up (such as `/gemini`) to the appropriate chat completion endpoint of the LLM provider for you, based on the LLM provider that you set up in the Backend resource.

   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.networking.k8s.io/v1
   kind: HTTPRoute
   metadata:
     name: google
     namespace: {{< reuse "docs/snippets/namespace.md" >}}
     labels:
       app: agentgateway
   spec:
     parentRefs:
       - name: agentgateway
         namespace: {{< reuse "docs/snippets/namespace.md" >}}
     rules:
     - matches:
       - path:
           type: PathPrefix
           value: /gemini
       backendRefs:
       - name: google
         namespace: {{< reuse "docs/snippets/namespace.md" >}}
         group: gateway.kgateway.dev
         kind: Backend
   EOF
   ```

5. Send a request to the LLM provider API. Verify that the request succeeds and that you get back a response from the chat completion API.

   {{< tabs tabTotal="2" items="Cloud Provider LoadBalancer,Port-forward for local testing" >}}
   {{% tab tabName="Cloud Provider LoadBalancer" %}}

   ````sh
   curl -vik "$INGRESS_GW_ADDRESS:8080/gemini" -H content-type:application/json  -d '{
     "model": "",
     "messages": [
      {"role": "user", "content": "Explain how AI works in simple terms."}
    ]
   }'
   {{% /tab %}}
   {{% tab tabName="Port-forward for local testing" %}}
   ```sh
   curl -vik "localhost:8080/gemini" -H content-type:application/json  -d '{
     "model": "",
     "messages": [
      {"role": "user", "content": "Explain how AI works in simple terms."}
    ]
   }'
   ````

   {{% /tab %}}
   {{< /tabs >}}

   Example output:

   ```json
   {"id":"aGLEaMjbLp6p_uMPopeAoAc",
   "choices":
     [{"index":0,"message":{
         "content":"Imagine teaching a dog a trick.  You show it what to do, reward it when it's right, and correct it when it's wrong.  Eventually, the dog learns.\n\nAI is similar.  We \"teach\" computers by showing them lots of examples.  For example, to recognize cats in pictures, we show it thousands of pictures of cats, labeling each one \"cat.\"  The AI learns patterns in these pictures – things like pointy ears, whiskers, and furry bodies – and eventually, it can identify a cat in a new picture it's never seen before.\n\nThis learning process uses math and algorithms (like a secret code of instructions) to find patterns and make predictions.  Some AI is more like a dog learning tricks (learning from examples), and some is more like following a very detailed recipe (following pre-programmed rules).\n\nSo, in short: AI is about teaching computers to learn from data and make decisions or predictions, just like we teach dogs tricks.\n",
         "role":"assistant"
         },
      "finish_reason":"stop"
      }],
    "created":1757700714,
    "model":"gemini-1.5-flash-latest",
    "object":"chat.completion",
    "usage":{
        "prompt_tokens":8,
        "completion_tokens":205,
        "total_tokens":213
        }
   }
   ```