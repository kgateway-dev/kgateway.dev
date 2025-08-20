---
title: Deep Dive into the Gateway API Inference Extension
toc: false
publishDate: 2025-04-01T00:00:00-00:00
author: Christian Posta
excludeSearch: true
---

Running AI inference workloads on Kubernetes has some unique characteristics and challenges, and the Gateway API Inference Extension project aims to solve some of those challenges. I recently wrote about these new capabilities [introduced in kgateway v2.0.0](https://kgateway.dev/blog/smarter-ai-reference-kubernetes-gateway-api/). In this blog we’ll take a deep dive into how it all works.

Most people think of request routing on Kubernetes in terms of the Gateway API, Ingress or Service Mesh (we'll call it L7 router). All of those implementations work very similarly: you specify some routing rules that evaluate attributes of a request (headers, path, etc) and the L7 router makes a decision about which backend endpoint to send to. This is done with some kind of load balancing algorithm ([round robin, least request, ring hash, zone aware, priority,](https://www.envoyproxy.io/docs/envoy/latest/intro/arch_overview/upstream/load_balancing/load_balancing) etc)

`{{< reuse-image src="blog/deep-dive-inf-1.png" width="750px" >}}

Traditional load balancing algorithms may not be well-suited for AI/LLM model backends. Unlike typical stateless web APIs, GPU-backed LLMs operate differently and require a more nuanced approach – which can save a lot of money. What if we could leverage real-time metrics from the models and GPUs to make smarter routing and load-balancing decisions? For instance, if a backend LLM has already loaded specific fine-tuned (LoRA) adapters, requests for those models should be routed there rather than to endpoints that lack the adapter—avoiding unnecessary GPU overhead from loading it on demand. Similarly, if a backend is already overwhelmed with queued prompts, sending more requests would only degrade performance. And in cases where all backend LLMs are heavily loaded, can we implement load shedding (where appropriate) to safeguard system stability?

`{{< reuse-image src="blog/deep-dive-inf-2.png" width="750px" >}}

That's exactly what the [Gateway API Inference Extension](https://gateway-api-inference-extension.sigs.k8s.io) project does. It introduces two new Kubernetes CRDs, [InferenceModel and InferencePool](https://gateway-api-inference-extension.sigs.k8s.io/concepts/api-overview/), and the concept of an "endpoint picker" that can extend L7 routing. This endpoint picker leverages metrics from the underlying LLM to make smarter routing and load balancing decisions for the L7 routing infrastructure. Projects like [kgateway](https://kgateway.dev/) and [Istio](https://istio.io), for example, can plug this into their implementations.

## Inference Extension extends Gateway API

The Gateway API Inference Extension introduces two new Custom Resource Definitions (CRDs): InferenceModel and InferencePool. By using these two new resources, along with the endpoint picker, the L7 routing infrastructure becomes an “Inference Gateway” enabling you to  
self-host GenAI/LLMs with a “model-as-a-service” mindset.

The [InferenceModel CRD](https://gateway-api-inference-extension.sigs.k8s.io/api-types/inferencemodel/) is designed for AI engineers, allowing them to define logical model inference endpoints. It maps user-facing model names to backend models and provides flexibility for traffic splitting between fine-tuned adapters. For example, maybe you want to expose a model named `llama2` to clients, but the backend models may be named `vllm-llama2-7b-2024-11-20` or `vllm-llama2-7b-2024-12-10`.  Using an InferenceModel, you can do that and split traffic among those models. Maybe you want to introduce a newer model such as `vllm-llama2-7b-2025-03-24`.

```yaml
apiVersion: inference.networking.x-k8s.io/v1alpha2
kind: InferenceModel
metadata:
  name: inferencemodel-llama2
spec:
  modelName: llama2
  criticality: Critical
  poolRef:
    name: vllm-llama2-7b-pool
  targetModels:
  - name: vllm-llama2-7b-2024-11-20
    weight: 75
  - name: vllm-llama2-7b-2025-03-24
    weight: 25
```

Additionally, it enables workload owners to specify request criticality, ensuring that real-time services receive priority over best-effort batch jobs. Below we'll see how that plays out depending on LLM metrics.

The [InferencePool CRD](https://gateway-api-inference-extension.sigs.k8s.io/api-types/inferencepool/), on the other hand, is intended for platform operators managing model-serving infrastructure. It represents a group of model-serving instances and acts as a specialized backend service for AI workloads. In other words, you can route requests from an HTTPRoute directly to a pool of inference endpoints with the InferencePool CR. The pool manages inference-aware endpoint selection by specifying which endpoint picker to use, making intelligent routing decisions based on real-time metrics such as request queue depth and GPU memory availability.

```yaml
apiVersion: inference.networking.x-k8s.io/v1alpha2  
kind: InferencePool  
metadata:  
  name: vllm-llama2-7b-pool  
spec:  
  targetPortNumber: 8000  
  selector:  
    app: vllm-llama2-7b  
  extensionRef:  
    name: vllm-llama2-7b-endpoint-picker
```
To set up routing so that prompts/requests to the inference gateway get sent to the backend LLMs, we need to first create an HTTPRoute that routes traffic to an InferencePool.

```yaml
apiVersion: gateway.networking.k8s.io/v1  
kind: HTTPRoute  
metadata:  
  name: llm-route  
spec:  
  parentRefs:  
  - name: inference-gateway  
  rules:  
  - backendRefs:  
    - group: inference.networking.x-k8s.io  
      kind: InferencePool  
      name: vllm-llama2-7b  
    matches:  
    - path:  
        type: PathPrefix  
        value: /  
```
Now when a request comes to the inference gateway, it will match on whatever is in the HTTPRoute and then send the request to the InferencePool. And here's where things get interesting. With an Envoy backed L7 router (like kgateway or Istio), normally the routing policy and load balancing will pick the endpoint that the request gets sent to. But with an InferencePool, the request first goes to a specialized extension "endpoint selection extension picker" or ESE.  This ESE will have logic to pick the right backend LLM endpoint based on metrics from the LLM themselves. Let's dig into how that works a little more.

## How the Endpoint Selection Works

When a request reaches the Endpoint Selection Extension (ESE), it extracts the modelName from the request body. Currently, the ESE expects the request body to follow the [OpenAI API format](https://platform.openai.com/docs/api-reference/chat/create). Once the modelName is identified, the ESE compares it against the modelName field of available InferenceModel objects to determine the corresponding backend model names or LoRA adapters. For example, if the ESE detects a request with the model name `llama2`, it will locate the matching InferenceModel and route the request to an appropriate endpoint, such as `vllm-llama2-7b-2024-11-20` or `vllm-llama2-7b-2025-03-24`.

The logic for choosing the specific endpoint for a particular model is defined in a series of "filters" in the ESE. The filters evaluate the following criteria to decide what the final endpoint should be:

* Criticality of the request (Critical or Sheddable)  
* Queue wait size of the LLM  
* LoRA adapter availability/affinity  
* KV cache usage of the LLM

`{{< reuse-image src="blog/deep-dive-inf-3.png" width="750px" >}}

The filter flow starts with "is this a critical request"? If the request is a Critical request, it will then check whether there are LLM endpoints with a wait queue lower than 50\. If it finds these, then it will check whether those endpoints have the LoRA adapter loaded for the model. If it finds a single endpoint that makes it through these filters, that is the endpoint that is returned. If it does not find an endpoint with the correct LoRA adapter loaded, it finds the next best option which is an endpoint that *can* load the requested LoRA adapter.

If the filter sees a request that is *Sheddable* then it will find LLMs that have lower than 80% KV cache utilization and fewer than 5 requests waiting in its queue. If it cannot find LLM endpoints that meet that criteria, the *Sheddable* request is dropped.

`{{< reuse-image src="blog/deep-dive-inf-4.png" width="500px" >}}

Let’s walk through some scenarios:

### **Example 1: Critical Request with LoRA Adapter**

Given these pods:

* Pod A: Queue=10, KV Cache=30%, has LoRA-X loaded  
* Pod B: Queue=5, KV Cache=70%, doesn't have LoRA-X  
* Pod C: Queue=60, KV Cache=20%, has LoRA-X loaded

For a critical request needing LoRA-X:

1. **Critical Request Check**: Pass (request is critical)  
2. **Low Queuing Filter**: Pods A and B pass (queue \< 50\)  
3. **LoRA Affinity Check**: Only Pod A passes (has LoRA-X)  
4. **Least Queuing Filter**: Pod A passes (only one pod)  
5. **Least KV Cache Filter**: Pod A passes (only one pod)  
6. **Final selection**: Pod A

### **Example 2: Non-Critical Request**

Given these pods:

* Pod A: Queue=6, KV Cache=85%  
* Pod B: Queue=4, KV Cache=75%  
* Pod C: Queue=7, KV Cache=60%

For a non-critical request:

1. **Critical Request Check**: Fail (request is not critical)  
2. **Has Capacity Filter**: Only Pod B passes (queue ≤ 5 and KV cache ≤ 80%)  
3. **Least Queue \+ LoRA \+ KV Cache Filter Chain**: Pod B continues (only one pod)  
4. **Final selection**: Pod B

### **Example 3: Critical Request with High Queue Everywhere**

Given these pods:

* Pod A: Queue=70, KV Cache=40%, has LoRA-Y  
* Pod B: Queue=80, KV Cache=60%, has LoRA-Y  
* Pod C: Queue=65, KV Cache=70%, doesn't have LoRA-Y

For a critical request needing LoRA-Y:

1. **Critical Request Check**: Pass (request is critical)  
2. **Low Queuing Filter**: Fail (all queues \> 50\)  
3. **Least Queuing Filter**: Pods A and C pass (in the first segment of the queue range)  
4. **Low Cost LoRA Filter**: Only Pod A passes (has LoRA-Y)  
5. **Least KV Cache Filter**: Pod A passes (only one pod)  
6. **Final selection**: Pod A

## Wrapping up

The Gateway API Inference Extension project introduces some powerful model selection and load balancing features that aim to improve GPU and LLM utilization when running on Kubernetes. GPUs are in short supply and thus very expensive. The Inference Extension project can significantly improve prompt processing and save organizations a lot of money. Some preliminary numbers are available on [the project’s website](https://gateway-api-inference-extension.sigs.k8s.io/performance/benchmark/), and I will have some more load testing numbers in the next blog post. 
