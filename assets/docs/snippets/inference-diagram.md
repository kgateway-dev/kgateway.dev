```mermaid
graph LR
    Client -->|inference request| kgateway
    kgateway -->|routes to| InferencePool
    subgraph  
        subgraph InferencePool
            direction LR
            InferenceModel_v1
            InferenceModel_v2
            InferenceModel_v3
        end
        kgateway
    end
```