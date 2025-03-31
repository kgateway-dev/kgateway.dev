---
title: Inference Extension
weight: 10
description: Use kgateway with the Inference Extension project.
---

Use {{< reuse "docs/snippets/product-name.md" >}} with the Kubernetes Gateway API [Inference Extension project](https://gateway-api-inference-extension.sigs.k8s.io/). This project extends the Gateway API so that you can route to AI inference workloads such as local Large Language Models (LLMs) that run in your Kubernetes environment.

## About Inference Extension {#about}

```mermaid
graph TD
    InferencePool --> InferenceModel_v1["InferenceModel v1"]
    InferencePool --> InferenceModel_v2["InferenceModel v2"]
    InferencePool --> InferenceModel_v3["InferenceModel v3"]
    
    subgraph InferencePool
        direction TB
        InferenceModel_v1
        InferenceModel_v2
        InferenceModel_v3
    end
```

## Kgateway with Inference Extension {#kgateway}


```mermaid
graph TD
    Client -->|inference request| kgateway
    kgateway -->|route to| InferencePool
    InferencePool --> InferenceModel_v1["InferenceModel v1"]
    InferencePool --> InferenceModel_v2["InferenceModel v2"]
    InferencePool --> InferenceModel_v3["InferenceModel v3"]
    subgraph  
        subgraph InferencePool
            direction TB
            InferenceModel_v1
            InferenceModel_v2
            InferenceModel_v3
        end
        kgateway
    end
```

## Setup steps {#setup}

Refer to the **Getting started** guide in the Inference Extension docs.

{{< cards >}}
  {{< card link="https://gateway-api-inference-extension.sigs.k8s.io/guides/" title="Inference Extension docs" icon="external-link">}}
{{< /cards >}}